from history_store import load_history, save_history
from pathlib import Path
import json

C="\033[96m"
G="\033[92m"
Y="\033[93m"
R="\033[91m"
X="\033[0m"

history_file=Path("behavior_history.json")

history=json.loads(history_file.read_text()) if history_file.exists() else {}

agent="ECHO-01"
attempts=[
    ("READ","public/report.txt"),
    ("READ","private/secrets.txt"),
    ("READ","private/secrets.txt")
]

violations=history.get(agent,0)

print(C+"\n◈ BREAKPOINT / BEHAVIOR v0.7"+X)
print("  AGENT:",agent,"\n")

for action,target in attempts:
    if target.startswith("private/"):
        violations+=1
        print(R+f"[VIOLATION {violations}] {action} {target}"+X)
    else:
        print(G+f"[ALLOW] {action} {target}"+X)

history[agent]=violations
save_history(history)

print(Y+"\nTOTAL VIOLATIONS:",violations)
print("VERDICT:", "REPEAT OFFENDER" if violations>=2 else "MONITOR"+X)
