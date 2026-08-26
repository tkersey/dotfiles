#!/bin/sh
set -eu

skill_root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
ledger_bin=${LEDGER_BIN:-ledger}
jaq_bin=${JAQ_BIN:-jaq}
definition="$skill_root/definitions/ledger/counterexample-corpus.json"
valid="$skill_root/tests/fixtures/counterexample-capture-valid.json"
tmp=$(mktemp -d "${TMPDIR:-/tmp}/review-fold-counterexamples.XXXXXX")
tmp=$(CDPATH='' cd -- "$tmp" && pwd -P)
trap 'rm -rf "$tmp"' EXIT HUP INT TERM
repo="$tmp/repo"
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

"$ledger_bin" transact \
  --definition "$definition" \
  --operation capture \
  --repo "$repo" \
  --input "submission=$valid" \
  --format json >"$tmp/capture.json"

"$ledger_bin" project \
  --definition "$definition" \
  --projection basis \
  --repo "$repo" \
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

"$ledger_bin" project \
  --definition "$definition" \
  --projection record \
  --repo "$repo" \
  --param "id=$counterexample_id" \
  --payload-only \
  --format json >"$tmp/record.json"

"$jaq_bin" -e \
  --arg id "$counterexample_id" \
  '(.id == $id) and ((.observed_fact | length) > 0)' \
  "$tmp/record.json" >/dev/null

"$ledger_bin" project \
  --definition "$definition" \
  --projection law-history \
  --repo "$repo" \
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
