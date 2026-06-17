---
name: spec-gate
description: "Decide whether a grill/handoff packet is complete enough for `$plan`, spec generation, or downstream mutation; emit spec_gate_receipt. Use for `$spec-gate`, ready to plan, block planning, handoff/decision packet, premature specs, no-grill justification, mutation gate, underspecified questions, proof bar, scope, non-goals, rollout/rollback, receipts, or SGATE-v1."
metadata:
  version: "1.3.0"
---

# Spec Gate

## Mission

Prevent `$plan` from discovering the objective and prevent mutation from outrunning decisions.

A plan is allowed only when the handoff packet is decision-complete or every remaining gap is explicitly assumed, deferred, owned, and defaulted.

Downstream mutation is allowed only after a complete spec has also passed invariant challenge, fresh-eyes pass, spec lint, and governance receipt.

## Readiness test

Planning is allowed only when this sentence can be completed concretely:

```text
We are building X, for Y, by changing Z, while explicitly not doing A/B/C, and success means P/Q/R proofs pass.
```

## Required fields

- goal
- problem_layer
- target_user_or_maintainer
- scope
- non_goals
- locked_decisions
- primary_invariant
- success_criteria
- proof_bar
- compatibility_posture
- rollout_rollback_posture
- default_assumptions
- clarification receipt: either `grill_rounds > 0` or concrete `no_grill_justification`
- plan_allowed

## Blocking conditions

Return `PLAN_ALLOWED: false` when any are true:

- goal can still be interpreted in multiple materially different ways;
- scope or non-goals are missing;
- implementer must choose architecture, compatibility posture, or proof bar;
- open questions exist without owner/default/consequence;
- success criteria are vague;
- proof is scaffold-only when runtime/integration proof is required;
- rollback or abort posture is absent;
- primary invariant is missing;
- strictness profile is mismatched to risk;
- `grill_rounds: 0` and no concrete `no_grill_justification` is present;
- a plan, title, or Round Delta changed the objective without a locked user decision.

## Mutation gate

Emit `MUTATION_ALLOWED: false` for handoff-only gates unless the input already includes:

- complete implementation spec;
- passing invariant challenge;
- passing fresh-eyes pass;
- passing spec lint;
- spec governance receipt;
- no unaccounted subagents;
- proof and rollback surfaces.

When only a decision packet is being gated, planning may be allowed while mutation remains blocked.

## Output

```text
PLAN_ALLOWED: true|false
MUTATION_ALLOWED: true|false
strictness_profile: fast|balanced|strict|campaign
missing_fields:
material_open_questions:
blocking_risks:
recommended_defaults:
clarification_receipt:
next_grill_questions:
```

Also emit:

```yaml
spec_gate_receipt:
  receipt_version: SGATE-v1
  plan_allowed: yes | no
  mutation_allowed_pre_spec: no
  script_gate: passed | failed | skipped
  gate_changed_decision: yes | no
  gate_blocked_plan: yes | no
  gate_defaulted_decisions: []
  material_open_questions_remaining: yes | no
  pass_no_delta: yes | no
  reason: "..."
```

Ask at most 1-3 next grill questions, each with a stable `snake_case` id and bounded choices.

## Script helper

For handoff packets saved to disk:

```bash
python codex/skills/spec-gate/scripts/spec_gate.py --strict-receipts path/to/handoff.md
```

The script is a conservative structural check. The model must still judge semantic completeness.

## Hard rules

- Do not allow mutation from a pre-spec gate.
- Do not count gate success without `spec_gate_receipt`.
- Do not ask questions for discoverable facts.
- Do not allow planning if the handoff sentence is vague.
