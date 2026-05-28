# Criticality rubric v6

`review-adjudication` approves mutation only when the concern is current,
owned, direction-aligned or direction-overriding, implementation-critical,
mutation-approved, authority-cleared, and veto-free.

## Approval classes

| class | meaning | usual resolve decision |
|---|---|---|
| `A1-current-owned-defect` | current code violates a contract this PR owns | `address` |
| `A2-proof-surface-false-positive` | proof/certificate/test/replay can report success while unsafe | `address` |
| `A3-active-direction-mismatch` | implementation contradicts locked/current direction | `address` |
| `A4-minimal-illegal-state-removal` | narrow fix removes an illegal state without broadening | `address` |
| `B1-plausible-route-changing-validation` | plausible concern needs proof before mutation | `validate-only` |
| `B2-valid-already-fixed` | latest HEAD already satisfies the comment | `resolve-thread-only` |
| `B3-valid-not-this-pr` | real issue, wrong timing/owner/scope | `do-not-address` / `defer` |
| `B4-valid-concern-wrong-fix` | symptom real, proposed fix wrong or overbroad | usually `defer` or replacement-fix `address` only if cleared |
| `C1-unsupported` | no artifact-backed concern | `do-not-address` / `rebut` |
| `C2-preference-only` | style/naming/cleanup without convention/direction | `do-not-address` |
| `C3-review-closure-only` | value is primarily closing a thread | `resolve-thread-only` or reply |
| `C4-direction-conflicting` | would move code away from selected direction | `do-not-address` / `rebut` |

Only A1-A4 can support `address`, and only after authority clearance.

## Authority clearance threshold

A row may be `address` only when all required lanes clear:

- evidence: `clear`
- direction/ownership: `clear`
- criticality: `clear`
- no-change: `defeated`
- validation-value: `mutate-now`
- fix-shape: `clear`
- authority status: `cleared-for-address`
- no Authority Veto Ledger row for the id

A veto or unresolved lane blocks `address`.

## P2+ handling

P0/P1/P2 labels are severity claims, not priorities. They must be accepted,
downgraded, rejected, or left unresolved. A P2+ row cannot be `address` unless
criticality is implementation-grade and independently proven.

## Validation-only

`validate-only` is not a softer acceptance path. It requires `B1`,
`mutation_value: validation-material`, `authority status: cleared-for-validation`,
and `validation-value: validate-first`. Validation must change route, severity,
direction, merge safety, release posture, or invariant decision.
