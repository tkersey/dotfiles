---
name: spec-pipeline
description: >
  Turn ambiguous project, architecture, implementation, or product requests into decision-complete implementation specs by researching first, asking only material judgment questions, gating readiness before planning, compiling a spec, running one invariant challenge, and linting the final artifact. Use when prompts say "$spec-pipeline", "write a spec", "turn this plan into a spec", "grill me then spec", "spec automation", or when $grill-me and $plan need a strict handoff boundary. Never emit a proposed_plan block.
metadata:
  version: "1.1.0"
  hardened_from: "2026-05-08 spec-pipeline forensics report"
  activation_cost: high
  default_depth: full
  requires_explicit_invocation: false
---

# Spec Pipeline

## Mission

Produce implementation-ready specifications without letting planning become objective discovery.

`spec-pipeline` is a state machine, not a prose style. Its job is to keep these phases visibly separated:

```text
Evidence Brief -> Grill Decision Packet -> Gate Result -> Implementation Spec -> Invariant Challenge -> Spec Lint -> Execution Handoff
```

The skill succeeds only when the user, a later agent, or a validator can tell which phase was completed, which facts were researched, which decisions were locked, which assumptions were defaulted, and why planning is or is not allowed.

## Hard output boundary

Never wrap a `spec-pipeline` output in `<proposed_plan>`. That block is reserved for `$plan`.

A complete `spec-pipeline` output must be one of exactly two shapes:

1. **Gate failure / questions-only**: no spec, no plan, only missing fields, drift warnings if any, and 1-3 next questions.
2. **Implementation spec handoff**: plain markdown with Evidence Brief, Gate Result, `spec_decision_packet`, required implementation spec sections, one Invariant Challenge, Spec Lint Result, and a brief Execution Handoff.

Do not emit `$plan` iteration scaffolding such as `Round Delta`, `Iteration Change Log`, `Decision Impact Map`, `Adversarial Findings`, `Contract Signals`, dependency rows, execution waves, or `<proposed_plan>` tags. `$plan` owns dependency-ordered execution planning after this skill passes gate, challenge, and lint.

If the user explicitly asks for `$plan` and `$spec-pipeline` at the same time, run `spec-pipeline` first. End with an execution handoff that says `$plan` may now consume the spec. Do not combine the artifacts.

## Boundary with neighboring skills

- `$grill-me` owns unresolved decisions, contradictions, priorities, non-goals, and authority questions.
- `spec-pipeline` owns decision extraction, readiness gating, exact spec compilation, invariant challenge, and spec lint.
- `$plan` owns execution shape, dependency ordering, file-by-file implementation sequencing, rollback sequencing, and proof commands after the spec is ready.
- `spec-gate` owns readiness judgment before planning.
- `spec-challenge` owns exactly one strongest invariant/adversarial challenge.
- `spec-lint` owns implementation-readiness lint after the spec exists.

Do not let planning discover the objective. Do not let grilling rediscover facts already supplied or available from artifacts. Do not let a spec become an implementation plan.

## Decision-complete fast path

If the user supplies all of the following, treat the brief as presumptively sufficient and do not ask `$grill-me` questions unless a material contradiction remains:

- goal;
- target system or repository surface;
- scope;
- non-goals;
- locked authority boundary or primary invariant;
- acceptance criteria or success criteria;
- proof commands, proof surfaces, or validation bar.

In this fast path, research discoverable facts, emit the exact Evidence Brief, produce the decision packet, run the gate, compile the spec, run one challenge, lint it, and hand off. Questions are allowed only for contradictions, missing authority, missing secrets, irreversible approval, or a proof bar that cannot be inferred.

When prior plan or grill churn exists, anchor the fast path to the user's original or latest restated authoritative brief. Classify earlier mismatched questions or plan directions as `invalidated`, `deferred`, or `immaterial` instead of silently carrying them forward.

## Anti-drift checkpoint

Before asking further questions, emitting a spec, or handing off to `$plan`, compare the current candidate objective against the original authoritative user brief.

Check these fields:

- target;
- scope;
- non-goals;
- authority boundary;
- compatibility posture;
- proof bar;
- rollout/rollback posture;
- public API or user-visible behavior boundary.

If the candidate changes any of those fields without explicit user approval, stop and emit:

```text
SPEC_PIPELINE_DRIFT_WARNING
changed_field:
original_brief_value:
candidate_value:
why_this_matters:
action: ask_user | restore_original_brief | defer_change
```

Do not continue to questions, spec, lint, or plan handoff until the drift is resolved.

## Research first

Inspect available artifacts before asking questions: code, docs, plans, tests, tickets, logs, diagrams, schemas, config, session history, and supplied reports.

