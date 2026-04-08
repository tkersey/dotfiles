
# Pre-closure one-change challenge

Use this challenge after the current artifact set appears to be at a material fixed point and before every final closure attempt.

## Exact prompt

> If you could change one thing about this changeset what would you change?

## Purpose

Force one last counterfactual pass that looks for a single clearly dominant improvement which is still worth the churn.

## Decision rules

- Pick at most one candidate change.
- Prefer changes that improve correctness, misuse resistance, invariant clarity, verification strength, or consequential maintainability.
- Do not elevate cosmetic preferences.
- If the best remaining change is accretive, route it to `accretive-implementer`.
- If the best remaining change is structural and constraints forbid it, emit `needs-decision` or `blocked`.
- If no change is clearly worth the churn, emit `no-impactful-change`.

## Reopen rule

Any implemented one-change improvement must re-enter the full de novo review loop before closure.
