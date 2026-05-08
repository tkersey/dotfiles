#!/usr/bin/env bash
# scripts/rubric-calibrate.sh — Validate the 11-dim rubric against expert judgment.
#
# Workflow:
#   1. User picks 10 surfaces from a known-well-scored CLI (gh's pr commands,
#      cargo's package commands, etc.) and writes them to a corpus JSONL.
#   2. Multiple human experts score each surface across all 11 dims —
#      independently — and append their scores to the corpus.
#   3. The skill runs its LLM scorer subagents on the same surfaces.
#   4. This script computes Spearman correlation between LLM medians and
#      expert medians per dim. Reports pass/fail per dim + overall.
#
# Required threshold: ≥ 0.7 mean correlation across dims. Any dim < 0.5 means
# the rubric anchors for that dim are mis-tuned and need revision before the
# skill can be trusted.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/rubric-calibrate.sh <calibration-corpus.jsonl> <llm-scores.jsonl>

Compute Spearman rank correlation per dim between expert and LLM scores.

Inputs:
  <calibration-corpus.jsonl>   One record per surface, schema:
    {
      "surface_id": "verb__pr_create",
      "expert_scores": {
        "expert_a": {"agent_intuitiveness": 720, ...},
        "expert_b": {"agent_intuitiveness": 700, ...},
        "expert_c": {"agent_intuitiveness": 750, ...}
      }
    }
    See assets/calibration-corpus-template.jsonl for the template.

  <llm-scores.jsonl>          The result of running the LLM scorer subagent
                              on the same surfaces (raw partials concatenated,
                              or aggregated agent_surfaces.jsonl rows).

Output (markdown to stdout):
  - Per-dim Spearman ρ (LLM-median vs expert-median)
  - Overall mean ρ
  - PASS / FAIL per dim (threshold: ρ ≥ 0.7 PASS, ρ ∈ [0.5, 0.7) WARN, ρ < 0.5 FAIL)
  - List of surfaces where LLM and expert disagreed by ≥ 200 pts on any dim

Exit codes:
  0  Mean ρ ≥ 0.7 (rubric calibrated; skill output trustable)
  1  Mean ρ ∈ [0.5, 0.7) (rubric needs revision)
  2  Mean ρ < 0.5 OR any dim < 0.3 (rubric is mis-anchored)
  3  Bad args / missing files
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  ""|--*)    usage >&2; exit 3 ;;
esac

CORPUS="$1"
LLM="${2:-}"

[ -f "$CORPUS" ] || { echo "calibration corpus not found: $CORPUS" >&2; exit 3; }
if [ -z "$LLM" ] || [ ! -f "$LLM" ]; then
  echo "llm-scores file not found: $LLM" >&2
  exit 3
fi

# Use python for the Spearman rank correlation — bash arithmetic doesn't do
# floats and reimplementing rank-corr in awk is more bugs than it's worth.
python3 - "$CORPUS" "$LLM" <<'PY'
import json
import sys
from statistics import median

corpus_path, llm_path = sys.argv[1], sys.argv[2]

DIMS = [
    'agent_intuitiveness','agent_ergonomics','agent_ease_of_use',
    'output_parseability','error_pedagogy','intent_inference',
    'safety_with_recovery','determinism_and_reproducibility',
    'self_documentation','composability','regression_resistance'
]

# Load expert scores: {surface_id: {dim: median_across_experts}}
expert = {}
with open(corpus_path) as f:
    for line in f:
        line = line.strip()
        if not line: continue
        rec = json.loads(line)
        sid = rec['surface_id']
        # Median across experts per dim
        per_dim = {}
        for dim in DIMS:
            vals = []
            for exp_id, scores in rec.get('expert_scores', {}).items():
                v = scores.get(dim)
                if v is not None: vals.append(v)
            if vals: per_dim[dim] = median(vals)
        expert[sid] = per_dim

# Load LLM scores: support both partial scorer rows (one per scorer per surface)
# and aggregated final rows (one per surface). For partials, take median per dim.
llm_partials = {}
with open(llm_path) as f:
    for line in f:
        line = line.strip()
        if not line: continue
        rec = json.loads(line)
        sid = rec.get('surface_id')
        if not sid: continue
        scores = rec.get('scores', {})
        llm_partials.setdefault(sid, []).append(scores)

