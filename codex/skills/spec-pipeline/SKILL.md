---
name: spec-pipeline
description: "Turn ambiguous project, architecture, implementation, or product requests into decision-complete implementation specs with phase-impact receipts. Use for `$spec-pipeline`, write a spec, turn this plan into a spec, grill me then spec, spec automation, strict `$grill-me` to `$plan` handoff, spec receipts, spec readiness automation, spec governance receipt / SGR-v1, gate/challenge/fresh-eyes/lint impact, or report-driven spec-retro automation. Never emit a proposed_plan block."
metadata:
  version: "1.3.0"
  activation_cost: high
  default_depth: full
  requires_explicit_invocation: false
---

# Spec Pipeline

## Mission

Produce implementation-ready specifications without letting planning become objective discovery or execution outrun decisions.

`spec-pipeline` is a state machine, not a prose style. Its job is to keep these phases visibly separated:

```text
Profile + Spec Pipeline Receipt
-> Evidence Brief
-> Grill or No-Grill Justification
-> Decision Packet
-> Gate Result
-> Implementation Spec
-> Invariant Challenge
-> Fresh-Eyes Pass
-> Spec Lint
-> Spec Governance Receipt
-> Execution Handoff
```

The skill succeeds only when a later user, agent, validator, or report can tell:

- which phases completed;
- which facts were researched;
- which decisions were locked;
- why grilling was or was not needed;
- what the gate/challenge/fresh-eyes/lint phases changed;
- whether downstream planning may start;
- whether downstream mutation may start;
- whether companion checks were phase-impacting or merely pass-no-delta.

## New doctrine: phase impact, not companion-count theatre

Do not optimize for standalone activations of `$spec-gate`, `$spec-challenge`, `$spec-lint`, or `$spec-retro`.

The root workflow may perform gate/challenge/lint/fresh-eyes internally, but it must leave compact receipts that future reports can audit.

A companion phase is materially useful when it does one of:

```text
blocked a bad handoff
changed the spec
changed the proof bar
changed scope/risk/architecture
created useful defaults
confirmed readiness with script-backed evidence
returned to grill
triggered retro automation
```

If it does none of those, record it as `pass_no_delta`.

## Hard output boundary

Never wrap a `spec-pipeline` output in `<proposed_plan>`. That block is reserved for `$plan`.

A complete `spec-pipeline` output must be one of exactly three shapes:

1. **Drift warning**: `SPEC_PIPELINE_DRIFT_WARNING`, `## Spec Pipeline Receipt`, and no spec, plan, or execution sequence.
2. **Gate failure / questions-only**: `SPEC_PIPELINE_GATE_FAILURE`, `## Spec Pipeline Receipt`, no spec, no plan, only missing fields, drift/churn warnings if any, and 1-3 next questions.
3. **Implementation spec handoff**: plain markdown with `## Spec Pipeline Receipt`, Evidence Brief, Gate Result, `spec_decision_packet`, required implementation spec sections, one Invariant Challenge, Fresh-Eyes Pass, Spec Lint Result, `spec_governance_receipt`, and a brief Execution Handoff.

Do not emit `$plan` iteration scaffolding such as `Round Delta`, `Iteration Change Log`, `Decision Impact Map`, `Adversarial Findings`, `Contract Signals`, dependency rows, execution waves, or `<proposed_plan>` tags. `$plan` owns dependency-ordered execution planning after this skill passes gate, challenge, fresh-eyes, lint, and governance receipt.

If the user explicitly asks for `$plan` and `$spec-pipeline` at the same time, run `spec-pipeline` first. End with an execution handoff that says whether `$plan` may now consume the spec. Do not combine the artifacts.

## Boundary with neighboring skills

- `$grill-me` owns unresolved decisions, contradictions, priorities, non-goals, and authority questions.
- `spec-pipeline` owns decision extraction, receipting, readiness gating, exact spec compilation, one invariant challenge, fresh-eyes review, spec lint, governance receipt, and execution handoff.
- `$plan` owns execution shape, dependency ordering, file-by-file implementation sequencing, rollback sequencing, and proof commands after the spec is ready.
- `spec-gate` owns readiness judgment before planning and contributes `spec_gate_receipt`.
- `spec-challenge` owns exactly one strongest invariant/adversarial challenge and contributes `spec_challenge_receipt`.
- `spec-lint` owns implementation-readiness lint after the spec exists and contributes `spec_lint_receipt`.
- `spec-retro` owns historical learning, churn detection, and future automation updates when triggered by reports or repeated pipeline gaps.

