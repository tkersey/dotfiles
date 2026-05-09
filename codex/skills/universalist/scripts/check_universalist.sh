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
  references/universal-architecture-ecosystem.md references/canonical-boundary-artifacts.md
  references/kan-boundaries-for-universalist.md references/yoneda-coyoneda-defunctionalization.md
  references/universal-architecture-law-tests.md
  templates/universalist-plan.md templates/universalist-report.md templates/universal-architecture-report.md
  scripts/init_universalist_plan.sh scripts/detect_signals.py scripts/emit_scaffold.py scripts/emit_boundary_adapter.py
  scripts/emit_verification_plan.py scripts/emit_law_test_stub.sh scripts/emit_universal_artifact_matrix.sh
  scripts/emit_canonical_artifact_plan.sh scripts/emit_universal_architecture_prompt.sh
)
for f in "${required[@]}"; do
  test -f "$f" || { echo "missing $f" >&2; exit 1; }
done
python3 - <<'PY'
from pathlib import Path
text = Path('SKILL.md').read_text()
for r in ['name: universalist','Track D','Universal architecture','canonical boundary artifact','one signal, one seam']:
    if r not in text:
        raise SystemExit(f'SKILL.md missing {r}')
print('metadata ok')
PY
./scripts/emit_law_test_stub.sh coproduct typescript >/dev/null
./scripts/emit_law_test_stub.sh universal-architecture agnostic >/dev/null
./scripts/emit_universal_artifact_matrix.sh >/dev/null
./scripts/emit_canonical_artifact_plan.sh lifted-implementation typescript >/dev/null
./scripts/emit_universal_architecture_prompt.sh >/dev/null
python3 scripts/emit_scaffold.py coproduct typescript >/dev/null
python3 scripts/emit_boundary_adapter.py decoder typescript >/dev/null
python3 scripts/emit_verification_plan.py coproduct >/dev/null
python3 scripts/detect_signals.py SKILL.md >/dev/null || true
echo "check_universalist: ok"
