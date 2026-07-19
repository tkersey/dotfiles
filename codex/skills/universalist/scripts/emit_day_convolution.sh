#!/usr/bin/env bash
set -euo pipefail

mode="${1:-day}"
language="${2:-agnostic}"

emit_header() {
  cat <<OUT
# Day Convolution / Description Composition (${mode}, ${language})

Use after Universalist has named the index world, base composition, indexed descriptions, observations, witness seam, law, falsifier, and resource boundary.
OUT
}

case "$mode" in
  day|day-convolution)
    emit_header
    cat <<'OUT'

## Selection

- index category/world:
- tensor:
- unit:
- indexed descriptions `F,G`:
- target semantic category:
- variance:
- nearby product rejected: pointwise / substitution / monadic composition / ordinary product

## Definition

```text
F star G = Lan_tensor(F external-product G)

(F star G)(c)
  ~= coend_{a,b} C(a tensor b,c) * F(a) * G(b)
```

## Effective artifact

- representation:
- legal-decomposition enumerator:
- finite-support/boundedness:
- coend/normal-form quotient:
- aggregation:
- interpreter/lax-monoidal map:

## Laws

- `represent(a) star represent(b) ~= represent(a tensor b)`
- unit
- associativity
- decomposition soundness/completeness
- quotient coherence
- interpretation preservation
- effect-order and resource law

## Falsifier

- illegal decomposition admitted:
- legal decomposition omitted:
- semantic collision under quotient:
- non-effective enumeration:
OUT
    ;;

  promonoidal|promonoidal-convolution)
    emit_header
    cat <<'OUT'

## Partial/relational composition kernel

```text
Compose(a,b;c)

(F star G)(c)
  ~= coend_{a,b} Compose(a,b;c) * F(a) * G(b)
```

- indices/resources/interfaces:
- admissibility witness:
- multiple-witness/provenance policy:
- incompatible composition:
- quotient policy:
- residual/internal hom:

## Laws

- every composite carries an admissibility witness;
- every supported legal witness contributes;
- incompatible pairs fail closed;
- witness provenance survives when observable;
- residual agrees with convolution order, when claimed.

## Falsifier

- incompatible resources accepted;
- distinct semantic witnesses silently collapsed;
OUT
    ;;

  applicative|applicative-convolution|static-effects)
    emit_header
    cat <<'OUT'

## Static computation description

- operation/index world:
- fixed computation shape:
- free/applicative description IR:
- dependency extractor:
- cost/documentation interpreter:
- execution interpreter:
- value-dependent case that must remain monadic:

## Laws

- Day multiplication agrees with `liftA2`/static combination;
- unit agrees with pure/identity;
- all operation cases are statically inspectable;
- production and analysis interpreters agree on declared structure;
- parallelization requires an independent commutativity/resource witness.

## Falsifier

- later operation structure depends on an earlier result;
- static syntax is used to justify unsafe effect reordering.
OUT
    ;;

  resource|resource-convolution|separation)
    emit_header
    cat <<'OUT'

## Resource convolution

```text
(P star Q)(r)
  iff exists r1,r2.
       Compose(r1,r2;r)
       and P(r1)
       and Q(r2)
```

- resource type:
- partial composition:
- disjointness/compatibility:
- unit resource:
- assertion/predicate representation:
- residual/magic-wand analogue:
- split enumeration strategy:

## Laws

- only compatible splits contribute;
- unit resource is neutral;
- associativity holds up to resource equality;
- resource labels/provenance survive;
- split enumeration is bounded/effective.

## Falsifier

- overlap accepted;
- legal split omitted;
- exponential split search without representation strategy.
OUT
    ;;

  spatial|spatial-convolution)
    emit_header
    cat <<'OUT'

## Comonadic spatial composition

The always-defined starting point is:

```text
(P1 external-product P2)(U,V) = P1(U) x P2(V)
```

- left spatial world/subbasis:
- right spatial world/subbasis:
- shared/product index world:
- tensor/unit or promonoidal kernel:
- reindexing of the left description:
- reindexing of the right description:
- external-product patch vocabulary:
- density-Day comparison map:
- comparison status: isomorphism / observational equivalence / bounded approximation / no Day claim
- combined points:
- combined halos:
- labelled-halo translation:
- continuous projections:
- local/global identity policy:
- effective/indexed product representation:

## Laws

- external-product patches generate the selected density construction;
- a Day claim is made only when the shared index and comparison witness are explicit;
- projections preserve required locality;
- combined halo labels are preserved/translated explicitly;
- local/global identity remains traceable;
- product maintenance fits the resource budget.

## Falsifier

- external-product patches exist but no common Day index/category is supplied;
- ordinary list concatenation produces the same observations;
- product of point sets loses halo multiplicity or labels;
- no effective halo product exists.
OUT
    ;;

  compare|selector)
    emit_header
    cat <<'OUT'

| Pressure | Select | Reject |
| --- | --- | --- |
| same index | pointwise/Hadamard | no decomposition aggregation |
| every `a tensor b -> c` | Day convolution | not ordinary product |
| partial/relation-valued composition | promonoidal convolution | do not totalize |
| recursive typed insertion | substitution/plethysm | not Day/Cauchy |
| value-dependent sequencing | monadic/endofunctor composition | not applicative/static |
| ordered effect execution | Freyd/premonoidal | description tensor grants no interchange |
| shared-observation agreement | pullback | not convolution |
| overlap gluing | pushout | not convolution |
OUT
    ;;

  *)
    echo "unknown Day convolution mode: $mode" >&2
    echo "use: day | promonoidal | applicative | resource | spatial | compare" >&2
    exit 2
    ;;
esac
