"""BREAKPOINT Agent Recovery: simulated, permission-preserving guidance."""
from dataclasses import dataclass
from pathlib import PurePosixPath

@dataclass(frozen=True)
class Decision:
    status: str
    message: str

class RecoveryGate:
    def __init__(self, allowed_root="workspace", max_denials=2):
        self.allowed_root = allowed_root
        self.max_denials = max_denials
        self.denials = {}
        self.contained = set()
        self.events = []

    def check(self, agent, action, path, trusted=False):
        count = self.denials.get(agent, 0)
        if agent in self.contained:
            decision = Decision("HALTED", "Agent is contained; human review required.")
        else:
            # Reject traversal and absolute paths before normalization.
            parts = path.replace("\\", "/").split("/")
            valid = (
                action == "WRITE"
                and not path.startswith(("/", "\\"))
                and ".." not in parts
                and all(p not in ("", ".") for p in parts)
                and len(parts) >= 2
                and parts[0] == self.allowed_root
            )
            if valid:
                decision = Decision("ALLOW", "Action is within the authorized workspace.")
            else:
                count += 1
                self.denials[agent] = count
                if not trusted or count >= self.max_denials:
                    self.contained.add(agent)
                    decision = Decision("CONTAINED", "Unauthorized action blocked; human review required.")
                else:
                    decision = Decision("DENIED_GUIDED", "Action blocked. You may retry a WRITE inside workspace/ only; no permissions changed.")
        self.events.append({"agent": agent, "action": action, "path": path, "status": decision.status})
        return decision

def demo():
    gate = RecoveryGate()
    steps = [
        ("ECHO-01", "WRITE", "private/notes.txt", True),
        ("ECHO-01", "WRITE", "workspace/notes.txt", True),
        ("UNKNOWN-07", "WRITE", "private/secrets.txt", False),
        ("UNKNOWN-07", "WRITE", "workspace/notes.txt", False),
    ]
    for agent, action, path, trusted in steps:
        result = gate.check(agent, action, path, trusted)
        print(f"[{result.status}] {agent}: {path} — {result.message}")

if __name__ == "__main__":
    demo()
