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
grep -F 'The packet constrains admissibility, not imagination.' \
  "$skill_root/SKILL.md" >/dev/null
grep -F '`made irrelevant by mechanism change`' \
  "$skill_root/SKILL.md" >/dev/null
grep -F 'Metanoetic comparison surface / boundary dispositions / resource account' \
  "$skill_root/SKILL.md" >/dev/null
grep -F 'Treat each Universalist return as a **boundary contract**' \
  "$skill_root/SKILL.md" >/dev/null
grep -F 'source-derived predecessor topology T0' \
  "$skill_root/SKILL.md" >/dev/null
grep -F 'T1 = tau(T0)' "$skill_root/SKILL.md" >/dev/null
grep -F 'domain(F) = T1' "$skill_root/SKILL.md" >/dev/null
grep -F 'No self-authored omission list may serve as the sole evidence' \
  "$skill_root/SKILL.md" >/dev/null
grep -F 'A sanctioned path absent from the topology basis revokes' \
  "$skill_root/SKILL.md" >/dev/null
grep -F '| `$actuating analyze` |' "$skill_root/SKILL.md" >/dev/null
grep -F '`analyze` runs the complete counterexample-to-construction compiler' \
  "$skill_root/SKILL.md" >/dev/null

if grep -F '$actuating triage' "$skill_root/SKILL.md" >/dev/null ||
   grep -F '$actuating remediation-plan' "$skill_root/SKILL.md" >/dev/null
then
  echo "retired Actuating public route remains in SKILL.md" >&2
  exit 1
fi

grep -F '# Counterexample-to-Construction Compilation' \
  "$skill_root/references/counterexample-guided-normalization.md" >/dev/null
grep -F '## Durable source basis' \
  "$skill_root/references/counterexample-guided-normalization.md" >/dev/null
grep -F '## Consistency preflight' \
  "$skill_root/references/counterexample-guided-normalization.md" >/dev/null
grep -F '## Source-derived admission topology' \
  "$skill_root/references/counterexample-guided-normalization.md" >/dev/null
grep -F '## Admitted semantic carrier' \
  "$skill_root/references/counterexample-guided-normalization.md" >/dev/null
grep -F '## Invariant locus and semantic identity' \
  "$skill_root/references/counterexample-guided-normalization.md" >/dev/null
grep -F '## Source-derived factorization closure' \
  "$skill_root/references/counterexample-guided-normalization.md" >/dev/null
grep -F 'Adding a producer, edge, consumer, adapter, or bypass without a' \
  "$skill_root/references/counterexample-guided-normalization.md" >/dev/null
grep -F '## Producer migration' \
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
grep -F '## Source-derived factorization closure' \
  "$skill_root/references/review-contract.md" >/dev/null
grep -F 'A model-authored path list' \
  "$skill_root/references/review-contract.md" >/dev/null
grep -F 'second exact same-claim successor invalidation' \
  "$skill_root/references/review-contract.md" >/dev/null

grep -F 'source-derived predecessor topology T0' \
  "$skill_root/references/closure.md" >/dev/null
grep -F 'T1 = tau(T0) and domain(F) = T1' \
  "$skill_root/references/closure.md" >/dev/null
