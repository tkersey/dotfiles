# Lane and Specialist Budget

Use lanes to keep fixed-point orchestration calibrated. The goal is to preserve
proof-gated closure without turning narrow review-comment fixes into habitual
swarms.

## Lanes

| Lane | Trigger | Specialist budget | Default subagent mode |
|---|---|---:|---|
| `direct-closure` | One narrow comment/change, obvious proof lane, no material route uncertainty | 0 | `off` |
| `targeted` | A read-heavy uncertainty could materially change the route | 1-2 | `targeted` |
| `expanded-targeted` | Coupled invariants, multi-surface proof, or two independent uncertainty classes | 3-4 | `targeted` |
| `swarm` | Broad/high-risk/exhaustive request, audit carryover, or explicit independent coverage | 5+ | `swarm` |

The root-owned Negative Ledger Pass is required for non-trivial runs and does not
count against the specialist budget. `negative-ledger-mapper` is a specialist and
does count.

## Uncertainty classes

- evidence
- soundness
- invariant
- hazard
- complexity
- verification
- negative-evidence
- other

Avoid launching two specialists for the same uncertainty class unless replacing a
stale, wrong-scope, transport-invalid, or materially incomplete packet.
