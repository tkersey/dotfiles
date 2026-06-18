---
name: spec-pipeline
description: "Canonical current-spec engine. Turn ambiguous project, architecture, implementation, or product requests into decision-complete implementation specs; or operate narrowly in gate-only, challenge-only, lint-only, or repair mode. Use for `$spec-pipeline`, write a spec, is this ready to plan, pressure-test this spec, lint this spec, repair a failed spec gate, spec automation, strict `$grill-me` to `$plan` handoff, SGR-v2 governance receipts, or legacy spec-gate/spec-challenge/spec-lint intent. Never emit a proposed_plan block."
metadata:
  version: "2.0.0"
  activation_cost: adaptive
  default_depth: balanced
  requires_explicit_invocation: false
---

# Spec Pipeline

## Mission

`$spec-pipeline` is the single canonical skill for current-spec work.

It owns five modes:

```text
full
gate-only
challenge-only
lint-only
repair
```

The default is `full`.

The canonical full pipeline is:

```text
profile + mode
-> evidence brief
-> grill or no-grill justification
-> decision packet
-> pre-spec gate
-> implementation spec
-> one invariant challenge
-> fresh-eyes pass
-> pre-governance lint
-> spec governance receipt
-> final governance gate
-> execution handoff
```

The system needs separate phases, receipts, scripts, and optionally independent subagents. It does not need separate public skills for gate, challenge, and lint.

## Public boundary

Use `$spec-pipeline` for:

- creating a decision-complete implementation spec;
- deciding whether a brief or decision packet is ready;
- running one strongest invariant challenge;
- linting an existing implementation spec;
- repairing only sections implicated by a failed gate, challenge, fresh-eyes pass, lint, or governance gate;
- handing a ready spec to `$plan` or implementation.

Use `$spec-retro` for historical learning across multiple prior specs, sessions, reports, or governance receipts.

Use `$grill-me` when unresolved user judgment is the primary task.

Use `$plan` only after this skill authorizes planning.

Do not use this skill for implementation itself.

## Mode selection

Choose exactly one mode before deep work.

```yaml
spec_pipeline_mode:
  mode: full | gate-only | challenge-only | lint-only | repair
  reason: "..."
```

### full

Use when creating or materially reconstructing an implementation spec.

### gate-only

Use when the user asks whether an existing brief, decision packet, or handoff is ready for specification or planning.

Output only:

- evidence needed to judge readiness;
- Gate Result;
- `spec_gate_receipt`;
- at most 1-3 material questions;
- a partial `spec_governance_receipt`.

Do not generate a spec.

### challenge-only

Use when the user asks for one strongest critique or invariant pressure test of an existing spec or plan.

Output only:

- the primary invariant;
- one strongest challenge;
- affected sections;
- classification;
- required change;
- `spec_challenge_receipt`;
- a partial `spec_governance_receipt`.

Do not run a broad review.

Do not authorize mutation.

### lint-only

Use when the user asks whether an existing spec is implementation-ready.

Output only:

- structural lint;
- semantic lint;
- `spec_lint_receipt`;
- a partial `spec_governance_receipt`.

Do not rediscover the objective unless lint exposes a material missing decision.

Do not authorize mutation.

### repair

Use when a prior gate, challenge, fresh-eyes, lint, or governance result identifies bounded defects.

Change only affected sections. Then rerun the affected phase and all downstream phases required for a valid handoff.

## Profiles

Choose one profile:

| profile | Use when | Default subagent pattern |
|---|---|---|
| `fast` | Narrow local change, obvious proof, low ambiguity. | root only |
| `balanced` | Normal implementation spec. | evidence synthesizer, invariant challenger, governance auditor as needed |
| `strict` | Public API, migration, security, performance, compatibility, architecture, or multi-wave work. | evidence synthesizer, decision auditor, invariant challenger, governance auditor |
| `campaign` | Multi-session, repeated replanning, large artifact volume, or high fanout. | strict set plus checkpoint/retro-miner only when historically warranted |

Choose one lane:

```text
spec_only
spec_to_plan
repair
review_resolution
campaign_checkpoint
```

## Hard output boundary

Never emit `<proposed_plan>`.

`$plan` owns plan artifacts, task/wave ordering, and implementation sequencing after specification readiness.

A terminal output must be one of:

1. drift warning;
2. gate failure/questions-only;
3. mode-specific audit result;
4. complete implementation-spec handoff.

## One canonical receipt

Every terminal output must include:

```text
## Spec Pipeline Receipt
```

followed by one YAML object:

