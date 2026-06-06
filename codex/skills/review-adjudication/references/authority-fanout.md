# Authority fanout

Use authority fanout to solve both bandwidth and authority for `$review-adjudication`.
Subagents are not voters. Each lane owns one bounded clearance dimension. The
root adjudicator integrates packets, but cannot permissively override an
unresolved veto into `address`.

## Authority lanes

| role | owns | clearance values |
|---|---|---|
| `evidence-authority` | current grounding, reachability, proof-surface false positives | `clear` / `veto` / `unresolved` / `not-required` |
| `direction-ownership-authority` | same-objective direction, PR ownership, non-goals | `clear` / `veto` / `unresolved` / `not-required` |
| `criticality-authority` | accepted criticality, P2+ severity, review-closure-only downgrades | `clear` / `veto` / `unresolved` / `not-required` |
| `no-change-advocate` | strongest no-change/no-resolve case | `defeated` / `veto` / `unresolved` / `not-required` |
| `validation-value-authority` | mutate now versus validate first versus no validation value | `mutate-now` / `validate-first` / `no-validation-value` / `unresolved` / `not-required` |
| `fix-shape-authority` | minimum safe fix shape and wrong/overbroad fix risk | `clear` / `veto` / `unresolved` / `not-required` |
| `ablative-surface-authority` | deletion/collapse/reuse/privatization/decommissioning/canonicalization before additive mutation | `clear` / `veto` / `unresolved` / `not-required` |

## Trigger policy

Root-equivalent authority packets are allowed for empty live sets, already-fixed
proof-only threads, synthetic triage, or narrow obvious cases with no contested
implementation handoff.

Use full seven-lane fanout, or root-equivalent packets with the same schema, when:

- any P2+ row might be selected as `address`;
- every current automated finding would be selected as `address` or `validate-only`;
- any current CAS/Codex finding is invariant-framed and would mutate code;
- direction comes primarily from `$st`, `.step/proposed-plan.md`, or update-plan;
- the no-change countercase is weak, generic, or reviewer-authority-shaped;
- validation-only is rejected for an unproven but plausible finding;
- implementation would route to `$fixed-point-driver`;
- any selected action can add helpers, wrappers, adapters, flags, knobs, state variants, public symbols, fallback paths, branches, or abstractions;
- multiple comments orbit the same governing invariant or duplicate truth surface.

## Packet contract

```yaml
authority_packet:
  role: evidence-authority | direction-ownership-authority | criticality-authority | no-change-advocate | validation-value-authority | fix-shape-authority | ablative-surface-authority
  packet_status: accepted | rejected | root-equivalent
  artifact_state_id: "..."
  direction_state_id: "..."
  scoped_comment_ids: []
  scope_match: yes | no
  artifact_state_match: yes | no
  direction_state_match: yes | no | not-applicable
  clearance_by_id:
    "<id>": clear | veto | unresolved | defeated | mutate-now | validate-first | no-validation-value | not-required
  vetoes:
    - id:
      class:
      claim:
      evidence_ref:
      required_to_clear:
  positive_evidence:
    - id:
      evidence_ref:
      claim:
  packet_status_reason:
```

Reject stale, wrong-scope, wrong-objective, wrapper-leaking, acknowledgement-only,
role-exceeding, or no-evidence packets.

## Root authority rule

Root may always downgrade a row to a stricter route. Root may not upgrade a row
to `address` against `veto`, `unresolved`, missing clearance, a row in the
Authority Veto Ledger, or missing ablative-surface clearance when ablation was
triggered. Clear the veto with a fresh authority packet or block.

## Required output sections

- `Authority Packet Receipts`
- `Authority Clearance Matrix`
- `Authority Veto Ledger`
- `Ablation Activation Receipt`

`address` requires `authority status: cleared-for-address`, all required authority
clearances, no veto row for that id, and ablative-surface clearance when any
mutation-capable route or keep-surface decision exists.
