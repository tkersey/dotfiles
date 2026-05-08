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
    seq|refine|cron|auto|ship|fin|.system) return 0 ;;
    *) return 1 ;;
  esac
}

auto_is_protected_path() {
  local path="$1"
  local root
  root="$(auto_skill_root)"
  case "$path" in
    "$root/.system"|"$root/.system"/*) return 0 ;;
  esac
  auto_is_protected_name "$(basename "$path")"
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
  if [ -n "$home" ]; then
    text="${text//$home/\$HOME}"
  fi
  printf '%s' "$text" \
    | sed -E 's#/Users/[^[:space:]/]+#\$HOME#g; s#/(private/)?var/folders/[^[:space:]]+#<temp-path>#g; s#(token|secret|password|credential)[=:][^[:space:]]+#\1=<redacted>#Ig' \
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

auto_write_conservative_policy() {
  local skill_dir="$1"
  local name
  name="$(basename "$skill_dir")"
  cat > "$skill_dir/AUTO.md" <<EOF_POLICY
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

auto_revert_owned_target_changes() {
  local target_dir="$1"
  [ -d "$target_dir" ] || auto_die "target directory not found for safe revert: $target_dir"
  git restore -- "$target_dir" 2>/dev/null || true
  git clean -fd -- "$target_dir"
}
