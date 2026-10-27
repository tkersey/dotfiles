#!/bin/sh
set -eu
skill_root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
node --input-type=module - "$skill_root" <<'JS'
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const root = process.argv[2];
const read = path => JSON.parse(readFileSync(`${root}/${path}`, 'utf8'));
const policy = read('references/review-contract.json');
const fixture = read('tests/fixtures/construction-cycle-scenarios.json');
const lenses = policy.required_lenses.map(x => x.name);
assert.equal(fixture.schema, 'actuating-construction-cycle-scenarios/v6');
assert.equal(new Set(fixture.scenarios.map(x => x.id)).size, fixture.scenarios.length);

// Test-only reference model of receipt barriers. It neither runs CAS nor grants
// authority to an agent. Unlike the removed fixture, it has no theorem-equality
// or direct-gate input that can exempt a candidate from proof.
function observe(i) {
  const slots = new Map(), seen = new Set();
  assert(Array.isArray(i.focused_files), 'missing frozen file selection');
  assert(i.focused_files.length <= policy.focused_file_reviews.maximum_files, 'file review budget exceeded');
  assert.equal(new Set(i.focused_files.map(f => JSON.stringify(f))).size, i.focused_files.length, 'duplicate file selection');
  const initialSlots = new Map(policy.required_lenses.map(({name:lens, role}) =>
    [lens, {scope:'changeset', lens, role, focus:null}]));
  i.focused_files.forEach((focus, n) => policy.required_lenses.forEach(({name:lens, role}) =>
    initialSlots.set(`focused-file-${n}-${lens}`, {scope:'file', lens, role, focus})));
  const semantic = r => ['clean', 'findings'].includes(r.verdict);
  const credited = r => semantic(r) && r.credit_disposition === 'credit';
  const material = r => r.findings?.some(f => f.authority === 'entailed' && f.applicability === 'current');
  const initialComplete = () => [...initialSlots.keys()].every(slot => semantic(slots.get(slot)?.at(-1) ?? {}));
  for (const r of i.receipts) {
    assert(!seen.has(r.id), 'duplicate receipt'); seen.add(r.id);
    assert.equal(r.head, i.head, 'stale receipt');
    assert(lenses.includes(r.lens), 'unknown lens');
    assert(['changeset', 'file'].includes(r.scope), 'unknown scope');
    assert(['initial', 'confirmation'].includes(r.phase), 'unknown phase');
    assert(['clean', 'findings', 'verdictless'].includes(r.verdict), 'unknown verdict');
    if (r.scope === 'changeset' && r.lens === 'standard')
      assert.equal(r.custom_instructions, undefined, 'custom standard prompt');
    if (r.scope === 'file')
      assert.equal(typeof r.custom_instructions, 'string', 'missing file scope instructions');
    if (r.phase === 'initial') {
      const required = initialSlots.get(r.slot);
      assert(required, 'unselected initial request');
      assert.equal(r.scope, required.scope, 'wrong initial review scope');
      assert.equal(r.lens, required.lens, 'wrong initial review lens');
      assert.equal(r.role, required.role, 'wrong initial review role');
      assert.deepEqual(r.focus ?? null, required.focus, 'wrong focal file');
    }
    else {
      assert.equal(r.scope, 'changeset', 'file confirmation forbidden');
      assert.equal(r.lens, 'standard');
      assert.equal(r.role, 'standard');
      assert.equal(r.focus ?? null, null, 'focused confirmation forbidden');
      assert(initialComplete(), 'confirmation before initial barrier');
      assert(![...slots.values()].flat().some(material), 'confirmation after material finding');
      assert([...slots.values()].every(xs => xs.at(-1).slot === r.slot || credited(xs.at(-1))),
        'confirmation before review credit');
    }
    const history = slots.get(r.slot) ?? [];
    if (history.length) {
      assert.equal(history.at(-1).verdict, 'verdictless', 'duplicate semantic outcome');
      assert(history.length <= policy.transport_recovery.maximum_fresh_recovery_attempts, 'recovery exhausted');
      assert.equal(r.custom_instructions, history.at(-1).custom_instructions, 'changed recovery instructions');
    }
    history.push(r); slots.set(r.slot, history);
    if (history.length > policy.transport_recovery.maximum_fresh_recovery_attempts && !semantic(r))
      assert.fail('recovery exhausted without a semantic verdict');
  }
  const last = [...slots.values()].map(xs => xs.at(-1));
  const invalidated = last.some(material);
  const barrier = initialComplete() && last.every(semantic);
  const folded = last.every(r => i.folded.includes(r.id));
  const sourcesFolded = i.sources.every(s => s.status !== 'unfolded');
  const completionSources = i.sources.every(s => !s.required || ['folded', 'non-current'].includes(s.status));
  // Adjudication cannot turn a non-clean owner verdict into clean credit.
  // Verdictless transport attempts are not semantic outcomes; recovery stays
  // in the existing barrier. Count the ordered semantic suffix, not totals.
  let cleanStandards = 0;
  for (const r of i.receipts) if (r.scope === 'changeset' && r.lens === 'standard' && semantic(r))
    cleanStandards = r.verdict === 'clean' ? cleanStandards + Number(credited(r)) : 0;
  if (invalidated) cleanStandards = 0;
  const converged = barrier && last.every(credited) && !invalidated && folded && sourcesFolded &&
    cleanStandards >= policy.standard_convergence.required_consecutive_clean_attempts;
  const cutClosed = invalidated && barrier && folded && sourcesFolded;
  const open = i.receipts.length > 0 && !(cutClosed || converged);
  const mutating = ['implement', 'review-closeout', 'bare'].includes(i.route);
  const proofCurrent = i.proof?.head === i.head && i.proof?.status === 'passed';
  return {
    mutable: mutating && !open && sourcesFolded,
    epoch_open: open,
    complete: ['review-closeout', 'bare'].includes(i.route) && converged && proofCurrent && completionSources,
    may_dispatch: i.route !== 'implement' && proofCurrent && i.receipts.length === 0 && sourcesFolded
  };
}
for (const c of fixture.scenarios) {
  const input = {...fixture.defaults, ...c.input};
  input.receipts = input.receipts.map(ref => {
    assert(Object.hasOwn(fixture.receipt_catalog, ref), `missing receipt ${ref}`);
    return fixture.receipt_catalog[ref];
  });
  if (c.expected === 'invalid-or-blocked') assert.throws(() => observe(input), undefined, c.id);
  else assert.deepEqual(observe(input), c.expected, c.id);
}

