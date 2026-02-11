---
name: plan
description: Produce essay-heavy, decision-complete plans in proposed_plan block format. Use when asked to run $plan, turn a project brief into an execution-ready architecture plan, or iteratively refine strategy; optionally export to iterative `plan-N.md` files (max N=5) when explicitly requested outside Plan Mode.
---

# Plan

## Contract

- Single operating model: Plan-Mode-native planning.
- Primary artifact: exactly one `<proposed_plan>` block containing the final plan in normal Markdown.
- Rule of fives: iterate the plan in five refinement rounds maximum.
- Iteration tracking: include `Iteration: N/5` as the first line inside `<proposed_plan>`, where `N` is the current round.
- Iteration source of truth (in order): latest `Iteration: N/5` marker in this planning thread, then explicit user-provided round, else default `N=0`.
- If current `N >= 5`: do nothing; reply exactly: "Plan is ready."
- Plan style: essay-heavy and decision-complete, with concrete choices and rationale.
- Required content in the final plan: title, summary, interfaces/types/APIs impacted, data flow, edge cases/failure modes, tests/acceptance, rollout/monitoring, assumptions/defaults.
- In Plan Mode: do not mutate repo-tracked files.
- Research first; ask questions only for unresolved judgment calls that materially affect the plan.
- Prefer `request_user_input` for decision questions with meaningful multiple-choice options.
- If `request_user_input` is unavailable, ask direct concise questions and continue.

## Clarification flow (when needed)

- Research first; ask only judgment-call questions.
- Prefer `request_user_input` for material tradeoffs; each question must change scope, constraints, or implementation choices.
- After answers are received, determine whether another round of judgment-call questions is required.
- Repeat until no high-impact ambiguity remains, then finalize.

## Iterate on the plan

Purpose: Use the prompt below as an internal instruction to produce the best next essay-heavy plan revision.

Output rules:
- Advance one round per invocation: compute `next_round = N + 1` and output `Iteration: next_round/5`.
- Final output should be the plan content only inside one `<proposed_plan>` block.
- Do not include the prompt text, blockquote markers, or nested quotes in the plan body.
- The plan body must be normal Markdown (no leading `>` on every line).
- When inserting source plan text, include it verbatim with no extra quoting, indentation, or code fences.
- Preserve continuity: each round must incorporate and improve prior-round decisions unless explicitly superseded with rationale.

### Prompt template (verbatim, internal only — never write this into the plan file)

Carefully review this entire plan for me and come up with your best revisions in terms of better architecture, new features, changed features, etc. to make it better, more robust/reliable, more performant, more compelling/useful, etc.

For each proposed change, provide detailed analysis and rationale for why it improves the project. Make the plan decision-complete so an implementer has no unresolved design choices. Include concrete change sketches where useful; git-diff style snippets are optional, not required.

<INCLUDE CONTENTS OF PLAN FILE>

## Optional export to `plan-N.md` (explicit follow-up only)

- Export is secondary and runs only when the user explicitly asks to persist the finalized plan.
- Export must run outside Plan Mode. If currently in Plan Mode, do not write files.
- Export should target the same round index as the current planning iteration when available.
- Scope: operate in the repo root only; manage files named `plan-N.md` where `N` is an integer.
- Output location is fixed: write `plan-N.md` to the current repo root directory only.
- Never write `plan.md`, `PLAN.md`, or any non-`plan-N.md` filename.
- Never write outside the repo root. Prohibited examples include `~/Downloads`, `$HOME`, absolute paths, or sibling directories.
- If any instruction or path suggests writing outside the repo root, stop and ask for clarification.
- Define `N` as the maximum numeric suffix among files matching `plan-(\d+).md` (ignore non-matching filenames, including legacy `plan-N-E.md` / `plan-N-R.md`).
- If any matching file has `N > 5`: do nothing; reply exactly: "Plan is ready."
- If `plan-5.md` exists (case-insensitive): do nothing; reply exactly: "Plan is ready."
- If no matching `plan-(\d+).md` exists: create `plan-1.md`.
- Otherwise: create `plan-(N+1).md`.
- Never overwrite an existing target file; stop and report the conflict.
- Exported file content is plain Markdown plan content (no `<proposed_plan>` tags).
