#!/usr/bin/env bash
set -euo pipefail
kind="${1:-all}"
case "$kind" in
  embedding) echo 'Embedding law: new(embed(old)) == old(old)' ;;
  projection) echo 'Projection law: observe(project(internal)) == expectedPublicBehavior' ;;
  forgetful) echo 'Forgetful law: forget(combineRich(a,b)) == combineRaw(forget(a),forget(b))' ;;
  interpreter) echo 'Interpreter law: interpret(translate(syntax)) == oldBehavior(syntax)' ;;
  serializer) echo 'Serializer law: decode(encode(internal)) preserves public invariants' ;;
  migration) echo 'Migration law: oldReport(old) == oldReport(restrict(migrate(old)))' ;;
  handler) echo 'Handler law: run(handler(program)) satisfies operation observations' ;;
  freyd-category) echo 'Freyd effect-order law: pure embedding preserves identity/composition; reorder only with observational commutativity' ;;
  operad) echo 'Operadic substitution law: interpret(substitute(f,g1,...,gn)) == compose(interpret(f),interpret(g1),...,interpret(gn))' ;;
  coalgebra) echo 'Coalgebra law: observe(step(state,input)) satisfies protocol trace expectations' ;;
  generation) echo 'Generation law: lowerGenerated(payload,path) == directInterpret(path,payload)' ;;
  observation) echo 'Observation law: runObservation(obs,repack(subject)) == runObservation(obs,subject)' ;;
  defunctionalization) echo 'Defunctionalization law: apply(encodedCase,x) == oldFunction(x)' ;;
  *) cat <<'OUT'
Embedding: new(embed(old)) == old(old)
Projection: observe(project(internal)) == expectedPublicBehavior
Forgetful: forget(combineRich(a,b)) == combineRaw(forget(a),forget(b))
Interpreter: interpret(translate(syntax)) == oldBehavior(syntax)
Serializer: decode(encode(internal)) preserves public invariants
Migration: oldReport(old) == oldReport(restrict(migrate(old)))
Handler: run(handler(program)) satisfies operation observations
Freyd category: pure embedding preserves identity/composition; reorder only with observational commutativity
Operad: interpret(substitute(f,g1,...,gn)) == compose(interpret(f),interpret(g1),...,interpret(gn))
Coalgebra: observe(step(state,input)) satisfies protocol trace expectations
Generation: lowerGenerated(payload,path) == directInterpret(path,payload)
Observation: runObservation(obs,repack(subject)) == runObservation(obs,subject)
Defunctionalization: apply(encodedCase,x) == oldFunction(x)
OUT
    ;;
esac
