# Fixed-Point Driver Integration

Use `negative-ledger` as a routine companion protocol for non-trivial `fixed-point-driver` runs.

For every non-trivial fixed-point run:

1. Establish `artifact_state_id`.
2. Run root-owned negative-ledger query/map during routing preflight.
3. Normalize candidate evidence into a Negative Evidence Ledger.
4. Convert active entries into narrow exclusion rules.
5. Convert stale/reopened entries into proof prompts or reopening tests.
6. Before one-change challenge, check whether the candidate route matches active negative evidence.
7. Before final closure, emit Negative Ledger Handoff.
8. After witnessed failure/no-effect/regression/revert/rejection/pivot, run capture decision.

When consuming RCP/RDP, also consume:

- `negative_evidence.active_exclusions`
- `negative_route_exclusion_cards`
- `negative_evidence.reopened_or_stale`
- `negative_evidence.capture_required`
- `scar_tissue_inventory` for RDP
- route-wave negative evidence status

Reject or reroute if the selected normal form matches an active exclusion that has not been reopened or defeated by current proof.
