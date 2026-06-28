---
name: review-adjudication
description: "Convert review claims into minimal, intent-anchored counterexamples. Verify current behavior, branch liability, AC-v2 horizon relation, novelty, kernel impact, and the only legal disposition. Use for review findings, PR comments, CAS findings, terminal holdouts, CEX-v1, or deciding whether a valid issue belongs in the current campaign. Never issue direct code-mutation authority or hand raw review prose to an implementer."
metadata:
  version: "5.0.0"
  activation_cost: medium
  default_depth: strict
---

# Review Adjudication

## Mission

Separate:

```text
observed fact
review claim
repair suggestion
branch liability
intent entailment
counterexample novelty
kernel impact
legal disposition
```

Output one `counterexample / CEX-v1` or a rejected/blocked record.

A valid diff-local issue is not automatically campaign scope.

## Required inputs

```text
current artifact state
review mode
AC-v2 ID/fingerprint/horizon
accepted kernel/law refs when present
review claim and source refs
current code/proof evidence
known counterexample classes
```

If AC-v2 is required but absent or stale:

```text
disposition = blocked
```

## Review modes

```text
discovery
kernel_review
conformance
terminal_holdout
```

### Discovery

Broad search is allowed. Findings still require AC relation before admission.

### Kernel review

Evaluate AC/CEX/CEB/MBK/RC consistency. Do not review delivery implementation.

### Conformance

Only named RAP-v1 apertures are in review scope.

Allowed outputs:

```text
existing-law violation
missing law proof
orphan construct
stale artifact state
novel in-horizon CEX
outside-horizon proposal
clean
```

### Terminal holdout

Broad adversarial search is allowed once. No direct mutation authority.

## CEX-v1

```yaml
counterexample:
  counterexample_version: CEX-v1
  counterexample_id:
  campaign_id:
  batch_id:
  aperture_id:
  review_mode:

  artifact_state:
    base:
    head:
    dirty_fingerprint:
    review_receipt:

  claim:
    statement:
    source_refs: []
    suggested_repair:

  observation:
    actor:
    operation:
    pre_state:
    minimal_trace: []
    expected:
    actual:
    externally_visible_difference:
    reproduction_or_proof:

  validity:
    confirmed |
    refuted |
    stale |
    unknown

  liability:
    introduced_by_current_diff |
    exposed_and_required_by_current_acceptance |
    preexisting_but_blocks_current_invariant |
    adjacent_preexisting |
    reviewer_preference |
    unknown

  intent:
    contract_id:
    contract_fingerprint:
    horizon_fingerprint:
    acceptance_refs: []
    compatibility_refs: []
    forbidden_refs: []
    non_goal_refs: []
    kernel_law_refs: []
    relation:
      directly_entailed |
      compatibility_required |
      forbidden_state_witness |
      contract_invalidating |
      outside_horizon |
      unrelated |
      unknown
    witness:
    scope_effect:
      none |
      narrows |
      expands |
      invalidates_contract

  novelty:
    new_equivalence_class |
    new_witness_existing_class |
    duplicate |
    refuted |
    stale |
    unknown
  existing_class_ref:

  kernel_impact:
    existing_law_violation |
    additional_witness |
    missing_semantic_distinction |
    missing_proof |
    orphan_realization |
    stale_artifact_state |
    no_kernel_impact |
    unknown

  disposition:
    enter_kernel |
    attach_witness |
    invalidate_realization |
    return_to_contract |
    capture_followup |
    reject |
    blocked

  mutation_authority:
    allowed: no
    reason:
```

Mutation authority is always `no` at the finding level.

The controller grants realization authority only after a batch is sealed and the kernel/design gates pass.

## Minimal distinguishing trace

A confirmed actionable CEX must identify the smallest trace that distinguishes expected from actual behavior:

```text
actor
operation
pre-state
transition sequence
observable result
```

A broad code smell, speculative risk, or preferred repair is not a minimal trace.

## Deterministic decision table

### Refuted or stale

```text
disposition = reject
```

### Unknown validity, liability, or intent relation

```text
disposition = blocked
```

### Reviewer preference or unrelated claim

```text
disposition = reject
```

### Adjacent preexisting + outside horizon

```text
disposition = capture_followup
```

### Contract invalidating or scope expanding

```text
disposition = return_to_contract
```

### Missing semantic distinction inside sealed horizon

```text
novelty = new_equivalence_class
disposition = enter_kernel
```

### Existing-law violation during conformance

```text
disposition = invalidate_realization
```

No direct patch authorization.

### New witness for existing class

```text
disposition = attach_witness
```

No new code distinction or test family.

### Duplicate

```text
disposition = reject
or attach_witness only when it materially strengthens proof
```

### Missing proof

```text
disposition = attach_witness
```

Proof-only by default.

### Orphan realization

```text
disposition = invalidate_realization
```

## Novelty discipline

`new_equivalence_class` requires a witness that an existing class cannot explain.

Similarity to a different file, function, or review comment is not novelty.

`new_witness_existing_class` cannot authorize:

```text
new branch
new helper
new state
new protocol case
new fallback
new public symbol
new wound-specific test family
```

## Current-code verification

Before classification:

1. Reproduce or prove the observed behavior.
2. Identify the authority owner.
3. Distinguish claim from suggested repair.
4. Compare against current AC/kernel fingerprints.
5. Search existing CEX classes.
6. Classify liability and horizon relation.
7. Derive disposition.

Do not accept stale review text as current evidence.

## Validation

```bash
python3 codex/skills/review-adjudication/tools/counterexample_gate.py cex.json
```

## Output

Return:

```text
counterexample ID
validity / liability
intent relation / anchors
minimal trace
novelty / existing class
kernel impact
disposition
mutation authority = no
source/proof refs
```

## Hard rules

- Valid does not mean branch-liable.
- Branch-liable does not mean intent-entailed.
- Repair suggestions are not scope.
- Raw review prose never reaches an implementer.
- Every admitted CEX has a minimal trace and stable intent/law anchors.
- Additional witness does not create a code distinction.
- Conformance findings invalidate or return; they do not directly patch.
- Scope expansion returns to AC authority.
- Every finding-level mutation authority is `no`.
