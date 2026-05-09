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
  yoneda|observation|yoneda-observation)
    cat <<OUT
# Yoneda law-test plan (${language})

## Observation round trip

If an identity observation is available:

observe(toYonedaLike(value), identityObservation) == value

Otherwise choose one canonical public observation and assert it agrees with the old direct accessor.

## Map / observation fusion

For observations or maps f and g:

observe(value, compose(f, g)) == observeMapped(observe(value, f), g)

Use the concrete names in the codebase: selectors, projections, query paths, policy checks, or test oracles.

## Representation independence

Two internal representations that project to the same public behavior must agree on every sanctioned Observation.

## Selected Kan law

- Ran: counit projections through the observer agree with legacy observations.
- Rft: projected residual obligations are sound for each public observation.
- P_*: public behavior is produced only through P and observe.

## Failure case

Add one observer that tries to inspect forbidden internals and assert it cannot be expressed or fails validation.
OUT
    ;;
  coyoneda|generation|coyoneda-generation)
    cat <<OUT
# Coyoneda law-test plan (${language})

## Identity lowering

If an identity path is available:

lower(identityPath, payload) == payload

Otherwise choose one canonical old/core payload and assert lowering agrees with the old interpreter.

## Map/path fusion

For deferred paths p and q:

lower(composePath(p, q), payload) == lower(q, lower(p, payload))

Use the concrete names in the codebase: migration paths, projection paths, generated artifact lowering, or plugin defaults.

## Provenance preservation

Generated/deferred artifacts must retain source identity and path until lowering.

## Selected Kan law

- Lan: identity/generated path on an old/core artifact agrees with eta / old behavior after embedding.
- Lft: candidate realizer plus projection path realizes the required behavior through P.

## Failure case

Add one invalid path/payload pairing and assert lowering fails explicitly.
OUT
    ;;
  yoneda-coyoneda|yc|boundary-representation)
    cat <<OUT
# Yoneda/Coyoneda boundary-representation law-test plan (${language})

## Yoneda side

- Every sanctioned observation is explicit and runnable.
- Observations are representation-independent.
- Overlapping observations commute when the selected construction is Ran/Rft.

## Coyoneda side

- Every generated payload keeps source provenance.
- Deferred paths lower through one interpreter.
- Map/path fusion holds on a witness path pair.

## Lift combination

For P : B -> C and F : A -> C:

runObservation(P(realizer(a)), obs) == runObservation(F(a), obs)

for every witness observation obs.

## Defunctionalization link

If observations or paths are functions, replace them with constructors and prove:

runObservation(defunctionalizedObs) == originalObserver
lower(defunctionalizedPath, payload) == originalMap(payload)

## Failure case

Missing projection path emits an explicit residual obligation.
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
  contract-lift|lift-contract|outside-in-refactor)
    cat <<OUT
# Contract-first Kan lift law-test plan (${language})

## Projection law

For witness case a, candidate implementation L(a), projection P, and required behavior F(a):

observe(P(L(a)), obs) == observe(F(a), obs)

for every public observation obs in the witness suite.

## Approximation variant

If exact equality is not the goal, state the relation explicitly:

required(a) <= project(L(a))        # covering / realization
project(R(a)) <= required(a)        # sound residual

## Projection centrality

Assert all public outputs, traces, reports, and contract checks flow through P.

## No-exact-lift failure

Add one required observation that current P cannot produce and assert the code emits an explicit no-exact-lift/obligation report.
OUT
    ;;
  obligation-lift|lift-obligations|residual-obligations)
    cat <<OUT
# Kan lift obligation law-test plan (${language})

## Obligation soundness

For each derived obligation R(a):

project(R(a)) <= required(a)

State the order: containment, implication, trace refinement, policy order, snapshot equivalence, or exact equality.

## Necessity approximation

For finite witness suites, removing a required obligation should make at least one observation fail.

## Obligation ledger coherence

Observations that refer to the same public fact agree after projection.

## Repair tests

For every no-exact-lift obstruction, add a failing test first and a repair acceptance test after enriching B, changing P, or weakening F.
OUT
    ;;
  no-exact-lift|obstruction)
    cat <<OUT
# No-exact-lift law-test plan (${language})

## Obstruction witness

Choose one case a and observation obs such that F(a) requires behavior P cannot produce from current B.

Test:

assertNoExactLift(a, obs)

## Report completeness

The obstruction report must name:
- required observation;
- current projection result;
- missing data / transition / capability / temporal guarantee / projection path;
- repair options;
- approximation status.

## Repair law

After repair, the original projection law must pass:

observe(P(L(a)), obs) == observe(F(a), obs)
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
