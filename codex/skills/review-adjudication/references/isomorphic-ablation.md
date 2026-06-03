# Isomorphic ablation

Use this reference when a review comment or selected route proposes deletion,
collapse, reuse, canonicalization, privatization, or decommissioning.

## One rule

Prove behavior preservation before removing or merging surface. No proof means
`validate-first`, `proof-only`, or `blocked`, not deletion.

## Ablative Isomorphism Card

```md
Ablative Isomorphism Card:
- id/thread:
- surface:
- proposed action: delete | collapse | reuse | canonicalize | privatize | decommission
- behavior preserved:
- public contract preserved:
- error semantics preserved:
- ordering / side effects preserved:
- clone classification:
- abstraction-ladder check:
- compatibility risk: none | low | medium | high
- proof signal:
- deletion/collapse witness:
- card status: pass | validate-first | missing | not-required
```

## Clone classification

- `exact-clone`: byte-identical or structurally identical; usually safe to collapse
  with proof.
- `parametric-clone`: same shape with literals/names varied; candidate for
  parameterization when variance is bounded.
- `gapped-clone`: same shape with small additions/removals; collapse only when the
  variance is explicit and tested.
- `semantic-clone`: different code with apparently same behavior; do not merge
  without strong equivalence proof.
- `accidental-rhyme`: similar-looking code with independent lifecycle or invariant;
  do not merge.

## Abstraction ladder

- one case is unique;
- two cases may be coincidence;
- three cases can justify extraction;
- one axis of variance per rung;
- if variance exceeds shape, the abstraction is worse than the duplication.

## Review-adjudication usage

`address` is not permission to add code. For every mutation-capable warrant,
first ask whether the lower-surface route is deletion, reuse, collapse,
canonicalization, privatization, decommissioning, validate-first, or proof-only.
