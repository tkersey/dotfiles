#!/usr/bin/env bash
# scripts/discover-cli.sh — Detect CLI language, build system, binary entry points,
# completion-script paths, embedded man pages, env-var prefix conventions.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/discover-cli.sh <target-dir>

Detects a CLI repo's language(s), build system, binary entry points,
existing agent-ergonomic surfaces (--robot-* / capabilities / robot-docs),
and env-var prefix conventions. Writes a single JSON object to stdout.

Args:
  <target-dir>   Path to the target CLI's source repo (defaults to cwd).

Output:
  JSON object on stdout. Redirect to <sibling>/audit/phase0_cli.json.
  Diagnostics on stderr.

Example:
  scripts/discover-cli.sh ~/code/mytool > audit/phase0_cli.json

Exit codes:
  0  Success.
  2  <target-dir> does not exist or is not a directory.
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
esac

TARGET="${1:-.}"
if [ ! -d "$TARGET" ]; then
  echo "target not a directory: $TARGET" >&2
  echo "(run with --help for usage)" >&2
  exit 2
fi
TARGET="$(cd "$TARGET" && pwd)"

# Detect language(s) — initialize empty arrays explicitly for set -u safety
langs=()
binaries=()

if [ -f "$TARGET/Cargo.toml" ]; then
  langs+=("rust")
  # Best-effort manifest scan first (fast, no cargo invocation).
  # Use FS="\"" to extract the value between the quotes ($2 is the name).
  while IFS= read -r bin; do
    [ -n "$bin" ] && binaries+=("$bin")
  done < <(awk -F'"' '
    /^\[\[bin\]\]/                                  { in_bin=1; in_pkg=0; next }
    /^\[package\]/                                  { in_pkg=1; in_bin=0; next }
    /^\[/ && !/^\[\[bin\]\]/ && !/^\[package\]/     { in_bin=0; in_pkg=0 }
    in_bin && /^[[:space:]]*name[[:space:]]*=/      { print $2 }
    in_pkg && /^[[:space:]]*name[[:space:]]*=/      { pkg_name=$2 }
    END { if (pkg_name) print pkg_name }
  ' "$TARGET/Cargo.toml" 2>/dev/null)
  # Dedupe (awk can emit dupes if [[bin]].name == [package].name).
  # mapfile is bash-4-only; do this portably.
  if [ ${#binaries[@]} -gt 0 ]; then
    deduped_str=$(printf '%s\n' "${binaries[@]}" | awk '!seen[$0]++')
    binaries=()
    while IFS= read -r line; do
      [ -n "$line" ] && binaries+=("$line")
    done <<< "$deduped_str"
  fi
  if [ ${#binaries[@]} -eq 0 ] && [ -f "$TARGET/src/main.rs" ]; then
    binaries+=("$(basename "$TARGET")")
  fi
fi

if [ -f "$TARGET/go.mod" ]; then
  langs+=("go")
  for cmddir in "$TARGET"/cmd/*/; do
    [ -d "$cmddir" ] && binaries+=("$(basename "$cmddir")")
  done
  if [ -f "$TARGET/main.go" ] && [ ${#binaries[@]} -eq 0 ]; then
    binaries+=("$(basename "$TARGET")")
  fi
fi

if [ -f "$TARGET/package.json" ]; then
  langs+=("typescript_or_javascript")
  while IFS= read -r bin; do
    [ -n "$bin" ] && binaries+=("$bin")
  done < <(jq -r 'if (.bin | type) == "object" then .bin | keys[] elif (.bin | type) == "string" then (.name // empty) else empty end' "$TARGET/package.json" 2>/dev/null || true)
fi

if [ -f "$TARGET/pyproject.toml" ] || [ -f "$TARGET/setup.py" ]; then
  langs+=("python")
  if [ -f "$TARGET/pyproject.toml" ]; then
    # Extract `name = ...` keys under `[project.scripts]`. The previous regex
    # `s/^\s*([^=]+)\s*=.*/\1/` captured `[^=]+` greedily including any
    # whitespace before `=`, so a line like `mybin = "mymod:run"` produced a
    # binary name `mybin ` (with a trailing space) — that leaked into
    # downstream PATH lookups, surface_id keys, and JSON fields with the
    # trailing space silently embedded. Use `[^=[:space:]]+` so the capture
    # stops at the first whitespace OR `=`. POSIX `[[:space:]]` instead of
    # `\s` for GNU/BSD sed portability.
    while IFS= read -r bin; do
      binaries+=("$bin")
    done < <(grep -A 5 '\[project.scripts\]' "$TARGET/pyproject.toml" 2>/dev/null | grep -E '^\s*\w' | head -10 | sed -E 's/^[[:space:]]*([^=[:space:]]+).*/\1/' || true)
  fi
fi

# C / C++ detection: classic autotools or Makefile-based build with a top-level
# configure script or Makefile.am, and no higher-priority manifest already
# detected. Without this, big C projects like jq (no Cargo/go.mod/etc.) used
# to fall through to the bash branch and get mis-classified as a bash CLI
# whose "binary" was whatever helper shell script (e.g. `compile-ios`)
# happened to live at the top of the repo.
if [ ${#langs[@]} -eq 0 ]; then
  if [ -f "$TARGET/configure.ac" ] || [ -f "$TARGET/configure.in" ] || \
     [ -f "$TARGET/Makefile.am" ] || [ -f "$TARGET/CMakeLists.txt" ] || \
     { [ -f "$TARGET/Makefile" ] && find "$TARGET" -maxdepth 2 \( -name '*.c' -o -name '*.cc' -o -name '*.cpp' -o -name '*.h' \) -print -quit 2>/dev/null | grep -q .; }; then
    langs+=("c_or_cpp")
    # Best guess for the binary name: AC_INIT([name], ...) from configure.ac,
    # else the repo basename. C projects don't have a manifest equivalent to
    # Cargo.toml's [[bin]] so this is a heuristic, but it beats falling
    # through to bash detection.
    if [ -f "$TARGET/configure.ac" ]; then
      ac_init_name=$(grep -oE 'AC_INIT\(\[[^],]+' "$TARGET/configure.ac" 2>/dev/null | head -1 | sed -E 's/AC_INIT\(\[//')
      [ -n "$ac_init_name" ] && binaries+=("$ac_init_name")
    fi
    [ ${#binaries[@]} -eq 0 ] && binaries+=("$(basename "$TARGET")")
  fi
fi

# Bash detection: only treat as a bash CLI if there are executable shell scripts
# at the top level (not nested in scripts/, tests/, etc.) AND no other primary
# language manifests already detected. This avoids false positives on Rust/Go/
# Py/C repos that ship helper shell scripts (e.g. jq's `compile-ios`).
if [ ${#langs[@]} -eq 0 ] && find "$TARGET" -maxdepth 1 -name '*.sh' -executable -print -quit 2>/dev/null | grep -q .; then
	langs+=("bash")
	while IFS= read -r bin; do
		binaries+=("$(basename "$bin")")
	done < <(find "$TARGET" -maxdepth 1 -name '*.sh' -executable 2>/dev/null | head -5)
fi

# Detect existing agent-ergonomic surfaces.
# Scan only source files (not README/CHANGELOG/docs which may mention future plans).
ROBOT_MODE_HINT=false
CAPABILITIES_HINT=false
ROBOT_DOCS_HINT=false

# Source-file globs (per language)
src_dirs=()
[ -d "$TARGET/src" ]      && src_dirs+=("$TARGET/src")
[ -d "$TARGET/cmd" ]      && src_dirs+=("$TARGET/cmd")
[ -d "$TARGET/internal" ] && src_dirs+=("$TARGET/internal")
[ -d "$TARGET/lib" ]      && src_dirs+=("$TARGET/lib")
# If no canonical src dirs, fall back to TARGET top-level files only (depth 1, no docs)
if [ ${#src_dirs[@]} -eq 0 ]; then
  while IFS= read -r f; do
    src_dirs+=("$f")
  done < <(find "$TARGET" -maxdepth 1 -type f \( -name '*.rs' -o -name '*.go' -o -name '*.py' -o -name '*.ts' -o -name '*.js' -o -name '*.sh' -o -name '*.rb' \) 2>/dev/null)
fi

if [ ${#src_dirs[@]} -gt 0 ]; then
  if grep -rqE --include='*.rs' --include='*.go' --include='*.py' --include='*.ts' --include='*.js' --include='*.sh' --include='*.rb' \
                -- '--robot-?[a-zA-Z]+' "${src_dirs[@]}" 2>/dev/null; then
    ROBOT_MODE_HINT=true
  fi
  if grep -rqE --include='*.rs' --include='*.go' --include='*.py' --include='*.ts' --include='*.js' --include='*.sh' --include='*.rb' \
                'capabilities[^a-zA-Z]+(--?json|json)|"capabilities"' "${src_dirs[@]}" 2>/dev/null; then
    CAPABILITIES_HINT=true
  fi
  if grep -rqE --include='*.rs' --include='*.go' --include='*.py' --include='*.ts' --include='*.js' --include='*.sh' --include='*.rb' \
                'robot-docs|--robot-help' "${src_dirs[@]}" 2>/dev/null; then
    ROBOT_DOCS_HINT=true
  fi
fi

# Detect env-var prefix (scan only source dirs, not docs)
prefix=""
if [ ${#binaries[@]} -gt 0 ] && [ ${#src_dirs[@]} -gt 0 ]; then
  for tool_name in "${binaries[@]}"; do
    upper=$(echo "$tool_name" | tr '[:lower:]' '[:upper:]' | tr '-' '_')
    if grep -rqE --include='*.rs' --include='*.go' --include='*.py' --include='*.ts' --include='*.js' --include='*.sh' --include='*.rb' \
                  "${upper}_[A-Z]+" "${src_dirs[@]}" 2>/dev/null; then
      prefix="$upper"
      break
    fi
  done
fi

# Recommend mode
if [ ${#binaries[@]} -le 1 ] && [ "$ROBOT_MODE_HINT" = false ]; then
  recommended_mode="full"
elif [ "$ROBOT_MODE_HINT" = true ] && [ "$CAPABILITIES_HINT" = true ] && [ "$ROBOT_DOCS_HINT" = true ]; then
  recommended_mode="audit-only"  # Already mature; might just be re-scoring
else
  recommended_mode="full"  # Has gaps; full pass would help
fi

# Emit JSON.
# Use jq to assemble so that paths/names containing `"` or `\` are properly escaped.
# `jq -n` builds JSON from --arg / --argjson inputs; this is the safe pattern.
#
# Note: `printf '%s\n'` with no args still emits one newline (because the format
# string is processed once even with zero args), which `jq -R | jq -cs` would then
# read as a single empty string and produce `[""]`. Detect empty arrays explicitly.
DISCOVERED_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)
if [ ${#langs[@]} -eq 0 ]; then
  LANGS_JSON='[]'
else
  LANGS_JSON=$(printf '%s\n' "${langs[@]}" | jq -R . | jq -cs .)
fi
if [ ${#binaries[@]} -eq 0 ]; then
  BINS_JSON='[]'
else
  BINS_JSON=$(printf '%s\n' "${binaries[@]}" | jq -R . | jq -cs .)
fi

jq -n \
  --arg target_path "$TARGET" \
  --arg discovered_at "$DISCOVERED_AT" \
  --argjson languages "$LANGS_JSON" \
  --argjson binaries "$BINS_JSON" \
  --arg env_var_prefix "$prefix" \
  --argjson robot_mode "$ROBOT_MODE_HINT" \
  --argjson capabilities "$CAPABILITIES_HINT" \
  --argjson robot_docs "$ROBOT_DOCS_HINT" \
  --arg recommended_mode "$recommended_mode" \
  '{
    target_path: $target_path,
    discovered_at: $discovered_at,
    languages: $languages,
    binaries: $binaries,
    env_var_prefix: $env_var_prefix,
    existing_surfaces: {
      robot_mode: $robot_mode,
      capabilities: $capabilities,
      robot_docs: $robot_docs
    },
    recommended_mode: $recommended_mode
  }'

exit 0
