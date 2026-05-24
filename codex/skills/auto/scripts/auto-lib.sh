#!/usr/bin/env bash

auto_die() {
  printf 'auto: %s\n' "$*" >&2
  exit 1
}

auto_have() {
  command -v "$1" >/dev/null 2>&1
}

auto_repo_root() {
  git rev-parse --show-toplevel 2>/dev/null || auto_die "not inside a git repository"
}

auto_skill_root() {
  local root
  root="$(auto_repo_root)"
  printf '%s/codex/skills\n' "$root"
}

auto_quick_validate() {
  local root
  root="$(auto_repo_root)"
  printf '%s/codex/skills/.system/skill-creator/scripts/quick_validate.py\n' "$root"
}

auto_is_protected_name() {
  case "$1" in
    seq|refine|cron|auto|ship|land|.system) return 0 ;;
    *) return 1 ;;
  esac
}

auto_canonical_path() {
  local input_path="$1"
  local dir
  local base
  if [ -d "$input_path" ]; then
    (cd -P "$input_path" && pwd -P)
    return
  fi
  dir="$(dirname "$input_path")"
  base="$(basename "$input_path")"
  if [ -d "$dir" ]; then
    printf '%s/%s\n' "$(cd -P "$dir" && pwd -P)" "$base"
    return
  fi
  printf '%s\n' "$input_path"
}

