# Learnings as a Negative-Ledger Source

`$learnings` supplies historical candidate evidence. The negative ledger owns failed-hypothesis semantics and operational route state in:

```text
.ledger/negative-ledger/events.jsonl
```

## Read Path

```bash
learnings recall \
  --query "<artifact> <objective> failed attempt regression revert no-effect avoid" \
  --limit 10 \
  --drop-superseded
```

## Candidate Test

A learning may seed a ledger capture only when it has:

- condition/action statement relevant to the current task;
- inspectable command, test, benchmark, commit, revert, trace, path, or review witness;
- application that changes routing;
- current artifact-state applicability;
- narrow exclusion semantics;
- explicit reopening criteria.

## Promotion Path

```text
learning row
  -> verify evidence and applicability
  -> ledger capture
  -> ledger export
  -> memory-note append (only when memory admission qualifies)
```

Do not send the learning row directly to the negative-ledger memory extension as an active exclusion.
