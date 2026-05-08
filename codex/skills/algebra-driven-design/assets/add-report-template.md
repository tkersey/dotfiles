# Algebra-Driven Design Report

## 1. Executive summary

- System/problem:
- Main algebraic finding:
- Architecture recommendation:
- Implementation recommendation:
- Highest-risk law/counterexample:
- Immediate next action:

## 2. Domain frame

### Goal

### Scope

### Actors

### External effects

### Irreversible operations

### Observations that matter

## 3. Carriers

| Carrier | Meaning | Valid states | Invalid states | Observed by |
|---|---|---|---|---|

## 4. Operations

| Operation | Signature | Kind | Pure/effectful | Notes |
|---|---|---|---|---|

Operation kinds: constructor, combinator, transformation, observation, command, event, interpreter, validator.

## 5. Observations and equality

| Observation | Carrier | Defines equality? | Notes |
|---|---|---|---|

Distinguish structural equality, semantic equality, trace equality, policy equality, and performance equality.

## 6. Laws, non-laws, and counterexamples

| Candidate law | Formula | Status | Preconditions | Counterexample | Consequence |
|---|---|---|---|---|---|

Status values: LAW, CONDITIONAL, NON-LAW, POLICY LAW, TEST LAW, UNKNOWN.

## 7. Algebraic structures discovered

| Structure | Carrier | Operation(s) | Laws satisfied | Caveats |
|---|---|---|---|---|

Examples: monoid, semilattice, lattice, semiring, reducer, state machine, category, validation algebra.

## 8. Architecture implications

| Law/non-law | Architecture boundary | Runtime mechanism | Why it follows |
|---|---|---|---|

## 9. Proposed architecture

### Components

### Ports/adapters/interpreters

### State and event model

### Policy/approval/guardrail model

### Data consistency model

### Error and compensation model

## 10. Codebase implementation plan

| Carrier/operation/law | Implementation artifact | File/module | Notes |
|---|---|---|---|

### Reference implementation

### Optimized implementation

### Interface/port definitions

### Database/API changes

### Migration sequence

## 11. Test strategy

| Law/invariant | Test type | Generator/fixture | Expected result |
|---|---|---|---|

Test types: example, property, trace, parity, state-machine, scenario, contract, runtime monitor.

## 12. Risks and open questions

| Risk/question | Affected law | Impact | Mitigation/decision needed |
|---|---|---|---|

## 13. Acceptance criteria

- [ ] Carriers are named.
- [ ] Operations have signatures.
- [ ] Observations are explicit.
- [ ] Laws and non-laws are documented.
- [ ] Architecture decisions are tied to laws.
- [ ] Implementation steps are tied to operations and carriers.
- [ ] Tests execute the laws.
- [ ] Runtime guardrails enforce policy laws.
- [ ] Counterexamples are preserved as tests or design constraints.

## 14. Next actions

1.
2.
3.
