# 03 — Plan Source Contract / PSC-v1

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

The Architectonic Thread is carried inside `implementation_spec` and
`decision_packet`; PSC-v1 adds no second architecture artifact.

## Authority

PSC-v1 is source authority, not implementation or mutation authority.

`$plan` may not change the semantic target, scope, non-goals, compatibility posture,
proof bar, or a `source_fixed` architectonic seam. If those fields are missing or
contradictory, `$plan` returns to `$spec-pipeline` or `$grill-me`.

PSC-v1 carries `source_fixed`, `source_bounded`, and `specification_local`
authority. EPG-v1 does not copy those labels mechanically:

| PSC-v1 state | EPG-v1 state | Preservation law |
|---|---|---|
| `source_fixed` | `source_fixed` | Preserve the seam or return to source authority. |
| `source_bounded` | `source_bounded` | Refine only inside the carried observation, compatibility, scope, proof, and candidate envelope. |
| `specification_local` with a settled disposition | `source_fixed` | The governed spec has accepted the decision; Plan may encode it but may not reopen it. |
| `specification_local` + `downstream_open` | `plan_local` + `evidence_conditioned` | The spec explicitly delegates the bounded choice to Plan. |
| `source_bounded` + `downstream_open` | `source_bounded` + `evidence_conditioned` | Plan may choose only inside the source-bounded envelope. |

`source_fixed + downstream_open` is contradictory and invalid. A
`downstream_open` translation copies its admissible candidate space into
`candidate_movements`, deciding observations into `decision_observation_refs`,
forbidden outcomes and invalidators into EPG invalidators and safety routes, and
its safe default or blocker into a policy rule or terminal. No constraint may be
dropped during translation.

`selected` and `evidence_conditioned` remain unchanged.
`underdetermined` or `obstructed` cannot become a compile-ready EPG disposition;
Plan returns the named obstruction instead. An `obstructed` seam also makes the
spec ineligible for the automatic Plan tail-call.

Within that translation, `$plan` may iteratively refine `source_bounded` and
derived `plan_local` seams. Such an architecture change is a normal synthesis
refinement only when the resulting architecture-policy square commutes.

## Normal flow

```text
SGR-v2 complete
-> PSC-v1 with Architectonic Thread
-> plan identity
-> joint architecture-policy synthesis fixed point
-> canonical EPG-v1 emission
-> Ledger validation under plan/execution-policy-graph
-> <proposed_plan>
```

## Forbidden

```text
planning from PSC-v1 when lane=spec_only
planning from PSC-v1 when gate.plan_allowed=no
planning from PSC-v1 when the governed handoff is blocked
planning from PSC-v1 when next_owner != $plan
planning from PSC-v1 when do_not_execute_before is non-empty
silently repairing missing source decisions inside $plan
silently replacing a source_fixed architectonic seam
accepting a downstream_open seam without its admissible space and deciding observation
mapping a settled specification_local seam to plan_local
dropping a downstream_open bound during EPG translation
```

The canonical source projection is JSON even when prose documents display the
schema in YAML for readability.
