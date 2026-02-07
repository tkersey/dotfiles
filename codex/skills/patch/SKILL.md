---
name: patch
description: Create micro-patches from staged git changes (minimal incision) with at least one validation signal per patch. Use when users ask to export/share git patches instead of committing.
---

# Patch

## Intent
Carve changes into surgical git patch files: one coherent change, minimal blast radius, and at least one feedback signal before exporting.

This skill treats a patch as a transport artifact (a context-sensitive diff), not a magical commutative "merge atom". The goal is to make patches
small, reviewable, and maximally likely to apply cleanly.

## Mental model (why this is harder than it looks)
- A git patch file is a *procedure over a base*: it is not commutative, not associative, and not idempotent in general.
- Patch-based VCSes (Darcs/Pijul) work hard to make patch application order-independent; git-style patches don't promise that.
- Therefore: always be explicit about the intended base (usually `HEAD`), keep patches tiny, and validate against a clean base.

## When to use
- "Split this into micro patches."
- "Stage only the minimal change and make a patch file."
- "Keep the patch tiny, keep checks passing."

## Output formats (choose intentionally)
- Default: `git apply`-style patch from the index.
  - Use when you want "here are the staged changes" and the consumer will apply with `git apply`.
- Optional: `git am`/email-style patch (requires commits).
  - Use when the consumer needs commit message/author metadata and will apply with `git am`.
  - This skill prefers the non-commit path unless the user explicitly asks for `format-patch`.

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

Heuristics that reduce downstream conflicts:
- Prefer "one file or one conceptual area" per patch.
- Avoid adjacent edits that increase diff ambiguity (e.g. unrelated edits near each other).
- Avoid formatting-only noise unless required; it increases patch context fragility.

### 4) Close the loop (required)
- Select the tightest available signal and run it.
- If the repo's test/check command is not discoverable, ask for the preferred command.
- Reference: `references/loop-detection.md`.

### 5) Export patch
- Choose an output path, e.g. `patches/0001-<slug>.patch`.
- Before exporting, sanity-check for secrets (tokens, creds, private keys). If likely, stop and ask.

- Export the staged change as a binary-safe patch (deterministic diff output):
  - `git diff --cached --binary --no-ext-diff --no-textconv --no-color > <patch-path>`
- Verify the patch is non-empty:
  - `test -s <patch-path>`

- Verify patch correctness (two levels):
  - Fast local consistency check (works even if the changes are already present in the working tree):
    - `git apply --check --reverse --binary <patch-path>`
  - Strong check against a clean base (recommended when sharing externally):
    - `git worktree add --detach <tmp-dir> HEAD`
    - in `<tmp-dir>`: `git apply --check --binary <patch-path>`
    - `git worktree remove <tmp-dir>`

- Keep staged changes intact unless the user asks to unstage or reset.

### 6) Repeat
Repeat until the working tree is clean or remaining changes are intentionally deferred.

## Guardrails
- Don't widen scope without asking.
- Prefer the smallest check that meaningfully exercises the change.
- Don't claim completion without a passing signal and at least one patch verification step (reverse-check or clean-base check).
- Don't export or share secrets; if in doubt, ask before writing the patch file.
- Don't overwrite existing patch files unless the user asks.

## Notes on patch identity (optional)
- Patch identity matters for deduplication ("have we already applied this logical change?").
- In git ecosystems you can approximate this locally with `git patch-id --stable` (best-effort, not cryptographic).
- Patch identity is a major reason patch-based merge can outperform diff3-style merges; see `references/patch-theory.md`.

## Resources
- `scripts/micro_scope.py`
- `references/loop-detection.md`
- `references/patch-theory.md`
