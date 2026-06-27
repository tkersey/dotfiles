# Spec 01 — RAC-v1 and `resolve-c3 authority-chain`

Order: 1 of 4.

## Purpose

Make review-originated mutation authority mechanically inspectable.

Raw review text cannot authorize mutation. A review finding must be compiled into
`resolve_authority_chain / RAC-v1` before any mutation gate can pass.

## Native CLI surface

```bash
resolve-c3 authority-chain init \
  --campaign <campaign-id> \
  --artifact-state <artifact-state.json> \
  --review-claim <claim.json> \
  --acceptance <ac-v2.json> \
  --cex <cex-v1.json> \
  --batch <rb-v1.json> \
  --basis <ceb-v2.json> \
  --kernel <mbk-v1.json> \
  --reduction <rc-v1.json> \
  --proof-obligation <proof-ref> \
  --realization-target <target.json> \
  --output rac.yaml

resolve-c3 authority-chain check \
  --chain rac.yaml \
  --format text|json
```

Reference compatibility script:

```bash
python3 codex/skills/resolve/tools/resolve_authority_chain_gate.py rac.yaml
```

## Exit codes

```text
0  valid chain
2  invalid or incomplete chain
3  input unreadable or unsupported format
```

## RAC-v1 object

```yaml
resolve_authority_chain:
  chain_version: RAC-v1
  chain_id:
  campaign_id:

  artifact_state:
    base_sha:
    head_sha:
    dirty_fingerprint:
    review_receipt:

  review_claim:
    claim_id:
    source:
    statement:
    suggested_repair:

  acceptance:
    contract_id:
    contract_fingerprint:
    horizon_fingerprint:
    law_refs: []
    relation:
      directly_entailed |
      compatibility_required |
      forbidden_state_witness |
      contract_invalidating |
      outside_horizon |
      unrelated |
      unknown |
      rejected

  adjudication:
    cex_id:
    validity:
      confirmed | refuted | stale | unknown
    liability:
    novelty:
    disposition:
    minimal_trace_ref:

  batch:
    batch_id:
    sealed: true
    mode:
      discovery | kernel_review | conformance | terminal_holdout

  compression:
    ceb_id:
    class_id:
    class_status:
    quotient_witness_ref:
    mbk_id:
    rc_id:
    transition_ref:
    proof_obligation_ref:

  realization:
    allowed: true | false
    target_owner:
    target_boundary:
    forbidden_expansions: []

  gate:
    current_artifact_state: yes | no
    complete_chain: yes | no
    mutation_allowed: yes | no
```

## Required checks

A valid mutation-authorizing RAC requires:

```text
chain_version = RAC-v1
artifact_state is complete
review_claim.claim_id present
acceptance contract/horizon/law present
acceptance relation is in-horizon
adjudication.validity = confirmed
batch.sealed = true
compression has CEB class, MBK, RC, transition, proof obligation
realization.allowed = true
gate.current_artifact_state = yes
gate.complete_chain = yes
gate.mutation_allowed = yes
```

A legal non-mutation RAC may set `realization.allowed=false` and
`mutation_allowed=no`, but it must still explain the non-mutation route using
acceptance/adjudication disposition.

## Fail-closed reasons

```text
missing_chain_version
missing_artifact_state
missing_review_claim
missing_acceptance_contract
missing_horizon
missing_law_refs
outside_horizon
unrelated_or_rejected
invalid_cex
unsealed_batch
missing_ceb_class
missing_mbk_or_rc
missing_transition
missing_proof_obligation
artifact_state_stale
realization_not_allowed
mutation_gate_disagrees
```

## Output JSON

```json
{
  "status": "valid" | "invalid",
  "mutation_allowed": true,
  "missing": [],
  "violations": [],
  "chain_id": "RAC-...",
  "campaign_id": "..."
}
```