// Each terminal outcome is necessary, not just a nonempty fold or a standard-only
// fold. The same condition protects both completion and the frozen epoch.
const cleanCase = fixture.scenarios.find(c => c.id === 'five-standard-cleans-and-all-auxiliaries-complete');
assert(cleanCase);
const cleanInput = {...fixture.defaults, ...cleanCase.input};
cleanInput.receipts = cleanInput.receipts.map(ref => fixture.receipt_catalog[ref]);
for (const receipt of cleanInput.receipts) {
  assert.deepEqual(observe({...cleanInput, folded:cleanInput.folded.filter(id => id !== receipt.id)}),
    {mutable:false, epoch_open:true, complete:false, may_dispatch:false}, `unfolded ${receipt.id}`);
}
// A folded verdictless predecessor cannot stand in for its recovered outcome.
const recovered = {...cleanInput, receipts:cleanInput.receipts.flatMap(r =>
  r.lens === 'fresh-eyes' ? [fixture.receipt_catalog.r13, fixture.receipt_catalog.r14] : [r])};
assert.deepEqual(observe(recovered), {mutable:false, epoch_open:true, complete:false, may_dispatch:false});
assert.equal(observe({...recovered, folded:[...recovered.folded, fixture.receipt_catalog.r14.id]}).complete, true);

// A rejected strengthening breaks the native clean suffix without becoming
// mutation authority. These traces previously completed on five TOTAL cleans.
const initial = cleanInput.receipts.filter(r => r.phase === 'initial');
const confirmation = (n, verdict = 'clean', authority = 'strengthening') => ({
  id:`suffix-${n}`, slot:`suffix-${n}`, phase:'confirmation', scope:'changeset', lens:'standard', role:'standard',
  head:cleanInput.head, verdict, credit_disposition:verdict === 'verdictless' ? 'hold' : 'credit',
  ...(verdict === 'findings' ? {findings:[{authority, applicability:'current'}]} : {})
});
const evaluate = receipts => observe({...cleanInput, receipts, folded:receipts.map(r => r.id)});
for (const authority of ['strengthening','preference']) {
  const prefix = [...initial, confirmation(1), confirmation(2,'findings',authority)];
  for (let count = 0; count <= 5; count++) {
    const receipts = [...prefix, ...Array.from({length:count}, (_,n) => confirmation(n+3))];
    assert.deepEqual(evaluate(receipts),
      {mutable:count === 5, epoch_open:count !== 5, complete:count === 5, may_dispatch:false},
      `${authority}: suffix ${count}, not cumulative clean count`);
  }
}
// An auxiliary non-liability does not interrupt the standard-only suffix.
const auxiliaryFinding = cleanInput.receipts.map(r => r.lens === 'footgun-finder'
  ? {...r, verdict:'findings', findings:[{authority:'preference', applicability:'current'}]} : r);
