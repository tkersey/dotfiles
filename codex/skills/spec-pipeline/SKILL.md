---
name: spec-pipeline
description: >
  Turn ambiguous project, architecture, implementation, or product requests into decision-complete specs by researching first, grilling only judgment calls, gating readiness before planning, compiling a spec, running one invariant challenge, and linting the final artifact. Use when prompts say "$spec-pipeline", "write a spec", "turn this plan into a spec", "grill me then spec", "spec automation", or when $grill-me and $plan need a strict handoff boundary.
---

# Spec Pipeline

## Mission

Produce implementation-ready specifications without letting planning become objective discovery.

Run this state machine:

```text
Evidence Brief -> Grill Decision Packet -> Spec Handoff Packet -> Implementation Spec -> Invariant Challenge -> Spec Lint -> Execution Handoff
```

## Non-negotiable boundary

- `$grill-me` owns uncertainty, contradiction, priority, and scope.
- `$plan` owns execution shape, interfaces, tests, rollout, rollback, and proof.
- If material decisions are missing, do not produce a spec or plan.
- If a plan starts discovering the objective, route back to grilling or gating.

## Step 1: Research first

Inspect artifacts before asking questions: code, docs, plans, tests, tickets, logs, diagrams, schemas, config, session history, and supplied reports.

Do not ask the user for discoverable facts. Ask only for judgment calls, priorities, trade-offs, unavailable context, or explicit authority.

When useful, ask the parent to spawn read-only subagents:

```text
Spawn spec_evidence_cartographer, spec_constraint_miner, and spec_proof_surface_mapper to gather current-state evidence, hard constraints, and proof surfaces, then synthesize their packets before asking questions.
```

## Step 2: Produce an Evidence Brief

Use this exact shape:

```text
Evidence Brief
- Current state:
- Relevant surfaces:
- Existing behavior:
- Known constraints:
- Obvious risks:
- Proof surfaces already available:
- Facts not yet verified:
- Judgment calls still needed:
```

Keep it concise. The brief is not the spec.

## Step 3: Grill for decisions

Ask 1-3 bounded questions per round using `$grill-me` style. Each question must be atomic and have a stable `snake_case` id. Put the recommended option first.

Ask questions only for material gaps in:

- problem and root cause;
- user, maintainer, stakeholder, and owner;
- scope and non-goals;
- primary invariant;
- compatibility posture;
- rollout and rollback posture;
- success criteria and proof bar;
- dependencies, interfaces, and data boundaries;
- edge cases, failure modes, abuse cases, and second-order effects.

## Step 4: Maintain the Grill Decision Packet

Maintain this privately until the user has answered enough. When ready to gate, emit it exactly:

```yaml
spec_decision_packet:
  goal:
  problem_layer:
  target_user_or_maintainer:
  scope:
  non_goals:
  locked_decisions:
  tradeoffs_accepted:
  primary_invariant:
  success_criteria:
  proof_bar:
  compatibility_posture:
  rollout_rollback_posture:
  open_questions:
  deferred_questions:
  default_assumptions:
```

Open questions are allowed only if each has an owner, default action, and consequence.

## Step 5: Gate before planning

Before `$plan`, run the handoff sentence:

```text
We are building X, for Y, by changing Z, while explicitly not doing A/B/C, and success means P/Q/R proofs pass.
```

If this sentence is incomplete, continue grilling.

If using files, run:

```bash
python codex/skills/spec-gate/scripts/spec_gate.py path/to/handoff.md
```

Planning is allowed only when `plan_allowed=true` and no material open question lacks a default or deferral rationale.

## Step 6: Compile the Implementation Spec

When planning is allowed, produce an implementation spec, not a prose roadmap.

Required sections:

1. Objective
2. Context / Current State
3. Locked Decisions
4. Scope
5. Non-Goals
6. Requirements
7. Design / Implementation Approach
8. Dependency-Ordered Implementation Sequence
9. Requirement-to-Test Traceability
10. Proof Commands
11. Risks and Edge Cases
12. Rollback / Abort Criteria
13. Binary Done-State
14. Open / Deferred Items

## Step 7: Run one invariant challenge

After the first spec is generated, run exactly one strongest project-specific challenge.

Examples:

- Does this create a second authority?
- Does this preserve zero-cost abstraction?
- Does this prove runtime behavior, not just scaffold shape?
- Does this preserve public API compatibility?
- Does this have a real rollback path?

If the challenge changes architecture or proof, regenerate the affected spec sections. If it only adds preference-level polish, record it as non-blocking.

## Step 8: Lint

If using files, run:

```bash
python codex/skills/spec-lint/scripts/spec_lint.py path/to/spec.md
```

Fail the spec if:

- material open questions remain without owner/default/consequence;
- non-goals are missing;
- proof bar is vague;
- major requirements are not mapped to tests;
- rollback or abort criteria are missing;
- implementation order is not dependency-aware;
- the primary invariant is missing;
- long audit sections repeat rationale without changing implementation behavior.

## Step 9: Execution handoff

Only after lint passes, hand off to `$st`, `$select`, `$fixed-point-driver`, `$tk`, `$ship`, or ordinary implementation flow.

Execution must not reopen locked decisions unless new evidence invalidates the spec.

## Output discipline

- If material unknowns remain: ask questions only.
- If the handoff is incomplete: emit gate failure and next questions.
- If the handoff is complete: produce the spec.
- If lint fails: return to the smallest necessary question or section rewrite.
- Do not hide assumptions. Classify each as answered, researched, assumed, deferred, or immaterial.