Do not let planning discover the objective. Do not let grilling rediscover facts already supplied or available from artifacts. Do not let a spec become an implementation plan. Do not let tool-heavy execution begin until the governance receipt says mutation is allowed.

## Profile and lane selection

Choose one profile before researching deeply:

| profile | Use when | Default specialist budget |
|---|---|---:|
| `fast` | Narrow local change, obvious proof, low ambiguity. | 0 pre-gate, 2 total |
| `balanced` | Normal implementation spec. | 3 pre-gate, 5 total |
| `strict` | Public API, migration, security, performance, compatibility, architecture, or multi-wave work. | 5 pre-gate, 8 total |
| `campaign` | Long-running, multi-session, high-signal, high-fanout, or repeated replanning work. | explicit budget required |

Choose one lane:

```text
spec_only | spec_to_plan | repair | review_resolution | campaign_checkpoint
```

Trigger `campaign` mode or a `campaign_checkpoint` when any of these are visible:

- session or artifact volume is clearly large;
- subagents exceed 8 total or exceed profile budget;
- `$plan` or `update_plan` is regenerated more than twice;
- objective/title/scope changes after planning;
- repeated `blocked` states appear without a taxonomy;
- implementation discovers a missing material decision;
- scope expands after execution starts.

Campaign mode requires a checkpoint receipt before continuing.

## Spec Pipeline Receipt

Every terminal output must include this block. For gate failures and drift warnings, place it immediately after the warning block. For a complete spec, place it before the Evidence Brief.

```text
## Spec Pipeline Receipt
profile: fast|balanced|strict|campaign
lane: spec_only|spec_to_plan|repair|review_resolution|campaign_checkpoint
evidence_brief_emitted: true|false
grill_rounds: <integer>
no_grill_justification: <text|null>
decision_packet_emitted: true|false
gate_verdict: pass|fail|skipped
plan_allowed: true|false
mutation_allowed: true|false
subagent_budget: <used>/<limit> pre_gate=<used>/<limit|explicit> status=within_budget|over_budget|not_applicable
subagent_receipt: spawned=<n> consumed=<n> rejected=<n> timed_out=<n> open_at_end=<n>
invariant_challenge: pass|changed_architecture|changed_proof|changed_scope|changed_risk|skipped
fresh_eyes: pass|changed_spec|return_to_grill|skipped
lint_verdict: pass|fail|skipped
spec_governance_receipt: present|missing
execution_handoff: yes|no
```

Rules:

- If `grill_rounds: 0`, `no_grill_justification` must be concrete and must say why material decisions were already researched, supplied, defaulted, deferred, or immaterial.
- If any subagent is spawned, `subagent_receipt` must account for it as consumed, rejected, timed out, superseded, or still open. `open_at_end` must be `0` before a passing handoff.
- `mutation_allowed: true` is allowed only after Gate Result, Invariant Challenge, Fresh-Eyes Pass, Spec Lint Result, and Spec Governance Receipt pass or after a consciously accepted fast-path exception with proof and rollback present.
- A skipped gate, challenge, fresh-eyes pass, or lint must have a concrete reason in its own section.

## Decision-complete fast path

If the user supplies all of the following, treat the brief as presumptively sufficient and do not ask `$grill-me` questions unless a material contradiction remains:

- goal;
- target system or repository surface;
- scope;
- non-goals;
- locked authority boundary or primary invariant;
- acceptance criteria or success criteria;
- proof commands, proof surfaces, or validation bar.

In this fast path, research discoverable facts, emit the exact Evidence Brief, emit `grill_rounds: 0` with a concrete No-Grill Justification, produce the decision packet, run the gate, compile the spec, run one challenge, run Fresh-Eyes, lint it, emit `spec_governance_receipt`, and hand off. Questions are allowed only for contradictions, missing authority, missing secrets, irreversible approval, or a proof bar that cannot be inferred.

## Anti-drift checkpoint

Before asking further questions, emitting a spec, or handing off to `$plan`, compare the current candidate objective against the original authoritative user brief.

Check:

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

Do not continue to questions, spec, lint, or plan handoff until drift is resolved.

## Research first

