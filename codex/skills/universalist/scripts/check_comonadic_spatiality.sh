#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

require_text() {
  local path="$1" text="$2"
  grep -Fq "$text" "$path" || { echo "$path missing: $text" >&2; exit 1; }
}

for path in references/comonadic-spatiality-doctrine.md references/mechanics/comonads-as-spaces.md scripts/emit_comonadic_spatiality.sh templates/mechanics/comonadic-spatiality-report.md; do
  test -f "$path" || { echo "missing $path" >&2; exit 1; }
done
require_text package.json '"version": "17.0.0"'
require_text references/comonadic-spatiality-doctrine.md 'density-Day comparison map'
require_text references/comonadic-spatiality-doctrine.md 'shared/product index world'
require_text tests/golden/output-invariants.yml 'comonadic_spatiality_requires_locality_laws'
require_text tests/golden/output-invariants.yml 'spatial_convolution_requires_shared_product_index'

bash -n scripts/emit_comonadic_spatiality.sh
bash scripts/emit_comonadic_spatiality.sh space agnostic >/dev/null
bash scripts/emit_comonadic_spatiality.sh density agnostic >/dev/null
bash scripts/emit_comonadic_spatiality.sh halo typescript >/dev/null
bash scripts/emit_comonadic_spatiality.sh continuous agnostic >/dev/null
./scripts/emit_mechanics_report.sh comonad-space agnostic >/dev/null
./scripts/emit_mechanics_report.sh density-comonad agnostic >/dev/null
./scripts/emit_mechanics_report.sh continuous-comonad-map agnostic >/dev/null

echo "check_comonadic_spatiality: ok"
