# Invariant Gate contract

The Invariant Gate is the boundary between invariant analysis and implementation, validation, proof-only closure, or no-change.

## Required sections

`Review Basis`, `Candidate Invariant Inventory`, `Counterexample Ledger`, `Invariant Ledger`, `Owner and Scope Ledger`, `Transition / Induction Matrix`, `Enforcement Boundary Decision`, `Policy / Exception Ledger`, `Witness and Fixture Parity Ledger`, `Verification Plan`, `Authority Packet Receipts`, `Authority Clearance Matrix`, `Authority Veto Ledger`, `Accepted Invariants`, `Validate Only`, `Proof Only`, `Defer / No Change`, `Change Agenda`, `Acceptance Skew Audit`, `Invariant Gate`, and `Ace Bottom Line`.

## Pass rule

`enforce-now` is legal only when:

- the invariant is `accepted`;
- owner, scope, holds-when, source of truth, boundary, verification, and evidence refs are concrete;
- counterexample, owner/scope, induction, boundary, witness/parity, and verification clearances are `clear`;
- skeptic is `defeated`;
- authority status is `cleared-for-enforcement`;
- no veto ledger row remains for that ID;
- the Change Agenda mirrors the route exactly;
- the Invariant Gate passes.

`validate-only`, `proof-only`, `defer`, `no-change`, and `blocked` are not implementation permission.
