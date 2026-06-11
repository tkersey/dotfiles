# Structural Proof Patterns

When a change alters representation, normalization, construction, elimination, or combination, prefer a matching structural check:

- constructor/eliminator coverage
- round-trip or canonicalization test
- idempotence for migrations/setup/retries
- preservation test for state transitions
- progress test for valid continuations
- identity/associativity checks when combining values
- fixture repair when tests admitted impossible states
- no-code proof when the current owner already enforces the contract
- surface-retirement proof when deletion/collapse/canonicalization is selected

A green unrelated test is not a witness for a structural claim.
