# Codex custom agents for review-adjudication

This package includes runnable Codex custom agents for the `$review-adjudication`
authority panel. The authority panel is designed to solve both bandwidth and
authority: lanes can run in parallel, but each lane owns only one clearance
dimension.

## Install locations

In this dotfiles repo, `codex/agents` is linked into `$HOME/.codex/agents`.
Codex custom agents are discovered from project `.codex/agents/*.toml` or user
`$HOME/.codex/agents/*.toml`.

This drop-in includes / expects:

- `codex/agents/review-evidence-authority.toml`
- `codex/agents/review-direction-ownership-authority.toml`
- `codex/agents/review-criticality-authority.toml`
- `codex/agents/review-no-change-advocate.toml`
- `codex/agents/review-validation-value-authority.toml`
- `codex/agents/review-fix-shape-authority.toml`
- `codex/agents/review-ablative-surface-authority.toml`
- `codex/agents/ablation-activation-sentinel.toml`

## Authority agents

| Authority lane | Codex custom agent | Blocks `address` when |
|---|---|---|
| evidence-authority | `review_evidence_authority` | ungrounded, unreachable, stale, already fixed, or unresolved artifact proof |
| direction-ownership-authority | `review_direction_ownership_authority` | wrong-owner, out-of-scope, direction-conflicting, wrong-objective, or unresolved direction |
| criticality-authority | `review_criticality_authority` | severity downgraded/rejected/unresolved, review-closure-only, low-value, or out-of-lane |
| no-change-advocate | `review_no_change_advocate` | no-change/proof-only/defer route remains stronger than mutation |
| validation-value-authority | `review_validation_value_authority` | validation should precede mutation or validation has no material decision value |
| fix-shape-authority | `review_fix_shape_authority` | wrong fix, overbroad fix, under-specified cut, hidden invariant, or missing lower-surface clearance |
| ablative-surface-authority | `review_ablative_surface_authority` | additive mutation is dominated by deletion, collapse, reuse, privatization, decommissioning, canonicalization, or validate-first |
| ablation-activation-sentinel | `ablation_activation_sentinel` | activation is missing, not-required is unsupported, or root-equivalent work would otherwise omit a receipt |

## Parent orchestration rule

Launch all required authority agents before waiting. Keep them read-only. Assign
the same `artifact_state_id`, `direction_state_id`, and exact scoped comment ids.
Require the Authority Packet shape in `references/authority-fanout.md` and use `ablation_activation_sentinel` when activation is ambiguous or root-equivalent.

The parent/root adjudicator may always downgrade a row to a stricter route. It
may not upgrade a row to `address` against a veto, unresolved clearance, missing
authority packet, stale packet, or missing ablation activation receipt.

## Fallback

If the custom agents are unavailable, emit root-equivalent Authority Packets with
the same role names and schema. Root-equivalent packets must be evidence-bearing
and are not a license to skip the clearance matrix, veto ledger, or ablation
activation receipt.
