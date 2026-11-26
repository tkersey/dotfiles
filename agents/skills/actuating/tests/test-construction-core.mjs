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
  'review-closeout.md', 'references/counterexample-guided-normalization.md',
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
  const core=normalized(section(skill,'Construction decision'));
  const architecture=normalized(src['architecture.md']);
  const counter=src['counterexamples.md'];
  const adapter=normalized(src['universalist-composition.md']);
  const policy=JSON.parse(src['references/review-contract.json']);
  assert.equal(policy.standard_convergence.required_consecutive_clean_attempts,5);
  const contract=JSON.parse(src['references/decision-contract.json']).skill_decision_contract;
  // Pin the authorized source-binding and assignment changes while preserving
  // the unchanged realization and completion obligations.
  for (const [h,digest] of Object.entries({
    'Source binding':'0ce580c9d1999f6f65d90044e7e053e75c6379dfb97e09178d37c2cbbd0a8b4d',
    'Realization and common proof obligations':'8f782e151a2c48cca2da1506830376ad597b689fde6985014f30c466f87be6e3',
    'Completion':'dc56a54f2fd79d07f4d801b030cbf5b5a1ec6758be7a8c72eae0e8c2f630f58f'
  })) assert.equal(hash(section(skill,h)),digest,`changed acceptance/authority section: ${h}`);
  assert.equal(hash(section(skill,'Construction Working Set')),
    'cb4b5c0f65ef2e97170cd10f6abdd141d683786eec2c6f47fb37f4a45c8bd0a1','changed construction assignment binding');
  const admissionStart=counter.indexOf('Before counterexample-driven selection,');
  const admissionEnd=counter.indexOf('\n## Compile the first loss of guarantee');
  assert(admissionStart>=0 && admissionEnd>admissionStart);
  assert.equal(hash(counter.slice(admissionStart,admissionEnd)),
    '81bde09e7b0e74e521ea72849c03cae3e8252682058090f8c4223b946e0d484d','changed witness admission');

  assert(core.includes('No fixed order of diagnosis, algebraic derivation, prototyping, or proof attempts is required'));
  assert(core.includes('Missing proof is not a witnessed defect'));
  assert(core.includes('neither local-repair-first nor redesign is compulsory'));
  assert(core.includes('including `$universalist` for task-relevant semantic work'));
  assert(core.includes('independent evidence'));
  const sourceBinding=normalized(section(skill,'Source binding'));
  const workingSet=normalized(section(skill,'Construction Working Set'));
  for(const rule of [
    'Use this decision for initial work and every substantive return to construction',
    'Each entry route retains its admission, recovery, and freeze rules',
    'No finding, advance alternative, or completed diagnosis is required to begin',
    'Treat the incumbent and proposed remedies as candidates, not requirements',
    'Keep required observations and effect authority fixed',
    'Decide correctness liability and construction opportunity separately',
    'Rejecting an allegation does not erase independently supported evidence useful to authorized construction',
    'Retain that evidence and its premises without importing the rejected requirement or semantic change',
    'An opportunity remains nonblocking unless its realization is part of the accepted task or an accepted obligation is violated',
    'neither repetition nor a preferred design supplies that authority',
    'An observation gap calls for evidence recovery, not an assumed construction defect',
    'recovery can justify continuing the unchanged candidate',
    'No alternatives quota, comparison packet, or new stage is required'
  ]) assert(core.includes(rule),`lost construction-decision boundary: ${rule}`);
  for(const rule of [
    'When a restriction excludes a material alternative, recover its accepted authority',
    'An agent-selected boundary remains revisable unless the accepted source adopted it',
    'An unavailable capability constrains current execution; it does not make an authorized capability change inadmissible',
    'Reconsidering a restriction grants no additional effects or resources'
  ]) assert(sourceBinding.includes(rule),`lost restriction authority: ${rule}`);
  assert(workingSet.includes('Retain decision-relevant opportunity evidence and the authority of consequential restrictions'));
  for(const boundary of [
    'When replacing, combining, reordering, sharing, or removing a construction',
    'use the accepted source to determine which inputs, observations, and continuations the affected construction must support',
    'Establish the required relationships in the actual admitted environments, callbacks, applications, and handlers',
    'matching type names or isolated results alone do not establish interchangeability',
    'When combining edits, check whether one changes a premise used to justify another',
    'Re-establish affected reasoning on the assembled construction',
    'reuse reasoning whose dependencies remain established',
    'The existing [proof acceptance](#proof-acceptance) rules still govern required checks and completion credit',
    'Preserve required joint observations with shared context',
    'Distinguish a captured value, a fresh effect occurrence, and replay of an acquired response when observable'
  ]) assert(core.includes(boundary),`lost composition boundary: ${boundary}`);
  // Skills carry no repository-specific content: no sentence opens with an all-caps
  // project label such as "NAME:", and no link points at a particular repository's
  // commits, pull requests, or issues.
  const anecdote=/(^|[.!?]\s+)[A-Z][A-Z0-9-]{3,}:/m;
  const repositoryLink=/github\.com\/[^\s/)]+\/[^\s/)]+\/(?:commit|pull|issues)\//;
  for(const path of ['SKILL.md','construction.md','architecture.md','counterexamples.md','recurrence.md',
    'review-closeout.md','universalist-composition.md','references/counterexample-guided-normalization.md'])
    assert(!anecdote.test(src[path]) && !repositoryLink.test(src[path]),`repository-specific content: ${path}`);
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
  const simulation=normalized(section(skill,'Simulation-first correctness'));
  for(const rule of ['A law is trace-dependent when its truth depends on one of the properties listed below',
    'A law that depends only on the order of operations on in-memory state is a sequence law; property tests that generate operation sequences check it, wherever the code lives',
    "Each state's pending obligation cites the binding law that creates it; that law is the source law the rest-reachability check protects",
    'durable state: data that outlives the process that wrote it',
    'concurrency: actors such as threads, tasks, processes, or peers',
    'retry, restart, recovery, or replay of an input','time: clocks, deadlines, timeouts, or schedules',
    'external effects whose outcome later behavior depends on',
    'Daemons, runtimes, stores, schedulers, and protocols qualify',
    'Software with none of these, such as a parser, codec, or in-memory data structure, is a pure library',
    'So is a one-shot tool whose effects only fail fast',
    'A tool that resumes, retries, syncs, caches, or keeps a state file is stateful',
    'Classify by these properties, not by repository, language, or size',
    'Input order alone does not establish any of these properties',
    'Reclassify it only when the evidence establishes a listed property that its earlier classification missed',
    'For stateful or concurrent software, the construction includes',
    'every state reaches rest through ordinary inputs',
    'The simulator asserts that every transition it observes is in the table',
    'checks observed membership only; it cannot establish that a declared exit is implemented or its guard can be satisfied',
    'establish that the real code implements the exits and feasible guards on which the reachability check relies',
    'The oracle shares none of the deciding logic it checks',
    'the scheduling of runnable actors','checked against the real service',
    'Control its filesystem or disk seam when source-required faults include lost unsynced writes, torn or reordered writes, or power loss',
    'Keep the real storage implementation above that seam',
    'a process restart with surviving operating system caches does not establish power-loss durability',
    'Running one seed twice yields the same event trace','It checks safety laws after every event',
    'Check required progress under the source-required assumptions about future inputs, dependency availability, recovery, and scheduling fairness',
    'State and realize those premises in the generated continuation',
    'check that the admitted obligations reach rest',
    'A source-permitted wait for approval, a future input, or an unavailable dependency is valid while its progress premise is absent',
    'Also exercise the continuation where that premise holds, so a missing required exit still fails',
    'It pins each failure as its seed and recorded event trace',
    'Pure libraries use property-based tests of their laws',
    'A one-shot tool also injects a failure at every effect seam','only the user can reduce them',
    'a sweep that never produces an event kind the changed code handles is incomplete',
    'When no simulator exists, build the smallest one',
    'keeps its ordinary tests, with property tests for its sequence laws, and runs in the simulator as real code',
    'a seam outside the authorized path scope is a [source-binding](#source-binding) blocker',
    'In `analyze`, classify and judge against these rules without building, extending, or running mutating controls'])
    assert(simulation.includes(rule),`lost simulation rule: ${rule}`);
  // Law coverage is checked against the source binding in both directions, not by
  // handing reviewers the simulator's law inventory.
  for(const rule of ['Every trace-dependent law in the [source binding](#source-binding) is cited by an executable law the simulator checks',
    'and every sequence law by a property test','Every executable law that gates code cites a binding law',
    'a construction-rule assertion also names the [construction rule](#construction-rules) it enforces',
    'also cites the required source law it protects and the conditions under which violating the rule breaks that law',
    'A rule alone grants no gating authority',
    'A binding law without a check is missing required verification',
    'A law that cites no binding law cannot gate the code',
    'Where the accepted source has stable clause identifiers in the repository, make this check executable',
    'Coverage shows that each law is checked, not that its check is adequate',
    'with the same two-way coverage against the binding'])
    assert(simulation.includes(rule),`lost law coverage rule: ${rule}`);
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
  for(const rule of ['extend the applicable property-test generator or oracle to expose recurring families, including operation sequences',
    'Reclassify it only when evidence establishes a listed stateful or concurrent property',
    'recurring sequence findings alone do not establish one',
    "the simulator's for trace-dependent laws and the property tests' for sequence laws",
    'Clean counts do not measure this coverage'])
    assert(plateau.includes(rule),`lost recurrence boundary: ${rule}`);
  assert(normalized(progress).includes('pre-epoch screens and their corrections'));
  for(const rule of [
    'count each candidate-invalidating return from a screen or closed epoch once',
    'Observation-only holds are recovery attempts, not candidate invalidations',
    'A pre-epoch screen counts as no epoch and earns no review credit',
    'each third candidate-invalidating return from a screen or closed review epoch',
    'These are attention thresholds, not proof of stagnation, automatic passage reinjection, a redesign requirement, or round limits'
  ]) assert(normalized(progress).includes(rule),`lost construction-progress boundary: ${rule}`);
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
    'with no epoch open, it triggers no initial evidence barrier',
    'Retain screen findings, holds, and their corrections in the existing [attempt history](recurrence.md#progress-before-another-iteration)',
    'Candidate-invalidating screen returns count toward its construction progress backstop',
    'holds retain their recovery history and applicable causal triggers',
    'Screens open no epoch and do not advance the invalidated-epoch count',
    'An observation-only hold requires recovery, not a successor mutation',
    'Findings already supported by partial inquiry still undergo admission on their own evidence',
    'The screen awards no review credit and replaces no request'])
    assert(screen.includes(rule),`lost screen rule: ${rule}`);
  const screenPolicy=policy.pre_epoch_screen;
  assert.equal(screenPolicy.guidance_ref,'agents/skills/actuating/review-closeout.md#pre-epoch-screen');
  assert.equal(screenPolicy.applies_to,'every-review-epoch');
  assert.equal(screenPolicy.disposition_field,'screen_disposition');
  for(const key of ['records_credit_disposition','awards_review_credit','opens_review_epoch',
    'replaces_initial_inventory_request','finding_triggers_initial_evidence_barrier'])
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
  assert.equal(contract.skill.source_fingerprint,'actuating-construction-core-v47');
  const clauses=Object.fromEntries(contract.clauses.map(c=>[c.clause_id,c]));
  assert(clauses['ACT-IMPLEMENT-ENTRY-001'].success_signals.some(s=>s.includes('without a fixed reasoning sequence')));
  const initial=clauses['ACT-IMPLEMENT-ENTRY-001'];
  assert(initial.success_signals.includes('initial work enters the canonical construction decision directly from the Goal; substantive returns use the same decision without requiring a finding, advance alternative, completed diagnosis, or review dispatch'));
  assert(clauses['ACT-OWNER-FACTS-001'].success_signals.some(s=>s.includes('agent-selected boundaries remain revisable unless the source adopted them')));
  assert(clauses['ACT-LAW-AUTHORITY-001'].success_signals.includes('correctness liability and construction opportunity are decided separately; rejecting an allegation retains independently supported evidence and its premises for authorized selection without importing the rejected requirement or semantic change'));
  assert(clauses['ACT-METANOETIC-ADMISSIBILITY-001'].success_signals.some(s=>s.includes('each third candidate-invalidating return from a screen or closed review epoch')));
  assert(initial.success_signals.includes('primitive meanings and their composition are established under the source-required observation or refinement relation when replacing, combining, reordering, sharing, or removing a construction, including admitted higher-order contexts and required joint observations'));
  assert(initial.success_signals.includes('combined edits check whether one changes a premise used to justify another; affected reasoning is re-established on the assembled construction, while reasoning whose dependencies remain established is reused under existing proof-acceptance rules'));
  assert(initial.failure_signals.includes('combined edits retain justifications whose deciding premises another edit changes, or reopen reasoning whose dependencies remain established solely because edits were combined'));
  assert(initial.failure_signals.includes('matching type names or isolated results alone are credited as interchangeability, or reused reasoning substitutes for required exact-head verification or completion credit'));
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
  assert(sim.success_signals.includes('an observation-only hold requires evidence recovery rather than successor mutation; findings independently supported by partial inquiry still undergo admission on their own evidence'));
  assert(sim.required_artifacts.some(s=>s.startsWith('two-way law coverage')),'lost law coverage artifact');
  assert(sim.required_artifacts.some(s=>s.includes('evidence that real code implements the exits and feasible guards the reachability check relies on')));
  assert(sim.required_artifacts.some(s=>s.includes('a gating construction-rule assertion also cites the required source law and the conditions under which violating the rule breaks that law')));
  assert(sim.failure_signals.some(s=>s.startsWith('a trace-dependent binding law has no executable law')));
  assert(sim.failure_signals.some(s=>s.startsWith('a sequence law is left to indirect simulator generation')),'sequence-law routing lost');
  assert(sim.failure_signals.some(s=>s.startsWith('a lifecycle state holds a pending obligation that cites no binding law')),'obligation citation lost');
  for(const signal of ['recurring sequence-dependent findings alone reclassify pure software as stateful without evidence of a listed stateful or concurrent property',
    'a valid wait is failed or forced to terminate while its source-required progress premise is absent, or the required exit remains unchecked when that premise holds',
    'observed transition membership is treated as proof that a declared exit or its guard is implemented and feasible',
    'a process restart with surviving operating system caches is credited as power-loss durability evidence, or source-required storage faults are left outside simulator control'])
    assert(sim.failure_signals.includes(signal),`lost simulation boundary: ${signal}`);
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
    'Supply the complete control and candidate instructions as accessible files',
    'Preserve its ability to discover the same relationship or choose the same task',
    'Give both arms the same requirements, evidence, suggested repairs, source and theory access',
    'Assignment','Continuation','Fresh context',
    'adequate-incumbent','direct-fix','false-allegation','wrong-oracle',
    'A: accumulated','B: reduced','C: protocol-free',
    'Do not substitute new inputs while relabeling historical receipts and results as a replay','AGENTS.md','compaction','memory',
    'required-valid','Freeze the first completed candidate','timeouts',
    'A tie or insufficient power is inconclusive','no permission for paid model runs']) {
    assert(normalized(comparison).includes(required),`lost comparison control: ${required}`);
  }
  assert.equal(policy.efficacy.comparison_ref,'agents/skills/actuating/tests/construction-comparison.md');
  assert.equal(policy.efficacy.held_out_requires_witness_not_supplied_to_implementing_run,true);
  const simulationComparison=normalized(section(comparison,'Simulation-first construction'));
  for(const control of ['authored, not model-replayed',
    'Supplied construction and review guidance without the construction-rule, simulation-first, re-injection, and pre-epoch-screen bundle being evaluated',
    'informs their revision, not their current force','the implementing run never sees them',
    'Supply the complete accepted requirements to both arms',
    'two-way coverage must flag it before review',
    'Retain all attempts in the denominators',
    'Report simulator construction, seed budget, and CI time separately from per-defect time to first detection',
    'Report simulator, pre-epoch screen, and epoch-review detection separately',
    'A tie or underpowered result is inconclusive','adds no delivery gate or permission for paid model runs'])
    assert(simulationComparison.includes(control),`lost simulation comparison control: ${control}`);
  assert(!/\b\d+ of \d+\b/.test(simulationComparison),'repository-specific comparison evidence');
  const constructionComparison=normalized(section(comparison,'One source-bound construction decision'));
  for(const control of ['authored, not executed',
    "Keep both arms' required verification, immutable review subjects, full inventory, and five-clean gate unchanged",
    'Neither arm receives an extra solution or a deliberately weakened construction assignment',
    'Freeze the first construction, justified no-change decision, or unfinished attempt before later feedback',
    'A correct liability classification does not establish good construction selection',
    'source-contract checks do not execute this comparison or establish model efficacy'])
    assert(constructionComparison.includes(control),`lost construction-decision comparison control: ${control}`);
}

