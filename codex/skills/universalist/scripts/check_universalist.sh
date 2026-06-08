#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"
required=(
  SKILL.md README.md package.json agents/openai.yaml
  references/universalist-overview.md references/discovery-signals.md references/language-encoding-matrix.md
  references/framework-boundaries.md references/cost-model-and-false-positives.md references/structures-and-laws.md
  references/testing-playbook.md references/migration-playbooks.md references/case-studies.md
  references/examples-haskell.md references/examples-go.md references/examples-typescript.md references/examples-python.md
  references/examples-java-kotlin.md references/examples-rust-swift.md references/sources.md
  references/universal-architecture-kernel.md references/universal-architecture-ecosystem.md
  references/artifact-selection-by-unknown-location.md references/canonical-boundary-artifacts.md
  references/world-boundary-inventory.md references/boundary-law-catalogue.md
  references/kan-boundaries-for-universalist.md references/freyd-aft-boundary-diagnostic.md
  references/effects-and-coalgebras.md references/yoneda-coyoneda-defunctionalization.md
  references/universal-architecture-law-tests.md references/universal-composition-doctrine.md
  references/composition-certificates.md references/boundary-normal-form.md
  references/presentation-strategies.md references/dense-dual-presentation.md references/semantic-compression.md
  references/exact-context-doctrine.md references/context-certificates.md references/context-normal-form.md references/semantic-consumption-boundaries.md references/verified-context-plane.md references/context-publication-boundaries.md references/cql-fit-assessment.md references/pushout-reconciliation.md references/context-provenance-manifest.md references/possibility-sheafification.md references/sheafification-certificates.md references/abstraction-normal-form.md references/abstraction-manipulator-playbook.md
  templates/universalist-plan.md templates/universalist-report.md templates/universal-architecture-report.md
  templates/freyd-boundary-diagnostic.md templates/world-boundary-inventory.md templates/composition-certificate.md
  templates/boundary-normal-form-report.md templates/presentation-diagnostic.md templates/context-certificate.md templates/context-normal-form-report.md templates/verified-context-plane-report.md templates/cql-fit-assessment.md templates/context-provenance-manifest.md templates/sheafification-certificate.md templates/abstraction-normal-form-report.md
  scripts/init_universalist_plan.sh scripts/detect_signals.py scripts/emit_scaffold.py scripts/emit_boundary_adapter.py
  scripts/emit_verification_plan.py scripts/emit_law_test_stub.sh scripts/emit_universal_artifact_matrix.sh
  scripts/emit_canonical_artifact_plan.sh scripts/emit_universal_architecture_prompt.sh scripts/emit_freyd_boundary_diagnostic.sh
  scripts/emit_world_boundary_inventory.sh scripts/emit_boundary_law_catalogue.sh scripts/emit_composition_certificate.sh
  scripts/emit_boundary_normal_form_plan.sh scripts/emit_presentation_diagnostic.sh scripts/emit_context_certificate.sh
  scripts/emit_context_compiler_plan.sh scripts/emit_exact_context_prompt.sh scripts/emit_verified_context_plane.sh scripts/emit_cql_fit_assessment.sh scripts/emit_context_publication_boundary.sh scripts/emit_possibility_sheafifier.sh scripts/emit_sheafification_certificate.sh scripts/emit_abstraction_normal_form_plan.sh
  references/mechanics/README.md references/mechanics/foundations.md references/mechanics/kan-lifts.md references/mechanics/freyd-aft.md
  references/mechanics/yoneda-coyoneda.md references/mechanics/codensity-presentations.md references/mechanics/defunctionalization.md
  references/mechanics/context-compilation.md references/mechanics/cql-context-management.md references/mechanics/possibility-sheafification-mechanics.md
  templates/mechanics-report.md templates/mechanics/codensity-presentation-report.md templates/mechanics/context-compilation-report.md templates/mechanics/sheafification-kan-report.md
  scripts/emit_mechanics_report.sh scripts/emit_kan_stub.sh scripts/emit_codensity_presentation.sh scripts/emit_context_compilation_report.sh
  scripts/emit_cql_context_report.sh scripts/emit_sheafification_kan.sh scripts/emit_abstraction_replacement_kan.sh
  tests/golden/activation.yml tests/golden/output-invariants.yml
)
for f in "${required[@]}"; do
  test -f "$f" || { echo "missing $f" >&2; exit 1; }
done
python3 - <<'PY'
from pathlib import Path
import re
text = Path('SKILL.md').read_text()
fm = text.split('---', 2)[1]
m = re.search(r'^description:\s*[\"\']?(.*?)[\"\']?\s*$', fm, flags=re.M)
if not m:
    raise SystemExit('SKILL.md missing description')
desc = m.group(1)
if len(desc) >= 1024:
    raise SystemExit(f'SKILL.md description too long: {len(desc)} chars')
if 'allow_implicit_invocation: true' not in Path('agents/openai.yaml').read_text():
    raise SystemExit('agents/openai.yaml must allow implicit invocation')
