#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"

fail() {
  printf 'check_skill: %s\n' "$*" >&2
  exit 1
}

require_file() {
  [[ -f "$1" ]] || fail "missing required file: $1"
}

require_executable() {
  [[ -x "$1" ]] || fail "script is not executable: $1"
}

required_files=(
  SKILL.md
  README.md
  PATCH_NOTES.md
  agents/openai.yaml
  references/sources.md
  references/sources.yml
  references/claim-map.md
  references/foundations.md
  references/control-families.md
  references/defunctionalization.md
  references/language-examples.md
  references/implementation-and-evaluation.md
  references/research-roadmap.md
  references/witness-programs.md
  scripts/emit_artifact_stub.sh
  scripts/emit_source_pack.sh
  scripts/emit_witness_pack.sh
  scripts/check_skill.sh
  examples/agnostic/static-vs-dynamic.trace.md
  examples/agnostic/evaluator-to-machine.trace.md
  examples/racket/shift-reset-vs-control.rkt
  examples/racket/prompt-tags.rkt
  examples/ocaml/one-shot-effects.md
  examples/ocaml/delimcc-multiprompt.md
  tests/golden/activation.yml
  tests/golden/output-invariants.yml
)

for f in "${required_files[@]}"; do
  require_file "$f"
done

for s in scripts/*.sh; do
  require_executable "$s"
done

PYTHON_BIN="${PYTHON_BIN:-$(command -v /usr/bin/python3 2>/dev/null || command -v python3 2>/dev/null || true)}"
[[ -n "$PYTHON_BIN" ]] || fail "python3 not found"
"$PYTHON_BIN" - <<'PY'
from pathlib import Path
import re, sys
root = Path('.')

def die(msg):
    print(f'check_skill: {msg}', file=sys.stderr)
    sys.exit(1)

sources_md = (root/'references/sources.md').read_text(encoding='utf-8')
sources_yml = (root/'references/sources.yml').read_text(encoding='utf-8')
md_ids = set(re.findall(r'\[([A-Z0-9][A-Z0-9-]+)\]', sources_md))
yml_ids = set(re.findall(r'^  ([A-Z0-9][A-Z0-9-]+):\n', sources_yml, flags=re.M))
if not md_ids:
    die('no source IDs found in references/sources.md')
if md_ids != yml_ids:
    missing_yml = sorted(md_ids - yml_ids)
    missing_md = sorted(yml_ids - md_ids)
    die(f'source ID mismatch; missing in yml={missing_yml}; missing in md={missing_md}')

scan_paths = []
for pattern in ['references/*.md', 'examples/**/*.md', 'tests/golden/*.yml']:
    scan_paths.extend(root.glob(pattern))
for p in sorted(set(scan_paths)):
    if p.name == 'sources.md':
        continue
    text = p.read_text(encoding='utf-8')
    ids = set(re.findall(r'\[([A-Z0-9][A-Z0-9-]+)\]', text))
    unknown = sorted(ids - md_ids)
    if unknown:
        die(f'{p} references unknown source IDs: {unknown}')

skill = (root/'SKILL.md').read_text(encoding='utf-8')
for ref in [
    'references/foundations.md',
    'references/control-families.md',
    'references/defunctionalization.md',
    'references/language-examples.md',
    'references/implementation-and-evaluation.md',
    'references/research-roadmap.md',
    'references/witness-programs.md',
    'references/claim-map.md',
    'references/sources.md',
    'references/sources.yml',
]:
    if ref not in skill:
        die(f'SKILL.md does not mention {ref}')
    if not (root/ref).exists():
        die(f'SKILL.md mentions missing reference {ref}')

for golden in sorted((root/'tests/golden').glob('*.yml')):
    text = golden.read_text(encoding='utf-8')
    for needle in ['prompt:', 'expected:']:
        if needle not in text:
            die(f'{golden} missing {needle}')
PY

# Valid script calls should succeed.
scripts/emit_artifact_stub.sh derivation-memo agnostic >/dev/null
scripts/emit_artifact_stub.sh benchmark-plan ocaml >/dev/null
scripts/emit_source_pack.sh semantics static-vs-dynamic >/dev/null
scripts/emit_source_pack.sh language racket >/dev/null
scripts/emit_witness_pack.sh one-shot ocaml >/dev/null
scripts/emit_witness_pack.sh machine-derivation agnostic >/dev/null

# Invalid script calls should fail.
if scripts/emit_artifact_stub.sh bogus agnostic >/dev/null 2>&1; then
  fail "emit_artifact_stub.sh accepted invalid kind"
fi
if scripts/emit_source_pack.sh bogus broad >/dev/null 2>&1; then
  fail "emit_source_pack.sh accepted invalid track"
fi
if scripts/emit_witness_pack.sh bogus agnostic >/dev/null 2>&1; then
  fail "emit_witness_pack.sh accepted invalid topic"
fi

printf 'check_skill: ok\n'
