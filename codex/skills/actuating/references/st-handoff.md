# `$st` Handoff

## New material plan

```bash
st intake scaffold --source <plan.md> --out .ledger/st/intake/st-intake.md
# Agent authors/corrects semantic intake.
st intake check --input .ledger/st/intake/st-intake.md --gate implementation-ready --format json
st intake normalize --input .ledger/st/intake/st-intake.md --out .ledger/st/intake/st-intake.normalized.md
st intake apply \
  --file .ledger/st/st-plan.jsonl \
  --input .ledger/st/intake/st-intake.normalized.md \
  --gate implementation-ready
st compile aperture --file .ledger/st/st-plan.jsonl --limit 7
```

## Existing graph

```bash
st compile aperture --file .ledger/st/st-plan.jsonl --limit 7
```

## Hard rule

For material work:

```text
no current executable GCR
or
unwaived blocking graph debt
=> no delivery mutation
```

Do not silently switch to ledger/prose execution.

## Projection

Project only `plan_sync.codex.plan`.

Default to one `update_plan` call per GCR sequence.

Repeated projection without a graph/GCR change is a projection-inversion warning.

## Completion

```bash
st proof plan --file .ledger/st/st-plan.jsonl --scope aperture --format json
st proof record \
  --file .ledger/st/st-plan.jsonl \
  --id <st-id> \
  --obligation <proof-id> \
  --action <proof-action-id> \
  --command "<validation command>" \
  --evidence-ref <proof-log> \
  --artifact-ref "git:<sha-or-working-tree-fingerprint>"
st complete --file .ledger/st/st-plan.jsonl --id <st-id>
st compile aperture --file .ledger/st/st-plan.jsonl --limit 7
st assert-projection --file .ledger/st/st-plan.jsonl
```

ASL may reference `$st` IDs and receipts. It may not independently mark `$st` tasks complete.
