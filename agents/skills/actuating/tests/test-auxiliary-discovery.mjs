#!/usr/bin/env node
// Offline discovery subjects and executable fixture probes, not an agent judge.
// --case exposes only authority and source; the evaluator key stays separate.
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {runInNewContext} from 'node:vm';

const cases = [];
function add(id, pair, lens, goal, source, probe, observation, verdict, basis, evidence = {}) {
  cases.push({id, pair, lens, input: {
    subject: `Isolated current fixture ${id}; supplied source is the complete relevant surface.`,
    goal, candidate_source: source, ...evidence
  }, probe, observation, verdict, basis});
}

const batchGoal = 'For arrays of booleans, report complete only when every item succeeded. Report partial otherwise. An empty batch is complete. No external effects.';
const batch = predicate => `function report(results) {
  return {status: results.${predicate}(x => x) ? 'complete' : 'partial'};
}`;
const batchProbe = '[report([true,false]),report([true,true]),report([])]';
add('subject-01','judgment','soundness-skeptic',batchGoal,batch('every'),batchProbe,
  [{status:'partial'},{status:'complete'},{status:'complete'}], 'no-finding',
  'Every positive completion judgment is justified in the finite boolean domain, including the empty case.');
add('subject-02','judgment','soundness-skeptic',batchGoal,batch('some'),batchProbe,
  [{status:'complete'},{status:'complete'},{status:'partial'}], 'findings',
  'Mixed results are falsely called complete; the required empty-batch observation also fails.');

const deleteGoal = 'remove accepts boolean dryRun and a store of string IDs. The documented dryRun option must never change the store; it returns the existing targets. Normal removal must delete exactly those targets.';
const remove = body => `const store = new Set(['a','b']);
function remove(ids, {dryRun = false} = {}) {
  const targets = ids.filter(id => store.has(id));
  ${body}
  return targets;
}`;
const removeProbe = `(() => {
  const preview = remove(['a'], {dryRun:true}), afterPreview = [...store];
  remove(['a']); return {preview,afterPreview,afterRemoval:[...store]};
})()`;
add('subject-03','affordance','footgun-finder',deleteGoal,
  remove('for (const id of targets) store.delete(id);'),removeProbe,
  {preview:['a'],afterPreview:['b'],afterRemoval:['b']}, 'findings',
  'A documented dry run deletes through the ordinary operation; no admission bypass is required for this trap.');
add('subject-04','affordance','footgun-finder',deleteGoal,
  remove('if (!dryRun) for (const id of targets) store.delete(id);'),removeProbe,
  {preview:['a'],afterPreview:['a','b'],afterRemoval:['b']}, 'no-finding',
  'The no-effect preview and normal deletion both satisfy the accepted contract.');

const rangeGoal = 'admit snapshots scalar bounds with integer 0 <= start <= end <= 100. Reject other bounds. Public values are immutable; later caller writes must not change them. length equals end-start. No other transitions exist.';
const range = owned => `function admit(raw) {
  const {start,end} = raw.bounds;
  if (!Number.isInteger(start) || !Number.isInteger(end) || start < 0 || start > end || end > 100) throw Error('invalid');
  const bounds = ${owned ? 'Object.freeze({start,end})' : 'raw.bounds'};
  return Object.freeze({bounds,length:end-start});
}`;
const rangeProbe = `(() => {
  const raw = {bounds:{start:1,end:3}}, value = admit(raw);
  raw.bounds.end = 4;
  return {start:value.bounds.start,end:value.bounds.end,length:value.length};
})()`;
add('subject-05','preservation','invariant-ace',rangeGoal,range(false),rangeProbe,
  {start:1,end:4,length:2}, 'findings',
  'A valid admission loses its guarantee through a retained writable alias.');
add('subject-06','preservation','invariant-ace',rangeGoal,range(true),rangeProbe,
  {start:1,end:3,length:2}, 'no-finding',
  'The owned scalar snapshot closes the alias. A stronger static type is optional, not a missing guarantee.');

