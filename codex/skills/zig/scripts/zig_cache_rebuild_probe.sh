#!/usr/bin/env bash
set -euo pipefail

root="${1:-.}"
root_abs="$(cd "$root" && pwd)"
cd "$root_abs"

echo "== Zig cache rebuild probe =="
echo "root: $root_abs"

if ! command -v zig >/dev/null 2>&1; then
  echo "zig not found"
  echo "CACHE_REBUILD_UNVERIFIED"
  exit 1
fi

echo "zig version: $(zig version)"

if [ -f build.zig ]; then
  echo
  echo "== dependency fetch probe =="
  zig build --fetch=needed

  echo
  echo "== build probe =="
  zig build --summary all
  echo "CACHE_REBUILD_VERIFIED"
else
  echo "No build.zig found. Run the project-specific zig build-exe/zig test command."
  echo "CACHE_REBUILD_UNVERIFIED"
fi
