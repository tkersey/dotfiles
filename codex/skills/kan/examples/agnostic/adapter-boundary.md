# Adapter boundary as Ran candidate

Problem: a new service must support old mobile, web, and batch clients.

Kan data:

- `C`: legacy client observation category.
- `D`: new service/domain model.
- `K`: maps legacy observations into the new model boundary.
- `F`: legacy observable behavior.
- Candidate: `Ran_K F`.
- `ε`: projection from the new facade restricted to old observations back to legacy behavior.

Witness object `d`: `AccountSummaryV2`.

Observations:

- mobile needs `displayName` and `balance`;
- web needs `displayName`, `balance`, `riskFlags`;
- batch needs `accountId`, `balance`.

Coherence tests:

```text
mobile.balance(AccountSummaryV2) == batch.balance(AccountSummaryV2)
web.displayName(AccountSummaryV2) == mobile.displayName(AccountSummaryV2)
```

Failure mode: each adapter computes `balance` independently.
