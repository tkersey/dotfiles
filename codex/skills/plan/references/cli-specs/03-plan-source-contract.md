# 03 — Plan Source Contract / PSC-v1

PSC-v1 is the exact packet `$spec-pipeline` passes to `$plan` after a governed
spec is complete and plan-ready.

## Schema

```yaml
plan_source_contract:
  contract_version: PSC-v1
  source_owner: spec-pipeline
  spec_id:
  implementation_spec:
  decision_packet:
  sgr_v2:
    spec_governance_receipt:
      receipt_version: SGR-v2
      mode: full | repair
      lane: spec_to_plan
      status: complete
      gate:
        plan_allowed: yes
        material_open_questions_remaining: no
      lint:
        verdict: pass
        blocked_handoff: no
      execution_handoff:
        ready_for_plan: yes
        next_owner: $plan
        do_not_execute_before: []
      auto_plan_handoff:
        eligible: yes
        invocation: same_turn_tail_call
  proof_bar:
  non_goals: []
  target_branch:
  do_not_execute_before: []
```

## Authority

PSC-v1 is source authority, not implementation authority.

`$plan` may use it to compile an execution policy. `$plan` may not change the
semantic target, scope, non-goals, compatibility posture, or proof bar. If those
fields are missing or contradictory, `$plan` returns to `$spec-pipeline` or
`$grill-me`.

## Normal flow

```text
SGR-v2 complete
-> PSC-v1
-> ledger validate plan-source-contract
-> plan identity
-> policy synthesis fixed point
-> PSR-v1
-> <proposed_plan>
```

## Forbidden

```text
planning from PSC-v1 when lane=spec_only
planning from PSC-v1 when gate.plan_allowed=no
planning from PSC-v1 when lint failed or blocked handoff
planning from PSC-v1 when next_owner != $plan
planning from PSC-v1 when do_not_execute_before is non-empty
silently repairing missing spec decisions inside $plan
```

The executable projection is canonical JSON even when prose documents display
the schema in YAML for readability.
