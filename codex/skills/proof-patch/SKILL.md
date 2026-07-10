---
name: proof-patch
description: "Render a concise terminal human proof from a current complete closure-decision/v1 after implementation or review closeout. Use for local or published completion summaries; bind goal, changes, validation, review disposition, anti-gaming checks, residual risk, and human review focus without acting as closure or publication authority."
---

# Proof Patch

## Mission

Render the final human-readable proof after live closure has been derived.

~~~text
current closure-decision/v1
-> patch and evidence summary
-> human review focus
~~~

This skill does not decide completion, select review repairs, count CAS
attempts, or publish.

## Required input

~~~yaml
proof_patch_input:
  closure_decision:
    version: closure-decision/v1
    decision_id:
    run_id:
    evaluated_artifact: {}
    run_digest:
    resolution_digest:
    verdict: complete
    outcomes: {}
    evidence_basis: []
    review_basis: []
    ship_basis: []
    implementation_checkpoint: {} | null
  actuation_run: {}
  review_resolution: {} | null
  evidence_folds: []
  cas_evidence: {} | null
  ship_record: {} | null
  changed_paths: []
  diff_summary:
  validation_results: []
  review_dispositions: []
  residual_risks: []
~~~

Recompute or reject the closure decision if the branch, head, live-state
fingerprint, run digest, or resolution digest no longer matches. Render review
strategy, lenses, dispositions, and semantic balance only from the bound
resolution and evidence objects; basis IDs alone are not enough.
For a bare pipeline, confirm the proof basis covers the retained implementation
prefix and every review-phase material step; do not render a fresh review run
as continuous provenance.

## Output

~~~markdown
# Proof Patch

## Goal
...

## Artifact
- Run:
- Closure decision:
- Branch/head/live state:
- Goal outcome:
- Implementation outcome:
- Next owner:

## Changed
...

## Review resolution
- Review source:
- Resolution digest:
- Strategies:
- Accepted liabilities:
- No-code dispositions:
- Selected lenses:
- Standard CAS record IDs:

## Evidence
| Check | Result | Binding |
|---|---|---|

## Semantic balance
- Live diff and admitted-step provenance:
- Uncovered liabilities:
- Added constructs and replacements:
- Required/completed retirements:
- Dominated constructs remaining:

## Anti-gaming
- Tests deleted:
- Assertions weakened:
- Checks skipped:
- Coverage reduced:
- Outside-goal behavior changed:

## Residual risk
...

## Human review focus
...
~~~

## Procedure

1. Require a current `closure-decision/v1` with `verdict: complete`.
2. Bind every reported claim to the decision's current artifact and basis
   records.
3. Summarize only goal-relevant changes and review dispositions.
4. Include semantic balance and anti-gaming checks.
5. State unavailable checks and residual risk directly.

## Guardrails

- Do not emit final proof before closure.
- Do not accept a replayed or hand-edited closure decision.
- Do not hide failed or unavailable verification.
- Do not treat rejected or proof-only findings as code changes.
- Do not publish, replace `$ship`, or perform public side effects.
