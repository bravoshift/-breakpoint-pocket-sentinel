# Security Policy

## Scope

BREAKPOINT / Pocket Sentinel v1.3 is a **research demonstration**, not a production security boundary. Its agents and containment are simulated. Do not use it to protect real files, credentials, or live AI agents.

## Reporting vulnerabilities

Please **do not publish working bypasses or sensitive proof-of-concept details in public issues**. Use GitHub's private vulnerability reporting feature if enabled:

https://github.com/bravoshift/-breakpoint-pocket-sentinel/security/advisories/new

If private reporting is unavailable, open a public issue asking for a private contact channel **without disclosing exploit details**.

Useful reports include affected version/commit, reproduction steps, expected versus actual behavior, and potential impact. Do not include real credentials, private data, or third-party targets.

## Known limitations (not new vulnerability reports)

- A previously authenticated history/tag pair can be replayed to roll back violation counts.
- Removing the local key, history, and tag together resets the demonstration.
- Anyone with access to the local signing key can forge history.
- Local SHA-256 evidence sidecars do not protect against an attacker who can edit both evidence and hashes.
- The system does not enforce operating-system-wide containment or intercept external agents.

These are explicitly out of scope for the v1.3 prototype and would require a separate trusted security boundary to address.

## Supported versions

v1.3 is the current frozen research baseline. Earlier milestones are historical demonstrations and are not maintained as security products.

## Disclosure

Please allow time to reproduce and assess reports before public disclosure. No response-time or remediation guarantee is offered for this experimental project.
