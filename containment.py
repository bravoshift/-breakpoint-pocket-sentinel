import posixpath

C="\033[96m"
G="\033[92m"
R="\033[91m"
Y="\033[93m"
X="\033[0m"

print(C+"\n◈ BREAKPOINT / CONTAINMENT v0.3"+X)
print("  AGENT: ECHO-01\n")

actions = [
    ("READ", "public/report.txt"),
    ("WRITE", "workspace/notes.txt"),
    ("READ", "public/../private/secrets.txt"),
    ("WRITE", "workspace/results.txt"),
]

rules = {"READ": "public/", "WRITE": "workspace/"}
contained = False

for action, path in actions:
    if contained:
        print(Y+"[HALTED] "+X+action+" "+path)
        continue

    normalized = posixpath.normpath(path)
    allowed = normalized.startswith(rules.get(action, "\0"))

    if allowed:
        print(G+"[ALLOW] "+X+action+" "+path)
    else:
        print(R+"[DENY]  "+X+action+" "+path)
        print(R+"[!] AGENT CONTAINED"+X)
        contained = True

print(C+"\nFINAL STATE: "+X+
      ("CONTAINED" if contained else "ACTIVE"))