llm = {}
for sid, partials in llm_partials.items():
    per_dim = {}
    for dim in DIMS:
        vals = [p[dim] for p in partials if p.get(dim) is not None]
        if vals: per_dim[dim] = median(vals)
    llm[sid] = per_dim

# Surfaces present in both.
common = sorted(set(expert.keys()) & set(llm.keys()))
if len(common) < 5:
    print(f"## ERROR: only {len(common)} surfaces in common between corpus and LLM scores; need ≥ 5 for meaningful correlation")
    sys.exit(3)

def spearman(xs, ys):
    """Spearman rank correlation (handles ties via average rank)."""
    n = len(xs)
    if n < 2: return None
    def ranks(vals):
        sorted_idx = sorted(range(n), key=lambda i: vals[i])
        r = [0.0]*n
        i = 0
        while i < n:
            j = i
            while j+1 < n and vals[sorted_idx[j+1]] == vals[sorted_idx[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j+1):
                r[sorted_idx[k]] = avg
            i = j+1
        return r
    rx, ry = ranks(xs), ranks(ys)
    mean_x, mean_y = sum(rx)/n, sum(ry)/n
    cov = sum((rx[i]-mean_x)*(ry[i]-mean_y) for i in range(n))
    var_x = sum((rx[i]-mean_x)**2 for i in range(n))
    var_y = sum((ry[i]-mean_y)**2 for i in range(n))
    if var_x == 0 or var_y == 0: return None
    return cov / (var_x*var_y)**0.5

print(f"# Rubric Calibration Report")
print()
print(f"Surfaces in calibration corpus: {len(expert)}")
print(f"Surfaces in LLM-score input:    {len(llm)}")
print(f"Surfaces in common:             {len(common)}")
print()
print(f"## Per-dim Spearman correlation (LLM-median vs expert-median)")
print()
print(f"| dim | ρ | verdict |")
print(f"|-----|---|---------|")

rhos = []
worst_dim_rho = 1.0
for dim in DIMS:
    xs, ys = [], []
    for sid in common:
        ex = expert[sid].get(dim)
        lm = llm[sid].get(dim)
        if ex is not None and lm is not None:
            xs.append(ex); ys.append(lm)
    if len(xs) < 5:
        print(f"| {dim} | — | INSUFFICIENT_DATA ({len(xs)} pairs) |")
        continue
    rho = spearman(xs, ys)
    if rho is None:
        print(f"| {dim} | — | NO_VARIANCE |")
        continue
    rhos.append(rho)
    worst_dim_rho = min(worst_dim_rho, rho)
    if rho >= 0.7: verdict = "PASS"
    elif rho >= 0.5: verdict = "WARN"
    else: verdict = "FAIL"
    print(f"| {dim} | {rho:.3f} | {verdict} |")

mean_rho = sum(rhos)/len(rhos) if rhos else 0
print()
print(f"## Overall")
print()
print(f"- Mean ρ across dims: **{mean_rho:.3f}**")
print(f"- Worst-dim ρ:        **{worst_dim_rho:.3f}**")

# Disagreements
print()
print(f"## Surfaces with ≥ 200pt disagreement on any dim")
print()
shown = 0
for sid in common:
    for dim in DIMS:
        ex = expert[sid].get(dim)
        lm = llm[sid].get(dim)
        if ex is not None and lm is not None and abs(ex - lm) >= 200:
            print(f"- {sid} on {dim}: expert={ex}, LLM={lm}, Δ={lm-ex:+d}")
            shown += 1
            if shown >= 20:
                print(f"... (truncated; see full output for more)")
                break
    if shown >= 20: break
if shown == 0:
    print("(none — LLM and expert agreed within 200pts on all surface×dim pairs)")

# Exit code reflects calibration verdict.
if worst_dim_rho < 0.3 or mean_rho < 0.5:
    sys.exit(2)
elif mean_rho < 0.7:
    sys.exit(1)
sys.exit(0)
PY
