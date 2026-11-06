"""BREAKPOINT recovery policy prototype. Not a process/OS security boundary.

Operator supplies trusted identities. Persistent mode uses the v1.3 HMAC history;
same-user modification, identity impersonation, rollback and key deletion remain
outside the protection of this prototype.
"""
from dataclasses import dataclass
from pathlib import Path
import json
import os

@dataclass(frozen=True)
class Decision:
    status: str
    message: str

class RecoveryGate:
    def __init__(self, allowed_root="workspace", max_denials=2,
                 trusted_agents=(), persistent=False, workspace_root=None):
        if not isinstance(allowed_root, str) or not allowed_root.isidentifier():
            raise ValueError("Invalid workspace name")
        self.allowed_root = allowed_root
        self.max_denials = max_denials
        self.trusted_agents = frozenset(trusted_agents)
        self.persistent = persistent
        self.workspace_root = Path(workspace_root or Path(__file__).resolve().parent / allowed_root).resolve()
        self.events = []
        self.denials = {}
        self.contained = set()
        if persistent:
            from history_store import load_history
            self.denials = load_history()
            self.contained = {a for a, n in self.denials.items()
                              if n >= (max_denials if a in self.trusted_agents else 1)}

    def _save(self):
        if self.persistent:
            from history_store import save_history
            save_history(self.denials)

    def _valid_path(self, action, path):
        if action != "WRITE" or not isinstance(path, str):
            return False, True
        parts = path.replace("\\", "/").split("/")
        hostile = (not path or path.startswith(("/", "\\")) or
                   "\\" in path or ".." in parts or
                   any(p in ("", ".") for p in parts))
        if hostile:
            return False, True
        if len(parts) < 2 or parts[0] != self.allowed_root:
            return False, False
        # Resolve existing symlinks, including in parent directories.
        candidate = (self.workspace_root.parent / path).resolve()
        if not candidate.is_relative_to(self.workspace_root):
            return False, True
        return True, False

    def check(self, agent, action, path):
        if not isinstance(agent, str) or not agent or agent != agent.strip():
            return Decision("CONTAINED", "Invalid identity; no action authorized.")
        if agent in self.contained:
            decision = Decision("HALTED", "Agent is contained; human review required.")
        else:
            valid, hostile = self._valid_path(action, path)
            if valid:
                decision = Decision("ALLOW", "Authorized path accepted (simulation only).")
            else:
                count = self.denials.get(agent, 0) + 1
                self.denials[agent] = count
                if hostile or agent not in self.trusted_agents or count >= self.max_denials:
                    self.contained.add(agent)
                    decision = Decision("CONTAINED", "Unauthorized action blocked; human review required.")
                else:
                    decision = Decision("DENIED_GUIDED", "Action blocked. Retry a WRITE inside workspace/ only.")
                self._save()
        self.events.append({"agent": agent, "action": action, "path": str(path), "status": decision.status})
        return decision

    def release(self, agent, approver, reason):
        """Demo release. Caller MUST independently authenticate approver."""
        if agent not in self.contained:
            raise ValueError("Agent is not contained")
        if not all(isinstance(x, str) and x.strip() for x in (approver, reason)):
            raise ValueError("Approver and reason required")
        self.contained.remove(agent)
        # Keep counts. Persistent history counts are not reset.
        self.events.append({"agent": agent, "status": "RELEASED",
                            "approver": approver, "reason": reason})
        # Persistent containment cannot be released securely with the v1.3
        # count-only schema. Fail closed instead of pretending it can.
        if self.persistent:
            self.contained.add(agent)
            raise RuntimeError("Persistent release needs an external authorization service")

def demo():
    gate = RecoveryGate(trusted_agents={"ECHO-01"})
    for agent, path in (("ECHO-01", "private/notes.txt"),
                        ("ECHO-01", "workspace/notes.txt"),
                        ("UNKNOWN-07", "private/secrets.txt"),
                        ("UNKNOWN-07", "workspace/notes.txt")):
        result = gate.check(agent, "WRITE", path)
        print(f"[{result.status}] {agent}: {path} — {result.message}")

if __name__ == "__main__":
    demo()
