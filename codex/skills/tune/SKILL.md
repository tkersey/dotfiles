---
name: tune
description: "Diagnose and optimize existing Codex skills from real usage evidence. Trigger when asked to use `$tune`, analyze a skill's usage, compare intended vs observed behavior, inspect missed/false/partial activations, mine `$seq` evidence, classify skill gaps, or produce a `$refine` brief. For analysis/recommendation asks, stop at audit/proposal; only apply edits when the user explicitly asks to change files now."
---

# Tune

## Overview

Use `tune` to improve an existing Codex skill by comparing the skill's intended contract with observed usage evidence.

`tune` is an orchestration skill:

- `$seq` mines session, memory, tool, workflow, routing, and historical skill-block evidence.
- `$tune` reconstructs the target skill's intended-use contract, interprets evidence, classifies gaps, and writes a precise `$refine` brief.
- `$refine` performs the in-place skill edit or upgrade and validates it.
- `$ship` and `$land` remain responsible for PR and merge workflows.
- `$ms` remains responsible for creating new skills and direct skill-surgery primitives when no usage-backed diagnosis is needed.

Core question:

```text
Given what this skill is intended to do and how it is currently being used,
is it working as intended, and what should change?
```

## Trigger Cues

Use `$tune` when the user asks to:

- Analyze a skill's current usage or performance.
- Determine whether a skill is being used as intended.
- Optimize, improve, fix, or upgrade a skill based on usage evidence.
- Use `$seq` and `$refine` together.
- Compare a skill's stated purpose with actual behavior.
- Find missed activations, false activations, partial activations, or weak activations.
- Diagnose trigger, workflow, metadata, tooling, validation, resource, or boundary gaps.
- Produce a usage-backed refinement brief for `$refine`.
- Apply a usage-backed refinement when the user explicitly asks to change files now.

Example prompts:

- "Use `$tune` on the pdf skill."
- "Analyze whether `$seq` is being used as intended."
- "Do a deep analysis of the tune skill so we can make it optimal."
- "Tune the docx skill based on recent sessions, but don't edit yet."
- "Use `$seq` to inspect current usage of the gh skill, then refine it."
- "Find out why the slides skill keeps missing validation and improve it."
- "Compare the algebra skill's intended contract to how agents actually use it."
- "Create a refinement brief for the ship skill from recent usage evidence."

## Non-Goals

Do not use `$tune` to:

- Edit a skill directly without usage, validation, routing, or explicit current-turn evidence. Use `$refine` or `$ms` as appropriate.
- Mine arbitrary sessions without a target skill. Use `$seq`.
- Create a new skill. Use `$ms`.
- Apply an already-complete refinement brief without further diagnosis. Use `$refine`.
- Run autonomous broad ecosystem scans.
- Create or update PRs. Use `$ship`.
- Merge PRs or clean up branches. Use `$land`.
- Replace `$refine` as the direct editing/upgrading skill.
- Replace `$seq` as the session-mining tool.
- Treat raw skill mentions as proof of successful skill use.
- Make broad redesigns from one ambiguous session.

## Operating Modes

Choose exactly one mode before mining evidence.

### Audit Only

Use when the user asks whether a skill is working, how it is being used, or what the evidence shows.

Output:

- intended-use contract,
- observed-use summary,
- evidence classes,
- gap classification,
- recommended next step.

Do not edit the skill.

### Proposal Only

Use when the user asks what should change, asks for deep analysis, asks for optimization guidance, or wants a refinement plan.

Output:

- usage-backed diagnosis,
- `$refine` brief,
- success criteria,
- validation plan,
- remaining uncertainty.

Do not edit the skill unless the user explicitly asks to apply the proposal.

### Apply with `$refine`

Use only when the user explicitly asks to apply, edit, patch, update, or change skill files now.

Output:

- tuning diagnosis,
- `$refine` brief,
- applied changes,
- validation proof,
- remaining uncertainty.

## Mode Precedence

Resolve mode in this order:

1. Explicit `apply`, `edit the files`, `patch now`, `make the change`, `update the skill`, or equivalent file-change instruction: `apply-with-refine` if the apply gate is satisfied.
2. Explicit `audit`, `analyze`, `deep analysis`, `is it working`, `what should change`, `recommend`, `proposal`, or `make it optimal`: `audit-only` or `proposal-only`, even when the prompt also says `improve`, `fix`, `optimize`, or `upgrade`.
3. Ambiguous optimization requests: `proposal-only`.
4. Complete evidence-backed brief supplied and user asks only for file edits: hand off to `$refine` or run only the `$refine` phase.
5. Protected or self-targeted skills: default to `proposal-only` unless the user explicitly asks to apply file changes.

Choose `audit-only` for status/evidence questions. Choose `proposal-only` when the user asks what to change, asks for deep analysis, or asks how to optimize. Choose `apply-with-refine` only after the apply gate below passes.

