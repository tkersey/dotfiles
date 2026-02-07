---
name: gen-plan
description: Generate iterative `plan-N.md` files in the repo root (max N=5). Use only when asked; clarify before `plan-1.md`; stop at `plan-5.md`.
---

# Gen-Plan

## Contract

- Scope: operate in the repo root only; manage files named `plan-N.md` where `N` is an integer.
- Output location is fixed: write `plan-N.md` to the current repo root directory only.
- Never write `plan.md`, `PLAN.md`, or any non-`plan-N.md` filename.
- Never write outside the repo root. Prohibited examples include `~/Downloads`, `$HOME`, absolute paths, or sibling directories.
- If any instruction or path suggests writing outside the repo root, stop and ask for clarification.
- Define `N` as the maximum numeric suffix among files matching `plan-(\d+).md` (ignore non-matching filenames, including legacy `plan-N-E.md` / `plan-N-R.md`).
- If any matching file has `N > 5`: do nothing; reply exactly: "Plan is ready."
- If `plan-5.md` exists (case-insensitive): do nothing; reply exactly: "Plan is ready."
- If no matching `plan-(\d+).md` exists: run the clarification flow, then create `plan-1.md`.
- Otherwise: create `plan-(N+1).md`. Source plan markdown: `plan-N.md`.
- When loading plan markdown from a source file, insert the full contents of `plan-N.md` at the `<INCLUDE CONTENTS OF PLAN FILE>` placeholder in the plan template.
- Never overwrite an existing target file; stop and report the conflict.
- Ask questions only when unresolved judgment calls block the next iteration.

## Clarification flow (when needed)

- Research first; ask only judgment-call questions.
- Use the `GRILL ME: HUMAN INPUT REQUIRED` block with numbered questions.
- After questions are answered, determined if another round of questions is needed; if so continue asking questions until there are no more then write the next plan file.

## Iterate on the plan

Purpose: Use the prompt below as an internal instruction to produce `plan-(N+1).md` from `plan-N.md`.

Output rules:
- The plan file must contain the response to the prompt, not the prompt itself.
- Do not include the prompt text, blockquote markers, or nested quotes in the plan file.
- The output must be normal Markdown (no leading `>` on every line).
- When inserting the source plan, include it verbatim with no extra quoting, indentation, or code fences.

### Prompt template (verbatim, internal only — never write this into the plan file)

Carefully review this entire plan for me and come up with your best revisions in terms of better architecture, new features, changed features, etc. to make it better, more robust/reliable, more performant, more compelling/useful, etc.

For each proposed change, give me your detailed analysis and rationale/justification for why it would make the project better along with the git-diff style changes relative to the original markdown plan shown below:

<INCLUDE CONTENTS OF PLAN FILE>
