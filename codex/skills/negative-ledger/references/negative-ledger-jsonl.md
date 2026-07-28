# Negative Ledger JSONL Store

## Canonical Operational Store

```text
<repo>/.ledger/negative-ledger/events.jsonl
```

Use the `ledger` CLI. Do not hand-edit the store and do not treat `.ledger/learnings/events.jsonl` as the operational negative-ledger authority.

The sole structural definition is:

```text
${CODEX_HOME:-$HOME/.codex}/skills/negative-ledger/definitions/ledger/negative-evidence-protocol.json
```

Every command selects this definition and names its operation or projection.

## Generic Operations and Projections

```bash
negative_ledger_definition="${CODEX_HOME:-$HOME/.codex}/skills/negative-ledger/definitions/ledger/negative-evidence-protocol.json"

ledger doctor \
  --definition "$negative_ledger_definition" \
  --repo "<repo-root>" \
  --format json

ledger transact \
  --definition "$negative_ledger_definition" \
  --operation bind-existing \
  --repo "<repo-root>" \
  --input event="<repo-root>/.ledger/negative-ledger/events.jsonl" \
  --format json

ledger transact \
  --definition "$negative_ledger_definition" \
  --operation capture \
  --repo "<repo-root>" \
  --input capture=capture.json \
  --format json

ledger transact \
  --definition "$negative_ledger_definition" \
  --operation promote \
  --repo "<repo-root>" \
  --input promotion=promotion.json \
  --format json

ledger transact \
  --definition "$negative_ledger_definition" \
  --operation transition \
  --repo "<repo-root>" \
  --input transition=transition.json \
  --format json

ledger project \
  --definition "$negative_ledger_definition" \
  --projection current-records \
  --repo "<repo-root>" \
  --format json

ledger project \
  --definition "$negative_ledger_definition" \
  --projection memory-note \
  --repo "<repo-root>" \
  --param id=NEG-000001 \
  --format json
```

Before retrying a route, use the `route-gate` projection with the immutable
artifact identity and the identity required by the record's declared scope.
Exit `0` means no exact active match, `2` means an exact active/applicable
match, and `3` means the gate could not establish a valid result.

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