```yaml
spec_governance_receipt:
  receipt_version: SGR-v2
  spec_id: "..."
  mode: full | gate-only | challenge-only | lint-only | repair
  profile: fast | balanced | strict | campaign
  lane: spec_only | spec_to_plan | repair | review_resolution | campaign_checkpoint
  status: complete | blocked | drift | audit-only | partial
  authoritative_brief:
    present: yes | no
    drift_detected: yes | no
  phase_presence:
    evidence_brief: yes | no | not-required
    decision_packet: yes | no | not-required
    gate: yes | no | not-required
    implementation_spec: yes | no | not-required
    challenge: yes | no | not-required
    fresh_eyes: yes | no | not-required
    lint: yes | no | not-required
    execution_handoff: yes | no | not-required
  gate:
    receipt_version: SGATE-v1
    plan_allowed: yes | no | not-assessed
    mutation_allowed_pre_spec: no
    script_gate: passed | failed | skipped | not-run
    gate_changed_decision: yes | no | unknown
    gate_blocked_plan: yes | no | not-assessed
    gate_defaulted_decisions: []
    material_open_questions_remaining: yes | no | unknown
    pass_no_delta: yes | no | not-assessed
    reason: "..."
  challenge:
    receipt_version: SCHAL-v1
    classification: pass | changed_architecture | changed_proof | changed_scope | changed_risk | preference_only | skipped | not-run
    changed_spec: yes | no | not-assessed
    changed_route: yes | no | not-assessed
    pass_no_delta: yes | no | not-assessed
    strongest_challenge: "..."
  fresh_eyes:
    receipt_version: SFE-v1
    changed_spec: yes | no | not-assessed
    returned_to_grill: yes | no | not-assessed
    drift_detected: yes | no | not-assessed
    pass_no_delta: yes | no | not-assessed
  lint:
    receipt_version: SLINT-v1
    verdict: pass | fail | skipped | not-run
    script_lint: passed | failed | skipped | not-run
    semantic_lint: passed | failed | not-run
    changed_spec: yes | no | not-assessed
    blocked_handoff: yes | no | not-assessed
    pass_no_delta: yes | no | not-assessed
    proof_gaps_found: []
    rollback_gaps_found: []
    unmapped_requirements_found: []
    receipt_gaps_found: []
  subagents:
    spawned: 0
    consumed: 0
    rejected: 0
    timed_out: 0
    open_at_end: 0
    positive_packets: 0
    neutral_packets: 0
    negative_packets: 0
  execution_control:
    plan_allowed: yes | no
    mutation_allowed: yes | no
    execution_handoff: yes | no
    plan_started_after_gate: yes | no | unknown
    mutation_started_after_lint: yes | no | unknown
  retro:
    trigger_required: yes | no
    reason: "..."
    next_owner: spec-retro | none
```

This single object replaces duplicated top-level pipeline, gate, challenge, lint, fresh-eyes, and governance receipt blocks.

Mode-specific human-readable sections are still required, but the machine-readable truth is `spec_governance_receipt`.

## Research first

Inspect available artifacts before asking questions:

- code;
- docs;
- existing specs/plans;
- tests;
- tickets;
- logs;
- diagrams;
- schemas;
- config;
- session history;
- supplied reports.

Do not ask the user for discoverable facts.

Ask only for:

- judgment;
- unavailable context;
- explicit authority;
- irreversible approval;
- private constraints;
- conflicts artifacts cannot resolve.

## Evidence Brief

In `full` mode, emit exactly:

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

Use `none` only after considering the field.

## Grilling

Ask 1-3 bounded questions per round only when material decisions remain.

Each question must:

- be atomic;
- have a stable `snake_case` id;
- put the recommended option first when justified;
- avoid asking for discoverable facts.

If no question is needed, emit a concrete no-grill justification:

```yaml
no_grill_justification:
  reasons: []
  material_unknowns_remaining: false
  defaulted_decisions: {}
```

## Anti-drift checkpoint

Before asking more questions, compiling a spec, or handing off, compare the candidate against the authoritative brief:

- target;
- scope;
- non-goals;
- authority boundary;
- compatibility posture;
- proof bar;
- rollout/rollback posture;
- public behavior boundary.

If any changed without explicit approval, stop with:

```text
SPEC_PIPELINE_DRIFT_WARNING
```

and set receipt status to `drift`.

## Decision packet

Before the pre-spec gate, emit:

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
  clarification_receipt:
    grill_rounds:
    no_grill_justification:
