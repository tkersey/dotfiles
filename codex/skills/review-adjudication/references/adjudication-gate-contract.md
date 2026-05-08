# Adjudication Gate contract

The Adjudication Gate is the automation boundary between review analysis and
implementation. It must be emitted for every real PR review adjudication.

## Required block

```md
## Adjudication Gate

| field | value | basis |
|---|---|---|
| identity_coverage | pass | every raw comment has id/thread, reviewer, location, and claim |
| no_change_coverage | pass | every comment has a countercase and status |
| disposition_coverage | pass | every comment has exactly one allowed disposition |
| proposed_fix_separation | pass | concern validity and proposed-fix validity are separate |
| evidence_coverage | pass | every action has current artifact evidence |
| invariant_pass | pass | invariant clustering checked or named |
| acceptance_skew_audit | pass | disposition distribution audited |
| handoff_allowed | yes | all gate fields pass |
```

## Pass conditions

- `identity_coverage`: every real review comment has stable raw identity.
- `no_change_coverage`: every comment has a strongest no-change countercase and
  one allowed status.
- `disposition_coverage`: every comment has exactly one disposition from the
  allowed set.
- `proposed_fix_separation`: every comment separates concern validity from
  proposed-fix validity.
- `evidence_coverage`: every `act` row has current artifact evidence.
- `invariant_pass`: invariant clustering was performed; shared invariants are
  named, or absence is justified.
- `acceptance_skew_audit`: disposition skew was audited; all-action outputs have
  an All-Action Justification.
- `handoff_allowed`: `yes` only when all preceding fields are `pass`.

## Fail behavior

If any field fails, emit:

```md
handoff_allowed: no
Adjudication Bottom Line: Blocked: incomplete adjudication. Do not implement yet.
```

Do not route to `$accretive-implementer` or `$fixed-point-driver` from an
incomplete adjudication.

## All-action fail-closed rule

If every substantive comment is `act`, the gate may pass only when the output
contains a specific All-Action Justification covering:

- stale/superseded check
- unsupported check
- preference-only check
- out-of-scope check
- misdiagnosis check
- proposed-fix validity check
- validation-only alternative
- shared-invariant check

Generic language like "all comments are valid" is insufficient.

## Checker integration

The optional checker in `tools/review_adjudication_gate.py` validates the
mechanical parts of this contract. It cannot prove semantic correctness, but it
can block incomplete ledgers before implementation routing.
