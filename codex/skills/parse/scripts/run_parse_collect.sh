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

json_array_from_lines() {
  if [ $# -eq 0 ]; then
    printf '[]'
    return 0
  fi
  printf '%s\n' "$@" | jq -R . | jq -s .
}

choose_focus_paths() {
  local repo_root="$1"
  local collect_json="$2"
  local repo_kind
  local -a focus_paths=()
  local -a preferred_dirs=()
  local candidate=""

  add_focus_path() {
    local path="$1"
    local existing=""
    [ -n "$path" ] || return 0
    [ -e "$repo_root/$path" ] || return 0
    if [ ${#focus_paths[@]} -gt 0 ]; then
      for existing in "${focus_paths[@]}"; do
        if [ "$existing" = "$path" ]; then
          return 0
        fi
      done
    fi
    if [ ${#focus_paths[@]} -lt 4 ]; then
      focus_paths+=("$path")
    fi
  }

  repo_kind="$(jq -r '.repo_kind_hints[0].repo_kind // ""' "$collect_json")"

  while IFS= read -r candidate; do
    add_focus_path "$candidate"
  done < <(jq -r '.manifests[].path // empty' "$collect_json")

  case "$repo_kind" in
    library-sdk)
      preferred_dirs=(src lib docs examples test tests bench)
      ;;
    cli-tooling)
      preferred_dirs=(cmd cli src lib docs test tests examples bench internal)
      ;;
    monorepo-platform)
      preferred_dirs=(apps packages services libs modules docs)
      ;;
    plugin-extension)
      preferred_dirs=(plugins plugin providers extensions src lib docs test tests)
      ;;
    infra-ops)
      preferred_dirs=(infra terraform ansible k8s helm scripts docs)
      ;;
    data-pipeline)
      preferred_dirs=(pipelines workflows dags jobs src sql docs test tests)
      ;;
    *)
      preferred_dirs=(src app apps packages cmd cli lib internal core services docs test tests examples bench tools codex nvim .config)
      ;;
  esac

  for candidate in "${preferred_dirs[@]}"; do
    if jq -r '.top_level_dirs[] // empty' "$collect_json" | grep -Fxq "$candidate"; then
      add_focus_path "$candidate"
    fi
  done

  for candidate in README.md FORMAL_CORE.md ARCHITECTURE.md docs/ARCHITECTURE.md docs/research_decision.md AGENTS.md; do
    add_focus_path "$candidate"
  done

  if [ ${#focus_paths[@]} -gt 0 ]; then
    printf '%s\n' "${focus_paths[@]}"
  fi
}

emit_repo_wide_collect() {
  local collect_json
  local thin_count=0
  local thin_repo_wide=false
  local focus_paths_json='[]'
  local thin_signal_classes_json='[]'
  local followup_hint=""
  local -a thin_signal_classes=()
  local -a focus_paths=()

  collect_json="$(mktemp)"
  trap 'rm -f "$collect_json"' EXIT

  if [ ${#extra_args[@]} -gt 0 ]; then
    parse-arch collect "$repo_path" "${extra_args[@]}" >"$collect_json"
  else
    parse-arch collect "$repo_path" >"$collect_json"
  fi

  if ! command -v jq >/dev/null 2>&1; then
    cat "$collect_json"
    trap - EXIT
    rm -f "$collect_json"
    return 0
  fi

  while IFS= read -r candidate; do
    [ -n "$candidate" ] && thin_signal_classes+=("$candidate")
  done < <(
    jq -r '
      [
        if (.repo_kind_hints | length) == 0 then "repo_kind_hints" else empty end,
        if .evidence_summary.entrypoint_hints == 0 then "entrypoint_hints" else empty end,
        if .evidence_summary.dependency_direction_hints == 0 then "dependency_direction_hints" else empty end,
        if .evidence_summary.runtime_boundary_hints == 0 then "runtime_boundary_hints" else empty end,
        if .evidence_summary.subsystem_hints == 0 then "subsystem_hints" else empty end
      ][]' "$collect_json"
  )

  thin_count="${#thin_signal_classes[@]}"
  if [ "$thin_count" -gt 0 ]; then
    thin_signal_classes_json="$(json_array_from_lines "${thin_signal_classes[@]}")"
  fi
  if [ "$thin_count" -ge 3 ]; then
    thin_repo_wide=true
    while IFS= read -r candidate; do
      [ -n "$candidate" ] && focus_paths+=("$candidate")
    done < <(choose_focus_paths "$repo_path" "$collect_json")
    if [ ${#focus_paths[@]} -gt 0 ]; then
      focus_paths_json="$(json_array_from_lines "${focus_paths[@]}")"
      followup_hint="Repo-wide signals are thin. Rerun the helper with the suggested focus paths before broader manual inspection."
    fi
  fi

  jq \
    --arg read_depth_verdict "$(if $thin_repo_wide; then echo thin_repo_wide; else echo repo_wide_ok; fi)" \
    --argjson thin_signal_classes "$thin_signal_classes_json" \
    --argjson suggested_focus_paths "$focus_paths_json" \
    --arg followup_hint "$followup_hint" \
    '
    . + {
      read_depth_verdict: $read_depth_verdict,
      thin_signal_classes: $thin_signal_classes,
      suggested_focus_paths: $suggested_focus_paths
    }
    + if ($followup_hint | length) > 0 then
        { followup_hint: $followup_hint }
      else
        {}
      end
    ' "$collect_json"

  trap - EXIT
  rm -f "$collect_json"
}

repo_path=""
extra_args=()
has_focus_paths=false

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
      if [ "$1" = "--focus-path" ]; then
        has_focus_paths=true
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
if $has_focus_paths; then
  exec parse-arch collect "$repo_path" "${extra_args[@]}"
fi
emit_repo_wide_collect
