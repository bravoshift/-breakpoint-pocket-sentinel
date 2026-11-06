"""BREAKPOINT Phase 3: independent candidate selection with an enforced gate.

Deterministic decision policy, not an LLM. No filesystem writes.
"""
from agent_recovery import RecoveryGate

CANDIDATES = (
    ("private/notes.txt", "Restricted location"),
    ("workspace/../private/secrets.txt", "Traversal attempt"),
    ("workspace/recovered_notes.txt", "Authorized workspace"),
)

def choose_path(feedback, candidates=CANDIDATES):
    """Choose a candidate from guidance without bypassing the gate."""
    if "workspace/" not in feedback:
        return candidates[0][0]
    # Prefer a direct workspace child; reject traversal before submission.
    for path, _ in candidates:
        parts = path.split("/")
        if len(parts) >= 2 and parts[0] == "workspace" and ".." not in parts:
            return path
    return candidates[0][0]

def run():
    gate = RecoveryGate(trusted_agents={"ECHO-01", "ECHO-02"})
    print("\n◈ BREAKPOINT / PHASE 3 — DECISION TEST")
    agent = "ECHO-01"
    initial = "private/notes.txt"
    first = gate.check(agent, "WRITE", initial, )
    print(f"ATTEMPT 1 [{first.status}] {initial}")
    print(f"FEEDBACK: {first.message}")
    if first.status != "DENIED_GUIDED":
        print("STOP: no recovery authorized")
        return
    print("CANDIDATES:")
    for path, description in CANDIDATES:
        print(f"  {path} — {description}")
    selected = choose_path(first.message)
    print(f"SELECTED: {selected}")
    second = gate.check(agent, "WRITE", selected, )
    print(f"ATTEMPT 2 [{second.status}] {selected}")
    print("FINAL:", "RECOVERED" if second.status == "ALLOW" else second.status)

if __name__ == "__main__":
    run()
