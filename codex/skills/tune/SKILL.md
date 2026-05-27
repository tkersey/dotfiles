---
name: tune
description: "Diagnose and optimize Codex skills from orthogonal evidence. Trigger for `$tune`, in-flight or historical skill usage analysis, intended-vs-observed behavior, missed/false/partial activations, `$seq` session evidence, skill-gap classification, `$refine` briefs, or applying a validated edit. Stop at audit/proposal for analysis asks; apply, commit, and push only when explicitly asked."
---

# Tune

## Overview

Use `tune` to improve an existing Codex skill by comparing the skill's intended contract with observed evidence.

`tune` is an orchestration skill:

- `$tune` owns diagnosis, evidence interpretation, gap classification, and `$refine` brief writing.
- `$seq` is the default historical-session evidence adapter, not the only possible evidence source.
- `$refine` owns in-place skill edits once the gap and success criteria are known.
- `$ship` and `$land` remain responsible for PR and merge workflows.
- `$ms` remains responsible for new skills and direct skill surgery when no usage-backed diagnosis is needed.

Core question:

```text
Given what this skill is intended to do and what the selected evidence sources show,
is it working as intended, and what should change?
```

## Trigger Cues

Use `$tune` when the user asks to:

- Analyze a skill's current, in-flight, or historical usage.
- Determine whether a skill is being used as intended.
- Optimize, improve, fix, or upgrade a skill based on usage, validation, routing, or current-turn evidence.
- Use `$seq` and `$refine` together.
- Compare a skill's stated purpose with actual behavior.
- Find missed activations, false activations, partial activations, or weak activations.
- Diagnose trigger, workflow, metadata, tooling, validation, resource, or boundary gaps.
- Produce a usage-backed refinement brief for `$refine`.
- Apply a usage-backed refinement when the user explicitly asks to change files now.

Example prompts:

- "Use `$tune` on the pdf skill."
- "Tune this in-flight conversation: should the slides skill have triggered?"
- "Go back through all relevant session history and tune docx."
- "Do a deep analysis of the tune skill so we can make it optimal."
- "Tune the docx skill based on recent sessions, but don't edit yet."
- "Find out why the slides skill keeps missing validation and apply a fix."

## Non-Goals

Do not use `$tune` to:

- Edit a skill directly without evidence. Use `$refine` or `$ms` as appropriate.
- Mine arbitrary sessions without a target skill. Use `$seq`.
- Create a new skill. Use `$ms`.
- Apply an already-complete refinement brief without further diagnosis. Use `$refine`.
- Run autonomous broad ecosystem scans.
- Create or update PRs. Use `$ship`.
- Merge PRs or clean up branches. Use `$land`.
- Treat raw skill mentions as proof of successful skill use.
- Make broad redesigns from one ambiguous session.

## Operating Modes

Choose exactly one mode before mining evidence. Mode is independent of evidence source.

### Audit Only

Use when the user asks whether a skill is working, how it is being used, or what the evidence shows.

Output:

- intended-use contract,
- evidence-source declaration,
- observed-use summary,
- evidence classes,
- gap classification,
- recommended next step.

Do not edit the skill.

### Proposal Only

Use when the user asks what should change, asks for deep analysis, asks for optimization guidance, or wants a refinement plan.

Output:

- usage-backed diagnosis,
- evidence ledger,
- `$refine` brief,
- success criteria,
- validation plan,
- remaining uncertainty.

Do not edit the skill unless the user explicitly asks to apply the proposal.

### Apply with `$refine`

Use only when the user explicitly asks to apply, edit, patch, update, or change skill files now.

Output:

- tuning diagnosis,
- evidence ledger,
- `$refine` brief,
- applied changes,
- validation proof,
- commit and push proof for each validated atomic change,
- remaining uncertainty.

## Mode Precedence

Resolve mode in this order:

1. Explicit file-change instruction such as `apply`, `edit the files`, `patch now`, `make the change`, or `update the skill`: `apply-with-refine` if the apply gate passes.
2. Explicit `audit`, `analyze`, `deep analysis`, `is it working`, `what should change`, `recommend`, `proposal`, or `make it optimal`: `audit-only` or `proposal-only`, even when the prompt also says `improve`, `fix`, `optimize`, or `upgrade`.
3. Ambiguous optimization requests: `proposal-only`.
4. Complete evidence-backed brief supplied and user asks only for file edits: hand off to `$refine` or run only the `$refine` phase.
5. Protected or self-targeted skills: default to `proposal-only` unless the user explicitly asks to apply file changes.

