---
name: tune
description: "Use `$seq` and `$refine` together to tune existing Codex skills from real usage evidence. Trigger when asked to analyze whether a skill is working as intended, compare intended vs observed use, find missed/false/partial activations, diagnose usage gaps, produce a refinement brief, or apply a targeted skill improvement with `$refine`."
---

# Tune

## Overview

Use `tune` to improve an existing Codex skill by comparing what the skill is supposed to do with how it is actually being used.

`tune` is an orchestration skill. It does not replace the core skills it coordinates:

- `$seq` mines sessions, memories, skill mentions, historical skill blocks, routing gaps, workflow evidence, and tool traces.
- `$tune` interprets that evidence, reconstructs the target skill's intended-use contract, classifies the gap, and writes a precise refinement brief.
- `$refine` performs the actual in-place skill edit or upgrade and validates the result.
- `$ship` and `$land` remain responsible for PR and merge workflows when needed.
- `$auto` remains responsible for broad autonomous skill-ecosystem scans and guarded autonomous maintenance.

Core question:

```text
Given what this skill is intended to do and how it is currently being used,
is it working as intended, and what should change?
```

## Trigger Cues

Use `$tune` when the user asks to:

- Analyze a skill's current usage.
- Determine whether a skill is being used as intended.
- Improve a skill based on session evidence.
- Use `$seq` and `$refine` together.
- Compare a skill's stated purpose with actual behavior.
- Find missed activations, false activations, partial activations, or weak activations.
- Diagnose trigger, workflow, metadata, tooling, validation, or boundary gaps.
- Decide whether a skill should be upgraded.
- Produce a refinement brief for `$refine`.
- Apply a usage-backed refinement or upgrade to a target skill.

Example prompts:

- "Use `$tune` on the pdf skill."
- "Analyze whether `$seq` is being used as intended."
- "Tune the docx skill based on recent sessions."
- "Use `$seq` to inspect current usage of the gh skill, then refine it."
- "Find out why the slides skill keeps missing validation and improve it."
- "Compare the algebra skill's intended contract to how agents actually use it."
- "Create a refinement brief for the ship skill from recent usage evidence."

## Non-Goals

Do not use `$tune` to:

- Edit a skill directly without usage or performance evidence. Use `$refine`.
- Mine arbitrary sessions without a target skill. Use `$seq`.
- Run autonomous broad ecosystem scans. Use `$auto`.
- Create or update PRs. Use `$ship`.
- Merge PRs or clean up branches. Use `$land`.
- Replace `$refine` as the direct editing/upgrading skill.
- Replace `$seq` as the session-mining tool.
- Treat raw skill mentions as proof of successful skill use.
- Make broad redesigns from one ambiguous session.

## Operating Modes

Choose the mode from the user's request.

### Audit Only

Use when the user asks whether a skill is working, how it is being used, or what the current evidence shows.

Output:

- intended-use contract,
- observed-use summary,
- evidence classes,
- gap classification,
- recommended next step.

Do not edit the skill.

### Proposal Only

Use when the user asks what should change or wants a refinement plan.

Output:

- usage-backed diagnosis,
- `$refine` brief,
- success criteria,
- validation plan.

Do not edit the skill unless the user asks to apply the proposal.

### Apply with `$refine`

Use when the user asks to tune, improve, fix, upgrade, or apply the usage-backed change.

Output:

- tuning diagnosis,
- `$refine` brief,
- applied changes,
- validation proof,
- remaining uncertainty.

Prefer this mode when the request includes verbs such as `improve`, `fix`, `refine`, `upgrade`, `patch`, `update`, or `apply`.

## Inputs

Identify these before mining evidence:

- Target skill name or path.
- User's tuning goal.
- Time window, if provided.
- Specific failure mode, if provided.
- Specific sessions, repos, workdirs, or commands, if provided.
- Desired mode: audit-only, proposal-only, or apply-with-refine.
- Protected-skill status.
- Whether raw transcript excerpts are allowed. Default: do not include them.

If no time window is provided, use a recent window appropriate to the request. For general usage tuning, default to the last 90 days.

## Protected Skill Gate

Protected skills require extra care:

- `seq`
- `refine`
- `cron`
- `auto`
- `ship`
- `land`
- `.system/*`

For protected skills:

- Proceed only when the user explicitly names the protected skill.
- Prefer audit-only or proposal-only unless the user clearly asks to apply a change.
- Keep any applied change narrow.
- Preserve the skill's core role and companion-skill boundaries.
- Require validation proof for every edit.

## Workflow

### 1. Scope the Tuning Run

Write a one-line goal:

```text
Goal: Tune <skill> so that <intended behavior> better matches <observed or suspected usage pattern>.
```

Choose the mode:

```text
Mode: audit-only | proposal-only | apply-with-refine
```

If the user asks a diagnostic question, stop at audit-only unless they ask for edits. If the user asks to improve, fix, update, or upgrade, continue to apply-with-refine when the evidence supports it.

### 2. Reconstruct the Intended-Use Contract

Read the target skill first:

