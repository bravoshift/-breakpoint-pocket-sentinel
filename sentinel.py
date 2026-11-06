import hashlib
import json
import posixpath
from datetime import datetime

C = "\033[96m"
G = "\033[92m"
R = "\033[91m"
Y = "\033[93m"
X = "\033[0m"

rules = {
    "READ": ["public/"],
    "WRITE": ["workspace/"]
}

events = [
    ("READ", "public/report.txt"),
    ("WRITE", "workspace/summary.txt"),
    ("READ", "private/secrets.txt"),
    ("WRITE", "agent/instructions.txt"),
    ("DELETE", "public/report.txt")
]

print(C + "\n╔══════════════════════════════════╗")
print("║   BREAKPOINT / POCKET SENTINEL   ║")
print("╚══════════════════════════════════╝" + X)
print("   DETECTION ENGINE v0.2\n")

evidence = []
alerts = 0

for action, target in events:
    allowed = any(
        posixpath.normpath(target).startswith(prefix)
        for prefix in rules.get(action, [])
    )
    status = "PASS" if allowed else "ALERT"
    color = G if allowed else R
    print(f"{color}[{status}]{X} {action}: {target}")
    alerts += not allowed
    evidence.append({
        "action": action,
        "target": target,
        "allowed": allowed,
        "agent_id": "ECHO-01",
        "reason": "Within permitted scope" if allowed else "Action or path not permitted"
    })

record = {
    "timestamp": datetime.now().isoformat(),
    "rules": rules,
    "events": evidence
}

data = json.dumps(record, sort_keys=True)
digest = hashlib.sha256(data.encode()).hexdigest()

with open("evidence.json", "w") as f:
    f.write(data)

with open("evidence.sha256", "w") as f:
    f.write(digest + "\n")

print(Y + f"\nTHREATS DETECTED: {alerts}" + X)
print(f"EVIDENCE SHA-256: {digest[:16]}...")
print(G + "Evidence saved: evidence.json (fingerprint: evidence.sha256)" + X)