assert.equal(evaluate(auxiliaryFinding).complete, true);
// A verdictless final confirmation remains pending, then its one fresh semantic
// recovery can complete the existing suffix; it supplies no extra clean itself.
const pending = [...initial, ...[1,2,3].map(n => confirmation(n)), confirmation(4,'verdictless')];
assert.equal(evaluate(pending).complete, false);
assert.equal(evaluate([...pending, {...confirmation(4), id:'suffix-4-recovery'}]).complete, true);
// A material finding invalidates all credit and forbids more confirmations.
const materialCut = [...initial, confirmation(1,'findings','entailed')];
assert.deepEqual(evaluate(materialCut), {mutable:true, epoch_open:false, complete:false, may_dispatch:false});
assert.throws(() => evaluate([...materialCut, confirmation(2)]), /confirmation after material finding/);

const focusedFiles = [
  {base_path:'src/old-a.js', head_path:'src/a.js'},
  {base_path:null, head_path:'src/b.js'},
  {base_path:'src/c.js', head_path:null}
];
const fileReceipts = focusedFiles.flatMap((focus, n) => policy.required_lenses.map(({name:lens, role}) => ({
  id:`file-${n}-${lens}`, slot:`focused-file-${n}-${lens}`, phase:'initial', scope:'file', lens, role,
  head:cleanInput.head, verdict:'clean', credit_disposition:'credit', focus, custom_instructions:JSON.stringify({focus, lens})
})));
const evaluateFiles = receipts => observe({...cleanInput, focused_files:focusedFiles,
  receipts, folded:receipts.map(r => r.id)});
const focusedInitial = [...initial, ...fileReceipts];
const focusedClean = [...focusedInitial, ...[1,2,3,4].map(n => confirmation(n))];
assert.equal(focusedInitial.length, 24);
assert.equal(focusedClean.length, 28);
assert.equal(evaluateFiles(focusedClean).complete, true);
for (let count = 0; count < 4; count++)
  assert.equal(evaluateFiles([...focusedInitial, ...Array.from({length:count}, (_, n) => confirmation(n+1))]).complete,
    false, `file standards cannot replace whole-changeset confirmation ${count+1}`);
const invalidInitial = initial.map(r => r.lens === 'standard' ? fixture.receipt_catalog.r01 : r);
for (const omitted of fileReceipts) {
  const partial = focusedInitial.filter(r => r.id !== omitted.id);
  assert.deepEqual(evaluateFiles(partial), {mutable:false, epoch_open:true, complete:false, may_dispatch:false});
  assert.throws(() => evaluateFiles([...partial, confirmation(1)]), /confirmation before initial barrier/);
  assert.deepEqual(evaluateFiles([...invalidInitial, ...fileReceipts.filter(r => r.id !== omitted.id)]),
    {mutable:false, epoch_open:true, complete:false, may_dispatch:false});
  assert.equal(observe({...cleanInput, focused_files:focusedFiles, receipts:focusedClean,
    folded:focusedClean.filter(r => r.id !== omitted.id).map(r => r.id)}).complete, false);
}
assert.deepEqual(evaluateFiles(invalidInitial), {mutable:false, epoch_open:true, complete:false, may_dispatch:false});
assert.deepEqual(evaluateFiles([...invalidInitial, ...fileReceipts]),
  {mutable:true, epoch_open:false, complete:false, may_dispatch:false});
for (const authority of ['strengthening', 'preference']) {
  const nonmaterial = focusedClean.map(r => r.scope === 'file' && r.lens === 'standard'
    ? {...r, verdict:'findings', findings:[{authority, applicability:'current'}]} : r);
  assert.equal(evaluateFiles(nonmaterial).complete, true, `${authority}: file standard does not reset native suffix`);
}
const fileMaterial = focusedInitial.map(r => r.id === fileReceipts[0].id
  ? {...r, verdict:'findings', findings:[{authority:'entailed', applicability:'current'}]} : r);
