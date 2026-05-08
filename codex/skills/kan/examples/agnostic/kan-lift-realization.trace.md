# Kan lift realization trace

## Problem

A public API contract exists, but the internal service design that realizes it has not been chosen.

## Lift data

- `A`: endpoint requirements.
- `B`: internal service implementation options.
- `C`: observable HTTP/API behavior.
- `P : B -> C`: public projection of an internal implementation.
- `F : A -> C`: desired public API behavior.
- Candidate: `Lft_P F`.
- Comparison: `η : F -> P · Lft_P F`.

## Witness

- `a`: `POST /payments/capture`.
- `F(a)`: idempotent capture with audit event.
- `Lft_P F(a)`: transactional payment module with audit outbox.
- `P(Lft_P F(a))`: public endpoint behavior as exposed through API gateway and event publication.

## Law test

```text
F(a) <= P(Lft_P F(a))
```

Concrete regression:

```text
capture request + retry -> one charge + one durable audit event
```

## Failure mode prevented

The public endpoint is implemented directly in the API layer, bypassing the internal service boundary `P` and producing behavior that cannot be audited or reused.