const ownerGoal = 'fee(n) is the sole production fee-policy owner for integer quantities 1..3. quote and charge must use that authority and agree. Independent test/reference oracles are permitted and must not share the production helper.';
const feeSource = charge => `function fee(n) { return n * 2; }
function quote(n) { return fee(n); }
function charge(n) { return ${charge}; }`;
const feeProbe = '[1,2,3].map(n => [quote(n),charge(n)])';
add('subject-07','ownership','complexity-mitigator',ownerGoal,feeSource('fee(n)'),feeProbe,
  [[2,2],[4,4],[6,6]], 'no-finding',
  'Both production paths derive from the same semantic owner.');
add('subject-08','ownership','complexity-mitigator',ownerGoal,feeSource('n === 3 ? 5 : n * 2'),feeProbe,
  [[2,2],[4,4],[6,5]], 'findings',
  'A competing production policy violates sole ownership and disagrees at quantity 3.');

const queueGoal = 'enqueue accepts string job IDs. Every accepted job must become done on the next tick. The environment guarantees that tick runs; jobs require no external work. Only queued and done are valid states.';
const queue = progress => `const jobs = [];
function enqueue(id) { jobs.push({id,state:'queued'}); }
function tick() { ${progress ? "for (const job of jobs) job.state = 'done';" : 'return;'} }`;
const queueProbe = "(() => { enqueue('x'); tick(); return jobs; })()";
add('subject-09','outcome','fresh-eyes',queueGoal,queue(true),queueProbe,
  [{id:'x',state:'done'}], 'no-finding',
  'The required end-to-end progress occurs; replacing the bounded loop is not necessary.');
add('subject-10','outcome','fresh-eyes',queueGoal,queue(false),queueProbe,
  [{id:'x',state:'queued'}], 'findings',
  'All states remain valid, but the guaranteed tick fails the accepted progress obligation.');

const proofGoal = 'A published complete status asserts that unit and migration verification have passed on head h1. Judge the supplied provider evidence; do not infer any runtime bug from a proof gap.';
const publication = "const publication = {head:'h1',status:'complete'};";
for (const [id,passed] of [['subject-11',['unit']],['subject-12',['unit','migration']]]) {
  add(id,'justification','soundness-skeptic',proofGoal,publication,
    '({head:publication.head,status:publication.status,passed:provider.passed})',
    {head:'h1',status:'complete',passed}, passed.length === 1 ? 'findings' : 'no-finding',
    passed.length === 1 ? 'The complete claim lacks exact mandatory migration evidence, without establishing a runtime violation.' : 'The exact-head complete claim has both required provider results.',
    {provider_evidence:{owner:'independent fixture verifier',head:'h1',inventory_complete:true,passed}});
}

const oracle = `${feeSource('fee(n)')}
function referenceFee(n) { return [0,2,4,6][n]; }
function check() { return [1,2,3].every(n => fee(n) === referenceFee(n)); }`;
add('subject-13','control','complexity-mitigator',ownerGoal,oracle,'check()',true,
  'no-finding','A separate finite reference oracle is not competing production authority; do not recommend removing its independence.');
add('subject-14','control','complexity-mitigator',ownerGoal,feeSource('n * 2'),feeProbe,
  [[2,2],[4,4],[6,6]], 'findings',
  'The accepted sole-production-owner requirement is violated even though this finite sample agrees. Structural evidence need not invent a behavioral disagreement.');
add('subject-15','control','footgun-finder',
  'checkService independently rejects hostile quantities unless integer 1..3. clientSend also rejects them early for usability. Client checks are untrusted; both boundaries are required. Valid quantities reach stored exactly once.',
  `const stored = [];
function checkService(n) {
  if (!Number.isInteger(n) || n < 1 || n > 3) return 'rejected';
  stored.push(n); return 'accepted';
}
function clientSend(n) {
  if (!Number.isInteger(n) || n < 1 || n > 3) return 'rejected';
  return checkService(n);
}`,
  '({direct:checkService(-1),client:clientSend(-1),valid:clientSend(2),stored})',
  {direct:'rejected',client:'rejected',valid:'accepted',stored:[2]}, 'no-finding',
  'The two checks have distinct required trust-boundary and usability roles.');