assert.deepEqual(evaluateFiles(fileMaterial), {mutable:true, epoch_open:false, complete:false, may_dispatch:false});
assert.throws(() => evaluateFiles([...fileMaterial, confirmation(1)]), /confirmation after material finding/);
const fileRecovery = focusedInitial.map(r => r.id === fileReceipts[0].id ? {...r, verdict:'verdictless'} : r);
assert.equal(evaluateFiles(fileRecovery).epoch_open, true);
const recoveredFile = {...fileReceipts[0], id:'file-0-standard-recovery'};
assert.equal(evaluateFiles([...fileRecovery, recoveredFile,
  ...[1,2,3,4].map(n => confirmation(n))]).complete, true);
assert.throws(() => evaluateFiles([...fileRecovery, {...recoveredFile, verdict:'verdictless'}]), /recovery exhausted/);
assert.throws(() => evaluateFiles([...fileRecovery, {...recoveredFile, custom_instructions:'different scope prompt'}]),
  /changed recovery instructions/);
const invalidRecovery = [...invalidInitial, ...fileRecovery.filter(r => r.scope === 'file')];
assert.equal(evaluateFiles(invalidRecovery).epoch_open, true);
assert.deepEqual(evaluateFiles([...invalidRecovery, recoveredFile]),
  {mutable:true, epoch_open:false, complete:false, may_dispatch:false});
for (const [delta, error] of [
  [{focus:focusedFiles[1]}, /wrong focal file/],
  [{focus:{...focusedFiles[0], base_path:'src/unrelated.js'}}, /wrong focal file/],
  [{lens:'footgun-finder', role:'auxiliary'}, /wrong initial review lens/],
  [{role:'auxiliary'}, /wrong initial review role/],
  [{scope:'changeset', custom_instructions:undefined, focus:null}, /wrong initial review scope/],
  [{scope:undefined}, /unknown scope/],
  [{head:'h0'}, /stale receipt/],
  [{custom_instructions:undefined}, /missing file scope instructions/]
]) {
  assert.throws(() => evaluateFiles([...initial, {...fileReceipts[0], ...delta}, ...fileReceipts.slice(1)]), error);
  assert.throws(() => evaluateFiles([...fileRecovery, {...recoveredFile, ...delta}]), error);
}
assert.throws(() => evaluateFiles([...focusedInitial,
  {...fileReceipts[0], id:'file-confirmation', slot:'file-confirmation', phase:'confirmation'}]), /file confirmation forbidden/);
assert.throws(() => observe({...cleanInput, focused_files:[...focusedFiles,
  {base_path:'src/d.js', head_path:'src/d.js'}]}), /file review budget exceeded/);

for (const receipt of focusedInitial) for (const credit_disposition of ['hold', undefined]) {
  const held = focusedInitial.map(r => r.id === receipt.id ? {...r, credit_disposition} : r);
  assert.deepEqual(evaluateFiles(held), {mutable:false, epoch_open:true, complete:false, may_dispatch:false});
  assert.throws(() => evaluateFiles([...held, confirmation(1)]), /confirmation before review credit/,
    `${receipt.lens}: ${credit_disposition ?? 'absent'}`);
  const restored = held.map(r => r.id === receipt.id ? {...r, credit_disposition:'credit'} : r);
  assert.equal(evaluateFiles([...restored, ...[1,2,3,4].map(n => confirmation(n))]).complete, true);
}
for (const n of [1,2,3,4]) for (const credit_disposition of ['hold', undefined]) {
  const held = [...focusedInitial, ...Array.from({length:n-1}, (_,i) => confirmation(i+1)),
    {...confirmation(n), credit_disposition}];
  assert.deepEqual(evaluateFiles(held), {mutable:false, epoch_open:true, complete:false, may_dispatch:false});
  assert.throws(() => evaluateFiles([...held, confirmation(n+1)]), /confirmation before review credit/);
  const restored = [...held.slice(0,-1), confirmation(n),
    ...Array.from({length:4-n}, (_,i) => confirmation(n+i+1))];
  assert.equal(evaluateFiles(restored).complete, true);
}
const uncreditedInvalidated = [...invalidInitial, ...fileReceipts].map(r => ({...r, credit_disposition:'hold'}));
assert.deepEqual(evaluateFiles(uncreditedInvalidated),
  {mutable:true, epoch_open:false, complete:false, may_dispatch:false});

