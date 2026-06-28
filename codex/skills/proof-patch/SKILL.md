---
name: proof-patch
description: "Produce a proof-carrying patch or PR handoff bound to current artifact state: goal, changes, validation, anti-gaming checks, review disposition, residual risk, and human review focus."
metadata:
  version: "1.0.0"
  activation_cost: low
  default_depth: standard
---

# Proof Patch

## Mission

Close the loop with a concise proof-bearing artifact.

```text
patch + evidence + review dispositions -> human-reviewable proof
```

This is not a release process. `$ship` still owns stronger publication/release gates. `proof-patch` is the ordinary final fold for goal work and PR handoff.

## Output shape

```markdown
# Proof Patch

## Goal
...

## Changed
...

## Review disposition
| Class | Disposition | Why |
|---|---|---|

## Evidence
| Check | Result | Notes |
|---|---|---|

## Anti-gaming checks
- Tests removed:
- Assertions weakened:
- Checks skipped:
- Coverage reduced:
- Behavior outside goal changed:

## Residual risk
...

## Human review focus
...
```

## Procedure

1. Bind to current branch/head/diff or state that artifact binding is unavailable.
2. Summarize only the changes relevant to the goal.
3. Include evidence commands and results.
4. Include review-fold disposition when review pressure was present.
5. Include anti-gaming checks.
6. Name residual risks and focused human review targets.
7. Hand off to `$ship` only when PR/release/publication gates are required.

## Guardrails

- Do not turn proof into marketing.
- Do not hide failed or unavailable verification.
- Do not claim review closure without review disposition.
- Do not replace `$ship` for release or public-side-effect authority.
