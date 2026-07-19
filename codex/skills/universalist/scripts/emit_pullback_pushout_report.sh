#!/usr/bin/env bash
set -euo pipefail
mode="${1:-compare}"
language="${2:-agnostic}"

case "$mode" in
  pullback)
    cat <<OUT
# Pullback Report (${language})

## Software seam
- witness object / compatible pair:
- shared target/observation C:

## Diagram
- f : A -> C:
- g : B -> C:
- P with pA : P -> A and pB : P -> B:

## Agreement
- equation f.pA = g.pB:
- mismatch behavior:

## Effective implementation
- opaque constructor / validated join / dependent pair:
- public bypass prevention:

## Universal law
- every compatible A/B candidate factors through P:
- uniqueness approximation / normalization:

## Tests
- matching pair accepted:
- mismatch rejected:
- projections preserved:
- falsifier:
OUT
    ;;
  pushout)
    cat <<OUT
# Pushout Report (${language})

## Software seam
- source A:
- source B:
- explicit overlap O:

## Diagram
- i : O -> A:
- j : O -> B:
- Q with qA : A -> Q and qB : B -> Q:

## Overlap policy
- identities safe to identify:
- structures that must remain distinct:
- named conflict policy:

## Effective implementation
- tagged coproduct:
- quotient / union-find / canonical IDs:
- provenance survival:

## Universal law
- qA.i = qB.j:
- every compatible A/B consumer factors through Q:
- uniqueness approximation / canonical normalization:

## Tests
- non-overlap preserved:
- overlap identified exactly once:
- false merge rejected:
- conflict surfaced:
- falsifier:
OUT
    ;;
  dpo|double-pushout|graph-rewrite)
    cat <<OUT
# Double-Pushout Rewrite Report (${language})

## Rule
- L <- K -> R:
- preserved interface K:
- match L -> G:

## Pushout complement
- deletions L-K:
- dangling-edge check:
- identification check:
- obstruction report if complement does not exist:

## Pushout
- additions R-K:
- result H:
- provenance / rewrite trace:

## Tests
- preserved interface unchanged:
- deleted structure absent:
- added structure present:
- forbidden dangling rewrite rejected:
- local rewrite composes under selected adhesive assumptions:
OUT
    ;;
  compare|selector)
    cat <<OUT
# Pullback / Pushout Selector (${language})

## Governing question

1. Is the unknown a witness/input whose A and B views must agree in C?
   -> Pullback.

2. Is the unknown an integrated output gluing A and B along explicit O?
   -> Pushout.

3. Is the task a graph/model rewrite with delete-preserve-add structure?
   -> Pushout complement + double pushout.

4. No agreement target or overlap?
   -> Product/coproduct or ordinary adapter instead.

## Candidate diagram
- worlds:
- maps:
- agreement or overlap:
- selected category:
- existence assumptions:

## Proof obligations
- commutative square:
- factorization:
- uniqueness approximation:
- operational constraints:
- falsifier:
OUT
    ;;
  *)
    echo "Unknown mode: $mode" >&2
    echo "Use pullback, pushout, dpo, or compare." >&2
    exit 2
    ;;
esac
