#!/usr/bin/env bash
# scripts/cluster-recommendations.sh — Dedup near-duplicate recommendations.
#
# Phase 4 typically produces N raw recs from M surfaces, where many recs are
# the SAME canonical pattern applied to different surfaces (e.g., "add
# levenshtein typo correction for --json", "add levenshtein typo correction
# for --colour", ...). Clustering merges these into one canonical
# recommendation covering all member surfaces, dramatically reducing Phase 5
# applier load and reviewer cognitive cost.
#
# Algorithm:
#   1. For each rec, derive a clustering signature:
#        sig = (sorted(touched_dims), normalize(diff_sketch_keywords),
#               anchor_pattern, sorted(operators_applied))
#   2. Group recs whose signatures share enough components; the default requires
#      3 of the 4 signature components (dims, keywords, anchor_pattern,
#      operators).
#   3. Within each group, pick the rec with the highest expected_uplift_total
#      as canonical; merge the others' surface_ids into it; record member IDs.
#   4. Emit recommendations.clustered.jsonl alongside the input file.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/cluster-recommendations.sh <sibling> [--threshold N]

Cluster near-duplicate recommendations from <sibling>/audit/recommendations.jsonl
into canonical recs at <sibling>/audit/recommendations.clustered.jsonl.

Args:
  <sibling>      Audit workspace root.
  --threshold N  Minimum signature-overlap to merge (default 3; range 1-4).
                 Higher = stricter (fewer merges); lower = looser.

Output (markdown to stdout):
  Per-cluster summary: cluster_id, member count, total surfaces covered, max
  expected uplift, canonical title.

Cluster file schema (recommendations.clustered.jsonl):
  {
    "cluster_id": "C-01",
    "canonical_recommendation_id": "R-007",
    "title": "<canonical title>",
    "member_recommendation_ids": ["R-007", "R-012", "R-018"],
    "surface_ids": ["flag__list__json", "flag__add__json", ...],
    "touched_dims": ["intent_inference", "error_pedagogy"],
    "expected_uplift_total": 600,
    "anchor_pattern": "Pattern 2 from CANONICAL-EXEMPLARS",
    "members_count": 3,
    "surfaces_count": 8
  }

Exit codes:
  0  Clustering produced (even if every rec is its own cluster).
  1  Bad args / no input recs.
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 1 ;;
esac

die() {
  echo "$*" >&2
  exit 1
}
need_value() {
  [ -n "${2:-}" ] || die "$1 requires a value"
  case "$2" in --*) die "$1 requires a value, got option-like token: $2" ;; esac
}

SIBLING="$1"; shift
# Default threshold = 3 (out of 4 signature components: dims, keywords,
# anchor_pattern, operators). 2 is too loose — the operators ① and 🩹 apply
# to almost every ergonomic fix, and "same dims" is a weak signal because
# many recommendations target the same low-scoring dim families. With
# 2-of-4 the dogfood saw recs from different anchor patterns (Pattern-1
# typo-correction vs Pattern-6 structured-error) merge into one cluster.
# With 3-of-4 at least one of {keywords, anchor_pattern} must overlap in
# addition to {dims, operators}, which catches genuine semantic overlap
# without false-merging unrelated fixes.
THRESHOLD=3
while [ "$#" -gt 0 ]; do
  case "$1" in
    --threshold)
      need_value "$1" "${2:-}"
      THRESHOLD="$2"; shift 2
      ;;
    *) die "unknown arg: $1" ;;
  esac
done

case "$THRESHOLD" in
  ''|*[!0-9]*) die "bad --threshold: $THRESHOLD (expected integer 1-4)" ;;
esac
if [ "$THRESHOLD" -lt 1 ] || [ "$THRESHOLD" -gt 4 ]; then
  die "bad --threshold: $THRESHOLD (expected integer 1-4)"
fi

RECS="$SIBLING/audit/recommendations.jsonl"
OUT="$SIBLING/audit/recommendations.clustered.jsonl"
[ -f "$RECS" ] || { echo "no recs file: $RECS" >&2; exit 1; }

n_in=$(wc -l < "$RECS")
[ "$n_in" -eq 0 ] && { echo "empty recs file" >&2; exit 1; }

# Use python for the actual clustering — bash + jq is too slow / brittle for
# this. Python reads the JSONL, builds signatures, groups by overlap.
python3 - "$RECS" "$OUT" "$THRESHOLD" <<'PY'
import json, sys, re

recs_path, out_path, thr_s = sys.argv[1], sys.argv[2], sys.argv[3]
threshold = int(thr_s)

# Load recs.
recs = []
with open(recs_path) as f:
    for line in f:
        line = line.strip()
        if not line: continue
        recs.append(json.loads(line))

if not recs:
    sys.exit(0)

