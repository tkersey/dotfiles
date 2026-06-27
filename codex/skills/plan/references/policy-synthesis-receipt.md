# Policy Synthesis Receipt

PSR-v1 is the compact proof that `$plan` ran source-bound policy synthesis to a
fixed point.

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

## Required properties

```text
receipt_version = PSR-v1
plan_id present
source_digest present
source_contract.kind present
passes non-empty
radical_candidate.disposition present
convergence.complete_clean_sweep = true
convergence.independent_press_pass_clean = true
convergence.improvements_exhausted = true
convergence.unresolved_errors empty
convergence.untreated_material_risks empty
```

If the plan comes from PSC-v1, `source_contract.source_owner=spec-pipeline` and
`source_contract.spec_id` must be present.

PSR-v1 does not expose private reasoning or draft iteration logs.
