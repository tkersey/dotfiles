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
assert.equal(fixture.schema, 'actuating-construction-cycle-scenarios/v5');
assert.equal(new Set(fixture.scenarios.map(x => x.id)).size, fixture.scenarios.length);

// Test-only reference model of receipt barriers. It neither runs CAS nor grants
// authority to an agent. Unlike the removed fixture, it has no theorem-equality
// or direct-gate input that can exempt a candidate from proof.
function observe(i) {
  const slots = new Map(), seen = new Set();
  const semantic = r => ['clean', 'findings'].includes(r.verdict);
  const material = r => r.findings?.some(f => f.authority === 'entailed' && f.applicability === 'current');
  const initialComplete = () => lenses.every(l => semantic(slots.get(l)?.at(-1) ?? {}));
  for (const r of i.receipts) {
    assert(!seen.has(r.id), 'duplicate receipt'); seen.add(r.id);
    assert.equal(r.head, i.head, 'stale receipt');
    assert(lenses.includes(r.lens), 'unknown lens');
    assert(['initial', 'confirmation'].includes(r.phase), 'unknown phase');
    assert(['clean', 'findings', 'verdictless'].includes(r.verdict), 'unknown verdict');
    if (r.lens === 'standard') assert.equal(r.custom_instructions, undefined, 'custom standard prompt');
    if (r.phase === 'initial') assert.equal(r.slot, r.lens);
    else {
      assert.equal(r.lens, 'standard');
      assert(initialComplete(), 'confirmation before initial barrier');
      assert(![...slots.values()].flat().some(material), 'confirmation after material finding');
    }
    const history = slots.get(r.slot) ?? [];
    if (history.length) {
      assert.equal(history.at(-1).verdict, 'verdictless', 'duplicate semantic outcome');
      assert(history.length <= policy.transport_recovery.maximum_fresh_recovery_attempts, 'recovery exhausted');
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
  for (const r of i.receipts) if (r.lens === 'standard' && semantic(r))
    cleanStandards = r.verdict === 'clean' ? cleanStandards + 1 : 0;
  if (invalidated) cleanStandards = 0;
  const converged = barrier && !invalidated && folded && sourcesFolded &&
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
  id:`suffix-${n}`, slot:`suffix-${n}`, phase:'confirmation', lens:'standard',
  head:cleanInput.head, verdict,
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
console.log(`actuating: ${fixture.scenarios.length} receipt scenarios and finite family/path/preservation/authority discriminators passed`);
JS
sh "$skill_root/tests/test-composition-contract.sh"