// Executable finite discriminator: a guard for the observed enum case misses
// a sum/product sibling. An independent inhabitant enumerator also prevents the
// reject-all shortcut. These are illustrative constructions, NOT a model A/B run.
const E = n => ({kind:'enum', n}), S = xs => ({kind:'sum', xs});
const P = xs => ({kind:'product', xs}), A = (x,n) => ({kind:'array', x,n});
function cardinality(s) {
  switch (s.kind) {
    case 'enum': return s.n;
    case 'sum': return s.xs.reduce((n,x) => n + cardinality(x), 0);
    case 'product': return s.xs.reduce((n,x) => n * cardinality(x), 1);
    case 'array': return cardinality(s.x) ** s.n;
    default: throw Error('unknown schema');
  }
}
function inhabitants(s) {
  const product = sets => sets.reduce((rows,set) => rows.flatMap(row => set.map(x => [...row,x])), [[]]);
  switch (s.kind) {
    case 'enum': return Array.from({length:s.n}, (_,i) => i);
    case 'sum': return s.xs.flatMap((x,tag) => inhabitants(x).map(value => ({tag,value})));
    case 'product': return product(s.xs.map(inhabitants));
    case 'array': return product(Array.from({length:s.n}, () => inhabitants(s.x)));
    default: throw Error('unknown schema');
  }
}
const domain = [E(0),E(1),E(2),S([]),P([]),S([E(0),E(1)]),P([E(0),E(2)]),A(E(0),0),A(E(0),2)];
const enumPatch = s => !(s.kind === 'enum' && s.n === 0);
assert.equal(enumPatch(E(0)), false); // observed example passes
assert.equal(enumPatch(S([])), true); // sibling still fails
for (const s of domain) assert.equal(cardinality(s), inhabitants(s).length);
assert.equal(cardinality(A(E(0),0)), 1); // required-valid empty array survives
assert.equal(cardinality(P([E(0),E(2)])), 0);

// Derive the domain from a concrete graph, not from the candidate's declared
// dispositions. A new public producer must fail even when labeled restoration.
function verifyCut(graph, dispositions, cut, producers, consumer) {
  assert.deepEqual(Object.keys(dispositions).sort(), Object.keys(graph).sort(), 'omitted source element');
  for (const edges of Object.values(graph)) for (const to of edges) assert(Object.hasOwn(graph,to));
  for (const start of producers) {
    const seen = new Set(), pending = [start];
    while (pending.length) {
      const n = pending.pop();
      if (n === cut || seen.has(n)) continue;
      assert.notEqual(n, consumer, 'trusted consumer reachable around cut');
      seen.add(n); pending.push(...graph[n]);
    }
  }
}
const graph = {producer:['admit'],admit:['consume'],consume:[]};
const dispositions = {producer:'factor-through',admit:'owner',consume:'consumer'};
verifyCut(graph,dispositions,'admit',['producer'],'consume');
const bypass = {...graph,alternate:['consume']};
assert.throws(() => verifyCut(bypass,dispositions,'admit',['producer','alternate'],'consume'), /omitted/);
assert.throws(() => verifyCut(bypass,{...dispositions,alternate:'factor-through'},'admit',['producer','alternate'],'consume'), /around cut/);
verifyCut({...graph,alternate:['admit']},{...dispositions,alternate:'factor-through'},'admit',['producer','alternate'],'consume');

// Every producer can cross admission while its predicate proves an easier law.
// Checking all supplied attempt/capture pairs does not detect their joint
// omission. These finite facts are authoritative independently of the archive;
// this example makes no completeness claim beyond those retained roots.
const occurrenceIds = ['first','second'];
const selectedIds = mask => occurrenceIds.filter((_,i) => mask & (1 << i));
const suppliedPairsAgree = archive =>
  archive.attempts.every(id => archive.captures.includes(id)) &&
  archive.captures.every(id => archive.attempts.includes(id));
const completeEvidence = (facts,archive) => suppliedPairsAgree(archive) &&
  facts.filter(fact => fact.required).every(fact =>
    archive.attempts.includes(fact.id) && archive.captures.includes(fact.id));
const requiredFacts = occurrenceIds.map(id => ({id,required:true}));
const jointOmission = {attempts:['first'],captures:['first']};
assert(suppliedPairsAgree(jointOmission)); // the selected invariant still holds
assert(!completeEvidence(requiredFacts,jointOmission)); // the source law fails
for (let required = 0; required < 4; required++)
  for (let attempts = 0; attempts < 4; attempts++)
    for (let captures = 0; captures < 4; captures++) {
      const facts = occurrenceIds.map((id,i) => ({id,required:Boolean(required & (1 << i))}));
      const archive = {attempts:selectedIds(attempts),captures:selectedIds(captures)};
      // Independent bitset oracle covers all 64 states of this finite domain.
      const expected = attempts === captures && (attempts & required) === required;
      assert.equal(completeEvidence(facts,archive), expected);
    }
