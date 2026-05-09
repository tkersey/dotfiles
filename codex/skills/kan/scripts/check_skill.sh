#!/usr/bin/env bash
set -euo pipefail
python3 - <<'PY'
from pathlib import Path
import re, yaml
root = Path.cwd()
skill = root / "SKILL.md"
if not skill.exists():
    raise SystemExit("missing SKILL.md")
text = skill.read_text()
if not text.startswith("---\n"):
    raise SystemExit("SKILL.md missing YAML frontmatter")
try:
    _, fm, _ = text.split("---", 2)
except ValueError:
    raise SystemExit("invalid frontmatter delimiter")
meta = yaml.safe_load(fm) or {}
if meta.get("name") != root.name:
    raise SystemExit(f"SKILL.md name {meta.get('name')!r} must match parent directory {root.name!r}")
if not meta.get("description"):
    raise SystemExit("missing description")
for rel in [
    "references",
    "scripts",
    "examples",
    "tests/golden",
    "agents/openai.yaml",
    "README.md",
    "references/kan-lifts.md",
    "references/architecture-transformation.md",
    "references/lift-law-tests.md",
    "references/lift-claim-map.md",
    "references/defunctionalization.md",
    "references/defunctionalization-claim-map.md",
    "references/yoneda-coyoneda.md",
    "references/yoneda-coyoneda-claim-map.md",
    "references/lift-architecture-playbook.md",
    "references/lift-obligation-discovery.md",
    "scripts/emit_lift_playbook.sh",
]:
    if not (root / rel).exists():
        raise SystemExit(f"missing {rel}")
sources = yaml.safe_load((root / "references" / "sources.yml").read_text())["sources"]
known = set(sources)
pattern = re.compile(r"\[([A-Z0-9][A-Z0-9-]+)\]")
errors = []
for path in list((root / "references").glob("*.md")) + [skill, root / "README.md"] + list((root / "examples").rglob("*")):
    if path.is_file() and path.suffix in {".md", ".hs", ".ts", ".rs", ".py"}:
        ids = set(pattern.findall(path.read_text(errors="ignore")))
        unknown = sorted(i for i in ids if i.startswith(("KAN-", "OPENAI-", "AGENT-")) and i not in known)
        if unknown:
            errors.append(f"{path.relative_to(root)} references unknown source IDs: {unknown}")
for script in (root / "scripts").glob("*.sh"):
    if not script.stat().st_mode & 0o111:
        errors.append(f"script not executable: {script.relative_to(root)}")
# Basic coequal support smoke checks.
skill_text = text.lower()
for needle in ["kan extensions", "kan lifts", "lft_p", "rft_p", "precomposition", "postcomposition", "defunctionalization", "boundary ir", "yoneda", "coyoneda", "observation", "deferred", "outside-in", "no exact lift", "obligation ledger"]:
    if needle not in skill_text:
        errors.append(f"SKILL.md missing coequal support marker: {needle}")
if errors:
    raise SystemExit("\n".join(errors))
print("check_skill: ok")
PY
./scripts/emit_kan_stub.sh plugin-api agnostic >/dev/null
./scripts/emit_kan_stub.sh lift-realization agnostic >/dev/null
./scripts/emit_kan_stub.sh lift-obligation agnostic >/dev/null
./scripts/emit_witness_pack.sh pointwise-lan agnostic >/dev/null
./scripts/emit_witness_pack.sh left-kan-lift agnostic >/dev/null
./scripts/emit_witness_pack.sh right-kan-lift agnostic >/dev/null
./scripts/emit_law_test_plan.sh ran agnostic >/dev/null
./scripts/emit_law_test_plan.sh left-lift agnostic >/dev/null
./scripts/emit_law_test_plan.sh right-lift agnostic >/dev/null
./scripts/emit_source_pack.sh foundations pointwise >/dev/null
./scripts/emit_source_pack.sh lifts residual >/dev/null
./scripts/emit_source_pack.sh lift-playbook outside-in >/dev/null
./scripts/emit_source_pack.sh defunctionalization boundary-ir >/dev/null
./scripts/emit_defun_pass.sh boundary-ir agnostic >/dev/null
./scripts/emit_yoneda_pass.sh observation-boundary agnostic >/dev/null
./scripts/emit_yoneda_pass.sh generation-boundary agnostic >/dev/null
./scripts/emit_yoneda_pass.sh lift agnostic >/dev/null
./scripts/emit_lift_playbook.sh contract-refactor agnostic >/dev/null
./scripts/emit_lift_playbook.sh obligation-discovery agnostic >/dev/null
./scripts/emit_lift_playbook.sh no-exact-lift agnostic >/dev/null
./scripts/emit_witness_pack.sh defunctionalization agnostic >/dev/null
./scripts/emit_witness_pack.sh yoneda-observation agnostic >/dev/null
./scripts/emit_witness_pack.sh coyoneda-generation agnostic >/dev/null
./scripts/emit_witness_pack.sh yoneda-coyoneda-lift agnostic >/dev/null
./scripts/emit_witness_pack.sh lift-contract-refactor agnostic >/dev/null
./scripts/emit_witness_pack.sh lift-obligation-discovery agnostic >/dev/null
./scripts/emit_law_test_plan.sh defunctionalization agnostic >/dev/null
./scripts/emit_law_test_plan.sh yoneda agnostic >/dev/null
./scripts/emit_law_test_plan.sh coyoneda agnostic >/dev/null
./scripts/emit_law_test_plan.sh yoneda-coyoneda agnostic >/dev/null
./scripts/emit_law_test_plan.sh contract-lift agnostic >/dev/null
./scripts/emit_law_test_plan.sh obligation-lift agnostic >/dev/null
./scripts/emit_law_test_plan.sh no-exact-lift agnostic >/dev/null
./scripts/emit_source_pack.sh yoneda representation >/dev/null
if [ -f examples/python/finite_kan.py ]; then python3 examples/python/finite_kan.py >/dev/null; fi
if [ -f examples/python/schema_migration_lan.py ]; then python3 examples/python/schema_migration_lan.py >/dev/null; fi
if [ -f examples/python/codensity_witness.py ]; then python3 examples/python/codensity_witness.py >/dev/null; fi
python3 examples/python/poset_lift_witness.py >/dev/null
python3 examples/python/defunctionalized_lift_witness.py >/dev/null
python3 examples/python/yoneda_coyoneda_witness.py >/dev/null
python3 examples/python/lift_contract_obligations.py >/dev/null
