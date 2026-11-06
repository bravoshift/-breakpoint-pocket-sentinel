from agent_recovery import RecoveryGate

gate = RecoveryGate(max_denials=1)
agent = "UNKNOWN-07"

print("BREAKPOINT / PHASE 10")

first = gate.check(agent, "WRITE", "private/secrets.txt")
print("INITIAL:", first.status)

approval = input("Human approval to release? (yes/no): ")

if approval.strip().lower() == "yes":
    gate.contained.discard(agent)
    gate.denials[agent] = 0
    print("RELEASED BY HUMAN")
else:
    print("CONTAINMENT MAINTAINED")

final = gate.check(agent, "WRITE", "workspace/notes.txt")
print("FINAL:", final.status)
