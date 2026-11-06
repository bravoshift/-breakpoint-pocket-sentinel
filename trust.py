import json

from pathlib import Path
history_file = Path("behavior_history.json")
history = json.loads(history_file.read_text()) if history_file.exists() else {}
agent = "ECHO-01"
violations = history.get(agent, 0)

print("\n◈ BREAKPOINT / TRUST CHECK v0.8")
print("AGENT:", agent)
print("PAST VIOLATIONS:", violations)

if violations >= 3:
    print("\033[91m[LOCKED] Agent access denied\033[0m")
else:
    print("\033[92m[TRUSTED] Agent access permitted\033[0m")
