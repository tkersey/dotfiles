# Fixed-Point Driver Integration

Use `negative-ledger` as an optional companion skill for `fixed-point-driver` when prior failed attempts would materially change routing.

## When to invoke

Invoke `negative-ledger` or `negative-ledger-mapper` when at least one is true:

- the user mentions prior failed attempts, reverted changes, benchmark regressions, repeated hypotheses, or dead ends
- commit history, review comments, logs, or `$learnings` suggest a previous route failed
- a prior loop produced a no-effect result, local/global regression, unsoundness finding, or review rejection
- the task is optimization-heavy, debugging-heavy, flaky-test-heavy, migration-heavy, or design-search-heavy
- the one-change challenge risks selecting a previously disconfirmed route

Do not invoke it for simple one-pass implementation tasks with no prior attempts and no search-space uncertainty.

## Root versus specialist authority

`fixed-point-driver` root owns:

- authoritative fmt/lint/build/test commands
- final closure verdict
- canonical ledgers
- deciding whether to reopen the loop

`negative-ledger-mapper` may:

- read current campaign ledgers, `$learnings` recall output, logs, review comments, diffs, and commit/revert evidence
- classify prior failed attempts
- mark evidence active, stale, superseded, reopened, or unknown
- recommend active exclusions and adjacent search frontier

`negative-ledger-mapper` must not:

- edit files
- run final proof gates
- claim closure
- veto current work without current-state applicability evidence
- append to `$learnings` during read-only specialist mapping

## Recommended fixed-point sequence

1. Establish `artifact_state_id` and `artifact_state_label`.
2. Run `negative-ledger source-preflight` if negative evidence is likely material.
3. Optionally launch `negative-ledger-mapper` with a narrow scope.
4. Validate the specialist packet: state ID, scope, footer, and absence of transport wrappers.
5. Normalize accepted entries into the canonical Negative Evidence Ledger.
6. Use active entries to avoid exact repeated dead ends.
7. Use stale/reopened entries to plan current proof, not to suppress work.
8. Before the one-change challenge, check whether the candidate matches active negative evidence.
9. After a witnessed failed/remediated loop, capture durable negative evidence through `$learnings` when transferable.

## Specialist packet footer

Every packet must end with:

```md
artifact_state_id: ...
artifact_state_label: ...
scope: ...
top_material_signals:
  - ...
unresolved_signals:
  - ...
agreement_pressure: aligned | mixed | conflicting | unknown
stale: yes | no | unknown
final_call: ...
```

Reject the packet as `transport-invalid`, `wrong-scope`, or `stale` when it violates the common specialist packet rules.
