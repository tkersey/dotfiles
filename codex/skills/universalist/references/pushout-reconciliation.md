# Pushout Reconciliation

Pushout Reconciliation is the context/schema integration specialization of the general mechanics in `references/mechanics/pullbacks-and-pushouts.md`.

Use it when multiple systems, teams, stores, models, or contexts have an **explicit overlap** that must be glued with preserved provenance and visible conflict.

```text
Context A  <-  Overlap Context  ->  Context B
     |                               |
     v                               v
              Integrated Context
```

## Use when

- two source worlds overlap;
- entity identity must be explicit;
- the overlap maps can be named;
- conflicting overlap must be surfaced;
- provenance from each side must survive;
- merging by field name or string similarity would be unsafe.

Do not call an arbitrary merge a pushout. If there is no overlap object and no maps from it into both sources, use ordinary integration language until those semantics are modeled.

## Artifacts

```text
OverlapSchema
OverlapInstance
SourceContextA
SourceContextB
IntegratedContext
ConflictReport
ProvenanceManifest
CanonicalIdPolicy
```

## Universal-property witness

Let:

```text
i : Overlap -> ContextA
j : Overlap -> ContextB
qA : ContextA -> IntegratedContext
qB : ContextB -> IntegratedContext
```

Require:

```text
qA . i = qB . j
```

Then test the software approximation of factorization:

> Every downstream consumer that handles both contexts and agrees on the overlap must consume the canonical integrated context, rather than implement a competing merge path.

Approximate uniqueness with:

- one canonical integration function or materialized view;
- canonical IDs / normalized representatives;
- no public bypass merge;
- property tests showing source-order independence when promised by the policy.

## Laws

- overlap identities are explicit;
- only declared overlap structure is identified;
- non-overlap facts are preserved;
- overlap conflicts are reported or resolved by named policy;
- provenance from both sides survives integration;
- the integrated context satisfies target constraints;
- compatible downstream consumers factor through the integrated representation.

## Falsifiers

- false merge caused by name similarity;
- two source concepts identified despite different semantics;
- one source silently dominates another without policy;
- non-overlap data disappears;
- provenance is lost;
- two public merge functions yield observably different integrated contexts;
- no target object can satisfy the declared overlap constraints.

## Operational note

Pushout semantics do not replace transactions, authorization, distributed convergence, temporal ordering, or conflict-resolution policy. Operational stores own mutation; the pushout-shaped integration belongs at a verified publication, migration, reconciliation, or model-transformation boundary.
