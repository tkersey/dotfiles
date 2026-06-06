# Lane and Specialist Budget

Use lanes to keep fixed-point orchestration calibrated. The goal is to preserve
proof-gated closure without turning narrow review-comment fixes into habitual
swarms.

## Lanes

| Lane | Trigger | Specialist budget | Default subagent mode |
|---|---|---:|---|
| `direct-closure` | One narrow comment/change, obvious proof lane, no material route or ablation uncertainty | 0 | `off` |
| `targeted` | A read-heavy uncertainty could materially change the route | 1-2 | `targeted` |
| `expanded-targeted` | Coupled invariants, multi-surface proof, ablation risk, or two independent uncertainty classes | 3-4 | `targeted` |
| `swarm` | Broad/high-risk/exhaustive request, audit carryover, P2+ review pressure, or explicit independent coverage | 5+ | `swarm` |

The root-owned Negative Ledger Pass is required for non-trivial runs and does not
count against the specialist budget. `negative-ledger-mapper` and `ablation_auditor`
are specialists and do count unless the run explicitly requires them.

## Uncertainty classes

- evidence
- soundness
- invariant
- hazard
- complexity
- verification
- negative-evidence
- ablation
- ablation-activation
- isomorphism
- clone-classification
- abstraction-ladder
- other

Avoid launching two specialists for the same uncertainty class unless replacing a
stale, wrong-scope, transport-invalid, or materially incomplete packet.

## Ablation lane triggers

Launch `ablation_activation_sentinel` when ablation activation is ambiguous or root-equivalent. Launch `ablation_auditor` or emit a root-equivalent Ablation Packet when activation is `required`:

- selected work can add helpers, wrappers, adapters, flags, knobs, state variants, public symbols, branches, or abstractions;
- a patch preserves dominated, subsumed, vestigial, pass-through, duplicate, non-canonical, or temporary-scaffold surface;
- review/fix loops are producing local patch pileup;
- the one-change challenge could be answered by deletion, collapse, privatization, decommissioning, or canonicalization;
- closure would otherwise keep additive scaffolding because it helped pass an intermediate review loop.
