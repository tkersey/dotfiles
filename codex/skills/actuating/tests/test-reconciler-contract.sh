#!/bin/sh
set -eu

skill_root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
codex_root=$(CDPATH='' cd -- "$skill_root/../.." && pwd)
jaq_bin=${JAQ_BIN:-jaq}

for removed in \
  "$skill_root/definitions" \
  "$skill_root/hotspots" \
  "$skill_root/state" \
  "$skill_root/semantic-hotspots.json" \
  "$codex_root/skills/goal-contract/definitions" \
  "$codex_root/skills/review-fold/definitions" \
  "$codex_root/skills/review-fold/assets"
do
  if [ -e "$removed" ]; then
    echo "retired or prohibited protocol surface remains: $removed" >&2
    exit 1
  fi
done

active_files="
$skill_root/SKILL.md
$skill_root/references/architecture-reconciliation.md
$skill_root/references/semantic-hotspots.md
$skill_root/references/post-elimination-falsification.md
$skill_root/references/closure.md
$skill_root/references/review-contract.md
$codex_root/skills/goal-contract/SKILL.md
$codex_root/skills/review-fold/SKILL.md
$codex_root/skills/ship/SKILL.md
$codex_root/skills/cas/references/review-proof-boundary.md
$codex_root/skills/evidence-fold/SKILL.md
$codex_root/skills/reduce/SKILL.md
$codex_root/skills/universalist/SKILL.md
$codex_root/agents/review-reducer.toml
"

for pattern in \
  'construction-contract/v' \
  'counterexample-set/v1' \
  'actuating-evidence-event' \
  'actuating-closure-receipt' \
  'definitions/ledger/evidence-protocol' \
  'register-construction' \
  'register-counterexamples' \
  'prepare-operation' \
  'publication_observed'
do
  if printf '%s\n' "$active_files" | xargs grep -n -F "$pattern" >/dev/null 2>&1; then
    echo "retired protocol term remains: $pattern" >&2
    exit 1
  fi
done

grep -F 'level-triggered architecture reconciler' "$skill_root/SKILL.md" >/dev/null
grep -F '## Review-finding authority' "$skill_root/SKILL.md" >/dev/null
grep -F '## Elimination is a revocable theory lease' "$skill_root/SKILL.md" >/dev/null
grep -F 'revokes that elimination' "$skill_root/SKILL.md" >/dev/null
grep -F '## Generative reach and sibling prediction' "$skill_root/SKILL.md" >/dev/null
grep -F 'Passing repaired examples alone never reissues elimination' "$skill_root/SKILL.md" >/dev/null
grep -F 'No Actuating Ledger command' "$skill_root/SKILL.md" >/dev/null
grep -F 'Git is the realized construction' "$skill_root/SKILL.md" >/dev/null
grep -F '`parallel-reviews`' "$skill_root/SKILL.md" >/dev/null
grep -F '`serial-reviews`' "$skill_root/SKILL.md" >/dev/null
grep -F 'restart the selected' "$skill_root/SKILL.md" >/dev/null
grep -F "instruction-sensitive CAS target fingerprint remains receipt-scoped" \
  "$skill_root/SKILL.md" >/dev/null

review_context_block=$(sed -n '/^review_context:/,/^```$/p' \
  "$skill_root/references/review-contract.md")
if printf '%s\n' "$review_context_block" | grep -F 'target_fingerprint:' >/dev/null; then
  echo "shared review context still carries an instruction-sensitive target fingerprint" >&2
  exit 1
fi
if grep -F 'expected_cas_target_fingerprint' \
  "$skill_root/references/review-contract.md" >/dev/null; then
  echo "pre-dispatch binding still predicts CAS target identity" >&2
  exit 1
fi
grep -F 'instruction_digest' "$skill_root/references/review-contract.md" >/dev/null
grep -F 'requested_target_selector' "$skill_root/references/review-contract.md" >/dev/null
grep -F 'type, branch, sha, title' "$skill_root/references/review-contract.md" >/dev/null
grep -F 'git rev-parse --verify <selector>^{commit}' \
  "$skill_root/references/review-contract.md" >/dev/null
grep -F 'only bytes `0x20`, `0x09`, `0x0d`, and `0x0a`' \
  "$skill_root/references/review-contract.md" >/dev/null
grep -F '`uncommittedChanges` review' \
  "$skill_root/references/review-contract.md" >/dev/null
grep -F 'dedicated detached Git worktree' \
  "$skill_root/references/review-contract.md" >/dev/null
