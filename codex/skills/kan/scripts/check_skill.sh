#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"
required=(
  SKILL.md README.md package.json agents/openai.yaml
  references/world-boundary-preamble.md references/boundary-kind-to-kan.md references/foundations.md references/kan-lifts.md
  references/yoneda-coyoneda.md references/defunctionalization.md references/freyd-aft.md references/architecture-transformation.md
  references/law-tests.md references/claim-map.md references/sources.md references/sources.yml
  scripts/emit_world_boundary_preamble.sh scripts/emit_boundary_kind_map.sh scripts/emit_kan_stub.sh scripts/emit_law_test_plan.sh
  scripts/emit_yoneda_pass.sh scripts/emit_defun_pass.sh scripts/emit_freyd_pass.sh scripts/emit_source_pack.sh scripts/check_skill.sh
  templates/world-boundary-kan-report.md tests/golden/activation.yml tests/golden/output-invariants.yml
  examples/python/world_boundary_witness.py examples/agnostic/world-boundary-handoff.trace.md
)
for f in "${required[@]}"; do test -f "$f" || { echo "missing $f" >&2; exit 1; }; done
python3 - <<'PY'
from pathlib import Path
text=Path('SKILL.md').read_text()
for s in ['name: kan','World Model Preamble','Boundary Kind to Kan Mapping','Required Handoff Contract','Kan lifts','Yoneda','Coyoneda','Defunctionalization','Freyd/AFT']:
    if s not in text:
        raise SystemExit(f'SKILL.md missing {s}')
print('metadata ok')
PY
./scripts/emit_world_boundary_preamble.sh api typescript >/dev/null
./scripts/emit_boundary_kind_map.sh projection >/dev/null
./scripts/emit_kan_stub.sh lift typescript >/dev/null
./scripts/emit_law_test_plan.sh lan agnostic >/dev/null
./scripts/emit_law_test_plan.sh lift agnostic >/dev/null
./scripts/emit_law_test_plan.sh yoneda agnostic >/dev/null
./scripts/emit_yoneda_pass.sh mixed typescript >/dev/null
./scripts/emit_defun_pass.sh boundary typescript >/dev/null
./scripts/emit_freyd_pass.sh free-builder agnostic >/dev/null
./scripts/emit_source_pack.sh freyd boundary >/dev/null
python3 examples/python/world_boundary_witness.py >/dev/null
echo 'check_skill: ok'
