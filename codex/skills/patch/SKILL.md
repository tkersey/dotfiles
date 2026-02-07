---
name: patch
description: Create micro-patches from staged git changes (minimal incision) with at least one validation signal per patch. Use when users ask to export/share git patches instead of committing.
---

# Patch

## Intent
Carve changes into surgical git patches: one coherent change, minimal blast radius, and at least one feedback signal before exporting.

## When to use
- "Split this into micro patches."
- "Stage only the minimal change and make a patch file."
- "Keep the patch tiny, keep checks passing."

## Workflow (Surgeon's principle)

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

If you truly need hunk-level staging but your environment can't do interactive staging, ask the user to stage hunks locally or provide a patch you can apply.

### 3) Validate the micro scope
- Optional helper: `scripts/micro_scope.py` (staged vs unstaged size).
- If the staged diff is multi-concern, split it before running checks.

### 4) Close the loop (required)
- Select the tightest available signal and run it.
- If the repo's test/check command is not discoverable, ask for the preferred command.
- Reference: `references/loop-detection.md`.

### 5) Export patch
- Choose an output path, e.g. `patches/0001-<slug>.patch`.
- Export the staged change as a binary-safe patch:
  - `git diff --cached --binary > <patch-path>`
- Verify the patch is non-empty:
  - `test -s <patch-path>`
- Verify applicability:
  - `git apply --check --binary <patch-path>`
- Keep staged changes intact unless the user asks to unstage or reset.

### 6) Repeat
Repeat until the working tree is clean or remaining changes are intentionally deferred.

## Guardrails
- Don't widen scope without asking.
- Prefer the smallest check that meaningfully exercises the change.
- Don't claim completion without a passing signal and a successful `git apply --check`.
- Don't overwrite existing patch files unless the user asks.

## Resources
- `scripts/micro_scope.py`
- `references/loop-detection.md`
