---
name: gen-plan
description: Generate iterative `plan-N-E.md` / `plan-N-R.md` files in the repo root (max N=5, E then R). Use only when asked; clarify before `plan-1-E.md`; stop at `plan-5-R.md`.
---

# Gen-Plan

## Contract

- Scope: operate in the repo root; manage files named `plan-N-E.md` and `plan-N-R.md` where `N` is an integer and phase is `E` (enhance) or `R` (revise).
- `E` and `R` files use the same template; the phase exists to support separate passes (e.g., different models).
- Phases are case-insensitive (`-e`/`-r`), but write new files using uppercase `-E` / `-R`.
- Define `N` as the maximum numeric suffix among files matching `plan-(\d+)-[EeRr].md` (ignore non-matching filenames, including legacy `plan-N.md`).
- If any matching file has `N > 5`: do nothing; reply exactly: "Plan is ready."
- If `plan-5-R.md` exists (case-insensitive): do nothing; reply exactly: "Plan is ready."
- If no matching `plan-(\d+)-[EeRr].md` exists: run the clarification flow (same question style as `codex/skills/plan/SKILL.md`), then create `plan-1-E.md`.
- Otherwise:
  - If `plan-N-E.md` exists and `plan-N-R.md` does not: create `plan-N-R.md`. Source plan markdown: `plan-N-E.md`.
  - Else (if `plan-N-R.md` exists, regardless of whether `plan-N-E.md` exists): create `plan-(N+1)-E.md`. Source plan markdown: `plan-N-R.md`.
- When loading plan markdown from a source file, extract only the plan markdown section: everything after the `Plan markdown` line and before the closing `---` delimiter.
- Never overwrite an existing target file; stop and report the conflict.
- Ask questions only when unresolved judgment calls block the next iteration.

## Clarification flow (when needed)

Follow the same clarification protocol and formatting as `codex/skills/plan/SKILL.md`:

- Research first; ask only judgment-call questions.
- Use the `CLARIFICATION EXPERT: HUMAN INPUT REQUIRED` block with numbered questions.
- After questions are answered, determined if another round of questions is needed; if so continue asking questions until there are no more then write the next plan file.

## Iterate on the plan

Use the following to generate a plan

```md
---
Carefully review this entire plan for me and come up with your best revisions in terms of better architecture, new features, changed features, etc. to make it better, more robust/reliable, more performant, more compelling/useful, etc.

For each proposed change, give me your detailed analysis and rationale/justification for why it would make the project better along with the git-diff style changes relative to the original markdown plan shown below:

<INCLUDE CONTENTS OF PLAN FILE>
---
```
