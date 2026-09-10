#!/usr/bin/env node
// Offline fixture probes and source-contract checks, NOT a semantic judge or
// agent-efficacy test. --case exports evidence without the evaluator's answer.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';

const cases = [];
function add(id, pair, goal, finding, source, probe, observation, disposition, reason, extra = {}) {
  cases.push({id, pair, input: {
    subject: `synthetic fixture ${id}; current candidate shown below`,
    goal, proposed_finding: finding, candidate_source: source,
    proposed_probe: probe, ...extra
  }, observation, disposition, reason});
}

const validationGoal = 'Both public entry points submit and recover must reject quantities that are not nonnegative safe integers before any write. Hostile input is covered; nonnegative safe integers must still work.';
const validationFinding = 'recover(-1) bypasses validation and persists a negative quantity.';
const validationCore = `const stored = [];
function submit(n) {
  if (!Number.isSafeInteger(n) || n < 0) return 'rejected';
  stored.push(n); return 'accepted';
}
`;
const validationProbe = `({status: recover(-1), stored})`;
add('case-01', 'admission-path', validationGoal, validationFinding,
  validationCore + 'function recover(n) { return submit(n); }', validationProbe,
  {status:'rejected', stored:[]}, 'rejected', 'The only recovery path delegates to submit; the cited witness is rejected before writing.');
add('case-02', 'admission-path', validationGoal, validationFinding,
  validationCore + "function recover(n) { stored.push(n); return 'accepted'; }", validationProbe,
  {status:'accepted', stored:[-1]}, 'accepted', 'The supported untrusted boundary bypasses the required validation. Invalid input is not an exemption.');

const aliasGoal = 'admit must snapshot valid caller bounds. Later writes to the original input must not change the admitted bounds or their correlated length.';
const aliasFinding = 'After admission, mutating the original bounds makes the admitted length inconsistent.';
const aliasSource = expression => `function admit(raw) {
  const bounds = ${expression};
  return {bounds, length: bounds.end - bounds.start};
}`;
const aliasProbe = `(() => {
  const raw = {bounds:{start:1,end:3}}, value = admit(raw);
  raw.bounds.end = 4;
  return {start:value.bounds.start, end:value.bounds.end, length:value.length};
})()`;
add('case-03', 'alias', aliasGoal, aliasFinding, aliasSource('{...raw.bounds}'), aliasProbe,
  {start:1,end:3,length:2}, 'rejected', 'The input alias does not reach the owned snapshot; the allegation is refuted, not an invitation to add another guard.');
add('case-04', 'alias', aliasGoal, aliasFinding, aliasSource('raw.bounds'), aliasProbe,
  {start:1,end:4,length:2}, 'accepted', 'The actual external alias permits the claimed valid-state-to-invalid transition.');

const duplicateSource = 'const rows = []; function submit(id) { rows.push(id); }';
const duplicateProbe = "(() => { submit('x'); submit('x'); return rows.length; })()";
const duplicateFinding = 'Two submissions with the same ID persist two rows, violating uniqueness. Add a shared cache.';
add('case-05', 'authority', 'Record every submission independently. IDs are correlation labels, not uniqueness keys; two same-ID submissions must produce two records.',
  duplicateFinding, duplicateSource, duplicateProbe, 2, 'rejected', 'The observation is true but the alleged uniqueness law contradicts the accepted contract.');
add('case-06', 'authority', 'Repeated submissions with the same ID denote one operation and must persist at most one record.',
  duplicateFinding, duplicateSource, duplicateProbe, 2, 'accepted', 'The accepted at-most-one obligation is violated; the suggested cache is not thereby validated.');

