#!/usr/bin/env bash
set -euo pipefail

ROOT="."
OUTPUT="markdown"
MAX_DEPTH="${REDUCE_SCAN_MAX_DEPTH:-5}"
FILTERS=()

usage() {
  cat <<'TEXT'
Usage: reduce-scan.sh [OPTIONS] [ROOT]

Non-destructive inventory scanner for the reduce skill. Treat output as inventory, not proof.

Options:
  --json             Emit JSON using python3 when available.
  --markdown         Emit markdown/text sections. Default.
  --web              Include web-framework/build-stack scan.
  --infra            Include infrastructure scan.
  --codegen          Include codegen/generated-surface scan.
  --single-impl      Include single-implementation abstraction scan.
  --proof-commands   Include likely proof commands.
  --all              Include all category scans. Default when no category flag is passed.
  --max-depth N      Limit find traversal depth. Default: REDUCE_SCAN_MAX_DEPTH or 5.
  -h, --help         Show this help.
TEXT
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --json) OUTPUT="json"; shift ;;
    --markdown) OUTPUT="markdown"; shift ;;
    --web|--infra|--codegen|--single-impl|--proof-commands)
      FILTERS+=("${1#--}"); shift ;;
    --all) FILTERS=("web" "infra" "codegen" "single-impl" "proof-commands"); shift ;;
    --max-depth)
      if [ "$#" -lt 2 ]; then echo "--max-depth requires a value" >&2; exit 2; fi
      MAX_DEPTH="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    --) shift; break ;;
    -*) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
    *) ROOT="$1"; shift ;;
  esac
done

if [ "${#FILTERS[@]}" -eq 0 ]; then
  FILTERS=("web" "infra" "codegen" "single-impl" "proof-commands")
fi

if [ ! -d "$ROOT" ]; then
  echo "reduce-scan: root is not a directory: $ROOT" >&2
  exit 2
fi

cd "$ROOT"

have() { command -v "$1" >/dev/null 2>&1; }
contains_filter() {
  local needle="$1"
  local item
  for item in "${FILTERS[@]}"; do
    [ "$item" = "$needle" ] && return 0
  done
  return 1
}
section() { printf '\n## %s\n\n' "$1"; }

search() {
  local pattern="$1"
  shift || true
  if have rg; then
    rg -n --hidden \
      --glob '!node_modules' --glob '!vendor' --glob '!dist' --glob '!build' --glob '!coverage' \
      --glob '!.git' --glob '!.next' --glob '!target' \
      "$pattern" "${@:-.}" || true
  else
    grep -RInE \
      --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=vendor --exclude-dir=dist \
      --exclude-dir=build --exclude-dir=coverage --exclude-dir=.next --exclude-dir=target \
      "$pattern" "${@:-.}" 2>/dev/null || true
  fi
}

if [ "$OUTPUT" = "json" ]; then
  if ! have python3; then
    echo "reduce-scan: --json requires python3" >&2
    exit 2
  fi
  FILTERS_CSV="$(IFS=,; echo "${FILTERS[*]}")" MAX_DEPTH="$MAX_DEPTH" python3 - <<'PY_REDUCE_SCAN_JSON'
from __future__ import annotations
import json, os, re
from pathlib import Path

root = Path('.')
max_depth = int(os.environ.get('MAX_DEPTH', '5'))
filters = set(os.environ.get('FILTERS_CSV', '').split(','))
ignored = {'.git','node_modules','vendor','dist','build','coverage','.next','target','.venv','venv'}

def under_depth(path: Path) -> bool:
    return len(path.parts) <= max_depth + 1

def walk_files():
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ignored]
        base = Path(dirpath)
        if not under_depth(base):
            dirnames[:] = []
            continue
        for name in filenames:
            p = base / name
            if under_depth(p):
                yield p

def match_names(patterns):
    out = []
    for p in walk_files():
        s = str(p)
        if any(re.search(pattern, s, re.I) for pattern in patterns):
            out.append(s)
    return sorted(out)