// Absence of optional evidence is valid; demanding a pair for every occurrence
// would fix the omission example by silently strengthening the requirement.
assert(completeEvidence([{id:'first',required:true},{id:'second',required:false}],jointOmission));
assert(completeEvidence(requiredFacts.map(fact => ({...fact,required:false})),{attempts:[],captures:[]}));

// A covered admission path can still lose its guarantee through a writable
// alias. These concrete scalar-range constructions test that distinction, not
// model effectiveness or a universal theorem about JavaScript objects.
const temporalGraph = {producer:['admit'], admit:['mutate'], mutate:['consume'], consume:[]};
verifyCut(temporalGraph,
  {producer:'factor-through', admit:'owner', mutate:'transition', consume:'consumer'},
  'admit', ['producer'], 'consume');
const validRange = r => Number.isSafeInteger(r.bounds.start) && Number.isSafeInteger(r.bounds.end) &&
  r.bounds.start <= r.bounds.end && r.length === r.bounds.end - r.bounds.start;
const rawRange = (start,end) => ({bounds:{start,end}, length:end-start});
const admitAlias = raw => { assert(validRange(raw)); return raw; };
const raw = rawRange(1,3), admittedAlias = admitAlias(raw);
assert(validRange(admittedAlias));
raw.bounds.end = 4; // valid bounds, but the admitted length is now stale
assert(!validRange(admittedAlias));
const shallowRaw = rawRange(1,3), shallow = Object.freeze({...admitAlias(shallowRaw)});
shallowRaw.bounds.start = 0; // freezing only the wrapper keeps the same cause
assert(!validRange(shallow));

// Own the admitted scalar snapshot and derive the correlated fact. No generic
// deep-freeze helper, repeated consumer validation, or caller-authored length.
function admitOwned(raw) {
  const {start,end} = raw.bounds;
  assert(Number.isSafeInteger(start) && Number.isSafeInteger(end) && start <= end);
  assert(Number.isSafeInteger(end-start));
  return Object.freeze({bounds:Object.freeze({start,end}), length:end-start});
}
const observeRange = r => [r.bounds.start, r.bounds.end, r.length];
const shiftRange = (r,delta) => admitOwned({bounds:{start:r.bounds.start+delta, end:r.bounds.end+delta}});
for (const [start,end] of [[0,0],[0,2],[1,3]]) {
  const source = rawRange(start,end), owned = admitOwned(source);
  assert.deepEqual(observeRange(owned), [start,end,end-start]); // required-valid observations
  assert.deepEqual(observeRange(admitOwned({...source, length:999})), observeRange(owned));
  source.bounds.end += 1;
  source.bounds.start -= 1; // a sibling operation, not another production case
  source.length = -1;
  assert(validRange(owned));
  assert.deepEqual(observeRange(owned), [start,end,end-start]);
  assert.throws(() => { owned.bounds.end += 1; }, TypeError);
  assert.throws(() => { owned.length = -1; }, TypeError);
  for (const delta of [-1,0,1]) {
    const shifted = shiftRange(owned,delta);
    assert(validRange(shifted));
    assert.deepEqual(observeRange(shifted), [start+delta,end+delta,end-start]);
  }
}
assert.throws(() => admitOwned({bounds:{start:2,end:1}}));
assert.throws(() => admitOwned({bounds:{start:NaN,end:1}}));

// A rejected review strengthening cannot ride along with an authorized repair.
// Compare actual field deltas, not a batch's preferred response label.
function verifyDelta(before, after, authority) {
  for (const key of new Set([...Object.keys(before), ...Object.keys(after)]))
    if (before[key] !== after[key]) assert(authority.has(key), `unauthorized delta: ${key}`);
}
const before = {evidenceSource:'caller', streaming:'unchanged'};
const correction = {evidenceSource:'executor', streaming:'unchanged'};
verifyDelta(before, correction, new Set(['evidenceSource']));
assert.throws(() => verifyDelta(before, {...correction, streaming:'new-requirement'}, new Set(['evidenceSource'])), /unauthorized/);
verifyDelta(before, {...correction, streaming:'new-requirement'}, new Set(['evidenceSource','streaming']));
console.log(`actuating: ${fixture.scenarios.length} receipt scenarios and finite family/path/content/preservation/authority discriminators passed`);
JS
sh "$skill_root/tests/test-composition-contract.sh"
