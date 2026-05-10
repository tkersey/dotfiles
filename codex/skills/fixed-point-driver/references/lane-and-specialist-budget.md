# Lane and Specialist Budget

Use lanes to keep fixed-point orchestration calibrated. The goal is to preserve proof-gated closure without turning narrow review-comment fixes into habitual swarms.

## Lanes

| Lane | Trigger | Specialist budget | Default subagent mode |
|---|---|---:|---|
| `direct-closure` | One narrow comment/change, obvious proof lane, no material route uncertainty | 0 | `off` |
| `targeted` | A read-heavy uncertainty could materially change the route | 1-2 | `targeted` |
| `expanded-targeted` | Coupled invariants, multi-surface proof, or two independent uncertainty classes | 3-4 | `targeted` |
| `swarm` | Broad/high-risk/exhaustive request, audit carryover, or explicit independent coverage | 5+ | `swarm` |

The root-owned Negative Ledger Pass is required for non-trivial runs and does not count against the specialist budget. `negative-ledger-mapper` is a specialist and does count.

## Defaulting

- Use `direct-closure` for narrow review-comment remediation unless there is route-changing uncertainty.
- Use `targeted` when one or two read-heavy questions could change the route.
- Use `expanded-targeted` only when the third or fourth specialist covers a distinct uncertainty class.
- Use `swarm` only for broad, high-risk, explicit exhaustive coverage, or audit carryover.

## Uncertainty classes

- evidence
- soundness
- invariant
- hazard
- complexity
- verification
- negative-evidence
- other

Avoid launching two specialists for the same uncertainty class unless replacing a stale, wrong-scope, transport-invalid, or materially incomplete packet.

## Budget exception

Before exceeding budget:

```yaml
budget_exception:
  requested_extra_role: "..."
  current_lane: direct-closure | targeted | expanded-targeted | swarm
  current_specialist_count: 0
  budget_limit: 0
  distinct_uncertainty_class: yes | no
  why_root_cannot_resolve_locally: "..."
  expected_decision_delta: route | finding | proof | risk-retirement | negative-evidence-frontier | none
  approved: yes | no
```

Do not launch the extra specialist when:
- `expected_decision_delta: none`
- `distinct_uncertainty_class: no` and the prior packet is still valid
- the unresolved issue is a root-owned proof command rather than a read-heavy mapping problem

## Lane changes

Record lane changes in the Routing and Budget Ledger:

```yaml
lane_change_history:
  - from: direct-closure
    to: targeted
    reason: "preflight negative-ledger found prior failed route that could change remediation"
```
