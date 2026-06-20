---
name: tune
description: "Tune an existing Codex skill by comparing its intended decision contract with observed decision episodes and outcomes. Prefer `seq skill-decision-audit --mode tune-packet`; use for `$tune`, intended-vs-observed behavior, missed/false/ceremonial activations, ignored clauses, wrong routes, outcome regressions, repeated workarounds, STE-v1 packets, skill-delta candidates, or explicit `$refine` handoff. Stop at audit/proposal unless apply is explicit. `$seq` CLI changes require a separate special spec."
---

# Tune

## Mission

Improve a skill by finding the smallest evidence-backed change that alters future decisions for the better.

```text
activation evidence asks: was the skill present?
decision evidence asks: what changed because of it?
outcome evidence asks: was that change useful?
```

`$tune` owns diagnosis and the refinement decision.

`$seq` owns historical/session/tool evidence.

`$refine` owns in-place edits after the apply gate passes.

## Canonical evidence

For historical or multi-session tuning, prefer:

```bash
seq skill-decision-audit \
  --skill <skill> \
  --skill-root codex/skills \
  --repo <repo> \
  --last 30d \
  --exclude-current \
  --mode tune-packet \
  --format json
```

Canonical packet:

```text
skill_tuning_evidence / STE-v1
```

For one watched session, prefer:

```bash
seq skill-decision-audit \
  --skill <skill> \
  --session-id <session> \
  --since-cursor '<cursor>' \
  --mode delta \
  --format json
```

If the installed CLI lacks `skill-decision-audit`:

1. use the existing narrow `$seq` surfaces needed for the question;
2. keep activation, decision, and outcome evidence separate;
3. mark decision causality as `unknown` unless explicit;
4. emit a `seq_special_spec_handoff` when the missing surface materially limits diagnosis;
5. do not replace the missing CLI with broad ad hoc transcript mining as the normal workflow.

## Modes

Choose exactly one:

```text
audit-only
proposal-only
apply-with-refine
```

### audit-only

Explain what evidence supports and what it does not support.

No edits.

### proposal-only

Default for “improve,” “optimize,” or “what should change?”

Produce a bounded decision delta, terminal repeat state, or no-action decision.

No edits.

### apply-with-refine

Use only when the user explicitly asks to edit or apply changes now.

Produce the diagnosis first, then hand a bounded brief to `$refine`.

## Target skill type

Classify the target before judging it:

```text
decision
execution
evidence
orchestration
mixed
```

### decision

Value lies in selecting, rejecting, narrowing, blocking, or escalating a route.

Primary evidence:

```text
decision effect
clause compliance
downstream outcome
```

### execution

Value lies in performing a task correctly and efficiently.

Primary evidence:

```text
handoff fidelity
surface budget
validation
rework
```

### evidence

Value lies in retrieving, classifying, or preserving trustworthy evidence.

Primary evidence:

```text
coverage
precision
provenance
false-positive/negative behavior
```

### orchestration

Value lies in lifecycle, state transition, concurrency, or handoff control.

Primary evidence:

```text
phase correctness
handoff completeness
blocked/terminal states
loop efficiency
```

### mixed

Name which evidence dimensions apply.

Do not force a route-change metric onto a skill whose job is evidence retrieval or execution.

## Intended-use contract

Read the target skill before judging usage:

```text
SKILL.md
agents/openai.yaml
references/decision-contract.yaml
scripts/
references/
assets/
```

Prefer an explicit:

```text
skill_decision_contract / SKDC-v1
```

If absent, reconstruct only the minimum provisional contract needed for diagnosis and label it:

```text
contract_authority: inferred
```

Do not pretend inferred clauses are stable historical identifiers.

## Evidence hierarchy

Use the strongest available evidence and preserve weaker classes separately:

```text
1. SDR-v1 structured decision receipt
2. explicit assistant statement tying skill to a decision
3. explicit skill use plus contract-aligned route/action
4. skill use plus downstream outcome with no route attribution
5. co-occurrence or raw mention
```

Only levels 1–2 establish a strong skill-caused decision delta.

Levels 3–4 support alignment or association, not causal proof.

Level 5 is weak evidence.

## Decision-effect classes

```text
explicit_route_change
prevented_action
narrowed_scope
added_or_changed_proof
escalated_or_blocked
reinforced_existing_choice
no_visible_delta
contrary_to_contract
trigger_missed
false_activation
ceremonial_activation
unknown
```

### Ceremonial activation

Use when the skill was loaded or declared but:

- no clause was exercised;
- no route, scope, proof, or lifecycle state changed;
- the resulting work is indistinguishable from a no-skill path.

Ceremony is not automatically harmful. It becomes a tuning gap when recurrent or costly.

## Gap classes

Classify the smallest useful gap:

```text
activation
interpretation
workflow
tooling
resource
validation
metadata
boundary
source-scope
decision-contract
observability
outcome
ceremony
overconstraint
```

Examples:

- trigger present, no activation -> `activation`
- clause loaded but wrong route selected -> `interpretation`
- repeated manual workaround -> `tooling` or `workflow`
- no stable clause IDs -> `decision-contract`
- skill appears useful but decision effect cannot be recovered -> `observability`
- compliant route repeatedly reopens -> `outcome`
- repeated use with no visible delta -> `ceremony`

## Decision episode analysis

For each material episode, preserve:

```yaml
decision_episode:
  decision_id:
  session_id:
  artifact_state:
  trigger:
  activation_evidence:
  question:
  alternatives_considered: []
  selected_route:
  rejected_routes: []
  clause_refs: []
  decision_effect:
  evidence_strength:
  downstream:
  counterevidence: []
```

Do not infer alternatives that were never observed.

Do not count a later successful session as proof that a skill caused the success.

## Counterfactual skepticism

Before proposing a change, ask:

```text
Would the observed action plausibly have happened without the skill?
Did the skill change the route, or merely describe it?
Did compliance improve the outcome?
Did a missed activation actually cause a failure?
Could another companion skill own the effect?
```

For high-impact or ambiguous tuning, use:

```text
skill_decision_provenance_auditor
skill_outcome_skeptic
```

## Canonical tune packet

Consume or emit `skill_tuning_evidence / STE-v1`.

It must preserve target kind, contract authority, window, denominator, trigger quality, decision influence, clause compliance, outcomes, workarounds, exemplars, recurrent gaps, and limitations.

See [ste-v1.md](references/ste-v1.md).

Validate:

```bash
python3 codex/skills/tune/tools/ste_gate.py <packet.json>
```

## Skill delta

Produce at most one dominant `skill_delta_candidate / SDC-v2` per cycle.

Required fields:

```text
target and type
source packet
gap signature/type
episode and clause refs
evidence class/recurrence/confidence
expected decision delta
smallest change
protected contracts
validation query and plan
proposed action
```

If there is no expected decision delta, do not produce a long redesign.

## Repeat proposal ledger

Track proposal signature, first/last seen, repeat count, evidence delta, state, and next action.

If the same proposal appears three times without new decision/outcome evidence, emit one terminal state:

```text
apply-blocked
final-brief
transferred-to-seq
retired
```

## Apply gate

All must hold:

- explicit user request to edit now;
- target skill identified;
- evidence source declared;
- intended contract reconstructed;
- decision or outcome gap is sufficiently evidenced;
- smallest sufficient change is known;
- stable clause IDs are preserved unless the change intentionally replaces them;
- validation query exists;
- protected-skill restrictions are satisfied.

If any fail, stop at audit/proposal.

## `$refine` handoff

Use `REFINE-SKILL-v3`.

The brief must bind the source packet, target kind, gap and clause refs, expected delta, optimization boundary, intervention budget, forbidden changes, smallest-change hint, and static/contract/script/behavioral validation.

Do not hand `$refine` raw transcripts when STE-v1 is available.

## `$seq` special-spec handoff

When a missing evidence surface blocks diagnosis, emit `SEQ-SPEC-HANDOFF-v2` with the need, observed gap, desired command/packet fields, acceptance criteria, validation examples, and source evidence.

Do not edit `$seq` inside ordinary skill refinement.

## Subagent policy

Default root-only for small, explicit gaps.

Use:

```text
skill_contract_modeler
```

when the target is decision-oriented and lacks SKDC-v1.

Use:

```text
skill_decision_provenance_auditor
```

when episodes are numerous or attribution is ambiguous.

Use:

```text
skill_outcome_skeptic
```

when compliance/outcome correlation could be mistaken for causation.

`$refine` owns all authorized skill-package optimization after `$tune` produces a bounded packet or brief. Do not delegate this to a system-managed optimizer.

## Validation

Static:

```bash
uv run --with pyyaml -- python3 \
  codex/skills/.system/skill-creator/scripts/quick_validate.py \
  codex/skills/<skill>
```

Contract:

```bash
python3 codex/skills/tune/tools/decision_contract_lint.py \
  codex/skills/<skill>/references/decision-contract.yaml
```

Behavioral:

```text
rerun the exact skill-decision-audit query named by validation_query
```

A text edit is not validated merely because frontmatter parses.

## Report

```text
Tuned:
- Target:
- Target kind:
- Mode:

Evidence:
- Source:
- Packet:
- Contract authority:
- Decision episodes:
- Limitations:

Diagnosis:
- Intended:
- Observed:
- Gap:
- Decision effect:
- Outcome signal:

Skill delta:
- From:
- To:
- Smallest change:
- Repeat state:

Handoff / action:
- <no action | refine brief | seq spec | applied edit>

Validation:
- Static:
- Contract:
- Behavioral:

Remaining uncertainty:
```

## Hard rules

- Raw mentions are not activation.
- Activation is not decision influence.
- Decision influence is not outcome causality.
- A successful outcome is not proof of skill effectiveness by itself.
- A clause never observed may be unnecessary, untriggered, or merely unobservable; do not assume which.
- Preserve denominators.
- Preserve counterevidence.
- Prefer no edit over a weakly supported edit.
- No decision delta, no full cycle.
- No repeated proposal without terminal state.
- No `$seq` CLI edit without a separate spec.
