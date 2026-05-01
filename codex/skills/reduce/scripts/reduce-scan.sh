#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.}"
MAX_DEPTH="${REDUCE_SCAN_MAX_DEPTH:-5}"

if [ ! -d "$ROOT" ]; then
  echo "reduce-scan: root is not a directory: $ROOT" >&2
  exit 2
fi

cd "$ROOT"

section() {
  printf '\n== %s ==\n' "$1"
}

have() {
  command -v "$1" >/dev/null 2>&1
}

search() {
  # Usage: search PATTERN [PATH...]
  local pattern="$1"
  shift || true
  if have rg; then
    rg -n --hidden --glob '!node_modules' --glob '!vendor' --glob '!dist' --glob '!build' --glob '!coverage' --glob '!.git' "$pattern" "${@:-.}" || true
  else
    grep -RInE --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=vendor --exclude-dir=dist --exclude-dir=build --exclude-dir=coverage "$pattern" "${@:-.}" 2>/dev/null || true
  fi
}

section "reduce scan"
printf 'root: %s\n' "$(pwd)"
printf 'max_depth: %s\n' "$MAX_DEPTH"
printf 'timestamp_utc: %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || true)"

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

section "ci/deploy files"
find . -maxdepth "$MAX_DEPTH" -type f \( \
  -path './.github/workflows/*' -o -path './.gitlab-ci.yml' -o -name Jenkinsfile -o \
  -name Dockerfile -o -name docker-compose.yml -o -name compose.yaml -o \
  -name Chart.yaml -o -name values.yaml -o -name kustomization.yaml -o -name '*.tf' \
\) -print 2>/dev/null | sort

section "package scripts"
if [ -f package.json ] && have python3; then
  python3 - <<'PY' || true
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
        print(f'{name}: {cmd}')
PY
elif [ -f package.json ]; then
  grep -n '"scripts"' package.json || true
else
  echo "no root package.json"
fi

section "likely abstraction signals"
search 'codegen|generate|generated|plugin|registry|middleware|decorator|reflect|container|inject|provider|adapter|factory|graphql|resolver|schema|prisma|typeorm|sequelize|knex|drizzle|hibernate|activerecord|helm|kustomize|terraform|pulumi|turbo|nx|bazel|vite|webpack|rollup|module federation|service mesh|istio|envoy'

section "routing/request-path candidates"
search 'route|router|controller|handler|endpoint|middleware|resolver|loader|action|serverless|lambda|webhook|consumer|listener' .

section "generated-file clues"
find . -maxdepth "$MAX_DEPTH" -type f \( \
  -name '*generated*' -o -name '*.gen.*' -o -name '*.generated.*' -o -name 'openapi.*' -o -name 'schema.graphql' -o -name '*.graphql' -o -name '*.proto' \
\) -print 2>/dev/null | sort

section "single-implementation abstraction clues"
search 'interface [A-Z][A-Za-z0-9_]*|abstract class|implements [A-Z][A-Za-z0-9_]*|protocol [A-Z][A-Za-z0-9_]*|trait [A-Z][A-Za-z0-9_]*|class .*Service|class .*Repository|type .* interface' .

section "next manual checks"
cat <<'TEXT'
1. Trace one real behavior path: input -> validation -> core rule -> persistence -> output.
2. For each candidate layer, record call sites, tests, deploy/runtime config, and public/external surfaces.
3. Score T/V/D only after evidence is tied to a concrete layer.
4. Treat this scan as inventory, not proof of safe deletion.
TEXT
