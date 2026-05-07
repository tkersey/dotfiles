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
for rel in ["references", "scripts", "examples", "tests/golden", "agents/openai.yaml", "README.md"]:
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
if errors:
    raise SystemExit("\n".join(errors))
print("check_skill: ok")
PY
./scripts/emit_kan_stub.sh plugin-api agnostic >/dev/null
./scripts/emit_witness_pack.sh pointwise-lan agnostic >/dev/null
./scripts/emit_law_test_plan.sh ran agnostic >/dev/null
./scripts/emit_source_pack.sh foundations pointwise >/dev/null
python3 examples/python/finite_kan.py >/dev/null
python3 examples/python/schema_migration_lan.py >/dev/null
python3 examples/python/codensity_witness.py >/dev/null
