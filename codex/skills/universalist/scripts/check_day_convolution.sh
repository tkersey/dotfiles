#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

require_text() {
  local path="$1" text="$2"
  grep -Fq "$text" "$path" || { echo "$path missing: $text" >&2; exit 1; }
}

for path in references/description-composition-doctrine.md references/mechanics/day-convolution.md scripts/emit_day_convolution.sh templates/mechanics/day-convolution-report.md; do
  test -f "$path" || { echo "missing $path" >&2; exit 1; }
done
require_text package.json '"version": "17.0.0"'
grep -R -Fq 'expert_name: Day convolution' references/universal-constructions || { echo 'theorem cards missing: Day convolution' >&2; exit 1; }
require_text tests/golden/output-invariants.yml 'day_convolution_requires_index_tensor'
require_text tests/golden/output-invariants.yml 'applicative_structure_does_not_imply_effect_commutativity'

bash -n scripts/emit_day_convolution.sh
for mode in day promonoidal applicative resource spatial compare; do
  bash scripts/emit_day_convolution.sh "$mode" agnostic >/dev/null
done
for topic in day-convolution promonoidal-convolution applicative-convolution resource-convolution spatial-convolution; do
  ./scripts/emit_mechanics_report.sh "$topic" agnostic >/dev/null
done
if ./scripts/emit_mechanics_report.sh convolution agnostic >/dev/null 2>&1; then
  echo "bare convolution topic must fail as ambiguous" >&2
  exit 1
fi

echo "check_day_convolution: ok"