grep -F 'revokes topology and factorization closure immediately' \
  "$skill_root/references/closure.md" >/dev/null

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
  .schema == "actuating-review-contract/v12" and
  .contract_id == "actuating-review-contract-v14" and
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
  .candidate_lifecycle.topology_theorem_is_revocable_proof_lease == true and
  .candidate_lifecycle.revoked_theorem_closes_mutation_ship_and_review == true and
  .candidate_lifecycle.reviewable_reentry_after_revocation_requires_material_theorem_delta == true and
  .evidence_acquisition.initial_falsification_wave_complete_before_successor_selection == true and
  .evidence_acquisition.projected_counterexamples_are_reclassified == true and
  .review_entry.admitted_carrier_required == true and
  .review_entry.complete_producer_factorization_required == true and
  .review_entry.complete_bypass_disposition_required == true and
  .review_entry.universalist_boundary_contract_realized_required == true and
  .review_entry.universalist_claim_strength_preserved_required == true and
  .review_entry.split_seams_proved_before_recomposition_required == true and
  .review_entry.source_derived_topology_required_for_complete_claim == true and
  .review_entry.topology_authority_identity_strength_and_falsifier_required == true and
  .review_entry.universalist_total_transformation_required == true and
  .review_entry.exact_head_successor_topology_rederived_required == true and
  .review_entry.topology_transformation_equality_required == true and
  .review_entry.factorization_domain_equality_required == true and
  .review_entry.cut_domination_or_owned_residual_required == true and
  .review_entry.self_authored_omission_list_sufficient == false and
  .review_entry.unproved_complete_factorization_lowers_to_bounded_or_contained == true and
  .universalist_compilation.owner == "actuating" and
  .universalist_compilation.topology_domain_owner == "actuating" and
  .universalist_compilation.strongest_repository_native_authority_required == true and
  .universalist_compilation.model_authored_path_list_exhaustive_forbidden == true and
  .universalist_compilation.predecessor_topology_passed_to_universalist == true and
  .universalist_compilation.total_topology_transformation_required == true and
  .universalist_compilation.total_disposition_law_required == true and
  .universalist_compilation.allowed_element_dispositions ==
    ["factor-through", "retire", "privatize", "derived-adapter", "residual"] and
  .universalist_compilation.aggregate_outcomes_not_element_dispositions ==
    ["contained", "obstructed"] and
  .universalist_compilation.exact_head_topology_rederivation_required_before_reviewable == true and
  .universalist_compilation.topology_transformation_equality_required == true and
  .universalist_compilation.factorization_domain_equality_required == true and
  .universalist_compilation.factorized_routes_cross_cut_or_owned_residual_required == true and
  .universalist_compilation.self_authored_omission_list_sufficient == false and
  .universalist_compilation.prose_only_nomination_forbidden == true and
  .universalist_compilation.ephemeral_working_set_only == true and
  .mutation_routes.allowed ==
    ["construction-normalization", "isolated-restoration"] and
  .same_family_recurrence.same_claim_evidence_required == true and
  .same_family_recurrence.same_law_or_owner_alone_insufficient == true and
  .same_family_recurrence.direct_theorem_premise_falsifier_revokes_immediately == true and
  .same_family_recurrence.unmodeled_sanctioned_topology_element_revokes_immediately == true and
  .same_family_recurrence.topology_falsifier_never_realization_local == true and
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
    "actuating-construction-compiler-v6" and
  ((.skill_decision_contract.triggers[] |
    select(.trigger_id == "ACT-ROUTE") |
    .cue_literals) == [
      "$actuating implement",
      "$actuating analyze",
      "$actuating review-closeout"
    ]) and
  ([.skill_decision_contract.routes[].route_id] | sort) ==
    (["ACT-IMPLEMENT", "ACT-ANALYZE", "ACT-REVIEW-CLOSEOUT", "ACT-CLOSE"] | sort) and
  ((.skill_decision_contract.routes[] |
    select(.route_id == "ACT-ANALYZE") |
    .aliases) == ["analyze"]) and
  ((.skill_decision_contract.routes[] |
    select(.route_id == "ACT-ANALYZE") |
    .terminal) == true) and
  ([.skill_decision_contract.routes[].route_id] | index("ACT-TRIAGE")) == null and
  ([.skill_decision_contract.routes[].route_id] | index("ACT-REMEDIATION")) == null and
  all(.skill_decision_contract.clauses[];
    (.expected_routes | index("ACT-TRIAGE")) == null and
    (.expected_routes | index("ACT-REMEDIATION")) == null) and
  ([.skill_decision_contract.clauses[].clause_id] |
    index("ACT-CONSTRUCTION-COMPILER-001")) != null and
  ((.skill_decision_contract.clauses[] |
    select(.clause_id == "ACT-CONSTRUCTION-COMPILER-001") |
    .expected_routes) | index("ACT-ANALYZE")) != null and
  ((.skill_decision_contract.clauses[] |
    select(.clause_id == "ACT-CONSTRUCTION-COMPILER-001") |
    .required_artifacts) |
    index("source-derived predecessor topology T0")) != null and
  ((.skill_decision_contract.clauses[] |
    select(.clause_id == "ACT-CONSTRUCTION-COMPILER-001") |
    .required_artifacts) |
    index("domain(F) = T1")) != null and
  ((.skill_decision_contract.clauses[] |
    select(.clause_id == "ACT-REVIEW-EVIDENCE-001") |
    .required_artifacts) |
    index("review-fold/counterexample-corpus basis projection or explicit incomplete horizon")) != null and
  ([.skill_decision_contract.clauses[].clause_id] |
    index("ACT-METANOETIC-ADMISSIBILITY-001")) != null and
  ([.skill_decision_contract.clauses[].clause_id] |
    index("ACT-UNIVERSALIST-COMPILATION-001")) != null and
  ((.skill_decision_contract.clauses[] |
    select(.clause_id == "ACT-UNIVERSALIST-COMPILATION-001") |
    .required_artifacts) == [
      "one architectural axis and typed hole per Universalist invocation",
      "source-derived predecessor topology T0 with authority, identity, evidence strength, and falsifier",
      "candidate | preserve-incumbent | obstructed nomination",
      "linked split invocations for independently governed axes",
      "complete Universalist Actuating projection",
      "canonical admission cut K",
      "total topology transformation tau over T0",
      "total disposition law F with explicit residuals",
      "compiled boundary contract",
      "claim-strength ceiling",
      "factorization-closure verifier selected before mutation",
      "exact-head independently re-derived successor topology T1",
      "T1 = tau(T0)",
      "domain(F) = T1",
      "cut-domination or owned-residual proof",
      "exact-head boundary-contract realization proof"
    ]) and
  ((.skill_decision_contract.clauses[] |
    select(.clause_id == "ACT-UNIVERSALIST-COMPILATION-001") |
    .success_signals) |
    index("Universalist receives the repository-derived topology rather than rediscovering it from Actuating prose")) != null and
  ((.skill_decision_contract.clauses[] |
    select(.clause_id == "ACT-UNIVERSALIST-COMPILATION-001") |
    .failure_signals) |
    index("a model-authored omission list is the sole completeness proof")) != null and
  ((.skill_decision_contract.clauses[] |
    select(.clause_id == "ACT-CLOSURE-001") |
    .required_artifacts) |
    index("exact-head source-derived topology re-derivation proof")) != null and
  ((.skill_decision_contract.clauses[] |
    select(.clause_id == "ACT-CLOSURE-001") |
    .required_artifacts) |
    index("exact-head total factorization-domain and cut-domination proof")) != null and
  ([.skill_decision_contract.clauses[].clause_id] |
    index("ACT-ISOLATED-RESTORATION-001")) != null and
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
