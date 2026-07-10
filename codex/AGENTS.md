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

### Language-surface pass

- Treat `$logophile` as implicitly in scope for every non-trivial root user-facing response and every human-facing artifact, even when wording is not the primary task. After the governing workflow fixes the facts and decisions, run `$logophile` as the final language pass on explanations, summaries, plans, review replies, commit and PR text, docs, headings, labels, error messages, handoffs, and closure notes.
- Keep the pass language-only: preserve facts, modality, uncertainty, scope, ownership, sequence, identifiers, code, paths, flags, schemas, protocol literals, and operational decisions. Never rewrite machine-consumed artifacts unless wording or naming on that surface is explicitly requested. Skip only terse acknowledgements or status updates and turns with no human-facing language surface.

## Actuation Governance

For material `$actuating` work, do not operate from a hidden loop.

Before first material mutation, establish a current `actuation-run/v1` with:

~~~text
accepted source and execution authority
current repo/base/branch/head/live-state fingerprint
one lead-selected step
explicit mutation and public-effect boundaries
~~~

If the run is missing, stop with:

~~~text
actuation verdict: blocked-run-missing
~~~

If the run is stale against current repo/base/branch/head/live state, stop with:

~~~text
actuation verdict: blocked-run-stale
~~~

No material mutation is valid without a selected work step.
No selected action is valid without a gate-derived `step-admission/v1` copied
into the step before execution and preserved after completion.
No continuation is valid without an evidence fold.
No completion is valid without a freshly derived `closure-decision/v1`.

Bare `$actuating` execution remains one append-only run across implementation,
`$ship`, and review-closeout. The gate-derived implementation checkpoint binds
the immutable implementation prefix and first SHIP receipt; do not reconstruct
a fresh review run or reset its initial artifact.

Workflow review must use `$cas` when fresh or exhaustive review is required.
Review findings must pass through `$review-fold`, which classifies only, then
through `review-resolution/v1` before implementation. Only a current selected
resolution node may grant review-derived mutation.

Review resolution must account for every touched owner-boundary abstraction and
prefer retirement, collapse, delegation, or replacement over accumulating
comment-shaped helpers. Local repair may not add semantic machinery. Closure
requires three distinct current standard CAS attempts when review closeout is
active; scalar clean counts and opaque proof references are invalid.

Subagents may mutate only one bounded selected node. Read-only scouting,
classification, and proof work may fan out; the lead owns scope, fan-in,
integration, CAS clean-run counting, proof closure, and `$ship` handoff.

`$ship` owns PR creation, update, promotion, and publication.

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
- Whenever `$learnings` is implicitly in scope for recall, capture, commit closeout, PR handoff, or wrap-up, evaluate `$synesthesia` too with `ledger --source synesthesia`; append only when the Synesthesia durable mapping or activation-boundary gate passes. If no durable authority exists but the turn exposes a reusable sensory phrase, activation boundary, or representational ambiguity with an engineering translation, treat it as a non-durable candidate for routing; otherwise keep the no-op internal.
- Keep source-memory bookkeeping out of normal final replies. Do not add trailing `learnings: ...`, `duplicate-skip: ...`, `0 records appended: ...`, `synesthesia: candidate: ...`, or `synesthesia: 0 records appended: ...` report lines just to prove the lifecycle ran. Surface learning/synesthesia outcomes only when they changed repo-visible state, need user action, explain a blocker/error, or the user explicitly asks.
- Recall before substantial implementation when relevant canonical or legacy learning stores exist. Use focused task, failure-surface, tool, path, and error-class terms; pass path hints when known; prefer `--drop-superseded`. Treat recall as input to current artifact inspection, not a replacement for it.
- Treat recalled learnings, prior route failures, memories, and session-derived summaries as candidate precedent, not authority. Before applying them, classify the match as `binding`, `persuasive`, `distinguishable`, `stale`, `superseded`, or `rejected`; apply only when current artifacts support the analogy and the action delta is explicit.
- Capture only decision-shaping evidence: validation transitions, strategy pivots, footgun discoveries, acceleration patterns, useful or failed recalled lessons, repeated failures, durable user corrections, and delivery after real implementation work.
- If a recalled learning looks like failed-hypothesis or route-exclusion evidence, do not block directly from the learning row. Verify current applicability and promote through Negative Ledger (`ledger capture`, then `ledger export`) when it qualifies.
- A precedent with no action delta is background context, not routing authority. A stale or superseded precedent must not block the current route unless it is revalidated against current branch/head/diff and promoted through the owning ledger.
- Before the first learning append in a repo, or before commit closeout when learning capture is warranted, run `ledger doctor --source learnings`. If it reports `legacy-only`, run `ledger migrate --source learnings --dry-run --mode copy` and `ledger migrate --source learnings --mode copy` before appending.
- Before the first Synesthesia append in a repo, run `ledger doctor --source synesthesia`; if it reports `notes-only`, migrate only when an explicit copy import is intended, and never treat ordinary metaphorical prose as a durable event.
- Before any Codex-made commit, check session-owned changes in `.ledger/learnings/events.jsonl`, `.ledger/negative-ledger/events.jsonl`, and `.ledger/synesthesia/events.jsonl` alongside the intended commit scope.
- If a source-memory store is dirty and publishable, stage current-turn/session-owned rows by default; if it is local-only by `.git/info/exclude`, leave it unstaged unless explicitly asked.
- Legacy `.learnings.jsonl` is migration input only after migration; do not append new rows there.
- `memory-note` is the safe writer for custom memory-source admission snapshots. Do not hand-write custom source notes as a fallback.
- A missing `memory-note` CLI must not block canonical `.ledger` capture. Complete the source-store write first, then report the missing admission step.
- Phase 2 compiled memory outputs are not ordinary edit targets.
