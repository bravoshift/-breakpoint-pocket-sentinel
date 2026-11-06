from history_store import load_history
import json
from pathlib import Path

agent = "ECHO-01"
history = load_history()
violations = history.get(agent, 0)

target = Path("test_lab/workspace/locked_agent.txt")

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
