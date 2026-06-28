# Example Invocations

## Compact root-equivalent adjudication

```md
Use $review-adjudication in Kernelized Surface-Budgeted v9 mode.

Goal: decide which current PR review findings may affect downstream work.

Rules:
- emit Claim Decision Kernel and Resolution Warrants even if using root-equivalent reasoning
- bind the output to artifact_state_id
- do not allow implementation without a mutate-code warrant
- if any route can mutate, include Surface Budget Ledger and bounded mutation receipts
```

## Least-surface implementation handoff

```md
Use $review-adjudication for this review batch, then hand off only licensed
mutation warrants to the owning implementation workflow.

Bias:
- prefer delete/collapse/canonicalize/reuse before additive mutation
- require surface budgets for every mutate-code warrant
- request Surface Budget Preflight and Surface Delta Receipts in the Handoff Agenda
```

## Proof-only cleanup

```md
Use $review-adjudication to separate already-fixed review threads from code work.
Use resolve-thread-only only when current proof makes mutation unnecessary.
Do not route proof-only rows to implementation.
```
