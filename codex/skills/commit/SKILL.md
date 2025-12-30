---
name: commit
description: Create micro commits using the surgeon's principle (minimal incision, maximal precision) with git commands only. Use when Codex needs to split changes into surgical commits, stage hunks precisely, or keep commits small while ensuring at least one feedback loop passes before each commit.
---

# Commit

## Overview
Create surgical, micro commits that capture one precise change and pass at least one tight feedback loop before committing.

## Trigger Examples
- "Split this change into micro commits."
- "Make a surgical commit for this fix."
- "Stage only the minimal hunk and commit it."
- "Keep the commit tiny, tests passing."
- "Carve this diff into separate micro commits."
- "I want a minimal, precise commit here."

## Workflow (Surgeon's Principle)

### 1) Scope the incision
- Identify the smallest coherent change that can stand alone.
- Isolate unrelated edits (use patch staging or stash them).
- Avoid refactors, formatting, or drive-by edits unless they are required for correctness.

### 2) Stage surgically (git only)
- Inspect: `git status -sb`, `git diff`, `git diff --stat`.
- Stage by hunk: `git add -p`.
- Undo accidental staging: `git reset -p`.
- Discard accidental edits: `git restore -p`.
- Verify: `git diff --cached` is exactly the intended incision.

### 3) Validate the micro scope
- Optional helper: run `scripts/micro_scope.py` to summarize staged vs unstaged size.
- If the staged diff feels multi-concern, split it before any checks.

### 4) Close the loop (required)
- Discover the tightest available signal from the codebase.
- Run at least one check that exercises the change.
- If nothing is discoverable, ask the user for the preferred command.
- Reference: `references/loop-detection.md`.

### 5) Commit (message is irrelevant)
- Use a minimal message: `git commit -m "micro"`.
- Only commit after the loop passes.

### 6) Repeat or clean up
- If more changes remain, repeat from step 1.
- Keep each commit single-purpose and minimal.

## JJ Compatibility (Git Mode)
- Use plain git commands only; avoid jj commands.
- Avoid history-rewriting commands (`git rebase`, `git reset --hard`, `git filter-branch`) unless the user explicitly asks.

## Guardrails
- If staging cannot isolate the change cleanly, ask before widening scope.
- Prefer small, targeted checks over full test suites when appropriate.
- Do not claim completion without a passing signal.

## Resources
- `scripts/micro_scope.py` - summarize staged vs unstaged diff size and scope.
- `references/loop-detection.md` - heuristics to select a tight feedback loop.