## Apply Gate

All conditions must hold before editing:

- The user explicitly asked to change skill files now.
- The target skill is identified.
- The intended-use contract has been reconstructed first.
- Evidence is strong enough for the proposed change, or the user has supplied explicit current-turn feedback that supports a narrow local change.
- The change is the smallest sufficient edit or justified upgrade.
- Protected-skill restrictions are satisfied.
- Validation is available or, if blocked, the final report states exactly what blocked it and does not claim a pass.

If any condition fails, stop at audit-only or proposal-only.

## Inputs

Identify these before mining evidence:

- Target skill name or path.
- User's tuning goal.
- Time window, if provided.
- Specific failure mode, trigger phrase, workflow, repo, workdir, command pattern, or session, if provided.
- Desired or inferred mode.
- Protected-skill status.
- Whether raw transcript excerpts are allowed. Default: do not include them.

If no time window is provided, default to the last 90 days for general usage tuning.

## Protected Skill Gate

Protected skills require extra care:

- `seq`
- `tune`
- `refine`
- `cron`
- `ship`
- `land`
- `.system/*`

For protected skills:

- Proceed only when the user explicitly names the protected skill.
- Prefer audit-only or proposal-only unless the user clearly asks to apply a change.
- Keep any applied change narrow.
- Preserve the skill's core role and companion-skill boundaries.
- Require validation proof for every edit.

When the target skill is `tune`, default to proposal-only unless the user explicitly asks to apply file changes. Preserve mode-selection, evidence-strength, and companion-skill boundaries unless direct evidence justifies changing them.

## Companion-Skill Boundaries

- `$seq` owns evidence mining and artifact/session forensics.
- `$tune` owns intended-vs-observed diagnosis, evidence interpretation, gap classification, and `$refine` brief writing.
- `$refine` owns in-place edits once the gap and success criteria are known.
- `$ms` owns new skill creation and direct skill surgery when no usage-backed tuning diagnosis is needed.
- `$ship` and `$land` own PR and merge workflows.

If the user asks to discover whether a change is needed, `$tune` owns the turn. If the user provides a complete evidence-backed brief and asks only for edits, hand off to `$refine`. If the user asks for both diagnosis and edits, diagnose first, write the brief, then invoke `$refine` only if the apply gate passes.

## Workflow

### 1. Scope the Tuning Run

Write:

```text
Goal: Tune <skill> so that <intended behavior> better matches <observed or suspected usage pattern>.
Mode: audit-only | proposal-only | apply-with-refine
Apply gate: pass | blocked: <reason>
```

### 2. Reconstruct the Intended-Use Contract

Read the target skill before judging usage:

```text
codex/skills/<skill>/SKILL.md
codex/skills/<skill>/agents/openai.yaml
codex/skills/<skill>/scripts/
codex/skills/<skill>/references/
codex/skills/<skill>/assets/
```

Only read resources relevant to the target skill or suspected gap.

Summarize:

- Primary purpose.
- Trigger cues.
- Anti-triggers and boundaries.
- Expected inputs and outputs.
- Required workflow.
- Required tools, scripts, references, or assets.
- Validation expectations.
- Companion-skill handoffs.
- Upgrade boundaries.

### 3. Mine Observed Usage with `$seq`

Use `$seq` for session-backed evidence. Prefer lifted commands before raw `seq query`. Use `references/seq-evidence-playbook.md` for command selection.

Baseline commands:

```bash
seq skill-success-rank --root ~/.codex/sessions --skill <skill> --mode sessions --last 90d --format jsonl
seq skill-audit --root ~/.codex/sessions --skill <skill> --mode trend --since <iso8601> --format table
seq skill-cohort --root ~/.codex/sessions --skill <skill> --since <iso8601> --format table
seq skill-blocks --root ~/.codex/sessions --skill <skill> --history latest --format json
seq skill-blocks --root ~/.codex/sessions --skill <skill> --history all --format jsonl
```

Add targeted searches for named triggers, failure phrases, workflows, workdirs, or command patterns. Use raw `seq query` only when no specialized command covers the evidence need.

### 4. Sanitize Evidence

Use sanitized summaries in user-facing reports and refinement briefs.

Do not include raw transcript text, raw memory text, secrets, credentials, private personal details, sensitive local paths, private user-identifying path fragments, or unnecessarily long command output. Raw excerpts are allowed only when the user explicitly asks for them and the content is safe to show.

### 5. Build an Evidence Ledger

For each important source, record:

```text
- Command or source:
- Why this source was chosen:
- What it proves:
- What it does not prove:
- Evidence class:
- Confidence: high | medium | low
- Recurrence:
- Counterevidence:
- Sanitization note:
```

Do not treat running a command as proof. Explain what the result actually establishes.

### 6. Classify Evidence Strength