auto_is_protected_path() {
  local input_path="$1"
  local root
  local canonical_path
  root="$(auto_canonical_path "$(auto_skill_root)")"
  canonical_path="$(auto_canonical_path "$input_path")"
  case "$canonical_path" in
    "$root/.system"|"$root/.system"/*) return 0 ;;
  esac
  auto_is_protected_name "$(basename "$canonical_path")"
}

auto_list_skill_dirs() {
  local skills
  skills="$(auto_skill_root)"
  [ -d "$skills" ] || auto_die "skills root not found: $skills"
  find "$skills" -mindepth 1 -maxdepth 1 -type d -exec test -f '{}/SKILL.md' ';' -print | sort
}

auto_list_ordinary_skill_dirs() {
  local dir
  while IFS= read -r dir; do
    if ! auto_is_protected_path "$dir"; then
      printf '%s\n' "$dir"
    fi
  done < <(auto_list_skill_dirs)
}

auto_strong_evidence_classes() {
  cat <<'TEXT'
repeated_session_evidence
explicit_user_feedback
clear_validation_failure
clear_routing_failure
TEXT
}

auto_weak_evidence_classes() {
  cat <<'TEXT'
thin_usage_signal
stale_metadata_signal
trigger_overlap_signal
workflow_ambiguity_signal
missing_validation_guidance
TEXT
}

auto_is_strong_evidence_class() {
  local class="$1"
  case "$class" in
    repeated_session_evidence|explicit_user_feedback|clear_validation_failure|clear_routing_failure) return 0 ;;
    *) return 1 ;;
  esac
}

auto_is_known_evidence_class() {
  local class="$1"
  case "$class" in
    repeated_session_evidence|explicit_user_feedback|clear_validation_failure|clear_routing_failure|thin_usage_signal|stale_metadata_signal|trigger_overlap_signal|workflow_ambiguity_signal|missing_validation_guidance) return 0 ;;
    *) return 1 ;;
  esac
}

auto_slugify() {
  printf '%s' "$1" \
    | tr '[:upper:]' '[:lower:]' \
    | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//; s/-+/-/g' \
    | cut -c 1-48
}

auto_sanitize_summary() {
  local text="${1:-}"
  local home="${HOME:-}"
  local tmpdir="${TMPDIR:-}"
  local normalized_tmpdir
  if [ -n "$home" ]; then
    text="${text//$home/\$HOME}"
  fi
  if [ -n "$tmpdir" ]; then
    normalized_tmpdir="${tmpdir%/}"
    text="${text//$normalized_tmpdir/<temp-path>}"
  fi
  # shellcheck disable=SC2016
  printf '%s' "$text" \
    | sed -E \
      -e 's#/Users/[^[:space:]/]+#\$HOME#g' \
      -e 's#/(private/)?tmp/[^[:space:]]+#<temp-path>#g' \
      -e 's#/(private/)?var/folders/[^[:space:]]+#<temp-path>#g' \
      -e 's#sk-[A-Za-z0-9_-]{16,}#<redacted-secret>#g' \
      -e 's#gh[pousr]_[A-Za-z0-9_]{16,}#<redacted-secret>#g' \
      -e 's#github_pat_[A-Za-z0-9_]{16,}#<redacted-secret>#g' \
      -e 's#AKIA[0-9A-Z]{16}#<redacted-secret>#g' \
      -e 's#eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}#<redacted-secret>#g' \
      -e 's#([Bb]earer[[:space:]]+)[A-Za-z0-9._~+/-]{16,}#\1<redacted>#g' \
      -e 's#([[:alnum:]_-]*(token|secret|password|credential|api[_-]?key|access[_-]?key|private[_-]?key)[[:alnum:]_-]*[[:space:]]*[=:][[:space:]]*).*$#\1<redacted>#Ig' \
      -e 's#(authorization[[:space:]]*:[[:space:]]*bearer[[:space:]]+).*$#\1<redacted>#Ig' \
    | tr '\n' ' ' \
    | cut -c 1-260
}

auto_git_status_snapshot() {
  git status --porcelain
}

auto_branch_exists() {
  git show-ref --verify --quiet "refs/heads/$1"
}

auto_remote_branch_exists() {
  git show-ref --verify --quiet "refs/remotes/origin/$1"
}

auto_require_tools() {
  local missing=0
  local tool
  for tool in "$@"; do
    if ! auto_have "$tool"; then
      printf 'missing tool: %s\n' "$tool" >&2
      missing=1
    fi
  done
  [ "$missing" -eq 0 ] || exit 1
}

auto_validate_one_skill() {
  local skill_dir="$1"
  local validator
  validator="$(auto_quick_validate)"
  [ -f "$validator" ] || auto_die "quick_validate.py not found: $validator"
  uv run --with pyyaml -- python3 "$validator" "$skill_dir"
}

auto_print_conservative_policy() {
  local name
  name="$1"
  cat <<EOF_POLICY
# AUTO

## Update Intent

Improve the \`$name\` skill when evidence shows its triggers, workflow, validation guidance, or bundled resources are causing avoidable friction.

## Allowed Changes

Conservative updates to \`SKILL.md\`, \`agents/openai.yaml\`, scripts, references, examples, or validation guidance when evidence shows a concrete need.

## Discouraged Changes

Avoid broad rewrites, speculative new workflows, scheduler/state additions, raw transcript copying, or changes that duplicate responsibilities owned by another skill.

## Evidence Cues

Prefer repeated session evidence, explicit user feedback, clear validation failures, or clear routing failures. Treat thin usage, stale metadata, trigger overlap, workflow ambiguity, and missing validation guidance as weak signals unless supported by stronger evidence.

## Validation Expectations

Run the relevant skill validation and any script-specific smoke checks. For ordinary skill edits, include quick validation proof and exact commands in the handoff.

## Examples of Safe Edits

- Tighten trigger wording after repeated routing misses.
- Add a concise validation step after observed skipped proof.
- Update a helper script only when the same deterministic action is repeatedly needed.
EOF_POLICY
}

auto_write_conservative_policy() {
  local skill_dir="$1"
  local name
  if [ -e "$skill_dir/AUTO.md" ] || [ -L "$skill_dir/AUTO.md" ]; then
    return 0
  fi
  name="$(basename "$skill_dir")"
  auto_print_conservative_policy "$name" > "$skill_dir/AUTO.md"
}

auto_ensure_skill_mentions_auto_policy() {
  local skill_md="$1"
  if grep -q 'AUTO.md' "$skill_md"; then
    return 0
  fi
  cat >> "$skill_md" <<'EOF_POLICY_REF'

## Auto Policy

When using `$auto` to evaluate this skill for evidence-backed maintenance, read `AUTO.md` if present. Treat it as advisory guidance, not as a hard constraint.
EOF_POLICY_REF
}
