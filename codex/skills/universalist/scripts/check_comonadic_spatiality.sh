#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

required=(
  references/comonadic-spatiality-doctrine.md
  references/mechanics/comonads-as-spaces.md
  templates/mechanics/comonadic-spatiality-report.md
  scripts/emit_comonadic_spatiality.sh
  templates/context-certificate.md
  templates/composition-certificate.md
  tests/golden/activation.yml
  tests/golden/output-invariants.yml
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
require_text references/universal-architecture-kernel.md "Comonadic spatiality"
require_text references/universal-architecture-ecosystem.md "Continuous comonadic map"
require_text references/effective-universal-architecture-thesis.md "effective locality when semantic"
require_text scripts/emit_mechanics_report.sh "comonad-space"
require_text scripts/emit_mechanics_report.sh "density-comonad"
require_text scripts/emit_mechanics_report.sh "continuous-comonad-map"
require_text references/sources.md "Comonads as Spaces"
require_text references/decision-contract.yaml "comonad density halo"
require_text templates/composition-certificate.md "## Spatial geometry"
require_text templates/context-certificate.md "## Spatial locality"
require_text templates/universalist-plan.md "## Spatial geometry / halo:"
require_text tests/golden/activation.yml "compute its dependency, ownership, test, and provenance neighborhood"
require_text tests/golden/output-invariants.yml "comonadic_spatiality_requires_locality_laws"
require_text ../../agents/universalist-world-cartographer.toml "representative halos"
require_text ../../agents/universalist-categorical-architect.toml "comonads as spaces"
require_text ../../agents/universalist-semanticist.toml "comonad coalgebras"
require_text ../../agents/universalist-proof-auditor.toml "point preservation as continuity"
require_text ../../agents/universalist-resource-realist.toml "basis explosion"
require_text ../../agents/universalist-verifier.toml "bounded halo"
require_text package.json '"version": "16.1.0"'

bash -n scripts/emit_comonadic_spatiality.sh
bash -n scripts/emit_mechanics_report.sh
bash -n scripts/emit_context_certificate.sh
bash -n scripts/emit_composition_certificate.sh
bash -n scripts/emit_boundary_law_catalogue.sh
bash -n scripts/emit_effective_universal_architecture.sh
bash -n scripts/emit_universalist_team_prompt.sh
bash scripts/emit_comonadic_spatiality.sh space agnostic >/dev/null
bash scripts/emit_comonadic_spatiality.sh density agnostic >/dev/null
bash scripts/emit_comonadic_spatiality.sh halo typescript >/dev/null
bash scripts/emit_comonadic_spatiality.sh continuous agnostic >/dev/null
bash scripts/emit_comonadic_spatiality.sh compare agnostic >/dev/null
bash scripts/emit_mechanics_report.sh comonad-space agnostic >/dev/null
bash scripts/emit_mechanics_report.sh density-comonad agnostic >/dev/null
bash scripts/emit_mechanics_report.sh halo typescript >/dev/null
bash scripts/emit_mechanics_report.sh continuous-comonad-map agnostic >/dev/null
bash scripts/emit_context_certificate.sh spatial-context agnostic >/dev/null
bash scripts/emit_composition_certificate.sh locality-boundary agnostic >/dev/null
bash scripts/emit_boundary_law_catalogue.sh comonadic-spatiality >/dev/null
bash scripts/emit_boundary_law_catalogue.sh continuous-comonad-map >/dev/null
bash scripts/emit_effective_universal_architecture.sh spatial-system agnostic >/dev/null
bash scripts/emit_universalist_team_prompt.sh spatial >/dev/null

if bash scripts/emit_comonadic_spatiality.sh nonsense agnostic >/dev/null 2>&1; then
  echo "unknown comonadic spatiality mode must fail" >&2
  exit 1
fi

echo "check_comonadic_spatiality: ok"