```text
codex/skills/<skill>/SKILL.md
codex/skills/<skill>/agents/openai.yaml
codex/skills/<skill>/AUTO.md
codex/skills/<skill>/scripts/
codex/skills/<skill>/references/
codex/skills/<skill>/assets/
```

Only read resources that are relevant to the target skill or the suspected gap.

Summarize the intended-use contract:

- Primary purpose.
- Trigger cues.
- Anti-triggers and boundaries.
- Expected inputs.
- Expected outputs.
- Required workflow.
- Required tools, scripts, references, or assets.
- Validation expectations.
- Companion-skill handoffs.
- Upgrade boundaries.

Do not judge usage before reconstructing the intended contract.

### 3. Mine Observed Usage with `$seq`

Use `$seq` for session-backed evidence. Prefer lifted commands before raw `seq query`.

Start with skill-level usage:

```bash
seq skill-success-rank --root ~/.codex/sessions --skill <skill> --mode sessions --last 90d --format jsonl
seq skill-audit --root ~/.codex/sessions --skill <skill> --mode trend --since <iso8601> --format table
seq skill-cohort --root ~/.codex/sessions --skill <skill> --since <iso8601> --format table
```

Inspect historical skill versions when behavior may have changed:

```bash
seq skill-blocks --root ~/.codex/sessions --skill <skill> --history latest --format json
seq skill-blocks --root ~/.codex/sessions --skill <skill> --history all --format jsonl
```

Use targeted searches when the question names a trigger phrase, failure phrase, command pattern, or workflow:

```bash
seq message-search --root ~/.codex/sessions --contains "<trigger-or-failure-phrase>" --roles user,assistant --limit 50 --format jsonl
seq tool-search --root ~/.codex/sessions --contains "<repeated-command-or-tool-pattern>" --mode rows --format table
seq workflow-audit --root ~/.codex/sessions --workflow <workflow-name> --mode report --since <iso8601> --format markdown
seq session-detail --root ~/.codex/sessions --session-id <session_id> --format markdown
```

Use raw `seq query` only when no specialized command covers the evidence need.

### 4. Sanitize Evidence

Use sanitized summaries in user-facing reports and refinement briefs.

Do not include:

- raw transcript text,
- raw memory text,
- secrets,
- credentials,
- private personal details,
- sensitive local paths,
- private user-identifying path fragments,
- unnecessarily long command outputs.

Raw excerpts are allowed only when the user explicitly asks for them and the content is safe to show.

### 5. Classify Evidence Strength

Use named evidence classes.

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

One strong evidence class can justify an applied `$refine` change. Weak-only evidence usually supports audit-only or proposal-only. A tiny clarification may be applied on weak evidence only when it is local, low-risk, and clearly improves the skill's contract.

### 6. Diagnose the Gap

Classify the mismatch between intended and observed use.

#### Activation Gap

The skill fails to trigger when it should, or triggers when it should not.

Likely `$refine` actions:

- frontmatter description update,
- trigger cue update,
- anti-trigger addition,
- example addition,
- `agents/openai.yaml` update.

#### Interpretation Gap

The skill triggers, but the agent misunderstands what to do.

Likely `$refine` actions:

- clarify purpose,
- add decision rules,
- add input classification,
- add positive and negative examples.

#### Workflow Gap

The skill triggers, but agents skip, weaken, or misorder required steps.

Likely `$refine` actions:

- revise workflow order,
- add checkpoints,
- add fallback rules,
- add validation requirements.

#### Tooling Gap

The skill repeatedly uses fragile ad hoc commands or lacks deterministic helpers.

Likely `$refine` actions:

- add or revise scripts,
- document command usage,
- add representative sample runs,
- avoid scripts for judgment-heavy work.

#### Resource Gap

The skill needs reusable reference material or assets.

Likely `$refine` actions:

- add `references/`,
- add `assets/`,
- move long reusable guidance out of `SKILL.md`,
- keep `SKILL.md` concise.

#### Validation Gap

The skill lacks a clear proof path.

Likely `$refine` actions:

- add `quick_validate`,
- add script sample commands,
- add corpus validation when shared assumptions change,
- add concrete success criteria.

#### Metadata Gap

Skill metadata no longer matches the skill's behavior or actual use.

Likely `$refine` actions:

- update frontmatter description,
- update `agents/openai.yaml`,
- align display name, short description, and default prompt.

#### Boundary Gap

The skill overlaps with another skill or has weak handoff rules.

Likely `$refine` actions:

- add non-goals,
- add anti-triggers,
- clarify companion-skill routing,
- tighten handoff rules.

### 7. Decide Whether to Apply

Stop at audit-only when:

- the user only asks whether the skill is working,
- evidence is thin or ambiguous,
- the target is protected and no explicit edit was requested,
- the likely change is broad or risky,
- `$seq` evidence does not support the suspected gap.

Produce proposal-only when:

- there is a plausible gap but not enough proof to edit,
- the user asks for recommendations,
- the edit would affect trigger boundaries across multiple skills,
- the target skill's current contract is ambiguous.

Apply with `$refine` when:

- the user asks to improve, fix, tune, update, or upgrade,
- direct user feedback identifies the problem,
- `$seq` shows repeated session evidence,
- validation failure is clear,
- routing failure is clear,
- the change is small enough to be local and validated.

### 8. Produce the `$refine` Brief

Before invoking `$refine`, write a concise brief:

```text
Target skill: <skill>

Tuning goal:
- <one-line goal>

Intended-use contract:
- Purpose: <summary>
- Trigger boundary: <summary>
- Workflow expectation: <summary>
- Validation expectation: <summary>

Observed usage:
- Evidence class: <class>
- Source: <seq command or user feedback>
- Finding: <sanitized finding>
- Recurrence: <frequency or recurrence summary, if known>

Gap:
- Type: <activation | interpretation | workflow | tooling | resource | validation | metadata | boundary>
- Diagnosis: <specific mismatch>

Recommended `$refine` action:
- <smallest sufficient edit or upgrade>

Success criteria:
- <criterion 1>
- <criterion 2>
- <criterion 3>

Validation:
- quick_validate target skill
- script sample run, if scripts changed
- corpus validation, if shared assumptions or multiple skills changed
```

### 9. Invoke `$refine`

Use `$refine` to apply the brief. The handoff should be explicit:

```text
Use `$refine` on <skill> with this tuning brief. Make the smallest sufficient edit that closes the diagnosed <gap_type> gap. Preserve unrelated behavior. Validate with quick_validate. Update agents/openai.yaml only if metadata changed. Add scripts/references/assets only if the brief explicitly justifies them.
```

If the runtime cannot literally invoke another skill, perform the edit by following `$refine` rules and clearly report that the `$refine` phase was executed manually.

### 10. Validate

Require `$refine` validation:

```bash
uv run --with pyyaml -- python3 codex/skills/.system/skill-creator/scripts/quick_validate.py codex/skills/<skill>
```

If shared assumptions or multiple skills changed, also run:

```bash
codex/skills/auto/scripts/auto-validate-corpus codex/skills
```

If scripts changed, run at least one representative sample command.

### 11. Report

Use this result shape:

```text
Tuned: <skill>

Mode:
- <audit-only | proposal-only | apply-with-refine>

Evidence:
- <evidence_class>: <sanitized evidence summary>

Diagnosis:
- Intended: <summary>
- Observed: <summary>
- Gap: <gap type and explanation>

Refinement:
- <files changed, or proposed files>
- <why the changes close the gap>

Validation:
- <command>: <pass/fail/not run and why>

Remaining uncertainty:
- <anything not proven by the evidence>
```

## Upgrade Policy

`tune` may recommend or drive upgrades, not just wording fixes.

Allowed upgrade types:

- Trigger upgrade.
- Workflow upgrade.
- Capability upgrade within the skill's existing purpose.
- Tooling upgrade.
- Resource upgrade.
- Metadata upgrade.
- Validation upgrade.
- Handoff or boundary upgrade.

An upgrade is justified when the current skill cannot reliably satisfy its intended contract under observed usage.

Do not recommend a capability upgrade that changes the skill's core purpose. That should be a new skill or an explicit user-directed redesign.

## Decision Rules for Common Cases

### Missed Activation

Evidence pattern:

- User asks for the skill's work, but the skill is absent or appears late.

Action:

- Strengthen frontmatter description and trigger cues.
- Add user-language examples.
- Add anti-overlap notes if another skill intercepted the request.

### False Activation

Evidence pattern:

- Skill activates in sessions it should not own.

Action:

- Add anti-triggers and non-goals.
- Tighten frontmatter description.
- Clarify handoff to the correct skill.

### Partial Activation

Evidence pattern:

- Skill appears, but key workflow steps are skipped.

Action:

- Add workflow checkpoints.
- Add validation requirements.
- Add an output checklist.

### Repeated Manual Workaround

Evidence pattern:

- Similar command sequence appears repeatedly across sessions.

Action:

- Add a small deterministic helper script only if it reduces fragility.
- Add sample-run validation.

### Stale Metadata

Evidence pattern:

- `agents/openai.yaml` or frontmatter no longer matches current behavior.

Action:

- Update metadata and validate.

### Thin Evidence

Evidence pattern:

- One ambiguous session or low activation count.

Action:

- Produce audit or proposal only.
- Avoid broad changes.

## Quality Bar

A good `$tune` run:

- Reads the target skill before judging usage.
- Uses `$seq` evidence for observed behavior.
- Separates intended purpose from observed behavior.
- Classifies the gap before proposing a fix.
- Hands `$refine` a precise brief.
- Keeps edits small unless evidence justifies an upgrade.
- Validates the result.
- Reports uncertainty when evidence is thin.

A bad `$tune` run:

- Rewrites a skill without usage evidence.
- Treats raw mentions as successful activations.
- Confuses `$seq` mining with `$refine` editing.
- Makes broad changes from one ambiguous session.
- Expands triggers without checking overlap.
- Adds scripts without repeated deterministic need.
- Includes raw private transcript text unnecessarily.
