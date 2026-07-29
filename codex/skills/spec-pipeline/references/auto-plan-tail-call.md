# Automatic `$plan` Tail-Call

`$spec-pipeline` owns the decision that a spec is ready for planning. `$plan`
owns execution-policy synthesis. This reference makes the seam automatic without
letting `$spec-pipeline` emit plan artifacts.

## Lane selection before the predicate

Before the final SGR-v2 exists, choose the lane with the rule in
[lane-selection.md](lane-selection.md): in `full` mode, default to `spec_to_plan`
unless the user explicitly requested spec-only output or a material gate blocks
planning.

Explicit `$spec-pipeline` invocation is not a request for `spec_only`. If the
run completes with a plan-ready governed spec, the lane must remain
`spec_to_plan` and this tail-call predicate decides whether same-turn `$plan`
runs.

## Predicate

First validate the exact final SGR-v2 under
`spec-pipeline/spec-governance-receipt`. Then run `$plan` only when every semantic
predicate holds:

```text
mode in {full, repair}
status = complete
lane = spec_to_plan
authoritative_brief.drift_detected = no
phase_presence.gate = yes
phase_presence.implementation_spec = yes
phase_presence.challenge = yes
phase_presence.fresh_eyes = yes
phase_presence.execution_handoff = yes
gate.plan_allowed = yes
gate.material_open_questions_remaining = no
fresh_eyes.drift_detected = no
subagents.open_at_end = 0
execution_control.plan_allowed = yes
execution_control.execution_handoff = yes
execution_handoff.ready_for_plan = yes
execution_handoff.next_owner = $plan
execution_handoff.do_not_execute_before = []
auto_plan_handoff.eligible = yes
auto_plan_handoff.invocation = same_turn_tail_call
```

## Tail-call packet

Pass this compact JSON source contract to `$plan`:

```json
{
  "plan_source_contract": {
    "contract_version": "PSC-v1",
    "source_owner": "spec-pipeline",
    "spec_id": "<spec-id>",
    "implementation_spec": {},
    "decision_packet": {},
    "sgr_v2": {
      "spec_governance_receipt": {}
    },
    "proof_bar": {},
    "non_goals": [],
    "target_branch": "<target-branch>",
    "do_not_execute_before": []
  }
}
```

Embed the exact SGR-v2 object and validate the completed packet through
`spec-pipeline/plan-source-contract` before tail-calling Plan. Ledger structural
validity does not grant the tail-call; Spec Pipeline's semantic receipt values do.

`$plan` synthesizes that source contract into one EPG-v1 policy and validates the
exact result through Plan's passive Ledger definition. Plan emits no synthesis
receipt or execution handoff.

## Fail-closed cases

Do not auto-run `$plan` when:

- user explicitly requested `spec_only`, `spec only`, `no plan`, or equivalent;
- mode is `gate-only` or `challenge-only`;
- status is `blocked`, `drift`, `audit-only`, or `partial`;
- lane is not `spec_to_plan` for a legal blocker recorded in the receipt;
- material questions remain;
- fresh-eyes returned to grill or detected drift;
- any subagent remains open;
- `next_owner` is not `$plan`;
- `do_not_execute_before` is non-empty;
- `auto_plan_handoff.eligible = no` with a concrete blocker other than “the user did not separately ask for `$plan`.”

If same-turn loading of `$plan` is unavailable, emit:

```text
AUTO_PLAN_HANDOFF_REQUIRED
reason: same-turn tail-call unavailable in this runtime
next_owner: $plan
```

That marker means automation failed; it does not authorize implementation.
It must not be replaced with `spec_only` merely because the tail-call could not
run.
