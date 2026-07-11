# Negative Ledger JSONL Store

## Canonical Operational Store

```text
<repo>/.ledger/negative-ledger/events.jsonl
```

Use the native CLI through `$ledger`. Do not hand-edit the store and do not treat `.ledger/learnings/events.jsonl` as the operational negative-ledger authority.

## Commands

```text
$ledger run -- init
$ledger run -- capture --json capture.json
$ledger run -- query
$ledger run -- map --route "<route>" --cluster "<cluster>" --artifact "<artifact-state>"
$ledger run -- show --id NEG-000001
$ledger run -- handoff
$ledger run -- compact
$ledger run -- doctor
$ledger run -- export --id NEG-000001 --format full
$ledger run -- export --id NEG-000001 --format memory-note
$ledger run -- status --id NEG-000001 --to stale --reason "..."
```

`export` and generic `status` are required by the companion skills-zig specification.

## Operational Versus Memory Authority

```text
.ledger/negative-ledger/events.jsonl
  decides current route state

extensions/negative-ledger/notes/*.md
  immutable exported snapshots admitted to Phase 2

MEMORY.md / memory_summary.md / skills/*
  compiled memory
```

A memory note must never become the blocking route gate. The ledger must remain available and applicable to the current artifact state.

## Lifecycle Events

Use append-only transitions:

```text
capture_candidate
need-evidence
unknown
active
accepted_risk
stale
reopened
superseded
```

Do not rewrite prior events.

## Proof Lines

```text
ledger-capture: neg_id=NEG-... status=active
ledger-status: neg_id=NEG-... status=stale
memory-note: id=MSN-... extension=negative-ledger kind=ledger-projection status=created
```
