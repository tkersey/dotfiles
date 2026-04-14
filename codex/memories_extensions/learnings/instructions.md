# Learnings memory extension

Use this extension only during memory consolidation.

## What this source is
- This extension represents my evidence-backed learnings store.
- The canonical detailed records come from repo-local `.learnings.jsonl` entries produced by my `learnings` skill.
- Work directly from `.learnings.jsonl` evidence and its existing metadata. Do not assume an extension-local `resources/` digest exists.
- Never edit, append, or rewrite `.learnings.jsonl` from the memory pipeline.

## Goal
Distill learnings into durable Codex memory.

Promote only information that will help future sessions:
- apply my stable defaults without extra steering,
- reuse proven workflows,
- avoid recurring failure modes,
- route quickly to the right repo, task family, or learnings source.

## Promotion rules
Promote a learning into `MEMORY.md` or `memory_summary.md` only when at least one is true:
- the same theme appears repeatedly, especially across 3+ learnings,
- the status is `codify_now`,
- it captures a stable user preference or operating default,
- it contains a reusable failure shield with concrete evidence,
- it would likely save future correction, retries, or search work.

## Status weighting
- `codify_now`: highest priority; likely belongs in durable memory and possibly a skill.
- `avoid_for_now`: strong candidate for a failure-shield note when evidence is concrete.
- `do_more` / `do_less`: good candidates when they recur or clearly express a stable default.
- `investigate_more`: tentative; promote only with reinforcement.
- `review_later`: do not promote on its own.

## Scope rules
- Use `context.repo`, `context.paths`, tags, and related chains to keep repo-specific guidance scoped correctly.
- Promote cross-repo guidance only when it is clearly a stable user preference or a reusable workflow default.
- Respect `supersedes_id` and newer evidence when records conflict.

## Compression rules
- Summarize; do not copy raw JSONL rows or large evidence blobs.
- Preserve only the minimum anchors needed for retrieval: repo slug, path family, exact error string, command, tag, or status when they materially help.
- Convert repeated learnings into concise rules such as: `When X, prefer Y because Z`.
- Keep detailed implementation history in the learnings store, not in Codex memory.

## Artifact targeting
- Put global or cross-task defaults in `memory_summary.md`.
- Put richer operational guidance, reusable procedures, decision triggers, and failure shields in `MEMORY.md`.
- Create or update `skills/*` only when a procedure repeats enough to justify a reusable runbook.

## Routing rule
- Codex memory should answer: what matters, what default applies, what failure to avoid, and where to look next.
- The learnings store should answer: what exactly happened, what evidence proved it, and which repo or path it came from.

## Skill threshold
Create or update a skill only when the learnings show a repeatable procedure that:
- has clear trigger cues,
- has efficient first steps,
- has a proven verification checklist,
- reliably saves time or avoids mistakes.

If the procedure is not yet repeatable, keep it as a concise `MEMORY.md` note instead of a skill.

## Non-goals
Do not use this extension to:
- duplicate the learnings log,
- preserve changelog-style chronology,
- store transient branch or session state,
- store speculative or weakly evidenced lessons,
- scan unrelated repositories just to increase coverage.

If there is no meaningful durable signal, make no memory change.
