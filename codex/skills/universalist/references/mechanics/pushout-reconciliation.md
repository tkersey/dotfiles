# Pushout Reconciliation Mechanics

Read `pullbacks-and-pushouts.md` first for the formal universal property, implementation patterns, DPO rewriting, and selection criteria.

Use this specialization when two or more contexts or schemas overlap and must be integrated with explicit identity, conflict, and provenance semantics.

```text
ContextA <- OverlapContext -> ContextB
      \                         /
       \                       /
        IntegratedContext
```

## Recover

- source contexts or schemas;
- overlap schema;
- overlap instance / identity correspondences;
- maps from overlap into each source;
- attributes and relations safe to identify;
- attributes and relations that must remain distinct;
- conflict policy;
- target integrated context schema;
- provenance survival policy;
- canonical public integration path.

## Universal law

With `i : O -> A`, `j : O -> B`, `qA : A -> Q`, and `qB : B -> Q`:

```text
qA . i = qB . j
```

Every compatible pair of consumers from `A` and `B` that agrees on `O` should factor through `Q`. Approximate uniqueness with one canonical integration function/view and normalized identifiers.

## Laws

- overlap identities are explicit;
- only declared overlap is identified;
- non-overlap facts are preserved;
- conflicts are reported or resolved by named policy;
- provenance from each source survives;
- integrated context satisfies target constraints;
- competing merge paths are removed or shown observationally equivalent.

## Falsifiers

- false identity;
- silent conflict collapse;
- lost provenance;
- source-order-dependent result where order independence was promised;
- integrated constraints are inconsistent;
- a downstream consumer bypasses the canonical integrated representation.
