"""Phase 7 keyed evidence demo. Same-user key compromise/rollback remain possible."""
import argparse
import hashlib
import hmac
import json
from pathlib import Path
from agent_recovery import RecoveryGate
from history_store import _key, load_history

SCENARIOS = [
    ("ECHO-01", ["private/notes.txt", "workspace/notes.txt"]),
    ("ECHO-02", ["private/notes.txt", "workspace/../private/secrets.txt", "workspace/notes.txt"]),
    ("UNKNOWN-07", ["private/secrets.txt", "workspace/notes.txt"]),
]

def canonical(record):
    return json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=True)

def digest(record):
    return hmac.new(_key(), b"breakpoint-evidence-v1:" + canonical(record).encode(), hashlib.sha256).hexdigest()

def make_audit():
    gate = RecoveryGate(trusted_agents={"ECHO-01", "ECHO-02"})
    entries = []
    previous = "0" * 64
    for agent, paths in SCENARIOS:
        for path in paths:
            decision = gate.check(agent, "WRITE", path)
            entry = {"sequence": len(entries) + 1, "agent": agent,
                     "action": "WRITE", "path": path,
                     "decision": decision.status, "reason": decision.message,
                     "previous_hash": previous}
            entry["hash"] = digest(entry)
            previous = entry["hash"]
            entries.append(entry)
    return entries

def verify(entries, expected_final_hash=None, expected_count=None):
    if not entries or (expected_count is not None and len(entries) != expected_count):
        return False
    previous = "0" * 64
    for index, item in enumerate(entries, 1):
        entry = dict(item)
        tag = entry.pop("hash", None)
        if (entry.get("sequence") != index or entry.get("previous_hash") != previous
                or not isinstance(tag, str)
                or not hmac.compare_digest(digest(entry), tag)):
            return False
        previous = tag
    return expected_final_hash is None or hmac.compare_digest(previous, expected_final_hash)

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--output", help="Create JSONL and signed manifest; no overwrite")
    group.add_argument("--verify", help="Verify JSONL against its signed manifest")
    args = parser.parse_args()
    # Initialize authenticated history together with the key on first use.
    load_history()
    if args.verify:
        target = Path(args.verify)
        manifest = Path(str(target) + ".manifest")
        try:
            meta = json.loads(manifest.read_text())
            signature = meta.pop("signature")
            if not hmac.compare_digest(digest(meta), signature):
                raise ValueError("Manifest signature mismatch")
            entries = [json.loads(x) for x in target.read_text().splitlines()]
            if not verify(entries, meta["final_hash"], meta["count"]):
                raise ValueError("Evidence mismatch")
        except (OSError, ValueError, KeyError, TypeError) as exc:
            print("FAILED:", exc)
            return 1
        print("VERIFIED:", len(entries), "records")
        return 0
    entries = make_audit()
    assert verify(entries)
    print("VERIFIED:", len(entries), "linked decisions (local demo)")
    if args.output:
        target = Path(args.output)
        manifest = Path(str(target) + ".manifest")
        if target.exists() or manifest.exists():
            parser.error("Evidence or manifest already exists")
        meta = {"count": len(entries), "final_hash": entries[-1]["hash"]}
        meta["signature"] = digest(meta)
        try:
            with target.open("x") as f:
                for item in entries:
                    f.write(canonical(item) + "\n")
            with manifest.open("x") as f:
                f.write(canonical(meta) + "\n")
        except OSError:
            print("FAILED to write complete evidence; inspect partial files")
            return 1
        print("SAVED:", target)
    else:
        print("DRY RUN: no evidence file written")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
