"""BREAKPOINT Phase 2: feedback-driven local agent simulation.

This is a deterministic agent, NOT an LLM integration. No files are written.
"""
from agent_recovery import RecoveryGate

class LocalAgent:
    def __init__(self, name, trusted, initial_target):
        self.name = name
        self.trusted = trusted
        self.target = initial_target

    def run(self, gate):
        for attempt in range(1, 4):
            decision = gate.check(self.name, "WRITE", self.target)
            print(f"{self.name} attempt {attempt}: [{decision.status}] {self.target}")
            print(f"  BREAKPOINT: {decision.message}")
            if decision.status == "ALLOW":
                print("  VERIFIED: authorized path accepted (no file written)")
                return "RECOVERED" if attempt > 1 else "ALLOWED"
            if decision.status != "DENIED_GUIDED":
                return decision.status
            # Deterministic feedback interpreter: the agent selects a permitted path.
            # This does NOT bypass the gate; the retry is checked again.
            self.target = "workspace/recovered_notes.txt"
        return "STOPPED"

def main():
    gate = RecoveryGate(trusted_agents={"ECHO-01", "ECHO-02"})
    print("\n◈ BREAKPOINT / AGENT RECOVERY PHASE 2")
    for agent in (
        LocalAgent("ECHO-01", True, "private/notes.txt"),
        LocalAgent("UNKNOWN-07", False, "private/secrets.txt"),
    ):
        result = agent.run(gate)
        print(f"FINAL {agent.name}: {result}\n")

if __name__ == "__main__":
    main()
