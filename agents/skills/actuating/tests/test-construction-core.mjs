#!/usr/bin/env node
// Source-contract and mutation tests only. These do not execute coding agents,
// measure efficacy, or prove the behavior of an implementation produced by a model.
import assert from 'node:assert/strict';
import './test-success-premises.mjs';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const paths = ['SKILL.md', 'construction.md', 'architecture.md', 'counterexamples.md', 'recurrence.md',
  'review-closeout.md',
  'agents/openai.yaml', 'references/review-contract.json',
  'references/decision-contract.json', 'universalist-composition.md',
  '../universalist/SKILL.md', '../universalist/README.md',
  'tests/construction-comparison.md'];
const sources = Object.fromEntries(paths.map(p => [p, readFileSync(resolve(root,p),'utf8')]));
const hash = s => createHash('sha256').update(s).digest('hex');
const section = (s,h) => {
  assert(s.includes(`## ${h}\n`), `missing section: ${h}`);
  return s.split(`## ${h}\n`)[1].split('\n## ')[0];
};
const normalized = s => s.replace(/\s+/g,' ');

function check(src) {
  const skill=src['SKILL.md']+'\n'+src['construction.md'];
  assert(normalized(section(src['SKILL.md'],'Public routes')).includes(
    'It may acquire evidence about an existing candidate but cannot mutate, publish, grant closure credit, or claim completion'));
  const core=normalized(section(skill,'Initial construction'));
  const architecture=normalized(src['architecture.md']);
  const counter=src['counterexamples.md'];
  const adapter=normalized(src['universalist-composition.md']);
  const policy=JSON.parse(src['references/review-contract.json']);
  assert.equal(policy.standard_convergence.required_consecutive_clean_attempts,5);
  const contract=JSON.parse(src['references/decision-contract.json']).skill_decision_contract;
  // Byte-bound safeguards from fc82de2d26052ff2b20f0fe9d4ebae289965091d.
  // Their source authority is unchanged by the construction experiment.
  for (const [h,digest] of Object.entries({
    'Source binding':'a08472adfb58b7540f832680acac69f92a87e7ee8e4086c9621134194aa4639d',
    'Realization and common proof obligations':'8f782e151a2c48cca2da1506830376ad597b689fde6985014f30c466f87be6e3',
    'Completion':'dc56a54f2fd79d07f4d801b030cbf5b5a1ec6758be7a8c72eae0e8c2f630f58f'
  })) assert.equal(hash(section(skill,h)),digest,`changed acceptance/authority section: ${h}`);
  assert.equal(hash(section(skill,'Construction Working Set')),
    'a700fdc90b29b61e05f7520f2e36ffaebf35baa668c8a7bfb0bb055550ff7b45','changed construction assignment binding');
  const admissionStart=counter.indexOf('Before counterexample-driven selection,');
  const admissionEnd=counter.indexOf('\n## Compile the first loss of guarantee');
  assert(admissionStart>=0 && admissionEnd>admissionStart);
  assert.equal(hash(counter.slice(admissionStart,admissionEnd)),
    '565fc772892c5d343f778cf96706610aa545d965c1f5d08105b2bf6c07d370a5','changed witness admission');

  assert(core.includes('No fixed order of diagnosis, algebraic derivation, prototyping, or proof attempts is required'));
  assert(core.includes('Missing proof is not a witnessed defect'));
  assert(core.includes('neither local-repair-first nor redesign is compulsory'));
  assert(core.includes('including `$universalist` for task-relevant semantic work'));
  assert(core.includes('independent evidence'));
  assert(!/Protean|Horos|Kosmos/.test(core+architecture+adapter),'repository-specific construction policy');
  assert(architecture.includes('This pairing does not impose an order relative to Universalist'));
  assert(architecture.includes('apply `$glaze` then `$metanoetic` verbatim in one shared activation'));
  assert(adapter.includes('optional presentation, not required output'));
  assert(adapter.includes('does not relax their applicable evidence, comparison, or claim-strength requirements'));
  assert(adapter.includes('`analyze` remains read-only'));
  assert(!/\bActuating\b|\$actuating|actuating-composition\.md/.test(src['../universalist/SKILL.md']),'Universalist entry imports its implementation caller');
  assert(architecture.includes('[Universalist composition](universalist-composition.md)'));
  assert(src['../universalist/SKILL.md'].includes('authorized implementation includes required'));
  assert(src['../universalist/README.md'].includes("Architectonic's read-only nomination contract is unchanged"));
  assert(counter.includes('[proof acceptance](SKILL.md#proof-acceptance)'));
  const repeated='Before accepting validation for local completion or reviewability';
  assert.equal(skill.split(repeated).length-1,1,'canonical verifier-integrity rule missing or duplicated');
  assert(!counter.includes(repeated),'duplicated verifier-integrity rule');
  assert(normalized(section(skill,'Proof acceptance')).includes('A passing weakened suite cannot discharge an unchanged requirement'));
  assert(normalized(section(skill,'Proof acceptance')).includes('does not demand a finished causal account before authorized exploration'));

  // Simulation-first correctness is an owner decision. These are source-contract checks,
  // not a simulator run or evidence that an agent builds or uses one.
  // Skills carry no repository-specific history: no sentence opens with an all-caps
  // project label such as "NAME:" in runtime guidance or the decision rationale.
  const anecdote=/(^|[.!?]\s+)[A-Z][A-Z0-9-]{3,}:/m;
  for(const path of ['SKILL.md','construction.md','counterexamples.md','recurrence.md','review-closeout.md'])
    assert(!anecdote.test(src[path]),`repository-specific content: ${path}`);
  const simulation=normalized(section(skill,'Simulation-first correctness'));
  for(const rule of ['A law is trace-dependent when its truth depends on the order, interleaving, timing, or repetition',
    'durable state: data that outlives the process that wrote it',
    'concurrency: actors such as threads, tasks, processes, or peers',
    'retry, restart, recovery, or replay of an input','time: clocks, deadlines, timeouts, or schedules',
    'external effects whose outcome later behavior depends on',
    'Daemons, runtimes, stores, schedulers, and protocols qualify',
    'Software with none of these, such as a parser, codec, or in-memory data structure, is a pure library',
    'So is a one-shot tool whose effects only fail fast',
    'A tool that resumes, retries, syncs, caches, or keeps a state file is stateful',
    'Classify by these properties, not by repository, language, or size',
    'For stateful or concurrent software, the construction includes',
    'every state reaches rest through ordinary inputs',
    'The simulator asserts that every transition it observes is in the table',
    'The oracle shares none of the deciding logic it checks',
    'the scheduling of runnable actors','checked against the real service',
    'Running one seed twice yields the same event trace','It checks every law after every event',
    'every admitted obligation has reached rest','It pins each failure as its seed and recorded event trace',
    'Pure libraries use property-based tests of their laws',
    'A one-shot tool also injects a failure at every effect seam','only the user can reduce them',
    'a sweep that never produces an event kind the changed code handles is incomplete',
    'When no simulator exists, build the smallest one',
    'keeps its ordinary tests and runs in the simulator as real code',
    'a seam outside the authorized path scope is a [source-binding](#source-binding) blocker',
    'In `analyze`, classify and judge against these rules without building, extending, or running mutating controls'])
    assert(simulation.includes(rule),`lost simulation rule: ${rule}`);
  const rules=normalized(section(skill,'Construction rules'));
  for(const rule of ['Apply these rules to the stored state, transitions, and interfaces the Goal builds or changes',
    'They are construction means, not source requirements: a violation is a liability only through a required law it breaks',
    'Delete state whose subject no longer exists','is history about its subject, not live state',
    'Give every stored state an exit by an ordinary transition',
    'Editing data, code, or configuration outside that interface is not one',
    'Compute each derived quantity in exactly one function, invoked by every transition that changes it',
    'Give every admitted input exactly one recorded terminal disposition','never none and never two',
    'Give each wire value one canonical spelling','emit only the canonical one',
    'Pass values, not references, across trust or namespace boundaries',
    'Make read surfaces report recorded facts, not predictions of a later decision'])
    assert(rules.includes(rule),`lost construction rule: ${rule}`);
  const reinjection=normalized(section(counter,'Re-inject confirmed defects'));
  for(const rule of ['Before a head carrying its fix becomes reviewable or is published',
    'A scripted replay of the reported trace is not an extension',
    'Pin a seed, with its trace, that fails on the defective version and passes with the fix',
    "A catch must come from a law or oracle exposing the defect's wrong observation",
    'so re-inject outside an open review epoch',
    'Only a defect whose wrong observation is not behavior of the running software',
    'is an [oracle correction](#observe-and-adjudicate)',
    'until the simulator expresses the defect or the user accepts the gap'])
    assert(reinjection.includes(rule),`lost re-injection rule: ${rule}`);
  // One fallback for an unavailable control: the existing unresolved-coverage rule.
  assert(normalized(counter).includes('If a safe, proportionate control is unavailable, use a decisive independent source argument or leave the affected coverage claim unresolved'));
  assert(!/only the user can waive/i.test(reinjection),'second re-injection fallback');
  const progress=src['recurrence.md'].split('## Progress before another iteration\n')[1];
  const plateau=normalized(progress.slice(progress.indexOf('For [stateful or concurrent software]'),progress.indexOf('When an admitted defect lies')));
  assert(plateau.includes('that explicit assessment, and any earlier one prompted by recurring findings, includes simulator coverage'),'lost plateau simulator check');
  assert(plateau.includes('reclassify it') && plateau.includes('Clean counts do not measure this coverage'));
  // Obligations stay unconditional; only the separate behavioral model is optional.
  const weakening=/\boptional(?!\s*\[executable behavioral model\])|\bmay (?:skip|omit|include)\b|best[- ]effort|where (?:practical|feasible)|if convenient/i;
  for(const [name,text] of [['simulation',simulation],['re-injection',reinjection],['plateau',plateau]])
    assert(!weakening.test(text),`weakened ${name} obligation`);
  // Epoch opening, screen, and credit agree between prose and policy JSON.
  const closeout=src['review-closeout.md'];
  const epoch=normalized(section(closeout,'Review-epoch immutability and evidence acquisition'));
  assert(epoch.includes('A review epoch opens on the first initial-inventory request'),'epoch opening not bound to the initial inventory');
  assert(epoch.includes('the [pre-epoch screen](#pre-epoch-screen) precedes it and opens none'));
  assert.equal(policy.review_epoch.opens_on_first_initial_inventory_dispatch,true);
  assert(!('opens_on_first_review_dispatch' in policy.review_epoch),'contradictory epoch opening');
  const screen=normalized(section(closeout,'Pre-epoch screen'));
  for(const rule of ['Before the first initial-inventory request on a reviewable head',
    'record `screen_disposition: pass | hold` with its basis, never `credit_disposition`',
    'The screen must observe the complete base-to-head patch',
    'that holds the screen and every epoch standard alike','The screen binds its exact head',
    'with no epoch open, it triggers no initial-inventory barrier',
    'The screen awards no review credit and replaces no request'])
    assert(screen.includes(rule),`lost screen rule: ${rule}`);
  const screenPolicy=policy.pre_epoch_screen;
  assert.equal(screenPolicy.guidance_ref,'agents/skills/actuating/review-closeout.md#pre-epoch-screen');
  assert.equal(screenPolicy.applies_to,'every-review-epoch');
  assert.equal(screenPolicy.disposition_field,'screen_disposition');
  for(const key of ['records_credit_disposition','awards_review_credit','opens_review_epoch',
    'replaces_initial_inventory_request','finding_triggers_initial_inventory_barrier'])
    assert.equal(screenPolicy[key],false,key);
  for(const key of ['complete_patch_observation_required','summary_only_patch_observation_holds_every_changeset_standard',
    'binds_exact_reviewable_head','held_screen_blocks_epoch'])
    assert.equal(screenPolicy[key],true,key);
  assert.equal(policy.contract_id,'actuating-review-contract-v33');
  assert.equal(policy.construction_selection.reasoning_sequence_required,false);
  assert.equal(policy.construction_selection.metanoetic_before_universalist_when_triggered,false);
  assert.equal(policy.universalist_compilation.nomination_result_required,false);
  assert.equal(policy.universalist_compilation.nomination_is_executed_proof,false);
  assert.equal(policy.efficacy.policy_unit_tests_prove_model_efficacy,false);
  assert.equal(contract.skill.source_fingerprint,'actuating-construction-core-v43');
  const clauses=Object.fromEntries(contract.clauses.map(c=>[c.clause_id,c]));
  assert(clauses['ACT-IMPLEMENT-ENTRY-001'].success_signals.some(s=>s.includes('without a fixed reasoning sequence')));
  assert(clauses['ACT-METANOETIC-ADMISSIBILITY-001'].success_signals.some(s=>s.includes('no required order relative to Universalist')));
  assert(clauses['ACT-UNIVERSALIST-COMPILATION-001'].success_signals.some(s=>s.includes('optional presentation')));
  const routeIds=new Set(contract.routes.map(r=>r.route_id));
  const triggerIds=new Set(contract.triggers.map(t=>t.trigger_id));
  assert.equal(routeIds.size,4); assert.equal(triggerIds.size,5);
  assert.deepEqual(Object.keys(clauses).sort(),["ACT-CLOSURE-001","ACT-CONSTRUCTION-COMPILER-001","ACT-IMPLEMENT-ENTRY-001","ACT-LAW-AUTHORITY-001","ACT-METANOETIC-ADMISSIBILITY-001","ACT-OWNER-FACTS-001","ACT-REVIEW-EPOCH-001","ACT-REVIEW-EVIDENCE-001","ACT-SIMULATION-001","ACT-UNIVERSALIST-COMPILATION-001"]);
  const sim=clauses['ACT-SIMULATION-001'];
  assert(sim.failure_signals.includes('a pure library is required to build a simulator'));
  assert(sim.expected_routes.includes('ACT-ANALYZE'));
  assert(sim.success_signals.some(s=>s.startsWith('analyze classifies and judges against these rules without building')),'analyze may build');
  assert(sim.failure_signals.includes('analyze builds or extends a simulator or runs mutating controls'));
  assert(sim.success_signals.some(s=>s.includes('every re-injected defect pins a seed and trace')),'pinning limited to misses');
  assert(sim.required_artifacts.some(s=>s.includes('a pinned seed and trace that fail on the defective version and pass with the fix')));
  assert(sim.failure_signals.some(s=>s.includes('screen results are recorded as credit_disposition')));
  assert(!anecdote.test(sim.rationale) && !/\b\d+ of \d+\b/.test(sim.rationale),'repository-specific rationale');
  for(const c of contract.clauses) {
    for(const id of c.trigger_refs) assert(triggerIds.has(id),id);
    for(const id of [...c.expected_routes,...c.prohibited_routes]) assert(routeIds.has(id),id);
  }
  const metadata=src['agents/openai.yaml'];
  assert(metadata.includes('allow_implicit_invocation: true'));
  const prompt=JSON.parse(metadata.split('  default_prompt: ')[1].trim());
  assert(prompt.includes('selected route and completion boundary in SKILL.md'));
  assert(!prompt.includes('Universalist derives and nominates'));

  const comparison=src['tests/construction-comparison.md'];
  for(const required of ['authored, not model-replayed','Control: current workflow','Candidate: active construction task',
    '753569e0df6935a428ed8c509fb7fac5f23c008d',
    'Preserve its ability to discover the same relationship or choose the same task',
    'Give both arms the same requirements, evidence, suggested repairs, source and theory access',
    'Assignment','Continuation','Fresh context',
    'adequate-incumbent','direct-fix','false-allegation','wrong-oracle',
    'A: accumulated','B: reduced','C: protocol-free',
    '5159d76f3b627fb334e2ecb89c5cccf1db9d2e07','AGENTS.md','compaction','memory',
    'required-valid','Freeze the first completed candidate','timeouts',
    'A tie or insufficient power is inconclusive','no permission for paid model runs']) {
    assert(normalized(comparison).includes(required),`lost comparison control: ${required}`);
  }
  assert.equal(policy.efficacy.comparison_ref,'agents/skills/actuating/tests/construction-comparison.md');
  assert.equal(policy.efficacy.held_out_requires_witness_not_supplied_to_implementing_run,true);
  const simulationComparison=normalized(section(comparison,'Simulation-first construction'));
  for(const control of ['authored, not model-replayed','5939b6c039478a5fb932459bab4c5c2bee5edd19',
    'informs their revision, not their current force','the implementing run never sees them',
    'Retain all attempts in the denominators',
    'Report simulator construction, seed budget, and CI time separately from per-defect time to first detection',
    'A tie or underpowered result is inconclusive','adds no delivery gate or permission for paid model runs'])
    assert(simulationComparison.includes(control),`lost simulation comparison control: ${control}`);
  assert(!/\b\d+ of \d+\b/.test(simulationComparison),'repository-specific comparison evidence');
}

