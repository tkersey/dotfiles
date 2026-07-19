#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

required=(
  SKILL.md README.md package.json agents/openai.yaml
  references/universal-problem-ir.md
  references/universal-construction-registry.yaml
  references/universal-constructions/01-cards.yaml
  references/decision-contract.yaml
  references/composition-geometry.md
  references/description-composition-doctrine.md
  references/contextual-morphism-doctrine.md
  references/comonadic-spatiality-doctrine.md
  references/exact-context-doctrine.md
  references/possibility-sheafification.md
  references/category-pivot.md
  templates/universal-problem-certificate.md
  templates/universalist-plan.md
  templates/universalist-report.md
  scripts/compile_universal_problem.py
  scripts/check_universal_problem.sh
  scripts/init_universalist_plan.sh
  scripts/emit_boundary_adapter.py
  scripts/emit_scaffold.py
  tests/test_universal_problem_compiler.py
  tests/test_emitters.py
  tests/golden/activation.yml
  tests/golden/output-invariants.yml
)
for path in "${required[@]}"; do
  test -f "$path" || { echo "missing $path" >&2; exit 1; }
done

uv run --with pyyaml python3 - <<'PY'
from pathlib import Path
import json
import re
import tomllib
import yaml

skill = Path('SKILL.md').read_text(encoding='utf-8')
fm = skill.split('---', 2)[1]
match = re.search(r'^description:\s*["\']?(.*?)["\']?\s*$', fm, flags=re.M)
if not match:
    raise SystemExit('SKILL.md missing description')
description = match.group(1)
if len(description) >= 1024:
    raise SystemExit(f'SKILL.md description too long: {len(description)}')
for token in (
    'boundary consideration itself is the signal',
    'Keep implicit invocation enabled',
    'hidden optimizer',
    'Universal problem compiler',
    'category theory must beat the boring architecture',
    'Material architectural delta',
    'competitor mediation',
    'effective presentation',
    'Description product',
    'Context action',
):
    if token.lower() not in skill.lower():
        raise SystemExit(f'SKILL.md missing token: {token}')

package = json.loads(Path('package.json').read_text())
if package.get('version') != '17.0.0':
    raise SystemExit('package version must be 17.0.0')
if package.get('minimum_ledger_version') != '0.10.4':
    raise SystemExit('minimum Ledger version mismatch')
if package.get('minimum_seq_version') != '0.3.51':
    raise SystemExit('minimum Seq version mismatch')

openai = yaml.safe_load(Path('agents/openai.yaml').read_text())
if openai['policy']['allow_implicit_invocation'] is not True:
    raise SystemExit('implicit invocation must remain enabled')
if 'hidden universal shadow' not in openai['interface']['default_prompt']:
    raise SystemExit('default prompt must route through the hidden shadow')

registry_index = yaml.safe_load(Path('references/universal-construction-registry.yaml').read_text())
if registry_index.get('schema') != 'universal-construction-registry/v1':
    raise SystemExit('registry schema mismatch')
constructions = []
for relative_path in registry_index.get('includes', []):
    fragment_path = Path('references') / relative_path
    fragment = yaml.safe_load(fragment_path.read_text())
    constructions.extend(fragment.get('constructions', []))
if len(constructions) < 50:
    raise SystemExit('registry must preserve the full categorical corpus')

plan = Path('templates/universalist-plan.md').read_text()
for field in (
    '## Ordinary candidate:',
    '## Universal shadow:',
    '## Material architectural delta:',
    '## Universal witness / mediator:',
    '## Admissible alternatives / comparison maps:',
    '## Observations / equivalence:',
    '## Falsifier / negative witness:',
    '## Effectivity / resource bound:',
):
    if field not in plan:
        raise SystemExit(f'plan missing field: {field}')

contract = Path('references/decision-contract.yaml').read_text()
for token in ('UNI-DISPOSITION-001', 'UNI-MINIMAL-001', 'UNI-SHADOW-001', 'UNI-MECHANICS-001', 'UNI-ROOT-001'):
    if token not in contract:
        raise SystemExit(f'decision contract missing {token}')

activation = yaml.safe_load(Path('tests/golden/activation.yml').read_text())
prompts = {case['prompt']: case for case in activation['cases']}
for prompt in (
    'Use category theory internally, but show me the smallest ordinary architecture unless the universal shadow materially improves it.',
    'The categorical shadow names a pullback, but it changes no owner, state, composition, proof, resource, or migration decision.',
    'The public behavior underdetermines authority and retry policy; do not invent a canonical implementation.',
):
    if prompt not in prompts:
        raise SystemExit(f'activation fixture missing: {prompt}')

agent_tokens = {
  'universalist-world-cartographer.toml': ('ordinary candidate', 'comparison universe', 'material delta'),
  'universalist-substrate-architect.toml': ('universal shadow', 'effective', 'ordinary candidate'),
  'universalist-categorical-architect.toml': ('Universal Problem', 'competitor mediation', 'material architectural delta'),
  'universalist-semanticist.toml': ('universal shadow', 'observations', 'mediator'),
  'universalist-resource-realist.toml': ('universal shadow', 'material', 'ordinary candidate'),
  'universalist-proof-auditor.toml': ('Universal Problem Certificate', 'competitor mediation', 'discard shadow'),
  'universalist-witness-implementer.toml': ('Universal Problem Certificate', 'repository-native lowering', 'material delta'),
  'universalist-verifier.toml': ('Universal Problem Certificate', 'material delta', 'competitor mediation'),
}
agent_root = Path('../../agents')
for name, tokens in agent_tokens.items():
    path = agent_root / name
    data = tomllib.loads(path.read_text())
    instructions = data['developer_instructions']
    if 'Do not spawn subagents' not in instructions:
        raise SystemExit(f'{path} permits recursive delegation')
    for token in tokens:
        if token not in instructions:
            raise SystemExit(f'{path} missing token: {token}')

print(f'description length ok: {len(description)}')
print(f'theorem cards: {len(constructions)}')
print('primary Universal Problem routing ok')
PY

seq skill-contract validate --file references/decision-contract.yaml --format json >/dev/null
uv run --with pyyaml -- python3 ../tune/tools/decision_contract_lint.py references/decision-contract.yaml >/dev/null
PYTHONDONTWRITEBYTECODE=1 uv run --with pyyaml -- python3 tests/test_decision_observability.py
bash scripts/check_universal_problem.sh
bash -n scripts/init_universalist_plan.sh

echo "check_universalist: ok"
