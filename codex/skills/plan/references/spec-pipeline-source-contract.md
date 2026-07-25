# Spec Pipeline Source Contract

PSC-v1 is the exact packet `$spec-pipeline` passes to `$plan` after a governed spec
is complete and plan-ready.

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

The Architectonic Thread travels inside `implementation_spec` and
`decision_packet`. PSC-v1 needs no new top-level architecture artifact.

## Authority

PSC-v1 is source authority, not implementation or mutation authority.

`$plan` may not change the semantic target, scope, non-goals, compatibility posture,
proof bar, or any `source_fixed` architectonic seam. If those fields are missing or
contradictory, `$plan` returns to `$spec-pipeline` or `$grill-me`.

`$plan` may iteratively refine:

```text
source_bounded seams
  inside the specification's observation, compatibility, authority, scope,
  and proof envelope

downstream_open seams
  inside the declared admissible candidate space and decision observations

plan_local seams
  when necessary to make the execution policy coherent
```

An architecture change inside those bounds is a normal policy-synthesis refinement,
not an automatic return to the specification.

## Normal flow

```text
SGR-v2 complete
-> PSC-v1 with Architectonic Thread
-> plan identity
-> joint architecture-policy synthesis fixed point
-> PSR-v1
-> <proposed_plan>
```

## Forbidden

```text
planning from PSC-v1 when lane=spec_only
planning from PSC-v1 when gate.plan_allowed=no
planning from PSC-v1 when the governed handoff is blocked
planning from PSC-v1 when next_owner != $plan
planning from PSC-v1 when do_not_execute_before is non-empty
silently repairing missing source semantics inside $plan
silently replacing a source_fixed architectonic seam
accepting a downstream_open seam without its admissible space and deciding observation
```

The executable projection is canonical JSON even when prose documents display the
schema in YAML for readability.
