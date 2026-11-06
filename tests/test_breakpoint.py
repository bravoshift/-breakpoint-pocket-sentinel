"""Run with: python -m unittest discover -s tests -v"""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

class BreakpointTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.cwd = Path(self.tmp.name)
        self.env = dict(os.environ, PYTHONPATH=str(REPO))

    def run_script(self, script):
        return subprocess.run([sys.executable, str(REPO / script)],
                              cwd=self.cwd, env=self.env,
                              text=True, capture_output=True)

    def test_fresh_clone_and_containment(self):
        result = self.run_script("breakpoint_v11.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("[DENIED] ECHO-02", result.stdout)
        self.assertIn("[HALTED] ECHO-02", result.stdout)
        self.assertFalse((self.cwd / "test_lab/private/secrets.txt").exists())
        self.assertEqual(self.run_script("trust.py").returncode, 0)

    def test_tampered_history_fails_closed(self):
        self.assertEqual(self.run_script("breakpoint_v11.py").returncode, 0)
        history = self.cwd / "behavior_history.json"
        history.write_text('{"ECHO-02": 0}')
        result = self.run_script("innocent.py")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("authentication failed", result.stderr)
        self.assertIn("[ALERT] behavior_history", self.run_script("watchdog.py").stdout)

    def test_deleted_history_fails_closed(self):
        self.assertEqual(self.run_script("breakpoint_v11.py").returncode, 0)
        (self.cwd / "behavior_history.json").unlink()
        (self.cwd / "behavior_history.hmac").unlink()
        self.assertNotEqual(self.run_script("lockdown.py").returncode, 0)

    def test_evidence_verification(self):
        self.assertEqual(self.run_script("blackbox.py").returncode, 0)
        self.assertEqual(self.run_script("sentinel.py").returncode, 0)
        self.assertEqual(self.run_script("breakpoint_v11.py").returncode, 0)
        self.assertIn("[VERIFIED] blackbox", self.run_script("watchdog.py").stdout)
        self.assertIn("[VERIFIED] evidence", self.run_script("watchdog.py").stdout)
        self.assertIn("[VERIFIED] behavior_history", self.run_script("watchdog.py").stdout)

if __name__ == "__main__":
    unittest.main()