Do not ask the user for discoverable facts. Ask only for judgment calls, unavailable context, explicit authority, irreversible approvals, private constraints, or conflicts that artifacts cannot resolve.

When useful and available, ask the parent to spawn read-only subagents:

```text
Spawn spec_evidence_cartographer, spec_constraint_miner, and spec_proof_surface_mapper to gather current-state evidence, hard constraints, and proof surfaces, then synthesize their packets before asking questions.
```

## Exact Evidence Brief contract

The Evidence Brief must contain exactly these labels, in this order. Do not rename, omit, reorder, or merge labels:

```text
## Evidence Brief
- Current state:
- Relevant surfaces:
- Existing behavior:
- Known constraints:
- Obvious risks:
- Proof surfaces already available:
- Facts not yet verified:
- Judgment calls still needed:
```

Keep each field concise but concrete. Use `none` only when the field was actually considered. Use `not yet verified` for facts that matter but were not inspected. Do not hide uncertainty by omitting a label.

## Grill only material decisions

Ask 1-3 bounded questions per round using `$grill-me` style only when the Evidence Brief and anti-drift checkpoint show that material decisions remain.

Each question must be atomic and have a stable `snake_case` id. Put the recommended option first when a recommendation is justified by evidence.

Ask only for material gaps in:

- problem and root cause;
- user, maintainer, stakeholder, and owner;
- scope and non-goals;
- primary invariant or authority boundary;
- compatibility posture;
- rollout and rollback posture;
- success criteria and proof bar;
- dependencies, interfaces, and data boundaries;
- edge cases, failure modes, abuse cases, and second-order effects.

Do not ask questions merely to make the interaction feel rigorous. If the user's brief is decision-complete, say `Judgment calls still needed: none` and continue.

If structured UI answers are ambiguous, incomplete, or fail to capture the needed free-form correction, ask one normal text question that names the missing decision. Do not keep looping through ambiguous UI selections.

## Decision packet

Maintain the decision packet internally while researching and grilling. When ready to gate, emit it exactly as YAML:

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

Rules:

- `open_questions` are allowed only if each has an owner, default action, consequence, and reason it does not block the spec.
- `default_assumptions` must distinguish inferred defaults from user-locked decisions.
- If the user corrected drift, include the correction as a locked decision or invalidated prior assumption.
- Do not smuggle implementation choices into the packet unless the user locked them or artifacts prove they are required.

## Gate before spec and before planning

Before compiling the spec, run the handoff sentence:

```text
We are building X, for Y, by changing Z, while explicitly not doing A/B/C, and success means P/Q/R proofs pass.
```

Then emit a visible Gate Result:

```text
## Gate Result
plan_allowed: true|false
script_gate: passed|failed|skipped
script_gate_reason:
material_open_questions:
defaults:
deferrals:
handoff_sentence:
```

Planning is allowed only when `plan_allowed: true` and no material open question lacks an owner/default/consequence.

When feasible, write the handoff packet to a temporary file and run the structural helper before final output:

```bash
uv run python codex/skills/spec-gate/scripts/spec_gate.py <handoff-file>
```

If repo policy or environment requires a different runner, use the repo-approved runner. If the script is unavailable, the workspace is read-only, or the spec is produced in a context without shell/filesystem access, set `script_gate: skipped` and state the concrete reason. A skipped script is allowed only when semantic gating is still performed visibly.

## Gate failure output

If the handoff is incomplete, do not produce a spec and do not produce a plan. Emit only:

```text
SPEC_PIPELINE_GATE_FAILURE
missing_fields:
material_open_questions:
blocking_risks:
recommended_defaults:
next_grill_questions:
```

Ask at most 1-3 next questions. Do not include implementation sequence, plan waves, or `<proposed_plan>`.

## Implementation spec contract

When planning is allowed, produce an implementation spec, not a prose roadmap and not a `$plan` artifact.

Required sections, in this order:

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

The dependency-ordered sequence is allowed because implementers need ordering context, but keep it spec-level. Do not turn it into `$plan` iterations, task rows, or execution waves.

## Invariant challenge

After the first spec is generated, run exactly one strongest project-specific challenge.

Choose the challenge most likely to invalidate the spec's primary invariant. Examples:

- Does this create a second authority?
- Does this preserve zero-cost abstraction?
- Does this prove runtime behavior, not just scaffold shape?
- Does this preserve public API compatibility?
- Does this have a real rollback path?
- Does this fail closed if dependencies are stale or missing?

Emit:

```text
## Invariant Challenge
primary_invariant:
strongest_challenge:
affected_sections:
classification: architecture_change_required|proof_change_required|scope_change_required|risk_mitigation_required|preference_only
required_change:
regenerate_spec: yes|no
```

