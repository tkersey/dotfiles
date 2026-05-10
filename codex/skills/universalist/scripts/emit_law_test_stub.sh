#!/usr/bin/env bash
set -euo pipefail
kind="${1:-coproduct}"
language="${2:-agnostic}"
case "$kind" in
  product)
    echo "# Product law test (${language})"; echo "construct -> project fields consistently" ;;
  coproduct)
    echo "# Coproduct law test (${language})"; echo "exhaustive handling; invalid legacy shapes rejected" ;;
  refined|equalizer)
    echo "# Refined type/equalizer law test (${language})"; echo "valid accepted; invalid rejected; normalization idempotent" ;;
  pullback)
    echo "# Pullback law test (${language})"; echo "matching inputs accepted; mismatches rejected; projections preserved" ;;
  exponential|strategy)
    echo "# Exponential/strategy law test (${language})"; echo "strategy parity with old branch fixtures" ;;
  free|free-syntax|initial-algebra)
    echo "# Free syntax law test (${language})"; echo "old evaluator and new interpreter match on corpus" ;;
  universal-architecture)
    cat <<OUT
# Universal architecture law test (${language})

Name:
- canonical artifact:
- boundary:
- witness:

Positive law:
- expected commuting/projection/observation/lowering behavior:

Negative witness:
- invalid state/path/obligation/handler/callback:
OUT
    ;;
  lifted-implementation|lift|kan-lift)
    echo "# Lifted implementation law test (${language})"; echo "project(realize(case)) == required(case)" ;;
  free-builder|freyd)
    echo "# Free builder law test (${language})"; echo "project(free(required(case))) satisfies required(case) or reports obstruction" ;;
  obstruction|obstruction-report)
    echo "# Obstruction report law test (${language})"; echo "required behavior fails for named evidence/template/constraint reason" ;;
  residual|obligation|rift)
    echo "# Residual obligation law test (${language})"; echo "missing obligation fails; satisfying obligations passes" ;;
  behavioral-coalgebra|coalgebra|protocol|state-machine)
    cat <<OUT
# Behavioral coalgebra law test (${language})

Given:
- State
- Input
- step : State × Input -> State
- observe : State -> ObservationResult

Positive:
trace(step, observe, initial, inputs) == expectedTrace

Negative:
invalid transition rejected
states claimed equivalent produce equivalent observations
OUT
    ;;
  effect-handler|effects|algebraic-effects)
    cat <<OUT
# Effect signature / handler law test (${language})

Given:
- Operation
- Program
- handleTest
- handleProd
- observeProd

Positive:
handleTest(program) == expectedFixture
observeProd(handleProd(program)) == expectedObservation

Negative:
missing operation handler fails
handler mismatch must be explained by explicit observation law
OUT
    ;;
  yoneda|observation)
    echo "# Yoneda observation law test (${language})"; echo "runObservation(obs, repack(subject)) == runObservation(obs, subject)" ;;
  coyoneda|generation)
    echo "# Coyoneda generation law test (${language})"; echo "lowerGenerated({payload,path}) == directInterpret(path,payload)" ;;
  defunctionalization|explicit-ir)
    echo "# Defunctionalized IR law test (${language})"; echo "apply(encodedCase, x) == oldFunction(x)" ;;
  *) echo "unknown law-test kind: $kind" >&2; exit 2 ;;
esac
