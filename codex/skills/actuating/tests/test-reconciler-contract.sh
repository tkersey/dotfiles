#!/bin/sh
set -eu

skill_root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
codex_root=$(CDPATH='' cd -- "$skill_root/../.." && pwd)
repo_root=$(CDPATH='' cd -- "$codex_root/.." && pwd)
jaq_bin=${JAQ_BIN:-jaq}

for removed in \
  "$skill_root/definitions" \
  "$codex_root/skills/goal-contract/definitions" \
  "$codex_root/skills/review-fold/definitions" \
  "$codex_root/skills/review-fold/assets"
do
  if [ -e "$removed" ]; then
    echo "retired protocol surface remains: $removed" >&2
    exit 1
  fi
done

for removed in \
  "$skill_root/references/artifact-kernel.md" \
  "$skill_root/references/construction-contract.md" \
  "$skill_root/references/evidence-ledger.md" \
  "$skill_root/references/review-accretion.md" \
  "$codex_root/skills/goal-contract/references/artifact-kernel-v1.md" \
  "$codex_root/skills/cas/definitions/ledger/review-finding.json" \
  "$codex_root/skills/cas/definitions/ledger/review-receipt.json"
do
  if [ -e "$removed" ]; then
    echo "retired file remains: $removed" >&2
    exit 1
  fi
done

active_files="
$skill_root/SKILL.md
$skill_root/references/architecture-reconciliation.md
$skill_root/references/closure.md
$skill_root/references/review-contract.md
$codex_root/skills/goal-contract/SKILL.md
$codex_root/skills/review-fold/SKILL.md
$codex_root/skills/ship/SKILL.md
$codex_root/skills/ship/references/ship-record.md
$codex_root/skills/cas/references/review-proof-boundary.md
$codex_root/skills/evidence-fold/SKILL.md
$codex_root/skills/complexity-mitigator/SKILL.md
$codex_root/skills/reduce/SKILL.md
$codex_root/skills/universalist/SKILL.md
$codex_root/skills/universalist/README.md
$codex_root/skills/negative-ledger/references/counterexample-construction-integration.md
$codex_root/agents/review-reducer.toml
$codex_root/agents/one-seam-operator.toml
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
  'publication_observed' \
  'goal_contract_ref' \
  'construction_ref' \
  'expected_subject_digest' \
  'proof_obligation_refs'
do
  if printf '%s\n' "$active_files" | xargs grep -n -F "$pattern" >/dev/null 2>&1; then
    echo "retired protocol term remains: $pattern" >&2
    exit 1
  fi
done

grep -F 'level-triggered architecture reconciler' "$skill_root/SKILL.md" >/dev/null
grep -F 'Architecture-closure test' "$skill_root/SKILL.md" >/dev/null
grep -F 'Architecture Working Set' "$skill_root/SKILL.md" >/dev/null
grep -F 'No Actuating Ledger command' "$skill_root/SKILL.md" >/dev/null
grep -F 'Git is the realized construction' "$skill_root/SKILL.md" >/dev/null
grep -F 'start a fresh full wave' "$skill_root/references/review-contract.md" >/dev/null
grep -F 'publication observation digest' "$skill_root/references/review-contract.md" >/dev/null

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
    "actuating-live-reconciler-v1" and
  ([.skill_decision_contract.routes[].route_id] | sort) ==
    (["ACT-IMPLEMENT", "ACT-TRIAGE", "ACT-REMEDIATION",
      "ACT-REVIEW-CLOSEOUT", "ACT-SHIP-HANDOFF", "ACT-CLOSE"] | sort)
' "$skill_root/references/decision-contract.json" >/dev/null

"$jaq_bin" -e '
  .ledger == [{
    "id": "cas/fork-inquiry-receipt",
    "path": "ledger/fork-inquiry-receipt.json"
  }]
' "$codex_root/skills/cas/definitions/manifest.json" >/dev/null

for lens in standard-review.md \
  lenses/footgun-review.md \
  lenses/invariant-review.md \
  lenses/complexity-review.md \
  lenses/fresh-eyes-review.md
do
  test -s "$skill_root/references/$lens"
done

echo "actuating reconciler contract: pass"
