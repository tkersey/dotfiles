#!/bin/sh
set -eu

skill_root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
codex_root=$(CDPATH='' cd -- "$skill_root/../.." && pwd)
jaq_bin=${JAQ_BIN:-jaq}

for removed in \
  "$skill_root/hotspots" \
  "$skill_root/state" \
  "$skill_root/semantic-hotspots.json" \
  "$skill_root/definitions/ledger/evidence-protocol.json" \
  "$skill_root/definitions/ledger/construction-contract.json" \
  "$skill_root/definitions/ledger/construction-registration-receipt.json" \
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
$skill_root/references/counterexample-guided-normalization.md
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
grep -F '## Counterexample-guided normalization' "$skill_root/SKILL.md" >/dev/null
grep -F 'Knowledge is monotone. Realization is not.' "$skill_root/SKILL.md" >/dev/null
grep -F '## Direct-repair admission gate' "$skill_root/SKILL.md" >/dev/null
grep -F 'actuating/direct-repair-admission' "$skill_root/SKILL.md" >/dev/null
grep -F '## Elimination is a revocable theory lease' "$skill_root/SKILL.md" >/dev/null
grep -F 'revokes that elimination' "$skill_root/SKILL.md" >/dev/null
grep -F '## Generative reach and sibling prediction' "$skill_root/SKILL.md" >/dev/null
grep -F 'Passing repaired examples alone never reissues elimination' "$skill_root/SKILL.md" >/dev/null
grep -F 'No durable Actuating workflow store' "$skill_root/SKILL.md" >/dev/null
grep -F 'Git is the realized construction' "$skill_root/SKILL.md" >/dev/null
grep -F '`parallel-reviews`' "$skill_root/SKILL.md" >/dev/null
grep -F '`serial-reviews`' "$skill_root/SKILL.md" >/dev/null
grep -F 'restart the selected' "$skill_root/SKILL.md" >/dev/null

grep -F '# Counterexample-Guided Normalization' \
  "$skill_root/references/counterexample-guided-normalization.md" >/dev/null
grep -F '## Why one gate' \
  "$skill_root/references/counterexample-guided-normalization.md" >/dev/null
grep -F '## Semantic-novelty firewall' \
  "$skill_root/references/counterexample-guided-normalization.md" >/dev/null
grep -F '## Ledger execution' \
  "$skill_root/references/counterexample-guided-normalization.md" >/dev/null
grep -F '## Gate falsifier and retirement rule' \
  "$skill_root/references/counterexample-guided-normalization.md" >/dev/null
grep -F 'No second same-generator member-specific repair' \
  "$skill_root/references/counterexample-guided-normalization.md" >/dev/null

grep -F '# Post-Elimination Falsification' \
  "$skill_root/references/post-elimination-falsification.md" >/dev/null
grep -F '## Immediate revocation' \
  "$skill_root/references/post-elimination-falsification.md" >/dev/null
grep -F '## Failed-premise localization' \
  "$skill_root/references/post-elimination-falsification.md" >/dev/null
grep -F '## Direct-repair admission' \
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
  .schema == "ledger-artifact-definition/v1" and
  .id == "actuating/direct-repair-admission" and
  .owner == "actuating" and
  .storage.kind == "pure" and
  .operations == {} and
  .projections == {} and
  .identity.op == "content-address" and
  (.requires.operators | index("reference-exists")) != null and
  (.requires.operators | index("field-equal")) != null
' "$skill_root/definitions/ledger/direct-repair-admission.json" >/dev/null

"$jaq_bin" -e '
  .schema == "actuating-review-contract/v3" and
  .contract_id == "actuating-review-contract-v5" and
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
  .transport_recovery.maximum_fresh_recovery_attempts == 1
' "$skill_root/references/review-contract.json" >/dev/null

"$jaq_bin" -e '
  .skill_decision_contract.skill.source_fingerprint ==
    "actuating-review-scheduling-v7" and
  ([.skill_decision_contract.triggers[].trigger_id] |
    index("ACT-POST-ELIMINATION")) != null and
  ([.skill_decision_contract.triggers[].trigger_id] |
    index("ACT-REVIEW-SCHEDULING")) != null and
  ([.skill_decision_contract.clauses[].clause_id] |
    index("ACT-LAW-AUTHORITY-001")) != null and
  ([.skill_decision_contract.clauses[].clause_id] |
    index("ACT-POST-ELIMINATION-001")) != null and
  ([.skill_decision_contract.clauses[].clause_id] |
    index("ACT-CLOSURE-005")) != null
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

JAQ_BIN="$jaq_bin" "$skill_root/tests/test-direct-repair-admission.sh"
JAQ_BIN="$jaq_bin" "$skill_root/tests/test-semantic-hotspot-scenarios.sh"
JAQ_BIN="$jaq_bin" "$skill_root/tests/test-post-elimination-scenarios.sh"

echo "actuating direct-repair admission and reconciler contract: pass"
