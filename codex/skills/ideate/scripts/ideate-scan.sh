#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.}"
cd "$ROOT"

section() {
  printf '\n## %s\n' "$1"
}

have() {
  command -v "$1" >/dev/null 2>&1
}

run_rg() {
  local pattern="$1"
  shift || true
  if have rg; then
    rg -n --hidden \
      --glob '!{.git,node_modules,dist,build,target,vendor,.venv,coverage}/**' \
      "$pattern" . "$@" || true
  else
    grep -RInE \
      --exclude-dir=.git \
      --exclude-dir=node_modules \
      --exclude-dir=dist \
      --exclude-dir=build \
      --exclude-dir=target \
      --exclude-dir=vendor \
      --exclude-dir=.venv \
      --exclude-dir=coverage \
      "$pattern" . || true
  fi
}

section "Project guidance"
find . -maxdepth 4 \( \
  -name 'AGENTS.md' -o \
  -name 'README*' -o \
  -name 'CONTRIBUTING*' -o \
  -name 'ARCHITECTURE*' -o \
  -name 'CHANGELOG*' -o \
  -name 'ROADMAP*' -o \
  -name 'TODO*' \
\) -print | sort | head -200

section "Docs and design notes"
find . -maxdepth 4 -type f \( \
  -path './docs/*' -o \
  -path './doc/*' -o \
  -path './adr/*' -o \
  -path './adrs/*' -o \
  -path './design/*' -o \
  -path './notes/*' \
\) -print | sort | head -200

section "Manifests, build, and config"
find . -maxdepth 4 -type f \( \
  -name 'package.json' -o \
  -name 'Cargo.toml' -o \
  -name 'pyproject.toml' -o \
  -name 'go.mod' -o \
  -name 'pom.xml' -o \
  -name 'build.gradle*' -o \
  -name 'Makefile' -o \
  -name 'justfile' -o \
  -name 'Taskfile.yml' -o \
  -name '*.config.js' -o \
  -name '*.config.ts' -o \
  -name '*.yml' -o \
  -name '*.yaml' -o \
  -name '*.toml' \
\) -print | sort | head -250

section "CI and automation"
find . -maxdepth 5 -type f \( \
  -path './.github/workflows/*' -o \
  -path './.gitlab-ci.yml' -o \
  -path './.circleci/*' -o \
  -path './scripts/*' -o \
  -path './bin/*' \
\) -print | sort | head -250

section "Friction comments"
run_rg 'TODO|FIXME|HACK|XXX|temporary|workaround|deprecated|flaky|slow|brittle|confusing|cleanup|refactor|tech debt|manual step|follow[- ]?up'

section "Public surfaces and entry points"
run_rg 'fn main|def main|if __name__|func main|public static void main|createRoot|FastAPI\(|Flask\(|express\(|Router\(|app\.(get|post|put|delete)|export default|module\.exports|commander|yargs|click|typer|cobra|clap|argparse|subcommand|route\(|controller|handler|endpoint'

section "Errors, diagnostics, and observability"
run_rg 'throw new|raise |panic!|expect\(|unwrap\(|console\.error|logger\.|log\.|debug\(|trace\(|warn\(|error\(|diagnostic|telemetry|metrics|span|status|health|doctor|explain'

section "Reliability and recovery hints"
run_rg 'retry|timeout|rollback|cleanup|finally|defer |idempot|transaction|migration|lock|race|concurrent|queue|resume|recover|partial|validate|schema|sanitize'

section "Performance hints"
run_rg 'cache|memo|batch|stream|lazy|eager|serialize|deserialize|for .* in|while |N\+1|benchmark|bench|perf|slow|startup|hot path|optimi[sz]e'

section "Test surfaces"
find . -maxdepth 5 -type d \( \
  -name test -o \
  -name tests -o \
  -name __tests__ -o \
  -name spec -o \
  -name specs -o \
  -name fixtures \
\) -print | sort | head -200
run_rg 'describe\(|it\(|test\(|pytest|unittest|#\[test\]|func Test|@Test|assert|expect\(|snapshot|golden|fixture|mock|stub'

section "Large tracked files"
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git ls-files | while IFS= read -r file; do
    case "$file" in
      *.png|*.jpg|*.jpeg|*.gif|*.webp|*.pdf|*.zip|*.gz|*.lock) continue ;;
    esac
    [ -f "$file" ] || continue
    lines=$(wc -l < "$file" 2>/dev/null || echo 0)
    printf '%8s %s\n' "$lines" "$file"
  done | sort -nr | head -50
else
  echo "Not a git repository; skipping large tracked file scan."
fi

section "Recent churn"
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git log --since='90 days ago' --name-only --pretty=format: 2>/dev/null \
    | sed '/^$/d' \
    | sort \
    | uniq -c \
    | sort -nr \
    | head -50 || true
else
  echo "Not a git repository; skipping churn scan."
fi

section "Recent commit subjects"
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git log --since='90 days ago' --pretty=format:'%h %ad %s' --date=short 2>/dev/null | head -80 || true
else
  echo "Not a git repository; skipping recent commit scan."
fi

section "Scan note"
echo "This is a read-only signal index. Use it to seed hypotheses, then verify the relevant files directly before ranking ideas."
