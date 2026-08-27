#!/bin/sh
set -eu

skill_root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
codex_root=$(CDPATH='' cd -- "$skill_root/../.." && pwd)
review_fold_root="$codex_root/skills/review-fold"
jaq_bin=${JAQ_BIN:-jaq}

for removed in \
  "$skill_root/definitions/ledger/cumulative-ablation-basis.json" \
  "$skill_root/references/cumulative-ablation-contract.json" \
  "$skill_root/tests/test-cumulative-ablation-basis.sh" \
  "$skill_root/tests/test-cumulative-ablation-scenarios.sh" \
  "$skill_root/tests/fixtures/cumulative-ablation-basis-valid.json" \
  "$skill_root/tests/fixtures/cumulative-ablation-scenarios.json" \
  "$skill_root/tests/test-review-candidate-traces.sh" \
  "$skill_root/tests/fixtures/review-candidate-traces.json"
do
  if [ -e "$removed" ]; then
    echo "retired process surface remains: $removed" >&2
    exit 1
  fi
done

grep -F 'counterexample-to-construction compiler' "$skill_root/SKILL.md" >/dev/null
grep -F 'review-fold/counterexample-corpus' "$skill_root/SKILL.md" >/dev/null
grep -F 'Counterexample corpus basis IDs' "$skill_root/SKILL.md" >/dev/null
grep -F 'No durable **Actuating** workflow' "$skill_root/SKILL.md" >/dev/null
grep -F '## Evidence acquisition before mutation' "$skill_root/SKILL.md" >/dev/null
grep -F '## Exactly two bug-driven mutation routes' "$skill_root/SKILL.md" >/dev/null
grep -F '## Construction Working Set' "$skill_root/SKILL.md" >/dev/null
grep -F 'No second Actuating Ledger definition' "$skill_root/SKILL.md" >/dev/null
grep -F 'Construction completeness is a revocable proof lease' \
  "$skill_root/SKILL.md" >/dev/null
grep -F 'No third reviewable candidate under a materially unchanged theorem' \
  "$skill_root/SKILL.md" >/dev/null

grep -F '# Counterexample-to-Construction Compilation' \
  "$skill_root/references/counterexample-guided-normalization.md" >/dev/null
grep -F '## Durable source basis' \
  "$skill_root/references/counterexample-guided-normalization.md" >/dev/null
grep -F '## Consistency preflight' \
  "$skill_root/references/counterexample-guided-normalization.md" >/dev/null
grep -F '## Admitted semantic carrier' \
  "$skill_root/references/counterexample-guided-normalization.md" >/dev/null
grep -F 'sanctioned producer-to-trusted-consumer path' \
  "$skill_root/references/counterexample-guided-normalization.md" >/dev/null
grep -F '## Invariant locus and semantic identity' \
  "$skill_root/references/counterexample-guided-normalization.md" >/dev/null
grep -F '## Producer migration' \
  "$skill_root/references/counterexample-guided-normalization.md" >/dev/null
grep -F 'canonical constructor is not factorization' \
  "$skill_root/references/counterexample-guided-normalization.md" >/dev/null
grep -F 'Ablation is evidence that the construction absorbed the law' \
  "$skill_root/references/counterexample-guided-normalization.md" >/dev/null

grep -F '# Counterexample Corpus' \
  "$review_fold_root/references/counterexample-corpus.md" >/dev/null
grep -F 'Persist counterexamples; recompile their meaning.' \
  "$review_fold_root/references/counterexample-corpus.md" >/dev/null
grep -F 'Capture each independent witness' \
  "$review_fold_root/SKILL.md" >/dev/null
grep -F 'Do not persist a Review Fold, class registry, family registry' \
  "$review_fold_root/SKILL.md" >/dev/null

grep -F 'continue the remaining initial lenses' \
  "$skill_root/references/review-contract.md" >/dev/null
grep -F 'for evidence only' \
  "$skill_root/references/review-contract.md" >/dev/null
grep -F 'A material confirmation finding' \
  "$skill_root/references/review-contract.md" >/dev/null
grep -F '## Counterexample history projection' \
  "$skill_root/references/review-contract.md" >/dev/null
grep -F '### Construction-theorem proof lease' \
  "$skill_root/references/review-contract.md" >/dev/null
grep -F 'second exact same-claim successor invalidation' \
  "$skill_root/references/review-contract.md" >/dev/null
grep -F 'executable or exhaustive factorization witness' \
  "$skill_root/references/review-contract.md" >/dev/null

for lens in \
  "$skill_root/references/standard-review.md" \
  "$skill_root/references/lenses/footgun-review.md" \
  "$skill_root/references/lenses/invariant-review.md" \
  "$skill_root/references/lenses/complexity-review.md" \
  "$skill_root/references/lenses/fresh-eyes-review.md"
do
  test -s "$lens"
done

"$jaq_bin" -e '
  .schema == "skill-definition-set/v1" and
  .skill == "actuating" and
  .seq == [] and
  .ledger == [
    {
      "id": "actuating/direct-repair-admission",
      "path": "ledger/direct-repair-admission.json"
    }
  ]
' "$skill_root/definitions/manifest.json" >/dev/null

"$jaq_bin" -e '
  .schema == "skill-definition-set/v1" and
  .skill == "review-fold" and
  .seq == [] and
  .ledger == [
    {
      "id": "review-fold/counterexample-corpus",
      "path": "ledger/counterexample-corpus.json"
    }
  ]
' "$review_fold_root/definitions/manifest.json" >/dev/null

