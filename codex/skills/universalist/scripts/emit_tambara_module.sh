#!/usr/bin/env bash
set -euo pipefail
mode="${1:-module}"
language="${2:-agnostic}"

header() {
  cat <<OUT
# Tambara Module Mechanics (${mode}, ${language})

Terminology: Pastro-Street / profunctor-optics Tambara module; not an equivariant Tambara functor.
OUT
}

case "$mode" in
  module|contextual-morphism)
    header
    cat <<'OUT'

## Signal

A generalized transformation, relation, observation/update capability, or proof must remain valid when the same admissible context is added around both endpoints.

## Data

```text
(M, tensor, I)              ambient context world
L : M x C -> C              source action
R : M x D -> D              target action
P : C^op x D -> V           underlying profunctor
alpha_m : P(a,b) -> P(L(m,a), R(m,b))
```

## Laws

- `alpha_I ~= id`
- `alpha_(m tensor n) ~= alpha_m . alpha_n`
- endpoint reindexing commutes with framing
- coherent context reindexing preserves observations
- interpretation of framing agrees with semantic framing
- framing grants no effect commutativity or resource reuse

## First witness

- one local capability:
- one context:
- one frame operation:
- unit test:
- nested-frame test:
- naturality test:
- falsifier:
OUT
    ;;
  mixed|mixed-optic)
    header
    cat <<'OUT'

## Mixed Tambara / optic

Use when one context world acts differently on source and target worlds.

```text
L : M x C -> C
R : M x D -> D
P : C^op x D -> V
```

Residual optic form:

```text
exists m.
  decompose : s -> L(m,a)
  rebuild   : R(m,b) -> t
```

Interpretation:

```text
p -> alpha_m(p) -> dimap(decompose, rebuild, alpha_m(p))
```

Record:

- source and target actions:
- residual/context IR:
- coend/reindexing quotient:
- profunctor representation:
- domain optic laws:
- effect-order owner:
- residual leak falsifier:
OUT
    ;;
  optic)
    header
    cat <<'OUT'

## Optic representation

```text
Optic((a,b),(s,t))
  = coend_m C(s,L(m,a)) x D(R(m,b),t)
```

Profunctor representation, when assumptions hold:

```text
forall p. Tambara p => p a b -> p s t
```

Checklist:

- residual type/context:
- decomposition:
- reconstruction:
- quotient/normal form:
- Tambara interpreter:
- parametricity assumptions:
- lens/prism/traversal/domain laws:
- hidden-residual falsifier:
OUT
    ;;
  free|free-tambara)
    header
    cat <<'OUT'

## Free contextual closure

Generate every legal framed use of a bare profunctorial capability.

Schematic form:

```text
FreeTambara(Sigma)(f,g)
  = coend_{m,a,b}
      C(f,L(m,a)) x Sigma(a,b) x D(R(m,b),g)
```

Checklist:

- bare generator/profunctor:
- context basis/enumerator:
- residual IR:
- reindexing quotient:
- normal form:
- interpreter:
- finite/bounded support:
- resource bound:
- non-effective obstruction:
OUT
    ;;
  cofree|all-context)
    header
    cat <<'OUT'

## Cofree all-context observation

Schematic form:

```text
Theta(P)(a,b) = end_m P(L(m,a), R(m,b))
P -> Theta(P)
```

Checklist:

- supported context basis/query:
- coherent family of framed capabilities:
- unit/coassociativity laws:
- symbolic/lazy representation:
- finite observation surface:
- effectivity obstruction:
OUT
    ;;
  dependent|dependent-tambara)
    header
    cat <<'OUT'

## Dependent Tambara module

Use when context changes indices or depends on the focused object. Model the context action with a double category rather than erasing indices.

Checklist:

- double category of contexts:
- horizontal and vertical indices:
- source/target dependent actions:
- horizontal naturality/framing law:
- index transport:
- residual representation:
- typed counterexample rejected:
- effective encoding:
OUT
    ;;
  center|day-center|day-center-tambara)
    header
    cat <<'OUT'

## Day-center / Tambara relationship

Under suitable closedness/rigidity hypotheses:

```text
strong Tambara modules
  ~=
monoidal center of ([A,V], Day convolution)
```

Interpretation:

```text
Day centrality    descriptions move coherently through convolution
Tambara strength generalized morphisms move coherently through context
```

Checklist:

- base closed/rigid hypotheses:
- Day product:
- strong/left-strong Tambara structure:
- half-braiding/centrality witness:
- Cayley/profunctor representation:
- executable consequence:
- hypothesis-failure falsifier:
OUT
    ;;
  representable|module-functor)
    header
    cat <<'OUT'

## Representability diagnostic

A Tambara module is a generalized morphism and may not be a concrete module functor.

Checklist:

- underlying Tambara module:
- right-adjoint/Cauchy-completeness assumptions:
- candidate concrete module functor:
- representation map:
- round-trip law:
- nonrepresentability obstruction:
OUT
    ;;
  compare)
    header
    cat <<'OUT'

## Selection matrix

| Pressure | Select |
| --- | --- |
| one context acts on both endpoints | Tambara module |
| endpoint actions differ | mixed Tambara module |
| context changes indices | dependent/double-categorical Tambara |
| residual must be explicit | optic/double/residual IR |
| bare operation needs all legal frames | free Tambara |
| capability must expose every frame coherently | cofree/all-context Tambara |
| actual implementation map is required | representability/module-functor diagnostic |
| descriptions themselves combine over decompositions | Day/promonoidal convolution |
| runtime effects sequence observably | Freyd/premonoidal mechanics |
| locality/halos define context | comonadic spatiality plus possible Tambara action |

Reject Tambara when a plain adapter, ordinary profunctor, context parameter, reader/environment value, or explicit residual record already makes the seam exact.
OUT
    ;;
  *)
    echo "unknown Tambara module mode: $mode" >&2
    echo "Use module, mixed, optic, free, cofree, dependent, center, representable, or compare." >&2
    exit 2
    ;;
esac