Inspect available artifacts before asking questions: code, docs, plans, tests, tickets, logs, diagrams, schemas, config, session history, and supplied reports.

Do not ask the user for discoverable facts. Ask only for judgment calls, unavailable context, explicit authority, irreversible approvals, private constraints, or conflicts that artifacts cannot resolve.

When useful and available, ask the parent to spawn read-only subagents within the selected budget:

```text
Spawn spec_evidence_cartographer, spec_constraint_miner, and spec_proof_surface_mapper to gather current-state evidence, hard constraints, and proof surfaces, then synthesize their packets before asking questions.
```

When specialists are used, assign the current `artifact_state_id`, exact scope, and the shared specialist packet contract. Consume only packet-native, scoped, evidence-bearing, current packets. Reject stale, wrong-scope, wrapper-leaking, acknowledgement-only, or no-evidence packets before they affect the Evidence Brief, decision packet, gate, spec, challenge, fresh-eyes pass, lint, governance receipt, or execution handoff.

Record one value receipt per specialist packet. A valid but unsurprising packet is neutral. A malformed, stale, wrong-scope, timeout, acknowledgement-only, or wrapper-leaking packet is negative. A positive packet must change route, add a finding, change proof, or retire a risk.

## Exact Evidence Brief contract

The Evidence Brief must contain exactly these labels, in this order:

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

Keep each field concise but concrete. Use `none` only when actually considered. Use `not yet verified` for facts that matter but were not inspected.

## Grill only material decisions

Ask 1-3 bounded questions per round using `$grill-me` style only when the Evidence Brief and anti-drift checkpoint show that material decisions remain.

Each question must be atomic and have a stable `snake_case` id. Put the recommended option first when justified by evidence.

Do not ask questions merely to make the interaction feel rigorous. If the user's brief is decision-complete, say `Judgment calls still needed: none`, emit the No-Grill Justification, and continue.

## No-Grill Justification

If no questions are asked, emit the reason in the receipt and ensure it is visible near the decision packet:

```yaml
no_grill_justification:
  reason:
    - "repo evidence resolved current behavior"
    - "user supplied scope, non-goals, invariant, and proof bar"
  material_unknowns_remaining: false
  defaulted_decisions:
    compatibility_posture: "non-breaking unless contradicted by evidence"
    rollout_rollback_posture: "local patch with revert/abort criteria"
```

A no-grill path is invalid if any material judgment call remains unresearched, unanswered, undefaulted, or undeferred.

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
  clarification_receipt:
    grill_rounds:
    no_grill_justification:
```

Rules:

- `open_questions` are allowed only if each has owner, default action, consequence, and reason it does not block the spec.
- `default_assumptions` must distinguish inferred defaults from user-locked decisions.
- If the user corrected drift, include the correction as a locked decision or invalidated prior assumption.
- Do not smuggle implementation choices into the packet unless the user locked them or artifacts prove they are required.
- If `clarification_receipt.grill_rounds` is `0`, `clarification_receipt.no_grill_justification` must be concrete.

## Gate before spec, planning, or mutation

Before compiling the spec, run the handoff sentence:

```text
We are building X, for Y, by changing Z, while explicitly not doing A/B/C, and success means P/Q/R proofs pass.
```

Then emit a visible Gate Result:

```text
## Gate Result
plan_allowed: true|false
mutation_allowed: false
script_gate: passed|failed|skipped
script_gate_reason:
clarification_receipt: grill_rounds=<n> no_grill_justification=<present|absent>
material_open_questions:
defaults:
deferrals:
handoff_sentence:
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
  pass_no_delta: yes | no
  reason: "..."
```

Planning is allowed only when `plan_allowed: true` and no material open question lacks an owner/default/consequence.

Mutation is not allowed at the pre-spec gate.

When feasible, write the handoff packet to a temporary file and run the structural helper:

```bash
uv run python codex/skills/spec-gate/scripts/spec_gate.py --strict-receipts <handoff-file>
```

If the script is unavailable or environment lacks shell/filesystem access, set `script_gate: skipped` and state the concrete reason. A skipped script is allowed only when semantic gating is still performed visibly.

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

Then emit `## Spec Pipeline Receipt` with `gate_verdict: fail`, `plan_allowed: false`, `mutation_allowed: false`, and `execution_handoff: no`.