def grep(pattern):
    rx = re.compile(pattern, re.I)
    hits = []
    for p in walk_files():
        if p.suffix.lower() not in {'.py','.ts','.tsx','.js','.jsx','.go','.rs','.java','.kt','.rb','.php','.cs','.json','.yaml','.yml','.toml','.sh','.md','.tf','.graphql','.proto'}:
            continue
        try:
            lines = p.read_text(encoding='utf-8', errors='ignore').splitlines()
        except OSError:
            continue
        for idx, line in enumerate(lines, 1):
            if rx.search(line):
                hits.append({'path': str(p), 'line': idx, 'text': line.strip()[:240]})
                if len(hits) >= 200:
                    return hits
    return hits

out = {
  'root': str(Path.cwd()),
  'max_depth': max_depth,
  'filters': sorted(filters),
  'note': 'Inventory only; not proof of safe deletion.',
  'manifests': match_names([r'package\.json$', r'pnpm-workspace\.yaml$', r'turbo\.json$', r'nx\.json$', r'Makefile$', r'justfile$', r'pyproject\.toml$', r'go\.mod$', r'Cargo\.toml$', r'pom\.xml$', r'build\.gradle', r'Dockerfile$', r'compose\.ya?ml$', r'\.tf$']),
}
if 'web' in filters:
    out['web_stack'] = grep(r'react|next|remix|vite|webpack|rollup|parcel|svelte|vue|angular|hydration|jsx|tsx|client router|css-in-js|styled-components|emotion')
if 'infra' in filters:
    out['infra'] = match_names([r'\.github/workflows/', r'Dockerfile$', r'compose\.ya?ml$', r'Chart\.yaml$', r'values\.yaml$', r'kustomization\.yaml$', r'\.tf$', r'helm', r'kubernetes', r'k8s'])
if 'codegen' in filters:
    out['codegen'] = grep(r'codegen|generate|generated|openapi|swagger|graphql-codegen|protoc|prisma generate|sqlc|buf generate')
    out['generated_files'] = match_names([r'generated', r'\.gen\.', r'\.generated\.', r'openapi\.', r'schema\.graphql$', r'\.proto$'])
if 'single-impl' in filters:
    out['single_impl_clues'] = grep(r'interface [A-Z][A-Za-z0-9_]*|abstract class|implements [A-Z][A-Za-z0-9_]*|protocol [A-Z][A-Za-z0-9_]*|trait [A-Z][A-Za-z0-9_]*|class .*Service|class .*Repository|type .* interface')
if 'proof-commands' in filters:
    out['proof_command_clues'] = grep(r'"(test|check|lint|typecheck|build|verify)[^"]*"\s*:|pytest|go test|cargo test|mvn test|gradle test|tsc|vitest|jest|playwright|cypress')
print(json.dumps(out, indent=2))
PY_REDUCE_SCAN_JSON
  exit 0
fi

section "reduce scan"
printf 'root: %s\n' "$(pwd)"
printf 'max_depth: %s\n' "$MAX_DEPTH"
printf 'filters: %s\n' "${FILTERS[*]}"
printf 'timestamp_utc: %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || true)"
printf '\nInventory only; not proof of safe deletion.\n'

section "repository state"
if have git && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  printf 'git_root: %s\n' "$(git rev-parse --show-toplevel 2>/dev/null || true)"
  printf 'branch: %s\n' "$(git branch --show-current 2>/dev/null || true)"
  printf 'head: %s\n' "$(git rev-parse --short HEAD 2>/dev/null || true)"
  printf 'status_short:\n'
  git status --short 2>/dev/null || true
else
  echo "not a git worktree or git unavailable"
fi

section "build/test/runtime manifests"
find . -maxdepth "$MAX_DEPTH" -type f \( \
  -name package.json -o -name pnpm-workspace.yaml -o -name yarn.lock -o -name package-lock.json -o -name turbo.json -o -name nx.json -o \
  -name Makefile -o -name justfile -o -name Taskfile.yml -o -name Taskfile.yaml -o \
  -name pyproject.toml -o -name requirements.txt -o -name poetry.lock -o -name uv.lock -o -name Pipfile -o \
  -name go.mod -o -name Cargo.toml -o -name pom.xml -o -name build.gradle -o -name build.gradle.kts -o -name gradle.properties -o \
  -name Dockerfile -o -name docker-compose.yml -o -name compose.yaml -o \
  -name '.gitlab-ci.yml' -o -name Jenkinsfile -o -name Chart.yaml -o -name kustomization.yaml -o -name '*.tf' \
\) -print 2>/dev/null | sort

