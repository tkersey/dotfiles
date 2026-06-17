---
name: tune
description: "Goal-native skill tuning from orthogonal evidence. Use for `$tune`, skill usage analysis, intended-vs-observed behavior, missed/false/partial activations, proposal-only gaps, skill delta candidates, `$refine` briefs, `$seq` evidence gaps, or validated skill edits only when explicit. Stop at audit/proposal unless apply is explicit. Do not edit `$seq` CLI without a separate special spec."
---

# Tune

## Purpose

Use `$tune` to improve an existing Codex skill by comparing its intended contract with observed evidence.

In `/goal` workflows, `$tune` should produce a bounded **decision delta** or a terminal state, not another repeated essay.

Core rules:

```text
No decision delta, no full cycle.
No repeated proposal without terminal state.
No skill edit without explicit apply route.
Seq CLI changes require a separate special spec.
```

## Role boundaries

- `$tune` owns diagnosis, evidence interpretation, gap classification, skill-delta candidates, and `$refine` briefs.
- `$shadow` owns watched-session cycle filtering.
- `$seq` owns historical/session/tool evidence surfaces.
- `$refine` owns in-place skill edits once the gap and success criteria are known.
- `$ship` and `$land` own PR and merge workflows.
- `$ms` owns new skill creation or direct skill surgery when no usage-backed diagnosis is needed.

## Trigger cues

Use `$tune` when the user asks to:

- analyze a skill's current, in-flight, or historical usage;
- determine whether a skill is working as intended;
- optimize, improve, fix, or upgrade a skill based on usage/evidence;
- compare intended vs observed behavior;
- find missed, false, partial, or weak activations;
- diagnose trigger, workflow, metadata, tooling, validation, resource, source-scope, or boundary gaps;
- produce a usage-backed `$refine` brief;
- apply a validated edit when explicitly asked.

## Non-goals

Do not use `$tune` to:

- edit directly without evidence;
- mine arbitrary sessions without a target skill;
- create a new skill;
- apply an already-complete brief without diagnosis;
- run broad autonomous ecosystem scans;
- create PRs or merge work;
- treat raw skill mentions as successful skill use;
- make broad redesigns from one ambiguous session;
- produce repeated proposal-only analyses without terminal state;
- change `$seq` CLI without a separate special spec.

## Modes

Choose exactly one mode before mining evidence.

### audit-only

Use when the user asks what evidence shows.

Output:

- intended-use contract;
- evidence-source declaration;
- observed-use summary;
- evidence classes;
- gap classification;
- recommended next step.

No edits.

### proposal-only

Default for analysis, deep optimization, and "what should change?"

Output:

- usage-backed diagnosis;
- evidence ledger;
- skill delta candidate or `$refine` brief;
- success criteria;
- validation plan;
- remaining uncertainty.

No edits.

### apply-with-refine

Use only when the user explicitly asks to apply, edit, patch, update, or change skill files now.

Output:

- diagnosis;
- evidence ledger;
- `$refine` brief;
- applied changes;
- validation proof;
- commit/push proof when policy allows;
- remaining uncertainty.

## Mode precedence

1. Explicit file-change instruction: `apply-with-refine` if apply gate passes.
2. Explicit audit/analysis/proposal: `audit-only` or `proposal-only`.
3. Ambiguous optimization: `proposal-only`.
4. Complete evidence-backed brief plus edit request: hand off to `$refine`.
5. Protected/self-targeted skills: default `proposal-only`.

## Apply gate

All must hold before editing:

- user explicitly asked to change files now;
- target skill identified;
- mode and evidence sources declared;
- intended-use contract reconstructed first;
- evidence is strong enough for the proposed change;
- edit is smallest sufficient change;
- protected-skill restrictions are satisfied;
- validation is available or blockage is reported;
- worktree and publishing context can be checked.

If any condition fails, stop at audit/proposal.

## Evidence source model

Supported sources:

```text
in-flight
history
provided
worktree
mixed
```

Declare:

```text
Evidence source:
- Kind:
- Locator:
- Scope:
- Window:
- Access method:
- Privacy constraint:
- Limitation:
```

Do not make historical `$seq` mandatory for in-flight tuning. Do not infer historical recurrence from current-turn evidence alone.

## Goal-native skill delta

When `$tune` is invoked as part of `/goal` or `$shadow`, prefer a compact decision delta:

```yaml
skill_delta_candidate:
  record_version: SDC-v1
  target_skill: "..."
  source:
    kind: in-flight | history | provided | worktree | mixed
    locator: "..."
  observed_gap:
    gap_type: activation | interpretation | workflow | tooling | resource | validation | metadata | boundary | source-scope
    signature: "..."
    evidence_class: explicit_current_turn_feedback | in_flight_validation_failure | repeated_session_evidence | clear_validation_failure | clear_routing_failure | repeated_manual_workaround | tooling_gap | weak_signal
  expected_decision_delta:
    from: "..."
    to: "..."
  proposed_action:
    kind: no-action | status-only | final-brief | ask-apply-permission | handoff-refine | handoff-seq-special-spec | retire | apply-with-refine
    reason: "..."
  protected_contracts: []
  validation_plan: []
```

If there is no expected decision delta, do not produce a long new analysis.

## Repeat Proposal Ledger

Track repeated proposal-only gaps:

```yaml
repeat_proposal_ledger:
  proposal_signature: "..."
  target_skill: "..."
  first_seen: "..."
  last_seen: "..."
  repeat_count: 0
  evidence_delta_since_first: yes | no | unknown
  state: active | apply-blocked | final-brief | transferred-to-seq | retired
  next_action: ask-apply-permission | emit-final-brief | handoff-seq-special-spec | retire-no-action | continue
```

Hard rule:

```text
If repeat_count >= 3 and evidence_delta_since_first == no, $tune must produce a terminal state, not another full diagnosis.
```

Terminal states:

- `apply-blocked`: the only useful next step is explicit apply permission.
- `final-brief`: produce one final `$refine` brief and stop repeating.
- `transferred-to-seq`: produce a `$seq` special-spec handoff.
- `retired`: no further action unless new evidence appears.

## `$seq` CLI boundary

If tuning identifies a `$seq` CLI change, do not bundle it into ordinary skill edits.

Produce a special-spec handoff:

```yaml
seq_special_spec_handoff:
  spec_version: SEQ-SPEC-HANDOFF-v1
  need: "..."
  observed_gap: "..."
  required_behavior: "..."
  command_shape: "..."
  acceptance_criteria: []
  representative_validation: []
  source_evidence: []
```

The user owns whether to create/apply the special `$seq` CLI spec.

## Evidence strength

Strong evidence:

- explicit current-turn feedback;
- in-flight validation failure;
- provided artifact evidence;
- repeated session evidence;
- clear validation failure;
- clear routing failure;
- repeated manual workaround;
- stale or contradictory metadata;
- historical skill regression.

Weak evidence:

- thin usage signal;
- single ambiguous session;
- low activation count;
- possible trigger overlap;
- style preference only;
- missing examples without failure;
- unbounded history without sampling plan.

Prefer no edit when evidence is weak.

## Workflow

### 1. Scope

```text
Goal: Tune <skill> so that <intended behavior> better matches <observed pattern>.
Mode: audit-only | proposal-only | apply-with-refine
Evidence source: <descriptor>
Apply gate: pass | blocked: <reason>
```

### 2. Reconstruct intended-use contract

Read the target skill before judging usage:

```text
<skill-root>/<skill>/SKILL.md
<skill-root>/<skill>/agents/openai.yaml
<skill-root>/<skill>/scripts/
<skill-root>/<skill>/references/
<skill-root>/<skill>/assets/
```

Only read relevant resources.

### 3. Select evidence

Use the least invasive source that can answer the question. Use `$seq` for historical evidence. Keep mixed-source ledgers separate before synthesis.

### 4. Build evidence ledger

For each important source:

```text
- Source kind:
- Command, locator, or source:
- Why chosen:
- What it proves:
- What it does not prove:
- Evidence class:
- Confidence:
- Scope/window:
- Recurrence:
- Counterevidence:
- Sanitization note:
```

### 5. Diagnose gap

Classify:

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
```

Identify the smallest sufficient fix. Prefer no edit when evidence is thin or source scope ambiguous.

### 6. Produce skill delta or `$refine` brief

For proposal mode, produce either:

- `skill_delta_candidate`;
- `repeat_proposal_ledger` terminal state;
- `$refine` brief;
- `seq_special_spec_handoff`;
- no-action retirement.

Do not produce another full diagnosis for a repeated unchanged proposal.

### 7. Apply only if allowed

Use `$refine` only after apply gate passes:

```text
Use $refine on <skill> with this tuning brief. Make the smallest sufficient edit that closes the diagnosed <gap_type> gap. Preserve unrelated behavior. Validate with quick_validate.
```

If another skill cannot literally be invoked, follow `$refine` rules and report manual execution.

### 8. Validate

For applied edits:

```bash
uv run --with pyyaml -- python3 codex/skills/.system/skill-creator/scripts/quick_validate.py <skill-root>/<skill>
```

If shared assumptions or multiple skills changed:

```bash
codex/skills/tune/scripts/validate-changed-skills
```

If validation is unavailable, report blocked and do not claim pass.

## Report shape

```text
Tuned: <skill>

Mode:
- <audit-only | proposal-only | apply-with-refine>

Evidence sources:
- <source descriptor summary>

Apply gate:
- <pass | blocked: reason>

Evidence:
- <evidence_class>: <sanitized summary>

Diagnosis:
- Intended:
- Observed:
- Gap:

Skill delta:
- Decision delta:
- Proposed action:
- Repeat state:

Refinement / handoff:
- <refine brief | seq special spec | no action | retired>

Validation:
- <command>: <pass/fail/blocked/not run and why>

Remaining uncertainty:
- <what evidence did not prove>
```

## Quality bar

A good `$tune` run:

- chooses mode first;
- declares evidence source and limits;
- reads target skill before judging;
- separates intended vs observed;
- classifies the gap;
- produces a decision delta, terminal repeat state, or precise brief;
- does not repeat unchanged proposal-only findings;
- preserves protected skill boundaries;
- validates applied changes.

A bad `$tune` run:

- treats "optimize" as edit permission;
- repeats the same proposal without terminal state;
- treats raw mentions as successful activations;
- infers history from in-flight evidence;
- edits `$seq` CLI without a special spec;
- rewrites a skill without usage evidence;
- commits unrelated work.
