#!/usr/bin/env bash
set -euo pipefail

mesh_die() {
  echo "error: $*" >&2
  exit 2
}

mesh_require_cmd() {
  command -v "$1" >/dev/null 2>&1 || mesh_die "missing required command: $1"
}

mesh_common_flags() {
  cat <<'USAGE'
Common flags:
  -h, --help     Show help and exit
  --dry-run      Print intended actions without executing
  --json         Emit machine-readable JSON output
USAGE
}

mesh_json_escape() {
  local s="$1"
  s=${s//\\/\\\\}
  s=${s//\"/\\\"}
  s=${s//$'\n'/\\n}
  s=${s//$'\r'/\\r}
  s=${s//$'\t'/\\t}
  printf '%s' "$s"
}

mesh_parse_common_flags() {
  MESH_HELP=0
  MESH_DRY_RUN=0
  MESH_JSON=0
  MESH_ARGS=()

  while [[ $# -gt 0 ]]; do
    case "$1" in
      -h|--help)
        MESH_HELP=1
        shift
        ;;
      --dry-run)
        MESH_DRY_RUN=1
        shift
        ;;
      --json)
        MESH_JSON=1
        shift
        ;;
      --)
        shift
        MESH_ARGS+=("$@")
        break
        ;;
      -* )
        MESH_ARGS+=("$@")
        break
        ;;
      *)
        MESH_ARGS+=("$1")
        shift
        ;;
    esac
  done
}

mesh_emit() {
  if [[ "${MESH_JSON}" -eq 1 ]]; then
    printf '{"ok":true,"message":"%s"}\n' "$(mesh_json_escape "$1")"
  else
    echo "$1"
  fi
}

mesh_run() {
  if [[ "${MESH_DRY_RUN}" -eq 1 ]]; then
    mesh_emit "dry-run: $*"
    return 0
  fi
  "$@"
}