section "package scripts and likely proof commands"
if [ -f package.json ] && have python3; then
  python3 - <<'PY_PACKAGE_SCRIPTS' || true
import json
from pathlib import Path
try:
    data = json.loads(Path('package.json').read_text())
except Exception as exc:
    print(f'package.json parse failed: {exc}')
else:
    scripts = data.get('scripts') or {}
    if not scripts:
        print('no scripts')
    for name, cmd in sorted(scripts.items()):
        marker = '  [proof?]' if any(k in name.lower() for k in ('test','check','lint','type','build','verify')) else ''
        print(f'{name}: {cmd}{marker}')
PY_PACKAGE_SCRIPTS
else
  echo "no root package.json or python3 unavailable"
fi

if contains_filter web; then
  section "web framework/build stack clues"
  search 'react|next|remix|vite|webpack|rollup|parcel|svelte|vue|angular|hydration|jsx|tsx|client router|css-in-js|styled-components|emotion|tailwind|postcss'
fi

if contains_filter infra; then
  section "ci/deploy/infra files"
  find . -maxdepth "$MAX_DEPTH" -type f \( \
    -path './.github/workflows/*' -o -path './.gitlab-ci.yml' -o -name Jenkinsfile -o \
    -name Dockerfile -o -name docker-compose.yml -o -name compose.yaml -o \
    -name Chart.yaml -o -name values.yaml -o -name kustomization.yaml -o -name '*.tf' \
  \) -print 2>/dev/null | sort
  section "infra abstraction clues"
  search 'helm|kustomize|terraform|pulumi|kubernetes|k8s|service mesh|istio|envoy|module "|resource "|chart|values\.yaml|overlay'
fi

if contains_filter codegen; then
  section "generated-file clues"
  find . -maxdepth "$MAX_DEPTH" -type f \( \
    -name '*generated*' -o -name '*.gen.*' -o -name '*.generated.*' -o -name 'openapi.*' -o -name 'schema.graphql' -o -name '*.graphql' -o -name '*.proto' \
  \) -print 2>/dev/null | sort
  section "codegen and schema clues"
  search 'codegen|generate|generated|openapi|swagger|graphql-codegen|protoc|prisma generate|sqlc|buf generate|apollo|relay|schema\.graphql'
fi

if contains_filter single-impl; then
  section "single-implementation abstraction clues"
  search 'interface [A-Z][A-Za-z0-9_]*|abstract class|implements [A-Z][A-Za-z0-9_]*|protocol [A-Z][A-Za-z0-9_]*|trait [A-Z][A-Za-z0-9_]*|class .*Service|class .*Repository|type .* interface'
fi

section "likely abstraction signals"
search 'codegen|generate|generated|plugin|registry|middleware|decorator|reflect|container|inject|provider|adapter|factory|graphql|resolver|schema|prisma|typeorm|sequelize|knex|drizzle|hibernate|activerecord|helm|kustomize|terraform|pulumi|turbo|nx|bazel|vite|webpack|rollup|module federation|service mesh|istio|envoy|workflow|state machine|event bus|queue'

section "routing/request-path candidates"
search 'route|router|controller|handler|endpoint|middleware|resolver|loader|action|serverless|lambda|webhook|consumer|listener|command|job|worker'

if contains_filter proof-commands; then
  section "proof command clues"
  search '"(test|check|lint|typecheck|build|verify)[^"]*"\s*:|pytest|go test|cargo test|mvn test|gradle test|tsc|vitest|jest|playwright|cypress|rspec|phpunit'
fi

section "next manual checks"
cat <<'TEXT_NEXT_CHECKS'
1. Trace one real behavior path: input -> validation -> core rule -> persistence -> output.
2. For each candidate layer, record call sites, tests, deploy/runtime config, public/external surfaces, and rollback.
3. Run the essential-abstraction check before replace/delete.
4. Score T/V/D only after evidence is tied to a concrete layer.
5. Treat this scan as inventory, not proof of safe deletion.
TEXT_NEXT_CHECKS
