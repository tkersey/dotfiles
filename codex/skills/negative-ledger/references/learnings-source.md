# Learnings as a Negative-Ledger Source

`$learnings` supplies historical candidate evidence through its canonical
passive protocol definition. The `$negative-ledger` skill owns
failed-hypothesis semantics and operational route state through its protocol
definition. Ledger validates and transacts the declared structure without
deciding route meaning or authority.

## Read Path

```bash
learnings_definition="$(realpath "${CODEX_HOME:-$HOME/.codex}/skills/learnings/definitions/ledger/learnings-protocol.json")"
ledger project \
  --definition "$learnings_definition" \
  --projection recall \
  --repo <repo> \
  --param "query=<artifact> <objective> failed attempt regression revert no-effect avoid" \
  --param "now=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --param search_limit=10 \
  --param drop_superseded=true \
  --format json
```

## Candidate Test

A learning may seed a Negative Evidence capture transaction only when it has:

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