```

Rules:

- open questions need owner, default, consequence, and non-blocking reason;
- defaults must be distinguishable from locked user decisions;
- implementation choices must not be smuggled in without authority or evidence.

## Gate phase

Before compiling a spec, complete:

```text
We are building X, for Y, by changing Z, while explicitly not doing A/B/C, and success means P/Q/R proofs pass.
```

Emit:

```text
## Gate Result
plan_allowed:
mutation_allowed: false
material_open_questions:
defaults:
deferrals:
handoff_sentence:
script_gate:
script_gate_reason:
```

When feasible, run:

```bash
python codex/skills/spec-pipeline/tools/spec_gate.py --strict-receipts <handoff-file>
```

A script pass is structural evidence, not semantic proof.

If gate fails:

- do not produce a spec;
- do not produce a plan;
- ask at most 1-3 next material questions;
- set receipt status to `blocked`.

## Implementation spec contract

A complete implementation spec uses these sections in order:

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

Keep the implementation sequence at spec level. Do not create task rows, iterations, or execution waves.

## Challenge phase

Run exactly one strongest project-specific challenge tied to the primary invariant.

Emit:

```text
## Invariant Challenge
primary_invariant:
strongest_challenge:
affected_sections:
classification: pass|changed_architecture|changed_proof|changed_scope|changed_risk|preference_only
required_change:
regenerate_spec: yes|no
```

If the challenge changes architecture, proof, scope, or risk, revise only affected sections.

Independent subagent use is valuable here because challenge independence matters.

## Fresh-Eyes phase

Reread the final candidate against:

- authoritative brief;
- Evidence Brief;
- Gate Result;
- decision packet.

Emit:

```text
## Fresh-Eyes Pass
fresh_eyes_delta: none|changed_spec|return_to_grill
changed_sections:
why_preserves_authoritative_brief:
```

Look for:

- drift;
- missing non-goals;
- smuggled implementation choices;
- vague proof;
- scaffold-only proof;
- rollback gaps;
- unmapped requirements;
- plan-shaped detail;
- stale assumptions.

If a material decision is missing, return to gate failure rather than handing off.

## Lint phase

Run structural and semantic lint after challenge/fresh-eyes revisions.

When feasible:

```bash
python codex/skills/spec-pipeline/tools/spec_lint.py \
  --phase pre-governance \
  --strict-receipts \
  <spec-file>
```

Emit:

```text
## Spec Lint Result
SPEC_READY:
script_lint:
script_lint_reason:
blocking_errors:
material_risks:
missing_sections:
unmapped_requirements:
rollback_gaps:
proof_gaps:
receipt_gaps:
recommended_next_action:
```

The pre-governance lint must not require the governance receipt that has not yet been emitted.

## Governance gate

After emitting `spec_governance_receipt`, run when feasible:

```bash
python codex/skills/spec-pipeline/tools/sgr_gate.py <spec-file>
```

For a final handoff, optionally run final lint:

```bash
python codex/skills/spec-pipeline/tools/spec_lint.py \
  --phase handoff \
  --strict-receipts \
  <spec-file>
```

A complete handoff is invalid if the final governance gate fails.

## Execution handoff

Only `full` or a fully repaired `repair` mode may authorize mutation.

Emit:

```text
## Execution Handoff
ready_for_plan: yes|no
mutation_allowed: yes|no
next_owner: $plan|implementation|grill-me|spec-pipeline|spec-retro
handoff_summary:
do_not_execute_before:
```

`gate-only`, `challenge-only`, and `lint-only` do not authorize mutation.

## Subagent profiles

Use subagents only when they improve evidence quality or independent judgment.

Preferred agents:

```text
spec_evidence_synthesizer
spec_decision_auditor
spec_invariant_challenger
spec_governance_auditor
spec_retro_miner
```

Profiles:

```text
fast:
  root only

balanced:
  evidence synthesizer when repo evidence is broad
  invariant challenger for non-trivial specs
  governance auditor for final handoff

strict:
  evidence synthesizer
  decision auditor
  invariant challenger
  governance auditor

campaign:
  strict set
  retro miner only for checkpoint/historical learning
```

Every packet must be scoped to the current `artifact_state_id`.

A positive packet must:

- change a decision;
- add a material finding;
- change proof;
- retire a risk;
- or block a bad handoff.

Otherwise it is neutral.

No passing handoff with open subagents.

## Retro trigger

Do not run historical retro inside every spec.

Set `retro.trigger_required: yes` when:

- 5 or more full pipeline sessions occurred since the last retro;
- the same gate/challenge/lint failure recurred at least twice;
- execution outran readiness;
- plan churn recurred;
- no-grill justifications are repeatedly generic;
- subagent fanout repeatedly produced no impact;
- reports cannot recover phase impact.

Then set next owner to `$spec-retro`.

## Hard rules

- One canonical current-spec skill.
- No `<proposed_plan>`.
- No planning before gate pass.
- No mutation before full challenge, fresh-eyes, lint, and governance pass.
- No broad multi-challenge review by default.
- No script pass substituted for semantic judgment.
- No separate gate/challenge/lint skill invocation required.
- No retro ceremony in every spec.
- No complete handoff without `SGR-v2`.
- No execution handoff from gate-only, challenge-only, or lint-only mode.

## Resources

- [modes.md](references/modes.md)
- [gate-contract.md](references/gate-contract.md)
- [challenge-contract.md](references/challenge-contract.md)
- [fresh-eyes-contract.md](references/fresh-eyes-contract.md)
- [lint-contract.md](references/lint-contract.md)
- [governance-receipt.md](references/governance-receipt.md)
- [subagent-profiles.md](references/subagent-profiles.md)
- [output-templates.md](references/output-templates.md)
- [report-metrics.md](references/report-metrics.md)