grep -F 'review_worktree_custody: campaign-exclusive' \
  "$skill_root/references/review-contract.md" >/dev/null
grep -F 'git status --porcelain == empty' \
  "$skill_root/references/review-contract.md" >/dev/null
grep -F 'actuating-external-symlink-closure/v1' \
  "$skill_root/references/review-contract.md" >/dev/null
grep -F 'Movable symbolic refs are not creditable' \
  "$skill_root/references/review-contract.md" >/dev/null
if grep -F 'expected base, head, and target fingerprint' \
  "$codex_root/skills/cas/references/review-proof-boundary.md" >/dev/null; then
  echo "CAS proof boundary still requires a caller-predicted target fingerprint" >&2
  exit 1
fi
grep -F 'owner-issued target fingerprint agrees' \
  "$codex_root/skills/cas/references/review-proof-boundary.md" >/dev/null
grep -F 'requested selector' \
  "$codex_root/skills/cas/references/review-proof-boundary.md" >/dev/null
grep -F 'target type, branch, sha, and title' \
  "$codex_root/skills/cas/references/review-proof-boundary.md" >/dev/null
grep -F 'developer instruction bytes match' \
  "$codex_root/skills/cas/references/review-proof-boundary.md" >/dev/null

grep -F '# Post-Elimination Falsification' \
  "$skill_root/references/post-elimination-falsification.md" >/dev/null
grep -F '## Immediate revocation' \
  "$skill_root/references/post-elimination-falsification.md" >/dev/null
grep -F '## Failed-premise localization' \
  "$skill_root/references/post-elimination-falsification.md" >/dev/null
grep -F '## Sibling prediction' \
  "$skill_root/references/post-elimination-falsification.md" >/dev/null
grep -F '## Reissuing elimination' \
  "$skill_root/references/post-elimination-falsification.md" >/dev/null
grep -F 'No unchanged-theory re-elimination from repaired examples' \
  "$skill_root/references/post-elimination-falsification.md" >/dev/null

grep -F 'Law authority' "$skill_root/references/semantic-hotspots.md" >/dev/null
grep -F 'post-elimination-falsification.md' \
  "$skill_root/references/semantic-hotspots.md" >/dev/null
tr '\n' ' ' < "$skill_root/references/semantic-hotspots.md" |
  grep -F 'predicted sibling counterexamples' >/dev/null

grep -F 'law_authority: entailed | strengthening | preference' \
  "$codex_root/skills/review-fold/SKILL.md" >/dev/null
grep -F 'post_elimination_relation: none | same-claim |' \
  "$codex_root/skills/review-fold/SKILL.md" >/dev/null
grep -F 'same-law-different-family | outside-horizon | different-law | unknown' \
  "$codex_root/skills/review-fold/SKILL.md" >/dev/null
grep -F 'recurrence.status = unknown' \
  "$codex_root/skills/review-fold/SKILL.md" >/dev/null
grep -F 'validity_horizon:' \
  "$codex_root/skills/review-fold/SKILL.md" >/dev/null
grep -F 'reviewer consensus as Goal authority' \
  "$codex_root/skills/review-fold/SKILL.md" >/dev/null
grep -F 'Actuating must revoke and adjudicate' \
  "$codex_root/skills/review-fold/SKILL.md" >/dev/null