If the challenge changes architecture, proof, scope, or risk mitigation, revise only the affected spec sections and then lint the revised spec. If it is preference-only, record it as non-blocking.

## Spec lint

After the challenge, lint the spec. Prefer script-backed lint even for inline final specs.

When feasible, write the spec to a temporary file and run:

```bash
uv run python codex/skills/spec-lint/scripts/spec_lint.py <spec-file>
```

If repo policy or environment requires a different runner, use the repo-approved runner. If the script is unavailable, the workspace is read-only, or no file access exists, set `script_lint: skipped` and state the reason.

Always emit:

```text
## Spec Lint Result
SPEC_READY: true|false
script_lint: passed|failed|skipped
script_lint_reason:
blocking_errors:
material_risks:
preferences:
missing_sections:
unmapped_requirements:
rollback_gaps:
proof_gaps:
churn_signals:
recommended_next_action: proceed_to_plan|return_to_grill|revise_spec|run_spec_challenge
```

Fail the spec if:

- material open questions remain without owner/default/consequence;
- non-goals are missing;
- proof bar is vague;
- major requirements are not mapped to tests;
- rollback or abort criteria are missing;
- implementation order is not dependency-aware;
- the primary invariant is missing;
- long audit sections repeat rationale without changing implementation behavior;
- the spec changes the objective relative to the authoritative brief;
- the output contains `<proposed_plan>`.

A manual lint pass is lower proof than script-backed lint. If manual lint is used, say why script lint was skipped and keep the lint fields exact.

## Execution handoff

Only after Gate Result, Invariant Challenge, and Spec Lint Result pass may the output include an execution handoff.

Keep it short:

```text
## Execution Handoff
ready_for_plan: yes|no
next_owner: $plan|implementation|grill-me|spec-pipeline
handoff_summary:
do_not_execute_before:
```

`spec-pipeline` may say that `$plan` should consume the spec next. It must not convert the spec into a `$plan` artifact.

## Output templates

### Complete spec handoff

```markdown
# <Spec Title>

## Evidence Brief
- Current state:
- Relevant surfaces:
- Existing behavior:
- Known constraints:
- Obvious risks:
- Proof surfaces already available:
- Facts not yet verified:
- Judgment calls still needed:

## Gate Result
plan_allowed: true
script_gate: passed|skipped
script_gate_reason:
material_open_questions:
defaults:
deferrals:
handoff_sentence:

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

## 1. Objective

## 2. Context / Current State

## 3. Locked Decisions

## 4. Scope

## 5. Non-Goals

## 6. Requirements

## 7. Design / Implementation Approach

## 8. Dependency-Ordered Implementation Sequence

## 9. Requirement-to-Test Traceability

## 10. Proof Commands

## 11. Risks and Edge Cases

## 12. Rollback / Abort Criteria

## 13. Binary Done-State

## 14. Open / Deferred Items

## Invariant Challenge
primary_invariant:
strongest_challenge:
affected_sections:
classification:
required_change:
regenerate_spec:

## Spec Lint Result
SPEC_READY:
script_lint:
script_lint_reason:
blocking_errors:
material_risks:
preferences:
missing_sections:
unmapped_requirements:
rollback_gaps:
proof_gaps:
churn_signals:
recommended_next_action:

## Execution Handoff
ready_for_plan:
next_owner:
handoff_summary:
do_not_execute_before:
```

### Gate failure / questions-only

```text
SPEC_PIPELINE_GATE_FAILURE
missing_fields:
material_open_questions:
blocking_risks:
recommended_defaults:
next_grill_questions:
```

### Drift warning

```text
SPEC_PIPELINE_DRIFT_WARNING
changed_field:
original_brief_value:
candidate_value:
why_this_matters:
action:
```

## Optional output validator

For a saved `spec-pipeline` output, use:

```bash
uv run python codex/skills/spec-pipeline/scripts/check_spec_pipeline_output.py path/to/spec-output.md
```

This helper checks the mechanical contract: no `<proposed_plan>`, exact Evidence Brief labels, Gate Result presence, decision packet presence, required spec sections, Invariant Challenge, and Spec Lint Result. It is not a semantic substitute for model judgment.

## Success criteria

A successful `spec-pipeline` run leaves the user with:

- no `<proposed_plan>` output;
- exact Evidence Brief labels;
- visible Gate Result;
- explicit decision packet;
- implementation spec with all required sections;
- one strongest invariant challenge;
- script-backed or explicitly skipped lint;
- no unresolved objective drift;
- a short execution handoff that tells `$plan` what to consume next.
