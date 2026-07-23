---
name: spec-pipeline
description: "Canonical current-spec engine. Turn ambiguous project, architecture, implementation, or product requests into decision-complete implementation specs; operate narrowly in gate-only, challenge-only, or repair mode; default full-mode plan-ready specs to lane=spec_to_plan; and tail-call `$plan` when SGR-v2 and execution handoff authorize planning. Never emit a proposed_plan block."
metadata:
  version: "2.2.0"
  activation_cost: adaptive
  default_depth: balanced
  requires_explicit_invocation: false
---

# Spec Pipeline

## Mission

`$spec-pipeline` is the canonical current-spec workflow.

It converts an accepted or clarified objective into a decision-complete
implementation spec and hands planning authority to `$plan` when the spec
governance receipt authorizes that transition.

```text
profile + mode
-> evidence brief
-> grill or no-grill justification
-> decision packet
-> pre-spec gate
-> implementation spec
-> strongest invariant challenge
-> fresh-eyes pass
-> SGR-v2 governance receipt
-> execution handoff
-> mandatory same-turn $plan tail-call when eligible
```

`$spec-pipeline` owns accepted semantics. `$plan` owns execution-policy
synthesis, task/wave ordering, policy fixed-point refinement, and `$actuating`
handoff. `$actuating` owns source-bound local execution governance; it does not
claim fencing or durable coordination. This skill never mutates repository
product files and never emits `<proposed_plan>`.

## Public boundary

Use `$spec-pipeline` for:

- creating or materially reconstructing an implementation spec;
- deciding whether a brief, decision packet, spec, or handoff is ready;
- running one strongest invariant challenge;
- repairing only sections implicated by a blocked readiness decision,
  challenge, fresh-eyes pass, or governance result;
- handing a ready spec to `$plan` or implementation.

Use `$grill-me` when unresolved user judgment is the primary task. Use
`$spec-retro` for historical learning across multiple prior specs, sessions,
reports, or governance receipts.

Do not use this skill for implementation itself.

## Mode selection

Choose exactly one mode before deep work:

```yaml
spec_pipeline_mode:
  mode: full | gate-only | challenge-only | repair
  reason: "..."
```

Modes:

- `full` — create or materially reconstruct a complete implementation spec.
- `gate-only` — decide whether an existing brief, decision packet, or handoff
  is ready. Do not generate a spec, plan, or mutation authority.
- `challenge-only` — return one strongest critique or invariant pressure test.
  Do not authorize mutation.
- `repair` — change only sections implicated by a prior blocked readiness
  decision, challenge, fresh-eyes pass, or governance result; then rerun
  affected and downstream phases.

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

### Lane-selection law

For `full` mode, the default lane is:

```text
spec_to_plan
```

unless the user explicitly requests spec-only/no-plan output or a material gate
blocks downstream planning.

Explicit `$spec-pipeline` invocation is **not** a request for `spec_only`. A
user saying `$spec-pipeline`, `make a spec`, `write the spec`, `produce the
governed spec`, or equivalent asks the spec workflow to run. If the workflow
finishes complete and plan-ready, planning authority transfers to `$plan`
through SGR-v2 and the Execution Handoff.

Use `spec_only` only when a concrete blocker exists: explicit spec-only user
request, gate-only/challenge-only mode, blocked/drift/partial status,
unresolved material user judgment, `plan_allowed=no`, fresh-eyes drift,
`ready_for_plan=no`, `next_owner != $plan`, non-empty
`do_not_execute_before`, or same-turn `$plan` being unavailable. When `$plan`
cannot load, emit `AUTO_PLAN_HANDOFF_REQUIRED`; do not silently convert to
`spec_only`.

See [01-lane-selection.md](references/cli-specs/01-lane-selection.md).

## Research first

Inspect available artifacts before asking questions: code, docs, specs, plans,
tests, tickets, logs, diagrams, schemas, config, session history, and supplied
reports.

Do not ask the user for discoverable facts. Ask only for judgment, unavailable
context, explicit authority, irreversible approval, private constraints, or
conflicts that artifacts cannot resolve.

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

Ask 1-3 bounded questions per round only when material decisions remain. Each
question must be atomic, have a stable `snake_case` id, put the recommended
option first when justified, and avoid asking for discoverable facts.

If no question is needed, emit:

```yaml
no_grill_justification:
  reasons: []
  material_unknowns_remaining: false
  defaulted_decisions: {}
```

## Anti-drift checkpoint

Before asking more questions, compiling a spec, or handing off, compare the
candidate against the authoritative brief:

```text
target
scope
non-goals
authority boundary
compatibility posture
proof bar
rollout/rollback posture
public behavior boundary
```

If any changed without explicit approval, stop with:

```text
SPEC_PIPELINE_DRIFT_WARNING
```

and set SGR-v2 status to `drift`.

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

Open questions need owner, default, consequence, and non-blocking reason.
Defaults must be distinguishable from locked user decisions. Implementation
choices must not be smuggled in without authority or evidence.

## Gate phase

Before compiling a spec, complete this sentence:

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
```

If the gate fails, do not produce a spec or plan. Ask at most 1-3 next material
questions and set SGR-v2 status to `blocked`.

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

Keep the implementation sequence at spec level. Do not create task rows,
iterations, execution waves, or `<proposed_plan>`.

## Challenge phase

Run exactly one strongest project-specific challenge tied to the primary
invariant.

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

If the challenge changes architecture, proof, scope, or risk, revise only
affected sections and rerun affected downstream phases.

## Fresh-Eyes phase

Reread the final candidate against the authoritative brief, Evidence Brief, Gate
Result, and decision packet.

Emit:

```text
## Fresh-Eyes Pass
fresh_eyes_delta: none|changed_spec|return_to_grill
changed_sections:
why_preserves_authoritative_brief:
```

Look for drift, missing non-goals, smuggled implementation choices, vague proof,
scaffold-only proof, rollback gaps, unmapped requirements, plan-shaped detail,
and stale assumptions. If a material decision is missing, return to gate failure
rather than handing off.

## Spec Pipeline Receipt

Every terminal output must include exactly one `## Spec Pipeline Receipt`
section followed by one YAML object:

