---
name: commit
description: Create micro-commits (minimal incision) with at least one validation signal per commit. Use when requests say "split this into micro commits," "stage only the minimal change and commit," "keep commits tiny while checks pass," or when parallel workers/slices need isolated, reviewable commits.
---

# Commit

## Intent
Carve changes into surgical commits: one coherent change, minimal blast radius, and at least one feedback signal before committing.

## When to use
- “Split this into micro commits.”
- “Stage only the minimal change and commit it.”
- “Keep the commits tiny, keep checks passing.”

## Workflow (Surgeon’s principle)

### 1) Scope the incision
- Identify the smallest change that can stand alone.
- Isolate unrelated edits; avoid drive-by refactors/formatting unless required for correctness.

### 2) Stage surgically (non-interactive-first)
Inspect:
- `git status -sb`
- `git diff`

Stage what you intend (prefer file-level staging in non-interactive harnesses):
- `git add <paths...>`
- `git restore --staged <paths...>`

Verify:
- `git diff --cached` matches the intended incision.

If you truly need hunk-level staging but your environment can’t do interactive staging, ask the user to stage hunks locally or provide a patch you can apply.

### 3) Validate the micro scope
- Optional helper: `scripts/micro_scope.py` (staged vs unstaged size).
- If the staged diff is multi-concern, split it before running checks.

### 4) Close the loop (required)
- Select the tightest available signal and run it.
- If the repo’s test/check command is not discoverable, ask for the preferred command.
- Reference: `references/loop-detection.md`.

### 5) Commit
- Use a terse message; optimize for clarity, not poetry.
- Commit only after at least one signal passes.

### 6) Repeat
Repeat until the working tree is clean or the remaining changes are intentionally deferred.

## Guardrails
- Don’t widen scope without asking.
- Prefer the smallest check that meaningfully exercises the change.
- Don’t claim completion without a passing signal.

## Resources
- `scripts/micro_scope.py`
- `references/loop-detection.md`
