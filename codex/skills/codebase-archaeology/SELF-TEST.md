# SELF-TEST: codebase-archaeology-codex

Run from the package root after unpacking.

## 1) Skill files exist

```bash
test -f .agents/skills/codebase-archaeology/SKILL.md
test -f .agents/skills/codebase-archaeology/references/CODEX_SUBAGENTS.md
test -f .agents/skills/codebase-archaeology/references/LANGUAGES.md
test -f .agents/skills/codebase-archaeology/references/PATTERNS.md
test -f .agents/skills/codebase-archaeology/references/EXAMPLES.md
```

## 2) Codex custom agents exist

```bash
test -f .codex/agents/archaeology-explorer.toml
test -f .codex/agents/archaeology-docs.toml
test -f .codex/agents/archaeology-entrypoints.toml
test -f .codex/agents/archaeology-domain.toml
test -f .codex/agents/archaeology-dataflow.toml
test -f .codex/agents/archaeology-integrations.toml
test -f .codex/agents/archaeology-tests.toml
```

## 3) TOML parses and required fields are present

```bash
python3 - <<'PY'
from pathlib import Path
import tomllib
required = {'name', 'description', 'developer_instructions'}
for path in Path('.codex/agents').glob('*.toml'):
    data = tomllib.loads(path.read_text())
    missing = required - data.keys()
    if missing:
        raise SystemExit(f'{path}: missing {sorted(missing)}')
    if data.get('sandbox_mode') != 'read-only':
        raise SystemExit(f'{path}: sandbox_mode should be read-only')
print('OK')
PY
```

## 4) Install into a test repo

```bash
repo=$(mktemp -d)
./install-project.sh "$repo"
test -f "$repo/.agents/skills/codebase-archaeology/SKILL.md"
test -f "$repo/.codex/agents/archaeology-explorer.toml"
test -f "$repo/.codex/config.toml"
```

## 5) Smoke-test archaeology commands in a target repo

From a repository you want to explore:

```bash
cat AGENTS.md README.md 2>/dev/null | head -40
find . -maxdepth 2 -type f \( -name 'package.json' -o -name 'Cargo.toml' -o -name 'pyproject.toml' -o -name 'go.mod' \) -print
rg -n "fn main|def main|func main|FastAPI\(|express\(|Router\(|clap|argparse|commander" . || true
rg -n "process\.env|std::env|os\.environ|config|settings" . || true
```

Expected: commands run without errors; some searches may have no matches depending on the repository.