"$jaq_bin" -e '
  .schema == "actuating-review-contract/v12" and
  .contract_id == "actuating-review-contract-v14" and
  (.required_lenses | length) == 5 and
  ([.required_lenses[].name] | sort) ==
    (["standard", "footgun-finder", "invariant-ace",
      "complexity-mitigator", "fresh-eyes"] | sort) and
  .review_scheduling.default_mode == "parallel-reviews" and
  .review_scheduling.request_local == true and
  .review_scheduling.all_lenses_required == true and
  .review_scheduling.initial_lens_order ==
    ["standard", "footgun-finder", "invariant-ace",
     "complexity-mitigator", "fresh-eyes"] and
  .review_scheduling.modes["parallel-reviews"].dispatch == "concurrent" and
  .review_scheduling.modes["parallel-reviews"].non_cancelling == true and
  .review_scheduling.modes["parallel-reviews"].terminal_barrier == true and
  .review_scheduling.modes["serial-reviews"].dispatch == "serial" and
  .review_scheduling.modes["serial-reviews"].adjudicate_before_next == true and
  .review_scheduling.modes["serial-reviews"].stop_before_next_on_material_change == true and
  .standard_convergence.required_consecutive_clean_attempts == 5 and
  .standard_convergence.initial_standard_counts == true and
  .standard_convergence.later_attempts_serial == true and
  .material_change.identity == "git-head" and
  .material_change.resets_all_review_credit == true and
  .material_change.restarts_selected_schedule_from_initial_standard == true and
  .target_binding.common_context_scope == "repository-base-head" and
  .target_binding.credited_target_types == ["baseBranch", "commit"] and
  .target_binding.uncommitted_changes_credit == "forbidden" and
  .target_binding.clean_worktree_required == true and
  .target_binding.movable_base_refs_credit == "forbidden" and
  .subject_custody.review_worktree == "campaign-exclusive-detached-at-head" and
  .subject_custody.implementation_worktree_separate == true and
  .subject_custody.sanctioned_writers_during_campaign == 0 and
  .subject_custody.cas_store_root == "outside-review-worktree" and
  .subject_custody.pre_attempt_head_and_clean_check == true and
  .subject_custody.post_attempt_head_and_clean_check == true and
  .subject_custody.tracked_external_symlink_closure.mode ==
    "bind-resolved-regular-file-bytes" and
  .subject_custody.tracked_external_symlink_closure.domain ==
    "actuating-external-symlink-closure/v1" and
  .subject_custody.tracked_external_symlink_closure.order ==
    "repository-path-byte-order" and
  .subject_custody.tracked_external_symlink_closure.record_fields ==
    ["repository_path", "link_target_bytes", "resolved_realpath", "target_sha256"] and
  .subject_custody.tracked_external_symlink_closure.non_regular_or_missing_target == "block" and
  .subject_custody.tracked_external_symlink_closure.sanctioned_writers == 0 and
  .subject_custody.tracked_external_symlink_closure.pre_attempt_digest_check == true and
  .subject_custody.tracked_external_symlink_closure.post_attempt_digest_check == true and
  .subject_custody.mismatch_action ==
    "reject-credit-and-restart-selected-schedule-in-fresh-worktree" and
  .target_binding.requested_target_selector_scope == "per-request-caller-owned" and
  .target_binding.requested_target_selector_encoding ==
    "compact-json-fixed-order-type-branch-sha-title-explicit-nulls" and
  .target_binding.requested_target_selector_value_canonicalization.baseBranch ==
    "trim-bytes-20-09-0d-0a-require-full-oid-merge-base-equals-context-base-null-sha-title" and
  .target_binding.requested_target_selector_value_canonicalization.commit ==
    "resolve-full-commit-oid-trim-title-bytes-20-09-0d-0a-null-empty" and
  .target_binding.cas_target_fingerprint_scope == "per-request-receipt" and
  .target_binding.request_fingerprint_includes_target_selector == true and
  .target_binding.request_fingerprint_includes_instruction_digest == true and
  .target_binding.caller_recomputes_cas_target_fingerprint == false and
  .target_binding.receipt_target_matches_requested_selector == true and
  .attempt_quality.exact_requested_target_selector_required == true and
  .attempt_quality.per_request_target_fingerprint_required == true and
  .attempt_quality.owner_issued_target_fingerprint_required == true and
  .attempt_quality.committed_subject_required == true and
  .attempt_quality.campaign_exclusive_worktree_required == true and
  .attempt_quality.external_symlink_closure_required == true and
  .attempt_quality.immutable_base_selector_required == true and
  .transport_recovery.maximum_fresh_recovery_attempts == 1
' "$skill_root/references/review-contract.json" >/dev/null

