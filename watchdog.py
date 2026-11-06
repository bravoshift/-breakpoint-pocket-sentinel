import hashlib
from history_store import verify_history
from pathlib import Path

print("\n◈ BREAKPOINT / WATCHDOG")
print("  LOCAL EVIDENCE INTEGRITY CHECK\n")

for name in ("blackbox", "evidence"):
    evidence = Path(name + ".json")
    seal = Path(name + ".sha256")
    if not evidence.exists() and not seal.exists():
        print(f"[NOT FOUND] {name}: no evidence generated")
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

status = verify_history()
print(f"[{status}] behavior_history: local HMAC authentication")
print("\nNOTE: Local keys and hashes do not resist same-user compromise.")
print("WATCHDOG SCAN COMPLETE")
