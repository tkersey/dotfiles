#!/usr/bin/env bash
set -euo pipefail

root="."
yes=0
include_out=0
include_pkg=0
include_global=0
older_than_days=""
global_path=""
dry_run=1

usage() {
  cat <<'USAGE'
Usage:
  zig_cache_drain.sh [options]

Options:
  --root PATH             Project root to scan, default: .
  --yes                   Actually delete. Without this, dry-run only.
  --include-zig-out       Include zig-out generated install prefix/output.
  --include-zig-pkg       Include zig-pkg dependency tree, guarded.
  --include-global        Include global Zig cache, guarded.
  --global-path PATH      Explicit global cache path instead of zig env discovery.
  --older-than DAYS       Only delete candidates older than N days.
  --help                  Show this help.

Default behavior:
  Dry-run deletion of project-local .zig-cache / zig-cache only.
USAGE
}

while [ $# -gt 0 ]; do
  case "$1" in
    --root) root="$2"; shift 2 ;;
    --yes) yes=1; dry_run=0; shift ;;
    --include-zig-out) include_out=1; shift ;;
    --include-zig-pkg) include_pkg=1; shift ;;
    --include-global) include_global=1; shift ;;
    --global-path) global_path="$2"; shift 2 ;;
    --older-than) older_than_days="$2"; shift 2 ;;
    --help) usage; exit 0 ;;
    *) echo "unknown option: $1" >&2; usage; exit 2 ;;
  esac
done

root_abs="$(cd "$root" && pwd)"

if command -v pgrep >/dev/null 2>&1 && pgrep -x zig >/dev/null 2>&1; then
  echo "CACHE_ACTIVE_BUILD_REFUSED: a zig process appears to be running. Stop active Zig builds first."
  exit 1
fi

safe_du() { du -sh "$1" 2>/dev/null | awk '{print $1}' || printf '?'; }

is_older_than_threshold() {
  local p="$1"
  if [ -z "$older_than_days" ]; then
    return 0
  fi
  find "$p" -maxdepth 0 -mtime +"$older_than_days" -print -quit 2>/dev/null | grep -q .
}

delete_path_under_root() {
  local p="$1"
  case "$p" in
    "$root_abs"/*) ;;
    *) echo "refuse outside root: $p" >&2; return 1 ;;
  esac

  if ! is_older_than_threshold "$p"; then
    echo "skip recent: $p"
    return 0
  fi

  local size
  size="$(safe_du "$p")"
  if [ "$dry_run" -eq 1 ]; then
    echo "would delete: $p ($size)"
  else
    echo "delete: $p ($size)"
    rm -rf -- "$p"
  fi
}

guard_zig_pkg() {
  local p="$1"
  local dirty=0

  if find "$p" -type d -name .git -print -quit 2>/dev/null | grep -q .; then
    while IFS= read -r gitdir; do
      repo="${gitdir%/.git}"
      if git -C "$repo" status --porcelain 2>/dev/null | grep -q .; then
        echo "CACHE_MODIFIED_DEPENDENCY_UNTOUCHED: $repo"
        dirty=1
      fi
    done < <(find "$p" -type d -name .git 2>/dev/null)
  fi

  [ "$dirty" -eq 0 ]
}

extract_global_cache() {
  sed -nE \
    -e 's/^[[:space:]]*\.global_cache_dir = "([^"]+)".*/\1/p' \
    -e 's/^[[:space:]]*"global_cache_dir"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/p' |
  head -1
}

validate_global_path() {
  local p="$1"
  if [ -z "$p" ]; then return 1; fi
  case "$p" in
    /|/tmp|/var|/home|/Users|.) return 1 ;;
  esac
  if [ ! -d "$p" ]; then return 1; fi
  return 0
}

drain_global_cache() {
  local gc="$1"
  if ! validate_global_path "$gc"; then
    echo "CACHE_PATH_UNDISCOVERED: unsafe or missing global cache path: ${gc:-<empty>}"
    return 0
  fi

  echo "global cache: $gc ($(safe_du "$gc"))"
  find "$gc" -mindepth 1 -maxdepth 1 -print0 2>/dev/null |
  while IFS= read -r -d '' entry; do
    if ! is_older_than_threshold "$entry"; then
      echo "skip recent: $entry"
      continue
    fi
    local size
    size="$(safe_du "$entry")"
    if [ "$dry_run" -eq 1 ]; then
      echo "would delete global entry: $entry ($size)"
    else
      echo "delete global entry: $entry ($size)"
      rm -rf -- "$entry"
    fi
  done
}

echo "== Zig cache drain =="
echo "root: $root_abs"
[ "$dry_run" -eq 1 ] && echo "mode: dry-run" || echo "mode: destructive"

printf '\n== local cache candidates ==\n'
find "$root_abs" \
  \( -name .git -o -name node_modules -o -name target \) -prune -o \
  -type d \( -name .zig-cache -o -name zig-cache \) \
  -print0 |
while IFS= read -r -d '' d; do
  delete_path_under_root "$d"
done

if [ "$include_out" -eq 1 ]; then
  printf '\n== zig-out candidates ==\n'
  find "$root_abs" \
    \( -name .git -o -name node_modules -o -name target \) -prune -o \
    -type d -name zig-out \
    -print0 |
  while IFS= read -r -d '' d; do
    delete_path_under_root "$d"
  done
fi

if [ "$include_pkg" -eq 1 ]; then
  printf '\n== zig-pkg candidates ==\n'
  find "$root_abs" \
    \( -name .git -o -name node_modules -o -name target \) -prune -o \
    -type d -name zig-pkg \
    -print0 |
  while IFS= read -r -d '' d; do
    if guard_zig_pkg "$d"; then
      delete_path_under_root "$d"
    else
      echo "CACHE_ZIG_PKG_SKIPPED: $d"
    fi
  done
fi

if [ "$include_global" -eq 1 ]; then
  printf '\n== global cache candidate ==\n'
  if [ -z "$global_path" ]; then
    if command -v zig >/dev/null 2>&1; then
      global_path="$(zig env 2>/dev/null | extract_global_cache || true)"
    fi
  fi
  drain_global_cache "$global_path"
fi

if [ "$dry_run" -eq 1 ]; then
  echo "CACHE_DRY_RUN_ONLY"
else
  echo "CACHE_LOCAL_DRAINED"
  [ "$include_out" -eq 1 ] && echo "CACHE_OUTPUT_DRAINED"
  [ "$include_pkg" -eq 1 ] && echo "CACHE_ZIG_PKG_DRAINED"
  [ "$include_global" -eq 1 ] && echo "CACHE_GLOBAL_DRAINED"
fi
