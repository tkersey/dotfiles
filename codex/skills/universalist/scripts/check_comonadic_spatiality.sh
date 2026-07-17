#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

required=(
  references/comonadic-spatiality-doctrine.md
  references/mechanics/comonads-as-spaces.md
  templates/mechanics/comonadic-spatiality-report.md
  scripts/emit_comonadic_spatiality.sh
)

for path in "${required[@]}"; do
  test -f "$path" || { echo "missing $path" >&2; exit 1; }
done

require_text() {
  local path="$1"
  local text="$2"
  grep -Fq "$text" "$path" || {
    echo "$path missing required text: $text" >&2
    exit 1
  }
}

require_text references/comonadic-spatiality-doctrine.md "Worlds have halos."
require_text references/comonadic-spatiality-doctrine.md "Context is a germ."
require_text references/comonadic-spatiality-doctrine.md "Boundaries preserve locality."
require_text references/comonadic-spatiality-doctrine.md "Not every comonad is a topological space."
require_text references/mechanics/comonads-as-spaces.md "<P> = Lan_P P"
require_text references/mechanics/comonads-as-spaces.md "ordinary comonad map != continuous map"
require_text references/mechanics/comonads-as-spaces.md "local point"
require_text references/mechanics/comonads-as-spaces.md "Labelled halos"
require_text references/mechanics/comonads-as-spaces.md "basis supports canonical reconstruction"
require_text references/presentation-strategies.md "Density-comonadic spatial presentation"
require_text references/exact-context-doctrine.md "Context as a germ"
require_text references/possibility-sheafification.md "Density generates locality"
require_text references/mechanics/README.md "Comonads as spaces"
require_text scripts/emit_mechanics_report.sh "comonad-space"
require_text scripts/emit_mechanics_report.sh "density-comonad"
require_text scripts/emit_mechanics_report.sh "continuous-comonad-map"
require_text references/sources.md "Comonads as Spaces"
require_text templates/composition-certificate.md "## Spatial geometry"
require_text templates/context-certificate.md "## Spatial locality"
require_text templates/universalist-plan.md "## Spatial geometry / halo:"
require_text tests/golden/output-invariants.yml "comonadic_spatiality_requires_locality_laws"

bash -n scripts/emit_comonadic_spatiality.sh
bash -n scripts/emit_mechanics_report.sh
./scripts/emit_comonadic_spatiality.sh space agnostic >/dev/null
./scripts/emit_comonadic_spatiality.sh density agnostic >/dev/null
./scripts/emit_comonadic_spatiality.sh halo typescript >/dev/null
./scripts/emit_comonadic_spatiality.sh continuous agnostic >/dev/null
./scripts/emit_comonadic_spatiality.sh compare agnostic >/dev/null
./scripts/emit_mechanics_report.sh comonad-space agnostic >/dev/null
./scripts/emit_mechanics_report.sh density-comonad agnostic >/dev/null
./scripts/emit_mechanics_report.sh halo typescript >/dev/null
./scripts/emit_mechanics_report.sh continuous-comonad-map agnostic >/dev/null

if ./scripts/emit_comonadic_spatiality.sh nonsense agnostic >/dev/null 2>&1; then
  echo "unknown comonadic spatiality mode must fail" >&2
  exit 1
fi

echo "check_comonadic_spatiality: ok"