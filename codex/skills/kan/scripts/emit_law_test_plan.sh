#!/usr/bin/env bash
set -euo pipefail
direction="${1:-lan}"
language="${2:-agnostic}"
case "$direction" in
  lan|left)
    cat <<OUT
# Lan law-test plan (${language})

## Unit naturality

For f : c -> c' and x in F(c):

lan_map(K(f), eta(c, x)) == eta(c', F(f)(x))

## Factorization

Given alpha : F -> G.K, implement alphaSharp : Lan_K F -> G.
Assert:

alphaSharp(K(c), eta(c, x)) == alpha(c, x)

## Regression witness

Pick one old/core feature. Assert old behavior equals new behavior after embedding.

## Failure case

Add a test for one quotient/canonicalization collision.
OUT
    ;;
  ran|right)
    cat <<OUT
# Ran law-test plan (${language})

## Counit naturality

For f : c -> c' and family in Ran_K F(Kc):

F(f)(epsilon(c, family)) == epsilon(c', ran_map(K(f), family))

## Factorization

Given beta : G.K -> F, implement betaSharp : G -> Ran_K F.
Assert:

epsilon(c, betaSharp(g) at Kc) == beta(c, g restricted by K)

## Regression witness

Pick two overlapping old observations. Assert projections commute.

## Failure case

Add a test for inconsistent observations.
OUT
    ;;
  delta|restriction)
    cat <<OUT
# Delta/restriction law-test plan (${language})

For K : C -> D and target semantics G : D -> E:

Delta_K(G) = G . K

Tests:
- old endpoint/report over Delta_K(new) equals expected old behavior
- identities and composition are preserved by the mapping K
- no direct bypass around the restriction adapter
OUT
    ;;
  *) echo "Unknown direction: $direction" >&2; exit 2 ;;
esac