Strong evidence:

- `explicit_user_feedback`
- `repeated_session_evidence`
- `clear_validation_failure`
- `clear_routing_failure`
- `repeated_manual_workaround`
- `stale_or_contradictory_metadata`
- `historical_skill_regression`

Weak evidence:

- `thin_usage_signal`
- `single_ambiguous_session`
- `low_activation_count`
- `possible_trigger_overlap`
- `style_preference_only`
- `missing_examples_without_failure`

Default thresholds:

- `repeated_session_evidence`: same gap appears in at least 3 relevant sessions, or at least 2 independent sessions plus explicit user feedback.
- `repeated_manual_workaround`: substantially similar workaround appears in at least 3 sessions or across at least 2 target skills.
- `low_activation_count`: fewer than 3 relevant activations in the chosen window.
- `single_ambiguous_session`: one session with unclear intent, incomplete trace, or no explicit outcome signal.
- `clear_routing_failure`: user asked for the skill's owned work and a different skill or no skill handled the core workflow.
- `historical_skill_regression`: behavior changed after a material skill-block, trigger, metadata, or workflow update.

Explicit current-turn user feedback can be strong evidence for a narrow local change. It should not justify a broad redesign without corroborating session evidence.

### 7. Diagnose the Gap

Classify the mismatch using `references/gap-taxonomy.md`:

- activation,
- interpretation,
- workflow,
- tooling,
- resource,
- validation,
- metadata,
- boundary.

Identify the smallest sufficient fix. Prefer no edit when evidence is thin or the likely change crosses skill boundaries.

### 8. Produce the `$refine` Brief

Use `references/refinement-brief-template.md`. Include the evidence ledger, counterevidence, risk, success criteria, must-not-change constraints, and validation plan.

### 9. Apply with `$refine`, If Allowed

Use `$refine` only after the apply gate passes:

```text
Use `$refine` on <skill> with this tuning brief. Make the smallest sufficient edit that closes the diagnosed <gap_type> gap. Preserve unrelated behavior. Validate with quick_validate. Update agents/openai.yaml only if metadata changed. Add scripts/references/assets only if the brief explicitly justifies them.
```

If the runtime cannot literally invoke another skill, perform the edit by following `$refine` rules and report that the `$refine` phase was executed manually.

### 10. Validate

For any applied edit, run:

```bash
uv run --with pyyaml -- python3 codex/skills/.system/skill-creator/scripts/quick_validate.py codex/skills/<skill>
```

If shared assumptions or multiple skills changed, run:

```bash
codex/skills/tune/scripts/validate-changed-skills
```

If scripts changed, run at least one representative sample command.

If `codex/skills/.system/skill-creator/scripts/quick_validate.py` is unavailable, report validation as blocked and do not claim validation passed. Do not replace it with an unrelated validator.

### 11. Report

Use this result shape:

```text
Tuned: <skill>

Mode:
- <audit-only | proposal-only | apply-with-refine>

Apply gate:
- <pass | blocked: reason>

Evidence:
- <evidence_class>: <sanitized evidence summary>

Diagnosis:
- Intended: <summary>
- Observed: <summary>
- Gap: <gap type and explanation>

Refinement:
- <files changed, proposed files, or no edit>
- <why the changes close the gap>

Validation:
- <command>: <pass/fail/blocked/not run and why>

Remaining uncertainty:
- <anything not proven by the evidence>
```

## Upgrade Policy

`tune` may recommend or drive upgrades when the current skill cannot reliably satisfy its intended contract under observed usage.

Allowed upgrade types:

- Trigger upgrade.
- Workflow upgrade.
- Capability upgrade within the skill's existing purpose.
- Tooling upgrade.
- Resource upgrade.
- Metadata upgrade.
- Validation upgrade.
- Handoff or boundary upgrade.

Do not recommend a capability upgrade that changes the skill's core purpose. That should be a new skill or an explicit user-directed redesign.

## Quality Bar

A good `$tune` run:

- Chooses the mode before mining evidence.
- Reads the target skill before judging usage.
- Uses `$seq` evidence for observed behavior.
- Separates intended purpose from observed behavior.
- Maintains an evidence ledger with counterevidence.
- Classifies the gap before proposing a fix.
- Hands `$refine` a precise brief.
- Keeps edits small unless evidence justifies an upgrade.
- Validates applied changes.
- Reports uncertainty when evidence is thin.

A bad `$tune` run:

- Treats "optimize" or "improve" as permission to edit when the user asked for analysis.
- Rewrites a skill without usage or performance evidence.
- Treats raw mentions as successful activations.
- Confuses `$seq` mining with `$refine` editing.
- Makes broad changes from one ambiguous session.
- Expands triggers without checking overlap.
- Adds scripts without repeated deterministic need.
- Includes raw private transcript text unnecessarily.
