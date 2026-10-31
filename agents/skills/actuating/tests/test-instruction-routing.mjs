#!/usr/bin/env node
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const paths = ['SKILL.md', 'construction.md', 'agents/openai.yaml',
  'review-closeout.md', 'references/review-contract.md',
  'references/review-contract.json', 'references/closure.md', 'recurrence.md',
  '../universalist/references/claim-appropriate-proof.md',
  'tests/construction-comparison.md'];
const sources = Object.fromEntries(paths.map(path =>
  [path, readFileSync(resolve(root, path), 'utf8')]));
const hash = source => createHash('sha256').update(source).digest('hex');
const blob = source => createHash('sha1')
  .update('blob ' + Buffer.byteLength(source)).update(Buffer.from([0]))
  .update(source).digest('hex');
const normalized = source => source.replace(/\s+/g, ' ');
const section = (source, heading) => {
  assert.equal(source.split('## ' + heading + '\n').length, 2, heading);
  return source.split('## ' + heading + '\n')[1].split('\n## ')[0];
};
const coreHashes = {
  'Source binding': 'a08472adfb58b7540f832680acac69f92a87e7ee8e4086c9621134194aa4639d',
  'Initial construction': '914abbef7bedd3589e278ca02dfa7bc66a5fffa406b3efded52baff4ce01fbfa',
  'Proof acceptance': '9ce927daa4b505028355f061ca6d457269a9e6c4f2252047351ecec2f455031c',
  'Comments in code': '9dfab826dd63fbdd4ac448cbf0d7c690edef00145282604d9f0737c39edc39bf',
  'Realization and common proof obligations': '8f782e151a2c48cca2da1506830376ad597b689fde6985014f30c466f87be6e3',
  'Construction Working Set': '1b0b7d96a2434a3fceea83fc34be41db3623450e146913428ec4b355d34fc286',
  'Completion': 'dc56a54f2fd79d07f4d801b030cbf5b5a1ec6758be7a8c72eae0e8c2f630f58f'
};
const reviewHashes = {
  "Binding and owner authority": "2e9edaa0e078b9a777b67a43f1886377478a79dd2cb5c6b733af68aefe2fa15a",
  "Focused file reviews": "582c39e1d407d87381c8024231f41a0e3097b458308495eb3c61a1b62ad8b4b7",
  "Review-credit admission": "e86ce67f5abed7dd8427a7191117fb2c41288ae53a9be247a410a4aeb456768e",
  "Candidate lifecycle and causal response": "a887cf18ee794184cb80e1319500a0af833f94cd8031182f0de3a6af28718bdd",
  "Falsification and resumption": "17f87445bb36ab41373998afa14ac9a27667a9931103b04112d58ebd5989c591",
  "Lens ownership and evaluation": "dfae71b906890431a76b08118a70af3e022c69928c3b356869cd6f4e4cb62d95"
};
const closureHash = "d45edd0daf0d8c7ad7d852409b3f2c6c1d61e59cdfaf7eaaae2da93761b6e73d";

function checkPremiseIntegration(src) {
  const reference = '../universalist/references/claim-appropriate-proof.md';
  for (const [path, owner, target] of [
    ['construction.md', 'Proof acceptance', 'Claim-directed correspondence'],
    ['recurrence.md', 'Progress before another iteration', 'Premise-guided investigation']
  ]) {
    const anchor = target.toLowerCase().replaceAll(' ', '-');
    assert(section(src[path], owner).includes('](' + reference + '#' + anchor + ')'),
      'missing conditional integration: ' + path);
    assert(section(src[reference], target).trim(), 'missing canonical method: ' + target);
  }
  const investigation = normalized(section(src[reference], 'Premise-guided investigation'));
  assert(investigation.includes('without manufacturing doubt') &&
    investigation.includes('or a probe quota'), 'lost canonical investigation proportionality');
  const comparison = normalized(section(src['tests/construction-comparison.md'],
    'Premise-guided Actuating integration'));
  for (const control of ['authored, not model-replayed',
    '8df45b596459cd3d3d51ec3a3aefd0be99072055',
    'Both arms retain the same Universalist methods', 'fresh undisclosed task instances',
    'Freeze the first candidate, no-change decision, or unfinished attempt',
    'all attempts retained in the denominators', 'same correctness bar',
    'earn no production review credit'])
    assert(comparison.includes(control), 'lost integration comparison control: ' + control);
}

