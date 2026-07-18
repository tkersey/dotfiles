#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

required=(
  SKILL.md README.md package.json agents/openai.yaml
  references/universalist-overview.md
  references/universal-problem-kernel.md
  references/universal-construction-registry.yaml
  references/decision-contract.yaml
  references/comonadic-spatiality-doctrine.md
  templates/universal-problem-certificate.md
  templates/universalist-plan.md
  templates/universalist-report.md
  scripts/validate_universal_registry.py
  scripts/emit_universal_problem.py
  scripts/emit_boundary_adapter.py
  scripts/emit_scaffold.py
  scripts/check_universalist.sh
  scripts/check_universalist_replacement.sh
  scripts/universalist_doctor.sh
  tests/test_universal_problem_kernel.py
  tests/golden/activation.yml
  tests/golden/output-invariants.yml
)

if [[ "${UNIVERSALIST_PARTIAL_CHECK:-0}" != "1" ]]; then
  required+=(
    references/description-composition-doctrine.md
    references/contextual-morphism-doctrine.md
    references/composition-geometry.md
    references/possibility-sheafification.md
    references/exact-context-doctrine.md
    references/presentation-strategies.md
    references/canonical-boundary-artifacts.md
    references/structures-and-laws.md
    references/mechanics/README.md
    scripts/init_universalist_plan.sh
    scripts/emit_mechanics_report.sh
    tests/test_decision_observability.py
  )
fi
for path in "${required[@]}"; do
  test -f "$path" || { echo "missing $path" >&2; exit 1; }
done

uv run --with pyyaml python3 - <<'PY'
from pathlib import Path
import json
import re
import yaml

root = Path('.')
text = (root / 'SKILL.md').read_text(encoding='utf-8')
parts = text.split('---', 2)
if len(parts) != 3:
    raise SystemExit('SKILL.md must contain YAML frontmatter')
frontmatter = yaml.safe_load(parts[1])
if frontmatter.get('name') != 'universalist':
    raise SystemExit('SKILL.md frontmatter name must be universalist')
desc = frontmatter.get('description')
if not isinstance(desc, str) or not desc.strip():
    raise SystemExit('SKILL.md missing description')
if len(desc) >= 1024:
    raise SystemExit(f'SKILL.md description too long: {len(desc)} chars')
for phrase in (
    'implementing, reviewing, or resolving code that considers a boundary',
    'creating, changing, preserving, validating, migrating, bypassing, or removing',
    'ordinary feature work or PR/review resolution',
    'boundary consideration itself is the signal',
    'Keep implicit invocation enabled',
):
    if phrase not in desc:
        raise SystemExit(f'SKILL.md description missing trigger phrase: {phrase}')

for phrase in (
    'Universal Problem Compiler',
    'Produce the boring candidate',
    'Construct the task-local comparison universe',
    'Select universal bytecode',
    'Universal proof contract',
    'Existence',
    'Commutation',
    'Mediation',
    'Canonicality',
    'Effectivity',
    'Materiality gate',
    'Category theory must beat the boring architecture.',
    'Lower and erase',
    'references/universal-construction-registry.yaml',
    'Day convolution',
    'promonoidal convolution',
    'Tambara',
    'shared ambient monoidal index world',
    'Do not write a Day product between objects living over unrelated bases',
    'Track A0',
    'Track D',
    'Track E',
    'Track F',
    'Track G',
    'Track H',
    'Track I',
    'Boundary-trigger mandate',
    'Activation is broad; escalation is narrow',
    'Disposition: preserved / introduced / changed / repaired / removed / bypass-justified',
    'ledger create --source universalist',
    '.ledger/universalist/plan-{plan-id}.md',
    'exactly one root-scoped receipt',
):
    if phrase not in text:
        raise SystemExit(f'SKILL.md missing compiler contract: {phrase}')

boring = text.index('## Phase 1 — Produce the boring candidate')
universe = text.index('## Phase 2 — Construct the task-local comparison universe')
materiality = text.index('## Phase 7 — Materiality gate')
lowering = text.index('## Phase 8 — Lower and erase')
if not boring < universe < materiality < lowering:
    raise SystemExit('universal compiler phases are out of order')

openai = (root / 'agents/openai.yaml').read_text(encoding='utf-8')
for phrase in (
    'allow_implicit_invocation: true',
    'boring repository-native candidate',
    'universal-problem pass',
    'material delta',
):
    if phrase not in openai:
        raise SystemExit(f'agents/openai.yaml missing: {phrase}')

package = json.loads((root / 'package.json').read_text(encoding='utf-8'))
if package.get('version') != '16.3.0':
    raise SystemExit('package version must remain compatible with the 16.3.0 mechanics release')
if package.get('universal_problem_compiler') is not True:
    raise SystemExit('package.json must enable universal_problem_compiler')
if package.get('theorem_registry_schema') != 'universal-construction-registry/v1':
    raise SystemExit('package.json theorem_registry_schema mismatch')

