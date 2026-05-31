#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skill_dir="$(cd "$script_dir/.." && pwd)"
scaffold="$skill_dir/scripts/shadow-scaffold"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

mkdir -p "$tmp/codex/skills/tune" "$tmp/codex/skills/seq" "$tmp/codex/skills/my skill"
: > "$tmp/codex/skills/tune/SKILL.md"
: > "$tmp/codex/skills/seq/SKILL.md"
: > "$tmp/codex/skills/my skill/SKILL.md"

assert_contains() {
  local haystack="$1"
  local needle="$2"
  if ! grep -F -- "$needle" <<<"$haystack" >/dev/null; then
    echo "expected output to contain: $needle" >&2
    echo "--- output ---" >&2
    echo "$haystack" >&2
    exit 1
  fi
}

assert_not_contains() {
  local haystack="$1"
  local needle="$2"
  if grep -F -- "$needle" <<<"$haystack" >/dev/null; then
    echo "expected output not to contain: $needle" >&2
    echo "--- output ---" >&2
    echo "$haystack" >&2
    exit 1
  fi
}

assert_fails() {
  if "$@" >/tmp/shadow-scaffold-test.out 2>/tmp/shadow-scaffold-test.err; then
    echo "expected command to fail: $*" >&2
    cat /tmp/shadow-scaffold-test.out >&2 || true
    cat /tmp/shadow-scaffold-test.err >&2 || true
    exit 1
  fi
}

bash -n "$scaffold"

help_out="$($scaffold --help)"
assert_contains "$help_out" "Usage: shadow-scaffold"

id_out="$(cd "$tmp" && "$scaffold" --session-id 019abc --skill '$tune')"
assert_contains "$id_out" "- Session ref kind: session-id"
assert_contains "$id_out" "- Lens: tune"
assert_contains "$id_out" "cat codex/skills/tune/SKILL.md"
assert_contains "$id_out" "--session-id 019abc"
assert_contains "$id_out" "--skill tune"
assert_contains "$id_out" "- Mode: propose"
assert_not_contains "$id_out" 'codex/skills/$tune'

path_out="$(cd "$tmp" && "$scaffold" --path /tmp/rollout.jsonl --skill tune)"
assert_contains "$path_out" "- Session ref kind: path"
assert_contains "$path_out" "seq session-detail --path /tmp/rollout.jsonl --format markdown"
assert_contains "$path_out" 'watched_session_id="<resolved-session-id>"'
assert_contains "$path_out" "seq tool-search --path /tmp/rollout.jsonl"

infer_path_out="$(cd "$tmp" && "$scaffold" --session ./rollout.jsonl --skill tune)"
assert_contains "$infer_path_out" "- Session ref kind: path"
assert_contains "$infer_path_out" "--path ./rollout.jsonl"

space_skill_out="$(cd "$tmp" && "$scaffold" --session-id 019abc --skill 'my skill')"
assert_contains "$space_skill_out" 'cat codex/skills/my\ skill/SKILL.md'

worker_out="$(cd "$tmp" && "$scaffold" --session-id 019abc --skill seq --include-workers)"
assert_contains "$worker_out" "## Worker/subagent follow-up"
assert_contains "$worker_out" "seq session-graph --root"

assert_fails "$scaffold" --session-id 019abc --skill tune --mode bad
assert_fails "$scaffold" --session-id 019abc
assert_fails "$scaffold" --session-id
assert_fails "$scaffold" --session-id 019abc --skill missing-skill

novalidate_out="$(cd "$tmp" && "$scaffold" --session-id 019abc --skill missing-skill --no-validate-skill)"
assert_contains "$novalidate_out" "- Lens: missing-skill"

printf 'shadow-scaffold tests passed\n'
