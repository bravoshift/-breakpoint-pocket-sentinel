from pathlib import Path

C="\033[96m"
G="\033[92m"
R="\033[91m"
Y="\033[93m"
X="\033[0m"

root = (Path.cwd() / "test_lab").resolve()
root.mkdir(exist_ok=True)
workspace = root / "workspace"
workspace.mkdir(exist_ok=True)

contained = False

def agent_write(target, content):
    global contained

    if contained:
        print(Y+"[HALTED] "+X+target)
        return

    destination = (root / target).resolve()

    if not destination.is_relative_to(workspace):
        print(R+"[DENIED] "+X+target)
        print(R+"[!] ECHO-01 CONTAINED"+X)
        contained = True
        return

    destination.write_text(content)
    print(G+"[WRITTEN] "+X+target)

print(C+"\n◈ BREAKPOINT / SECURITY GATE v0.4"+X)
print("  AGENT: ECHO-01\n")

agent_write("workspace/report.txt", "Mission complete")
agent_write("private/secrets.txt", "Unauthorized")
agent_write("workspace/after.txt", "Should never run")

print("\nFINAL STATE:", "CONTAINED" if contained else "ACTIVE")
print("REPORT EXISTS:", (workspace/"report.txt").exists())
print("DENIED FILE EXISTS:", (root/"private/secrets.txt").exists())
print("AFTER FILE EXISTS:", (workspace/"after.txt").exists())
