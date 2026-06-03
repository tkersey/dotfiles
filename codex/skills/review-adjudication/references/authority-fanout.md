# Authority fanout

Use authority fanout to solve both bandwidth and authority for
`$review-adjudication`. Subagents are not voters. Each lane owns one bounded
clearance dimension. The root adjudicator integrates packets, but cannot
permissively override an unresolved veto into `address`.

## Authority lanes

| role | owns | clearance values |
|---|---|---|
| `evidence-authority` | current grounding, reachability, proof-surface false positives | `clear` / `veto` / `unresolved` / `not-required` |
| `direction-ownership-authority` | same-objective direction, PR ownership, non-goals | `clear` / `veto` / `unresolved` / `not-required` |
| `criticality-authority` | accepted criticality, P2+ severity, review-closure-only downgrades | `clear` / `veto` / `unresolved` / `not-required` |
| `no-change-advocate` | strongest no-change/no-resolve case | `defeated` / `veto` / `unresolved` / `not-required` |
| `validation-value-authority` | mutate now versus validate first versus no validation value | `mutate-now` / `validate-first` / `no-validation-value` / `unresolved` / `not-required` |
| `fix-shape-authority` | minimum safe fix shape and wrong/overbroad fix risk | `clear` / `veto` / `unresolved` / `not-required` |
| `ablative-surface-authority` | deletion/collapse/reuse/privatization/canonicalization before additive mutation | `clear` / `veto` / `unresolved` / `not-required` |

## Trigger policy

Root-equivalent authority packets are allowed for empty live sets, already-fixed
proof-only threads, synthetic triage, or narrow obvious cases with no contested
implementation handoff.

Use full seven-lane fanout, or root-equivalent packets with the same schema, when:

- any P2+ row might be selected as `address`
- every current automated finding would be selected as `address` or `validate-only`
- any current CAS/Codex finding is invariant-framed and would mutate code
- direction comes primarily from `$st`, `.step/proposed-plan.md`, or update-plan
- the no-change countercase is weak, generic, or reviewer-authority-shaped
- validation-only is rejected for an unproven but plausible finding
- implementation would route to `$fixed-point-driver`
- the proposed fix adds a helper, flag, fallback, branch, adapter, state variant,
  public symbol, compatibility path, or duplicate truth surface
- several comments orbit one governing invariant and could be solved by one owner
  correction rather than many local patches

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
  ablative_candidates:
    - id:
      deletion_candidate:
      collapse_candidate:
      reuse_candidate:
      canonical_owner:
      privatization_candidate:
      lower_surface_route: delete | collapse | reuse | canonicalize | privatize | decommission | validate-first | proof-only | none
      additive_mutation_justified: yes | no | unknown
      evidence_ref:
  packet_status_reason:
```

`ablative_candidates` is required for `ablative-surface-authority` and optional
for other roles.

Reject stale, wrong-scope, wrong-objective, wrapper-leaking, acknowledgement-only,
role-exceeding, or no-evidence packets.

## Root authority rule

Root may always downgrade a row to a stricter route. Root may not upgrade a row
to `address` against `veto`, `unresolved`, missing clearance, missing ablative
clearance, or a row in the Authority Veto Ledger. Clear the veto with a fresh
authority packet or block.

## Required output sections

- `Authority Packet Receipts`
- `Authority Clearance Matrix`
- `Authority Veto Ledger`
- `Ablative Counterproposal Ledger`

`address` requires `authority status: cleared-for-address`, all required authority
clearances, an ablative-surface clearance, and no veto row for that id.
