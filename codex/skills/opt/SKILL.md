---
name: opt
description: "Orchestrate Codex skill optimization during active sessions through $cas goal control, $shadow single-session evidence, $tune diagnosis/refinement briefs, and the skill-optimizer custom subagent. Trigger for $opt, skill optimization loops, session-driven skill tuning, meta-skill audits, or explicit validated skill edits. Do not use for general code optimization, product optimization, or performance tuning."
---

# opt (Skill Optimization Controller)

## Overview

Use `$opt` to optimize Codex skills during an active session.

`$opt` is an orchestration wrapper, not the specialist itself:

- `$cas` owns durable parent goal control and app-server/thread lifecycle evidence.
- `$shadow` owns following exactly one watched session through a target-skill lens.
- `$tune` owns intended-vs-observed skill-use diagnosis and refinement briefs.
- `skill-optimizer` owns bounded skill-package audit, proposal, patch, and validation work after the parent has supplied scope.

Core question:

```text
Given the target skill, the selected evidence, and the current session goal,
what is the smallest evidence-backed change or validation step that improves the skill without broadening its trigger surface?
```

## Trigger Cues

Use `$opt` when the user asks to:

- Optimize, tune, tighten, harden, or improve a Codex skill package during a session.
- Coordinate `$cas`, `$shadow`, and `$tune` for a skill-improvement loop.
- Turn a watched-session observation into a skill refinement proposal.
- Use a custom subagent to audit, patch, or validate skill instructions.
- Improve trigger precision, false activation, missed activation, workflow clarity, or validation coverage.
- Run a goal-managed multi-pass skill optimization.
- Apply a validated, explicitly requested skill edit.

Example prompts:

- "Use `$opt` on `$cas`; focus on goal-management ergonomics."
- "Use `$opt` with `$shadow` on session `<id>` and tune the target skill from the evidence."
- "Start a `$cas` goal to optimize `$tune`, then spawn `skill-optimizer` for one bounded audit pass."
- "Use `$opt` to patch `codex/skills/shadow/SKILL.md`; keep edits minimal and validate frontmatter."
- "Use `$opt` regression mode for the false activation we just saw."

## Non-Goals

Do not use `$opt` to:

- Optimize application code, runtime performance, business metrics, or product strategy.
- Replace `$tune` for evidence diagnosis.
- Replace `$shadow` for watched-session monitoring.
- Replace `$cas` for goal lifecycle control.
- Broadly scan all skills without an explicit target or user-authorized goal.
- Edit protected skills merely because the user says "optimize"; require explicit apply language.
- Commit, push, open PRs, merge, or clean up branches unless a separate workflow explicitly asks for that.
- Treat a subagent's `complete_candidate` as final goal completion without parent validation.

## Required Inputs

Identify these before delegating work:

- Target skill name or path.
- Mode: `audit`, `propose`, `tune`, `shadow-diagnose`, `patch`, `validate`, `regression`, or `goal-loop`.
- Evidence source: current turn, provided notes, `$shadow` report, `$tune` brief, validation output, worktree state, or mixed.
- Apply policy: `no_edit`, `propose_patch`, or `edit_allowed`.
- Allowed files and forbidden files.
- Completion evidence: validation command, probe, diff inspection, or explicit reason validation is blocked.
- Whether a parent `$cas` goal should be created, inspected, updated, or left alone.

Default only when unspecified:

- Ambiguous optimization request: `propose` with `no_edit`.
- Current-session failure: `tune` or `propose` with current-turn evidence first.
- Watched session id/path present: `shadow-diagnose` through `$shadow`, then `propose`.
- Explicit "edit", "patch", "apply", "update files", or "make the change": `patch` with `edit_allowed` after the apply gate passes.

## Mode Routing

### Audit

Use when the user asks whether a skill is well-shaped or what is wrong.

Behavior:

1. Reconstruct the target skill's intended-use contract.
2. Spawn `skill-optimizer` in `audit` mode.
3. Require findings only.
4. Do not edit.

### Propose

Use when the user asks what should change, asks for deep analysis, or says "optimize" without explicit file-change language.

Behavior:

1. Gather the minimum evidence needed.
2. Spawn `skill-optimizer` in `propose` mode.
3. Request a refinement plan, success criteria, and validation plan.
4. Do not edit.

### Tune

