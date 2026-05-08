#!/usr/bin/env bash
# tools/generate-pr-comment.sh — Reviewer-facing PR comment from an audit.
#
# audit-narrative.sh produces a complete multi-pass story for handoffs. This
# tool produces a SHORT, REVIEWER-FOCUSED comment for the actual PR thread:
# what changed, what improved, what to look at. Designed to fit GitHub's
# default expanded view (~30 lines) without truncation.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: tools/generate-pr-comment.sh <sibling> [--pass N] [--target-repo PATH]

Generate a tight markdown comment summarizing one pass for PR review.

Args:
  <sibling>           Audit workspace root.
  --pass N            Which pass to report on (default: latest).
  --target-repo PATH  Target repo, for embedding commit links (optional).
  --include-regressions  Also include any score regressions (default: yes).

Output:
  Markdown to stdout, suitable for `gh pr comment --body-file`.

Sections:
  - One-liner verdict (passed Polish-Bar / didn't / regressed).
  - Top 3 wins (by uplift).
  - Surfaces still below 750 (Polish-Bar).
  - Per-dim deltas vs prior pass (compact 11-column table).
  - Regression test plan checkboxes.

Exit codes:
  0  Comment generated.
  1  Bad args / missing inputs.
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

SIBLING="$1"; shift
PASS=""
TARGET_REPO=""
INCLUDE_REGRESSIONS=1
need_value() {
  [ -n "${2:-}" ] || die "$1 requires a value"
  case "$2" in --*) die "$1 requires a value, got option-like token: $2" ;; esac
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --pass)
      need_value "$1" "${2:-}"
      PASS="$2"; shift 2
      ;;
    --target-repo)
      need_value "$1" "${2:-}"
      TARGET_REPO="$2"; shift 2
      ;;
    --include-regressions)  INCLUDE_REGRESSIONS=1; shift ;;
    --no-regressions)       INCLUDE_REGRESSIONS=0; shift ;;
    *) die "unknown arg: $1" ;;
  esac
done

AUDIT="$SIBLING/audit"
SURFACES="$AUDIT/agent_surfaces.jsonl"
RECS="$AUDIT/recommendations.jsonl"
APPLIED="$AUDIT/applied_changes.jsonl"
MANIFEST="$AUDIT/manifest.json"

[ -f "$SURFACES" ] || { echo "no surfaces file: $SURFACES" >&2; exit 1; }

commit_base_url=""
if [ -n "$TARGET_REPO" ] && git -C "$TARGET_REPO" rev-parse --git-dir >/dev/null 2>&1; then
  remote_url=$(git -C "$TARGET_REPO" remote get-url origin 2>/dev/null || true)
  case "$remote_url" in
    git@github.com:*)
      repo_slug=${remote_url#git@github.com:}
      repo_slug=${repo_slug%.git}
      commit_base_url="https://github.com/$repo_slug/commit"
      ;;
    https://github.com/*)
      repo_slug=${remote_url#https://github.com/}
      repo_slug=${repo_slug%.git}
      commit_base_url="https://github.com/$repo_slug/commit"
      ;;
  esac
fi

commit_ref() {
  local sha="$1"
  [ -z "$sha" ] && return 0
  case "$sha" in
    *[!0-9a-fA-F]*|"")
      return 0
      ;;
  esac
  [ "${#sha}" -ge 7 ] && [ "${#sha}" -le 40 ] || return 0
  local short="${sha:0:7}"
  if [ -n "$commit_base_url" ]; then
    printf ' ([%s](%s/%s))' "$short" "$commit_base_url" "$sha"
  else
    printf " (\`%s\`)" "$short"
  fi
}

if [ -z "$PASS" ]; then
  PASS=$(jq -r '.pass // 1' "$SURFACES" | sort -n | tail -1)
fi
case "$PASS" in
  ''|*[!0-9]*) die "bad --pass: $PASS (expected positive integer)" ;;
esac
[ "$PASS" -gt 0 ] || die "bad --pass: $PASS (expected positive integer)"

# Pass aggregates.
total=$(jq -c --argjson p "$PASS" 'select((.pass // 1) == $p)' "$SURFACES" | wc -l)
[ "$total" -gt 0 ] || die "no scored surfaces found for pass $PASS in $SURFACES"
polish=$(jq -c --argjson p "$PASS" 'select((.pass // 1) == $p) | select((.weighted_score // 0) >= 750)' "$SURFACES" | wc -l)
median=$(jq -r --argjson p "$PASS" 'select((.pass // 1) == $p) | .weighted_score // empty' "$SURFACES" \
  | sort -n | awk 'BEGIN{c=0} {a[c++]=$1} END{ if (c==0) print "—"; else if (c%2==1) print a[int(c/2)]; else print int((a[c/2-1]+a[c/2])/2) }')

