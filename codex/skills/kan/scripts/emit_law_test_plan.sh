#!/usr/bin/env bash
set -euo pipefail
direction="${1:-lan}"
language="${2:-agnostic}"
case "$direction" in
  lan) echo "Lan law (${language}): lan_map(K(f), eta(c,x)) == eta(c', F(f)(x))" ;;
  ran) echo "Ran law (${language}): F(f)(epsilon(c,family)) == epsilon(c', ran_map(K(f),family))" ;;
  delta) echo "Delta law (${language}): old golden tests pass through restriction" ;;
  lift|lft) echo "Lift law (${language}): project(realize(case)) == required(case)" ;;
  rift|residual) echo "Residual law (${language}): missing obligation fails; satisfying obligations passes" ;;
  freyd|free-builder) echo "Freyd/free-builder law (${language}): P(Free(required(case))) satisfies required behavior" ;;
  yoneda) echo "Yoneda law (${language}): runObservation(obs,repack(subject)) == runObservation(obs,subject)" ;;
  coyoneda) echo "Coyoneda law (${language}): lowerGenerated(payload,path) == directInterpret(path,payload)" ;;
  defun|defunctionalization) echo "Defunctionalization law (${language}): apply(encodedCase,x) == oldFunction(x)" ;;
  *) echo "Unknown direction: $direction" >&2; exit 2 ;;
esac
