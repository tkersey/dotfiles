---
name: review-compression-compiler
description: "Compile raw review/CAS/PR/validation findings into a Minimum Behavioral Kernel rather than a repair queue. Use for repeated findings, local-surface families, authority/replay/reconstruction invariants, observational equivalence, counterexample compression, proof-law extraction, or MBK-v1. Read-only; never emit patch hunks or authorize mutation."
metadata:
  version: "5.0.0"
  activation_cost: medium
  default_depth: strict
---

# Review Compression Compiler

## Mission

```text
many review findings
-> few accepted observations
-> few governing laws
-> minimum behavioral kernel
```

The compiler does not answer “what code should we add?”

It answers:

```text
What behavior is actually distinguishable?
Who owns it?
Which observations prove the distinction?
Which local findings are witnesses of one law?
```

## Input

Preserve:

```text
artifact state
observed fact
review claim
suggested repair
liability
acceptance entailment
source refs
```

## Output

Emit `minimum_behavioral_kernel / MBK-v1`.

Required sections:

1. Acceptance and Non-Goals
2. Observation Ledger
3. Liability Ledger
4. Counterexample Family Compression
5. Authority Inventory
6. Carriers / State Vocabulary
7. Operations and Transitions
8. Governing Laws and Non-Laws
9. Observational Equivalence Partition
10. Forbidden States / Transitions
11. Proof-Law Basis
12. Local-Surface-to-Law Map
13. Kernel Gate

## Compression rules

- Same cluster does not imply same law.
- Different local surfaces may witness one law.
- A family named only after a file/API/check is undercompressed until its governing law is named.
- A new state distinction requires an accepted observation witness.
- Multiple representations with identical accepted observations should be quotiented.
- Reviewer repair proposals are hints.
- Non-branch-liable findings remain outside the kernel.
- Scope expansion returns to spec/user authority.
- Do not output code.
- Do not authorize realization.

## Kernel gate

```yaml
kernel_gate:
  all_branch_liabilities_covered:
  every_distinction_has_witness:
  every_family_maps_to_law:
  local_surface_families_eliminated:
  authorities_owned:
  non_goals_preserved:
  proof_laws_present:
  kernel_review_allowed:
```
