# Authority fanout for invariant-ace

Use authority fanout only for the independently required dimensions selected by
the [entry's escalation conditions](../SKILL.md#authority-fanout-mode), or an
explicit caller requirement. One bounded owner and an inspectable transition set
can be assessed directly without packets; all seven substantive questions and
the Invariant Gate remain required. Do not infer independent review from file
count, report length, or implementation intent alone.

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

Root may downgrade any row. Root may not upgrade a vetoed or unresolved row to
`enforce-now` without fresh evidence clearing the objection, including any
independently required clearance. A root-equivalent packet records direct
assessment; it cannot replace independently required evidence. If a required
worker is unavailable, keep the affected result unresolved and continue permitted
evidence gathering rather than manufacturing independence.

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
