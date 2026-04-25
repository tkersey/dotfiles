#!/usr/bin/env bash
# session_setup.sh — one-shot refactor-session kickoff.
#
# Runs:
#   1. check_skills.sh  (sibling + jsm state)
#   2. baseline.sh      (tests + goldens + LOC + lint snapshot)
#   3. dup_scan.sh      (duplication scanners)
#   4. ai_slop_detector.sh (pathology scan)
#   5. unpinned_deps.sh (dep-pin check)
#   6. metrics_snapshot.sh (dashboard baseline)
#
# Writes everything under refactor/artifacts/<run-id>/. Does not edit code.
#
# Usage: session_setup.sh [run-id] [src-dir]

set -euo pipefail

RUN_ID="${1:-$(date +%Y-%m-%d)-pass-1}"
SRC="${2:-src}"
SCRIPT_DIR="$(dirname "$0")"

printf '=== Refactor session setup — %s ===\n\n' "$RUN_ID"

have_script() { [[ -x "$SCRIPT_DIR/$1" ]]; }

# 1. Sibling skills check
if have_script check_skills.sh; then
  printf '\n[1/6] check_skills.sh\n'
  "$SCRIPT_DIR/check_skills.sh" "refactor/artifacts/$RUN_ID"
else
  echo "[1/6] check_skills.sh missing; skipping"
fi

# 2. Baseline
if have_script baseline.sh; then
  printf '\n[2/6] baseline.sh\n'
  "$SCRIPT_DIR/baseline.sh" "$RUN_ID" || echo "(baseline returned non-zero; continuing)"
else
  echo "[2/6] baseline.sh missing; skipping"
fi

# 3. Duplication scan
if have_script dup_scan.sh; then
  printf '\n[3/6] dup_scan.sh\n'
  "$SCRIPT_DIR/dup_scan.sh" "$RUN_ID" "$SRC" || echo "(dup_scan returned non-zero; continuing)"
else
  echo "[3/6] dup_scan.sh missing; skipping"
fi

# 4. AI-slop detector
if have_script ai_slop_detector.sh; then
  printf '\n[4/6] ai_slop_detector.sh\n'
  "$SCRIPT_DIR/ai_slop_detector.sh" "$SRC" "$RUN_ID" || echo "(slop detector returned non-zero; continuing)"
else
  echo "[4/6] ai_slop_detector.sh missing; skipping"
fi

# 5. Unpinned deps
if have_script unpinned_deps.sh; then
  printf '\n[5/6] unpinned_deps.sh\n'
  "$SCRIPT_DIR/unpinned_deps.sh" "$RUN_ID" || echo "(unpinned_deps returned non-zero; continuing)"
else
  echo "[5/6] unpinned_deps.sh missing; skipping"
fi

# 6. Metrics snapshot
if have_script metrics_snapshot.sh; then
  printf '\n[6/6] metrics_snapshot.sh\n'
  "$SCRIPT_DIR/metrics_snapshot.sh" "$RUN_ID" "$SRC" >/dev/null || echo "(metrics_snapshot returned non-zero; continuing)"
  echo "   (metrics JSON at refactor/artifacts/$RUN_ID/metrics.json)"
else
  echo "[6/6] metrics_snapshot.sh missing; skipping"
fi

# Final summary
ART="refactor/artifacts/$RUN_ID"
cat <<EOF

=== Session setup complete ===

Artifacts: ${ART}/
  - skill_inventory.json   sibling-skill state
  - baseline.md            test + LOC + lint snapshot
  - tests_before.txt       test output
  - duplication_map.md     duplication scanner output (EDIT MANUALLY to list candidates)
  - slop_scan.md           AI-slop pathology findings
  - unpinned_deps.md       dep-pin audit
  - metrics.json           baseline metrics

Next steps:

1. Review ${ART}/duplication_map.md and ${ART}/slop_scan.md.
2. Fill in candidates in duplication_map.md.
3. Score them: ./scripts/score_candidates.py ${ART}/duplication_map.md
4. For each accepted candidate, fill isomorphism card:
      ./scripts/isomorphism_card.sh <id> ${RUN_ID}
5. Edit code (Edit tool only; one lever per commit).
6. Verify: ./scripts/verify_isomorphism.sh ${RUN_ID}
7. Ledger row: ./scripts/ledger_row.sh ${RUN_ID} <id>

Invariants throughout (AGENTS.md + this skill):
  - No file deletion without explicit approval.
  - No sed / codemod — use Edit or parallel subagents.
  - No \`_v2\` / \`_new\` filenames.
  - One lever per commit.
  - UBS before every commit.

See references/SKILL.md §"The Loop" for the full phase sequence.
EOF
