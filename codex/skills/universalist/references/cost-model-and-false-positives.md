# Cost model and false positives

Prefer a stronger construction only when it buys concrete safety.

False positives:

- a one-off boolean does not justify a coproduct;
- a predicate used twice may not justify a refined type if it is not stable;
- a callback is fine if it does not cross a meaningful boundary;
- an adapter is enough when no universal boundary artifact changes code shape;
- a Freyd/AFT diagnostic is overkill if `P` is already a simple local projection and no canonical implementation builder is needed.

Escalation is justified when it prevents drift, duplicated interpretation, impossible states, lossy projections, hidden obligations, or untestable behavior.
