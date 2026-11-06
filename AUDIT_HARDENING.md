# BREAKPOINT — Claude audit hardening branch

This branch is an **experimental security-hardening candidate**, not a production control. The frozen v1.3 baseline and the Phase 10 checkpoint are preserved on their original refs.

## Changes for independent retest

- RecoveryGate takes an operator-configured trusted-agent set; callers can no longer pass `trusted=True`.
- Unknown identities are contained on denied requests. Identity strings are **not authenticated**: renaming or impersonating a known identity is still possible without an external identity provider.
- Optional `persistent=True` loads/saves v1.3 HMAC-authenticated violation counts and fails closed on damaged state. This does **not** solve same-user access, stale rollback, concurrency, or identity spoofing.
- Traversal, absolute and backslash paths are immediately contained; path resolution rejects symlink escapes in the current filesystem snapshot. This is **not** a race-safe OS sandbox and must not authorize actual writes.
- Phase 10 rejects piped input and records a demo approver/reason without clearing counts. The prompt is **not authentication**: a pseudo-terminal can bypass the piped-input check, and same-process code can mutate gate state. **N3 remains open:** release events exist only in memory and are not saved. Persistent release deliberately fails closed until an independent approval boundary exists. No release-evidence mechanism is added until approval can be authenticated.
- Phase 7 uses keyed HMAC chaining, saves a signed count/final-digest manifest and supports `--verify`. Evidence remains forgeable by anyone with the local key and is not rollback-resistant.
- Recovery remains scripted/deterministic in Phase 2 and default live-recovery dry-run. No file operations are authorized or executed by these phases.

## Run tests and evidence checks

```sh
python -m unittest discover -s tests -v
python agent_recovery.py
python phase7_audit.py --output /tmp/breakpoint-audit.jsonl
python phase7_audit.py --verify /tmp/breakpoint-audit.jsonl
python phase10_release.py
```

The Phase 7 output requires an intact local key and matching `.manifest` file. Do not treat a copied key and manifest as independent proof.

## Audit status

These changes are **submitted for independent re-evaluation**, not certified as secure. The previous 11 passing tests apply to the prior commit; rerun tests against this branch. The major unresolved design gap is the absence of an independently enforced, authenticated agent runtime and operator approval boundary.

The repository is public with all rights reserved; no open-source license is granted.