function check(src) {
  checkPremiseIntegration(src);
  const entry = src['SKILL.md'];
  const core = src['construction.md'];
  const review = src['references/review-contract.md'];
  const routes = normalized(section(entry, 'Public routes'));
  const metadata = src['agents/openai.yaml'];
  for (const [heading, digest] of Object.entries(coreHashes)) {
    assert.equal(hash(section(core, heading)), digest, heading);
    assert(!entry.includes('## ' + heading + '\n'), 'duplicated owner: ' + heading);
    const anchor = heading.toLowerCase().replaceAll(' ', '-');
    assert(entry.includes('<a id="' + anchor + '"></a>'), 'missing compatibility anchor: ' + anchor);
    assert(entry.includes('(construction.md#' + anchor + ')'), 'unrouted owner: ' + anchor);
  }
  for (const [heading, digest] of Object.entries(reviewHashes))
    assert.equal(hash(section(review, heading)), digest, heading);
  assert.equal(blob(src['review-closeout.md']), '776aee88aff2e4428d50ae32b0dc9fa2838dda4d');
  assert.equal(blob(src['references/review-contract.json']), '9119a8d8b362d729f5905af061b4aed700bfb8a0');
  const complete = src['references/closure.md'].split('For full `complete`, require:\n\n```text\n')[1];
  assert(complete, 'missing terminal contract');
  assert.equal(hash(complete.split('\n```')[0]), closureHash);
  for (const row of [
    '| Bare `$actuating` or `/goal $actuating` | implement -> Ship -> review-closeout | Explicitly authorized | `complete` |',
    '| `$actuating implement` | compile and realize locally | Explicitly authorized | local `complete` |',
    '| `$actuating analyze` | deepest honest read-only construction judgment | Forbidden | construction, incomparability, containment, or obstruction |',
    '| `$actuating review-closeout` | falsify, realize successors, Ship, converge | Explicitly authorized | `complete` |'
  ]) assert(routes.includes(row), 'lost route: ' + row);
  for (const boundary of [
    'An unqualified review, inspect, audit, classify, or analyze request selects `analyze`',
    'It may acquire evidence about an existing candidate but cannot mutate, publish, grant closure credit, or claim completion',
    'Mutation requires explicit implement, fix, resolve, address, or closeout intent',
    'It dispatches no review and requires no review receipt, counterexample, or initial falsification wave',
    'Implicit selection makes this skill available; it does not authorize mutation, publication, or a broader route',
    'A local fix stays local unless publication is authorized',
    'Mentioning this skill as the subject of a question is not a bare invocation',
    'Explicit bare invocation retains the end-to-end route above',
    'Review executor or scheduling selection alone neither dispatches review for `implement` nor enlarges `analyze` authority'
  ]) assert(routes.includes(boundary), 'lost authority boundary: ' + boundary);
  assert(entry.includes('corpus_write_authorized: false'));
  for (const path of ['construction.md', 'counterexamples.md', 'architecture.md',
    'verification.md', 'recurrence.md', 'review-closeout.md', 'references/closure.md'])
    assert(entry.includes('](' + path + ')'), 'unrouted guide: ' + path);
  assert(normalized(entry).includes('Do not load every guide at entry'));
  assert(section(review, 'Review epoch').includes('../review-closeout.md#review-epoch-immutability-and-evidence-acquisition'));
  assert(section(review, 'Source-derived coverage and preservation').includes('not as another mandatory review pass'));
  assert(section(review, 'Scheduling').includes('`parallel-reviews` is the default'));
  assert(metadata.includes('allow_implicit_invocation: true'));
  const prompt = JSON.parse(metadata.split('  default_prompt: ')[1].trim());
  assert.equal(prompt, 'Use $actuating for the requested task. Follow the selected route and completion boundary in SKILL.md.');
}

check(sources);
const mutations = [
  ['correspondence link lost', 'construction.md', '#claim-directed-correspondence)', '#missing-correspondence)'],
  ['premise link lost', 'recurrence.md', '#premise-guided-investigation)', '#missing-investigation)'],
  ['canonical method missing', '../universalist/references/claim-appropriate-proof.md', '## Premise-guided investigation\n', '## Missing method\n'],
  ['mandatory investigation introduced', '../universalist/references/claim-appropriate-proof.md', 'without manufacturing doubt', 'with mandatory investigation'],
  ['shared baseline removed', 'tests/construction-comparison.md', 'Both arms retain the same Universalist methods', 'Only the candidate receives the Universalist methods'],
  ['incomplete runs discarded', 'tests/construction-comparison.md', 'all attempts retained in the denominators', 'only successful attempts retained in the denominators'],
  ['lost verification', 'construction.md', 'Every required check must finish', 'An optional check may finish'],
  ['lost required-valid behavior', 'construction.md', 'required-valid behavior and observations preserved', 'optional valid behavior'],
  ['broken owner link', 'SKILL.md', '(construction.md#proof-acceptance)', '(construction.md#missing)'],
  ['lost read-only boundary', 'SKILL.md', 'It may acquire evidence', 'It may mutate evidence'],
  ['implicit publication', 'SKILL.md', 'it does not authorize mutation', 'it authorizes mutation'],
  ['local route widened', 'SKILL.md', 'local `complete`', 'published `complete`'],
  ['corpus capture authorized', 'SKILL.md', 'corpus_write_authorized: false', 'corpus_write_authorized: true'],
  ['implicit discovery disabled', 'agents/openai.yaml', 'allow_implicit_invocation: true', 'allow_implicit_invocation: false'],
  ['review count weakened', 'references/review-contract.json', '"required_consecutive_clean_attempts": 5', '"required_consecutive_clean_attempts": 4'],
  ['freeze removed', 'review-closeout.md', 'forbid successor mutation', 'allow successor mutation'],
  ['credit weakened', 'references/review-contract.md', 'including for historical receipts; do not infer adequacy', 'including for historical receipts; infer adequacy'],
  ['terminal proof weakened', 'references/closure.md', 'every required check finished successfully', 'some required checks finished successfully']
];
for (const [name, path, before, after] of mutations) {
  assert(sources[path].includes(before), 'inactive mutation: ' + name);
  const changed = {...sources, [path]: sources[path].replace(before, after)};
  assert.throws(() => check(changed), assert.AssertionError, 'undetected mutation: ' + name);
}
console.log('actuating: instruction routing, preserved contracts, and ' + mutations.length + ' mutation controls passed; model behavior not evaluated');
