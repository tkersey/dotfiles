# Route discovery and exact gating

Read [store.md](store.md) before canonical operations. Use the same resolved
personal store throughout. History is shared across worktrees; current artifact
applicability is not.

## Discover before selecting a resembling retry

Describe the component, invariant, and failed mechanism in ordinary terms, not
only a newly invented route label:

```bash
ledger project \
  --definition "$negative_ledger_definition" \
  --projection route-candidates \
  --store-root "<context.store_root>" --store-id "<context.store_id>" \
  --param "query=component admission repeated body evaluation" \
  --param limit=8 \
  --format json
```

This projection folds current lifecycle state and ranks existing record text
with native token relevance. It returns the complete candidate records and their
status. It deliberately does not filter by the proposed route label or artifact:
those filters would hide precisely the evidence needed to discover an old route.
No candidate score or candidate status alone grants exclusion authority.

Inspect only candidates that could change the decision. Compare their observed
failure, declared scope, applicability conditions, and reopening criteria with
the present construction. A candidate may establish the prior name for the same
route; resemblance alone cannot establish identity. Use the recorded identity
only after confirming that the proposal actually instantiates that route/scope.

An empty or limited lexical result is not exhaustive recall. If a known failure
still seems missing, broaden mechanism/component terms or inspect a bounded
`current-records` projection in this store. Do not turn a label-only miss into
"no relevant failure is known," scan every project, or create a search service.

## Apply the exact gate

Establish the current immutable `artifact_state_id` and every material declared
scope identity. A Git commit is optional provenance and does not identify dirty
code, fixtures, or configuration; include the relevant immutable surface when
those facts affect the claim. Retain readable provenance in `artifact_state_label`.

```bash
ledger project \
  --definition "$negative_ledger_definition" \
  --projection route-gate \
  --store-root "<context.store_root>" --store-id "<context.store_id>" \
  --param "artifact=<current-immutable-artifact-state-id>" \
  --param "identity=<established-declared-scope-identity>" \
  --format json
```

Pass the established identity for the record's exact, route, route-family,
cluster, authority-model, distinction-pattern, or proof-pattern scope. Never
substitute an old artifact ID merely to make a candidate match the gate.

Gate exit codes retain their exact meaning:

- `0`: no active exact exclusion for these supplied identities; no correctness
  or exhaustive-recall claim follows.
- `2`: an active exact artifact/identity match; confirm its applicability
  conditions before suppressing the proposed route.
- `3`: canonical context or store unavailable/invalid, not an empty history.

`route-candidates` returns `0` for valid results, whether empty or populated. A
nonzero result is a read failure, never an exclusion decision.

An active witnessed exclusion may block only when the proposal matches its
declared scope and current applicability. A similar viable route or a different
artifact is not banned by resemblance. Inapplicability here does not justify
globally marking a record stale for another artifact. Reopening, narrowing, and
supersession retain their source-owned proof obligations. Reuse already inspected
unchanged records; recheck when relevant source or artifact facts change.
