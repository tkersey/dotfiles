#!/usr/bin/env bash
set -euo pipefail
kind="${1:-all}"
case "$kind" in
  embedding) echo 'Embedding -> Lan/Ran/Delta; law: new(embed(old)) == old(old)' ;;
  projection) echo 'Projection -> Kan lift/P_*/Freyd; law: observe(P(internal)) == required' ;;
  forgetful) echo 'Forgetful -> adjunction/free builder; law: forget(free(raw)) satisfies raw behavior' ;;
  interpreter) echo 'Interpreter -> algebra/fold/handler; law: interpret syntax agrees with fixtures' ;;
  compiler|lowering) echo 'Compiler/lowering -> transported semantics/Coyoneda; law: lowering preserves semantics' ;;
  serializer) echo 'Serializer -> projection/restriction/lift obstruction; law: round-trip preserves invariants' ;;
  view|query) echo 'View/query -> Ran/Yoneda; law: overlapping observations commute' ;;
  handler) echo 'Handler -> free effects/defunctionalized ops; law: handler satisfies observations' ;;
  observer) echo 'Observer -> Yoneda/Ran/Rft; law: representation change preserves observation' ;;
  migration) echo 'Migration -> Delta/Lan/Ran; law: old reports pass through migration' ;;
  *) cat <<'OUT'
Embedding -> Lan/Ran/Delta
Projection -> Kan lift/P_*/Freyd diagnostic
Forgetful -> adjunction/free builder
Interpreter -> algebra/fold/handler
Compiler/lowering -> transported semantics/Coyoneda
Serializer -> projection/restriction/lift obstruction
View/query -> Ran/Yoneda
Handler -> free effects/defunctionalized operations
Observer -> Yoneda/Ran/Rft
Migration -> Delta/Lan/Ran
OUT
    ;;
esac
