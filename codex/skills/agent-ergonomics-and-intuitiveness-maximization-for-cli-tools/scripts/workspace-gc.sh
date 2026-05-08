#!/usr/bin/env bash
# scripts/workspace-gc.sh — Workspace garbage collection.
#
# audit/partial/ accumulates per-pass scorer partials forever; after 5+
# passes a 200-surface CLI workspace is hundreds of MB. This GC archives old
# partials (and other transient artifacts) to a single tarball, keeping the
# workspace lean.
#
# Retention policy (defaults):
#   - Keep partials for the LATEST K passes (default K=3).
#   - Archive older partials to audit/.archive/partial-pass<N>.tar.gz.
#   - Keep the latest dryrun/ workdir; archive older ones.
#   - NEVER touch: manifest.json, agent_surfaces.jsonl, recommendations.jsonl,
#     applied_changes.jsonl, surface_inventory.jsonl, intent_inference_corpus.jsonl,
#     telemetry.jsonl, provenance.jsonl, scorecard.html, scorecard.md.
#   - NEVER touch *.lock files (other processes may be using them).
#
# Refuses to operate without --apply (default is --plan, dry-run).
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/workspace-gc.sh <sibling> [opts]

Garbage-collect old transient artifacts in <sibling>/audit/.

Options:
  --plan               Dry-run; print what WOULD be archived (default).
  --apply              Actually archive. NO files are deleted; everything
                       moves to audit/.archive/<ts>/.
  --keep-passes K      Number of recent passes to keep partials for (default 3).
  --keep-dryruns N     Number of recent dryrun workdirs to keep (default 1).

Output:
  Markdown report: per-category bytes-saved, archive location, restore command.

Safety:
  - Never deletes files; only moves to audit/.archive/<ts>/.
  - Never touches canonical artifacts or lockfiles.
  - With --plan (default), only reports.
  - --apply must be explicit.
  - Refuses to run if any *.lock file appears active (held by a process).

Restore:
  Move files back from audit/.archive/<ts>/ to their original locations.
  Original paths are recorded in audit/.archive/<ts>/manifest.txt.

Exit codes:
  0  GC complete (or plan emitted).
  1  Bad args / no workspace.
  2  Active locks present; refusing to GC.
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 1 ;;
esac

SIBLING="$1"; shift
MODE=plan
KEEP_PASSES=3
KEEP_DRYRUNS=1
need_value() {
  [ -n "${2:-}" ] || { echo "$1 requires a value" >&2; exit 1; }
  case "$2" in --*) echo "$1 requires a value, got option-like token: $2" >&2; exit 1 ;; esac
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --plan)          MODE=plan; shift ;;
    --apply)         MODE=apply; shift ;;
    --keep-passes)   need_value "$1" "${2:-}"; KEEP_PASSES="$2"; shift 2 ;;
    --keep-dryruns)  need_value "$1" "${2:-}"; KEEP_DRYRUNS="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done

case "$KEEP_PASSES" in
  ''|*[!0-9]*) echo "--keep-passes must be a non-negative integer" >&2; exit 1 ;;
esac
case "$KEEP_DRYRUNS" in
  ''|*[!0-9]*) echo "--keep-dryruns must be a non-negative integer" >&2; exit 1 ;;
esac

AUDIT="$SIBLING/audit"
[ -d "$AUDIT" ] || { echo "no audit dir: $AUDIT" >&2; exit 1; }

# Refuse to operate if any active lock is held (don't race other processes).
# fuser is required to make this check meaningful: silently skipping it would
# let GC race with a live writer if locks are held but fuser is missing.
locks_present=0
for lock in "$AUDIT"/*.lock; do
  [ -f "$lock" ] || continue
  locks_present=1
  break
done
if [ "$locks_present" -eq 1 ]; then
  if ! command -v fuser >/dev/null 2>&1; then
    echo "warning: lock files present in $AUDIT but fuser(1) not installed — cannot verify whether locks are stale or active." >&2
    echo "  install fuser (apt: psmisc) or remove stale locks manually before running GC." >&2
    exit 2
  fi
  for lock in "$AUDIT"/*.lock; do
    [ -f "$lock" ] || continue
    if fuser "$lock" >/dev/null 2>&1; then
      echo "active lock held: $lock — refusing to GC" >&2
      exit 2
    fi
  done
fi

# Determine latest passes. A freshly scaffolded audit may not have partials yet;
# that is a valid "nothing to archive" workspace, not a GC failure.
latest_passes=""
if [ -d "$AUDIT/partial" ] && [ "$KEEP_PASSES" -gt 0 ]; then
  latest_passes=$(find "$AUDIT/partial" -name "scores_pass*.jsonl" 2>/dev/null \
                  | sed -n 's/.*scores_pass\([0-9]*\)_.*/\1/p' \
                  | sort -nu | tail -n "$KEEP_PASSES" | tr '\n' ' ')
