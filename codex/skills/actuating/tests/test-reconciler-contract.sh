#!/bin/sh
set -eu

skill_root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
codex_root=$(CDPATH='' cd -- "$skill_root/../.." && pwd)
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
grep -F '## Evidence acquisition before mutation' "$skill_root/SKILL.md" >/dev/null
grep -F '## Exactly two bug-driven mutation routes' "$skill_root/SKILL.md" >/dev/null
grep -F '## Construction Working Set' "$skill_root/SKILL.md" >/dev/null
grep -F 'No second Actuating Ledger definition' "$skill_root/SKILL.md" >/dev/null

grep -F '# Counterexample-to-Construction Compilation' \
  "$skill_root/references/counterexample-guided-normalization.md" >/dev/null
grep -F '## Admitted semantic carrier' \
  "$skill_root/references/counterexample-guided-normalization.md" >/dev/null
grep -F '## Producer migration' \
  "$skill_root/references/counterexample-guided-normalization.md" >/dev/null
grep -F 'Ablation is evidence that the construction absorbed the law' \
  "$skill_root/references/counterexample-guided-normalization.md" >/dev/null

grep -F 'continue the remaining initial lenses' \
  "$skill_root/references/review-contract.md" >/dev/null
grep -F 'for evidence only' \
  "$skill_root/references/review-contract.md" >/dev/null
grep -F 'A material confirmation finding' \
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
  .schema == "actuating-review-contract/v8" and
  .contract_id == "actuating-review-contract-v10" and
  (.required_lenses | length) == 5 and
  .review_scheduling.default_mode == "parallel-reviews" and
  .review_scheduling.modes["parallel-reviews"].non_cancelling == true and
  .review_scheduling.modes["serial-reviews"].continue_remaining_initial_lenses_after_invalidation == true and
  .review_scheduling.modes["serial-reviews"].post_invalidation_lenses_are_evidence_only == true and
  .evidence_acquisition.initial_falsification_wave_complete_before_successor_selection == true and
  .review_entry.admitted_carrier_required == true and
  .review_entry.complete_producer_factorization_required == true and
  .review_entry.complete_bypass_disposition_required == true and
  .mutation_routes.allowed ==
    ["construction-normalization", "isolated-restoration"] and
  .standard_convergence.required_consecutive_clean_attempts == 5
' "$skill_root/references/review-contract.json" >/dev/null

"$jaq_bin" -e '
  .skill_decision_contract.skill.source_fingerprint ==
    "actuating-construction-compiler-v1" and
  ([.skill_decision_contract.clauses[].clause_id] |
    index("ACT-CONSTRUCTION-COMPILER-001")) != null and
  ([.skill_decision_contract.clauses[].clause_id] |
    index("ACT-ISOLATED-RESTORATION-001")) != null and
  ([.skill_decision_contract.clauses[].clause_id] |
    index("ACT-REVIEW-EVIDENCE-001")) != null and
  ([.skill_decision_contract.clauses[].clause_id] |
    index("ACT-CLOSURE-001")) != null
' "$skill_root/references/decision-contract.json" >/dev/null

JAQ_BIN="$jaq_bin" "$skill_root/tests/test-direct-repair-admission.sh"
JAQ_BIN="$jaq_bin" "$skill_root/tests/test-semantic-hotspot-scenarios.sh"
JAQ_BIN="$jaq_bin" "$skill_root/tests/test-post-elimination-scenarios.sh"
JAQ_BIN="$jaq_bin" "$skill_root/tests/test-construction-cycle-scenarios.sh"

echo "actuating counterexample-to-construction contract: pass"
