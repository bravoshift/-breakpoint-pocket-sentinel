
import json

G = "\033[92m"
R = "\033[91m"
C = "\033[96m"
X = "\033[0m"

with open("evidence.json") as f:
    data = json.load(f)

print(C + "\n=== BREAKPOINT EVIDENCE REPORT ===" + X)
print("Recorded:", data["timestamp"])
print("-" * 36)

for event in data["events"]:
    allowed = event["allowed"]
    color = G if allowed else R
    status = "PASS" if allowed else "DENIED"

    print(color + f"\n[{status}] {event['agent_id']}" + X)
    print(f"Action: {event['action']}")
    print(f"Target: {event['target']}")
    print(f"Reason: {event['reason']}")

print(C + "\n=== END OF REPORT ===" + X)
passed = sum(e["allowed"] for e in data["events"])
denied = len(data["events"]) - passed

print(G + f"ALLOWED: {passed}" + X)
print(R + f"DENIED: {denied}" + X)
print(f"TOTAL EVENTS: {len(data['events'])}")
