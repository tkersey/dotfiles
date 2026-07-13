#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

required=(
  references/mechanics/pullbacks-and-pushouts.md
  references/mechanics/pushout-reconciliation.md
  references/pushout-reconciliation.md
  templates/mechanics/pullback-pushout-report.md
  scripts/emit_pullback_pushout_report.sh
)

for f in "${required[@]}"; do
  test -f "$f" || { echo "missing $f" >&2; exit 1; }
done

for token in \
  'every compatible pair factors' \
  'pushout complement' \
  'double-pushout' \
  'Adhesive categories' \
  'A plain pair is not automatically a pullback' \
  'a plain merge is not automatically a pushout'
do
  grep -R -F "$token" references scripts templates >/dev/null || {
    echo "missing pullback/pushout doctrine token: $token" >&2
    exit 1
  }
done

bash scripts/emit_pullback_pushout_report.sh pullback typescript >/dev/null
bash scripts/emit_pullback_pushout_report.sh pushout agnostic >/dev/null
bash scripts/emit_pullback_pushout_report.sh dpo agnostic >/dev/null
bash scripts/emit_pullback_pushout_report.sh compare agnostic >/dev/null

./scripts/emit_mechanics_report.sh pullback typescript >/dev/null
./scripts/emit_mechanics_report.sh pushout agnostic >/dev/null
./scripts/emit_mechanics_report.sh pullback-pushout agnostic >/dev/null
./scripts/emit_mechanics_report.sh double-pushout agnostic >/dev/null

./scripts/emit_boundary_law_catalogue.sh pullback >/dev/null
./scripts/emit_boundary_law_catalogue.sh pushout >/dev/null
./scripts/emit_boundary_law_catalogue.sh double-pushout >/dev/null

echo "check_pullback_pushout_mechanics: ok"
