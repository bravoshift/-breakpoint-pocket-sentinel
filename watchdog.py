import hashlib
from pathlib import Path

print("\n◈ BREAKPOINT / WATCHDOG")
print("  LOCAL EVIDENCE INTEGRITY CHECK\n")

for name in ("blackbox", "evidence", "behavior_history"):
    evidence = Path(name + ".json")
    seal = Path(name + ".sha256")
    if not evidence.exists() and not seal.exists():
        print(f"[NOT FOUND] {name}: no evidence generated")
        continue
    if name == "behavior_history" and evidence.exists() and not seal.exists():
        print("[UNPROTECTED] behavior_history: no trusted fingerprint configured")
        continue
    if not evidence.exists() or not seal.exists():
        print(f"[ALERT] {name}: evidence or fingerprint missing")
        continue
    expected = seal.read_text().strip()
    actual = hashlib.sha256(evidence.read_bytes()).hexdigest()
    if actual == expected:
        print(f"[VERIFIED] {name}: local fingerprint matches")
    else:
        print(f"[ALERT] {name}: evidence changed or fingerprint invalid")

print("\nNOTE: Local fingerprints are not tamper-resistant.")
print("WATCHDOG SCAN COMPLETE")