const proofFinding = 'The migration verification result is missing. Treat this as a completion blocker.';
// This fixture is an explicit, complete provider observation, not a candidate's
// self-authored proof inventory. Both variants expose the identical evidence.
const proofSource = "const provider = {subject:'current', inventoryComplete:true, passed:['unit']};";
const proofProbe = "({complete:provider.inventoryComplete, migration:provider.passed.includes('migration')})";
const proofEvidence = {source_owner:'Fixture provider: this is its complete current verification inventory.'};
add('case-07', 'proof-authority', 'Unit verification is mandatory. Migration verification is a useful optional follow-up and is not required for completion.',
  proofFinding, proofSource, proofProbe, {complete:true,migration:false}, 'follow-up', 'Optional missing evidence does not become a mandatory gate or a runtime bug.', proofEvidence);
add('case-08', 'proof-authority', 'Completion requires both unit and migration verification on the current subject, according to the provider inventory.',
  proofFinding, proofSource, proofProbe, {complete:true,migration:false}, 'accepted', 'The exact mandatory verification obligation is unsatisfied, without claiming a runtime violation.', proofEvidence);

const totalSource = 'function total(a,b) { return a-b; }';
const totalFinding = 'total(2,3) returns -1 rather than 5; this must be fixed in the current task.';
const unchanged = {base_source:totalSource, change:'Only usage documentation changed; execution paths and exposure are unchanged.'};
add('case-09', 'goal-scope', 'Correct a usage-documentation typo only. The unrelated legacy total implementation and its behavior are outside this task.',
  totalFinding, totalSource, 'total(2,3)', -1, 'rejected', 'The defect is real but neither caused/exposed by this delta nor within the accepted Goal.', unchanged);
add('case-10', 'goal-scope', 'Deliver correct current arithmetic totals, including legacy code: total(a,b) must return a+b. The obligation is Goal-wide, not restricted to the diff.',
  totalFinding, totalSource, 'total(2,3)', -1, 'accepted', 'A pre-existing defect in an unchanged file still violates the current Goal.', unchanged);

const staleFinding = 'The prior review reported that total(2,3) returns -1, violating the sum contract.';
const prior = {prior_owner_evidence:{subject:'prior candidate, not current', source:totalSource, observed:-1}};
add('case-11', 'current-subject', 'The current total function must return a+b.', staleFinding,
  'function total(a,b) { return a+b; }', 'total(2,3)', 5, 'rejected', 'The original report remains historical evidence, but this witness is already excluded on the current candidate.', prior);
add('case-12', 'current-subject', 'The current total function must return a+b.', staleFinding,
  totalSource, 'total(2,3)', -1, 'accepted', 'Re-evaluation of the actual current candidate supports the same witness; history alone was not the authority.', prior);

add('case-13', 'unknown', 'Adjudicate whether the current retry handler enforces at-most-one external effect per ID.',
  'Concurrent retries necessarily cause duplicate effects because reserve is non-atomic.',
  'async function handle(id, store, effect) { if (await store.reserve(id)) await effect(id); }',
  null, null, 'blocked', 'The store contract and implementation are unavailable. The decisive atomicity premise is unknown; block the dependent adjudication, not assert a bug or an exoneration.',
  {unavailable_evidence:['store.reserve implementation and atomicity contract'], scope:'No other mutation or completion decision is requested.'});

add('case-14', 'narrowing', 'Both public entry points must reject negative quantities before writing.',
  'Both submit and recover admit negative quantities; all validation is missing.',
  validationCore + "function recover(n) { stored.push(n); return 'accepted'; }",
  '({submit:submit(-1), recover:recover(-1), stored})',
  {submit:'rejected',recover:'accepted',stored:[-1]}, 'accepted', 'Accept only the recovery bypass. Reject the submit allegation and preserve the original broader report; one true consequence cannot validate its sibling.');

// Executable test failures do not make their expectations authoritative.
const failedCheck = totalSource + `
function check() {
  const actual = total(2,3), expected = 5;
  return {status:actual === expected ? 'passed' : 'failed', actual, expected};
}`;
const failedFinding = 'The failed assertion proves total must be changed to return 5.';
for (const [id,goal,disposition,reason] of [
  ['case-15','total(a,b) must add its arguments; valid verification is mandatory.','accepted','The failed execution demonstrates a product defect under the accepted sum law.'],
  ['case-16','total(a,b) must subtract b from a; valid verification is mandatory.','rejected','The production diagnosis is refuted by the difference law. Correct the expectation and obtain valid verification; the original run remains failed, not a pass.']
]) add(id,'failed-expectation',goal,failedFinding,failedCheck,'check()',
  {status:'failed',actual:-1,expected:5},disposition,reason);