plan = (root / 'templates/universalist-plan.md').read_text(encoding='utf-8')
for field in (
    '## Boring candidate:',
    '## Universal problem:',
    '## Comparison universe:',
    '## Selected theorem card or none:',
    '## Admissible alternatives:',
    '## Mediation / factorization:',
    '## Canonicality / equivalence:',
    '## Material delta:',
    '## Effectivity / resource bound:',
    '## Root decision receipt: pending / emitted',
):
    if field not in plan:
        raise SystemExit(f'plan template missing field: {field}')

contract = yaml.safe_load((root / 'references/decision-contract.yaml').read_text(encoding='utf-8'))
body = contract['skill_decision_contract']
clause_ids = {clause['clause_id'] for clause in body['clauses']}
if 'UNI-SHADOW-001' not in clause_ids:
    raise SystemExit('decision contract missing UNI-SHADOW-001')
for route in body['routes']:
    if route.get('aliases') != []:
        raise SystemExit(f"route aliases must remain empty: {route['route_id']}")

activation = yaml.safe_load((root / 'tests/golden/activation.yml').read_text(encoding='utf-8'))
prompts = {case['prompt']: case for case in activation['cases']}
for prompt in (
    'Compare the obvious checked tenant-pair constructor with the strongest universal solution and keep the category theory only if it changes the architecture.',
    'The public behavior leaves retry policy and authority unspecified; do not invent a canonical implementation.',
    'Use a pullback explanation, but retain the existing checked constructor if factorization adds no code or proof delta.',
):
    if prompt not in prompts or prompts[prompt].get('should_use_skill') is not True:
        raise SystemExit(f'activation fixture missing universal-shadow case: {prompt}')

invariants = yaml.safe_load((root / 'tests/golden/output-invariants.yml').read_text(encoding='utf-8'))
names = {item['name'] for item in invariants['invariants']}
for name in (
    'universal_shadow_starts_with_boring_candidate',
    'universal_problem_defines_comparison_universe',
    'universal_claim_requires_full_proof_contract',
    'materiality_gate_discards_explanatory_only_theory',
    'obstruction_is_first_class',
    'spatial_day_requires_shared_or_product_index',
):
    if name not in names:
        raise SystemExit(f'output invariant missing: {name}')

overview = (root / 'references/universalist-overview.md').read_text(encoding='utf-8')
for phrase in (
    'proof-carrying architecture compiler',
    'Boring candidate first',
    'Universal shadow',
    'Universal bytecode',
    'If category theory changes only the explanation, preserve the boring candidate.',
):
    if phrase not in overview:
        raise SystemExit(f'universalist overview missing compiler contract: {phrase}')

spatial = (root / 'references/comonadic-spatiality-doctrine.md').read_text(encoding='utf-8')
for phrase in (
    'shared ambient index',
    'explicit product index',
    'density/Day comparison map',
    'Do not assert:',
    'unrelated bases',
):
    if phrase not in spatial:
        raise SystemExit(f'spatial Day correction missing: {phrase}')

print(f'description length ok: {len(desc)} chars')
print('universal problem compiler metadata ok')
PY

registry_args=()
if [[ "${UNIVERSALIST_SKIP_REFERENCE_CHECK:-0}" != "1" ]]; then
  registry_args+=(--check-references)
fi
uv run --with pyyaml python3 scripts/validate_universal_registry.py "${registry_args[@]}"

uv run --with pyyaml python3 -m compileall -q \
  scripts/validate_universal_registry.py \
  scripts/emit_universal_problem.py \
  scripts/emit_boundary_adapter.py \
  scripts/emit_scaffold.py \
  tests/test_universal_problem_kernel.py

bash -n scripts/check_universalist.sh
bash -n scripts/check_universalist_replacement.sh
bash -n scripts/universalist_doctor.sh
if [[ "${UNIVERSALIST_PARTIAL_CHECK:-0}" != "1" ]]; then
  bash -n scripts/init_universalist_plan.sh
fi

if [[ "${UNIVERSALIST_SKIP_EXTERNAL:-0}" != "1" ]]; then
  command -v ledger >/dev/null || { echo 'missing ledger; set UNIVERSALIST_SKIP_EXTERNAL=1 only for isolated package checks' >&2; exit 1; }
  command -v seq >/dev/null || { echo 'missing seq; set UNIVERSALIST_SKIP_EXTERNAL=1 only for isolated package checks' >&2; exit 1; }
  seq skill-contract validate --file references/decision-contract.yaml --format json >/dev/null
  uv run --with pyyaml python3 ../tune/tools/decision_contract_lint.py references/decision-contract.yaml >/dev/null
  PYTHONDONTWRITEBYTECODE=1 uv run --with pyyaml python3 tests/test_decision_observability.py
fi

# Keep the semantic suite last: it exercises registry validation, plain/expert
# emission, fail-closed adapters, template synchronization, phase ordering, and
# spatial-Day routing in one interpreter process.
uv run --with pyyaml python3 tests/test_universal_problem_kernel.py

echo 'check_universalist: ok'
