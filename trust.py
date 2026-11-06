from history_store import load_history
import json

from pathlib import Path
history = load_history()
agent = "ECHO-01"
violations = history.get(agent, 0)

print("\n◈ BREAKPOINT / TRUST CHECK v0.8")
print("AGENT:", agent)
print("PAST VIOLATIONS:", violations)

if violations >= 3:
    print("\033[91m[LOCKED] Agent access denied\033[0m")
else:
    print("\033[92m[TRUSTED] Agent access permitted\033[0m")
