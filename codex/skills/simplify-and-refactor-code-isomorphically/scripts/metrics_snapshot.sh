#!/usr/bin/env bash
# metrics_snapshot.sh — compute the seven dashboard metrics.
# See references/METRICS-DASHBOARD.md.
#
# Usage: metrics_snapshot.sh [run-id] [src-dir]
# Writes JSON to stdout and to <workspace>/metrics.json

set -euo pipefail

RUN_ID="${1:-$(date +%Y-%m-%d)-pass-1}"
SRC="${2:-.}"
ART="refactor/artifacts/${RUN_ID}"
mkdir -p "$ART"
OUT="$ART/metrics.json"

have() { command -v "$1" >/dev/null 2>&1; }

# 1. LOC
loc="null"
if have tokei; then
  loc=$(tokei --output json "$SRC" 2>/dev/null | grep -oE '"code":\s*[0-9]+' | head -1 | awk -F: '{print $2}' | tr -d ' ' || echo "null")
elif have scc; then
  loc=$(scc --format json "$SRC" 2>/dev/null | grep -oE '"Code":\s*[0-9]+' | head -1 | awk -F: '{print $2}' | tr -d ' ' || echo "null")
fi

# 2. Duplication index (jscpd if available)
dup_pct="null"
if have jscpd && [[ -n "$(find "$SRC" -maxdepth 2 -name '*.ts' -o -name '*.tsx' 2>/dev/null | head -1)" ]]; then
  scan_dir="$ART/scans/jscpd-metrics"
  mkdir -p "$scan_dir"
  if jscpd --min-tokens 50 --reporters json --output "$scan_dir" "$SRC" >/dev/null 2>&1; then
    if [[ -f "$scan_dir/jscpd-report.json" ]]; then
      dup_pct=$(grep -oE '"percentage":\s*[0-9.]+' "$scan_dir/jscpd-report.json" | head -1 | awk -F: '{print $2}' | tr -d ' ' || echo "null")
    fi
  fi
fi

# 3. Cyclomatic (radon / gocyclo / lizard — best effort)
cc_mean="null"
if have radon && [[ -n "$(find "$SRC" -name '*.py' | head -1 2>/dev/null)" ]]; then
  cc_mean=$(radon cc -a -s "$SRC" 2>/dev/null | tail -1 | grep -oE '[0-9]+\.[0-9]+' | head -1 || echo "null")
elif have lizard; then
  cc_mean=$(lizard "$SRC" 2>/dev/null | grep -oE 'avg_CCN:\s*[0-9.]+' | awk '{print $2}' | head -1 || echo "null")
fi

# 4. Coupling (imports-out heuristic)
coupling_mean="null"
if have rg; then
  total=0; files=0
  while IFS= read -r f; do
    n=$(rg -c '^import |^use ' "$f" 2>/dev/null || echo 0)
    total=$(( total + n )); files=$(( files + 1 ))
  done < <(find "$SRC" -type f \( -name '*.ts' -o -name '*.tsx' -o -name '*.rs' -o -name '*.py' -o -name '*.go' \) 2>/dev/null | head -500)
  if (( files > 0 )); then
    coupling_mean=$(awk -v t="$total" -v f="$files" 'BEGIN { printf "%.2f", t/f }')
  fi
fi

# 5. Test pass count (best-effort per project type)
tests_pass="null"; tests_fail="null"; tests_skip="null"
# skip actual test run — metrics script is read-only; baseline.sh / verify.sh do the runs

# 6. Typecheck warnings (best-effort)
warnings="null"
if [[ -f Cargo.toml ]] && have cargo; then
  warnings=$(cargo clippy --all-targets --message-format=short 2>&1 | grep -c '^warning:' || echo "0")
elif [[ -f package.json ]] && have npx; then
  warnings=$(npx --no-install tsc --noEmit 2>&1 | grep -c 'error TS' || echo "0")
elif [[ -f go.mod ]] && have go; then
  warnings=$(go vet ./... 2>&1 | wc -l | tr -d ' ' || echo "0")
fi

# 7. Bundle size (frontend only, best-effort)
bundle_kb="null"
if [[ -d dist ]]; then
  bundle_kb=$(find dist -name '*.js' -exec gzip -c {} \; 2>/dev/null | wc -c | awk '{printf "%.1f", $1/1024}' || echo "null")
elif [[ -d .next/static ]]; then
  bundle_kb=$(find .next/static -name '*.js' -exec gzip -c {} \; 2>/dev/null | wc -c | awk '{printf "%.1f", $1/1024}' || echo "null")
fi

# emit JSON
cat > "$OUT" <<EOF
{
  "run_id": "${RUN_ID}",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "commit": "$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')",
  "loc": ${loc},
  "dup_pct": ${dup_pct},
  "cc_mean": ${cc_mean},
  "coupling_mean": ${coupling_mean},
  "tests_pass": ${tests_pass},
  "tests_fail": ${tests_fail},
  "tests_skip": ${tests_skip},
  "warnings": ${warnings},
  "bundle_kb_gz": ${bundle_kb}
}
EOF

cat "$OUT"
echo "" >&2
echo "wrote $OUT" >&2