check(sources);
// Deliberate source/contract mutations verify that this test is not a pass-by-default.
// They are not simulations of agent behavior or tests of the causal hypothesis.
const jsonMutation=(path,fn)=>src=>{const value=JSON.parse(src[path]);fn(value);src[path]=JSON.stringify(value)};
const loose=phrase=>new RegExp(phrase.replace(/[.*+?^${}()|[\]\\]/g,'\\$&').replace(/ /g,'\\s+'));
const swap=(path,before,after)=>src=>{src[path]=src[path].replace(loose(before),after);};
const append=(path,text)=>src=>{src[path]+=text;};
const decisionMutation=fn=>jsonMutation('references/decision-contract.json',p=>fn(p.skill_decision_contract.clauses.find(c=>c.clause_id==='ACT-SIMULATION-001')));
const initialMutation=fn=>jsonMutation('references/decision-contract.json',p=>fn(p.skill_decision_contract.clauses.find(c=>c.clause_id==='ACT-IMPLEMENT-ENTRY-001')));
const mutations=[
  ['construction opportunity discarded',swap('construction.md','Rejecting an allegation does not erase independently supported evidence useful to authorized construction','Rejecting an allegation discards every construction opportunity it suggested')],
  ['rejected requirement imported',swap('construction.md','without importing the rejected requirement or semantic change','by importing the rejected requirement and semantic change')],
  ['repetition grants opportunity authority',swap('construction.md','neither repetition nor a preferred design supplies that authority','repetition or a preferred design supplies that authority')],
  ['agent-selected boundary becomes law',swap('construction.md','An agent-selected boundary remains revisable unless the accepted source adopted it','An agent-selected boundary is fixed after it appears in a summary')],
  ['restriction reconsideration expands effects',swap('construction.md','Reconsidering a restriction grants no additional effects or resources','Reconsidering a restriction grants additional effects and resources')],
  ['observation gap forces construction',swap('construction.md','An observation gap calls for evidence recovery, not an assumed construction defect','An observation gap establishes a construction defect requiring repair')],
  ['screen invalidations escape progress',swap('recurrence.md','each third candidate-invalidating return from a screen or closed review epoch','each third closed invalidated review epoch')],
  ['observation holds inflate invalidations',swap('recurrence.md','Observation-only holds are recovery attempts, not candidate invalidations','Observation-only holds are candidate invalidations')],
  ['partial inquiry discards supported findings',swap('review-closeout.md','Findings already supported by partial inquiry still undergo admission on their own evidence','Incomplete inquiry discards every finding it contains')],
  ['canonical decision signal dropped',initialMutation(c=>{c.success_signals=c.success_signals.filter(s=>!s.startsWith('initial work enters the canonical construction decision'));})],
  ['concrete composition trigger lost',swap('construction.md','When replacing, combining, reordering, sharing, or removing a construction','When explicitly asked about composition')],
  ['candidate chooses supported context',swap('construction.md','use the accepted source to determine which inputs, observations, and continuations','use the candidate to determine which inputs, observations, and continuations')],
  ['incumbent observations become requirements',swap('construction.md','Establish the required relationships in the actual admitted environments','Preserve every incumbent observation in the actual admitted environments')],
  ['isolated agreement proves interchangeability',swap('construction.md','matching type names or isolated results alone do not establish interchangeability','matching type names or isolated results establish interchangeability')],
  ['combined edit premises unchecked',swap('construction.md','When combining edits, check whether one changes a premise used to justify another.','')],
  ['affected reasoning left stale',swap('construction.md','Re-establish affected reasoning on the assembled construction','Retain affected reasoning from the separate edits')],
  ['all reasoning reopened',swap('construction.md','reuse reasoning whose dependencies remain established','re-establish all reasoning after every edit')],
  ['reasoning reuse transfers completion credit',swap('construction.md','The existing [proof acceptance](#proof-acceptance) rules still govern required checks and completion credit.','Reused reasoning transfers prior completion credit to the assembled construction.')],
  ['joint observations dropped',swap('construction.md','Preserve required joint observations with shared context','Preserve isolated observations')],
  ['effect occurrence distinction dropped',swap('construction.md','Distinguish a captured value, a fresh effect occurrence, and replay of an acquired response when observable.','')],
  ['concrete composition signal dropped',initialMutation(c=>{c.success_signals=c.success_signals.filter(s=>!s.startsWith('primitive meanings and their composition'));})],
  ['combined premise signal dropped',initialMutation(c=>{c.success_signals=c.success_signals.filter(s=>!s.startsWith('combined edits check'));})],
  ['stale or needless rederivation signal dropped',initialMutation(c=>{c.failure_signals=c.failure_signals.filter(s=>!s.startsWith('combined edits retain'));})],
  ['substituted completion credit signal dropped',initialMutation(c=>{c.failure_signals=c.failure_signals.filter(s=>!s.startsWith('matching type names'));})],
  ['caller dependency reintroduced',src=>{src['../universalist/SKILL.md']+='\nInside Actuating, load its workflow.\n';}],
  ['review weakening',jsonMutation('references/review-contract.json',p=>p.standard_convergence.required_consecutive_clean_attempts=4)],
  ['fixed cross-skill order',jsonMutation('references/review-contract.json',p=>p.construction_selection.metanoetic_before_universalist_when_triggered=true)],
  ['required nomination',jsonMutation('references/review-contract.json',p=>p.universalist_compilation.nomination_result_required=true)],
  ['false efficacy credit',jsonMutation('references/review-contract.json',p=>p.efficacy.policy_unit_tests_prove_model_efficacy=true)],
  ['weakened proof',src=>{src['construction.md']=src['construction.md'].replace('required-valid behavior and observations preserved','optional valid behavior');}],
  ['lost read-only route',src=>{src['SKILL.md']=src['SKILL.md'].replace('It may acquire evidence','It may mutate evidence');}],
  ['lost mathematical capability',swap('construction.md','including `$universalist` for task-relevant semantic','excluding mathematical')],
  ['duplicate acceptance rule',src=>{src['counterexamples.md']+='\nBefore accepting validation for local completion or reviewability\n';}],
  ['baseline instruction leakage unchecked',src=>{src['tests/construction-comparison.md']=src['tests/construction-comparison.md'].replace('`AGENTS.md`','an unspecified file');}],
  ['first candidate unfrozen',src=>{src['tests/construction-comparison.md']=src['tests/construction-comparison.md'].replace('Freeze the first completed candidate','Score the final repaired result');}],
  ['repository history as policy',append('construction.md','\nPROJECTX: this project justified the rule.\n')],
  ['repository commit link',append('references/counterexample-guided-normalization.md','\nSee [abc1234](https://github.com/example/project/commit/abc1234).\n')],
  ['repository history in rationale',decisionMutation(c=>{c.rationale+=' The simulator caught 3 of 4 defects there.';})],
  ['one-way law coverage',swap('construction.md','Every executable law that gates code cites a binding law;','')],
  ['sequence laws uncovered',swap('construction.md',', and every sequence law by a property test','')],
  ['sequence law forced into simulator',swap('construction.md','property tests that generate operation sequences check it, wherever the code lives','the simulator checks it inside stateful software')],
  ['input order makes a law trace-dependent',swap('construction.md','one of the properties listed below','the order or repetition of inputs')],
  ['lifecycle obligation uncited',swap('construction.md',"Each state's pending obligation cites the binding law that creates it; that law is the source law the rest-reachability check protects.",'')],
  ['obligation-citation signal dropped',decisionMutation(c=>{c.failure_signals=c.failure_signals.filter(s=>!s.startsWith('a lifecycle state holds a pending obligation'));})],
  ['coverage gap tolerated',swap('construction.md','A binding law without a check is missing required verification.','A binding law without a check may be covered later.')],
  ['unauthorized law gates code',swap('construction.md','A law that cites no binding law cannot gate the code','A law that cites no binding law may gate the code')],
  ['construction-rule gate lacks source authority',swap('construction.md','also cites the required source law it protects and the conditions under which violating the rule breaks that law','needs only the construction rule it enforces')],
  ['coverage claimed as adequacy',swap('construction.md','Coverage shows that each law is checked, not that its check is adequate','Coverage shows that each check is adequate')],
  ['pure library laws uncovered',swap('construction.md','with the same two-way coverage against the binding, generators','with generators')],
  ['coverage artifact dropped',decisionMutation(c=>{c.required_artifacts=c.required_artifacts.filter(s=>!s.startsWith('two-way law coverage'));})],
  ['missing-law comparison dropped',swap('tests/construction-comparison.md','two-way coverage must flag it before review','reviewers may notice it')],
  ['source requirement withheld',swap('tests/construction-comparison.md','Supply the complete accepted requirements to both arms','Withhold the deciding requirement from both arms')],
  ['screen detection counted as simulation',swap('tests/construction-comparison.md','Report simulator, pre-epoch screen, and epoch-review detection separately','Count screen and simulator detection together')],
  ['simulator made optional',swap('construction.md','the construction includes','the construction may include')],
  ['sweep made optional',swap('construction.md','Record each sweep','The fresh sweep is optional. Record each sweep')],
  ['one-shot tools forced into simulation',swap('construction.md','So is a one-shot tool whose effects only fail fast','So is no one-shot tool, even one whose effects only fail fast')],
  ['pure libraries forced into simulation',swap('construction.md','in-memory data structure, is a pure library','in-memory data structure, is stateful')],
  ['external effects unconditioned',swap('construction.md','external effects whose outcome later behavior depends on','external effects of any kind')],
  ['simulator scope widened past durable state',swap('construction.md','durable state: data that outlives the process that wrote it','retained state: memory that a later operation reads')],
  ['concurrency trigger dropped',swap('construction.md','- concurrency: actors such as threads, tasks, processes, or peers whose interleaving can change an observation;\n','')],
  ['classified by repository',swap('construction.md','Classify by these properties, not by repository, language, or size.','Classify by repository.')],
  ['recurrence alone reclassifies pure code',swap('construction.md','Reclassify it only when the evidence establishes a listed property that its earlier classification missed.','Reclassify it whenever trace-dependent findings recur.')],
  ['scheduler left unowned',swap('construction.md','the scheduling of runnable actors, and','and')],
  ['fakes unchecked',swap('construction.md',', checked against the real service','')],
  ['nondeterministic replay tolerated',swap('construction.md',' Running one seed twice yields the same event trace.','')],
  ['lifecycle table may drift',swap('construction.md','The simulator asserts that every transition it observes is in the table.','')],
  ['table membership proves exits',swap('construction.md','checks observed membership only; it cannot establish that a declared exit is implemented or its guard can be satisfied','proves every declared exit is implemented and its guard can be satisfied')],
  ['lifecycle realization unchecked',swap('construction.md','establish that the real code implements the exits and feasible guards on which the reachability check relies','assume declared exits are implemented')],
  ['progress premises invented',swap('construction.md','source-required assumptions about future inputs, dependency availability, recovery, and scheduling fairness','any assumptions that make the check pass')],
  ['valid wait forced to terminate',swap('construction.md','A source-permitted wait for approval, a future input, or an unavailable dependency is valid while its progress premise is absent','Every wait must terminate after inputs stop')],
  ['progress continuation unchecked',swap('construction.md','Also exercise the continuation where that premise holds, so a missing required exit still fails.','')],
  ['required storage faults uncontrolled',swap('construction.md','Control its filesystem or disk seam when source-required faults include lost unsynced writes, torn or reordered writes, or power loss.','')],
  ['restart credited as power loss',swap('construction.md','a process restart with surviving operating system caches does not establish power-loss durability','a process restart establishes power-loss durability')],
  ['oracle shares deciding logic',swap('construction.md','The oracle shares none of the deciding logic it checks','The oracle may reuse the deciding logic it checks')],
  ['unbounded simulator construction',swap('construction.md','build the smallest one','build a complete one')],
  ['changed helper forced into simulation',swap('construction.md','keeps its ordinary tests, with property tests for its sequence laws, and runs in the simulator as real code','needs its own simulator')],
  ['scope broadened for seams',swap('construction.md','a seam outside the authorized path scope is a [source-binding](#source-binding) blocker, not license to broaden that scope','a seam outside the authorized path scope may be added')],
  ['analyze builds',swap('construction.md','without building, extending, or running mutating controls','and builds what is missing')],
  ['construction rule dropped',swap('construction.md','- Give every admitted input exactly one recorded terminal disposition, such as applied, rejected, superseded, or failed: never none and never two.\n','')],
  ['construction rules promoted to requirements',swap('construction.md','They are construction means, not source requirements','They are source requirements')],
  ['fix lands before re-injection',swap('counterexamples.md','Before a head carrying its fix becomes reviewable or is published','After a head carrying its fix is published')],
  ['scripted replay accepted',swap('counterexamples.md','A scripted replay of the reported trace is not an extension.','')],
  ['outside scope widened',swap('counterexamples.md','Only a defect whose wrong observation is not behavior of the running software','Any defect the current simulator does not reach')],
  ['second re-injection fallback',append('counterexamples.md','\nOnly the user can waive this control.\n')],
  ['plateau check optional',swap('recurrence.md','includes simulator coverage','optionally includes simulator coverage')],
  ['plateau bypasses pure classification',swap('recurrence.md','Reclassify it only when evidence establishes a listed stateful or concurrent property','Reclassify it whenever these findings recur')],
  ['plateau keyed to clean counts',swap('recurrence.md','Clean counts do not measure this coverage.','Rising clean counts establish this coverage.')],
  ['held-screen attempts forgotten',swap('review-closeout.md','Retain screen findings, holds, and their corrections in the existing [attempt history](recurrence.md#progress-before-another-iteration).','Discard screen-only repair history.')],
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
