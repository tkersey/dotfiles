---
name: goal-grind
description: "Execute exactly one lead-selected actuation-run step and return action evidence to the coordinator. Use after $goal-actuating has selected a node; do not create authority, choose scope, recurse, resolve review findings, or claim goal completion."
---

# Goal Grind

## Mission

Execute one already-selected step with the smallest owner-correct change.

~~~text
selected step
-> bounded action
-> verifier output
-> action result
-> return to $goal-actuating
~~~

## Input

~~~yaml
selected_step:
  run_id:
  step_id:
  owner_boundary:
  paths: []
  effect: inspect | edit | verify
  verifier: []
  review_resolution_ref:
~~~

For review-derived edits, `review_resolution_ref` and its selected work node are
required.

## Procedure

1. Verify the step is the current lead-selected node in the run.
2. Re-read the bounded paths before editing.
3. Make the smallest change that fixes the owning cause.
4. Prefer a replacement kernel when local repair would add semantic machinery
   or preserve a dominated abstraction.
5. Run the step verifier.
6. Return changed paths, commands, observations, and failure signature.
7. Stop. `$goal-actuating` owns evidence folding and continuation.

## Output

~~~yaml
step_action_result:
  run_id:
  step_id:
  owner_boundary:
  changed_paths: []
  commands: []
  observations: []
  result: passed | failed | blocked | regress
  failure_signature:
  public_effects: []
~~~

## Guardrails

- Do not select another step.
- Do not create or loosen the goal contract.
- Do not implement raw review prose.
- Do not perform public effects.
- Do not mark the node or goal complete; return evidence to the coordinator.
