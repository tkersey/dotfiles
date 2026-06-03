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
| `swarm` | Broad/high-risk/exhaustive request, audit carryover, deletion-sensitive change, or explicit independent coverage | 5+ | `swarm` |

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
- ablation
- other

Avoid launching two specialists for the same uncertainty class unless replacing a
stale, wrong-scope, transport-invalid, or materially incomplete packet.

## Ablation triggers

Launch `ablation_auditor` or emit a root-equivalent ablation packet when:

- implementation would add a helper, flag, branch, adapter, state variant, public
  symbol, compatibility path, fallback, or duplicate truth surface;
- several comments orbit one governing invariant;
- additive scaffolding survived a review loop;
- duplicate truth owners or shadow proof surfaces exist;
- a local patch may be dominated by delete/reuse/collapse/canonicalize;
- a path appears vestigial, subsumed, pass-through, uninhabited, or non-canonical;
- closure would otherwise proceed with `unretired_additive_scaffolds` or
  `duplicate_truth_owners` not equal to zero.


## Isomorphic ablation addendum

Ablation Ledger rows that select deletion, collapse, reuse, canonicalization, privatization, or decommissioning must be paired with an Ablative Isomorphism Card unless routed to `validate-first`. The fixed-point gate fails while selected lower-surface routes have missing behavior-preservation proof.
