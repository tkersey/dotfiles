#!/bin/sh
set -eu
# Default includes the unchanged Review Fold/Ledger integration suite.
# --local-only runs all Actuating checks without invoking that external owner.
case "${1:-}" in
  '') local_only=false ;;
  --local-only) local_only=true ;;
  *) echo "usage: $0 [--local-only]" >&2; exit 2 ;;
esac
[ "$#" -le 1 ] || { echo "too many arguments" >&2; exit 2; }
skill_root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
if [ -n "${JAQ_BIN:-}" ]; then jaq_bin=$JAQ_BIN
elif command -v jaq >/dev/null 2>&1; then jaq_bin=jaq
else jaq_bin=jq
fi
node --input-type=module - "$skill_root" <<'JS'
import assert from 'node:assert/strict';
import {readFileSync, readdirSync, existsSync} from 'node:fs';
import {resolve, dirname, relative} from 'node:path';
const root = resolve(process.argv[2]);
const text = p => readFileSync(resolve(root,p), 'utf8');
const json = p => JSON.parse(text(p));
const c = json('references/review-contract.json');
const d = json('references/decision-contract.json').skill_decision_contract;
const names = ['standard','soundness-skeptic','footgun-finder','invariant-ace','complexity-mitigator','fresh-eyes'];
assert.equal(c.schema, 'actuating-review-contract/v16');
assert.equal(c.contract_id, 'actuating-review-contract-v18');
assert.equal(d.contract_version, 'SKDC-v1');
assert.equal(d.skill.source_fingerprint, 'actuating-construction-compiler-v10');
assert.deepEqual(c.required_lenses.map(l => l.name), names);
assert.deepEqual(c.required_lenses[0], {name:'standard',role:'standard',instruction_source:'codex-default',custom_instructions:false});
assert.deepEqual(c.review_scheduling.initial_lens_order, names);
assert.equal(c.review_scheduling.default_mode, 'parallel-reviews');
assert.deepEqual(Object.keys(c.review_scheduling.modes).sort(), ['parallel-reviews','serial-reviews']);
assert.equal(c.review_scheduling.modes['parallel-reviews'].non_cancelling, true);
assert.equal(c.review_scheduling.modes['parallel-reviews'].all_launched_semantic_outcomes_before_cut, true);
assert.equal(c.review_scheduling.modes['serial-reviews'].continue_remaining_initial_lenses_after_invalidation, true);
assert.equal(c.review_scheduling.modes['serial-reviews'].post_invalidation_lenses_are_evidence_only, true);
assert.deepEqual(c.standard_convergence, {
  required_consecutive_clean_attempts:5, initial_standard_counts:true,
  later_attempts_serial:true, findings_reset_streak:true,
  native_default_review_required:true, custom_instructions_forbidden:true
});
assert.equal(c.transport_recovery.maximum_fresh_recovery_attempts, 1);
assert.equal(c.transport_recovery.required_recovery_is_part_of_semantic_barrier, true);
assert.equal(c.attempt_quality.required_backend_class, 'cas-start-wait');
assert.equal(c.attempt_quality.required_capability, 'cas_workflow_bound_owner_lived_review_v1');
for (const key of ['strong_principal_required','current_tuple_required','exact_instruction_digest_required',
  'exact_workflow_binding_required','owner_lived_transport_required','fallback_forbidden']) assert.equal(c.attempt_quality[key], true, key);
assert.equal(c.review_epoch.initial_implementation_requires_review_dispatch, false);
assert.equal(c.review_epoch.successor_mutation_forbidden_while_open, true);
assert.equal(c.review_epoch.confirmation_invalidation_requires_new_initial_wave, false);
assert.equal(c.evidence_acquisition.initial_implementation_requires_initial_falsification_wave, false);
assert.equal(c.counterexample_corpus.definition, 'review-fold/counterexample-corpus');
assert.equal(c.counterexample_corpus.current_applicability_recomputed, true);
assert.equal(c.counterexample_corpus.actuating_copy_or_store_forbidden, true);
assert.equal(c.construction_selection.objective, 'family-exclusion-with-required-valid-preservation');
for (const key of ['cumulative_causal_basis_before_candidate_selection','discriminator_selected_before_implementation',
  'mechanical_defect_requires_no_invented_sibling_quota','metanoetic_before_universalist_when_triggered',
  'live_boundary_not_route_label_triggers_universalist']) assert.equal(c.construction_selection[key], true, key);
for (const key of ['local_repair_first_required','incumbent_preservation_is_dominance',
  'pre_mutation_theorem_equality_required','two_complete_implementations_required']) assert.equal(c.construction_selection[key], false, key);
