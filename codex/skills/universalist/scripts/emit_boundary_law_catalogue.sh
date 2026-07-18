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
  day-convolution|day) echo 'Day laws: represent(a) star represent(b) ~= represent(a tensor b); unit/associativity, complete legal decompositions, quotient coherence, interpretation, and effectivity' ;;
  promonoidal-convolution|promonoidal) echo 'Promonoidal law: only explicit admissibility witnesses Compose(a,b;c) contribute; incompatible pairs fail closed and witness provenance is preserved' ;;
  tambara-module|contextual-morphism) echo 'Tambara laws: frame_I(p) ~= p; frame_(m tensor n)(p) ~= frame_m(frame_n(p)); endpoint naturality/context coherence; interpretation preserves framing' ;;
  mixed-tambara|mixed-optic) echo 'Mixed Tambara law: separate source and target actions frame one profunctor coherently and preserve declared observations' ;;
  optic|optic-tambara) echo 'Optic law: interpretOptic(m,decompose,rebuild,p) == dimap(decompose,rebuild,frame_m(p)); residual reindexing is quotiented and domain optic laws remain separate' ;;
  free-tambara) echo 'Free Tambara law: every supported legal frame of a generator is represented once modulo coherent context reindexing and interprets like direct framing' ;;
  cofree-tambara) echo 'Cofree Tambara law: every supported frame is observed coherently with identity and nested-context laws' ;;
  dependent-tambara) echo 'Dependent Tambara law: index-changing context transport composes horizontally and rejects invalid dependent frames' ;;
  tambara-representability) echo 'Tambara representability law: generalized morphism round-trips through a concrete context-preserving module functor/realizer; otherwise return obstruction' ;;
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
Day convolution: representable/unit/associativity, legal decomposition, quotient, interpretation, and effectivity laws
Promonoidal convolution: explicit admissibility witnesses and closed failure for incompatible pairs
Tambara module: identity/nested framing, endpoint naturality, context coherence, interpretation, and resource laws
Mixed Tambara: separate endpoint actions frame one profunctor coherently
Optic: residual decompose/rebuild interpretation plus separate domain optic laws
Free/cofree Tambara: effective contextual closure/all-context observation
Dependent Tambara: index-changing context transport remains typed and coherent
Tambara representability: concrete module functor/realizer or explicit obstruction
Behavioral coalgebra: observe(step(state,input)) satisfies protocol trace expectations
Comonadic spatiality: center, nested-neighborhood coherence, germ restriction, halo/label continuity, and resource laws
Basis density: supported situated objects reconstruct canonically from basic patches
Generation: lowerGenerated(payload,path) == directInterpret(path,payload)
Observation: runObservation(obs,repack(subject)) == runObservation(obs,subject)
Defunctionalization: apply(encodedCase,x) == oldFunction(x)
OUT
    ;;
esac
