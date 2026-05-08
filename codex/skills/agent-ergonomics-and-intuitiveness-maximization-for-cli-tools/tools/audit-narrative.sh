#!/usr/bin/env bash
# tools/audit-narrative.sh — Auto-generate the multi-pass narrative.
#
# Walks every pass in audit/manifest.json + recommendations + applied_changes
# + per-pass scorecards, and emits a chronological story:
#   "Pass 1: scored 141 surfaces; Polish-Bar 12/141; recommended 18, applied 12."
#   "Pass 2: re-scored, median +47 pts, Polish-Bar 56/141; ..."
#
# Output is suitable for:
#   - PR description body (`gh pr create --body "$(audit-narrative.sh ...)"`)
#   - the handoff document (paste into assets/handoff-template.md)
#   - end-of-session summary
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: tools/audit-narrative.sh <sibling> [--format md|plain]

Generate a chronological narrative across all passes in this audit.

Args:
  <sibling>     Audit workspace root.
  --format      'md' (default) — markdown with headings + tables.
                'plain'        — single paragraph per pass, no markup.
                                 Suitable for slack/email.

Output (markdown):
  # <target> Audit Narrative
  ## Pass 1 — <date range>
  - Phase 0 intake: <mode>, branch <name>
  - Inventory: <N> surfaces (verbs <V>, flags <F>, errors <E>)
  - Scoring: median weighted = <M>, Polish-Bar <K>/<N>
  - Recommendations: <R> drafted, <A> applied, <D> deferred
  - Re-score: median +<delta> pts; Polish-Bar <K2>/<N>
  - Top wins: ...
  - Regressions: ...
  ## Pass 2 — ...

Exit codes:
  0  Narrative produced.
  1  Bad args / missing manifest.
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 1 ;;
esac

SIBLING="$1"; shift
FORMAT=md
need_value() {
  [ -n "${2:-}" ] || { echo "$1 requires a value" >&2; exit 1; }
  case "$2" in --*) echo "$1 requires a value, got option-like token: $2" >&2; exit 1 ;; esac
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --format) need_value "$1" "${2:-}"; FORMAT="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done

case "$FORMAT" in md|plain) ;; *) echo "bad --format: $FORMAT" >&2; exit 1 ;; esac

AUDIT="$SIBLING/audit"
MANIFEST="$AUDIT/manifest.json"
SURFACES="$AUDIT/agent_surfaces.jsonl"
RECS="$AUDIT/recommendations.jsonl"
APPLIED="$AUDIT/applied_changes.jsonl"

[ -f "$MANIFEST" ] || { echo "manifest not found: $MANIFEST" >&2; exit 1; }

target_basename=$(jq -r '.tool_name // (.tool_repo | split("/")[-1]) // .target_basename // .target_path // "target"' "$MANIFEST")
n_passes=$(jq -r '.passes | length' "$MANIFEST")

if [ "$FORMAT" = md ]; then
  echo "# $target_basename — Audit Narrative"
  echo
  echo "_Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ) · $n_passes pass(es)_"
  echo
fi

