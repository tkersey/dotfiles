# Ideate Result Receipt (IDR-v1)

`IDR-v1` is a compact, auditable receipt that proves whether `$ideate` actually performed the important gates. It is not an implementation artifact and does not expose private reasoning.

## Schema

```yaml
ideate_result:
  receipt_version: IDR-v1
  mode: fast | standard | deep | audit-only
  terminal_state: portfolio_ready | evidence_too_thin | blocked_for_user_input | no_breakthrough_found
  scope: "..."
  evidence_sources_count: 0
  baseline_candidates_generated: 0
  candidates_shortlisted: 0
  glaze_gate:
    applied: yes | no
    material_delta_count: 0
  asi_gate:
    applied: yes | no
    cash_out_count: 0
  overlap_check:
    performed: yes | no
  chosen_direction: "..."
  seed_emitted: yes | no
  assumptions: []
  remaining_uncertainty: []
```

## Terminal states

- `portfolio_ready` — a ranked portfolio and seed were justified.
- `evidence_too_thin` — evidence did not support a credible portfolio.
- `blocked_for_user_input` — a material judgment is required.
- `no_breakthrough_found` — useful ideas may exist, but none passed both escalation gates.

## Receipt semantics

- `portfolio_ready` requires evidence, candidates, Glaze, ASI, overlap check, chosen direction, and seed.
- `evidence_too_thin` should not emit a seed by default.
- `no_breakthrough_found` may emit a non-breakthrough portfolio but should not claim a breakthrough.
- `audit-only` may skip Glaze/ASI if it is only reporting signals.
