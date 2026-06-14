# Fixed-Point Driver Integration

Use `negative-ledger` as a routine companion protocol for non-trivial `fixed-point-driver` runs. The goal is to preserve decision-shaping negative evidence, avoid repeated dead ends, and keep stale failures reopenable when the artifact state changes.

This is stronger than optional trigger-only use: fixed-point-driver should run a root-owned Negative Ledger Pass even when the result is `no-applicable-negative-evidence`.

## Required fixed-point use

For every non-trivial fixed-point run:

1. Establish `artifact_state_id` and `artifact_state_label`.
2. Run a root-owned negative-ledger `query`/`map` pass during routing preflight.
3. Normalize candidate evidence into the Negative Evidence Ledger.
4. Decide applicability: `active`, `stale`, `superseded`, `reopened`, `unknown`, or `need-evidence`.
5. Convert active entries into narrow exclusion rules.
6. Convert stale/reopened entries into explicit proof prompts or reopening tests.
7. After failed/no-effect/regression/revert/rejection/pivot events, run capture decision.
8. Before the one-change challenge, check whether the candidate route matches active negative evidence.
9. Before final closure, emit Negative Ledger Handoff.
10. Carry the Negative Evidence Closure Gate into `verification-closure`.

## Review-compression extension

When consuming `review_compression_packet` or `review_distillation_packet`, fixed-point must also consume:

- `negative_evidence.active_exclusions`
- `negative_evidence.reopened_or_stale`
- `negative_evidence.capture_required`
- `scar_tissue_inventory` for RDP
- route-wave negative evidence status

Reject or reroute if the selected normal form matches an active exclusion that has not been reopened or defeated by current proof.

## When to invoke negative-ledger-mapper

Invoke `negative-ledger-mapper` or `negative_evidence_route_auditor` when at least one is true:

- multiple prior failed attempts may apply;
- evidence is spread across learnings, route waves, RCP/RDP packets, CAS receipts, commits, PR comments, and current ledgers;
- repeated hypotheses or strategy pivots recur across loops;
- stale/superseded evidence may be reopened by current artifact changes;
- one-change challenge risks selecting a previously disconfirmed route;
- Review Distillation Mode has lab scar tissue that must not be transplanted.

## Specialist footer

Every packet must end with the shared specialist packet fields: `artifact_state_id`, `artifact_state_label`, `scope`, `top_material_signals`, `unresolved_signals`, `agreement_pressure`, `stale`, and `final_call`.
