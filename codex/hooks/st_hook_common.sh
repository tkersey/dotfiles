#!/bin/sh
set -eu

find_st_root() {
  dir="${1:-$PWD}"
  while [ "$dir" != "/" ]; do
    if [ -f "$dir/.step/st-plan.jsonl" ]; then
      printf '%s\n' "$dir"
      return 0
    fi
    dir=$(dirname "$dir")
  done
  return 1
}

st_plan_file() {
  printf '%s/.step/st-plan.jsonl\n' "$1"
}

json_continue() {
  jq -n '{continue: true}'
}

looks_like_wrap_up() {
  printf '%s' "${1:-}" | grep -Eiq '\b(done|completed|implemented|updated|changed|configured|wired|fixed|added|removed|created|verification|verified|validated|testing|tested|tests|pass(ed)?|smoke|setup)\b'
}

has_non_plan_changes() {
  repo_root="${1:?repo root required}"
  {
    git -C "$repo_root" diff --name-only
    git -C "$repo_root" diff --cached --name-only
    git -C "$repo_root" ls-files --others --exclude-standard
  } | awk 'NF' | sort -u | grep -Ev '(^|/)\.step/st-plan\.jsonl(\.lock)?$|(^|/)\.learnings\.jsonl$' | grep -q .
}

st_supports_command() {
  bin="${1:?binary required}"
  command_name="${2:?command required}"
  "$bin" --help 2>/dev/null | grep -Fq "$command_name"
}

resolve_st_bin() {
  required_command="${1:?command required}"

  if [ -n "${ST_HOOK_BINARY:-}" ] && [ -x "${ST_HOOK_BINARY:-}" ] && st_supports_command "$ST_HOOK_BINARY" "$required_command"; then
    printf '%s\n' "$ST_HOOK_BINARY"
    return 0
  fi

  for candidate in /Users/tk/workspace/tk/skills-zig/zig-out/bin/st "$(command -v st 2>/dev/null || true)"; do
    [ -n "${candidate:-}" ] || continue
    [ -x "$candidate" ] || continue
    if st_supports_command "$candidate" "$required_command"; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done

  return 1
}
