#!/bin/sh
set -eu

skill_root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
ledger_bin=${LEDGER_BIN:-ledger}
jaq_bin=${JAQ_BIN:-jaq}
definition="$skill_root/definitions/ledger/counterexample-corpus.json"
manifest="$skill_root/migration.json"
valid="$skill_root/tests/fixtures/counterexample-capture-valid.json"
tmp=$(mktemp -d "${TMPDIR:-/tmp}/review-fold-counterexamples.XXXXXX")
tmp=$(CDPATH='' cd -- "$tmp" && pwd -P)
trap 'rm -rf "$tmp"' EXIT HUP INT TERM
repo="$tmp/repo"
catalog="$tmp/personal-custody"
mkdir -p "$repo"

"$ledger_bin" definition check \
  --definition "$definition" \
  --format json |
  "$jaq_bin" -e '
    .schema == "ledger-definition-check-result/v1" and
    .valid == true and
    .passive == true and
    .authority_granted == false
  ' >/dev/null

set +e
"$ledger_bin" context --catalog-root "$catalog" --workspace "$repo" \
  --read-only --definition "$definition" --owner-manifest "$manifest" \
  >"$tmp/missing-owner.json"
missing_status=$?
set -e
test "$missing_status" -eq 3
"$jaq_bin" -e '
  .error_code == "OwnerPreparationRequired" and .storage_mutated == false
' "$tmp/missing-owner.json" >/dev/null
test ! -e "$catalog"

"$ledger_bin" context --catalog-root "$catalog" --workspace "$repo" \
  --ensure-owner --definition "$definition" --owner-manifest "$manifest" \
  --confirm-no-legacy-writers >"$tmp/context.json"
store_root=$("$jaq_bin" -r '.store_root' "$tmp/context.json")
store_id=$("$jaq_bin" -r '.store_id' "$tmp/context.json")

"$ledger_bin" transact \
  --definition "$definition" \
  --operation capture \
  --store-root "$store_root" --store-id "$store_id" \
  --input "submission=$valid" \
  --format json >"$tmp/capture.json"

"$ledger_bin" context --catalog-root "$catalog" --workspace "$repo" \
  --read-only --definition "$definition" --owner-manifest "$manifest" \
  >"$tmp/read-context.json"
"$jaq_bin" -e --arg id "$store_id" '
  .store_id == $id and .source_coverage == "not_checked" and
  .owner_health.healthy == true and .storage_mutated == false and
  .authority_granted == false
' "$tmp/read-context.json" >/dev/null

"$ledger_bin" project \
  --definition "$definition" \
  --projection basis \
  --store-root "$store_root" --store-id "$store_id" \
  --param repository=example/repository \
  --payload-only \
  --format json >"$tmp/basis.json"

"$jaq_bin" -e '
  length == 1 and
  .[0].repository_id == "example/repository" and
  .[0].goal_digest ==
    "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" and
  .[0].law_ref == "law.transition-admissibility" and
  (. [0].id | test("^CEX-[a-f0-9]{24}$")) and
  (. [0].fingerprint | test("^[a-f0-9]{64}$"))
' "$tmp/basis.json" >/dev/null

counterexample_id=$(
  "$jaq_bin" -r '.[0].id' "$tmp/basis.json"
)

"$ledger_bin" transact \
  --definition "$definition" --operation capture \
  --store-root "$store_root" --store-id "$store_id" \
  --input "submission=$valid" --format json >"$tmp/retry.json"
"$jaq_bin" -e '.valid == true and .effects[0].result == "idempotent"' \
  "$tmp/retry.json" >/dev/null

rm -rf "$repo"
"$ledger_bin" context --catalog-root "$catalog" --store-id "$store_id" \
  --read-only --definition "$definition" --owner-manifest "$manifest" \
  >"$tmp/later-context.json"
"$jaq_bin" -e --arg id "$store_id" '
  .store_id == $id and .workspace_root == null and .storage_mutated == false
' "$tmp/later-context.json" >/dev/null

"$ledger_bin" project \
  --definition "$definition" \
  --projection record \
  --store-root "$store_root" --store-id "$store_id" \
  --param "id=$counterexample_id" \
  --payload-only \
  --format json >"$tmp/record.json"

"$jaq_bin" -e \
  --arg id "$counterexample_id" \
  '(.id == $id) and ((.observed_fact | length) > 0)' \
  "$tmp/record.json" >/dev/null
"$jaq_bin" -S '.[0]' "$tmp/basis.json" >"$tmp/original-record.json"
"$jaq_bin" -S '.' "$tmp/record.json" >"$tmp/later-record.json"
cmp "$tmp/original-record.json" "$tmp/later-record.json"

"$ledger_bin" project \
  --definition "$definition" \
  --projection law-history \
  --store-root "$store_root" --store-id "$store_id" \
  --param repository=example/repository \
  --param law=law.transition-admissibility \
  --payload-only \
  --format json >"$tmp/law-history.json"

"$jaq_bin" -e 'length == 1 and .[0].id == $id' \
  --arg id "$counterexample_id" \
  "$tmp/law-history.json" >/dev/null

expect_invalid() {
  name=$1
  filter=$2
  candidate="$tmp/$name.json"
  output="$tmp/$name.out.json"
  "$jaq_bin" "$filter" "$valid" >"$candidate"
  set +e
  "$ledger_bin" validate \
    --definition "$definition" \
    --input "submission=$candidate" \
    --format json >"$output"
  status=$?
  set -e
  if [ "$status" -eq 0 ]; then
    echo "expected counterexample corpus rejection: $name" >&2
    exit 1
  fi
  "$jaq_bin" -e '
    .schema == "ledger-validation-result/v1" and
    .valid == false and
    .storage_mutated == false
  ' "$output" >/dev/null
}

expect_invalid missing-authority-basis \
  '.record.authority_basis_refs = []'
expect_invalid missing-source-provenance \
  '.record.source_refs = []'
expect_invalid malformed-goal-digest \
  '.record.goal_digest = "not-a-digest"'
expect_invalid empty-observed-fact \
  '.record.observed_fact = ""'

echo "review-fold counterexample corpus: pass"
