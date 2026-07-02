# Example: payment lifecycle

## Carriers

```text
PaymentState
PaymentCommand
PaymentEvent
PaymentTrace
Money
IdempotencyKey
```

## Operations

```text
authorize : PaymentDraft × AuthorizationCommand -> Effect[PaymentEvent]
capture   : AuthorizedPayment × CaptureCommand -> Effect[PaymentEvent]
void      : AuthorizedPayment × VoidCommand -> Effect[PaymentEvent]
refund    : CapturedPayment × RefundCommand -> Effect[PaymentEvent]
apply     : PaymentState × PaymentEvent -> PaymentState
observe   : PaymentState -> PaymentView
```

## Laws

```text
fold(s, []) = s
fold(s, xs ++ ys) = fold(fold(s,xs), ys)
capture(commandId, authorizedPayment) repeated = one capture effect
```

## Non-law

```text
refund(capture(p)) = p
```

This is false under audit/provider/settlement observations. Refund is compensation under a narrower money-balance observation, not inverse under full trace observation.

## Architecture implications

- use state variants, not loose booleans;
- external provider is an effect boundary/interpreter;
- event reducer is pure;
- transition and duplicate-command laws need tests;
- Freyd-category or effect-handler mechanics may be relevant because order and effects are observable.
