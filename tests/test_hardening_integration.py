"""Regression coverage for Phase 7 initialization, keyed evidence and phase scripts."""
import contextlib
import hashlib
import hmac
import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]

class HardeningIntegrationTests(unittest.TestCase):
    def test_phase_scripts_run(self):
        for script in ("second_chance_test.py", "phase6_challenge.py"):
            with self.subTest(script=script):
                result = subprocess.run([sys.executable, str(ROOT / script)],
                                        cwd=ROOT, capture_output=True, text=True, timeout=20)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("PASS", result.stdout)

    def test_phase7_first_run_preserves_history(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for name in ("phase7_audit.py", "agent_recovery.py", "history_store.py",
                         "breakpoint_v11.py"):
                shutil.copy2(ROOT / name, root / name)
            first = subprocess.run([sys.executable, "phase7_audit.py"], cwd=root,
                                   capture_output=True, text=True, timeout=20)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            second = subprocess.run([sys.executable, "breakpoint_v11.py"], cwd=root,
                                    capture_output=True, text=True, timeout=20)
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            self.assertTrue((root / "behavior_history.hmac").exists())

    def test_evidence_domain_separation(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for name in ("phase7_audit.py", "agent_recovery.py", "history_store.py"):
                shutil.copy2(ROOT / name, root / name)
            code = (
                "import phase7_audit as a; from history_store import load_history,_key;"
                "load_history(); record={'sequence':1};"
                "legacy=hmac.new(_key(),a.canonical(record).encode(),hashlib.sha256).hexdigest();"
                "assert legacy != a.digest(record)"
            )
            result = subprocess.run([sys.executable, "-c",
                                     "import hmac,hashlib;"+code], cwd=root,
                                    capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

if __name__ == "__main__":
    unittest.main()
