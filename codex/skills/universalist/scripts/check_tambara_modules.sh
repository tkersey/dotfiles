#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

require_text() {
  local path="$1" text="$2"
  grep -Fq "$text" "$path" || { echo "$path missing: $text" >&2; exit 1; }
}

for path in references/contextual-morphism-doctrine.md references/mechanics/tambara-modules.md scripts/emit_tambara_module.sh templates/mechanics/tambara-module-report.md; do
  test -f "$path" || { echo "missing $path" >&2; exit 1; }
done
require_text package.json '"version": "17.0.0"'
grep -R -Fq 'expert_name: Tambara module' references/universal-constructions || { echo 'theorem cards missing: Tambara module' >&2; exit 1; }
require_text tests/golden/output-invariants.yml 'tambara_module_requires_real_context_action'
require_text tests/golden/output-invariants.yml 'tambara_framing_does_not_imply_effect_commutativity'

bash -n scripts/emit_tambara_module.sh
for mode in ordinary mixed optic free cofree dependent day-center representability; do
  bash scripts/emit_tambara_module.sh "$mode" agnostic >/dev/null
done
for topic in tambara-module mixed-optic optic-tambara free-tambara cofree-tambara dependent-tambara day-center-tambara tambara-representability; do
  ./scripts/emit_mechanics_report.sh "$topic" agnostic >/dev/null
done
if ./scripts/emit_mechanics_report.sh tambara agnostic >/dev/null 2>&1; then
  echo "bare tambara topic must fail as ambiguous" >&2
  exit 1
fi

echo "check_tambara_modules: ok"
