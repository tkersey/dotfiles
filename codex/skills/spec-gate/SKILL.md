---
name: spec-gate
description: "Decide whether a grill/handoff packet is complete enough for `$plan` or spec generation. Use for `$spec-gate`, is this ready to plan, block planning, handoff packet, decision packet, or premature specs with underspecified questions, proof bar, scope, non-goals, or rollout/rollback."
---

# Spec Gate

## Mission

Prevent `$plan` from discovering the objective.

A plan is allowed only when the handoff packet is decision-complete or every remaining gap is explicitly assumed, deferred, owned, and defaulted.

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
- plan_allowed

## Blocking conditions

Return `PLAN_ALLOWED: false` when any of these are true:

- the goal can still be interpreted in multiple materially different ways;
- scope or non-goals are missing;
- the implementer must choose architecture, compatibility posture, or proof bar;
- open questions exist without owner/default/consequence;
- success criteria are vague;
- proof is only scaffold proof when runtime/integration proof is required;
- rollback or abort posture is absent;
- the primary invariant is missing;
- the strictness profile is mismatched to risk.

## Output

```text
PLAN_ALLOWED: true|false
strictness_profile: fast|balanced|strict
missing_fields:
material_open_questions:
blocking_risks:
recommended_defaults:
next_grill_questions:
```

Ask at most 1-3 next grill questions, each with a stable `snake_case` id and bounded choices.

## Script helper

For handoff packets saved to disk:

```bash
python codex/skills/spec-gate/scripts/spec_gate.py path/to/handoff.md
```

The script is a conservative structural check. The model must still judge semantic completeness.
