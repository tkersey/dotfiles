#!/usr/bin/env bash
# scripts/archetype-calibrate.sh — Validate that CLI archetypes are meaningful.
#
# Run mini-mode against multiple CLIs in each archetype; compute within- vs
# cross-archetype variance on weighted_score. If within-archetype variance is
# significantly less than cross-archetype variance, archetypes are real
# clusters. If the variances are comparable, the archetype distinction is
# noise and CLI-ARCHETYPES.md needs revision.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/archetype-calibrate.sh <fixtures-jsonl> [--workdir DIR]

Run inventory + score-projection against each CLI in <fixtures-jsonl> and
report variance within / across archetypes.

Fixtures schema (one line per CLI):
  {"archetype": "single-action-tool", "binary": "/usr/bin/jq"}
  {"archetype": "single-action-tool", "binary": "/usr/bin/rg"}
  {"archetype": "subcommand-tree-cobra", "binary": "/usr/bin/gh"}
  ...

Args:
  <fixtures-jsonl>   Path to fixtures file (≥ 3 binaries per archetype recommended).
  --workdir DIR      Workdir for inventory output. Default: /tmp/archetype-calibrate.

Output:
  Markdown report on stdout. Per-archetype mean + stddev of inventory size.

Note: this version uses INVENTORY SIZE (surfaces × kind ratio) as a proxy for
archetype identity, since a real LLM-scoring run is too expensive for ≥ 15
fixtures. The proxy works well enough for archetype-cluster validation but
should be replaced with real weighted_score once a calibration corpus exists.

Exit codes:
  0  Within-archetype variance < cross-archetype variance (archetypes meaningful).
  1  Variances comparable; archetype distinction is noise.
  2  Bad args / missing fixtures.
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 2 ;;
esac

FIXTURES="$1"; shift
WORKDIR=/tmp/archetype-calibrate
need_value() {
  [ -n "${2:-}" ] || { echo "$1 requires a value" >&2; exit 2; }
  case "$2" in --*) echo "$1 requires a value, got option-like token: $2" >&2; exit 2 ;; esac
}
while [ "$#" -gt 0 ]; do
  case "$1" in
    --workdir) need_value "$1" "${2:-}"; WORKDIR="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

[ -f "$FIXTURES" ] || { echo "fixtures not found: $FIXTURES" >&2; exit 2; }
mkdir -p "$WORKDIR"

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Run inventory on each fixture and capture (archetype, total_surfaces, verb_ratio).
samples="$WORKDIR/samples.jsonl"
: > "$samples"

while IFS= read -r line; do
  [ -z "$line" ] && continue
  arch=$(echo "$line" | jq -r '.archetype')
  target_bin=$(echo "$line" | jq -r '.binary')
  if ! command -v "$target_bin" >/dev/null 2>&1 && [ ! -x "$target_bin" ]; then
    echo "skip: $target_bin not reachable" >&2
    continue
  fi
  out="$WORKDIR/inv_$(basename "$target_bin").jsonl"
  /usr/bin/timeout 60 bash "$SKILL_DIR/scripts/inventory_surfaces.sh" "$target_bin" --depth 1 > "$out" 2>/dev/null || true
  total=$(wc -l < "$out")
  # Discard fixtures the inventory script couldn't introspect — a 0-surface
  # data point poisons the variance calc since it's an artifact, not a CLI
  # property.
  if [ "$total" -eq 0 ]; then
    echo "skip: $target_bin produced 0 surfaces (inventory failed?)" >&2
    continue
  fi
  verbs=$(jq -c 'select(.kind == "verb")' "$out" 2>/dev/null | wc -l)
  flags=$(jq -c 'select(.kind == "flag")' "$out" 2>/dev/null | wc -l)
  jq -nc --arg arch "$arch" --arg target "$target_bin" --argjson total "$total" \
        --argjson verbs "$verbs" --argjson flags "$flags" \
        '{archetype: $arch, binary: $target, total: $total, verbs: $verbs, flags: $flags}' >> "$samples"
done < "$FIXTURES"

n_samples=$(wc -l < "$samples")
[ "$n_samples" -lt 3 ] && { echo "too few samples ($n_samples); need ≥ 3" >&2; exit 1; }

# Compute variance.
python3 - "$samples" <<'PY'
import json, sys, statistics
samples = []
for line in open(sys.argv[1]):
    line = line.strip()
    if not line: continue
    samples.append(json.loads(line))

# Group by archetype.
groups = {}
for s in samples:
    groups.setdefault(s['archetype'], []).append(s['total'])

print("# Archetype Calibration\n")
print(f"Samples: {len(samples)}\n")
print("## Per-archetype inventory size")
print()
print("| archetype | n | mean | stddev | range |")
print("|-----------|---|------|--------|-------|")
within_vars = []
for arch, totals in groups.items():
    if len(totals) < 2:
        print(f"| {arch} | {len(totals)} | {totals[0] if totals else 0} | (1 sample) | — |")
        continue
    mean = statistics.mean(totals)
    sd = statistics.stdev(totals)
    rng = f"{min(totals)}..{max(totals)}"
    print(f"| {arch} | {len(totals)} | {mean:.0f} | {sd:.0f} | {rng} |")
    within_vars.append(sd**2)

# Overall (cross-archetype) variance: pool all samples, compute spread.
all_totals = [s['total'] for s in samples]
overall_var = statistics.variance(all_totals) if len(all_totals) >= 2 else 0
mean_within_var = statistics.mean(within_vars) if within_vars else 0

print(f"\n## Variance comparison\n")
print(f"- Mean within-archetype variance: {mean_within_var:.0f}")
print(f"- Cross-archetype variance:       {overall_var:.0f}")

if overall_var > 0:
    ratio = mean_within_var / overall_var
    print(f"- Ratio (within / cross):         {ratio:.2f}")
    print()
    if ratio < 0.5:
        print("✅ PASS: archetypes are meaningful clusters (within-variance ≪ cross-variance).")
        sys.exit(0)
    elif ratio < 0.8:
        print("⚠️  WARN: archetypes weakly clustered. Distinction is meaningful but noisy.")
        sys.exit(0)
    else:
        print("❌ FAIL: archetypes don't cluster — distinction is noise. Revise CLI-ARCHETYPES.md.")
        sys.exit(1)
else:
    print("(no cross-archetype variance — only one archetype sampled)")
    sys.exit(1)
PY
