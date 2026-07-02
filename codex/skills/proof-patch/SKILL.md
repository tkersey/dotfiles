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

## Loop governance
- ALSR-v1:
- HYL-v1:
- latest HSR-v1:
- selected loop:
- fused/unfused:
- verifier:
- stop rule:
- terminal fold:
- ATCG-v1:
- residual loop risk:

If ALSR/HYL exists, summarize the current receipts and cite their artifact
binding. If no ALSR/HYL exists because the run is direct-action fused, state
`direct-action fused exemption` and still name the objective, artifact scope,
verifier, stop rule, terminal fold, and side-effect boundary. Do not claim
completion unless ATCG-v1 permits it.

## Review closure
- CAS review source:
- review-fold disposition:
- resolve pass:
- accepted liabilities:
- no-code dispositions:
- clean normalized CAS runs:
- cached CAS receipts counted as fresh: no

## Review disposition
| Class | Disposition | Why |
|---|---|---|

## Parallelism
- mode:
- safe frontier:
- subagents used:
- fan-in reducer:
- accepted/rejected results:
- integration order:
- CAS clean-run reset:

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
3. Surface loop governance from ALSR-v1/HYL-v1/HSR-v1/ATCG-v1 receipts when
   they exist; otherwise state the direct-action fused exemption.
4. Include evidence commands and results.
5. Include review closure and review-fold disposition when review pressure was
   present.
6. Include parallelism state, even when the mode is `none`.
7. Include anti-gaming checks.
8. Name residual risks and focused human review targets.
9. Hand off to `$ship` only when PR/release/publication gates are required.

## Guardrails

- Do not turn proof into marketing.
- Do not hide failed or unavailable verification.
- Do not claim review closure without review disposition.
- Do not count cached CAS receipts as fresh clean CAS runs.
- Do not claim completion unless ATCG-v1 permits it.
- Do not claim completion unless ATCG-v1 returns a completion verdict that
  permits completion.
- Do not replace `$ship` for release or public-side-effect authority.
- Do not publish, update PR state, resolve GitHub threads, or perform delivery
  side effects; `$ship` owns that boundary.
