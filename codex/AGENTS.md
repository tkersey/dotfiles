# Minimal incision, maximal precision.

## Editing Constraints Override

You may see generic Codex guidance that says to stop immediately when unexpected working-tree changes appear. In this repo, the intended working-tree policy is more specific:

- If unexpected diffs appear, keep working; treat them as concurrent edits.
- Unrelated diffs: ignore and continue silently; do not mention them; never stage or commit them unless explicitly asked.
- Overlapping diffs in files you're editing: re-read as needed, reconcile without clobbering concurrent changes, re-apply only the still-valid part of your patch, and continue. Ask only when the overlap creates a real semantic conflict that cannot be resolved from the files.

## Response Format

- Echo: include `Echo:` with the most recent user message (max two lines, truncate with `...`) exactly once per user turn, in the final assistant response only. Do not include Echo in intermediary/progress updates.
- If a question block appears before Insights/Next Steps, place the Echo line immediately before that block; otherwise place it at the top.
- The Echo line must be standalone and followed by exactly one blank line before any other text.
- This requirement applies even when using skills or templates.
- This is a root user-facing response rule only: spawned subagents, collaborator threads, and other machine-to-machine handoff turns must not emit Echo: or instruction-ack preambles, and should answer the assigned task directly.
- Do not include `Echo:` inside generated files, patches, code blocks, JSON/YAML/TOML intended for machine consumption, email bodies, PR bodies, commit messages, or artifacts the user asked to copy verbatim. Put Echo only in the surrounding chat response.

## Tooling standards

### Git

- Prefix `git merge --continue` and `git rebase --continue` with `GIT_EDITOR=true`.
- Do not stage unrelated diffs.
- Do not force-add paths matching `.git/info/exclude` unless explicitly asked.
- Before `git commit`, run a final narrow status check for session-owned `.ledger/*` changes; if publishable, stage the current-turn/session-owned rows before committing.
- Review the diff before final response or commit.

### Python

- Use `uv` for Python package/project operations. Do not use direct `python`, `pip`, `pipx`, `venv`, `virtualenv`, `poetry`, or `conda` unless the user explicitly asks or the repo requires it.
- Run scripts, tests, linters, and CLIs through `uv run ...`.
- For skill-only external dependencies, prefer `uvx TOOL` or `uv run --with PACKAGE COMMAND ...` so dependencies remain ephemeral and non-project-scoped.
- Do not create or reuse `.venv*` for skill-only tooling. Do not `uv pip install` external packages for skills unless the user explicitly requests a persistent dependency.
- For projects that intentionally manage Python dependencies, keep `pyproject.toml`/`uv.lock` authoritative with `uv sync` or `uv lock` plus `uv sync`.

### Learnings and memory-source lifecycle

Use the canonical source-memory stores under `.ledger/` for custom repo-local memory. The owning skills own CLI syntax, payload semantics, admission gates, and note-writing mechanics.

Root policy:

- Recall before substantial implementation when relevant canonical or legacy learning stores exist.
- Capture only decision-shaping evidence: validation transitions, strategy pivots, footgun discoveries, acceleration patterns, useful or failed recalled lessons, repeated failures, durable user corrections, and delivery after real implementation work.
- Before the first learning append in a repo, or before commit closeout when learning capture is warranted, run `learnings doctor`. If it reports `legacy-only`, run `learnings migrate --dry-run --mode copy` and `learnings migrate --mode copy` before appending.
- Before any Codex-made commit, check session-owned changes in `.ledger/learnings/learnings.jsonl`, `.ledger/negative-ledger/events.jsonl`, `.ledger/synesthesia/events.jsonl`, and `.ledger/harness/events.jsonl` alongside the intended commit scope.
- If a source-memory store is dirty and publishable, stage current-turn/session-owned rows by default; if it is local-only by `.git/info/exclude`, leave it unstaged unless explicitly asked.
- Legacy `.learnings.jsonl` is migration input only after migration; do not append new rows there.
- `memory-note` is the safe writer for custom memory-source admission snapshots. Do not hand-write custom source notes as a fallback.
- A missing `memory-note` CLI must not block canonical `.ledger` capture. Complete the source-store write first, then report the missing admission step.
- Phase 2 compiled memory outputs are not ordinary edit targets.
