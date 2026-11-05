import json
import hashlib
from pathlib import Path
from datetime import datetime

C="\033[96m"
G="\033[92m"
R="\033[91m"
Y="\033[93m"
X="\033[0m"

root=(Path.cwd()/"blackbox_lab").resolve()
workspace=root/"workspace"
workspace.mkdir(parents=True,exist_ok=True)

events=[]
contained=False

def record(status,action,target):
    events.append({
        "time":datetime.now().isoformat(),
        "status":status,
        "action":action,
        "target":target
    })

def write(target,content):
    global contained
    if contained:
        status="HALTED"
    elif not (root/target).resolve().is_relative_to(workspace):
        status="DENIED"
        contained=True
    else:
        status="WRITTEN"
        (root/target).resolve().write_text(content)

    record(status,"WRITE",target)
    color={"WRITTEN":G,"DENIED":R,"HALTED":Y}[status]
    print(color+f"[{status}] {target}"+X)

print(C+"\n◈ BREAKPOINT / BLACK BOX v0.5"+X)
print("  AGENT: ECHO-01\n")

write("workspace/report.txt","Mission complete")
write("private/secrets.txt","Unauthorized")
write("workspace/after.txt","Blocked")

data=json.dumps(events,indent=2)
Path("blackbox.json").write_text(data)
digest=hashlib.sha256(data.encode()).hexdigest()
Path("blackbox.sha256").write_text(digest)

print(C+"\n╔══════════════════════════╗")
print("║    FLIGHT RECORDER       ║")
print("╚══════════════════════════╝"+X)
print("EVENTS RECORDED:",len(events))
print("FINAL STATE:","CONTAINED" if contained else "ACTIVE")
print(G+"EVIDENCE SEALED"+X)
print("SHA-256:",digest[:20]+"...")
print("BLACK BOX READY")