Use when evidence comes from intended-vs-observed behavior, false activation, missed activation, or workflow drift.

Behavior:

1. Use `$tune` to declare the evidence source and produce or update a refinement brief when useful.
2. Pass the `$tune` brief to `skill-optimizer`.
3. Ask for the smallest skill change or validation surface justified by the brief.
4. Apply only if the user explicitly requested edits and the apply gate passes.

### Shadow Diagnose

Use when the evidence source is one running or completed session.

Behavior:

1. Use `$shadow` on exactly one watched session and one target skill lens.
2. Keep `$shadow` in `observe` or `propose` unless the user explicitly requested apply behavior.
3. Treat the `$shadow` output as evidence; do not inspect raw watched-session JSONL unless separately authorized.
4. Spawn `skill-optimizer` with `mode=shadow-diagnose` to classify the skill implication.
5. Escalate to `$tune` if the watched-session evidence implies a refinement brief.

### Patch

Use only when the user explicitly asks to edit files now.

Apply gate:

- Target skill is identified.
- Allowed files are explicit.
- Existing worktree state is checked before editing.
- Evidence or direct user feedback supports a narrow change.
- Protected-skill restrictions are satisfied.
- Validation path is known or the final report will state why validation is blocked.

Behavior:

1. Spawn `skill-optimizer` in `patch` mode with `apply_policy=edit_allowed`.
2. Keep edits inside the target skill package unless the user authorized companion files.
3. Validate frontmatter, metadata, and any changed scripts.
4. Report changed files and validation proof.

### Validate

Use when the user asks whether a skill edit is safe, complete, or regression-resistant.

Behavior:

1. Run target-specific validators if present.
2. Run `codex/skills/opt/scripts/opt-sanity` when available.
3. Ask `skill-optimizer` for residual risk and missing validation.
4. Do not mark the parent goal complete until validation evidence supports it.

### Regression

Use when the user identifies a concrete prior failure.

Behavior:

1. Name the failure in one sentence.
2. Add or propose a probe that would catch recurrence.
3. Make the smallest skill change that makes the desired behavior explicit.
4. Validate with the probe or explain why it remains manual.

### Goal Loop

Use when the task is long-running or has a clear completion contract.

Behavior:

1. Use `$cas` to create or inspect the parent goal.
2. Keep the goal concrete: target skill, desired behavior, constraints, validation evidence, blocked condition.
3. Delegate one bounded pass to `skill-optimizer`.
4. Validate the subagent report in the parent session.
5. Use `$cas` to continue, pause, block, clear, or complete only after parent-side evidence review.

## Delegation Template

When spawning the subagent, use this shape:

```text
Spawn the custom agent `skill-optimizer` and wait for its result.

Delegation:
- target_skill: <path or skill name>
- mode: <audit|propose|tune|shadow-diagnose|patch|validate|regression>
- current_goal: <CAS parent goal text/id or "none">
- evidence: <current-turn notes | $shadow report | $tune brief | validation output | worktree facts>
- allowed_files: <explicit list/glob>
- forbidden_files: <explicit list/glob>
- validation_commands: <commands or "discover minimally">
- apply_policy: <no_edit|propose_patch|edit_allowed>
- output_required: Target, Mode, Evidence source, Files inspected, Changes made, Evidence/validation, Residual risks, Suggested parent CAS status, Suggested next parent action.

Rules:
- Do not manage the parent goal lifecycle.
- Do not broaden scope beyond the target skill and allowed files.
- Prefer surgical changes.
- If editing, run available validation or explain why validation was not possible.
```

## Parent Completion Check

Before treating the optimization as done, verify:

- Target skill frontmatter remains valid.
- The description is more precise, not merely longer.
- Trigger cues and non-goals are clearer.
- Instructions are operational and mode-routed.
- `$cas`, `$shadow`, `$tune`, `$refine`, and `$ms` boundaries are not blurred.
- Long examples or matrices live in `references/` when they would bloat `SKILL.md`.
- Any new script is deterministic and locally runnable.
- Validation, probe output, or explicit residual risk is reported.
- Parent `$cas` goal state is updated only after evidence supports the update.

## Output to User

Return:

```text
$opt result:
- Target:
- Mode:
- Parent goal status:
- Evidence source:
- What changed or what should change:
- Validation:
- Remaining risk:
- Next recommended action:
```