# Δ vs prior pass.
delta=""
if [ "$PASS" -gt 1 ]; then
  prev_med=$(jq -r --argjson p "$((PASS-1))" 'select((.pass // 1) == $p) | .weighted_score // empty' "$SURFACES" \
    | sort -n | awk 'BEGIN{c=0} {a[c++]=$1} END{ if (c==0) print "—"; else if (c%2==1) print a[int(c/2)]; else print int((a[c/2-1]+a[c/2])/2) }')
  if [ "$prev_med" != "—" ] && [ "$median" != "—" ]; then
    d=$((median - prev_med))
    sign=""; [ "$d" -gt 0 ] && sign="+"
    delta=" (${sign}${d} vs pass $((PASS-1)))"
  fi
fi

# Applied recs this pass.
n_applied=0
if [ -f "$APPLIED" ]; then
  n_applied=$(jq -c --argjson p "$PASS" 'select((.pass // 1) == $p)' "$APPLIED" 2>/dev/null | wc -l)
fi

# Tool name.
tool=$(jq -r '.tool_name // "<tool>"' "$MANIFEST" 2>/dev/null || echo "<tool>")

# === HEADER ===
cat <<EOF
## Agent-ergonomics audit — \`$tool\` (pass $PASS)

**Median weighted: $median$delta · Polish-Bar (≥ 750): $polish/$total · Applied: $n_applied recs**

EOF

# === Top wins ===
if [ "$n_applied" -gt 0 ] && [ -f "$RECS" ]; then
  echo "### Top wins"
  if [ -f "$APPLIED" ]; then
    applied_ids=$(jq -r --argjson p "$PASS" 'select((.pass // 1) == $p) | .recommendation_id' "$APPLIED" 2>/dev/null | sort -u)
    while IFS= read -r aid; do
      [ -z "$aid" ] && continue
      commit_sha=$(jq -r --arg id "$aid" --argjson p "$PASS" \
        'select(.recommendation_id == $id and (.pass // 1) == $p) | .commit_sha // empty' \
        "$APPLIED" 2>/dev/null | head -1)
      commit_suffix=$(commit_ref "$commit_sha")
      jq -r --arg id "$aid" \
        --arg commit "$commit_suffix" \
        'select(.recommendation_id == $id)
         | "\(.expected_uplift_total // 0)\t- **\(.recommendation_id)** \(.title // "(no title)") · +\(.expected_uplift_total // 0) pts\($commit)"' \
        "$RECS" 2>/dev/null | head -1
    done <<< "$applied_ids" | sort -t $'\t' -k1 -nr | head -3 | cut -f2-
  fi
  echo
fi

# === Below Polish-Bar ===
below=$((total - polish))
if [ "$below" -gt 0 ]; then
  echo "### Surfaces still below Polish-Bar (≥ 750)"
  jq -r --argjson p "$PASS" \
    'select((.pass // 1) == $p) | select((.weighted_score // 0) < 750) | "- \(.surface_id) · \(.weighted_score // 0)"' \
    "$SURFACES" 2>/dev/null | head -5
  remaining=$((below - 5))
  [ "$remaining" -gt 0 ] && echo "- _… and $remaining more (see scorecard.html)_"
  echo
fi

# === Regressions ===
if [ "$INCLUDE_REGRESSIONS" = "1" ] && [ "$PASS" -gt 1 ]; then
  echo "### Regressions"
  # A surface "regressed" if its weighted dropped vs prior pass.
  regressed=0
  while IFS= read -r line; do
    sid=$(echo "$line" | jq -r '.surface_id')
    new_w=$(echo "$line" | jq -r '.weighted_score // 0')
    old_w=$(jq -r --arg s "$sid" --argjson p "$((PASS-1))" \
      'select(.surface_id == $s and (.pass // 1) == $p) | .weighted_score // empty' "$SURFACES" | head -1)
    if [ -n "$old_w" ] && [ "$old_w" != "0" ] && [ "$new_w" -lt "$old_w" ]; then
      d=$((new_w - old_w))
      printf -- '- %s: %s → %s (%s)\n' "$sid" "$old_w" "$new_w" "$d"
      regressed=$((regressed + 1))
      [ "$regressed" -ge 5 ] && { echo "- _… and possibly more (see diff_scorecards.sh output)_"; break; }
    fi
  done < <(jq -c --argjson p "$PASS" 'select((.pass // 1) == $p)' "$SURFACES")
  if [ "$regressed" = 0 ]; then
    echo "(none)"
  fi
  echo
fi

# === Test plan ===
echo "### Test plan"
echo
if [ -d "$AUDIT/regression_tests" ]; then
  while IFS= read -r t; do
    [ -z "$t" ] && continue
    echo "- [ ] \`$t\`"
  done < <(find "$AUDIT/regression_tests" -name "*.test.sh" 2>/dev/null | head -10)
fi
echo "- [ ] Reviewer spot-check 2-3 random surfaces' before/after scores."
echo "- [ ] Run \`scripts/skill-self-test.sh\` if rubric was touched."

echo
echo "_Generated by \`tools/generate-pr-comment.sh\`. Full report at \`audit/scorecard.html\`._"
