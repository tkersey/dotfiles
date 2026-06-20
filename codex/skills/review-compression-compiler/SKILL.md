---
name: review-compression-compiler
description: "Compile raw review/CAS/PR/validation findings into a Minimum Behavioral Kernel by factoring obligations, quotienting observationally indistinguishable distinctions, naming governing laws, and emitting a Reduction Certificate. Use for repeated findings, local-surface families, authority/replay/reconstruction invariants, behavioral quotienting, counterexample compression, or MBK-v1. Read-only; never emit patch hunks or authorize mutation."
metadata:
  version: "6.0.0"
  activation_cost: medium
  default_depth: strict
---

# Review Compression Compiler

## Mission

```text
many local findings
-> accepted observations
-> behavioral factors
-> observational equivalence
-> quotient congruence
-> governing laws
-> minimum behavioral kernel
-> reduction certificate
```

The compiler does not answer “what code should we add?” It answers:

```text
What behavior is actually distinguishable?
Which obligations are live?
Who owns each obligation?
Which local findings are witnesses of one law?
Which distinctions can be quotiented?
What normal form can still recompose the live contract?
```

## Doctrine

Operate in **FACTORING**, **QUOTIENTING**, **CONGRUENCE-CHECKED**, **WITNESS-BEARING**, **ABLATIVE-CANDIDATE**, **NORMALIZING**, and **REFINEMENT-PRESERVING** mode.

- **FACTORING**: decompose the reviewed whole into factors with distinct obligations, owners, observations, and recomposition roles.
- **QUOTIENTING**: merge distinctions no accepted observation can detect.
- **CONGRUENCE-CHECKED**: quotient classes must be preserved by every accepted operation and transition.
- **WITNESS-BEARING**: every retained distinction and governing law needs an observation or counterexample witness.
- **ABLATIVE-CANDIDATE**: mark orphan, duplicated, expired, invalid, or unrequired factors for downstream removal; do not authorize mutation here.
- **NORMALIZING**: select one canonical behavioral kernel rather than preserving local-surface families.
- **REFINEMENT-PRESERVING**: preserve required behavior while allowing invalid, obsolete, duplicated, or unrequired behavior to disappear.

## Input contract

Preserve:

```text
artifact state
acceptance criteria and non-goals
observed fact
review claim
suggested repair
branch liability
acceptance entailment
authority / owner
source refs
proof refs
```

Reviewer repair proposals are hints, not kernel elements.

## Workflow

1. **Acceptance and non-goals**
   - State the live contract and explicit exclusions.
   - Separate scope expansion from current-branch liability.

2. **Observation ledger**
   - Accept only current, source-backed observations.
   - Keep refuted, stale, adjacent, preference-only, and unknown claims outside the kernel.

3. **Factorization basis**
   - Identify carriers/state vocabulary, authorities, operations, transitions, effects, proof surfaces, and external obligations.
   - Give each factor one live obligation and recomposition role.

4. **Counterexample-family compression**
   - Group local findings by governing law, not merely file, API, check, or subsystem.
   - Same cluster does not automatically mean same law.

5. **Observational equivalence**
   - Define the observations allowed to distinguish factors or states.
   - Merge representations with identical accepted observations unless a retained distinction has a witness.

6. **Congruence check**
   - Verify each operation and transition maps equivalent inputs to equivalent observable results.
   - A failed or unknown congruence check blocks quotienting.

7. **Ablation candidates**
   - Mark orphan realizations, duplicated owners, expired distinctions, wound-specific proof families, and non-branch-liable surfaces.
   - Do not delete or authorize deletion.

8. **Kernel normal form**
   - Emit one Minimum Behavioral Kernel with governing laws, forbidden states/transitions, and canonical owners.
   - Prove the retained factors can recompose every required observation.

9. **Reduction Certificate**
   - Emit `RC-v1` using [reduction-certificate.md](references/reduction-certificate.md).
   - The default preservation relation is `refinement-preserving`.
   - Use `observationally-equivalent` only when the selected observation set is explicit and complete enough for the claim.
   - Use `isomorphic` only when a reversible structure-preserving correspondence is actually required and witnessed.

## Core laws

### No quotient without congruence

If two factors are identified, every accepted operation, transition, and observation must preserve their indistinguishability.

### No retained distinction without a witness

Every distinction remaining in the kernel must have an accepted observation that can distinguish its classes.

### No normal form without recomposition

The retained kernel must generate or explain every required accepted observation.

### No local-surface family as final ontology

A family named only after a file, API, function, check, or reviewer comment is undercompressed until its governing law is named.

## Output

Emit `minimum_behavioral_kernel / MBK-v1` plus `reduction_certificate / RC-v1`.

Required sections:

1. Acceptance and Non-Goals
2. Observation Ledger
3. Liability Ledger
4. Factorization Basis
5. Counterexample Family Compression
6. Authority Inventory
7. Carriers / State Vocabulary
8. Operations and Transitions
9. Governing Laws and Non-Laws
10. Observational Equivalence Partition
11. Quotient Congruence Witnesses
12. Forbidden States / Transitions
13. Proof-Law Basis
14. Local-Surface-to-Law Map
15. Ablation Candidates
16. Kernel Normal Form
17. Reduction Certificate
18. Kernel Gate

```yaml
kernel_gate:
  all_branch_liabilities_covered:
  every_factor_has_obligation:
  every_retained_distinction_has_witness:
  every_family_maps_to_law:
  quotient_is_congruent:
  local_surface_families_eliminated:
  authorities_owned:
  non_goals_preserved:
  proof_laws_present:
  recomposition_proved:
  reduction_certificate_complete:
  kernel_review_allowed:
```

## Hard rules

- Do not output code.
- Do not authorize realization or deletion.
- Do not preserve a distinction merely because the implementation currently contains it.
- Do not merge semantic clones whose equivalence or congruence is unproven.
- Scope expansion returns to spec/user authority.
- A failed Reduction Certificate gate blocks implementation handoff.

## Resources

- [reduction-certificate.md](references/reduction-certificate.md)