assert.equal(c.review_entry.common_candidate_proof_regardless_of_label, true);
assert.equal(c.review_entry.actual_semantic_diff_authority_required, true);
assert.equal(c.candidate_acceptance.labels_grant_mutation_or_weaker_proof, false);
assert.equal(c.candidate_acceptance.self_authored_semantic_digests_are_evidence, false);
for (const key of ['strongest_repository_native_authority_required','independently_governed_axes_require_split',
  'complete_actuating_projection_required','total_topology_transformation_required','total_disposition_law_required',
  'exact_head_topology_rederivation_required_before_reviewable','topology_transformation_equality_required',
  'factorization_domain_equality_required','factorized_routes_cross_cut_or_owned_residual_required',
  'claim_strength_may_not_increase']) assert.equal(c.universalist_compilation[key], true, key);
assert.equal(c.universalist_compilation.self_authored_omission_list_sufficient, false);
assert.deepEqual(c.universalist_compilation.allowed_element_dispositions,
  ['factor-through','retire','privatize','derived-adapter','residual']);
assert.equal(c.same_family_recurrence.same_claim_revokes_exclusion_immediately, true);
assert.equal(c.same_family_recurrence.unmodeled_sanctioned_topology_element_revokes_immediately, true);
assert.equal(c.owner_source_frontier.omitted_live_finding_keeps_cut_open, true);
assert.equal(c.owner_source_frontier.unavailable_source_limits_only_dependent_claims, true);
assert.equal(c.efficacy.policy_unit_tests_prove_model_efficacy, false);
assert.equal(c.efficacy.counterexample_count_is_distance_to_correctness, false);
assert.deepEqual(d.routes.map(r => r.route_id).sort(),
  ['ACT-IMPLEMENT','ACT-ANALYZE','ACT-REVIEW-CLOSEOUT','ACT-CLOSE'].sort());
assert.deepEqual(d.routes.find(r => r.route_id === 'ACT-ANALYZE').aliases, ['analyze']);
for (const field of ['routes','triggers','clauses']) {
  const key = {routes:'route_id',triggers:'trigger_id',clauses:'clause_id'}[field];
  assert.equal(new Set(d[field].map(x => x[key])).size, d[field].length, field);
}
for (const cl of d.clauses) {
  for (const id of cl.trigger_refs) assert(d.triggers.some(t => t.trigger_id === id), id);
  for (const id of [...cl.expected_routes,...cl.prohibited_routes]) assert(d.routes.some(r => r.route_id === id), id);
}
assert.deepEqual(json('definitions/manifest.json'), {schema:'skill-definition-set/v1',skill:'actuating',seq:[],ledger:[]});
const retired = [
  'references/theorem-directed-response.md','references/standard-review.md',
  'definitions/ledger/direct-repair-admission.json',
  'tests/test-direct-repair-admission.sh','tests/fixtures/direct-repair-admission-valid.json'
];
for (const p of retired) assert(!existsSync(resolve(root,p)), `retired surface: ${p}`);
const walk = p => readdirSync(p,{withFileTypes:true}).flatMap(e => e.isDirectory() ? walk(resolve(p,e.name)) : [resolve(p,e.name)]);
assert.deepEqual(walk(resolve(root,'definitions')).map(p => relative(root,p)), ['definitions/manifest.json']);
for (const lens of c.required_lenses.slice(1)) {
  assert.equal(lens.role, 'auxiliary');
  assert(lens.instructions_ref.startsWith('codex/skills/actuating/'));
  assert(text(lens.instructions_ref.replace('codex/skills/actuating/','')).length > 0);
}
const forbidden = /direct-repair-admission|theorem-directed-response|predecessor_semantic_model_digest|successor_semantic_model_digest|theorem_directed_response|route_specific_construction_proof/;
for (const p of walk(root).filter(p => !relative(root,p).startsWith('tests/'))) {
  const s = readFileSync(p,'utf8');
  assert(!forbidden.test(s), `retired mechanism reference in ${p}`);
  if (p.endsWith('.json')) JSON.parse(s);
  if (p.endsWith('.md')) for (const m of s.matchAll(/\[[^\]]+\]\(([^)]+)\)/g)) {
    if (/^(https?:|#)/.test(m[1])) continue;
    assert(existsSync(resolve(dirname(p),m[1].split('#')[0])), `broken link: ${p} -> ${m[1]}`);
  }
}
assert(!/\$actuating (triage|remediation-plan)/.test(text('SKILL.md')));
assert(text('SKILL.md').includes('It dispatches no\nreview'));
assert(text('references/review-contract.md').includes('codex-default-review/v1'));
assert(text('agents/openai.yaml').includes('allow_implicit_invocation: true'));
console.log('actuating: contract, routing, proof ownership, retired surfaces, and reference links passed');
JS
sh "$skill_root/tests/test-construction-cycle-scenarios.sh"
sh "$skill_root/tests/test-post-elimination-scenarios.sh"
JAQ_BIN="$jaq_bin" sh "$skill_root/tests/test-semantic-hotspot-scenarios.sh"
if [ "$local_only" = true ]; then
  echo "actuating local suite: pass; Review Fold/Ledger integration explicitly not run"
else
  review_fold_root="$skill_root/../review-fold"
  JAQ_BIN="$jaq_bin" sh "$review_fold_root/tests/test-counterexample-corpus.sh"
  echo "actuating reconciler and Review Fold corpus integration: pass"
fi
