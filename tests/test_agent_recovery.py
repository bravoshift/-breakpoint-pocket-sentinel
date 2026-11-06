import unittest
from agent_recovery import RecoveryGate

class RecoveryTests(unittest.TestCase):
    def test_trusted_agent_can_correct(self):
        gate = RecoveryGate()
        self.assertEqual(gate.check("ECHO", "WRITE", "private/x", True).status, "DENIED_GUIDED")
        self.assertEqual(gate.check("ECHO", "WRITE", "workspace/x", True).status, "ALLOW")

    def test_untrusted_agent_contained(self):
        gate = RecoveryGate()
        self.assertEqual(gate.check("UNKNOWN", "WRITE", "private/x", False).status, "CONTAINED")
        self.assertEqual(gate.check("UNKNOWN", "WRITE", "workspace/x", False).status, "HALTED")

    def test_repeat_violation_contained(self):
        gate = RecoveryGate()
        gate.check("ECHO", "READ", "workspace/x", True)
        self.assertEqual(gate.check("ECHO", "WRITE", "private/x", True).status, "CONTAINED")

    def test_traversal_rejected(self):
        gate = RecoveryGate()
        self.assertEqual(gate.check("ECHO", "WRITE", "workspace/../private/x", True).status, "DENIED_GUIDED")

if __name__ == "__main__":
    unittest.main()