Choose `audit-only` for status/evidence questions. Choose `proposal-only` for deep analysis or change planning. Choose `apply-with-refine` only after the apply gate passes.

## Evidence Source Model

Evidence is orthogonal to `$tune`. `$tune` consumes evidence from declared sources; it must not hard-code the data plane into the skill.

Supported source kinds:

- `in-flight`: current conversation evidence, current user feedback, current tool/validation output, and the workflow that is unfolding now.
- `history`: prior Codex sessions, usually through `$seq`; scope may be recent, arbitrary, explicit session ids, workdir-bound, or repo-bound.
- `provided`: user-supplied briefs, logs, transcripts, validation output, diffs, or artifacts.
- `worktree`: current repo state, changed files, validation output, Git status, and metadata files.
- `mixed`: any combination of the above.

Source descriptor:

```text
Evidence source:
- Kind: in-flight | history | provided | worktree | mixed
- Locator: current conversation | sessions root | session id | workdir | repo | file/artifact | validation output
- Scope: current turn | current conversation | recent window | arbitrary history | explicit sessions | supplied evidence
- Window: <duration/date range/all/none>
- Access method: current context | $seq command | file read | tool output | user-provided text
- Privacy constraint: summarize only | raw excerpts allowed if safe | no raw transcript
- Limitation: <what this source cannot prove>
```

Do not make a historical `$seq` run mandatory for in-flight tuning. Do not let current-turn feedback justify broad historical claims. Use mixed sources when the user asks to connect current behavior to past recurrence.

## Source Selection Rules

- If the user says `this conversation`, `in flight`, `right now`, or points to the current behavior, use `in-flight` first.
- If the user says `recent`, `last N days`, or gives no scope for general usage tuning, use `history` with a recent default window of 90 days.
- If the user says `arbitrary`, `all history`, `go back as far as needed`, or gives explicit session ids, use `history` with an explicit arbitrary scope. Do not silently collapse it to 90 days.
- If the user supplies logs, diffs, validation output, or a refinement brief, use `provided` evidence and record its limits.
- If applying edits, always include `worktree` evidence for validation and publishing checks.
- If evidence sources disagree, report the conflict and prefer proposal-only unless the edit is narrow and directly supported.

## Apply Gate

All conditions must hold before editing:

- The user explicitly asked to change skill files now.
- The target skill is identified.
- The mode and evidence sources are declared.
- The intended-use contract has been reconstructed first.
- Evidence is strong enough for the proposed change, or explicit current-turn feedback supports a narrow local change.
- The change is the smallest sufficient edit or justified upgrade.
- Protected-skill restrictions are satisfied.
- Validation is available or, if blocked, the final report states exactly what blocked it and does not claim a pass.
- The Git/publishing context can be checked before any commit or push is attempted.

If any condition fails, stop at audit-only or proposal-only.

## Commit and Push Policy

In `apply-with-refine`, publish each validated atomic change unless the user explicitly says not to commit or push.

Rules:

- Treat one smallest coherent edit as one atomic change. If several unrelated skill updates are needed, validate, commit, and push each one separately.
- Never commit or push an unvalidated edit. If validation is blocked or fails, report the blockage and leave the change uncommitted unless the user explicitly requested otherwise.
- Stage only files justified by the `$refine` brief. Do not stage unrelated worktree changes.
- If target files already had pre-existing user changes that cannot be separated from the tuning edit, report commit/push as blocked rather than bundling them silently.
- Commit message format: `Tune <skill>: <short gap/fix summary>`.
- Push after each commit with `git push` when an upstream exists; if no upstream exists, use `git push -u origin HEAD` only when `origin` is configured and the current branch is appropriate.
- Do not create PRs, merge branches, or clean up branches. `$ship` and `$land` own those workflows.

Publishing sequence after validation passes:

```bash
git status --short
git add -- <scoped changed files>
git diff --cached --check
git commit -m "Tune <skill>: <short gap/fix summary>"
git rev-parse --abbrev-ref --symbolic-full-name @{u} >/dev/null 2>&1 && git push
# If no upstream exists and origin is configured, use: git push -u origin HEAD
```

Record the commit SHA and push result in the final report.

## Inputs

Identify these before mining evidence:

- Target skill name or path.
- User's tuning goal.
- Desired or inferred mode.
- Evidence source kind and scope.
- Skill root, if different from `codex/skills`.
- Sessions root, if historical evidence is used and different from `~/.codex/sessions`.
- Time window, explicit session ids, workdir, repo, or file/artifact locators, if provided.
- Specific failure mode, trigger phrase, workflow, command pattern, or validation issue, if provided.
- Protected-skill status.
- Whether raw transcript excerpts are allowed. Default: do not include them.

Default only when unspecified: general historical tuning uses `history` over the last 90 days. In-flight tuning uses current conversation evidence first.

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

When the target skill is `tune`, default to proposal-only unless the user explicitly asks to apply file changes. Preserve mode-selection, evidence-source orthogonality, evidence-strength, and companion-skill boundaries unless direct evidence justifies changing them.

## Companion-Skill Boundaries

- `$seq` owns historical session, memory, artifact, workflow, and tool-trace mining.
- `$tune` owns source selection, intended-vs-observed diagnosis, evidence interpretation, gap classification, and `$refine` brief writing.
- `$refine` owns in-place edits once the gap and success criteria are known.
- `$ms` owns new skill creation and direct skill surgery when no usage-backed tuning diagnosis is needed.
- `$ship` and `$land` own PR and merge workflows.
- `$tune` may commit and push validated `apply-with-refine` changes, but it does not create PRs, merge branches, or clean up branches.

If the user asks to discover whether a change is needed, `$tune` owns the turn. If the user provides a complete evidence-backed brief and asks only for edits, hand off to `$refine`. If the user asks for both diagnosis and edits, diagnose first, write the brief, then invoke `$refine` only if the apply gate passes.

## Workflow

### 1. Scope the Tuning Run

Write:

```text
Goal: Tune <skill> so that <intended behavior> better matches <observed or suspected usage pattern>.
Mode: audit-only | proposal-only | apply-with-refine
Evidence source: <source descriptor>
Apply gate: pass | blocked: <reason>
```

### 2. Reconstruct the Intended-Use Contract

Read the target skill before judging usage:

```text
<skill-root>/<skill>/SKILL.md
<skill-root>/<skill>/agents/openai.yaml
<skill-root>/<skill>/scripts/
<skill-root>/<skill>/references/
<skill-root>/<skill>/assets/
```

Only read resources relevant to the target skill or suspected gap.

Summarize primary purpose, triggers, anti-triggers, expected inputs/outputs, required workflow, resources, validation expectations, companion handoffs, and upgrade boundaries.

### 3. Select Evidence Sources

Use `references/evidence-source-model.md` to choose the data source. Declare what source can and cannot prove before drawing conclusions.

For `in-flight`, use current conversation evidence, explicit user feedback, current tool output, validation output, and visible workflow behavior. Summarize; do not include raw transcript unless explicitly allowed and safe.

For `history`, use `$seq` and `references/seq-evidence-playbook.md`. Respect the requested root, time window, session ids, workdir, or arbitrary scope.

For `provided`, inspect only the supplied evidence needed for the claim and record its provenance limits.

For `mixed`, keep separate ledger entries by source kind before synthesizing.

### 4. Mine and Sanitize Evidence

Use the least invasive source that can answer the question. Do not run broad historical mining when current-turn feedback is sufficient for a narrow edit. Do not infer recurrence from in-flight evidence alone.

Sanitize user-facing reports and briefs. Do not include raw transcript text, raw memory text, secrets, credentials, private personal details, sensitive local paths, private path fragments, or unnecessarily long command output.

### 5. Build an Evidence Ledger

For each important source, record:

```text
- Source kind:
- Command, locator, or source:
- Why this source was chosen:
- What it proves:
- What it does not prove:
- Evidence class:
- Confidence: high | medium | low
- Scope/window:
- Recurrence:
- Counterevidence:
- Sanitization note:
```

Do not treat running a command as proof. Explain what the result actually establishes.

### 6. Classify Evidence Strength

Strong evidence:

- `explicit_current_turn_feedback`
- `in_flight_validation_failure`
- `provided_artifact_evidence`
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
- `unbounded_history_without_sampling_plan`

Default thresholds:

- `repeated_session_evidence`: same gap appears in at least 3 relevant historical sessions, or at least 2 independent sessions plus explicit user feedback.
- `repeated_manual_workaround`: substantially similar workaround appears in at least 3 sessions or across at least 2 target skills.
- `low_activation_count`: fewer than 3 relevant activations in the selected history scope.
- `single_ambiguous_session`: one session with unclear intent, incomplete trace, or no explicit outcome signal.
- `clear_routing_failure`: user asked for the skill's owned work and a different skill or no skill handled the core workflow.
- `historical_skill_regression`: behavior changed after a material skill-block, trigger, metadata, or workflow update.

Explicit current-turn feedback can be strong evidence for a narrow local change. It must not justify broad claims about historical recurrence without historical evidence.

### 7. Diagnose the Gap

Classify the mismatch using `references/gap-taxonomy.md`:

- activation,
- interpretation,
- workflow,
- tooling,
- resource,
- validation,
- metadata,
- boundary,
- source-scope.

Identify the smallest sufficient fix. Prefer no edit when evidence is thin, source scope is ambiguous, or the likely change crosses skill boundaries.

### 8. Produce the `$refine` Brief

Use `references/refinement-brief-template.md`. Include source descriptors, the evidence ledger, counterevidence, risk, success criteria, must-not-change constraints, and validation plan.

### 9. Apply with `$refine`, If Allowed

Use `$refine` only after the apply gate passes:

```text
Use `$refine` on <skill> with this tuning brief. Make the smallest sufficient edit that closes the diagnosed <gap_type> gap. Preserve unrelated behavior. Validate with quick_validate. Update agents/openai.yaml only if metadata changed. Add scripts/references/assets only if the brief explicitly justifies them.
```

If the runtime cannot literally invoke another skill, perform the edit by following `$refine` rules and report that the `$refine` phase was executed manually.

### 10. Validate

For any applied edit, run:

```bash
uv run --with pyyaml -- python3 codex/skills/.system/skill-creator/scripts/quick_validate.py <skill-root>/<skill>
```

If shared assumptions or multiple skills changed, run:

```bash
codex/skills/tune/scripts/validate-changed-skills
```

If scripts changed, run at least one representative sample command.

If `codex/skills/.system/skill-creator/scripts/quick_validate.py` is unavailable, report validation as blocked and do not claim validation passed.

### 11. Commit and Push Each Validated Change

When mode is `apply-with-refine` and validation passes, commit and push the scoped files for that atomic change before starting another unrelated change.

Before committing, run `git status --short`, stage only brief-justified files, run `git diff --cached --check`, commit, and push. If any publishing step is blocked, report the blocked step and leave the repository in the safest available state.

### 12. Report

Use this result shape:

```text
Tuned: <skill>

Mode:
- <audit-only | proposal-only | apply-with-refine>

Evidence sources:
- <source descriptor summary>

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

Publishing:
- Commit: <sha | blocked/not run and why>
- Push: <remote/branch result | blocked/not run and why>
- Scoped files: <files staged and committed>

Remaining uncertainty:
- <anything not proven by the evidence>
```

## Upgrade Policy

`tune` may recommend or drive upgrades when the current skill cannot reliably satisfy its intended contract under selected evidence.

Allowed upgrade types: trigger, workflow, capability within existing purpose, tooling, resource, metadata, validation, and handoff/boundary upgrades.

Do not recommend a capability upgrade that changes the skill's core purpose. That should be a new skill or an explicit user-directed redesign.

## Quality Bar

A good `$tune` run:

- Chooses mode before mining evidence.
- Declares evidence sources and keeps data orthogonal to the skill.
- Reads the target skill before judging usage.
- Uses in-flight evidence when the user points to current behavior.
- Uses `$seq` for historical evidence, with explicit scope for arbitrary history.
- Keeps separate ledger entries for mixed sources before synthesizing.
- Separates intended purpose from observed behavior.
- Classifies the gap before proposing a fix.
- Hands `$refine` a precise brief.
- Validates applied changes before commit.
- Commits and pushes each validated atomic `apply-with-refine` change.
- Reports uncertainty when source scope or evidence strength is thin.

A bad `$tune` run:

- Hard-codes `~/.codex/sessions` when the user asked about in-flight behavior.
- Treats in-flight evidence as proof of historical recurrence.
- Treats raw mentions as successful activations.
- Treats "optimize" as permission to edit when the user asked for analysis.
- Rewrites a skill without usage or performance evidence.
- Makes broad changes from one ambiguous source.
- Commits unrelated worktree changes or pushes unvalidated edits.
- Includes raw private transcript text unnecessarily.
