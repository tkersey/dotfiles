#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage:
  run_parse_collect.sh <repo_path> [--focus-path <path> ...] [--read-limit <n>] [--json] [--format json]
  run_parse_collect.sh --repo-path <repo_path> [--focus-path <path> ...] [--read-limit <n>] [--json] [--format json]
  run_parse_collect.sh --repo <repo_path> [--focus-path <path> ...] [--read-limit <n>] [--json] [--format json]

Notes:
  - Output is always JSON.
  - Use exactly one repo selector.
EOF
}

install_parse_arch_direct() {
  local repo="${SKILLS_ZIG_REPO:-$HOME/workspace/tk/skills-zig}"
  if ! command -v zig >/dev/null 2>&1; then
    echo "zig not found. Install Zig from https://ziglang.org/download/ and retry." >&2
    return 1
  fi
  if [ ! -d "$repo" ]; then
    echo "skills-zig repo not found at $repo." >&2
    echo "clone it with: git clone https://github.com/tkersey/skills-zig \"$repo\"" >&2
    return 1
  fi
  if ! (cd "$repo" && zig build build-parse-arch -Doptimize=ReleaseFast); then
    echo "direct Zig build failed in $repo." >&2
    return 1
  fi
  if [ ! -x "$repo/zig-out/bin/parse-arch" ]; then
    echo "direct Zig build did not produce $repo/zig-out/bin/parse-arch." >&2
    return 1
  fi
  mkdir -p "$HOME/.local/bin"
  install -m 0755 "$repo/zig-out/bin/parse-arch" "$HOME/.local/bin/parse-arch"
}

parse_arch_compatible() {
  command -v parse-arch >/dev/null 2>&1 &&
    parse-arch --help 2>&1 | grep -q "parse-arch collect --repo-path <repo_path>"
}

ensure_parse_arch() {
  local os
  os="$(uname -s)"

  if parse_arch_compatible; then
    return 0
  fi

  if [ "$os" = "Darwin" ]; then
    if ! command -v brew >/dev/null 2>&1; then
      echo "homebrew is required on macOS: https://brew.sh/" >&2
      return 1
    fi
    brew upgrade tkersey/tap/parse-arch >/dev/null 2>&1 || brew install tkersey/tap/parse-arch
  else
    install_parse_arch_direct
  fi

  if parse_arch_compatible; then
    return 0
  fi

  echo "parse-arch binary missing or incompatible after install attempt." >&2
  if [ "$os" = "Darwin" ]; then
    echo "expected install path: brew upgrade tkersey/tap/parse-arch || brew install tkersey/tap/parse-arch" >&2
  else
    echo "expected direct path: SKILLS_ZIG_REPO=<skills-zig-path> zig build build-parse-arch -Doptimize=ReleaseFast" >&2
  fi
  return 1
}

repo_path=""
extra_args=()

while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    --focus-path|--read-limit)
      if [ $# -lt 2 ]; then
        echo "Missing value for $1" >&2
        usage
        exit 2
      fi
      extra_args+=("$1" "$2")
      shift 2
      ;;
    --repo-path|--repo)
      if [ $# -lt 2 ]; then
        echo "Missing value for $1" >&2
        usage
        exit 2
      fi
      if [ -n "$repo_path" ]; then
        echo "Ambiguous repo_path source: $1" >&2
        usage
        exit 2
      fi
      repo_path="$2"
      shift 2
      ;;
    --json)
      shift
      ;;
    --format)
      if [ $# -lt 2 ]; then
        echo "Missing value for --format" >&2
        usage
        exit 2
      fi
      if [ "$2" != "json" ]; then
        echo "Unsupported value for --format: $2" >&2
        usage
        exit 2
      fi
      shift 2
      ;;
    -*)
      echo "Unknown flag: $1" >&2
      usage
      exit 2
      ;;
    *)
      if [ -n "$repo_path" ]; then
        echo "Ambiguous repo_path source: $1" >&2
        usage
        exit 2
      fi
      repo_path="$1"
      shift
      ;;
  esac
done

if [ -z "$repo_path" ]; then
  echo "Missing repo_path" >&2
  usage
  exit 2
fi

ensure_parse_arch
if [ ${#extra_args[@]} -gt 0 ]; then
  exec parse-arch collect "$repo_path" "${extra_args[@]}"
fi
exec parse-arch collect "$repo_path"
