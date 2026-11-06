"""BREAKPOINT Phase 7: local, hash-chained agent decision audit demo.

Offline simulation. No LLM calls. Writes only when --output is supplied.
Hash chaining detects edits to an existing sequence but does not prevent
an attacker from replacing the entire log; protect the final digest separately.
"""
import argparse
import hashlib
import json
from pathlib import Path
from agent_recovery import RecoveryGate

SCENARIOS = [
    ("ECHO-01", True, ["private/notes.txt", "workspace/notes.txt"]),
    ("ECHO-02", True, ["private/notes.txt", "workspace/../private/secrets.txt", "workspace/notes.txt"]),
    ("UNKNOWN-07", False, ["private/secrets.txt", "workspace/notes.txt"]),
]

def canonical(record):
    return json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=True)

def make_audit():
    gate = RecoveryGate(trusted_agents={"ECHO-01", "ECHO-02"})
    entries = []
    previous = "0" * 64
    for agent, trusted, paths in SCENARIOS:
        for path in paths:
            decision = gate.check(agent, "WRITE", path)
            entry = {
                "sequence": len(entries) + 1,
                "agent": agent,
                "trusted": trusted,
                "action": "WRITE",
                "path": path,
                "decision": decision.status,
                "reason": decision.message,
                "previous_hash": previous,
            }
            entry["hash"] = hashlib.sha256(canonical(entry).encode("utf-8")).hexdigest()
            previous = entry["hash"]
            entries.append(entry)
    return entries

def verify(entries, expected_final_hash=None):
    previous = "0" * 64
    for index, item in enumerate(entries, 1):
        entry = dict(item)
        digest = entry.pop("hash", None)
        if (entry.get("sequence") != index or
                entry.get("previous_hash") != previous or
                not isinstance(digest, str) or
                hashlib.sha256(canonical(entry).encode("utf-8")).hexdigest() != digest):
            return False
        previous = digest
    return bool(entries) and (expected_final_hash is None or previous == expected_final_hash)

def main():
    parser = argparse.ArgumentParser(description="BREAKPOINT Phase 7 audit demo")
    parser.add_argument("--output", help="Explicit local JSONL output path")
    args = parser.parse_args()
    entries = make_audit()
    assert verify(entries), "Audit integrity check failed"
    for entry in entries:
        print(f'{entry["sequence"]:02d} {entry["agent"]}: {entry["decision"]} {entry["path"]}')
    print(f'VERIFIED: {len(entries)} linked decisions')
    print(f'FINAL SHA256: {entries[-1]["hash"]}')
    if args.output:
        destination = Path(args.output)
        if destination.exists():
            parser.error("Output already exists; refusing to overwrite audit evidence")
        with destination.open("x", encoding="utf-8") as handle:
            for entry in entries:
                handle.write(canonical(entry) + "\n")
        print(f'AUDIT SAVED: {destination}')
    else:
        print("DRY RUN: no files written")

if __name__ == "__main__":
    main()
