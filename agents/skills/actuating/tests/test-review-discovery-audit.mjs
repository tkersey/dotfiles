import assert from 'node:assert/strict';
import {mkdtempSync, rmSync, writeFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import test from 'node:test';
import {auditReviewDiscovery} from './review-discovery-audit.mjs';
import {assess, prepare, programs} from './review-action-fixture.mjs';

const hash = 'a'.repeat(64), otherHash = 'b'.repeat(64), goalHash = 'c'.repeat(64);
const here = dirname(fileURLToPath(import.meta.url));
const command = resolve(here, 'review-discovery-audit.mjs');
const witness = id => ({id, evidence_ref: `synthetic:source-witness:${id}`});
const review = (id, findings = [], changes = {}) => ({
  id, subject_id: 'subject-001', subject_sha256: hash, scope: 'changeset', focus: null, lens: 'fresh-eyes', standard_ordinal: null,
  execution: 'complete', credit: findings.length ? 'hold' : 'credit', inquiry: 'adequate',
  report_ref: `synthetic:review-observation:${id}`, findings: findings.map(witness),
  cost: {tokens: 10, execution_ms: 20}, ...changes
});
const sample = (groups = [[review('r1')]]) => ({
  evidence_kind: 'synthetic', subject: {id: 'subject-001', sha256: hash, goal_sha256: goalHash, evidence_ref: 'synthetic:subject'},
  batches: groups.map((attempts, index) => ({id: `batch-${index + 1}`, attempts})),
  audit: {subject_id: 'subject-001', subject_sha256: hash, evidence_ref: 'synthetic:independent-audit', scope: 'bounded', witnesses: []},
  episode: null
});
const addAuditWitness = (input, id, applies_to = input.batches.flatMap(batch => batch.attempts.map(item => item.id))) => {
  input.audit.witnesses.push({...witness(id), applies_to});
  return input;
};

function withDirectory(run) {
  const directory = mkdtempSync(resolve(tmpdir(), 'review-discovery-audit-'));
  try { return run(directory); }
  finally { rmSync(directory, {recursive: true, force: true}); }
}

function codecRecord(directory, program, goal) {
  const subject = resolve(directory, 'subject');
  prepare(subject, program, goal, 'none');
  const observation = assess(subject, program, goal, 'none');
  assert.equal(observation.execution, 'complete');
  const subjectId = `codec-${goal}`;
  const input = sample(Array.from({length: 5}, (_, index) => [review(`standard-${index + 1}`, [], {
    lens: 'standard', standard_ordinal: index + 1, subject_id: subjectId, subject_sha256: observation.candidate_sha256
  })]));
  input.subject.id = subjectId;
  input.subject.sha256 = observation.candidate_sha256;
  input.subject.goal_sha256 = observation.goal_sha256;
  input.audit.subject_id = subjectId;
  input.audit.subject_sha256 = observation.candidate_sha256;
  if (observation.observations.some(item => !item.pass)) addAuditWitness(input, 'timeout-contract');
  input.episode = {
    subject_id: subjectId, claim: 'complete', final_sha256: observation.candidate_sha256,
    assessment_ref: 'synthetic:actual-codec-assessment', assessment: observation,
    cost: {tokens: 100, execution_ms: 80}
  };
  return {input, observation, subject};
}

test('five synthetic clean observations can miss an independently executed real defect', () => {
  withDirectory(directory => {
    const {input, observation} = codecRecord(directory, 'original', 'distinct');
    const result = auditReviewDiscovery(input);
    assert.equal(observation.artifact_pass, false);
    assert.equal(result.evidence_kind, 'synthetic');
    assert(result.batches.every(batch => batch.new_witnesses.length === 0));
    assert.deepEqual(result.witnesses[0].missed_by, ['standard-1', 'standard-2', 'standard-3', 'standard-4', 'standard-5']);
    assert.deepEqual(result.residual.audited_unreported_witnesses, ['timeout-contract']);
    assert.equal(result.residual.credited_clean_misses.length, 5);
    assert.equal(result.episode.outcome, 'bounded_fail');
    assert.equal(result.episode.complete_claim_contradiction, true);
  });
});

for (const [program, goal, expected] of [
  ['repaired', 'distinct', 'bounded_pass'],
  ['restrictive', 'distinct', 'bounded_fail'],
  ['original', 'coalesced', 'bounded_pass'],
  ['placebo', 'distinct', 'bounded_fail']
]) test(`${program}/${goal} uses actual contract observations, not the variant label`, () => {
  withDirectory(directory => {
    const {input, observation} = codecRecord(directory, program, goal);
    const result = auditReviewDiscovery(input);
    assert.equal(result.episode.outcome, expected);
    assert.equal(result.episode.complete_claim_contradiction, expected === 'bounded_fail');
    assert.equal(result.residual.status, expected === 'bounded_fail' ? 'witnesses_present' : 'none_in_audited_scope');
    assert.equal(result.witnesses.length, observation.observations.some(item => !item.pass) ? 1 : 0);
  });
});

test('final repaired candidate and inclusive episode cost remain separate from the reviewed subject', () => {
  withDirectory(directory => {
    const {input, subject} = codecRecord(directory, 'original', 'distinct');
    writeFileSync(resolve(subject, 'codec.mjs'), programs.repaired);
    const final = assess(subject, 'original', 'distinct', 'none');
    input.episode.assessment = final;
    input.episode.final_sha256 = final.candidate_sha256;
    const result = auditReviewDiscovery(input);
    assert.notEqual(result.subject.sha256, result.episode.final_sha256);
    assert.equal(result.residual.status, 'witnesses_present');
    assert.equal(result.episode.outcome, 'bounded_pass');
    assert.deepEqual(result.review_cost.tokens, {measured_subtotal: 50, unknown_count: 0});
    assert.deepEqual(result.episode.cost.tokens, {measured_subtotal: 100, unknown_count: 0});
    assert.deepEqual(result.review_cost.execution_ms, {measured_subtotal: 100, unknown_count: 0});
    assert.deepEqual(result.episode.cost.execution_ms, {measured_subtotal: 80, unknown_count: 0});
  });
});

test('parallel batches have invariant union discovery and no invented within-batch ordering', () => {
  const input = addAuditWitness(sample([
    [review('r2', ['A'], {scope: 'file', focus: 'codec.mjs'}), review('r1', ['A'])],
    [review('r3', ['B'], {lens: 'standard', standard_ordinal: 1})],
    [review('r4', ['A'], {lens: 'standard', standard_ordinal: 2})]
  ]), 'C');
  const result = auditReviewDiscovery(input);
  const permuted = structuredClone(input);
  permuted.batches[0].attempts.reverse();
  assert.deepEqual(auditReviewDiscovery(permuted), result);
  assert.deepEqual(result.batches[0].new_witnesses, ['A']);
  assert.deepEqual(result.batches[0].attempts.map(item => item.new_to_prior_batches), [['A'], ['A']]);
  assert.deepEqual(result.batches[1].new_witnesses, ['B']);
  assert.deepEqual(result.batches[2].new_witnesses, []);
  assert.deepEqual(result.batches[2].repeated_witnesses, ['A']);
  assert.equal(result.batches[2].attempts[0].outcome, 'findings');
  assert.equal(result.batches[2].attempts[0].credited_clean, false);
  assert.deepEqual(result.batches[2].cumulative_witnesses, ['A', 'B']);
  assert.deepEqual(result.witnesses.find(item => item.id === 'C').missed_by, ['r1', 'r2', 'r3', 'r4']);
});

test('adequate held positive review may miss another applicable witness independently of credit', () => {
  const input = addAuditWitness(sample([[review('r1', ['A'])]]), 'B');
  const result = auditReviewDiscovery(input);
  assert.deepEqual(result.witnesses.find(item => item.id === 'B').missed_by, ['r1']);
  assert.deepEqual(result.residual.credited_clean_misses, []);
  input.batches[0].attempts[0].inquiry = 'unknown';
  const unknown = auditReviewDiscovery(input);
  assert.deepEqual(unknown.witnesses.find(item => item.id === 'A').detected_by, ['r1']);
  assert.deepEqual(unknown.witnesses.find(item => item.id === 'B').missed_by, []);
  assert.deepEqual(unknown.witnesses.find(item => item.id === 'B').unresolved_by, ['r1']);
});

test('exclusive batch contributions preserve overlaps without completion-order attribution', () => {
  const input = sample([[review('r1', ['A', 'B']), review('r2', ['A', 'C']), review('r3', ['A'])]]);
  const result = auditReviewDiscovery(input);
  assert.deepEqual(result.batches[0].new_witnesses, ['A', 'B', 'C']);
  assert.deepEqual(result.batches[0].attempts.map(item => item.exclusive_in_batch), [['B'], ['C'], []]);
  input.batches[0].attempts.reverse();
  assert.deepEqual(auditReviewDiscovery(input), result);
});

test('partial inquiry keeps valid discoveries and missing evidence unresolved', () => {
  const input = addAuditWitness(sample([[
    review('r1', ['A'], {execution: 'incomplete', inquiry: 'incomplete'}),
    review('r2', [], {credit: 'hold', inquiry: 'unknown'}),
    review('r3', [], {scope: 'file', focus: 'unrelated.mjs'})
  ]]), 'B', ['r1', 'r2']);
  const result = auditReviewDiscovery(input);
  assert.deepEqual(result.witnesses.find(item => item.id === 'A').detected_by, ['r1']);
  assert.deepEqual(result.witnesses.find(item => item.id === 'B').missed_by, []);
  assert.deepEqual(result.witnesses.find(item => item.id === 'B').unresolved_by, ['r1', 'r2', 'r3']);
  assert.deepEqual(result.residual.credited_clean_misses, []);
});

test('missing or unknown audit scope cannot establish an empty residual', () => {
  const input = sample();
  input.audit.scope = 'unknown';
  assert.equal(auditReviewDiscovery(input).residual.status, 'unknown');
  input.audit = null;
  assert.equal(auditReviewDiscovery(input).residual.status, 'unknown');
  input.batches[0].attempts[0] = review('r1', ['A']);
  assert.equal(auditReviewDiscovery(input).residual.status, 'witnesses_present');
  assert.deepEqual(auditReviewDiscovery(input).witnesses[0].missed_by, []);
});

test('unknown costs retain measured subtotals and unknown counts', () => {
  const input = sample([[review('r1'), review('r2', [], {cost: null}),
    review('r3', [], {cost: {tokens: 5, execution_ms: null}})]]);
  assert.deepEqual(auditReviewDiscovery(input).review_cost, {
    tokens: {measured_subtotal: 15, unknown_count: 1},
    execution_ms: {measured_subtotal: 20, unknown_count: 2}
  });
});

test('unavailable actual final execution leaves the complete claim unresolved', () => {
  withDirectory(directory => {
    const {input, subject} = codecRecord(directory, 'original', 'distinct');
    writeFileSync(resolve(subject, 'codec.mjs'), 'export function {\n');
    const final = assess(subject, 'original', 'distinct', 'none');
    assert.equal(final.execution, 'unavailable');
    input.episode.assessment = final;
    input.episode.final_sha256 = final.candidate_sha256;
    input.episode.cost = null;
    const result = auditReviewDiscovery(input);
    assert.equal(result.episode.outcome, 'unavailable');
    assert.equal(result.episode.complete_claim_contradiction, 'unknown');
    assert.deepEqual(result.episode.cost.tokens, {measured_subtotal: 0, unknown_count: 1});
    input.episode.claim = 'incomplete';
    assert.equal(auditReviewDiscovery(input).episode.complete_claim_contradiction, false);
  });
});

test('actual self-modifying candidate cannot bind a bounded failure or pass to the final subject', () => {
  withDirectory(directory => {
    const {input, subject} = codecRecord(directory, 'original', 'distinct');
    writeFileSync(resolve(subject, 'codec.mjs'), `import {writeFileSync} from 'node:fs';
writeFileSync(new URL(import.meta.url), ${JSON.stringify(programs.original)});
${programs.repaired}`);
    const final = assess(subject, 'original', 'distinct', 'none');
    assert.equal(final.execution, 'complete');
    assert.equal(final.candidate_stable, false);
    assert(final.observations.every(item => item.pass));
    assert.equal(final.artifact_pass, false);
    input.episode.assessment = final;
    input.episode.final_sha256 = final.candidate_sha256;
    const result = auditReviewDiscovery(input);
    assert.equal(result.episode.outcome, 'unavailable');
    assert.equal(result.episode.complete_claim_contradiction, 'unknown');
  });
});

for (const [name, change, expected] of [
  ['missing Goal binding', assessment => { delete assessment.goal_sha256; }, /goal_sha256/],
  ['missing stability', assessment => { delete assessment.candidate_stable; }, /candidate_stable/],
  ['unstable pass', assessment => { assessment.candidate_stable = false; }, /pass contradicts/],
  ['unavailable pass', assessment => { assessment.execution = 'unavailable'; }, /pass contradicts/],
  ['missing observation set', assessment => { delete assessment.observations; }, /observations/],
  ['empty completed observation set', assessment => { assessment.observations = []; }, /no observations/],
  ['failing observation in a pass', assessment => { assessment.observations[0].pass = false; }, /pass contradicts/],
  ['protected input changed in a pass', assessment => { assessment.protected_changes = ['GOAL.md']; }, /pass contradicts/]
]) test(`${name} cannot be presented as a bounded pass`, () => {
  withDirectory(directory => {
    const {input} = codecRecord(directory, 'repaired', 'distinct');
    change(input.episode.assessment);
    assert.throws(() => auditReviewDiscovery(input), expected);
  });
});

test('a false aggregate flag cannot manufacture a contradicted completion from passing observations', () => {
  withDirectory(directory => {
    const {input} = codecRecord(directory, 'repaired', 'distinct');
    input.episode.assessment.artifact_pass = false;
    assert.throws(() => auditReviewDiscovery(input), /artifact_pass contradicts/);
  });
});

for (const [name, change, issue] of [
  ['incomplete inquiry', entry => { entry.inquiry = 'incomplete'; }, 'inquiry_incomplete'],
  ['unknown inquiry', entry => { entry.inquiry = 'unknown'; }, 'inquiry_unknown'],
  ['incomplete execution', entry => { entry.execution = 'incomplete'; }, 'execution_incomplete'],
  ['admitted finding', entry => { entry.findings = [witness('A')]; }, 'reported_findings']
]) test(`observed credit with ${name} retains the original failed process outcome`, () => {
  const input = addAuditWitness(sample(), 'B');
  input.evidence_kind = 'observed';
  change(input.batches[0].attempts[0]);
  const result = auditReviewDiscovery(input);
  const attempt = result.batches[0].attempts[0];
  assert.equal(attempt.credit, 'credit');
  assert.deepEqual(attempt.credit_issues, [issue]);
  assert.equal(attempt.credited_clean, false);
  assert.equal(result.batches[0].attempts.length, 1);
  assert.deepEqual(result.review_cost.tokens, {measured_subtotal: 10, unknown_count: 0});
  assert.deepEqual(result.residual.credited_clean_misses, []);
  const missed = result.witnesses.find(item => item.id === 'B');
  assert.deepEqual(missed.unresolved_by, name === 'admitted finding' ? [] : ['r1']);
  assert.deepEqual(missed.missed_by, name === 'admitted finding' ? ['r1'] : []);
  if (name === 'admitted finding') assert.deepEqual(result.witnesses.find(item => item.id === 'A').detected_by, ['r1']);
});

for (const [name, change, expected] of [
  ['duplicate attempt', input => input.batches.push({id: 'b2', attempts: [review('r1')]}), /Duplicate attempt identity/],
  ['duplicate batch', input => input.batches.push({id: 'batch-1', attempts: [review('r2')]}), /Duplicate batch identity/],
  ['mixed reviewed candidate', input => { input.batches[0].attempts[0].subject_sha256 = otherHash; }, /does not match/],
  ['mixed reviewed authority', input => { input.batches[0].attempts[0].subject_id = 'another-subject'; }, /subject_id does not match/],
  ['stale independent audit', input => { input.audit.subject_sha256 = otherHash; }, /does not match/],
  ['missing provenance kind', input => { delete input.evidence_kind; }, /evidence_kind/],
  ['missing report evidence', input => { delete input.batches[0].attempts[0].report_ref; }, /report_ref/],
  ['missing witness evidence', input => { input.audit.witnesses = [{id: 'A', applies_to: ['r1']}]; }, /evidence_ref/],
  ['unknown applicable request', input => addAuditWitness(input, 'A', ['missing']), /Unknown applicable attempt/],
  ['duplicate finding', input => { input.batches[0].attempts[0] = review('r1', ['A', 'A']); }, /Duplicate .*witness/],
  ['nonstandard ordinal', input => { input.batches[0].attempts[0].standard_ordinal = 1; }, /outside changeset standard/],
  ['missing changeset standard ordinal', input => { input.batches[0].attempts[0].lens = 'standard'; }, /must be positive/],
  ['file scope without focus', input => { input.batches[0].attempts[0].scope = 'file'; }, /focus/],
  ['negative cost', input => { input.batches[0].attempts[0].cost.tokens = -1; }, /nonnegative/]
]) test(`${name} is rejected rather than becoming a negative observation`, () => {
  const input = sample();
  change(input);
  assert.throws(() => auditReviewDiscovery(input), expected);
});

test('changeset standard ordinals must identify distinct requests', () => {
  const input = sample([[review('r1', [], {lens: 'standard', standard_ordinal: 1})],
    [review('r2', [], {lens: 'standard', standard_ordinal: 1})]]);
  assert.throws(() => auditReviewDiscovery(input), /Duplicate changeset standard ordinal/);
});

test('stale final assessment cannot describe the final candidate', () => {
  withDirectory(directory => {
    const {input} = codecRecord(directory, 'repaired', 'distinct');
    input.episode.final_sha256 = otherHash;
    assert.throws(() => auditReviewDiscovery(input), /episode.assessment.candidate_sha256 does not match/);
  });
});

test('identical candidate bytes under different Goals cannot share an audit or episode authority', () => {
  withDirectory(first => withDirectory(second => {
    const a = codecRecord(first, 'original', 'distinct');
    const b = codecRecord(second, 'original', 'coalesced');
    assert.equal(a.input.subject.sha256, b.input.subject.sha256);
    assert.notEqual(a.observation.goal_sha256, b.observation.goal_sha256);
    assert.notEqual(a.observation.artifact_pass, b.observation.artifact_pass);
    const wrongAudit = structuredClone(a.input);
    wrongAudit.audit = b.input.audit;
    assert.throws(() => auditReviewDiscovery(wrongAudit), /audit.subject_id does not match/);
    const wrongEpisode = structuredClone(a.input);
    wrongEpisode.episode = b.input.episode;
    assert.throws(() => auditReviewDiscovery(wrongEpisode), /episode.subject_id does not match/);
    const wrongAssessment = structuredClone(a.input);
    wrongAssessment.episode.assessment = b.observation;
    assert.throws(() => auditReviewDiscovery(wrongAssessment), /episode.assessment.goal_sha256 does not match/);
  }));
});

test('observed designation is retained but does not authenticate supplied evidence', () => {
  const input = sample();
  input.evidence_kind = 'observed';
  assert.equal(auditReviewDiscovery(input).evidence_kind, 'observed');
  assert.equal(input.batches[0].attempts[0].report_ref, 'synthetic:review-observation:r1');
});

test('CLI reports descriptive failures successfully and rejects invalid inputs or invocation', () => {
  withDirectory(directory => {
    const {input} = codecRecord(directory, 'original', 'distinct');
    const file = resolve(directory, 'input.json');
    writeFileSync(file, JSON.stringify(input));
    const invoke = (...args) => spawnSync(process.execPath, [command, ...args], {encoding: 'utf8'});
    const result = invoke(file);
    assert.equal(result.status, 0, result.stderr);
    assert.deepEqual(JSON.parse(result.stdout), auditReviewDiscovery(input));
    assert.equal(JSON.parse(result.stdout).episode.outcome, 'bounded_fail');
    delete input.evidence_kind;
    writeFileSync(file, JSON.stringify(input));
    assert.equal(invoke(file).status, 2);
    writeFileSync(file, '{');
    assert.equal(invoke(file).status, 2);
    assert.equal(invoke().status, 2);
    assert.equal(invoke(file, file).status, 2);
    assert.equal(invoke(resolve(directory, 'missing.json')).status, 2);
  });
});

test('the helper leaves supplied evaluator records unchanged', () => {
  const input = addAuditWitness(sample(), 'A');
  const original = structuredClone(input);
  auditReviewDiscovery(input);
  assert.deepEqual(input, original);
});
