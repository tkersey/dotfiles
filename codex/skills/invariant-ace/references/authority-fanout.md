# Authority fanout for invariant-ace

Use authority fanout when an invariant result can drive implementation, review adjudication, closure, or fixed-point routing.

## Roles

| Agent | Authority dimension | Blocks `enforce-now` when |
|---|---|---|
| `inv-counterexample-authority` | Concrete bad trace and reachability | trace missing, ungrounded, stale, or non-current |
| `inv-owner-scope-authority` | State owner, scope, source of truth, direction fit | owner/scope/source of truth is unknown or wrong |
| `inv-induction-authority` | Allowed transitions and preservation | transition set incomplete or predicate not inductive |
| `inv-boundary-authority` | Enforcement boundary and minimum cut | boundary is duplicate, too local, too broad, or wrong phase |
| `inv-witness-parity-authority` | Identity/witness/fixture parity | validation/generation/projection/certificate semantics drift |
| `inv-verification-authority` | Proof signal tied to predicate | verification does not falsify predicate/enforcement |
| `inv-skeptic-authority` | Strongest no-invariant/no-enforce case | a non-enforcement route remains stronger |

## Root authority

Root may downgrade any row. Root may not upgrade a vetoed or unresolved row to `enforce-now` without clearing the veto through a fresh authority packet or same-schema root-equivalent packet.

## Packet requirements

Each packet must include:

```yaml
authority_packet:
  role:
  packet_id:
  artifact_state_id:
  scoped_candidate_ids:
  artifact_state_match: yes|no
  scope_match: yes|no
  clearance_by_id:
    inv1: clear|veto|unresolved|not-needed|not-in-scope
  vetoes:
    - id:
      class:
      claim:
      evidence_ref:
      required_to_clear:
  positive_evidence:
    - id:
      claim:
      evidence_ref:
  packet_status: accepted|rejected|root-equivalent
```

Reject stale, wrong-scope, generic, wrapper-leaking, acknowledgement-only, or no-evidence packets.