```yaml
spec_governance_receipt:
  receipt_version: SGR-v2
  spec_id: "..."
  mode: full | gate-only | challenge-only | repair
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
    execution_handoff: yes | no | not-required
  gate:
    receipt_version: SGATE-v1
    plan_allowed: yes | no | not-assessed
    mutation_allowed_pre_spec: no
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
    mutation_started_after_handoff: yes | no | unknown
  execution_handoff:
    ready_for_plan: yes | no
    next_owner: $plan | implementation | grill-me | spec-pipeline | spec-retro | none
    handoff_summary: "..."
    do_not_execute_before: []
    plan_source_ref: "inline implementation spec | path"
    governance_receipt_ref: "inline SGR-v2 | path"
  auto_plan_handoff:
    eligible: yes | no
    reason: "..."
    invocation: same_turn_tail_call | manual | none
  retro:
    trigger_required: yes | no
    reason: "..."
    next_owner: spec-retro | none
```

This single object is the machine-readable truth. Mode-specific human-readable
sections remain required, but duplicated top-level receipt blocks are not.

## Execution handoff

Only `full` or a fully repaired `repair` mode may authorize downstream planning
or mutation.

Emit:

```text
## Execution Handoff
ready_for_plan: yes|no
mutation_allowed: yes|no
next_owner: $plan|implementation|grill-me|spec-pipeline|spec-retro|none
handoff_summary:
do_not_execute_before:
auto_plan_handoff: eligible|not-eligible
```

`gate-only` and `challenge-only` do not authorize mutation or
same-turn planning.

## Automatic `$plan` tail-call

When final SGR-v2 and Execution Handoff satisfy all predicates, `$spec-pipeline`
must immediately continue into `$plan` in the same assistant turn. Do not ask the
user to invoke `$plan` separately.

```text
mode in {full, repair}
status = complete
lane = spec_to_plan
authoritative_brief.drift_detected = no
phase_presence.gate = yes
phase_presence.implementation_spec = yes
phase_presence.challenge = yes
phase_presence.fresh_eyes = yes
phase_presence.execution_handoff = yes
gate.plan_allowed = yes
gate.material_open_questions_remaining = no
fresh_eyes.drift_detected = no
subagents.open_at_end = 0
execution_control.plan_allowed = yes
execution_control.execution_handoff = yes
execution_handoff.ready_for_plan = yes
execution_handoff.next_owner = $plan
execution_handoff.do_not_execute_before = []
auto_plan_handoff.eligible = yes
auto_plan_handoff.invocation = same_turn_tail_call
```

The tail-call passes `plan_source_contract / PSC-v1` to `$plan`:

```yaml
plan_source_contract:
  contract_version: PSC-v1
  source_owner: spec-pipeline
  spec_id:
  implementation_spec:
  decision_packet:
  sgr_v2:
  proof_bar:
  non_goals: []
  target_branch:
  do_not_execute_before: []
```

`$spec-pipeline` still must not emit `<proposed_plan>`. `$plan` emits the
`<proposed_plan>` block and performs its fixed-point planning loop with PSR-v1.
`$plan` does not grant mutation authority.

Do not auto-run `$plan` when any of these are true:

```text
user explicitly requested spec-only/no-plan output
mode is gate-only or challenge-only
status is blocked, drift, audit-only, or partial
lane is not spec_to_plan for a legal blocker recorded in the receipt
gate did not allow planning
material questions remain
fresh-eyes returned to grill or detected drift
any subagent remains open
next_owner is not $plan
do_not_execute_before is non-empty
auto_plan_handoff.eligible = no with a concrete blocker other than "user did not separately ask for $plan"
```

If the runtime cannot actually load `$plan`, emit:

```text
AUTO_PLAN_HANDOFF_REQUIRED
reason: same-turn tail-call unavailable in this runtime
next_owner: $plan
```

This marker is a failure of automation, not a failure of the spec. It must not
be replaced with `spec_only` merely because the tail-call could not run.

See [02-auto-plan-tail-call.md](references/cli-specs/02-auto-plan-tail-call.md).

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

A positive packet must change a decision, add a material finding, change proof,
retire a risk, or block a bad handoff. Otherwise it is neutral. No passing
handoff with open subagents.

## Retro trigger

Do not run historical retro inside every spec. Set `retro.trigger_required: yes`
when:

- five or more full pipeline sessions occurred since the last retro;
- the same readiness or challenge failure recurred at least twice;
- execution outran readiness;
- plan churn recurred;
- no-grill justifications are repeatedly generic;
- subagent fanout repeatedly produced no impact;
- reports cannot recover phase impact.

Then set next owner to `$spec-retro`.

## Hard rules

- One canonical current-spec skill.
- No `<proposed_plan>`.
- In `full` mode, default to `spec_to_plan` unless a legal blocker exists.
- Explicit `$spec-pipeline` is not a `spec_only` request.
- No planning before gate pass.
- No mutation before full challenge, fresh-eyes, governance receipt, and execution handoff.
- No execution handoff from gate-only or challenge-only mode.
- No broad multi-challenge review by default.
- No separate readiness or challenge skill invocation required.
- No retro ceremony in every spec.
- No complete handoff without SGR-v2.
- If SGR-v2 says auto-plan is eligible, same-turn `$plan` tail-call is mandatory.
