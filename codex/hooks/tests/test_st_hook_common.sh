#!/bin/sh
set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
. "$script_dir/st_hook_common.sh"

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT INT HUP TERM

assert_eq() {
  expected="$1"
  actual="$2"
  label="$3"
  if [ "$expected" != "$actual" ]; then
    printf 'FAIL %s\nexpected: %s\nactual:   %s\n' "$label" "$expected" "$actual" >&2
    exit 1
  fi
}

canonical_repo="$tmp/canonical"
mkdir -p "$canonical_repo/.ledger/st" "$canonical_repo/nested"
: >"$canonical_repo/.ledger/st/st-plan.jsonl"
assert_eq "$canonical_repo" "$(find_st_root "$canonical_repo/nested")" "find canonical st root"
assert_eq ".ledger/st/st-plan.jsonl" "$(st_plan_rel "$canonical_repo")" "canonical st read path"
assert_eq ".ledger/st/st-plan.jsonl" "$(st_plan_write_rel)" "canonical st write path"

legacy_repo="$tmp/legacy"
mkdir -p "$legacy_repo/.step" "$legacy_repo/nested"
: >"$legacy_repo/.step/st-plan.jsonl"
assert_eq "$legacy_repo" "$(find_st_root "$legacy_repo/nested")" "find legacy st root"
assert_eq ".step/st-plan.jsonl" "$(st_plan_rel "$legacy_repo")" "legacy st read fallback"
assert_eq ".ledger/st/st-plan.jsonl" "$(st_plan_write_rel)" "legacy does not change write path"

both_repo="$tmp/both"
mkdir -p "$both_repo/.ledger/st" "$both_repo/.step"
: >"$both_repo/.ledger/st/st-plan.jsonl"
: >"$both_repo/.step/st-plan.jsonl"
assert_eq ".ledger/st/st-plan.jsonl" "$(st_plan_rel "$both_repo")" "canonical preferred over legacy"

printf 'st hook path policy: PASS\n'
