# Mesh Failure Taxonomy

Use this taxonomy for failure reporting, retry policy, and stop/go decisions. Codes are stable IDs and should not be renamed casually.

## Runtime transport/format failures

- `worker_turn_hang_before_output`
  - Trigger: worker fails to emit first artifact within timeout.
  - Action: retry once; if repeated, fallback swarm size or block task.
- `no_diff_parsed`
  - Trigger: worker output fails strict artifact parser contract.
  - Action: one strict follow-up; if still invalid, block with this code.
- `no_patch_returned`
  - Trigger: worker explicitly returns no patch/no diff.
  - Action: keep task open and route for reformulation or escalation.
- `no_response`
  - Trigger: transport/lifecycle timeout with no usable output.
  - Action: retry once, then fallback swarm; block if unresolved.

## Team-level quality and coordination failures

- `tk_shape_drift`
  - Trigger: coder output omits required TK sections in non-strict mode.
  - Action: reject artifact and request contract-complete rewrite.
- `proof_gap`
  - Trigger: completion attempted without executed proof signal.
  - Action: fail closed; block until proof is executed and recorded.
- `safety_regression`
  - Trigger: fixer finds unresolved invariant/safety risk.
  - Action: fixer returns `blocked_safety`; no promotion.
- `adjudication_deadlock`
  - Trigger: conflict class cannot be resolved after fallback process.
  - Action: block with explicit deadlock record.
- `state_desync`
  - Trigger: observed task state diverges from durable `$st` state.
  - Action: reconcile against `$st`; pause downstream promotion.
- `scope_collision`
  - Trigger: concurrent tasks overlap exclusive lock roots.
  - Action: serialize conflicting tasks and reopen affected units.
- `rubric_misgrade`
  - Trigger: completion accepted with invalid rubric math/threshold logic.
  - Action: invalidate completion and rerun rubric evaluation.

## Gate-related failures

- `missing_validation`
  - Trigger: validation commands absent when required.
  - Action: block and request explicit validation signal.
- `validation_failed`
  - Trigger: executed validation command fails.
  - Action: set blocked/rework; attach failing command evidence.
- `no_consensus`
  - Trigger: vote threshold not met after retries.
  - Action: block and publish decision log.
- `ambiguous_integration`
  - Trigger: patch application or integration result is not deterministically interpretable.
  - Action: block and request manual disambiguation.
- `wait_timeout_without_close`
  - Trigger: a wait cycle times out or resolves without a matching close sweep for the affected worker(s).
  - Action: run one retry-ladder attempt with a smaller prompt, run a close sweep, and block/rework if unresolved.
- `lifecycle_signal_mismatch`
  - Trigger: lifecycle counters diverge (`spawned`/`fanout`, `wait`, and `closed` do not reconcile).
  - Action: stop promotion, emit this code, reconcile mismatched ids, and rerun only the affected scope when safe.

## Reporting requirements

Every blocked/completed decision should reference one primary failure code (or `none`) and include evidence lines. Do not collapse multiple failures into a generic status.