Ask at most 1-3 next questions. Do not include implementation sequence, plan waves, or `<proposed_plan>`.

## Implementation spec contract

When planning is allowed, produce an implementation spec, not a prose roadmap and not a `$plan` artifact.

Required sections, in order:

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

Choose the challenge most likely to invalidate the spec's primary invariant.

Emit:

```text
## Invariant Challenge
primary_invariant:
strongest_challenge:
affected_sections:
classification: pass|architecture_change_required|proof_change_required|scope_change_required|risk_mitigation_required|preference_only
required_change:
regenerate_spec: yes|no
```

Also emit:

```yaml
spec_challenge_receipt:
  receipt_version: SCHAL-v1
  primary_invariant: "..."
  strongest_challenge: "..."
  affected_sections: []
  classification: pass | changed_architecture | changed_proof | changed_scope | changed_risk | preference_only | skipped
  required_change: "..."
  regenerate_spec: yes | no
  changed_spec: yes | no
  changed_route: yes | no
  pass_no_delta: yes | no
```

If the challenge changes architecture, proof, scope, or risk mitigation, revise only the affected spec sections and then run Fresh-Eyes and lint the revised spec. If preference-only, record it as non-blocking.

## Fresh-Eyes Pass

Before lint and Execution Handoff, reread the final spec against the original authoritative brief, Evidence Brief, Gate Result, and `spec_decision_packet`.

Emit:

```text
## Fresh-Eyes Pass
fresh_eyes_delta: none|changed_spec|return_to_grill
changed_sections:
why_preserves_authoritative_brief:
```

Also emit:

```yaml
spec_fresh_eyes_receipt:
  receipt_version: SFE-v1
  changed_spec: yes | no
  returned_to_grill: yes | no
  changed_sections: []
  drift_detected: yes | no
  pass_no_delta: yes | no
```

Look for objective drift, missing non-goals, smuggled implementation choices, vague proof commands, scaffold-only proof where runtime proof is required, rollback/abort gaps, requirements without tests, plan-shaped execution waves, and stale defaults or assumptions.

If material drift or missing decisions are found, return to gate failure / questions-only instead of handoff.

## Spec lint

After the challenge and Fresh-Eyes Pass, lint the spec. Prefer script-backed lint even for inline final specs.

When feasible, write the spec to a temporary file and run:

```bash
uv run python codex/skills/spec-lint/scripts/spec_lint.py --strict-receipts <spec-file>
```

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
receipt_gaps:
subagent_gaps:
churn_signals:
recommended_next_action: proceed_to_plan|return_to_grill|revise_spec|run_spec_challenge|campaign_checkpoint
```

Also emit:

```yaml
spec_lint_receipt:
  receipt_version: SLINT-v1
  verdict: pass | fail | skipped
  script_lint: passed | failed | skipped
  semantic_lint: passed | failed
  changed_spec: yes | no
  blocked_handoff: yes | no
  proof_gaps_found: []
  rollback_gaps_found: []
  unmapped_requirements_found: []
  receipt_gaps_found: []
  pass_no_delta: yes | no
```

Fail the spec if:

- material open questions remain without owner/default/consequence;
- non-goals are missing;
- proof bar is vague;
- major requirements are not mapped to tests;
- rollback or abort criteria are missing;
- implementation order is not dependency-aware;
- primary invariant is missing;
- long audit sections repeat rationale without changing implementation behavior;
- spec changes the objective relative to authoritative brief;
- `grill_rounds: 0` but no No-Grill Justification is present;
- spawned specialists are unaccounted for;
- balanced/strict/campaign work skips invariant challenge or fresh-eyes pass;
- output contains `<proposed_plan>`.

## Spec Governance Receipt

Every complete implementation spec handoff must include:

```yaml
spec_governance_receipt:
  receipt_version: SGR-v1
  spec_id: "..."
  profile: fast | balanced | strict | campaign
  lane: spec_only | spec_to_plan | repair | review_resolution | campaign_checkpoint
  phase_presence:
    evidence_brief: yes | no
    decision_packet: yes | no
    gate_result: yes | no
    invariant_challenge: yes | no
    fresh_eyes: yes | no
    spec_lint: yes | no
    execution_handoff: yes | no
  gate:
    plan_allowed: yes | no
    mutation_allowed_pre_spec: no
    script_gate: passed | failed | skipped
    gate_changed_decision: yes | no
    gate_blocked_plan: yes | no
    pass_no_delta: yes | no
  challenge:
    classification: pass | changed_architecture | changed_proof | changed_scope | changed_risk | preference_only | skipped
    changed_spec: yes | no
    changed_route: yes | no
    pass_no_delta: yes | no
  fresh_eyes:
    changed_spec: yes | no
    returned_to_grill: yes | no
    pass_no_delta: yes | no
  lint:
    verdict: pass | fail | skipped
    script_lint: passed | failed | skipped
    changed_spec: yes | no
    blocked_handoff: yes | no
    pass_no_delta: yes | no
  execution_control:
    handoff_allowed: yes | no
    plan_started_after_gate: yes | no | unknown
    mutation_started_after_lint: yes | no | unknown
  retro:
    retro_triggered: yes | no
    reason: "..."
