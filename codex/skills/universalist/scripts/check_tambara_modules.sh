#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

required=(
  references/contextual-morphism-doctrine.md
  references/mechanics/tambara-modules.md
  templates/mechanics/tambara-module-report.md
  scripts/emit_tambara_module.sh
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

require_text references/contextual-morphism-doctrine.md "Contexts act."
require_text references/contextual-morphism-doctrine.md "Morphisms frame."
require_text references/contextual-morphism-doctrine.md "Tambara laws certify the framing."
require_text references/contextual-morphism-doctrine.md "Do not thread context ad hoc"
require_text references/contextual-morphism-doctrine.md "equivariant Tambara functors"
require_text references/contextual-morphism-doctrine.md "Comonadic spatial interpretation"
require_text references/mechanics/tambara-modules.md "alpha_m : P(a,b) -> P(L(m,a), R(m,b))"
require_text references/mechanics/tambara-modules.md "Free contextual closure"
require_text references/mechanics/tambara-modules.md "Cofree / all-context observation"
require_text references/mechanics/tambara-modules.md "Profunctor representation theorem"
require_text references/mechanics/tambara-modules.md "Day convolution and the monoidal center"
require_text references/mechanics/tambara-modules.md "Representability diagnostic"
require_text references/mechanics/tambara-modules.md "Dependent Tambara modules"
require_text references/composition-geometry.md "Stage 3 — Context-action / contextual-morphism selector"
require_text references/composition-geometry.md "Tambara module"
require_text references/artifact-selection-by-unknown-location.md "Context-stable generalized morphism"
require_text references/boundary-law-catalogue.md "Tambara unit"
require_text references/category-pivot.md "context-action / Tambara world"
require_text references/effects-and-coalgebras.md "Context-stable profunctors / Tambara modules"
require_text references/exact-context-doctrine.md "Context-stable semantic capability"
require_text references/possibility-sheafification.md "Tambara framing preserves a local transformation under context action."
require_text references/presentation-strategies.md "Context action is a separate decision"
require_text references/mechanics/README.md "Tambara modules"
require_text references/sources.md "Doubles for monoidal categories"
require_text references/sources.md "Profunctor Optics: a Categorical Update"
require_text references/sources.md "Module categories, internal bimodules and Tambara modules"
require_text templates/composition-certificate.md "## Context action / Tambara structure"
require_text templates/category-pivot-certificate.md "## Context action / Tambara structure"
require_text templates/context-certificate.md "## Context-stable capability"
require_text templates/effective-universal-architecture-certificate.md "## Context actions and Tambara modules"
require_text templates/universalist-plan.md "## Context action / Tambara module:"
require_text scripts/emit_mechanics_report.sh "tambara-module"
require_text scripts/emit_mechanics_report.sh "mixed-optic"
require_text scripts/emit_mechanics_report.sh "free-tambara"
require_text scripts/emit_mechanics_report.sh "dependent-tambara"
require_text scripts/emit_mechanics_report.sh "day-center-tambara"
require_text tests/golden/output-invariants.yml "tambara_module_requires_real_context_action"
require_text tests/golden/output-invariants.yml "tambara_framing_does_not_imply_effect_commutativity"
require_text tests/golden/activation.yml "same validator through tenant, evidence, and capability wrappers"
require_text package.json '"version": "16.3.0"'

for agent in \
  ../../agents/universalist-world-cartographer.toml \
  ../../agents/universalist-categorical-architect.toml \
  ../../agents/universalist-semanticist.toml \
  ../../agents/universalist-resource-realist.toml \
  ../../agents/universalist-proof-auditor.toml \
  ../../agents/universalist-witness-implementer.toml \
  ../../agents/universalist-verifier.toml; do
  require_text "$agent" "Tambara"
done

bash -n scripts/emit_tambara_module.sh
bash -n scripts/emit_mechanics_report.sh
bash -n scripts/emit_boundary_law_catalogue.sh
bash -n scripts/emit_canonical_artifact_plan.sh
bash -n scripts/emit_composition_certificate.sh
bash -n scripts/emit_context_certificate.sh
bash -n scripts/emit_effective_universal_architecture.sh
bash -n scripts/emit_universalist_team_prompt.sh

bash scripts/emit_tambara_module.sh module agnostic >/dev/null
bash scripts/emit_tambara_module.sh mixed typescript >/dev/null
bash scripts/emit_tambara_module.sh optic typescript >/dev/null
bash scripts/emit_tambara_module.sh free agnostic >/dev/null
bash scripts/emit_tambara_module.sh cofree agnostic >/dev/null
bash scripts/emit_tambara_module.sh dependent agnostic >/dev/null
bash scripts/emit_tambara_module.sh center agnostic >/dev/null
bash scripts/emit_tambara_module.sh representable agnostic >/dev/null
bash scripts/emit_tambara_module.sh compare agnostic >/dev/null
bash scripts/emit_mechanics_report.sh tambara-module agnostic >/dev/null
bash scripts/emit_mechanics_report.sh mixed-optic typescript >/dev/null
bash scripts/emit_mechanics_report.sh free-tambara agnostic >/dev/null
bash scripts/emit_mechanics_report.sh dependent-tambara agnostic >/dev/null
bash scripts/emit_mechanics_report.sh day-center-tambara agnostic >/dev/null
bash scripts/emit_boundary_law_catalogue.sh tambara-module >/dev/null
bash scripts/emit_canonical_artifact_plan.sh tambara-module typescript >/dev/null
bash scripts/emit_composition_certificate.sh contextual-morphism typescript >/dev/null
bash scripts/emit_context_certificate.sh framed-context agnostic >/dev/null
bash scripts/emit_effective_universal_architecture.sh tambara typescript >/dev/null
bash scripts/emit_universalist_team_prompt.sh tambara >/dev/null

if bash scripts/emit_tambara_module.sh nonsense agnostic >/dev/null 2>&1; then
  echo "unknown Tambara mode must fail" >&2
  exit 1
fi

if bash scripts/emit_mechanics_report.sh tambara agnostic >/dev/null 2>&1; then
  echo "bare tambara mechanics topic must be rejected as ambiguous" >&2
  exit 1
fi

echo "check_tambara_modules: ok"
