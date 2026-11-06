import tempfile
import os
import unittest
from pathlib import Path
from agent_recovery import RecoveryGate

class RecoveryTests(unittest.TestCase):
    def test_operator_trust_and_guided_retry(self):
        gate = RecoveryGate(trusted_agents={"ECHO"})
        self.assertEqual(gate.check("ECHO", "WRITE", "private/x").status, "DENIED_GUIDED")
        self.assertEqual(gate.check("ECHO", "WRITE", "workspace/x").status, "ALLOW")

    def test_unknown_contained(self):
        gate = RecoveryGate()
        self.assertEqual(gate.check("UNKNOWN", "WRITE", "private/x").status, "CONTAINED")
        self.assertEqual(gate.check("UNKNOWN", "WRITE", "workspace/x").status, "HALTED")

    def test_repeat_denial(self):
        gate = RecoveryGate(trusted_agents={"ECHO"})
        gate.check("ECHO", "WRITE", "private/x")
        self.assertEqual(gate.check("ECHO", "WRITE", "private/x").status, "CONTAINED")

    def test_traversal_immediately_contained(self):
        gate = RecoveryGate(trusted_agents={"ECHO"})
        self.assertEqual(gate.check("ECHO", "WRITE", "workspace/../private/x").status, "CONTAINED")

    def test_no_caller_trust_argument(self):
        gate = RecoveryGate()
        with self.assertRaises(TypeError):
            gate.check("UNKNOWN", "WRITE", "private/x", trusted=True)

    def test_symlink_escape(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "workspace").mkdir()
            (root / "private").mkdir()
            (root / "workspace" / "link").symlink_to(root / "private", target_is_directory=True)
            gate = RecoveryGate(trusted_agents={"ECHO"}, workspace_root=root / "workspace")
            self.assertEqual(gate.check("ECHO", "WRITE", "workspace/link/x").status, "CONTAINED")

    def test_invalid_path_fails_closed(self):
        gate = RecoveryGate(trusted_agents={"ECHO"})
        self.assertEqual(gate.check("ECHO", "WRITE", None).status, "CONTAINED")

    def test_release_keeps_count_and_audit(self):
        gate = RecoveryGate(max_denials=1)
        gate.check("UNKNOWN", "WRITE", "private/x")
        gate.release("UNKNOWN", "operator", "reviewed demo")
        self.assertEqual(gate.denials["UNKNOWN"], 1)
        self.assertEqual(gate.events[-1]["status"], "RELEASED")
        self.assertEqual(gate.check("UNKNOWN", "WRITE", "workspace/x").status, "ALLOW")


    def test_hard_link_escape(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "workspace").mkdir()
            (root / "private").mkdir()
            secret = root / "private" / "secret.txt"
            secret.write_text("example")
            os.link(secret, root / "workspace" / "linked.txt")
            gate = RecoveryGate(trusted_agents={"ECHO"}, workspace_root=root / "workspace")
            self.assertEqual(gate.check("ECHO", "WRITE", "workspace/linked.txt").status, "CONTAINED")

    def test_custom_workspace_root(self):
        with tempfile.TemporaryDirectory() as d:
            custom = Path(d) / "ws"
            custom.mkdir()
            gate = RecoveryGate(trusted_agents={"ECHO"}, workspace_root=custom)
            self.assertEqual(gate.check("ECHO", "WRITE", "workspace/new.txt").status, "ALLOW")

if __name__ == "__main__":
    unittest.main()
