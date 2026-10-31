#!/usr/bin/env node
// Source-contract and mutation tests only. These do not execute coding agents,
// measure efficacy, or prove the behavior of an implementation produced by a model.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const paths = ['SKILL.md', 'construction.md', 'architecture.md', 'counterexamples.md',
  'agents/openai.yaml', 'references/review-contract.json',
  'references/decision-contract.json', '../universalist/actuating-composition.md',
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
  const adapter=normalized(src['../universalist/actuating-composition.md']);
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
    '1b0b7d96a2434a3fceea83fc34be41db3623450e146913428ec4b355d34fc286','changed construction assignment binding');
  const admissionStart=counter.indexOf('Before counterexample-driven selection,');
  const admissionEnd=counter.indexOf('\n## Compile the first loss of guarantee');
  assert(admissionStart>=0 && admissionEnd>admissionStart);
  assert.equal(hash(counter.slice(admissionStart,admissionEnd)),
    'ecd80ffbd34cb57ba11e83d6b671c73dda6123d4faa4621b43a54ad24435d516','changed witness admission');

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
  assert(src['../universalist/SKILL.md'].includes('Inside Actuating, contribute directly under its adapter'));
  assert(src['../universalist/README.md'].includes("Architectonic's read-only nomination contract is unchanged"));
  assert(counter.includes('[proof acceptance](SKILL.md#proof-acceptance)'));
  const repeated='Before accepting validation for local completion or reviewability';
  assert.equal(skill.split(repeated).length-1,1,'canonical verifier-integrity rule missing or duplicated');
  assert(!counter.includes(repeated),'duplicated verifier-integrity rule');
  assert(normalized(section(skill,'Proof acceptance')).includes('A passing weakened suite cannot discharge an unchanged requirement'));
  assert(normalized(section(skill,'Proof acceptance')).includes('does not demand a finished causal account before authorized exploration'));

  assert.equal(policy.contract_id,'actuating-review-contract-v28');
  assert.equal(policy.construction_selection.reasoning_sequence_required,false);
  assert.equal(policy.construction_selection.metanoetic_before_universalist_when_triggered,false);
  assert.equal(policy.universalist_compilation.nomination_result_required,false);
  assert.equal(policy.universalist_compilation.nomination_is_executed_proof,false);
  assert.equal(policy.efficacy.policy_unit_tests_prove_model_efficacy,false);
  assert.equal(contract.skill.source_fingerprint,'actuating-construction-core-v31');
  const clauses=Object.fromEntries(contract.clauses.map(c=>[c.clause_id,c]));
  assert(clauses['ACT-IMPLEMENT-ENTRY-001'].success_signals.some(s=>s.includes('without a fixed reasoning sequence')));
  assert(clauses['ACT-METANOETIC-ADMISSIBILITY-001'].success_signals.some(s=>s.includes('no required order relative to Universalist')));
  assert(clauses['ACT-UNIVERSALIST-COMPILATION-001'].success_signals.some(s=>s.includes('optional presentation')));
  const routeIds=new Set(contract.routes.map(r=>r.route_id));
  const triggerIds=new Set(contract.triggers.map(t=>t.trigger_id));
  assert.equal(routeIds.size,4); assert.equal(triggerIds.size,5);
  assert.deepEqual(Object.keys(clauses).sort(),["ACT-CLOSURE-001","ACT-CONSTRUCTION-COMPILER-001","ACT-IMPLEMENT-ENTRY-001","ACT-LAW-AUTHORITY-001","ACT-METANOETIC-ADMISSIBILITY-001","ACT-OWNER-FACTS-001","ACT-REVIEW-EPOCH-001","ACT-REVIEW-EVIDENCE-001","ACT-UNIVERSALIST-COMPILATION-001"]);
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
}

check(sources);
// Deliberate source/contract mutations verify that this test is not a pass-by-default.
// They are not simulations of agent behavior or tests of the causal hypothesis.
const jsonMutation=(path,fn)=>src=>{const value=JSON.parse(src[path]);fn(value);src[path]=JSON.stringify(value)};
const mutations=[
  ['review weakening',jsonMutation('references/review-contract.json',p=>p.standard_convergence.required_consecutive_clean_attempts=4)],
  ['fixed cross-skill order',jsonMutation('references/review-contract.json',p=>p.construction_selection.metanoetic_before_universalist_when_triggered=true)],
  ['required nomination',jsonMutation('references/review-contract.json',p=>p.universalist_compilation.nomination_result_required=true)],
  ['false efficacy credit',jsonMutation('references/review-contract.json',p=>p.efficacy.policy_unit_tests_prove_model_efficacy=true)],
  ['weakened proof',src=>{src['construction.md']=src['construction.md'].replace('required-valid behavior and observations preserved','optional valid behavior');}],
  ['lost read-only route',src=>{src['SKILL.md']=src['SKILL.md'].replace('It may acquire evidence','It may mutate evidence');}],
  ['lost mathematical capability',src=>{src['construction.md']=src['construction.md'].replace('including `$universalist` for task-relevant semantic','excluding mathematical');}],
  ['duplicate acceptance rule',src=>{src['counterexamples.md']+='\nBefore accepting validation for local completion or reviewability\n';}],
  ['baseline instruction leakage unchecked',src=>{src['tests/construction-comparison.md']=src['tests/construction-comparison.md'].replace('`AGENTS.md`','an unspecified file');}],
  ['first candidate unfrozen',src=>{src['tests/construction-comparison.md']=src['tests/construction-comparison.md'].replace('Freeze the first completed candidate','Score the final repaired result');}]
];
for(const [name,mutate] of mutations) {
  const mutant={...sources}; mutate(mutant);
  assert.throws(()=>check(mutant),assert.AssertionError,`undetected mutation: ${name}`);
}
console.log(`actuating: reduced-construction source contract and ${mutations.length} mutation controls passed; agent efficacy not evaluated`);
