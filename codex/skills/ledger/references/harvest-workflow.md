# Harvest Workflow

Harvest reads canonical source stores and recommends selective memory admission. It does not write compiled memory.

Inputs:

```text
.ledger/learnings/events.jsonl
.ledger/negative-ledger/events.jsonl
.ledger/synesthesia/events.jsonl
~/.codex/memories/extensions/*/notes/*.md
~/.codex/memories/extensions/synesthesia/resources/latest_synesthesia_digest.md
```

Outputs may be terminal reports, timestamped resource digests, or memory-source notes through `$memory-source-notes`.

Admission gates:

- Learnings: `codify_now`, repeated theme, explicit durable user preference, high-value failure shield, repo map, verification path, or repeatable procedure.
- Negative Ledger: current definition-bound `memory-note` projection with witness, applicability, exclusion, reopening criteria, and projection fingerprint.
- Synesthesia: explicit durable mapping or boundary event, rejection/retraction/reopening, or repeated accepted operational use.

Recommended handoff:

```bash
ledger project --definition <learnings-protocol.json> --projection recall --repo <repo> --param query="<topic>" --param limit=5 --format json
ledger doctor --definition <negative-evidence-protocol.json> --repo <repo> --format json
ledger project --definition <negative-evidence-protocol.json> --projection memory-note --repo <repo> --param id=NEG-000001 --payload-only --format json
memory-note append --extension <source> --kind <kind> --json -
```

Memory admission remains selective. Resource digests and notes are evidence for Phase 2, not runtime compiled memory.
