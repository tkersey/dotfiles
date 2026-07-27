# Learnings as a Negative-Ledger Source

`$learnings` supplies historical candidate evidence through its canonical
passive protocol definition. Negative Ledger owns failed-hypothesis semantics
and operational route state through its own protocol definition.

## Read Path

```bash
ledger project \
  --definition "${CODEX_HOME:-$HOME/.codex}/skills/learnings/definitions/ledger/learnings-protocol.json" \
  --projection recall \
  --repo <repo> \
  --param "query=<artifact> <objective> failed attempt regression revert no-effect avoid" \
  --param search_limit=10 \
  --param drop_superseded=true \
  --format json
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
  -> ledger transact with the Negative Ledger definition
  -> ledger project with the Negative Ledger definition
  -> memory-note append (only when memory admission qualifies)
```

Do not send the learning row directly to the negative-ledger memory extension as an active exclusion.
