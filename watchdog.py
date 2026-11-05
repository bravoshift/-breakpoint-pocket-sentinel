import hashlib
from pathlib import Path

C="\033[96m"
G="\033[92m"
R="\033[91m"
X="\033[0m"

print(C+"\n◈ BREAKPOINT / WATCHDOG v0.6"+X)
print("  INDEPENDENT INTEGRITY CHECK\n")

evidence=Path("blackbox.json")
seal=Path("blackbox.sha256")

if not evidence.exists() or not seal.exists():
    print(R+"[ALERT] EVIDENCE MISSING"+X)
else:
    expected=seal.read_text().strip()
    actual=hashlib.sha256(
        evidence.read_bytes()
    ).hexdigest()

    if actual==expected:
        print(G+"[VERIFIED] Evidence intact"+X)
    else:
        print(R+"[ALERT] EVIDENCE TAMPERED"+X)
        print("Expected:",expected[:20])
        print("Observed:",actual[:20])

print(C+"\nWATCHDOG SCAN COMPLETE"+X)
