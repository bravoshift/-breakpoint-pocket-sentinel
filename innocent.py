import json
from pathlib import Path

agent = "ECHO-02"
history_file = Path("behavior_history.json")
history = json.loads(history_file.read_text()) if history_file.exists() else {}
violations = history.get(agent, 0)

target = Path("test_lab/workspace/ECHO-02.txt")

print("\n◈ BREAKPOINT / LOCKDOWN v0.9")
print("AGENT:", agent)
print("PAST VIOLATIONS:", violations)

if violations >= 3:
    print("\033[91m[LOCKED] File write blocked\033[0m")
else:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("Authorized test")
    print("\033[92m[ALLOWED] File written\033[0m")

print("FILE EXISTS:", target.exists())
