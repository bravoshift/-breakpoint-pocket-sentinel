import hashlib
import json
from datetime import datetime

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

events = [
    ("READ", "public/report.txt", True),
    ("READ", "public/notes.txt", True),
    ("WRITE", "agent/instructions.txt", False),
    ("READ", "private/secrets.txt", False),
]

print(CYAN + "\n╔══════════════════════════════════╗")
print("║   BREAKPOINT / POCKET SENTINEL   ║")
print("╚══════════════════════════════════╝" + RESET)
print("   OBSERVE. SEAL. VERIFY.\n")

evidence = []
for action, target, allowed in events:
    status = "PASS" if allowed else "ALERT"
    color = GREEN if allowed else RED
    print(f"{color}[{status}]{RESET} {action}: {target}")
    evidence.append({
        "action": action,
        "target": target,
        "allowed": allowed
    })

record = {
    "timestamp": datetime.now().isoformat(),
    "events": evidence
}

data = json.dumps(record, sort_keys=True)
digest = hashlib.sha256(data.encode()).hexdigest()

with open("evidence.json", "w") as f:
    f.write(data)

print("\n" + YELLOW + "VERDICT: POLICY VIOLATIONS DETECTED")
print(RESET + f"Evidence SHA-256: {digest[:16]}...")
print(GREEN + "Evidence saved: evidence.json" + RESET)
