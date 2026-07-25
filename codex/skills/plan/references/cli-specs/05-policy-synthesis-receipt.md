# 05 — Policy Synthesis Receipt / PSR-v1

PSR-v1 is the compact proof that `$plan` ran source-bound synthesis of the complete
architecture-policy candidate to a fixed point.

## Schema

```yaml
policy_synthesis_receipt:
  receipt_version: PSR-v1
  plan_id:
  revision:
  source_digest:
  source_contract:
    kind: direct | PSC-v1 | revision
    source_owner:
    spec_id:
    sgr_digest:
  initial_policy_digest:
  final_policy_digest:
  passes:
    - pass_id:
      lens:
      candidate_digest_before:
      candidate_digest_after:
      findings: []
      material_changes: []
      disposition: changed | clean | blocked | return_to_spec | return_to_grill
  radical_candidate:
    candidate:
    disposition: adopt | reject | defer | return_to_spec | none
    reason:
    affected_refs: []
  convergence:
    complete_clean_sweep:
    independent_press_pass_clean:
    unresolved_errors:
    untreated_material_risks:
    improvements_exhausted:
```

## Candidate binding

Every policy digest in PSR-v1 binds the complete canonical EPG candidate, including:

```text
architectonic seams and authority
selected or evidence-conditioned organizations
factor dispositions
conceptual-compression state
action-to-seam and action-to-factor bindings
architectonic transport and square results
observations, policy, proof, rollback, terminals, and handoff
```

PSR-v1 remains one receipt. No separate architecture receipt or architectonic pass
list is introduced.

## Required properties

```text
receipt_version = PSR-v1
plan_id present
source_digest present
source_contract.kind present
passes non-empty
every pass disposition is a declared PSR-v1 disposition
the final nine passes are the required lenses in order, all clean, with no material changes
each of the final nine passes evaluates the architecture-policy pair
radical_candidate.disposition present
convergence.complete_clean_sweep = true
convergence.independent_press_pass_clean = true
convergence.improvements_exhausted = true
convergence.unresolved_errors empty
convergence.untreated_material_risks empty
```

The final nine identifiers remain:

```text
source_fidelity
semantic_authority
system_regime
belief_and_observation
action_completeness
policy_closure
safety_and_rollback
proof_and_terminal_state
simplicity_and_actuation_readiness
```

The last identifier uses `actuation` in its ordinary sense of putting the plan into
effect. It does not require the `$actuating` skill.

If the plan comes from PSC-v1, `source_contract.source_owner=spec-pipeline` and
`source_contract.spec_id` must be present.

PSR-v1 does not expose private reasoning or draft iteration logs. An architecture
change may delete actions or factors while still constituting an accretive
improvement because justification, observation preservation, and proof strength
increase.

Validate the canonical JSON projection with:

```bash
ledger validate policy-synthesis-receipt \
  --input .ledger/plan/<plan-id>/synthesis-receipt.json
```

The command emits `ledger-validate-decision/v1`, performs no storage mutation, and
grants no execution authority.
