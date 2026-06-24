---
name: review-compression-compiler
description: "Compile a sealed batch of intent-anchored CEX-v1 counterexamples into CEB-v2, one Minimum Behavioral Kernel, RC-v1, targeted review apertures, realization constraints, and an initial review-potential baseline. Use for repeated CAS/PR findings, same-family recurrence, behavioral quotienting, review batching, conformance planning, proof compression, MBK/RC synthesis, or review-driven growth. Read-only; never output patch hunks, mutate delivery, or admit raw review prose."
metadata:
  version: "7.0.0"
  activation_cost: high
  default_depth: strict
---

# Review Compression Compiler

## Mission

```text
sealed AC-v2
+ sealed RB-v1
+ validated CEX-v1 records
-> CEX quotient
-> CEB-v2
-> MBK-v1
-> RC-v1
-> targeted RAP-v1 apertures
-> minimum-realization constraints
-> PHI-v1 baseline
```

The compiler answers:

```text
Which counterexamples are novel?
Which are witnesses of one class?
Which accepted laws remain unsatisfied?
Which distinctions are observable?
Which classes may be quotiented?
Which owner and normal form can cover the complete basis?
Which proof families cover laws rather than review wounds?
```

It does not answer:

```text
What patch should we apply for this comment?
```

## Input contract

Require:

```text
sealed AC-v2 and horizon fingerprint
sealed review batch
all claims classified
validated CEX-v1 records
artifact/campaign tuple
existing kernel/RC when refining
existing negative route evidence when applicable
```

Reject:

```text
raw findings
open batch
unknown intent relation
unanchored counterexample
out-of-horizon item inside the basis
```

## 1. Seal the counterexample basis

Emit `counterexample_basis / CEB-v2`:

```yaml
counterexample_basis:
  basis_version: CEB-v2
  basis_id:
  campaign_id:
  contract_id:
  contract_fingerprint:
  horizon_fingerprint:
  batch_ids: []
  artifact_state:

  accepted_counterexamples: []
  excluded_counterexamples:
    - counterexample_id:
      disposition:
      reason:

  equivalence_classes:
    - class_id:
      governing_law_refs: []
      acceptance_refs: []
      representative_counterexample:
      member_counterexamples: []
      minimal_observation:
      canonical_owner:
      proof_obligation:
      novelty:
        new |
        existing
      status:
        open |
        satisfied |
        invalidated

  quotient:
    relation:
    method:
      exact_partition_refinement |
      exact_bisimulation |
      witness_checked_manual |
      not_applicable
    merged_counterexample_ids: []
    retained_class_ids: []
    congruence_witnesses: []
    unresolved: []

  gate:
    every_claim_classified:
    every_accepted_cex_in_horizon:
    every_cex_has_intent_anchor:
    duplicates_quotiented:
    no_unknown_novelty:
    batch_sealed:
    basis_allowed:
```

Validate:

```bash
python3 codex/skills/review-compression-compiler/tools/counterexample_basis_gate.py basis.json
```

## 2. Compile the MBK

Factor:

```text
accepted requirements
compatibility obligations
forbidden states
authorities
carriers
operations
transitions
effects
proof surfaces
recomposition roles
```

Every law must cite:

```text
AC requirement/compatibility/forbidden refs
accepted CEX classes
proof obligations
canonical owner
```

Every observation must cite a validated in-horizon CEX or a source AC witness.

## 3. Quotient behavioral distinctions

Merge states/paths when no accepted observation distinguishes them.

Do not merge when:

```text
accepted law distinguishes them
operation/transition is not congruent
authority owner differs observably
cleanup/failure semantics differ
proof obligation differs materially
```

No quotient without congruence.

## 4. Treat witness multiplicity correctly

When several findings witness one class:

```text
one kernel distinction
one governing law
one proof family
possibly multiple witness fixtures
```

Never:

```text
one branch/helper/test family per witness
```

## 5. Compile RC-v1

Include:

```text
factorization
quotient relation and congruence
retained distinction witnesses
ablation dispositions
target normal form
preservation relation
recomposition rule
surfaces to retire
```

Default preservation:

```text
refinement-preserving
```

Do not claim isomorphism because tests pass.

## 6. Compile minimum-realization constraints

Select design constraints lexicographically:

```text
1. no invented accepted distinction
2. no new authority owner
3. no new state/protocol/public/fallback dimension
4. maximum retirement of duplicate/orphan surface
5. minimum branches/helpers/test families
6. minimum textual diff
```

This is a hitting-set problem over accepted CEX classes and laws:

```text
selected constructs must cover every accepted class/law
every selected construct must map to at least one class/law
```

Do not output code.

## 7. Compile review apertures

Emit RAP-v1 apertures that target uncovered/high-risk cuts:

```yaml
review_aperture:
  aperture_version: RAP-v1
  aperture_id:
  review_mode:
  law_refs: []
  owner_refs: []
  operation_refs: []
  transition_refs: []
  proof_refs: []
  existing_class_refs: []
  requested_counterexample_kinds: []
  excluded_scope: []
  risk:
  overlap_with: []
  whole_diff_allowed:
```

Conformance apertures require named laws/owners and `whole_diff_allowed: no`.

Terminal holdout is the only post-kernel mode that may use a broad aperture.

## 8. Compile PHI baseline

Emit the pre-realization review potential:

```text
unclassified in-horizon CEX
unsatisfied laws
open CEX classes
orphan constructs
hard semantic surface
unmapped/missing proof debt
```

The controller computes and gates the observed post-realization PHI.

## 9. Proof compression

Map proof to laws/classes:

```text
focused witness proof
class/family property proof
recomposition proof
terminal holdout proof
```

Flag:

```text
wound-specific tests
duplicate proof families
proof actions without law mapping
stale proof epochs
```

## 10. Refinement

For a later sealed conformance batch:

```text
same-class recurrence
  -> invalidate realization; kernel class remains

new in-horizon class
  -> revise CEB/MBK/RC

outside horizon
  -> exclude from basis; follow-up or AC rebase

missing proof
  -> update proof basis without new semantic distinction
```

## Output

Emit:

```text
CEB-v2
MBK-v1
RC-v1
RAP-v1 set
realization constraint set
PHI-v1 baseline
proof-law basis
```

## Hard rules

- Consume only sealed, validated inputs.
- Do not admit outside-horizon findings.
- Do not create a kernel distinction for another witness.
- Do not preserve local-surface families as final ontology.
- Do not output patches or authorize mutation.
- No quotient without congruence.
- No retained distinction without an accepted witness.
- No normal form without recomposition.
- Every realization element must be class/law mapped.
