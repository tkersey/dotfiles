# Contract-first Kan lift trace

## Problem

Refactor a payment service from direct CRUD handlers into a workflow architecture without changing externally visible behavior.

## Lift data

- `A`: public contract cases: authorize, capture, refund.
- `B`: internal implementation plans: handlers, workflows, repositories, idempotency store, audit sink.
- `C`: observable behavior: response fields, status codes, audit events, idempotency outcomes.
- `P : B -> C`: run internal workflow and observe public response plus emitted events.
- `F : A -> C`: existing contract/golden behavior.

## Candidate

Use `Lft_P F` for the implementation realizer and `Rft_P F` for residual obligations before editing.

## Witness

`refund` endpoint.

Required observations:

- returns success response;
- emits `Refunded` audit event;
- rejects refund after settlement;
- repeated request with same idempotency key returns same result.

## Obligation ledger

| Observation | Required | Current projection | Missing B artifact | Repair |
|---|---|---|---|---|
| audit event | `Refunded` | absent | audit sink call | add workflow audit step |
| idempotency | second call same result | absent | idempotency key store | add idempotency repository |
| settlement rejection | reject after settlement | absent | payment state machine | add `Settled -> RefundRejected` branch |

## Defunctionalized IR

- `PublicObservation`: status, response field, audit event, idempotency result.
- `CandidateRealizer`: workflow step, repository change, external gateway capability.
- `ProjectionPath`: controller response, audit trace, persistence view.
- `ImplementationObligation`: needed data, transition, capability, projection path.

## Law test

```text
for obs in refund_observations:
  observe(P(realize(refund)), obs) == observe(F(refund), obs)
```

## No-exact-lift rule

If the public observation requires data not present in the internal model and not derivable from event history, do not invent it. Emit a no-exact-lift report with repair options.
