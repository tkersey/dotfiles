---
name: goal-grind
description: "Execute exactly one lead-selected Zig actuation operation and return event-bound evidence to the coordinator. Use after $goal-actuating has prepared a capability; do not create authority, choose scope, recurse, resolve review findings, or claim goal completion."
---

# Goal Grind

## Mission

Consume one already-prepared capability with the smallest owner-correct action.

~~~text
prepared actuation-operation/v1
-> bounded effect
-> Zig kernel observation
-> action result
-> return to $goal-actuating
~~~

## Ephemeral input

~~~yaml
selected_operation:
  run_id:
  step_id:
  idempotency_key:
  owner_boundary:
  paths: []
  effect: inspect | edit | verify
  obligation_refs: []
  capability: AKC1-...
  review_resolution_ref: # review edits only
  owner_synthesis_ref: # review edits only
~~~

The raw capability exists only in the active executor. Never persist, quote,
log, or return it. Its digest and the complete admitted operation already live
in the append-only event chain.

## Procedure

Before the first native Ledger command in this operation, load `$ledger` and
complete `$ledger ensure`. After readiness, invoke `ledger` directly; the
prepared capability and native CLI remain the executable authority.

1. Confirm `ledger state --source actuation --run RUN_ID` is `prepared` and its
   pending step exactly matches the selected operation.
2. Re-read the bounded paths.
3. For `edit`, make only the owner-correct change on the admitted paths, then
   consume and observe it:

   ~~~bash
   ledger record --source actuation --run RUN_ID --capability "$CAPABILITY"
   ledger observe --source actuation --run RUN_ID --step STEP_ID
   ~~~

4. For `inspect` or `verify`, let the kernel execute the obligation-owned
   verifier:

   ~~~bash
   ledger execute --source actuation --run RUN_ID --capability "$CAPABILITY"
   ~~~

5. Return changed paths, commands, transition event digests, observations, and
   any failure signature. Stop after this one operation.

For a review edit, require `owner_synthesis_ref` to match the prepared
operation and current resolution. Execute the synthesis-owned node exactly as
selected; do not reconsider the synthesis disposition, choose repair strategy,
or split the node into finding-shaped work.

## Output

~~~yaml
operation_result:
  run_id:
  step_id:
  idempotency_key:
  owner_boundary:
  review_resolution_ref: # review edits only; copied unchanged
  owner_synthesis_ref: # review edits only; copied unchanged
  changed_paths: []
  commands: []
  kernel_event_refs: []
  observations: []
  result: passed | failed | blocked | regress
  failure_signature:
  public_effects: []
~~~

## Guardrails

- Do not prepare or select another operation.
- Do not create or loosen the GoalContract.
- Do not implement raw review prose.
- Do not perform public effects.
- Do not claim node or goal completion; return evidence to the coordinator.
