---
name: spec-gate
description: "Decide whether a grill/handoff packet is complete enough for `$plan`, spec generation, or downstream mutation. Use for `$spec-gate`, is this ready to plan, block planning, handoff packet, decision packet, premature specs, no-grill justification, mutation gate, or underspecified questions, proof bar, scope, non-goals, rollout/rollback, and receipts."
metadata:
  version: "1.2.0"
  base_file_sha: "8689ba8bc8885737d470727319a95fe546985edd"
---

# Spec Gate

## Mission

Prevent `$plan` from discovering the objective and prevent mutation from outrunning decisions.

A plan is allowed only when the handoff packet is decision-complete or every remaining gap is explicitly assumed, deferred, owned, and defaulted.

Downstream mutation is allowed only after a complete spec has also passed invariant challenge, fresh-eyes pass, and lint. A pre-spec gate can allow planning while still keeping `mutation_allowed: false`.

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

Return `PLAN_ALLOWED: false` when any of these are true:

- the goal can still be interpreted in multiple materially different ways;
- scope or non-goals are missing;
- the implementer must choose architecture, compatibility posture, or proof bar;
- open questions exist without owner/default/consequence;
- success criteria are vague;
- proof is only scaffold proof when runtime/integration proof is required;
- rollback or abort posture is absent;
- the primary invariant is missing;
- the strictness profile is mismatched to risk;
- `grill_rounds: 0` and no concrete `no_grill_justification` is present;
- a plan, title, or Round Delta changed the objective without a locked user decision.

## Mutation gate

Emit `MUTATION_ALLOWED: false` for handoff-only gates unless the input already includes:

- a complete implementation spec;
- passing invariant challenge;
- passing fresh-eyes pass;
- passing spec lint;
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

Ask at most 1-3 next grill questions, each with a stable `snake_case` id and bounded choices.

## Script helper

For handoff packets saved to disk:

```bash
python codex/skills/spec-gate/scripts/spec_gate.py --strict-receipts path/to/handoff.md
```

The script is a conservative structural check. The model must still judge semantic completeness.
