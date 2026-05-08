# ADD Codebase Implementation Plan

## Target system

## Current implementation summary

## Desired algebra

### Carriers

| Carrier | Current representation | Target representation | Notes |
|---|---|---|---|

### Operations

| Operation | Current location | Target signature | Pure/effectful | Notes |
|---|---|---|---|---|

### Observations

| Observation | Current source | Target function/view | Notes |
|---|---|---|---|

## Laws and tests

| Law | Formula | Test type | Implementation mechanism |
|---|---|---|---|

## Reference implementation

Purpose:

Files/modules:

Semantics:

## Optimized implementation

Purpose:

Files/modules:

Parity test against reference:

## Interfaces and interpreters

| Port/interface | Abstract operation | Test interpreter | Production interpreter |
|---|---|---|---|

## Database/API changes

| Change | Law supported | Migration risk |
|---|---|---|

## Refactor sequence

1. Extract carriers.
2. Extract observations.
3. Extract pure operations.
4. Add reference implementation.
5. Add law tests.
6. Add interpreters/ports.
7. Implement optimized version.
8. Add runtime guards.
9. Migrate callers.
10. Monitor law violations.

## Risks and counterexamples

| Counterexample | Failed law | Design response |
|---|---|---|

## Acceptance criteria

- [ ] New code exposes domain carriers.
- [ ] Operations have explicit signatures.
- [ ] Observations are encoded.
- [ ] Law tests are passing.
- [ ] Optimized code matches reference behavior.
- [ ] Effects are behind interpreters.
- [ ] Runtime constraints enforce critical laws.