fi

# Append PID so two concurrent gc invocations in the same second don't share
# an archive subdir and `mv` over each other's files.
ARCHIVE_TS=$(date -u +%Y%m%dT%H%M%SZ)-$$
ARCHIVE_DIR="$AUDIT/.archive/$ARCHIVE_TS"

# Identify candidates.
candidates=()
total_bytes=0

# Old partials.
if [ -d "$AUDIT/partial" ]; then
  while IFS= read -r f; do
    [ -z "$f" ] && continue
    pass=$(echo "$f" | sed -n 's/.*scores_pass\([0-9]*\)_.*/\1/p')
    [ -z "$pass" ] && continue
    keep=0
    for kp in $latest_passes; do
      [ "$pass" = "$kp" ] && keep=1 && break
    done
    if [ "$keep" -eq 0 ]; then
      candidates+=("$f")
      sz=$(stat -c %s "$f" 2>/dev/null || echo 0)
      total_bytes=$((total_bytes + sz))
    fi
  done < <(find "$AUDIT/partial" -name "scores_pass*.jsonl" 2>/dev/null)
fi

# Old dryrun workdirs.
if [ -d "$AUDIT/dryrun" ]; then
  dryruns=()
  while IFS= read -r d; do
    [ -n "$d" ] && dryruns+=("$d")
  done < <(find "$AUDIT/dryrun" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort)
  n_total=${#dryruns[@]}
  to_archive=$(( n_total - KEEP_DRYRUNS ))
  if [ "$to_archive" -gt 0 ]; then
    for d in "${dryruns[@]:0:to_archive}"; do
      sz=$(du -sb "$d" 2>/dev/null | cut -f1)
      candidates+=("$d")
      total_bytes=$((total_bytes + ${sz:-0}))
    done
  fi
fi

human_bytes() {
  awk -v b="$1" 'BEGIN {
    units = "B KB MB GB"; split(units, u);
    i = 1; while (b >= 1024 && i < 4) { b /= 1024; i++ }
    printf "%.1f%s", b, u[i]
  }'
}

# Report.
echo "# Workspace GC Report"
echo
echo "- Workspace: \`$SIBLING\`"
echo "- Mode: $MODE"
echo "- Keeping partials for passes: $latest_passes"
echo "- Keeping last $KEEP_DRYRUNS dryrun workdir(s)"
echo "- Candidates: ${#candidates[@]}"
echo "- Estimated bytes to archive: $(human_bytes "$total_bytes")"
echo

if [ "${#candidates[@]}" -eq 0 ]; then
  echo "✅ Nothing to archive."
  exit 0
fi

if [ "$MODE" = plan ]; then
  echo "## Candidates (would archive)"
  echo
  shown=0
  for c in "${candidates[@]}"; do
    [ "$shown" -ge 20 ] && break
    echo "- $c"
    shown=$((shown + 1))
  done
  if [ "${#candidates[@]}" -gt 20 ]; then
    echo "- _… and $((${#candidates[@]} - 20)) more_"
  fi
  echo
  echo "Re-run with --apply to actually archive."
  exit 0
fi

# Apply: move (not delete) to archive.
mkdir -p "$ARCHIVE_DIR"
manifest="$ARCHIVE_DIR/manifest.txt"
: > "$manifest"
echo "## Archiving to \`$ARCHIVE_DIR\`"
echo
n_done=0
for c in "${candidates[@]}"; do
  [ ! -e "$c" ] && continue
  rel="${c#"$AUDIT/"}"
  dest="$ARCHIVE_DIR/$rel"
  mkdir -p "$(dirname "$dest")"
  /bin/mv "$c" "$dest"
  printf '%s\n' "$rel" >> "$manifest"
  n_done=$((n_done + 1))
done
echo "- archived: $n_done item(s)"
echo "- manifest: \`$manifest\`"
echo "- restore: move files back from \`$ARCHIVE_DIR/\` to \`$AUDIT/\` (paths in manifest.txt)"
exit 0
