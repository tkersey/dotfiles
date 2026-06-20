# Negative Ledger JSONL Store

## Canonical Operational Store

```text
<repo>/.ledger/negative-ledger.jsonl
```

Use the `ledger` CLI. Do not hand-edit the store and do not treat `.learnings.jsonl` as the operational negative-ledger authority.

## Commands

```bash
ledger init
ledger capture --json capture.json
ledger query
ledger map --route "<route>" --cluster "<cluster>" --artifact "<artifact-state>"
ledger show --id NEG-000001
ledger handoff
ledger compact
ledger doctor
ledger export --id NEG-000001 --format full
ledger export --id NEG-000001 --format memory-note
ledger status --id NEG-000001 --to stale --reason "..."
```

`export` and generic `status` are required by the companion skills-zig specification.

## Operational Versus Memory Authority

```text
.ledger/negative-ledger.jsonl
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
