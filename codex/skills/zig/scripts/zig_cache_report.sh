#!/usr/bin/env bash
set -euo pipefail

root="${1:-.}"
root_abs="$(cd "$root" && pwd)"

echo "== Zig cache report =="
echo "root: $root_abs"

extract_global_cache() {
  sed -nE \
    -e 's/^[[:space:]]*\.global_cache_dir = "([^"]+)".*/\1/p' \
    -e 's/^[[:space:]]*"global_cache_dir"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/p' |
  head -1
}

print_largest_from_nul_stream() {
  while IFS= read -r -d '' p; do
    du -sk "$p" 2>/dev/null || true
  done |
  sort -nr |
  head -30 |
  awk '{ size_kb=$1; $1=""; printf "%.1f MiB%s\n", size_kb/1024, $0 }'
}

if command -v zig >/dev/null 2>&1; then
  echo
  echo "== zig version =="
  zig version || true

  echo
  echo "== zig env cache hints =="
  zig_env="$(zig env 2>/dev/null || true)"
  if [ -n "$zig_env" ]; then
    printf '%s\n' "$zig_env" | grep -E 'global_cache_dir|local_cache_dir|lib_dir|std_dir|version' || true
    global_cache="$(printf '%s\n' "$zig_env" | extract_global_cache || true)"
  else
    echo "zig env unavailable"
    global_cache=""
  fi
else
  echo "zig: not found"
  global_cache=""
fi

if [ -n "${ZIG_GLOBAL_CACHE_DIR:-}" ]; then
  echo "env ZIG_GLOBAL_CACHE_DIR: $ZIG_GLOBAL_CACHE_DIR"
fi

printf '\n== project-local candidates ==\n'
(
  cd "$root_abs"
  for p in .zig-cache zig-cache zig-out zig-pkg; do
    if [ -e "$p" ]; then
      du -sh "$p" 2>/dev/null || true
    fi
  done
)

printf '\n== nested Zig cache/output candidates ==\n'
find "$root_abs" \
  \( -name .git -o -name node_modules -o -name target \) -prune -o \
  -type d \( -name .zig-cache -o -name zig-cache -o -name zig-out -o -name zig-pkg \) \
  -print0 |
while IFS= read -r -d '' d; do
  du -sh "$d" 2>/dev/null || true
done

printf '\n== largest Zig candidates under root ==\n'
find "$root_abs" \
  \( -name .git -o -name node_modules -o -name target \) -prune -o \
  -type d \( -name .zig-cache -o -name zig-cache -o -name zig-out -o -name zig-pkg \) \
  -print0 |
print_largest_from_nul_stream

if [ -n "$global_cache" ] && [ -e "$global_cache" ]; then
  printf '\n== global Zig cache ==\n'
  du -sh "$global_cache" 2>/dev/null || true
  printf '\n== largest top-level global cache entries ==\n'
  find "$global_cache" -mindepth 1 -maxdepth 1 -print0 2>/dev/null |
  print_largest_from_nul_stream
else
  printf '\n== global Zig cache ==\n'
  echo "CACHE_PATH_UNDISCOVERED"
fi

echo

echo "CACHE_AUDITED"
