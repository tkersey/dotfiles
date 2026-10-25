#!/usr/bin/env node
// Offline owner-adjudication replays. This is not Actuating's runtime or an agent judge.
// --case supplies current workflow guidance and evidence, never the evaluator key.
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {mkdtempSync, readFileSync, writeFileSync, rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {fileURLToPath} from 'node:url';

function fixtureObservations() {
  const dir = mkdtempSync(join(tmpdir(), 'actuating-credit-'));
  try {
    const path = join(dir, 'generated.json');
    const source = `const fs = require('node:fs');
try {
  const value = JSON.parse(fs.readFileSync(process.argv[1], 'utf8'));
  if (value.actual !== value.expected) throw Error('assertion failed');
  console.log(JSON.stringify({passed:1, skipped:0}));
} catch (error) { console.error(error.code || error.message); process.exitCode = 1; }`;
    const run = () => spawnSync(process.execPath, ['-e', source, path], {encoding:'utf8'});
    const missing = run();
    assert.equal(missing.status, 1, missing.stderr);
    assert.equal(missing.stderr.trim(), 'ENOENT');
    writeFileSync(path, JSON.stringify({actual:'ok', expected:'ok'}));
    const recovered = run();
    assert.equal(recovered.status, 0, recovered.stderr);
    assert.deepEqual(JSON.parse(recovered.stdout), {passed:1, skipped:0});
    const skipped = spawnSync(process.execPath, ['-e',
      'console.log(JSON.stringify({passed:0, skipped:1}))'], {encoding:'utf8'});
    assert.equal(skipped.status, 0, skipped.stderr);
    return {
      missing:{exit:missing.status, error:missing.stderr.trim()},
      recovered:{exit:recovered.status, ...JSON.parse(recovered.stdout)},
      skipped:{exit:skipped.status, ...JSON.parse(skipped.stdout)}
    };
  } finally { rmSync(dir, {recursive:true, force:true}); }
}
const observations = fixtureObservations();
const receipt = {
  status:'clean', clean:true, findingCount:0, failureCode:null,
  native_result:{findings:[], overall_correctness:'patch is correct',
    overall_confidence_score:0.53,
    overall_explanation:'No actionable defects were established in the inspected paths. The ReleaseSafe check was blocked by sandbox permission errors; cross-repository runtime integration was not verified.'}
};
const fixtureReceipt = {...receipt, native_result:{...receipt.native_result,
  overall_explanation:'No actionable defects in inspected code. Generated fixture execution was unavailable (ENOENT).'}};
const subject = {head:'h1', base:'b1', inputs:'i1', environment:'e1'};
const prior = {ref:'proof-1', ...subject, command:'zig build check',
  mode:'ReleaseSafe', result:'passed', provenance:'synthetic verifier observation'};
const cases = [];
function add(id, evidence, decision, basis) {
  cases.push({id, input:{
    subject, lens:'fresh-eyes',
    authenticated_current_receipt:true, receipt,
    prior_credit:{standard:5, auxiliary:4},
    requested_scope:'Independent end-to-end inspection. All pre-review proof obligations were satisfied; relevance of the newly blocked reviewer check has not been adjudicated.',
    other_required_obligations:'Complete and unchanged. Only this review remains.',
    ...evidence
  }, expected:{credit_disposition:'hold', limitation_disposition:'unresolved',
    standard_count_after:5, auxiliary_count_after:4,
    public_review_complete:false, original_check_status:'blocked', ...decision}, basis});
}
add('credit-01', {}, {},
  'Authenticity and no findings do not resolve the disclosed evidence gap; do not complete the final auxiliary or publish all clean.');
add('credit-02', {requested_scope:'Static API/documentation review only. The accepted task explicitly excludes runtime validation; all required static paths were inspected. ReleaseSafe was an exploratory attempt, not necessary to the static conclusion.'},
  {credit_disposition:'credit', limitation_disposition:'not-required', auxiliary_count_after:5, public_review_complete:true},
  'Allow the supported static obligation without requiring another test; retain the blocked execution and scoped public wording.');
add('credit-03', {requested_scope:'Independent source inspection plus ReleaseSafe validation. The reviewer completed its source reasoning and inspected proof-1 before its redundant local execution failed.', prior_evidence:[prior]},
  {credit_disposition:'credit', limitation_disposition:'covered', auxiliary_count_after:5, public_review_complete:true},
  'Exact current evidence covers validation and the reviewer used it. Do not relabel the blocked attempt or claim additional independent execution.');
add('credit-04', {requested_scope:'Independent source inspection plus ReleaseSafe validation. Inspection is complete; exact ReleaseSafe execution evidence is required.', prior_evidence:[{...prior, mode:null}]}, {},
  'A generic passing check with unspecified optimization flags cannot establish ReleaseSafe equivalence.');
add('credit-05', {requested_scope:'Review the generated fixture behavior. The reviewer says it cannot finish its reasoning without the generated fixture.',
  receipt:fixtureReceipt, reviewer_execution:observations.missing, parent_execution:observations.recovered,
  recovery_scope:'Same candidate and authorized generated fixture; no code, input contract, or review binding changed.'}, {},
  'Parent validation passed, but missing reviewer reasoning remains. Preserve both observations and do not award a reviewer confirmation.');
add('credit-06', {requested_scope:'Review the generated fixture behavior. The reviewer initially could not finish without it.',
  receipt:fixtureReceipt, reviewer_execution:observations.missing, parent_execution:observations.recovered,
  recovery_scope:'Same candidate and authorized generated fixture; no code, input contract, or review binding changed.',
  reviewer_followup:'The same bound reviewer inspected the recovered fixture and result, completed the dependent reasoning, and reported no findings.'},
  {credit_disposition:'credit', limitation_disposition:'recovered', auxiliary_count_after:5, public_review_complete:true},
  'Recover this obligation once; the parent test and reviewer continuation are not additional review credits.');
add('credit-07', {requested_scope:'The review must inspect the accepted migration contract.',
  accessible_evidence:{workflow_digest:'exact-matching-digest', migration_contract:null},
  reviewer_note:'The required migration contract is inaccessible; its digest is available.'}, {},
  'Matching identity is not delivery of a required premise.');
add('credit-08', {requested_scope:'Execute the fixture check; source inspection is already complete.',
  receipt:{...receipt, native_result:{...receipt.native_result,
    overall_explanation:'No defects found; the command exited zero but its only test was skipped.'}},
  reviewer_execution:observations.skipped}, {original_check_status:'skipped'},
  'Exit zero with zero executed tests does not discharge a required execution check.');
add('credit-09', {receipt:{...receipt, native_result:{...receipt.native_result,
    overall_explanation:'No actionable findings.'}}, historical_handoff:null,
  coverage_evidence:'The old receipt has no scope/adequacy evidence beyond its labels.'},
  {original_check_status:'unknown'},
  'An old receipt with unknown required coverage gets no implicit credit.');
add('credit-10', {lens:'standard', prior_credit:{standard:4, auxiliary:5}},
  {standard_count_after:4, auxiliary_count_after:5},
  'Hold the fifth standard, pause further standard confirmations, and preserve the four valid standards and five auxiliaries.');
add('credit-11', {requested_scope:'Static API/documentation review only; all required paths were inspected. Runtime execution is explicitly out of scope.',
  receipt:{...receipt, native_result:{...receipt.native_result,
    overall_explanation:'No actionable findings in the required static paths. Runtime execution was not requested or attempted.'}}},
  {credit_disposition:'credit', limitation_disposition:'not-required', auxiliary_count_after:5,
    public_review_complete:true, original_check_status:'not-run'},
  'A justified omitted optional check is not a universal blocker.');
add('credit-12', {receipt:{...receipt, status:'findings', clean:false, findingCount:1,
    native_result:{...receipt.native_result, findings:[{title:'Accepted current material counterexample', body:'Fixture violation admitted by Review Fold.',
      confidence_score:1, priority:1, code_location:{absolute_file_path:'/fixture/src/check.mjs', line_range:{start:1,end:1}}}],
      overall_correctness:'patch is incorrect'}},
  review_fold:'The current material counterexample is entailed, accepted, and unresolved.'},
  {limitation_disposition:null, standard_count_after:0, auxiliary_count_after:0},
  'The existing material-finding reset still applies; a hold is not an exemption from invalidation.');
add('credit-13', {requested_scope:'The accepted pre-review proof inventory required migration validation.',
  pre_review_proof:'The migration check was never run. This is newly discovered missing required candidate proof, not merely a reviewer access limitation.'},
  {standard_count_after:0, auxiliary_count_after:0},
  'Invalidate prior reviewability/credit under the existing missing-proof rule; do not treat this as an ordinary review-only hold.');
add('credit-14', {requested_scope:'Independent inspection plus exact-head ReleaseSafe validation.',
  prior_evidence:[{...prior, head:'h0'}]}, {},
  'A stale subject cannot discharge the current validation obligation.');
add('credit-15', {requested_scope:'Static API/documentation review only; all required paths were inspected. Generated fixture execution is explicitly outside this task and unnecessary to its conclusion.',
  receipt:fixtureReceipt, reviewer_execution:observations.missing},
  {credit_disposition:'credit', limitation_disposition:'not-required', auxiliary_count_after:5, public_review_complete:true},
  'The same actually unavailable fixture as credit-05 is nonblocking for an independently justified static scope.');

const subagentRequest = {execution_mode:'subagents', repository:'fixture/review',
  base_sha:'b1', head_sha:'h1', scope:'changeset', focus:null, lens_name:'standard', role:'standard',
  request_id:'standard-5', instruction_digest:'synthetic-complete-b1-h1-standard-instructions'};
const subagentOutput = {findings:[], overall_correctness:'patch is correct',
  overall_explanation:'Inspected the complete bound changeset and relevant dependencies against the accepted requirements. No supported defect or material evidence gap remains.',
  overall_confidence_score:0.9};
const subagentResult = {worker_id:'worker-5', result_ref:'runtime-result-5',
  terminal:true, raw_output:JSON.stringify(subagentOutput)};
const earlierStandards = Array.from({length:4}, (_, i) => ({
  assignment:{...subagentRequest, request_id:`standard-${i+1}`},
  worker_id:`worker-${i+1}`, result_ref:`runtime-result-${i+1}`,
  raw_output:JSON.stringify(subagentOutput), credit_disposition:'credit',
  credit_basis:'Exact current independent standard; full inquiry and evidence adequate.'
}));
function addSubagent(id, evidence, decision, basis) {
  cases.push({id, input:{
    subject, execution_mode:'subagents', lens:'standard',
    requested_assignment:subagentRequest, delivered_assignment:subagentRequest,
    instruction_observation:{source:'synthetic host delivery record',
      complete_bundle_identity:subagentRequest.instruction_digest,
      delivered_components:['execution wrapper','pinned Codex rubric','exact assignment and source evidence'],
      exact_bytes_match:true,
      rubric_source_sha256:'ec60e7f36a1d1c2679ce095c0205ecc56f7dd8fb57707a13ef362072390f219f'},
    launch_observation:{worker_id:'worker-5', request_id:'standard-5', delivery_ref:'runtime-delivery-5'},
    terminal_observation:subagentResult,
    context_observation:{fresh_context:true, inherited_peer_conclusions:false,
      full_assignment_delivered:true, accepted_requirements_accessible:true},
    prior_standard_reviews:earlierStandards, prior_credit:{standard:4, auxiliary:5},
    requested_scope:'Changeset-wide standard with the pinned Codex rubric. Full source inquiry is complete. All mandatory pre-review proof passed on this exact candidate; no exploratory check was attempted.',
    other_required_obligations:'All five changeset auxiliaries and the frozen focused-file inventory have exact current subagent evidence, adjudication and credit. No unresolved material findings or limitations.',
    ...evidence
  }, expected:{credit_disposition:'hold', limitation_disposition:null,
    standard_count_after:4, auxiliary_count_after:5,
    public_review_complete:false, original_check_status:'not-run', ...decision}, basis});
}
addSubagent('credit-16', {},
  {credit_disposition:'credit', standard_count_after:5, public_review_complete:true},
  'A fifth distinct fresh-context standard with directly attributed exact output completes portable convergence; it is not a CAS or native/default review.');
addSubagent('credit-17', {terminal_observation:{...subagentResult, worker_id:'unassigned-worker'}}, {},
  'Matching review prose and a clean object cannot replace runtime attribution. Recover the assigned worker state before replacement; another worker terminating does not establish that this attempt ended.');
addSubagent('credit-18', {delivered_assignment:{...subagentRequest, head_sha:'h0'}}, {},
  'A completed review of another head does not discharge the current request; preserve the four unrelated valid standard credits.');
addSubagent('credit-19', {
  launch_observation:{worker_id:'worker-4', request_id:'standard-5', delivery_ref:'runtime-continuation-4'},
  terminal_observation:{...subagentResult, worker_id:'worker-4'},
  context_observation:{fresh_context:false, inherited_peer_conclusions:false,
    full_assignment_delivered:true, accepted_requirements_accessible:true,
    prior_work:'This is a continuation of already credited standard-4 on the same worker.'}},
  {limitation_disposition:'unresolved'},
  'Continuing an already credited reviewer does not create another independent standard, even with a new request ID and terminal result.');
addSubagent('credit-20', {terminal_observation:{...subagentResult, raw_output:'clean'}}, {},
  'Terminal completion and a bare status have no structured semantic verdict; use the bounded exact-request recovery path, not clean credit.');
addSubagent('credit-21', {terminal_observation:{...subagentResult, raw_output:'{"findings":[]'}}, {},
  'Malformed output is not an empty clean review or a model-authored receipt; do not infer missing fields.');
addSubagent('credit-22', {terminal_observation:{...subagentResult,
    raw_output:JSON.stringify({...subagentOutput, findings:[{title:'Required migration drops valid entries',
      body:'The changed migration discards a required valid input, as confirmed by the bound source and reproduction.',
      confidence_score:1, priority:1, code_location:{absolute_file_path:'/fixture/src/migrate.mjs', line_range:{start:3,end:3}}}]})},
    review_fold:'The reported current material violation is entailed, accepted, and unresolved.'},
  {standard_count_after:0, auxiliary_count_after:0},
  'A clean correctness label cannot erase a nonempty finding array. Preserve the finding for admission; the accepted material violation invalidates all credit.');
addSubagent('credit-23', {context_observation:{fresh_context:false,
    inherited_peer_conclusions:true, full_assignment_delivered:true,
    accepted_requirements_accessible:true,
    inherited_context:'The parent transcript includes sibling findings, four prior clean verdicts, and the required fifth-clean target.'}},
  {limitation_disposition:'unresolved'},
  'An instruction to ignore inherited conclusions does not establish the required fresh independent context.');
addSubagent('credit-24', {
  requested_assignment:{...subagentRequest, request_id:'standard-1'},
  delivered_assignment:{...subagentRequest, request_id:'standard-1'},
  launch_observation:{worker_id:'worker-5', request_id:'standard-1', delivery_ref:'runtime-delivery-5'},
  prior_standard_reviews:earlierStandards.map(entry => ({...entry,
    assignment:{...entry.assignment, execution_mode:'cas'},
    provenance:'Historical native/CAS campaign, preserved under its original mode.'})),
  prior_credit:{execution_mode:'cas', standard:4, auxiliary:5},
  current_campaign:'A newly bound subagent initial wave; this is its first standard. The other required initial portable obligations are complete as described above.'},
  {credit_disposition:'credit', standard_count_after:1},
  'The first portable standard earns one portable credit. Four historical CAS standards cannot be combined with it to satisfy a mode-specific streak.');
addSubagent('credit-25', {launch_observation:null, terminal_observation:null,
    prior_standard_reviews:[], prior_credit:{standard:5, auxiliary:5},
    resume_evidence:'Only an earlier summary saying five standards and all auxiliaries clean survives; exact worker results, assignment deliveries, and runtime attribution are unavailable.',
    other_required_obligations:'No exact auxiliary or focused-file results are recoverable.'},
  {standard_count_after:0, auxiliary_count_after:0},
  'Resume cannot reconstruct review evidence from counts or prose. Recover exact results or require a fresh initial wave; retain any separately recoverable findings.');

const fields = {
  credit_disposition:'credit | hold', limitation_disposition:'recovered | covered | not-required | unresolved | null',
  standard_count_after:'integer', auxiliary_count_after:'integer', public_review_complete:'boolean',
  original_check_status:'blocked | skipped | not-run | unknown',
  credit_basis:'source-supported rationale', user_summary:'honest scoped user update', pr_summary:'honest scoped PR update'
};
function exported(c) {
  const selected = ['review-closeout.md','references/review-contract.md',
    'references/review-contract.json','references/closure.md'];
  if (c.input.execution_mode === 'subagents') selected.push('references/subagent-reviews.md');
  const guidance = Object.fromEntries(selected.map(path =>
    [path, readFileSync(new URL(`../${path}`, import.meta.url), 'utf8')]));
  return {task:'Act as the Actuating owner at review admission. Adjudicate this synthetic result using the supplied current workflow. Return the evaluation fields below, with the evidence basis and public updates. Do not fabricate observations or change the required scope. These fields are for offline evaluation, not a new production handoff schema.',
    guidance, evidence:c.input, response_fields:fields};
}
function grade(c, response) {
  assert(response && typeof response === 'object' && !Array.isArray(response), 'response must be an object');
  for (const [field, expected] of Object.entries(c.expected))
    assert.deepEqual(response[field], expected, `${c.id}: ${field}`);
  for (const field of ['credit_basis','user_summary','pr_summary'])
    assert(typeof response[field] === 'string' && response[field].trim(), `${c.id}: missing ${field}`);
  // No keyword heuristic can establish semantic adequacy or truthful free text.
}
const key = () => cases.map(({id,expected,basis}) => ({id, expected, semantic_checks:basis}));
const args = process.argv.slice(2);
const usage = 'usage: node test-review-credit.mjs [--list | --case credit-NN | --key | --grade credit-NN response.json]';
try {
  if (args.length === 1 && args[0] === '--list') console.log(cases.map(c => c.id).join('\n'));
  else if (args.length === 1 && args[0] === '--key') console.log(JSON.stringify(key(), null, 2));
  else if ((args.length === 2 && args[0] === '--case') || (args.length === 3 && args[0] === '--grade')) {
    const c = cases.find(c => c.id === args[1]);
    assert(c, 'unknown case');
    if (args[0] === '--case') console.log(JSON.stringify(exported(c), null, 2));
    else {
      grade(c, JSON.parse(readFileSync(args[2], 'utf8')));
      console.log('Structured replay observations match; independently assess the evidence rationale and both public summaries.');
    }
  } else if (args.length) throw Error(usage);
  else {
    assert.equal(new Set(cases.map(c => c.id)).size, cases.length);
    const invoke = (...params) => spawnSync(process.execPath,
      [fileURLToPath(import.meta.url), ...params], {encoding:'utf8'});
    const dir = mkdtempSync(join(tmpdir(), 'actuating-credit-grader-'));
    try {
      const responsePath = join(dir, 'response.json');
      let rejected = 0;
      for (const c of cases) {
        const result = invoke('--case', c.id);
        assert.equal(result.status, 0, result.stderr);
        assert.deepEqual(JSON.parse(result.stdout), exported(c));
        assert.deepEqual(Object.keys(exported(c)).sort(), ['evidence','guidance','response_fields','task']);
        const valid = {...c.expected, credit_basis:'grader self-test, not a model response',
          user_summary:'grader self-test', pr_summary:'grader self-test'};
        grade(c, valid);
        for (const field of Object.keys(c.expected)) {
          const wrong = {...valid, [field]:typeof valid[field] === 'number' ? valid[field]+1 : '__wrong__'};
          assert.throws(() => grade(c, wrong), new RegExp(field));
          rejected++;
        }
        const missing = {...valid}; delete missing.credit_disposition;
        assert.throws(() => grade(c, missing), /credit_disposition/);
        writeFileSync(responsePath, JSON.stringify(valid));
        assert.equal(invoke('--grade', c.id, responsePath).status, 0);
      }
      // The incident's reduction: acknowledge the caveat, but still credit and publish completion.
      writeFileSync(responsePath, JSON.stringify({credit_disposition:'credit', limitation_disposition:'unresolved',
        standard_count_after:5, auxiliary_count_after:5, public_review_complete:true,
        original_check_status:'blocked', credit_basis:'Receipt verified clean; sandbox limits disclosed.',
        user_summary:'All reviews clean.', pr_summary:'Review complete.'}));
      assert.equal(invoke('--grade', 'credit-01', responsePath).status, 2);
      writeFileSync(responsePath, '{');
      assert.equal(invoke('--grade', 'credit-01', responsePath).status, 2);
      for (const params of [['--case','missing'], ['--case'], ['--unknown'], ['--grade','credit-01','/nonexistent-response']])
        assert.equal(invoke(...params).status, 2, JSON.stringify(params));
      assert.deepEqual(JSON.parse(invoke('--key').stdout), key());
      assert.equal(invoke('--list').stdout.trim().split('\n').length, cases.length);
      console.log(`actuating: ${cases.length} evidence-only credit replays, three executed fixture probes, ${rejected} incorrect structured observations rejected, and CLI/key isolation passed; no model evaluation or runtime admission enforcement tested`);
    } finally { rmSync(dir, {recursive:true, force:true}); }
  }
} catch (error) { console.error(error.message); process.exitCode = 2; }
