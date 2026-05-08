#!/usr/bin/env bash
# tools/audit-doctor.sh — Diagnose audit workspace issues + suggest fixes.
#
# Scans for the failure modes documented in PIPELINE-RECOVERY.md:
#   - stale per-applier ledgers (partial/applier_*.state.json) from killed appliers
#   - incomplete JSONL (last line missing closing newline / unparseable)
#   - orphan flock files (*.lock with no holding process)
#   - missing schemas (manifest.json absent or invalid)
#   - duplicate (surface_id, pass) rows in agent_surfaces.jsonl
#   - applied_changes references to recommendation_ids that don't exist
#   - HANDOFF.md missing despite applied_changes.jsonl having entries
#
# Outputs per-issue: diagnosis, fix command. Optional --apply to run fixes.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: tools/audit-doctor.sh <sibling> [--apply]

Diagnoses common audit-workspace issues and suggests fixes. Without --apply,
it just reports; with --apply, it attempts safe auto-fixes (archive completed
applier ledgers, truncate orphan lock files). Per AGENTS.md, NO files are
deleted; archived artifacts are copied to audit/.archive/doctor_<timestamp>/.
Duplicate score rows are diagnosed only; rerun aggregate_scores.sh to replace
the affected `(surface_id, pass)` row.

Args:
  <sibling>   Audit workspace root.
  --apply     Auto-fix where safe. Without this, output is read-only.

Exit codes:
  0  No issues found, OR all issues auto-fixed.
  1  Issues found that need manual fixing.
  2  Bad args / missing workspace.
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 2 ;;
esac

SIBLING="$1"; shift
APPLY=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    --apply) APPLY=1; shift ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

AUDIT="$SIBLING/audit"
[ -d "$AUDIT" ] || { echo "no $AUDIT" >&2; exit 2; }

issues=0
fixed=0

issue() {
  local name="$1" diagnosis="$2" fix="$3"
  echo "ISSUE $name" >&2
  echo "  diagnosis: $diagnosis" >&2
  echo "  fix:       $fix" >&2
  echo "" >&2
  issues=$((issues + 1))
}

# ---- Check 1: manifest.json present + valid -----------------------------
if [ ! -f "$AUDIT/manifest.json" ]; then
  issue "manifest.json missing" \
        "$AUDIT/manifest.json absent — workspace may be unscaffolded or corrupted" \
        "scripts/scaffold-workspace.sh $SIBLING <target>  # if unscaffolded"
elif ! jq . "$AUDIT/manifest.json" >/dev/null 2>&1; then
  issue "manifest.json malformed" \
        "$AUDIT/manifest.json exists but isn't valid JSON" \
        "manually inspect / restore from .archive (NEVER delete)"
fi

# ---- Check 2: stale applier ledgers --------------------------------------
shopt -s nullglob
for ledger in "$AUDIT"/partial/applier_*.state.json; do
  [ -f "$ledger" ] || continue
  if ! jq . "$ledger" >/dev/null 2>&1; then
    issue "malformed applier ledger ($ledger)" \
          "$ledger exists but is not valid JSON; a writer may have crashed mid-record" \
          "manual: inspect and restore from audit/.archive if available"
    continue
  fi
  flipped=$(jq -r '.applied_flipped // null' "$ledger" 2>/dev/null)
  released=$(jq -r '.reservation_released // null' "$ledger" 2>/dev/null)
  if [ "$flipped" != "null" ] && [ "$released" != "null" ]; then
    # Completed ledger — fine to archive on --apply.
    if [ "$APPLY" -eq 1 ]; then
      archive_dir="$AUDIT/.archive/doctor_$(date +%s)"
      mkdir -p "$archive_dir"
      if cp "$ledger" "$archive_dir/"; then
        : > "$ledger"  # truncate (NEVER delete per AGENTS.md)
        fixed=$((fixed + 1))
      else
        issue "archive failed for completed applier ledger" \
              "could not copy $ledger to $archive_dir; refusing to truncate without an archive" \
              "inspect permissions and retry tools/audit-doctor.sh <sibling> --apply"
      fi
    fi
  elif [ "$flipped" = "null" ] || [ "$released" = "null" ]; then
    rid=$(jq -r '.recommendation_id // "<unknown>"' "$ledger")
    issue "stale applier ledger ($rid)" \
          "applier for $rid started but never completed (last_step_at: $(jq -r '.last_step_at // "?"' "$ledger"))" \
          "re-spawn applier with same <RECOMMENDATION_ID>; it will resume from the ledger automatically"
  fi
done
shopt -u nullglob

