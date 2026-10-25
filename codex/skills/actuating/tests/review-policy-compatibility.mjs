import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';

const canonical = value => Array.isArray(value) ? value.map(canonical)
  : value && typeof value === 'object'
    ? Object.fromEntries(Object.keys(value).sort().map(key => [key,canonical(value[key])]))
    : value;

export function assertNativeReviewPolicy(policy) {
  const native = policy.review_execution.modes.cas;
  const projected = structuredClone(policy);
  Object.assign(projected.required_lenses[0], {
    instruction_source:native.standard_review.instruction_source,
    custom_instructions:native.standard_review.custom_instructions
  });
  Object.assign(projected.focused_file_reviews.standard_review,native.file_standard);
  for (const key of ['owner','source','custom_instructions_argument_forbidden',
    'skill_authored_instruction_file_forbidden'])
    projected.review_scheduling.standard_review[key] = native.standard_review[key];
  delete projected.standard_convergence.selected_execution_mode_required;
  delete projected.standard_convergence.distinct_contexts_required;
  for (const key of ['native_default_review_required','custom_instructions_forbidden'])
    projected.standard_convergence[key] = native.standard_review[key];
  Object.assign(projected.attempt_quality,native.attempt_quality);
  const keys = ['required_lenses','focused_file_reviews','review_scheduling',
    'candidate_lifecycle','review_epoch','review_entry','evidence_acquisition',
    'standard_convergence','material_change','transport_recovery','attempt_quality'];
  const bytes = JSON.stringify(canonical(Object.fromEntries(keys.map(key => [key,projected[key]]))));
  assert.equal(createHash('sha256').update(bytes).digest('hex'),
    '8c13cc173966b7143d41f967ba6861e4f36fa2909b7cff5d980a747899905f37',
    'native review policy changed from the accepted pre-portability contract');
}