```

If `spec_governance_receipt` is missing, the spec is not implementation-ready even if the prose looks complete.

## Spec-retro trigger

`$spec-retro` is not per-spec ceremony. Trigger it when learning evidence exists.

Trigger a `spec_retro_update` recommendation when any are true:

- 5 or more `$spec-pipeline` sessions since last retro;
- 2 or more repeated gate/lint/challenge gaps;
- a report shows companion phases are invisible;
- execution started before gate/lint/challenge readiness;
- plan churn/campaign triggers recur;
- subagent fanout repeatedly produces no route impact;
- no-grill justifications are repeatedly generic.

Emit:

```yaml
spec_retro_trigger:
  required: yes | no
  reason: "..."
  suggested_owner: spec-retro | tune | none
```

Do not run a long retro inside every spec. If triggered, hand off a small retro brief.

## Blocked taxonomy

When the run cannot proceed, emit:

```yaml
blocked_receipt:
  blocked: true
  kind: decision_missing | evidence_missing | proof_failed | environment | dirty_worktree | external_dependency | plan_mode_boundary | review_unresolved | subagent_timeout | scope_conflict
  unblock_action: ask_user | inspect_repo | run_tests | revise_spec | return_to_grill | abort | campaign_checkpoint
  owner:
  consequence:
```

A blocked session without `blocked_receipt` is telemetry loss.

## Execution handoff

Only after Gate Result, Invariant Challenge, Fresh-Eyes Pass, Spec Lint Result, and Spec Governance Receipt pass may the output include an execution handoff.

Keep it short:

```text
## Execution Handoff
ready_for_plan: yes|no
mutation_allowed: yes|no
next_owner: $plan|implementation|grill-me|spec-pipeline|spec-retro
handoff_summary:
do_not_execute_before:
```

`spec-pipeline` may say `$plan` should consume the spec next. It must not convert the spec into a `$plan` artifact.

## Quality metrics for reports

Future reports should measure:

```yaml
spec_pipeline_quality:
  receipts:
    spec_pipeline_receipt_present:
    spec_governance_receipt_present:
    evidence_brief_present:
    decision_packet_present:
    gate_result_present:
    invariant_challenge_present:
    fresh_eyes_present:
    spec_lint_result_present:
    execution_handoff_present:
  phase_impact:
    gate_changed_decision:
    gate_blocked_plan:
    challenge_changed_spec:
    fresh_eyes_changed_spec:
    lint_changed_spec:
    lint_blocked_handoff:
    retro_triggered:
  execution_control:
    plan_started_before_gate:
    mutation_started_before_lint:
    apply_patch_before_mutation_allowed:
```

## Hard rules

- Do not emit `<proposed_plan>`.
- Do not treat companion phase mentions as success; emit phase receipts.
- Do not call a spec ready without `spec_governance_receipt`.
- Do not start execution before handoff.
- Do not let `$plan` discover the objective.
- Do not run multiple independent challenges unless the user asks for full review.
- Do not use `$spec-retro` in every run; trigger it from repeated/report-backed learning signals.
- Do not let scripts replace semantic judgment; structural script pass is necessary but not sufficient.

## Resources

- [spec-governance-receipt.md](references/spec-governance-receipt.md)
- [phase-impact-receipts.md](references/phase-impact-receipts.md)
- [spec-retro-trigger.md](references/spec-retro-trigger.md)
- [spec-report-metrics.md](references/spec-report-metrics.md)
- [companion-boundary.md](references/companion-boundary.md)
