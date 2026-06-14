# Review Resolution Integration

Use `$negative-ledger` as the memory of falsified review-resolution decisions.

A repeated review decision is not just a repeated decision. It is a falsified hypothesis.

## Trigger

Run negative-ledger query/map when:

- same cluster reappears after repair;
- selected normal form was falsified;
- `universalist_check.decision: not-needed` was falsified;
- add-surface route failed or became unsound;
- public bypass, compatibility path, fallback, parser tolerance, or proof matrix choice caused a CAS counterexample;
- Review Distillation Mode is active;
- one-change candidate resembles prior failed route.

## Closure rule

No selected normal form may violate active negative evidence unless the evidence is reopened, proven stale/superseded, or explicitly accepted as risk.