print(f'description length ok: {len(desc)} chars')
required = [
    'name: universalist', 'Track D', 'Track E', 'Track F', 'Universal architecture',
    'canonical boundary artifact', 'one signal, one seam', 'Freyd/AFT', 'free builder',
    'obstruction report', 'Behavioral coalgebra', 'Effect signature', 'P : B -> C',
    'Allow arbitrary domain primitives', 'Unknown-location artifact selector',
    'World and Boundary Inventory', 'Boundary Kind Taxonomy', 'Boundary Law Catalogue',
    'Universal Composition Doctrine', 'Composition Certificate', 'Boundary Normal Form',
    'Presentation Strategy Doctrine', 'Dense-Dual Presentation', 'Presentations compress',
    'Exact Context Doctrine', 'semantic consumer', 'Context Certificate', 'Context Normal Form',
    'Allow arbitrary sources', 'Forbid uncertified semantic consumption', 'Verified Context Plane',
    'Operational stores own mutation', 'Verified context planes own semantic publication',
    'Possibility Sheafification', 'Track G', 'Sheafification Certificate',
    'Abstraction Normal Form', 'Do not merely abstract. Sheafify possibility', 'internal mechanics layer', 'emit_mechanics_report.sh'
]
for r in required:
    if r not in text:
        raise SystemExit(f'SKILL.md missing {r}')
print('metadata ok')
PY
./scripts/emit_law_test_stub.sh coproduct typescript >/dev/null
./scripts/emit_law_test_stub.sh universal-architecture agnostic >/dev/null
./scripts/emit_law_test_stub.sh freyd agnostic >/dev/null
./scripts/emit_law_test_stub.sh obstruction agnostic >/dev/null
./scripts/emit_law_test_stub.sh behavioral-coalgebra agnostic >/dev/null
./scripts/emit_law_test_stub.sh effect-handler agnostic >/dev/null
./scripts/emit_law_test_stub.sh dense-probe agnostic >/dev/null
./scripts/emit_law_test_stub.sh sheafification agnostic >/dev/null
./scripts/emit_universal_artifact_matrix.sh >/dev/null
./scripts/emit_canonical_artifact_plan.sh lifted-implementation typescript >/dev/null
./scripts/emit_canonical_artifact_plan.sh free-builder typescript >/dev/null
./scripts/emit_canonical_artifact_plan.sh obstruction-report agnostic >/dev/null
./scripts/emit_canonical_artifact_plan.sh behavioral-coalgebra typescript >/dev/null
./scripts/emit_canonical_artifact_plan.sh effect-handler typescript >/dev/null
./scripts/emit_canonical_artifact_plan.sh dense-probe agnostic >/dev/null
./scripts/emit_universal_architecture_prompt.sh >/dev/null
./scripts/emit_freyd_boundary_diagnostic.sh boundary-diagnostic agnostic >/dev/null
./scripts/emit_freyd_boundary_diagnostic.sh free-builder typescript >/dev/null
./scripts/emit_freyd_boundary_diagnostic.sh no-exact-lift agnostic >/dev/null
./scripts/emit_world_boundary_inventory.sh architecture typescript >/dev/null
./scripts/emit_boundary_law_catalogue.sh projection >/dev/null
./scripts/emit_composition_certificate.sh api-boundary typescript >/dev/null
./scripts/emit_boundary_normal_form_plan.sh >/dev/null
./scripts/emit_presentation_diagnostic.sh compare agnostic >/dev/null
./scripts/emit_context_certificate.sh decision-packet agnostic >/dev/null
./scripts/emit_context_compiler_plan.sh semantic-consumer typescript >/dev/null
./scripts/emit_exact_context_prompt.sh audit >/dev/null
./scripts/emit_verified_context_plane.sh semantic-consumer typescript >/dev/null
./scripts/emit_cql_fit_assessment.sh context-boundary agnostic >/dev/null
./scripts/emit_context_publication_boundary.sh published-context agnostic >/dev/null
./scripts/emit_possibility_sheafifier.sh payment-status typescript >/dev/null
./scripts/emit_sheafification_certificate.sh payment-status typescript >/dev/null
./scripts/emit_abstraction_normal_form_plan.sh repo agnostic >/dev/null
./scripts/emit_mechanics_report.sh index agnostic >/dev/null
./scripts/emit_mechanics_report.sh kan-lift typescript >/dev/null
./scripts/emit_mechanics_report.sh codensity-presentation agnostic >/dev/null
./scripts/emit_mechanics_report.sh cql-context agnostic >/dev/null
./scripts/emit_mechanics_report.sh sheafification typescript >/dev/null
python3 scripts/emit_scaffold.py coproduct typescript >/dev/null
python3 scripts/emit_boundary_adapter.py decoder typescript >/dev/null
python3 scripts/emit_verification_plan.py coproduct >/dev/null
python3 scripts/detect_signals.py SKILL.md >/dev/null || true
echo "check_universalist: ok"
