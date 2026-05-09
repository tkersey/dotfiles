#!/usr/bin/env bash
set -euo pipefail
kind="${1:-coproduct}"
language="${2:-agnostic}"
case "$kind" in
  product) body="construct and project fields consistently" ;;
  coproduct) body="invalid states rejected; all cases handled exhaustively" ;;
  refined|equalizer) body="valid accepted, invalid rejected, normalization idempotent" ;;
  pullback) body="matching inputs accepted, mismatches rejected, projections preserved" ;;
  exponential) body="strategy parity with old branch fixtures" ;;
  free|initial-algebra) body="new interpreter matches old evaluator on corpus" ;;
  universal-architecture|track-d) body="artifact-specific law plus one negative witness" ;;
  freyd|aft|free-builder) body="project(free(required(case))) satisfies required(case), or obstruction is named" ;;
  *) body="state the law and one falsifier" ;;
esac
cat <<OUT
# Law-test stub: ${kind} (${language})

## Law
${body}

## Positive witness

## Negative witness

## Bypass / centralization check

## Verification command
OUT
