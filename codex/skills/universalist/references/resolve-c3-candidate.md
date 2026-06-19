# C³ Representation/Boundary Candidate

When `$resolve` requests a representation or boundary candidate:

- derive the governing rule from the counterexample basis;
- choose one canonical boundary;
- make invalid states unrepresentable when feasible;
- avoid new public or protocol surface unless required;
- return a disposable candidate patch and semantic-cost vector;
- do not edit delivery.
