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

- Treat `$learnings` as implicitly in scope for substantial implementation, fixes, refactors, debugging, tests, validation transitions, commit/PR/handoff closeout, wrap-up, repeated failures, strategy pivots, footgun discoveries, acceleration patterns, and durable user corrections when a canonical or legacy learning store may exist.
- Do not wait for the user to literally say `$learnings` when prior repo-local learning could change route selection, verification order, migration handling, tool choice, or closeout obligations.
- Whenever `$learnings` is implicitly in scope for recall, capture, commit closeout, PR handoff, or wrap-up, evaluate `$synesthesia` too with `ledger --source synesthesia`; append only when the Synesthesia durable mapping or activation-boundary gate passes. If no durable authority exists but the turn exposes a reusable sensory phrase, activation boundary, or representational ambiguity with an engineering translation, emit `synesthesia: candidate: ...`; otherwise report `synesthesia: 0 records appended: <reason>`.
- Recall before substantial implementation when relevant canonical or legacy learning stores exist. Use focused task, failure-surface, tool, path, and error-class terms; pass path hints when known; prefer `--drop-superseded`. Treat recall as input to current artifact inspection, not a replacement for it.
- Capture only decision-shaping evidence: validation transitions, strategy pivots, footgun discoveries, acceleration patterns, useful or failed recalled lessons, repeated failures, durable user corrections, and delivery after real implementation work.
- If a recalled learning looks like failed-hypothesis or route-exclusion evidence, do not block directly from the learning row. Verify current applicability and promote through Negative Ledger (`ledger capture`, then `ledger export`) when it qualifies.
- Before the first learning append in a repo, or before commit closeout when learning capture is warranted, run `ledger doctor --source learnings`. If it reports `legacy-only`, run `ledger migrate --source learnings --dry-run --mode copy` and `ledger migrate --source learnings --mode copy` before appending.
- Before the first Synesthesia append in a repo, run `ledger doctor --source synesthesia`; if it reports `notes-only`, migrate only when an explicit copy import is intended, and never treat ordinary metaphorical prose as a durable event.
- Before any Codex-made commit, check session-owned changes in `.ledger/learnings/events.jsonl`, `.ledger/negative-ledger/events.jsonl`, `.ledger/synesthesia/events.jsonl`, and `.ledger/harness/events.jsonl` alongside the intended commit scope.
- If a source-memory store is dirty and publishable, stage current-turn/session-owned rows by default; if it is local-only by `.git/info/exclude`, leave it unstaged unless explicitly asked.
- Legacy `.learnings.jsonl` is migration input only after migration; do not append new rows there.
- `memory-note` is the safe writer for custom memory-source admission snapshots. Do not hand-write custom source notes as a fallback.
- A missing `memory-note` CLI must not block canonical `.ledger` capture. Complete the source-store write first, then report the missing admission step.
- Phase 2 compiled memory outputs are not ordinary edit targets.

Synesthesia routing:

- Treat `$synesthesia` as implicitly in scope when the user asks what software feels, sounds, looks, moves, weighs, or resembles; asks for compare-by-feel analysis; literal analysis leaves multiple plausible structural, temporal, interaction, or boundary interpretations that a reversible sensory model could distinguish; an owning workflow documents such an ambiguity; or the user asks to reuse, correct, reject, retract, or remember an established sensory mapping.
- Do not wait for the user to literally say `$synesthesia` when a concrete representational ambiguity could change diagnosis, explanation, route selection, or lifecycle obligations. Do not activate it merely because work concerns architecture, performance, readability, maintainability, flaky behavior, onboarding, API/UX quality, refactoring, or a strange bug; those domains keep their technical owners unless the sensory lens itself distinguishes alternatives.
- Start from literal evidence, separate observations from hypotheses, choose the minimum sufficient modality, and translate every material sensory statement into concrete engineering meaning with uncertainty, a falsifier, and a next move.
- Whenever `$synesthesia` is evaluated from the `$learnings` lifecycle, source-memory closeout, or a durable mapping/boundary request, run the candidate pass: append a durable row when explicit or repeated accepted authority exists; emit `synesthesia: candidate: ...` when a reusable sensory phrase, activation boundary, or representational ambiguity has a concrete engineering translation but lacks authority; otherwise report `synesthesia: 0 records appended: <specific reason>`.
- Before the first Synesthesia append in a repo, run `ledger doctor --source synesthesia`; if it reports `notes-only`, migrate only when an explicit copy import is intended. Do not treat `notes-only` as the substantive reason for zero capture, and do not infer durable authority from assistant-authored novelty or ordinary metaphorical prose.
- For an explicit durable mapping or boundary, append the canonical `.ledger/synesthesia/events.jsonl` row first with `ledger capture --source synesthesia --kind <kind> --json -`; when global admission is warranted, hand off to `$memory-source-notes` in the same turn.
- The generated current-state digest refreshes automatically after a successful append; digest failure does not roll back the canonical row.
