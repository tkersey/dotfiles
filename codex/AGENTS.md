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
- This is a root user-facing response rule only: spawned subagents, collaborator threads, and other machine-to-machine handoff turns must not emit `Echo:` or instruction-ack preambles, and should answer the assigned task directly.
- Do not include `Echo:` inside generated files, patches, code blocks, JSON/YAML/TOML intended for machine consumption, email bodies, PR bodies, commit messages, or artifacts the user asked to copy verbatim. Put Echo only in the surrounding chat response.

### Language-surface pass

- Run `$logophile` as a final language-only pass on every non-trivial root response and human-facing artifact. Preserve facts, modality, uncertainty, scope, ownership, sequence, identifiers, code, paths, flags, schemas, protocol literals, and operational decisions; skip terse acknowledgements or status updates and machine-consumed surfaces.

## Actuation boundary

For `$actuating` work, the skill, its canonical live semantics, and its executable gate are authoritative. Do not restate versioned run, admission, review-resolution, or closure protocols here.

Fresh or closure-grade workflow review uses `$cas`. `$ship` alone owns PR creation, update, promotion, and publication.

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

- Treat `.ledger/*` stores as canonical repo-local source evidence. Mutate them only through their owning skills or CLIs; never hand-edit source JSONL.
- Treat memory-source notes as immutable derived admission snapshots, not canonical stores. Phase 2 owns `memory_summary.md`, `MEMORY.md`, and memory-root `skills/*`; do not edit those outputs directly during ordinary work.
- Treat legacy `.learnings.jsonl` as migration input only; never append new rows after migration.
- Failure to create or update a memory-source admission note must not invalidate or roll back a successful canonical source-store write.
