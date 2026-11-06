from history_store import load_history, save_history
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = (Path.cwd() / "test_lab").resolve()
WORK = ROOT / "workspace"
WORK.mkdir(parents=True, exist_ok=True)

history = load_history()
records = []
contained = set()

def check(agent, target):
    violations = history.get(agent, 0)
    destination = (ROOT / target).resolve()
    status = "DENIED"

    if agent in contained:
        status = "HALTED"
    elif agent in contained:
        status = "HALTED"
    elif violations >= 3:
        status = "LOCKED"
    elif not destination.is_relative_to(WORK):
        status = "DENIED"
        history[agent] = violations + 1
        contained.add(agent)
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text("Authorized BREAKPOINT test")
        status = "WRITTEN"

    records.append({
        "time": datetime.now(timezone.utc).isoformat(),
        "agent": agent,
        "target": target,
        "status": status
    })
    print(f"[{status}] {agent}: {target}")

print("\n◈ BREAKPOINT / CONTROLLER v1.1")

check("ECHO-01", "workspace/echo01.txt")
check("ECHO-02", "workspace/echo02.txt")
check("ECHO-02", "private/secrets.txt")
check("ECHO-02", "workspace/after_denial.txt")
check("ECHO-02", "workspace/after_denial.txt")

save_history(history)
Path("controller_log.json").write_text(
    json.dumps(records, indent=2)
)

print("\nECHO-01 FILE:", (WORK / "echo01.txt").exists())
print("ECHO-02 FILE:", (WORK / "echo02.txt").exists())
print("PRIVATE FILE:", (ROOT / "private/secrets.txt").exists())
print("LOG SAVED:", Path("controller_log.json").exists())
