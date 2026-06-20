# Failure Forensics

## Sources

```text
bug-fix commits
reverts
incident notes
review findings
regressions
hot symbols
duplicate validations
fallback/compatibility paths
negative-ledger records
agent/session decision history
```

## Family record

```yaml
failure_family:
  family_id:
  governing_law_ids: []
  local_surfaces: []
  independent_witnesses: []
  recurring_signatures: []
  historical_repairs: []
  routes_that_failed: []
  unresolved_risk:
  evidence_refs: []
```

## Normalization

Do not stop at local labels:

```text
WASM parser bug
archive acknowledgement bug
restore scheduler bug
```

Ask whether they share a deeper rule such as authority binding, replay safety, ordering, identity, or transaction atomicity.

## Historical searches

Use:

```text
git log --grep
git log -S
git log -G
git blame
git show
revert pairs
repeated test names
```

Record scope and date.

## Route failure

A route becomes negative evidence when it was applied to the same governing law and materially failed to close the family.

Do not exclude adjacent routes from name similarity alone.
