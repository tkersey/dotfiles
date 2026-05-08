#!/usr/bin/env bash
# scripts/rubric-fitness.sh — Single-number rubric quality metric.
#
# rubric-calibrate.sh produces 11 ρ values + a verdict. That's the right
# tool for diagnosis, but for tracking rubric quality over time (e.g. across
# rubric revisions), one number is more useful: a "fitness score" that bakes
# correlation, dim coverage, and disagreement spread into one figure.
#
# Fitness =     0.50 * mean(ρ)                        # rank-correlation
#             + 0.30 * (1 - max_disagreement / 1000)  # absolute-distance penalty
#             + 0.20 * fraction_of_dims_with_ρ>=0.7   # coverage of the rubric
#
# Output: one number ∈ [0.0, 1.0]. ≥ 0.75 = excellent. 0.50–0.74 = acceptable.
# < 0.50 = revise rubric.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/rubric-fitness.sh <calibration-corpus.jsonl> <llm-scores.jsonl>

Computes a SINGLE fitness number for the 11-dim rubric.

Fitness formula:
  F = 0.50 * mean(spearman_per_dim)
    + 0.30 * (1 - max_disagreement / 1000)
    + 0.20 * (fraction of dims with ρ >= 0.7)

Inputs: same as scripts/rubric-calibrate.sh (corpus + LLM partials).

Output:
  Single line: "rubric_fitness: 0.812"
  Also a one-line breakdown of the three components.

Exit codes:
  0  Fitness ≥ 0.75 (rubric excellent)
  1  Fitness ∈ [0.5, 0.75) (acceptable; consider revisions)
  2  Fitness < 0.5 (rubric needs major revision)
  3  Bad args / missing files

Use this in CI to track rubric quality across changes to SCORING-RUBRIC.md.
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  ""|--*)    usage >&2; exit 3 ;;
esac

CORPUS="$1"
LLM="${2:-}"
[ -f "$CORPUS" ] || { echo "corpus not found: $CORPUS" >&2; exit 3; }
if [ -z "$LLM" ] || [ ! -f "$LLM" ]; then
  echo "llm scores not found: $LLM" >&2; exit 3
fi

python3 - "$CORPUS" "$LLM" <<'PY'
import json, sys
from statistics import median

corpus_path, llm_path = sys.argv[1], sys.argv[2]

DIMS = [
    'agent_intuitiveness','agent_ergonomics','agent_ease_of_use',
    'output_parseability','error_pedagogy','intent_inference',
    'safety_with_recovery','determinism_and_reproducibility',
    'self_documentation','composability','regression_resistance'
]

expert = {}
with open(corpus_path) as f:
    for line in f:
        line=line.strip()
        if not line: continue
        rec = json.loads(line)
        sid = rec['surface_id']
        per_dim = {}
        for dim in DIMS:
            vals = [s.get(dim) for s in rec.get('expert_scores', {}).values()
                    if s.get(dim) is not None]
            if vals: per_dim[dim] = median(vals)
        expert[sid] = per_dim

llm_partials = {}
with open(llm_path) as f:
    for line in f:
        line=line.strip()
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

common = sorted(set(expert) & set(llm))
if len(common) < 5:
    print(f"INSUFFICIENT_DATA: only {len(common)} surfaces in common")
    sys.exit(3)

def spearman(xs, ys):
    n = len(xs)
    if n < 2: return None
    def ranks(vals):
        order = sorted(range(n), key=lambda i: vals[i])
        r = [0.0]*n
        i = 0
        while i < n:
            j = i
            while j+1 < n and vals[order[j+1]] == vals[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j+1):
                r[order[k]] = avg
            i = j+1
        return r
    rx, ry = ranks(xs), ranks(ys)
    mx, my = sum(rx)/n, sum(ry)/n
    cov = sum((rx[i]-mx)*(ry[i]-my) for i in range(n))
    vx = sum((rx[i]-mx)**2 for i in range(n))
    vy = sum((ry[i]-my)**2 for i in range(n))
    if vx == 0 or vy == 0: return None
    return cov / (vx*vy)**0.5

rhos = []
max_disagreement = 0
for dim in DIMS:
    xs, ys = [], []
    for sid in common:
        ex = expert[sid].get(dim); lm = llm[sid].get(dim)
        if ex is not None and lm is not None:
            xs.append(ex); ys.append(lm)
            max_disagreement = max(max_disagreement, abs(ex-lm))
    if len(xs) < 5: continue
    r = spearman(xs, ys)
    if r is not None: rhos.append(r)

if not rhos:
    print("INSUFFICIENT_DATA: no dim had ≥ 5 valid pairs")
    sys.exit(3)

mean_rho = sum(rhos) / len(rhos)
frac_strong = sum(1 for r in rhos if r >= 0.7) / len(rhos)
disagreement_term = 1 - min(max_disagreement, 1000) / 1000

fitness = 0.50 * mean_rho + 0.30 * disagreement_term + 0.20 * frac_strong

print(f"rubric_fitness: {fitness:.3f}")
print(f"  components: mean_rho={mean_rho:.3f}, disagreement_term={disagreement_term:.3f} (max_disagreement={max_disagreement}), frac_dims_with_rho>=0.7={frac_strong:.2f}")
print(f"  dims_evaluated: {len(rhos)}/11; surfaces_compared: {len(common)}")

if fitness >= 0.75:
    sys.exit(0)
elif fitness >= 0.50:
    sys.exit(1)
else:
    sys.exit(2)
PY
