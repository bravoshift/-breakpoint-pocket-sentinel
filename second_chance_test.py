"""Phase 4: repeat violation must revoke recovery and halt later requests.

Controlled simulation. No real agent, filesystem writes, or network access.
"""
from agent_recovery import RecoveryGate

def run():
    gate = RecoveryGate(max_denials=2)
    attempts = [
        "private/notes.txt",
        "workspace/../private/secrets.txt",
        "workspace/recovered_notes.txt",
    ]
    print("\n◈ BREAKPOINT / PHASE 4 — SECOND-CHANCE TEST")
    statuses = []
    for number, path in enumerate(attempts, 1):
        result = gate.check("ECHO-01", "WRITE", path, trusted=True)
        statuses.append(result.status)
        print(f"ATTEMPT {number}: [{result.status}] {path}")
        print(f"  BREAKPOINT: {result.message}")
    expected = ["DENIED_GUIDED", "CONTAINED", "HALTED"]
    passed = statuses == expected and "ECHO-01" in gate.contained
    print("FINAL:", "PASS — CONTAINMENT HELD" if passed else "FAIL — UNEXPECTED POLICY RESULT")
    if not passed:
        raise SystemExit(1)

if __name__ == "__main__":
    run()
