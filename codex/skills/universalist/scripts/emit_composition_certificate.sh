#!/usr/bin/env bash
set -euo pipefail
kind="${1:-generic}"
language="${2:-agnostic}"
cat <<OUT
# Composition Certificate scaffold (${kind}, ${language})

## Worlds

Source world:
- objects:
- transformations:
- invariants:
- observations:
- primitives:
- composition rules:

Target world:
- objects:
- transformations:
- invariants:
- observations:
- primitives:
- composition rules:

## Boundary

- name:
- kind: embedding / projection / forgetful / interpreter / compiler / serializer / view / handler / observer / migration / pullback agreement / pushout integration / graph rewrite / locality-preserving / indexed-description / adapter
- function or module:
- preserved:
- forgotten:
- generated:
- observed:

## Unknown

- location: after boundary / behind boundary / compatible witness / integrated output / local neighborhood / indexed descriptions / inside syntax / behavior / effects / observation / generation / callback

## Canonical artifact

- artifact:
- why this artifact:
- nearby alternative rejected:

## Pullback / pushout square, when applicable

- construction: none / pullback / pushout / pushout-complement + double-pushout
- category/world: Set / types / schemas / graphs / presheaves / other
- span or cospan maps:
- shared target or overlap:
- agreement / identity policy:
- commutative-square law:
- factorization witness:
- uniqueness approximation / canonical normal form:
- effective construction: validator / join / quotient / union-find / graph rewrite
- pushout-complement or existence obstruction:
- provenance and conflict policy:

## Spatial geometry, when applicable

- applicable: yes / no
- spatial structure: ordinary graph / density comonad / comonadic space / approximation
- points:
- local patches / subbasis:
- basis or coverage claim:
- local points:
- global points:
- local-to-global map / identifications:
- representative halo:
- halo representation: formal / finite / bounded / indexed
- labelled-halo fields:
- coalgebra / situated-object interpretation:
- counit / center extraction:
- comultiplication / nested local views:
- restriction / germ operation:
- point map across boundary:
- coalgebra/context transport:
- halo-map direction:
- ordinary comonad map / continuous map / both / neither:
- locality preserved:
- locality forgotten / translated / generated:
- basis-density / reconstruction witness:
- continuity law:
- continuity falsifier:
- resource / invalidation law:

## Description composition, when applicable

- applicable: yes / no
- base index category/world:
- index objects / grades / resources / interfaces:
- index morphisms / refinements:
- base tensor / composition operation:
- unit:
- promonoidal kernel, if partial/relational:
- description category:
- variance: covariant / presheaf
- indexed descriptions:
- selected product: pointwise / Day / promonoidal / substitution / endofunctor composition / ordinary
- nearby product rejected:
- distinguishing counterexample:
- Day specification: F star G = Lan_tensor(F external-product G)
- pointwise/coend formula:
- legal decomposition witnesses:
- coend/reindexing equivalence:
- atomic/representable embedding:
- executable representation:
- finite support / boundedness:
- decomposition enumerator / query:
- aggregation/target tensor:
- normalization / quotient:
- canonical representative:
- provenance retained outside quotient:
- lax-monoidal interpreter:
- residual/internal hom, if any:
- effect-order owner/restrictions:
- collision policy:
- complexity/resource bound:
- description-composition law:
- description-composition falsifier:

## Composition grammar

- geometry: category / monoidal / Freyd-premonoidal / operad / PROP-properad / traced-coalgebraic / resource-sensitive
- colors / port types:
- primitive operations / components:
- substitution / wiring rules:
- symmetry / ordering / centrality:
- multiple-output / feedback / resource requirements:
- forbidden wiring / effect reorderings:
- semantic algebras / interpretations:

## Effect geometry

- pure world/category:
- effectful world/category:
- pure embedding J:
- central operations:
- evaluation order:
- context action / value threading:
- certified commuting or parallel operations:
- noncommuting witness:

## Presentation

- mode: algebraic / codensity / density-comonadic-spatial / mixed / primitive
- generators / operations / equations:
- dense probes / finite approximants:
- dualizing observation object:
- local patches / subbasis:
- effective basis / halo representation:
- reconstruction / codensity operation:
- restriction / continuity operation:
- domain-specific theorem or assumption:
- presentation law:
- presentation falsifier:

## Primitive effects

- allowed primitives:
- where they enter:
- containment rule:

## Interpreter / projection / lowering / handler

- function:
- owner module:
- bypass prevention:

## Law witness

- positive law test:
- factorization / uniqueness / reconstruction approximation:
- falsifier / negative witness:

## Status

planned / implemented / verified / approximated / obstructed / primitive exception
OUT