check(sources);
// Deliberate source/contract mutations verify that this test is not a pass-by-default.
// They are not simulations of agent behavior or tests of the causal hypothesis.
const jsonMutation=(path,fn)=>src=>{const value=JSON.parse(src[path]);fn(value);src[path]=JSON.stringify(value)};
const loose=phrase=>new RegExp(phrase.replace(/[.*+?^${}()|[\]\\]/g,'\\$&').replace(/ /g,'\\s+'));
const swap=(path,before,after)=>src=>{src[path]=src[path].replace(loose(before),after);};
const append=(path,text)=>src=>{src[path]+=text;};
const decisionMutation=fn=>jsonMutation('references/decision-contract.json',p=>fn(p.skill_decision_contract.clauses.find(c=>c.clause_id==='ACT-SIMULATION-001')));
const mutations=[
  ['caller dependency reintroduced',src=>{src['../universalist/SKILL.md']+='\nInside Actuating, load its workflow.\n';}],
  ['review weakening',jsonMutation('references/review-contract.json',p=>p.standard_convergence.required_consecutive_clean_attempts=4)],
  ['fixed cross-skill order',jsonMutation('references/review-contract.json',p=>p.construction_selection.metanoetic_before_universalist_when_triggered=true)],
  ['required nomination',jsonMutation('references/review-contract.json',p=>p.universalist_compilation.nomination_result_required=true)],
  ['false efficacy credit',jsonMutation('references/review-contract.json',p=>p.efficacy.policy_unit_tests_prove_model_efficacy=true)],
  ['weakened proof',src=>{src['construction.md']=src['construction.md'].replace('required-valid behavior and observations preserved','optional valid behavior');}],
  ['lost read-only route',src=>{src['SKILL.md']=src['SKILL.md'].replace('It may acquire evidence','It may mutate evidence');}],
  ['lost mathematical capability',src=>{src['construction.md']=src['construction.md'].replace('including `$universalist` for task-relevant semantic','excluding mathematical');}],
  ['duplicate acceptance rule',src=>{src['counterexamples.md']+='\nBefore accepting validation for local completion or reviewability\n';}],
  ['baseline instruction leakage unchecked',src=>{src['tests/construction-comparison.md']=src['tests/construction-comparison.md'].replace('`AGENTS.md`','an unspecified file');}],
  ['first candidate unfrozen',src=>{src['tests/construction-comparison.md']=src['tests/construction-comparison.md'].replace('Freeze the first completed candidate','Score the final repaired result');}],
  ['repository history as policy',append('construction.md','\nPROJECTX: this project justified the rule.\n')],
  ['repository history in rationale',decisionMutation(c=>{c.rationale+=' The simulator caught 3 of 4 defects there.';})],
  ['simulator made optional',swap('construction.md','the construction includes','the construction may include')],
  ['sweep made optional',swap('construction.md','Record each sweep','The fresh sweep is optional. Record each sweep')],
  ['one-shot tools forced into simulation',swap('construction.md','So is a one-shot tool whose effects only fail fast','So is no one-shot tool, even one whose effects only fail fast')],
  ['pure libraries forced into simulation',swap('construction.md','in-memory data structure, is a pure library','in-memory data structure, is stateful')],
  ['external effects unconditioned',swap('construction.md','external effects whose outcome later behavior depends on','external effects of any kind')],
  ['simulator scope widened past durable state',swap('construction.md','durable state: data that outlives the process that wrote it','retained state: memory that a later operation reads')],
  ['concurrency trigger dropped',swap('construction.md','- concurrency: actors such as threads, tasks, processes, or peers whose interleaving can change an observation;\n','')],
  ['classified by repository',swap('construction.md','Classify by these properties, not by repository, language, or size.','Classify by repository.')],
  ['scheduler left unowned',swap('construction.md','the scheduling of runnable actors, and','and')],
  ['fakes unchecked',swap('construction.md',', checked against the real service','')],
  ['nondeterministic replay tolerated',swap('construction.md',' Running one seed twice yields the same event trace.','')],
  ['lifecycle table may drift',swap('construction.md','The simulator asserts that every transition it observes is in the table, so the table cannot drift from the code.','')],
  ['oracle shares deciding logic',swap('construction.md','The oracle shares none of the deciding logic it checks','The oracle may reuse the deciding logic it checks')],
  ['unbounded simulator construction',swap('construction.md','build the smallest one','build a complete one')],
  ['changed helper forced into simulation',swap('construction.md','keeps its ordinary tests and runs in the simulator as real code','needs its own simulator')],
  ['scope broadened for seams',swap('construction.md','a seam outside the authorized path scope is a [source-binding](#source-binding) blocker, not license to broaden that scope','a seam outside the authorized path scope may be added')],
  ['analyze builds',swap('construction.md','without building, extending, or running mutating controls','and builds what is missing')],
  ['construction rule dropped',swap('construction.md','- Give every admitted input exactly one recorded terminal disposition, such as applied, rejected, superseded, or failed: never none and never two.\n','')],
  ['construction rules promoted to requirements',swap('construction.md','They are construction means, not source requirements','They are source requirements')],
  ['fix lands before re-injection',swap('counterexamples.md','Before a head carrying its fix becomes reviewable or is published','After a head carrying its fix is published')],
  ['scripted replay accepted',swap('counterexamples.md','A scripted replay of the reported trace is not an extension.','')],
  ['outside scope widened',swap('counterexamples.md','Only a defect whose wrong observation is not behavior of the running software','Any defect the current simulator does not reach')],
  ['second re-injection fallback',append('counterexamples.md','\nOnly the user can waive this control.\n')],
  ['plateau check optional',swap('recurrence.md','includes simulator coverage','optionally includes simulator coverage')],
  ['plateau keyed to clean counts',swap('recurrence.md','Clean counts do not measure this coverage.','Rising clean counts establish this coverage.')],
  ['epoch opens on any review request',swap('review-closeout.md','opens on the first initial-inventory request','opens on the first review request')],
  ['screen records credit',swap('review-closeout.md','never `credit_disposition`','as `credit_disposition`')],
  ['screen skips the complete patch',swap('review-closeout.md','The screen must observe the complete base-to-head patch.','')],
  ['contradictory epoch opening key',jsonMutation('references/review-contract.json',p=>{p.review_epoch.opens_on_first_review_dispatch=true;})],
  ['screen credited',jsonMutation('references/review-contract.json',p=>p.pre_epoch_screen.awards_review_credit=true)],
  ['screen opens epoch',jsonMutation('references/review-contract.json',p=>p.pre_epoch_screen.opens_review_epoch=true)],
  ['screen scoped to stateful subjects',jsonMutation('references/review-contract.json',p=>p.pre_epoch_screen.applies_to='stateful-or-concurrent-subject')],
  ['screen credit disposition',jsonMutation('references/review-contract.json',p=>p.pre_epoch_screen.records_credit_disposition=true)],
  ['simulation clause removed',jsonMutation('references/decision-contract.json',p=>{p.skill_decision_contract.clauses=p.skill_decision_contract.clauses.filter(c=>c.clause_id!=='ACT-SIMULATION-001');})],
  ['pinning only after a miss',decisionMutation(c=>{c.success_signals=c.success_signals.map(s=>s.replace('every re-injected defect pins','a missed defect pins'));})],
  ['analyze route allowed to build',decisionMutation(c=>{c.failure_signals=c.failure_signals.filter(s=>!s.startsWith('analyze builds'));})],
  ['held-out comparison leaked',swap('tests/construction-comparison.md','the implementing run never sees them','the implementing run may see them')]
];
for(const [name,mutate] of mutations) {
  const mutant={...sources}; mutate(mutant);
  assert(Object.keys(sources).some(path=>mutant[path]!==sources[path]),`inactive mutation: ${name}`);
  assert.throws(()=>check(mutant),assert.AssertionError,`undetected mutation: ${name}`);
}
console.log(`actuating: reduced-construction source contract and ${mutations.length} mutation controls passed; agent efficacy not evaluated`);