"$jaq_bin" -e '
  .skill_decision_contract.skill.source_fingerprint ==
    "actuating-review-subject-closure-v16" and
  ([.skill_decision_contract.triggers[].trigger_id] |
    index("ACT-POST-ELIMINATION")) != null and
  ([.skill_decision_contract.triggers[].trigger_id] |
    index("ACT-REVIEW-SCHEDULING")) != null and
  ([.skill_decision_contract.clauses[].clause_id] |
    index("ACT-LAW-AUTHORITY-001")) != null and
  ([.skill_decision_contract.clauses[].clause_id] |
    index("ACT-POST-ELIMINATION-001")) != null and
  ([.skill_decision_contract.clauses[].clause_id] |
    index("ACT-CLOSURE-005")) != null and
  ([.skill_decision_contract.clauses[] |
      select(.clause_id == "ACT-REVIEW-001") |
      .success_signals[]] |
    index("the shared review context binds repository, base, and head while each request verifies its owner-issued instruction-sensitive CAS target fingerprint from the terminal receipt")) != null and
  ([.skill_decision_contract.clauses[] |
      select(.clause_id == "ACT-REVIEW-001") |
      .success_signals[]] |
    index("each request binds its caller-owned canonical target selector before dispatch and exact-matches the receipt target afterward")) != null and
  ([.skill_decision_contract.clauses[] |
      select(.clause_id == "ACT-REVIEW-001") |
      .success_signals[]] |
    index("the caller-owned target selector has one exact compact JSON encoding with fixed fields and explicit nulls")) != null and
  ([.skill_decision_contract.clauses[] |
      select(.clause_id == "ACT-REVIEW-001") |
      .success_signals[]] |
    index("selector values are canonicalized to the exact public values CAS reports before request binding")) != null and
  ([.skill_decision_contract.clauses[] |
      select(.clause_id == "ACT-REVIEW-001") |
      .success_signals[]] |
    index("branch and title normalization use the exact CAS space-tab-CR-LF byte trim set")) != null and
  ([.skill_decision_contract.clauses[] |
      select(.clause_id == "ACT-REVIEW-001") |
      .success_signals[]] |
    index("Actuating review credit admits only clean committed baseBranch or commit subjects")) != null and
  ([.skill_decision_contract.clauses[] |
      select(.clause_id == "ACT-REVIEW-001") |
      .success_signals[]] |
    index("all credited attempts run in one campaign-exclusive detached worktree with no sanctioned writer and external CAS storage")) != null and
  ([.skill_decision_contract.clauses[] |
      select(.clause_id == "ACT-REVIEW-001") |
      .success_signals[]] |
    index("external tracked symlink targets are byte-bound in the common context and held under campaign custody")) != null and
  ([.skill_decision_contract.clauses[] |
      select(.clause_id == "ACT-REVIEW-001") |
      .success_signals[]] |
    index("baseBranch selectors use immutable full OIDs whose merge base equals the bound base")) != null and
  ([.skill_decision_contract.clauses[] |
      select(.clause_id == "ACT-REVIEW-001") |
      .failure_signals[]] |
    index("one instruction-sensitive CAS target fingerprint is reused as shared five-lens review-context identity")) != null and
  ([.skill_decision_contract.clauses[] |
      select(.clause_id == "ACT-REVIEW-001") |
      .failure_signals[]] |
    index("Actuating reimplements CAS private target serialization to predict a fingerprint before dispatch")) != null and
  ([.skill_decision_contract.clauses[] |
      select(.clause_id == "ACT-REVIEW-001") |
      .failure_signals[]] |
    index("receipt-only target identity receives credit without matching the caller-requested target selector")) != null
  and
  ([.skill_decision_contract.clauses[] |
      select(.clause_id == "ACT-REVIEW-001") |
      .failure_signals[]] |
    index("uncommitted reviews with changing dirty bytes contribute to one exact-head clean suffix")) != null
  and
  ([.skill_decision_contract.clauses[] |
      select(.clause_id == "ACT-REVIEW-001") |
      .failure_signals[]] |
    index("concurrent implementation edits can change and restore the review worktree during a credited attempt")) != null
  and
  ([.skill_decision_contract.clauses[] |
      select(.clause_id == "ACT-REVIEW-001") |
      .failure_signals[]] |
    index("external symlink target bytes change while the Git worktree remains clean")) != null and
  ([.skill_decision_contract.clauses[] |
      select(.clause_id == "ACT-REVIEW-001") |
      .failure_signals[]] |
    index("a movable symbolic base ref changes after receipt identity capture")) != null
' "$skill_root/references/decision-contract.json" >/dev/null

"$jaq_bin" -e '
  .skill_decision_contract.skill.source_fingerprint ==
    "review-fold-law-authority-v3" and
  ([.skill_decision_contract.triggers[].trigger_id] |
    index("RF-LAW-AUTHORITY")) != null and
  ([.skill_decision_contract.triggers[].trigger_id] |
    index("RF-POST-ELIMINATION")) != null and
  ([.skill_decision_contract.clauses[].clause_id] |
    index("RF-LAW-AUTHORITY-001")) != null and
  ([.skill_decision_contract.clauses[].clause_id] |
    index("RF-POST-ELIMINATION-001")) != null
' "$codex_root/skills/review-fold/references/decision-contract.json" >/dev/null

JAQ_BIN="$jaq_bin" "$skill_root/tests/test-semantic-hotspot-scenarios.sh"
JAQ_BIN="$jaq_bin" "$skill_root/tests/test-post-elimination-scenarios.sh"

echo "actuating review scheduling and post-elimination contract: pass"
