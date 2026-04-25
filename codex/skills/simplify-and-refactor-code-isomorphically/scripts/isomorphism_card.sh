#!/usr/bin/env bash
# Emit a blank isomorphism card template for a candidate.
#
# Usage:  ./isomorphism_card.sh <candidate-id> [run-id]
# Output: refactor/artifacts/<run-id>/cards/<candidate-id>.md

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <candidate-id> [run-id]" >&2
  exit 1
fi

ID="$1"
RUN_ID="${2:-$(date +%Y-%m-%d)-pass-1}"
ART="refactor/artifacts/${RUN_ID}"
mkdir -p "${ART}/cards"

OUT="${ART}/cards/${ID}.md"
if [[ -e "${OUT}" ]]; then
  echo "Card already exists: ${OUT}" >&2
  exit 1
fi

{
printf '# Card %s — <one-line description>\n\n' "${ID}"
cat <<'EOF'

> Fill EVERY row before editing. "I don't know" → write a property test first.

## Equivalence contract

- **Inputs covered:**          [callers + tests touched]
- **Ordering preserved:**      [yes/no + why]
- **Tie-breaking:**            [unchanged/N/A]
- **Error semantics:**         [same Err variants under same conditions]
- **Error vs panic:**          [unchanged]
- **Laziness:**                [unchanged/forced]
- **Short-circuit eval:**      [unchanged]
- **Floating-point:**          [bit-identical/N/A]
- **Integer overflow:**        [unchanged]
- **RNG / hash order:**        [unchanged/N/A]
- **Side-effects (logs/metrics/spans/DB writes):** [identical order + payload]
- **Side-effect cardinality:** [N writes still N writes]
- **Async / Future identity:** [cancellation, drop order unchanged]
- **Type narrowing:**          [TS/Rust — narrowing preserved]
- **Public API / ABI / FFI:**  [unchanged or document break]
- **Compile-time guarantees:** [no looser bounds]
- **React semantics:**         [N/A or hook-order/memo-keys/Suspense unchanged]
- **Serialization:**           [wire format identical]
- **Concurrency:**             [no new shared state, lock order unchanged]
- **Resource lifecycle:**      [Drop / __del__ / defer order unchanged]
- **Telemetry:**               [span names, trace IDs unchanged]

## Predicted ΔLOC

- Before: ___ lines
- After:  ___ lines (estimate)
- Δ:      ___ lines

## Verification (run after edit)

- [ ] tests/0 mismatch with baseline → FAIL
- [ ] sha256sum -c goldens/checksums.txt → must succeed
- [ ] source-line delta within ±10% of prediction (`loc_delta.sh`)
- [ ] lint warnings count NOT > baseline
- [ ] no new `#[allow]` / `// eslint-disable` / `# noqa` / `# type: ignore`
EOF
} > "${OUT}"

echo "Card scaffold written: ${OUT}"
echo "Fill EVERY row before editing code. If a row is genuinely N/A, say why."
