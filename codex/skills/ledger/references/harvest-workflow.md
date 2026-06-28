# Harvest Workflow

Harvest reads canonical source stores and recommends selective memory admission. It does not write compiled memory.

Inputs:

```text
.ledger/learnings/learnings.jsonl
.ledger/negative-ledger/events.jsonl
.ledger/synesthesia/events.jsonl
.ledger/harness/events.jsonl
.learnings.jsonl
~/.codex/memories/extensions/*/notes/*.md
~/.codex/memories/extensions/synesthesia/resources/latest_synesthesia_digest.md
```

Outputs may be terminal reports, timestamped resource digests, or memory-source notes through `$memory-source-notes`.

Admission gates:

- Learnings: `codify_now`, repeated theme, explicit durable user preference, high-value failure shield, repo map, verification path, or repeatable procedure.
- Negative Ledger: current `ledger export --format memory-note` projection with witness, applicability, exclusion, reopening criteria, and projection fingerprint.
- Synesthesia: explicit durable mapping or boundary event, rejection/retraction/reopening, or repeated accepted operational use.
- Harness: durable trigger/behavior/verification operating rule.

Recommended handoff:

```bash
learnings recall --query "<topic>" --limit 5
ledger doctor
ledger export --id NEG-000001 --format memory-note
memory-note append --extension <source> --kind <kind> --json -
```

Memory admission remains selective. Resource digests and notes are evidence for Phase 2, not runtime compiled memory.