add('subject-16','control','invariant-ace',
  'At most one external effect per ID is required. Determine what the current handler establishes; store.reserve semantics are not supplied.',
  'async function handle(id, store, effect) { if (await store.reserve(id)) await effect(id); }',
  null,null,'evidence-gap',
  'Atomicity and persistence of reservation are unknown; do not invent either duplicate execution or a proof of safety.',
  {unavailable_evidence:['store.reserve implementation and atomicity contract']});

const task = 'Review the supplied current subject using the assigned review instructions. Discover supported in-scope findings independently, cite decisive source or evidence, and keep material uncertainty explicit. No allegation is supplied. Do not edit or infer unseen requirements.';
const exported = c => ({task,...c.input});
const key = () => cases.map(({id,pair,lens,verdict,basis}) => ({id,pair,primary_lens:lens,expected:verdict,basis}));
const args = process.argv.slice(2);
if (args.length === 1 && args[0] === '--list') {
  console.log(cases.map(c => c.id).join('\n'));
} else if (args.length === 2 && args[0] === '--case') {
  const c = cases.find(c => c.id === args[1]);
  if (!c) { console.error('unknown subject'); process.exitCode = 2; }
  else console.log(JSON.stringify(exported(c),null,2));
} else if (args.length === 1 && args[0] === '--key') {
  console.log(JSON.stringify(key(),null,2));
} else if (args.length) {
  console.error('usage: node test-auxiliary-discovery.mjs [--list | --case subject-NN | --key]');
  process.exitCode = 2;
} else {
  assert.equal(new Set(cases.map(c => c.id)).size,cases.length);
  let probes = 0;
  for (const c of cases) {
    assert(c.input.goal && c.input.candidate_source && c.basis,c.id);
    assert(['findings','no-finding','evidence-gap'].includes(c.verdict),c.id);
    assert.deepEqual(Object.keys(exported(c)).sort(),
      ['task',...Object.keys(c.input)].sort());
    for (const name of ['proposed_finding','proposed_probe','probe','observation','verdict','expected','basis','pair','lens','primary_lens'])
      assert(!Object.hasOwn(exported(c),name),`${c.id}: answer leakage`);
    if (c.probe === null) { assert.equal(c.observation,null); continue; }
    // Only checked-in synthetic code; no file, network, or process capabilities.
    // VM hygiene is not a security boundary for executing untrusted programs.
    const actual = runInNewContext(
      `${c.input.candidate_source}\nJSON.stringify(${c.probe})`,
      {provider:structuredClone(c.input.provider_evidence)}, {timeout:1000});
    assert.deepEqual(JSON.parse(actual),c.observation,c.id);
    probes++;
  }
  const pairs = ['judgment','affordance','preservation','ownership','outcome','justification'];
  for (const pair of pairs) {
    const [a,b,...rest] = cases.filter(c => c.pair === pair);
    assert(a && b && !rest.length,pair);
    assert.equal(a.input.goal,b.input.goal,pair);
    assert.notEqual(a.verdict,b.verdict,pair);
    assert(a.input.candidate_source !== b.input.candidate_source ||
      JSON.stringify(a.input.provider_evidence) !== JSON.stringify(b.input.provider_evidence),pair);
  }
  // Check serialized CLI inputs, not merely an internal projection function.
  const invoke = (...args) => spawnSync(process.execPath,[fileURLToPath(import.meta.url),...args],{encoding:'utf8'});
  for (const c of cases) {
    const result = invoke('--case',c.id);
    assert.equal(result.status,0,result.stderr);
    assert.deepEqual(JSON.parse(result.stdout),exported(c));
  }
  for (const args of [['--case','missing'],['--case'],['--unknown']])
    assert.equal(invoke(...args).status,2,JSON.stringify(args));
  assert.deepEqual(JSON.parse(invoke('--key').stdout),key());
  assert.equal(invoke('--list').stdout.trim().split('\n').length,cases.length);
  const policy = JSON.parse(readFileSync(new URL('../references/review-contract.json',import.meta.url),'utf8'));
  for (const c of cases) assert(policy.required_lenses.some(l => l.name === c.lens && l.role === 'auxiliary'),c.id);
  console.log(`actuating: ${probes} executable discovery probes, ${cases.length} evidence-only subjects, ${pairs.length} matched pairs, four controls, and CLI isolation checks passed; no model evaluation run`);
}
