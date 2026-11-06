"""N7: a v1.3-locked identity cannot bypass lockout with a higher recovery limit."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class PersistentLockoutTests(unittest.TestCase):
    def test_v13_lockout_cannot_be_overridden(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for name in ("agent_recovery.py", "history_store.py"):
                shutil.copy2(ROOT / name, root / name)
            code = (
                "from history_store import save_history,load_history,LOCKOUT_THRESHOLD;"
                "from agent_recovery import RecoveryGate;"
                "load_history();"
                "save_history({'ECHO-02': LOCKOUT_THRESHOLD});"
                "gate=RecoveryGate(trusted_agents={'ECHO-02'},persistent=True,max_denials=5);"
                "assert gate.check('ECHO-02','WRITE','workspace/allowed.txt').status=='HALTED'"
            )
            result = subprocess.run([sys.executable, "-c", code], cwd=root,
                                    capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


    def test_third_denial_contains_in_same_session(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for name in ("agent_recovery.py", "history_store.py"):
                shutil.copy2(ROOT / name, root / name)
            code = (
                "from history_store import LOCKOUT_THRESHOLD;"
                "from agent_recovery import RecoveryGate;"
                "gate=RecoveryGate(trusted_agents={'ECHO-02'},persistent=True,max_denials=5);"
                "statuses=[gate.check('ECHO-02','WRITE','private/notes.txt').status "
                "for _ in range(LOCKOUT_THRESHOLD)];"
                "assert statuses==['DENIED_GUIDED','DENIED_GUIDED','CONTAINED'],statuses;"
                "assert gate.check('ECHO-02','WRITE','workspace/ok.txt').status=='HALTED'"
            )
            result = subprocess.run([sys.executable, "-c", code], cwd=root,
                                    capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

if __name__ == "__main__":
    unittest.main()