"$jaq_bin" -e '
  .schema == "ledger-artifact-definition/v1" and
  .id == "review-fold/counterexample-corpus" and
  .owner == "review-fold" and
  .storage.kind == "event-log" and
  .storage.slots.events.path == "review-fold/counterexamples/events.jsonl" and
  ([.operations | keys[]] | sort) ==
    (["bind-existing", "capture", "rebind-existing"] | sort) and
  ([.projections | keys[]] | sort) ==
    (["basis", "law-history", "record"] | sort)
' "$review_fold_root/definitions/ledger/counterexample-corpus.json" >/dev/null

"$jaq_bin" -e '
  .schema == "actuating-review-contract/v10" and
  .contract_id == "actuating-review-contract-v12" and
  (.required_lenses | length) == 5 and
  .review_scheduling.default_mode == "parallel-reviews" and
  .review_scheduling.modes["parallel-reviews"].non_cancelling == true and
  .review_scheduling.modes["serial-reviews"].continue_remaining_initial_lenses_after_invalidation == true and
  .review_scheduling.modes["serial-reviews"].post_invalidation_lenses_are_evidence_only == true and
  .counterexample_corpus.owner == "review-fold" and
  .counterexample_corpus.definition == "review-fold/counterexample-corpus" and
  .counterexample_corpus.project_before_current_fold == true and
  .counterexample_corpus.capture_after_current_fold == true and
  .counterexample_corpus.current_applicability_recomputed == true and
  .counterexample_corpus.actuating_copy_or_store_forbidden == true and
  .candidate_lifecycle.construction_theorem_is_revocable_proof_lease == true and
  .candidate_lifecycle.revoked_theorem_closes_mutation_ship_and_review == true and
  .candidate_lifecycle.reviewable_reentry_after_revocation_requires_material_theorem_delta == true and
  .evidence_acquisition.initial_falsification_wave_complete_before_successor_selection == true and
  .evidence_acquisition.projected_counterexamples_are_reclassified == true and
  .review_entry.admitted_carrier_required == true and
  .review_entry.complete_producer_factorization_required == true and
  .review_entry.complete_bypass_disposition_required == true and
  .mutation_routes.allowed ==
    ["construction-normalization", "isolated-restoration"] and
  .same_family_recurrence.same_claim_evidence_required == true and
  .same_family_recurrence.same_law_or_owner_alone_insufficient == true and
  .same_family_recurrence.direct_theorem_premise_falsifier_revokes_immediately == true and
  .same_family_recurrence.second_same_claim_successor_invalidation_under_unchanged_theorem_revokes_theorem == true and
  .same_family_recurrence.third_reviewable_candidate_under_unchanged_theorem_forbidden == true and
  .same_family_recurrence.material_theorem_delta_required_for_reentry == true and
  .same_family_recurrence.source_anchored_admission_topology_required_for_reentry == true and
  .same_family_recurrence.executable_or_exhaustive_factorization_witness_required_for_reentry == true and
  .same_family_recurrence.same_law_different_family_does_not_increment == true and
  .standard_convergence.required_consecutive_clean_attempts == 5
' "$skill_root/references/review-contract.json" >/dev/null

"$jaq_bin" -e '
  .skill_decision_contract.skill.source_fingerprint ==
    "actuating-construction-compiler-v2" and
  ([.skill_decision_contract.clauses[].clause_id] |
    index("ACT-CONSTRUCTION-COMPILER-001")) != null and
  ((.skill_decision_contract.clauses[] |
    select(.clause_id == "ACT-CONSTRUCTION-COMPILER-001") |
    .required_artifacts[7:20]) == [
      "required-valid / invalid-family separation",
      "invalid-family exclusion",
      "strongest honest invariant locus",
      "canonical identity or explicit equivalence",
      "admission-path domination",
      "semantic producer factorization",
      "canonical ownership",
      "bypass closure",
      "required-valid and compatibility preservation",
      "family-level or exhaustive proof",
      "downstream compensator retirement",
      "lifecycle and realization cost",
      "raw source size"
    ]) and
  ((.skill_decision_contract.clauses[] |
    select(.clause_id == "ACT-REVIEW-EVIDENCE-001") |
    .required_artifacts) |
    index("review-fold/counterexample-corpus basis projection or explicit incomplete horizon")) != null and
  ([.skill_decision_contract.clauses[].clause_id] |
    index("ACT-ISOLATED-RESTORATION-001")) != null and
  ([.skill_decision_contract.clauses[].clause_id] |
    index("ACT-REVIEW-EVIDENCE-001")) != null and
  ([.skill_decision_contract.clauses[].clause_id] |
    index("ACT-CLOSURE-001")) != null
' "$skill_root/references/decision-contract.json" >/dev/null

"$jaq_bin" -e '
  .skill_decision_contract.skill.source_fingerprint ==
    "review-fold-counterexample-corpus-v1" and
  ([.skill_decision_contract.clauses[].clause_id] |
    index("RF-COUNTEREXAMPLE-CORPUS-001")) != null and
  .skill_decision_contract.instrumentation.counterexample_corpus ==
    "review-fold/counterexample-corpus"
' "$review_fold_root/references/decision-contract.json" >/dev/null

JAQ_BIN="$jaq_bin" "$review_fold_root/tests/test-counterexample-corpus.sh"
JAQ_BIN="$jaq_bin" "$skill_root/tests/test-direct-repair-admission.sh"
JAQ_BIN="$jaq_bin" "$skill_root/tests/test-semantic-hotspot-scenarios.sh"
JAQ_BIN="$jaq_bin" "$skill_root/tests/test-post-elimination-scenarios.sh"
JAQ_BIN="$jaq_bin" "$skill_root/tests/test-construction-cycle-scenarios.sh"

echo "actuating counterexample-to-construction and corpus contract: pass"
