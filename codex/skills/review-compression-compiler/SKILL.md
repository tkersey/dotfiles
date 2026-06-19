---
name: review-compression-compiler
description: "Compile raw review, CAS, PR, validation, and user findings into a smallest independent branch-liable counterexample basis for C³ `$resolve`. Use for repeated or adjacent findings, same-family recurrence, finding-family compression, liability separation, proof-obligation extraction, and candidate-route hints. Read-only; never output patch hunks or authorize delivery mutation."
metadata:
  version: "4.0.0"
  activation_cost: medium
  default_depth: strict
---

# Review Compression Compiler

## Mission

Turn review findings into a **counterexample basis**, not a repair queue.

```text
many comments
-> few independent governing rules
-> explicit proof obligations
```

## Input discipline

For every finding preserve:

```text
observed fact
review claim
proposed repair
uncertainty
artifact state
source refs
```

Classify liability before compression.

## Output

```yaml
counterexample_basis:
  basis_version: CEB-v1
  immutable_base:
  branch_liabilities:
    - finding_id:
      liability:
      observed_behavior:
      required_behavior:
      reproduction_or_proof:
      source_refs: []
  non_branch_liabilities:
    - finding_id:
      disposition: followup | reject | validate-only | blocked
      reason:
  families:
    - family_id:
      governing_rule:
      independent_witnesses: []
      subsumed_findings: []
      canonical_owner_candidates: []
      failure_surface:
      proof_obligations: []
      candidate_route_hints:
        - no-change
        - subtractive
        - existing-owner
        - representation
        - boundary
        - local-baseline
  original_acceptance: []
  gate:
    all_findings_classified: pass | fail
    every_branch_liability_covered: pass | fail
    non_branch_liabilities_excluded: pass | fail
```

## Compression rules

- Same cluster does not imply same family.
- Similar prose does not imply one governing rule.
- Several manifestations of one missing rule should not become several implementation tasks.
- Preserve independent witnesses that distinguish bad candidates.
- A finding may be valid and non-branch-liable.
- Reviewer repair suggestions are hints only.
- Candidate route hints must include a lower-surface alternative when plausible.
- Do not output code.
- Do not authorize mutation.