add('case-17','oracle','Production and the independent oracle must release resources in reverse acquisition order. Both acquire 1 then 2; verification is mandatory.',
  'The differential failure means production must use the oracle order.',
  'function production(){return [2,1];} function oracle(){return [1,2];}',
  '({actual:production(), expected:oracle()})',{actual:[2,1],expected:[1,2]},'accepted',
  'Accept the oracle defect, not the proposed production change. The required order is independently specified; repair the checker and obtain fresh evidence.');
add('case-18','setup','Completion requires running the current sum check in the supported environment.',
  'The test failed, so the sum implementation must be wrong.',
  'function total(a,b){return a+b;}',null,null,'blocked',
  'No sum assertion executed. Product failure is unestablished; the missing required verification blocks dependent completion, not unrelated work.',
  {owner_output:{status:'setup-failed',error:'cache PermissionDenied',assertions_executed:0}});
add('case-19','incidental','doubled(n) must return n+n. Internal helper selection is unrestricted; behavioral verification remains required.',
  'The helper-call assertion failed, so restore the old helper call.',
  'let helperCalls=0; function oldHelper(n){helperCalls++;return n+n;} function doubled(n){return n+n;}',
  '({actual:doubled(3), helperCalls, expectedHelperCalls:1})',
  {actual:6,helperCalls:0,expectedHelperCalls:1},'rejected',
  'The assertion enforces an incidental mechanism. It may be retired or replaced without restoring that mechanism, but required behavior still needs verification.');
add('case-20','retry','Each independent invocation must emit exactly one effect; both normal and recovery paths are supported.',
  'The first test emitted twice; a fresh retry passed, so ignore the earlier failure.',
  'function emit(recovery){const trace=[];trace.push(1);if(recovery)trace.push(1);return trace.length;}',
  '({first:emit(true), retry:emit(false)})',{first:2,retry:1},'accepted',
  'The recovery path violates the accepted law. A passing independent normal run does not erase that witness or establish flakiness.');