# ---- Check 3: malformed JSONL (truncated last line) ----------------------
for jsonl in \
  "$AUDIT/agent_surfaces.jsonl" \
  "$AUDIT/intent_inference_corpus.jsonl" \
  "$AUDIT/recommendations.jsonl" \
  "$AUDIT/applied_changes.jsonl" \
  "$AUDIT/surface_inventory.jsonl"
do
  [ -f "$jsonl" ] || continue
  if ! jq -c -e . < "$jsonl" >/dev/null 2>&1; then
    bad_line=$({ jq -c . < "$jsonl" 2>&1 || true; } | sed -nE 's/.*line ([0-9]+).*/\1/p' | head -1)
    [ -n "$bad_line" ] || bad_line="?"
    issue "malformed JSONL: $jsonl" \
          "jq fails to parse one or more lines (likely line $bad_line — torn write or truncated)" \
          "manual: archive the file, then re-derive; --apply only handles completed ledgers and orphan locks"
  fi
done

# ---- Check 4: duplicate (surface_id, pass) rows in agent_surfaces.jsonl --
if [ -f "$AUDIT/agent_surfaces.jsonl" ]; then
  dupes=$(jq -r '
    select(type == "object")
    | select((.surface_id | type) == "string")
    | select((.pass | type) == "number" and (.pass | floor) == .pass)
    | .surface_id + ":" + (.pass | tostring)
  ' "$AUDIT/agent_surfaces.jsonl" 2>/dev/null | sort | uniq -d || true)
  if [ -n "$dupes" ]; then
    while IFS= read -r d; do
      [ -z "$d" ] && continue
      issue "duplicate (surface_id,pass)=$d in agent_surfaces.jsonl" \
            "validate_scorecard.sh will reject this; an aggregator or re-scorer race left both rows" \
            "re-run scripts/aggregate_scores.sh (idempotency fix in round F replaces, not duplicates)"
    done <<< "$dupes"
  fi
fi

# ---- Check 5: applied_changes references non-existent rec ----------------
if [ -f "$AUDIT/applied_changes.jsonl" ] && [ -f "$AUDIT/recommendations.jsonl" ]; then
  applied_rids=$(jq -r '.recommendation_id' "$AUDIT/applied_changes.jsonl" 2>/dev/null | sort -u || true)
  rec_rids=$(jq -r '.recommendation_id' "$AUDIT/recommendations.jsonl" 2>/dev/null | sort -u || true)
  while IFS= read -r rid; do
    [ -z "$rid" ] && continue
    if ! echo "$rec_rids" | grep -qx "$rid"; then
      issue "applied_changes references unknown $rid" \
            "applier wrote applied_changes.jsonl entry for $rid, but that rec doesn't exist in recommendations.jsonl" \
            "manual: investigate; either restore the rec or remove the orphan applied_changes line"
    fi
  done <<< "$applied_rids"
fi

# ---- Check 6: HANDOFF.md missing despite applied changes -----------------
if [ -f "$AUDIT/applied_changes.jsonl" ] && [ ! -f "$AUDIT/HANDOFF.md" ]; then
  applied_count=$(wc -l < "$AUDIT/applied_changes.jsonl")
  if [ "$applied_count" -gt 0 ]; then
    issue "HANDOFF.md missing" \
          "$applied_count applied changes recorded but no HANDOFF.md written (Phase 10 not run)" \
          "spawn subagents/handoff-writer.md with <SIBLING> and <N> args"
  fi
fi

# ---- Check 7: orphan flock files -----------------------------------------
shopt -s nullglob
for lock in "$AUDIT"/*.lock "$AUDIT"/partial/*.lock; do
  [ -f "$lock" ] || continue
  if command -v fuser >/dev/null 2>&1; then
    if ! fuser "$lock" >/dev/null 2>&1; then
      # No process holds it — orphan.
      issue "orphan flock file: $lock" \
            "lockfile exists but no process holds it — left over from a killed phase script" \
            "safe to truncate via --apply; lock will recreate on next acquisition"
      if [ "$APPLY" -eq 1 ]; then
        : > "$lock"
        fixed=$((fixed + 1))
      fi
    fi
  fi
done
shopt -u nullglob

# ---- Summary -------------------------------------------------------------
echo "" >&2
if [ "$issues" -eq 0 ]; then
  echo "audit-doctor: workspace clean ($AUDIT)" >&2
  exit 0
fi
echo "audit-doctor: $issues issue(s) found, $fixed auto-fixed" >&2
[ "$APPLY" -eq 0 ] && echo "  (re-run with --apply to fix safe issues)" >&2
[ "$issues" -gt "$fixed" ] && exit 1 || exit 0
