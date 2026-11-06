"""Phase 10: terminal-only HUMAN RELEASE SIMULATION, not real authentication."""
import sys
from agent_recovery import RecoveryGate

def main():
    gate = RecoveryGate(max_denials=1)
    agent = "UNKNOWN-07"
    print("BREAKPOINT / PHASE 10 (SIMULATION)")
    print("INITIAL:", gate.check(agent, "WRITE", "private/secrets.txt").status)
    if not sys.stdin.isatty():
        print("REFUSED: interactive terminal required")
        return 1
    answer = input("Human approval to release? (type yes): ")
    if answer.strip() != "yes":
        print("CONTAINMENT MAINTAINED")
    else:
        approver = input("Approver name (demo only; not authenticated): ").strip()
        reason = input("Release reason: ").strip()
        try:
            gate.release(agent, approver, reason)
        except ValueError as exc:
            print("RELEASE REFUSED:", exc)
            return 1
        print("RELEASED IN DEMO; not an authenticated approval")
    final = gate.check(agent, "WRITE", "workspace/notes.txt")
    print("FINAL:", final.status)
    return 0

if __name__ == "__main__":
    sys.exit(main())
