#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

required=(
  references/description-composition-doctrine.md
  references/mechanics/day-convolution.md
  templates/mechanics/day-convolution-report.md
  scripts/emit_day_convolution.sh
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

require_text references/description-composition-doctrine.md "Indices compose."
require_text references/description-composition-doctrine.md "Descriptions convolve."
require_text references/description-composition-doctrine.md "Index composition before description composition."
require_text references/description-composition-doctrine.md "Density generates locality."
require_text references/mechanics/day-convolution.md "F star G = Lan_tensor(F external-product G)"
require_text references/mechanics/day-convolution.md "y(a) star y(b) ~= y(a tensor b)"
require_text references/mechanics/day-convolution.md "Promonoidal generalization"
require_text references/mechanics/day-convolution.md "coend"
require_text references/mechanics/day-convolution.md "Do not assume convolution preserves monomorphisms"
require_text references/composition-geometry.md "Description-product selector"
require_text references/composition-geometry.md "Day convolution"
require_text references/artifact-selection-by-unknown-location.md "Indexed descriptions over a tensor"
require_text references/boundary-law-catalogue.md "Day representable"
require_text references/category-pivot.md "functor / presheaf category"
require_text references/effects-and-coalgebras.md "Applicative / Day"
require_text references/comonadic-spatiality-doctrine.md "Day convolution composes locality."
require_text references/exact-context-doctrine.md "Requirement-indexed convolution"
require_text references/possibility-sheafification.md "Convolution composes indexed descriptions"
require_text references/presentation-strategies.md "Description composition"
require_text references/mechanics/README.md "Day convolution"
require_text references/sources.md "On closed categories of functors"
require_text references/sources.md "Day algebras"
require_text templates/composition-certificate.md "## Description composition"
require_text templates/category-pivot-certificate.md "## Description composition"
require_text templates/context-certificate.md "## Requirement-indexed composition"
require_text templates/effective-universal-architecture-certificate.md "Description composition"
require_text templates/universalist-plan.md "## Description composition:"
require_text scripts/emit_mechanics_report.sh "day-convolution"
require_text scripts/emit_mechanics_report.sh "promonoidal-convolution"
require_text scripts/emit_mechanics_report.sh "applicative-convolution"
require_text scripts/emit_mechanics_report.sh "resource-convolution"
require_text scripts/emit_mechanics_report.sh "spatial-convolution"
require_text tests/golden/output-invariants.yml "day_convolution_requires_index_tensor"
require_text tests/golden/output-invariants.yml "applicative_structure_does_not_imply_effect_commutativity"
require_text tests/golden/activation.yml "manual nested loops over all grade decompositions"
require_text package.json '"version": "16.3.0"'

for agent in \
  ../../agents/universalist-world-cartographer.toml \
  ../../agents/universalist-categorical-architect.toml \
  ../../agents/universalist-semanticist.toml \
  ../../agents/universalist-resource-realist.toml \
  ../../agents/universalist-proof-auditor.toml \
  ../../agents/universalist-witness-implementer.toml \
  ../../agents/universalist-verifier.toml; do
  require_text "$agent" "description composition"
done

bash -n scripts/emit_day_convolution.sh
bash -n scripts/emit_mechanics_report.sh
bash -n scripts/emit_boundary_law_catalogue.sh
bash -n scripts/emit_canonical_artifact_plan.sh
bash -n scripts/emit_composition_certificate.sh
bash -n scripts/emit_context_certificate.sh
bash -n scripts/emit_effective_universal_architecture.sh
bash -n scripts/emit_universalist_team_prompt.sh

bash ./scripts/emit_day_convolution.sh day agnostic >/dev/null
bash ./scripts/emit_day_convolution.sh promonoidal agnostic >/dev/null
bash ./scripts/emit_day_convolution.sh applicative typescript >/dev/null
bash ./scripts/emit_day_convolution.sh resource agnostic >/dev/null
bash ./scripts/emit_day_convolution.sh spatial agnostic >/dev/null
bash ./scripts/emit_day_convolution.sh compare agnostic >/dev/null
./scripts/emit_mechanics_report.sh day-convolution agnostic >/dev/null
./scripts/emit_mechanics_report.sh promonoidal-convolution agnostic >/dev/null
./scripts/emit_mechanics_report.sh applicative-convolution typescript >/dev/null
./scripts/emit_mechanics_report.sh resource-convolution agnostic >/dev/null
./scripts/emit_mechanics_report.sh spatial-convolution agnostic >/dev/null
./scripts/emit_boundary_law_catalogue.sh day-convolution >/dev/null
./scripts/emit_canonical_artifact_plan.sh day-convolution typescript >/dev/null
./scripts/emit_composition_certificate.sh indexed-description typescript >/dev/null
./scripts/emit_context_certificate.sh requirement-indexed agnostic >/dev/null
./scripts/emit_effective_universal_architecture.sh convolution typescript >/dev/null
./scripts/emit_universalist_team_prompt.sh convolution >/dev/null

if bash ./scripts/emit_day_convolution.sh nonsense agnostic >/dev/null 2>&1; then
  echo "unknown Day convolution mode must fail" >&2
  exit 1
fi

if ./scripts/emit_mechanics_report.sh convolution agnostic >/dev/null 2>&1; then
  echo "bare convolution mechanics topic must be rejected as ambiguous" >&2
  exit 1
fi

echo "check_day_convolution: ok"
