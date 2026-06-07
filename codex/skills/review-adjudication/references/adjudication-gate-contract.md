# Adjudication Gate Contract v9

The gate is the automation boundary between review analysis and downstream
mutation, validation, thread resolution, or reply/defer work.

```md
## Adjudication Gate

| field | value | basis |
|---|---|---|
| claim_kernel_complete | pass/fail | every raw claim appears exactly once in the Claim Decision Kernel |
| artifact_state_bound | pass/fail | Review Basis records artifact_state_id or names unavailable fields |
| warrant_coverage | pass/fail | every kernel row has exactly one matching Resolution Warrant |
| route_annexes_complete | pass/fail/not-required | mutation/delete routes have required annexes |
| surface_budget_coverage | pass/fail/not-applicable | mutation warrants have Surface Budget Ledger rows |
| fixed_point_handoff_complete | pass/fail/not-applicable | fixed-point handoff requests budget preflight/delta/closure receipts |
| handoff_agenda_consistency | pass/fail | Handoff Agenda ids match routes and warrants |
| adjudication_complete | pass/fail | all required fields pass |
| implementation_handoff_allowed | yes/no | yes only for active mutate-code warrants with required annexes/budgets |
| validation_handoff_allowed | yes/no | yes only for add-validation-only warrants |
| reply_handoff_allowed | yes/no | yes only for resolve-thread/draft-reply/defer warrants |
```

If any required field fails, emit:

```md
Adjudication Bottom Line: Blocked: incomplete adjudication. Do not implement yet.
```
