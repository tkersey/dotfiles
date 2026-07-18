#!/usr/bin/env bash
set -euo pipefail
kind="${1:-all}"
case "$kind" in
  embedding) echo 'Embedding law: new(embed(old)) == old(old)' ;;
  projection) echo 'Projection law: observe(project(internal)) == expectedPublicBehavior' ;;
  forgetful) echo 'Forgetful law: forget(combineRich(a,b)) == combineRaw(forget(a),forget(b))' ;;
  pullback) echo 'Pullback law: f(projectA(p)) == g(projectB(p)); every compatible pair factors uniquely through the canonical witness' ;;
  pushout) echo 'Pushout law: injectA(includeA(o)) == injectB(includeB(o)); every compatible pair of consumers factors uniquely through the integrated artifact' ;;
  double-pushout|dpo) echo 'Double-pushout law: preserved interface survives; delete/add squares commute; rewrite is rejected when the pushout complement does not exist' ;;
  interpreter) echo 'Interpreter law: interpret(translate(syntax)) == oldBehavior(syntax)' ;;
  serializer) echo 'Serializer law: decode(encode(internal)) preserves public invariants' ;;
  migration) echo 'Migration law: oldReport(old) == oldReport(restrict(migrate(old)))' ;;
  handler) echo 'Handler law: run(handler(program)) satisfies operation observations' ;;
  freyd-category) echo 'Freyd effect-order law: pure embedding preserves identity/composition; reorder only with observational commutativity' ;;
  operad) echo 'Operadic substitution law: interpret(substitute(f,g1,...,gn)) == compose(interpret(f),interpret(g1),...,interpret(gn))' ;;
  day-convolution|day) echo 'Day laws: represent(a) star represent(b) ~= represent(a tensor b); unit/associativity; legal decompositions sound and complete; quotient and interpretation preserve observations' ;;
  promonoidal-convolution|promonoidal) echo 'Promonoidal law: every composite carries an explicit P(a,b;c) admissibility witness; incompatible pairs fail closed; witness provenance survives when observable' ;;
  applicative-convolution|applicative) echo 'Applicative/Day law: static description combination is lax monoidal; analysis and execution agree on declared structure; static shape does not imply effect commutativity' ;;
  resource-convolution|separation) echo 'Resource convolution law: only compatible splits contribute; the unit is neutral; residuals agree with the resource order; split enumeration stays within budget' ;;
  spatial-convolution) echo 'Spatial Day law: external-product patches generate the product description; projections preserve required halos, labels, identities, and restrictions within the resource bound' ;;
  coalgebra|behavioral-coalgebra) echo 'Behavioral coalgebra law: observe(step(state,input)) satisfies protocol trace expectations' ;;
  comonad-space|comonadic-spatiality) echo 'Comonadic spatiality laws: extract(localView(x)) == x; nested local views cohere; restriction preserves germ meaning; locality-sensitive boundaries preserve required halos and labels' ;;
  halo|labelled-halo) echo 'Halo law: the effective halo is centered, restriction-stable, label-preserving, and complete enough for required observations within its declared budget' ;;
  basis-density|density-comonad) echo 'Basis-density law: every supported situated object decomposes into basic patches and reconstructs canonically under required observations' ;;
  continuous-comonad-map|spatial-continuity) echo 'Spatial continuity law: point map plus context transport maps required source halos into target halos and preserves restrictions and required labels' ;;
  generation) echo 'Generation law: lowerGenerated(payload,path) == directInterpret(path,payload)' ;;
  observation) echo 'Observation law: runObservation(obs,repack(subject)) == runObservation(obs,subject)' ;;
  defunctionalization) echo 'Defunctionalization law: apply(encodedCase,x) == oldFunction(x)' ;;
  *) cat <<'OUT'
Embedding: new(embed(old)) == old(old)
Projection: observe(project(internal)) == expectedPublicBehavior
Forgetful: forget(combineRich(a,b)) == combineRaw(forget(a),forget(b))
Pullback: shared projections agree; every compatible pair factors through the canonical witness
Pushout: source injections agree on overlap; every compatible consumer pair factors through the integrated artifact
Double pushout: preserved interface survives and missing pushout complement blocks the rewrite
Interpreter: interpret(translate(syntax)) == oldBehavior(syntax)
Serializer: decode(encode(internal)) preserves public invariants
Migration: oldReport(old) == oldReport(restrict(migrate(old)))
Handler: run(handler(program)) satisfies operation observations
Freyd category: pure embedding preserves identity/composition; reorder only with observational commutativity
Operad: interpret(substitute(f,g1,...,gn)) == compose(interpret(f),interpret(g1),...,interpret(gn))
Day convolution: representables preserve tensor; unit/associativity; sound/complete decompositions; quotient and interpretation laws
Promonoidal convolution: every composite has an admissibility witness and incompatible pairs fail closed
Applicative/Day: static analysis and execution agree; static shape does not imply effect commutativity
Resource convolution: only compatible splits contribute and residual/resource laws hold
Spatial convolution: external-product patches preserve halos, labels, identities, restrictions, and resource bounds
Behavioral coalgebra: observe(step(state,input)) satisfies protocol trace expectations
Comonadic spatiality: center, nested-neighborhood coherence, germ restriction, halo/label continuity, and resource laws
Basis density: supported situated objects reconstruct canonically from basic patches
Generation: lowerGenerated(payload,path) == directInterpret(path,payload)
Observation: runObservation(obs,repack(subject)) == runObservation(obs,subject)
Defunctionalization: apply(encodedCase,x) == oldFunction(x)
OUT
    ;;
esac