STOP = {'add','the','a','an','to','of','for','in','with','and','or','if','is','that','use','using'}
def keywords(text):
    """Tokenize a diff_sketch / title; return frozenset of significant tokens."""
    if not text: return frozenset()
    tokens = re.findall(r'[a-z0-9_-]+', text.lower())
    sig = {t for t in tokens if len(t) > 2 and t not in STOP}
    return frozenset(sig)

def signature(rec):
    """Return a tuple of (touched_dims, kw_set, anchor_pattern, ops_set)."""
    dims = frozenset((rec.get('expected_uplift_per_dim') or {}).keys())
    sketch_kw = keywords(rec.get('diff_sketch', ''))
    title_kw = keywords(rec.get('title', ''))
    kw = sketch_kw | title_kw
    anchor = (rec.get('anchor_pattern') or '').strip()
    ops = frozenset(rec.get('operators_applied') or [])
    return (dims, kw, anchor, ops)

def overlap_score(s1, s2):
    """Count how many of (dims-jaccard ≥ 0.5, kw-jaccard ≥ 0.3, same anchor,
       ops-jaccard ≥ 0.5) hold between two signatures."""
    dims1, kw1, anchor1, ops1 = s1
    dims2, kw2, anchor2, ops2 = s2
    n = 0
    # Dims
    if dims1 and dims2:
        d_inter = len(dims1 & dims2); d_union = len(dims1 | dims2)
        if d_union > 0 and d_inter / d_union >= 0.5: n += 1
    # Keywords
    if kw1 and kw2:
        k_inter = len(kw1 & kw2); k_union = len(kw1 | kw2)
        if k_union > 0 and k_inter / k_union >= 0.3: n += 1
    # Anchor
    if anchor1 and anchor2 and anchor1 == anchor2: n += 1
    # Operators
    if ops1 and ops2:
        o_inter = len(ops1 & ops2); o_union = len(ops1 | ops2)
        if o_union > 0 and o_inter / o_union >= 0.5: n += 1
    return n

# Greedy clustering: each rec joins the first existing cluster it's similar
# enough to; otherwise starts a new cluster.
sigs = [(rec, signature(rec)) for rec in recs]
clusters = []  # list of {recs:[...], sig_repr:(...)}
for rec, sig in sigs:
    placed = False
    for cluster in clusters:
        if overlap_score(sig, cluster['sig_repr']) >= threshold:
            cluster['recs'].append(rec)
            placed = True
            break
    if not placed:
        clusters.append({'recs': [rec], 'sig_repr': sig})

# Emit clustered records.
with open(out_path, 'w') as outf:
    for i, cluster in enumerate(clusters, 1):
        members = cluster['recs']
        # Pick canonical = highest expected_uplift_total (ties: lowest rec id).
        canonical = max(members, key=lambda r: (r.get('expected_uplift_total', 0),
                                                -int(re.sub(r'\D','', r['recommendation_id']) or 0)))
        all_sids = sorted({s for m in members for s in (m.get('surface_ids') or [])})
        all_dims = sorted({d for m in members for d in (m.get('expected_uplift_per_dim') or {}).keys()})
        clustered = {
            'cluster_id': f'C-{i:02d}',
            'canonical_recommendation_id': canonical['recommendation_id'],
            'title': canonical.get('title', '(no title)'),
            'member_recommendation_ids': sorted(m['recommendation_id'] for m in members),
            'surface_ids': all_sids,
            'touched_dims': all_dims,
            'expected_uplift_total': max((m.get('expected_uplift_total') or 0) for m in members),
            'anchor_pattern': canonical.get('anchor_pattern', ''),
            'members_count': len(members),
            'surfaces_count': len(all_sids)
        }
        outf.write(json.dumps(clustered) + '\n')

# Print summary.
print('# Recommendation Clustering Report')
print()
print(f'- Input recommendations: {len(recs)}')
print(f'- Output clusters: {len(clusters)}')
print(f'- Compression ratio: {len(recs) / max(1, len(clusters)):.1f}x')
print(f'- Output: `{out_path}`')
print()
print('## Per-cluster summary')
print()
print('| cluster | canonical | members | surfaces | uplift | title |')
print('|---------|-----------|---------|----------|--------|-------|')
for i, cluster in enumerate(clusters, 1):
    members = cluster['recs']
    canonical = max(members, key=lambda r: (r.get('expected_uplift_total', 0),
                                            -int(re.sub(r'\D','', r['recommendation_id']) or 0)))
    all_sids = sorted({s for m in members for s in (m.get('surface_ids') or [])})
    title = canonical.get('title', '(no title)')[:50]
    print(f'| C-{i:02d} | {canonical["recommendation_id"]} | {len(members)} | {len(all_sids)} | +{canonical.get("expected_uplift_total", 0)} | {title} |')
PY
exit 0
