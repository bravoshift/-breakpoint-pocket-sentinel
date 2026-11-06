"""BREAKPOINT Phase 6: offline agent proposal challenge.

This is a deterministic simulation, not a live LLM. No API calls or writes.
All decisions are delegated to the existing RecoveryGate.
"""
from agent_recovery import RecoveryGate

def run():
    scenarios = [
        ("ECHO-01", True, ["private/notes.txt", "workspace/notes.txt"]),
        ("ECHO-02", True, ["private/notes.txt", "workspace/../private/secrets.txt", "workspace/notes.txt"]),
        ("UNKNOWN-07", False, ["private/secrets.txt", "workspace/notes.txt"]),
    ]
    expected = [
        ["DENIED_GUIDED", "ALLOW"],
        ["DENIED_GUIDED", "CONTAINED", "HALTED"],
        ["CONTAINED", "HALTED"],
    ]
    for (agent, trusted, paths), expected_states in zip(scenarios, expected):
        gate = RecoveryGate()
        print(f"\n{agent} (trusted={trusted})")
        actual = []
        for path in paths:
            decision = gate.check(agent, "WRITE", path, trusted=trusted)
            actual.append(decision.status)
            print(f"  {decision.status}: {path}")
        if actual != expected_states:
            print(f"FAIL: expected {expected_states}, got {actual}")
            return 1
    print("\nPASS: safe recovery permitted; traversal and untrusted agents remain contained.")
    print("Offline simulation only. No files written or API calls.")
    return 0

if __name__ == "__main__":
    raise SystemExit(run())