# Enumerate passes 1..N.
for i in $(seq 1 "$n_passes"); do
	pass_idx=$((i - 1))
	started=$(jq -r --argjson i "$pass_idx" '.passes[$i].started_at // ""' "$MANIFEST")
	ended=$(jq -r --argjson i "$pass_idx"   '.passes[$i].completed_at // .passes[$i].ended_at // ""' "$MANIFEST")
	mode=$(jq -r --argjson i "$pass_idx"    '.passes[$i].mode       // "?"' "$MANIFEST")
	branch=$(jq -r --argjson i "$pass_idx"  '.passes[$i].feature_branch // .passes[$i].branch // "?"' "$MANIFEST")

  if [ "$FORMAT" = md ]; then
    echo "## Pass $i"
    echo
    echo "- **mode:** $mode"
    echo "- **branch:** \`$branch\`"
    echo "- **started:** $started"
    [ -n "$ended" ] && [ "$ended" != "null" ] && echo "- **ended:** $ended"
    echo
  fi

  # Inventory counts (only available if surface_inventory.jsonl exists).
  inv="$AUDIT/surface_inventory.jsonl"
  if [ -f "$inv" ]; then
    n_surf=$(wc -l < "$inv")
    n_verb=$(jq -c 'select(.kind == "verb")' "$inv" 2>/dev/null | wc -l)
    n_flag=$(jq -c 'select(.kind == "flag")' "$inv" 2>/dev/null | wc -l)
    n_err=$(jq -c  'select(.kind == "error")' "$inv" 2>/dev/null | wc -l)
    if [ "$FORMAT" = md ]; then
      echo "### Inventory"
      echo "| total | verbs | flags | errors |"
      echo "|-------|-------|-------|--------|"
      printf '| %s | %s | %s | %s |\n' "$n_surf" "$n_verb" "$n_flag" "$n_err"
      echo
    else
      echo "Pass $i: inventory = $n_surf surfaces ($n_verb verbs, $n_flag flags, $n_err errors)"
    fi
  fi

  # Scoring summary (this pass).
  if [ -f "$SURFACES" ]; then
    median=$(jq -r --argjson p "$i" 'select((.pass // 1) == $p) | .weighted_score // empty' "$SURFACES" \
      | sort -n | awk 'BEGIN{c=0} {a[c++]=$1} END{ if (c==0) print "—"; else if (c%2==1) print a[int(c/2)]; else print int((a[c/2-1]+a[c/2])/2) }')
    polish=$(jq -c --argjson p "$i" 'select((.pass // 1) == $p) | select((.weighted_score // 0) >= 750)' "$SURFACES" 2>/dev/null | wc -l)
    total=$(jq -c --argjson p "$i" 'select((.pass // 1) == $p)' "$SURFACES" 2>/dev/null | wc -l)
    if [ "$FORMAT" = md ]; then
      echo "### Scoring (pass $i)"
      echo "- median weighted: **$median**"
      echo "- Polish-Bar (≥ 750): **$polish / $total**"
      echo
    else
      echo "Pass $i: median=$median, Polish-Bar=$polish/$total"
    fi

    # Per-dim mean for this pass.
    if [ "$FORMAT" = md ] && [ "$total" -gt 0 ]; then
      echo "#### Per-dim mean"
      echo "| dim | mean |"
      echo "|-----|------|"
      for dim in agent_intuitiveness agent_ergonomics agent_ease_of_use output_parseability error_pedagogy intent_inference safety_with_recovery determinism_and_reproducibility self_documentation composability regression_resistance; do
        m=$(jq -r --argjson p "$i" --arg d "$dim" \
          'select((.pass // 1) == $p) | .scores[$d] // empty' "$SURFACES" 2>/dev/null \
          | awk 'NF { s += $1; n++ } END { if (n>0) printf "%.0f", s/n; else print "—" }')
        printf '| %s | %s |\n' "$dim" "$m"
      done
      echo
    fi

    # Δ vs previous pass: median delta
    if [ "$i" -gt 1 ] && [ "$FORMAT" = md ]; then
      prev_med=$(jq -r --argjson p "$((i-1))" 'select((.pass // 1) == $p) | .weighted_score // empty' "$SURFACES" \
        | sort -n | awk 'BEGIN{c=0} {a[c++]=$1} END{ if (c==0) print "—"; else if (c%2==1) print a[int(c/2)]; else print int((a[c/2-1]+a[c/2])/2) }')
      if [ "$prev_med" != "—" ] && [ "$median" != "—" ]; then
        delta=$((median - prev_med))
        sign=""
        [ "$delta" -gt 0 ] && sign="+"
        echo "### Δ vs Pass $((i-1)): median **$sign$delta** pts"
        echo
      fi
    fi
  fi

  # Recommendations + applied count for this pass.
  if [ -f "$RECS" ]; then
    n_recs=$(jq -c --argjson p "$i" 'select((.pass // 1) == $p)' "$RECS" 2>/dev/null | wc -l)
    n_applied=0
    if [ -f "$APPLIED" ]; then
      n_applied=$(jq -c --argjson p "$i" 'select((.pass // 1) == $p)' "$APPLIED" 2>/dev/null | wc -l)
    fi
    n_deferred=$(jq -c --argjson p "$i" 'select(((.pass // 1) == $p) and ((.deferred_reason // null) != null) and (.deferred_reason != ""))' "$RECS" 2>/dev/null | wc -l)
    if [ "$FORMAT" = md ]; then
      echo "### Recommendations"
      echo "- drafted: **$n_recs**"
      echo "- applied: **$n_applied**"
      echo "- deferred: **$n_deferred**"
      echo
      # Top 5 wins by expected_uplift_total — APPLIED recs only.
      # Sort robustly: prepend the numeric uplift via jq, sort by first field,
      # strip it before printing. Avoids parsing the rendered "+N pts" suffix
      # (which breaks if a title contains the "+" character).
      if [ "$n_applied" -gt 0 ] && [ -f "$APPLIED" ]; then
        echo "#### Top wins (applied, by expected uplift)"
        applied_ids=$(jq -r --argjson p "$i" 'select((.pass // 1) == $p) | .recommendation_id' "$APPLIED" 2>/dev/null \
                      | sort -u)
        if [ -n "$applied_ids" ]; then
          while IFS= read -r aid; do
            [ -z "$aid" ] && continue
            jq -r --arg id "$aid" \
              'select(.recommendation_id == $id)
               | "\(.expected_uplift_total // 0)\t- \(.recommendation_id): \(.title // "(no title)") — +\(.expected_uplift_total // 0) pts"' \
              "$RECS" 2>/dev/null | head -1
          done <<< "$applied_ids" \
            | sort -t $'\t' -k1 -nr | head -5 | cut -f2-
        fi
        echo
      fi
    else
      echo "Pass $i: recs=$n_recs (applied=$n_applied, deferred=$n_deferred)"
    fi
  fi
done

# Closing block: cumulative state.
if [ "$FORMAT" = md ]; then
  echo "---"
  echo
  echo "## Cumulative state"
  if [ -f "$SURFACES" ]; then
    last_pass=$n_passes
    cum_polish=$(jq -c --argjson p "$last_pass" 'select((.pass // 1) == $p) | select((.weighted_score // 0) >= 750)' "$SURFACES" 2>/dev/null | wc -l)
    cum_total=$(jq -c --argjson p "$last_pass" 'select((.pass // 1) == $p)' "$SURFACES" 2>/dev/null | wc -l)
    echo "- **Pass $last_pass Polish-Bar:** $cum_polish / $cum_total"
  fi
  if [ -f "$APPLIED" ]; then
    n_total_applied=$(wc -l < "$APPLIED")
    echo "- **Total recommendations applied across all passes:** $n_total_applied"
  fi
fi
