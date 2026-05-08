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
  left-lift|lft|lift-realization)
    cat <<OUT
# Left Kan lift law-test plan (${language})

## Unit/comparison naturality

For h : a -> a' and x in F(a), with eta : F -> P.L:

P(L(h))(eta(a, x)) == eta(a', F(h)(x))

## Realization

For each witness a:

F(a) is related to P(Lft_P F(a)) by eta

In a finite poset approximation:

desired(a) <= project(left_lift(a))

## Minimality / factorization

Given alpha : F -> P.G, implement alphaSharp : Lft_P F -> G.
Assert:

alpha == (P.alphaSharp) . eta

For posets, assert no smaller implementation still covers desired(a).

## Regression witness

Pick one endpoint/feature/test. Assert the synthesized internal artifact projects to the desired public behavior.

## Failure case

Add a test proving direct public behavior cannot bypass P.
OUT
    ;;
  right-lift|rift|lift-obligation)
    cat <<OUT
# Right Kan lift law-test plan (${language})

## Counit/comparison naturality

For h : a -> a' and projected behavior y in P(R(a)), with epsilon : P.R -> F:

F(h)(epsilon(a, y)) == epsilon(a', P(R(h))(y))

## Soundness

For each witness a:

P(Rft_P F(a)) is related to F(a) by epsilon

In a finite poset approximation:

project(right_lift(a)) <= desired(a)

## Maximality / factorization

Given beta : P.G -> F, implement betaSharp : G -> Rft_P F.
Assert:

beta == epsilon . (P.betaSharp)

For posets, assert no larger implementation remains sound under desired(a).

## Regression witness

Pick one test/spec slice. Assert residual obligations are sufficient/sound for that slice.

## Failure case

Add a test for one tempting obligation that violates the spec after projection.
OUT
    ;;
  defunctionalization|defun|boundary-ir)
    cat <<OUT
# Defunctionalization law-test plan (${language})

## Semantic preservation

For every original function value f crossing the boundary and its defunctionalized case df:

apply(df, input) == f(input)

Use the domain-specific interpreter name:
- interpretPath(path, payload)
- runObservation(model, observation)
- applyFrame(frame, value)
- projectImplementation(plan, case)
- satisfyObligation(design, obligation)

## Kan witness preservation

Tie the preservation test to the selected construction:

- Lan: interpretPath(identityPath, x) agrees with eta(x) / old behavior after embedding.
- Ran: runObservation projections commute through epsilon.
- Delta: restrict(defunctionalizedCase, newModel) equals old fixture.
- Lft: projectImplementation(plan(a)) realizes F(a).
- Rft: satisfyObligation obligations are sound for F(a).

## Centralization / factorization

Assert no public path invokes the old anonymous callbacks directly.
All boundary behavior flows through the case constructors and interpreter.

## Failure case

Add one constructor with invalid payloads or impossible projection and assert it fails explicitly.
OUT
    ;;
  postcomposition|pstar)
    cat <<OUT
# Postcomposition law-test plan (${language})

For P : B -> C and known implementation G : A -> B:

P_*(G) = P . G

Tests:
- P preserves identities and composition on the implementation slice
- public behavior is produced only through P
- one golden public observation equals P(G(a))
OUT
    ;;
  *) echo "Unknown direction: $direction" >&2; exit 2 ;;
esac
