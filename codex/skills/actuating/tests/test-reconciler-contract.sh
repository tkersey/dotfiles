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
grep -F 'predicted sibling counterexamples' \
  "$skill_root/references/semantic-hotspots.md" >/dev/null

grep -F 'law_authority: entailed | strengthening | preference' \
  "$codex_root/skills/review-fold/SKILL.md" >/dev/null
grep -F 'post_elimination_relation: none | same-law | different-law | unknown' \
  "$codex_root/skills/review-fold/SKILL.md" >/dev/null
grep -F 'reviewer consensus as Goal authority' \
  "$codex_root/skills/review-fold/SKILL.md" >/dev/null
grep -F 'Actuating must revoke and adjudicate' \
  "$codex_root/skills/review-fold/SKILL.md" >/dev/null

"$jaq_bin" -e '
  .schema == "actuating-review-contract/v2" and
  .contract_id == "actuating-review-contract-v4" and
  (.required_lenses | length) == 5 and
  ([.required_lenses[].name] | sort) ==
    (["standard", "footgun-finder", "invariant-ace",
      "complexity-mitigator", "fresh-eyes"] | sort) and
  .initial_wave.concurrent == true and
  .initial_wave.non_cancelling == true and
  .standard_convergence.required_consecutive_clean_attempts == 5 and
  .material_change.identity == "git-head" and
  .transport_recovery.maximum_fresh_recovery_attempts == 1
' "$skill_root/references/review-contract.json" >/dev/null

"$jaq_bin" -e '
  .skill_decision_contract.skill.source_fingerprint ==
    "actuating-post-elimination-falsifier-v5" and
  ([.skill_decision_contract.triggers[].trigger_id] |
    index("ACT-POST-ELIMINATION")) != null and
  ([.skill_decision_contract.clauses[].clause_id] |
    index("ACT-LAW-AUTHORITY-001")) != null and
  ([.skill_decision_contract.clauses[].clause_id] |
    index("ACT-POST-ELIMINATION-001")) != null and
  ([.skill_decision_contract.clauses[].clause_id] |
    index("ACT-CLOSURE-005")) != null
' "$skill_root/references/decision-contract.json" >/dev/null

"$jaq_bin" -e '
  .skill_decision_contract.skill.source_fingerprint ==
    "review-fold-law-authority-v2" and
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

echo "actuating post-elimination falsifier contract: pass"
