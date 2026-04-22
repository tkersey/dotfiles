# Pre-closure one-change challenge

Use this challenge after the current artifact set appears to be at a material fixed point and before every final closure attempt.

Do not use this challenge as early brainstorming. Do not ask it while material findings, validation gaps, unbounded critical invariants, material foot-guns, or material complexity hazards remain open.

## Exact prompt

> If you could change one thing about this changeset what would you change?

## Purpose

Force one last counterfactual pass that looks for a single clearly dominant improvement which is still worth the churn.

## Decision rules

- Pick at most one candidate change.
- Prefer changes that improve correctness, misuse resistance, invariant clarity, verification strength, or consequential maintainability.
- Do not elevate cosmetic preferences, novelty, or style-only edits.
- If the best remaining change is accretive, route it to `accretive-implementer`.
- If the best remaining change is structural and constraints forbid it, emit `needs-decision` or `blocked`.
- If the best remaining change is real but adjacent to this task's scope, emit `deferred-adjacent` and do not reopen the current task.
- If no change is clearly worth the churn, emit `no-impactful-change`.
- If unchanged-state reuse is valid and the latest challenge already applies to the unchanged artifact state, reuse the latest structured result instead of asking again.

## Structured result

Record the result in the One-Change Challenge Ledger with these fields:

- `question`
- `status`: `not-run` | `run`
- `outcome`: `unknown` | `implemented` | `no-impactful-change` | `needs-decision` | `blocked`
- `acceptance`: `unknown` | `accepted-now` | `deferred-adjacent` | `rejected-scope` | `rejected-nonmaterial`
- `candidate_change`
- `why_this_one`
- `routed_to`
- `evidence`
- `artifact_state_before`
- `artifact_state_after`

For final closure, do not leave `outcome` or `acceptance` as `unknown`. `unknown` is only valid before the challenge is legitimately runnable, such as targeted-validation packets.

## Reopen rule

Any implemented one-change improvement must re-enter the required de novo review loop for the active escalation level before closure.