const task = 'Using Review Fold, adjudicate the proposed finding from the supplied source and accepted Goal. Return the supported claim, existing disposition, decisive evidence/countercase, and any unresolved premise. Do not implement a fix, invent unseen code, or manufacture a rejection quota.';
function exported(c) { return {task, ...c.input}; }
const args = process.argv.slice(2);
if (args.length === 1 && args[0] === '--list') {
  console.log(cases.map(c => c.id).join('\n'));
} else if (args.length === 2 && args[0] === '--case') {
  const c = cases.find(c => c.id === args[1]);
  if (!c) { console.error('unknown case'); process.exitCode = 2; }
  else console.log(JSON.stringify(exported(c), null, 2));
} else if (args.length === 1 && args[0] === '--key') {
  console.log(JSON.stringify(cases.map(({id,pair,disposition,reason}) => ({id,pair,disposition,reason})), null, 2));
} else if (args.length) {
  console.error('usage: node test-counterexample-admission.mjs [--list | --case case-NN | --key]');
  process.exitCode = 2;
} else {
  assert.equal(new Set(cases.map(c => c.id)).size, cases.length);
  let probes = 0;
  for (const c of cases) {
    assert(c.input.goal && c.input.proposed_finding && c.reason, c.id);
    assert(['accepted','rejected','follow-up','blocked'].includes(c.disposition), c.id);
    for (const key of ['disposition','observation','reason','pair']) assert(!Object.hasOwn(exported(c),key));
    if (c.input.proposed_probe !== null) {
      // Execute only the checked-in synthetic program/probe, with no host I/O.
      // VM isolation here is fixture hygiene, not a sandbox for untrusted code.
      const actual = JSON.parse(runInNewContext(
        `${c.input.candidate_source}\nJSON.stringify(${c.input.proposed_probe})`,
        Object.create(null), {timeout:1000}));
      assert.deepEqual(actual, c.observation, c.id);
      probes++;
    } else assert.equal(c.observation, null, 'do not manufacture an observation for missing evidence');
  }
  for (const pair of ['admission-path','alias','authority','proof-authority','goal-scope','current-subject','failed-expectation']) {
    const [a,b,...rest] = cases.filter(c => c.pair === pair);
    assert(a && b && !rest.length, pair);
    assert.equal(a.input.proposed_finding, b.input.proposed_finding, pair);
    assert.notEqual(a.disposition, b.disposition, pair);
    assert(a.input.goal !== b.input.goal || a.input.candidate_source !== b.input.candidate_source, pair);
  }
  // Synthetic return semantics: protection preserves a future return obligation;
  // cleanup completion resumes an already-checked exit. Not a Boundary replay.
  const destination = valid => ({kind:'destination',valid});
  const protection = parent => ({kind:'protection',parent});
  const cleanup = {kind:'cleanup-completion',checkedExit:true};
  const firstRepair = f => f.kind === 'destination' ? f.valid : true;
  const model = f => f.kind === 'destination' ? f.valid :
    f.kind === 'protection' ? model(f.parent) : f.checkedExit;
  const frames = [destination(false), protection(destination(false)),
    protection(destination(true)), cleanup];
  const required = [false,false,true,true];
  for (const entry of ['live','saved']) {
    assert.deepEqual(frames.map(model),required,entry + ': corrected model and full participation');
    assert.notDeepEqual(frames.map(firstRepair),required,entry + ': broader application cannot fix wrong meaning');
  }
  assert.notDeepEqual(frames.map(() => true),required,'correct model omitted at saved entry');
  assert.notDeepEqual(frames.map(() => false),required,'reject-all violates required-valid behavior');
  const affine = {copyable:false,dropAllowed:true}, reusable = {copyable:true,dropAllowed:true};
  assert.equal(affine.dropAllowed,reusable.dropAllowed,'incumbent proxy merges these cases');
  assert.notEqual(!affine.copyable,!reusable.copyable,'ownership requires the missing distinction');

  // These checks bind the fixture suite to the declared admission handoff;
  // they do not demonstrate that a model follows or benefits from the policy.
  const read = path => readFileSync(new URL(path, import.meta.url),'utf8');
  const fold = read('../SKILL.md');
  const admission = fold.split('## Counterexample admission\n')[1]?.split('\n## ')[0];
  assert(admission, 'missing admission standard');
  for (const heading of ['**Obligation.**','**Validity.**','**Relevance.**','**Countercase.**'])
    assert(admission.includes(heading), heading);
  assert(!fold.includes('Assign disposition from authority plus current applicability'));
  assert.match(fold,/that passed Counterexample admission/);
  assert.match(fold,/reported_claim:[\s\S]*observed_fact: # established only/);
  assert.match(read('../references/counterexample-corpus.md'),/Counterexample admission established validity and current Goal relevance/);
  assert.match(read('../../actuating/SKILL.md'),/review-fold\/SKILL\.md#counterexample-admission/);
  assert.match(read('../agents/openai.yaml'),/Apply Counterexample admission to each proposed witness/);
  const normalized = admission.replace(/\s+/g,' ');
  for (const rule of [
    'failed assertions, differential mismatches, and verification failures use the same admission decision',
    "inspect the expectation's source authority, fixture preconditions",
    'Rejecting its diagnosis does not create a pass or waive mandatory verification',
    'Never change expected results merely to agree with the candidate',
    'A later passing retry does not erase an unexplained failure'
  ]) assert(normalized.includes(rule),rule);
  console.log(`review-fold: ${probes} concrete fixture probes, ${cases.length} evaluation cases, seven discriminating pairs, model/coverage/preservation probes, and admission handoff checks passed; no model evaluation run`);
}
