#!/bin/sh
set -eu
skill_root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
node --input-type=module - "$skill_root" <<'JS'
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
const root = process.argv[2];
const text = path => readFileSync(resolve(root,path),'utf8');
const section = (s, heading) => {
  assert(s.includes(`## ${heading}\n`), `missing section: ${heading}`);
  return s.split(`## ${heading}\n`)[1].split('\n## ')[0];
};
const sha256 = s => createHash('sha256').update(s).digest('hex');
const policy = JSON.parse(text('references/review-contract.json'));
const skill = text('SKILL.md');
const protectedSections = {
  "Review-epoch immutability and evidence acquisition": "c56ab6cd715441dce8a7b7eb659e450254d840e548eac57de7f4a65ea5bd4e05",
  "Review and closure": "f3f5c48880509207ad1b049403babf5cafa0fce63003f323c118837ddd063a17",
  // Apply the same proof bar to initial construction; witnesses are conditional.
  "Realization and common proof obligations": "8f782e151a2c48cca2da1506830376ad597b689fde6985014f30c466f87be6e3"
};
// Native executor naming changes; the freeze, credit, count, and proof laws remain intact.
const protectedSources = {
  "Realization and common proof obligations": text('construction.md'),
  "Review-epoch immutability and evidence acquisition": text('review-closeout.md'),
  "Review and closure": text('review-closeout.md')
};
assert(skill.includes('[review-closeout.md](review-closeout.md)'), 'review guide not routed');
for (const [name, digest] of Object.entries(protectedSections))
  assert.equal(sha256(section(protectedSources[name] ?? skill,name)),digest,`protected Actuating section: ${name}`);
// Preserve the lens bytes at d3f24e515059f6517cf238084ef084a55fff2242, except
// for the authorized verbatim transfer of the standalone Fresh Eyes doctrine
// into its auxiliary lens. All other review instructions remain unchanged.
const lensBlobs = {
  'soundness-review.md':'404d8a90ce66cd056de57b1171518e5a1b169975',
  'footgun-review.md':'1a8c3a133077a9d8e36a234687464564ad5f4180',
  'invariant-review.md':'523881241875cddae1512dfd23f1bd3a9faf2dd1',
  'complexity-review.md':'aa213ce128a1a5d6efecd15b4e4d42349cb1c320',
  'fresh-eyes-review.md':'9e22e998e392ae5912d45188104a8afc98666dca'
};
for (const [name, digest] of Object.entries(lensBlobs)) {
  const bytes = Buffer.from(text(`references/lenses/${name}`));
  assert.equal(createHash('sha1').update(`blob ${bytes.length}\0`).update(bytes).digest('hex'),
    digest,`review instruction bytes changed: ${name}`);
}
// Historical examples remain available techniques, not mandatory derivation steps.
{
  const guide = text('references/counterexample-guided-normalization.md').replace(/\s+/g, ' ');
  assert(guide.includes('### Derive the missing premise at its owner'));
  assert(guide.includes('[owner examples](#derive-the-missing-premise-at-its-owner)'));
  assert(guide.includes('try self.persist(value, previous, "task.cancel"); errdefer self.store().fence();'));
  assert(guide.includes('Swallowed errors, other scopes, and process crashes are not covered by this rule'));
  assert(guide.includes('Transaction-scoped import/audit views still validate without minting reusable committed-state facts'));
  assert(guide.includes('Snapshot lifetime and invalidation remain obligations'));
  assert(guide.includes('Zero ancestry bytes alone cannot distinguish reuse from bypassing the cache'));
  assert(guide.includes('not native runs performed by reading this guide or untouched evidence of skill efficacy'));
}
// The reduced construction contract is checked by test-construction-core.mjs.
// Source-contract checks below validate the declared handoffs. They do not
// simulate an agent, execute Ledger/Codex, or prove model effectiveness.
const nominationResults = ['candidate','preserve-incumbent','unresolved','obstructed'];
assert.deepEqual(policy.universalist_compilation.allowed_nomination_results,nominationResults);
for (const path of ['SKILL.md',
  '../universalist/SKILL.md','../universalist/README.md']) {
  const source = text(path);
  for (const result of nominationResults) assert(source.includes(result),`${path}: missing ${result}`);
}
assert(text('../universalist/SKILL.md').includes('[actuating-composition.md](actuating-composition.md)'), 'composition guide not routed');
const universalist = section(text('../universalist/actuating-composition.md'),'Actuating composition');
assert.match(universalist,/Missing evidence or incomparable\s+adequate candidates remain unresolved/);
assert.equal(policy.universalist_compilation.nomination_result_required,false);
assert.match(universalist,/not required output or a new route or mode/);
const fold = text('../review-fold/SKILL.md');
const admission = text('../review-fold/references/admission.md');
const corpus = text('../review-fold/references/counterexample-corpus.md');
assert.match(fold,/corpus_write_authorized: true \| false # enclosing task; omitted means false/);
assert.match(section(fold,'Effect authority'),/always false in\s+Actuating `analyze`/);
assert.match(section(fold,'Procedure'),/When `corpus_write_authorized` is true, capture/);
assert.match(section(corpus,'Capture after folding'),/corpus_write_authorized = true/);
assert.match(section(corpus,'Effect authority'),/not\s+`ledger transact --operation capture`/);
assert.match(skill,/corpus_write_authorized: false/);
for (const name of ['challenged_judgment','earliest_failed_premise','claim_strength_consequence'])
  assert(fold.includes(name),`lost judgment-challenge field: ${name}`);
assert(fold.includes('(references/admission.md#law-authority-classification)'));
assert.match(admission,/Missing proof alone is not evidence that the behavior is false/);
assert.match(admission,/never rewrites\s+an owner-issued `findings` verdict into `clean`/);
const visibility = text('../cas/references/review-proof-boundary.md');
assert.match(visibility,/does not deliver the hashed context or prove that a reviewer saw it/);
assert.match(visibility,/parent-only conversation premises are not implicitly inherited/);
assert.match(visibility,/adds no context packet, prompt argument,\s+review gate, attempt/);
const lensPrefix = 'agents/skills/actuating/';
for (const {name,instructions_ref} of policy.required_lenses.filter(lens => lens.role === 'auxiliary')) {
  assert(instructions_ref.startsWith(`${lensPrefix}references/lenses/`),`${name}: auxiliary source must belong to Actuating`);
  assert(text(instructions_ref.slice(lensPrefix.length)).trim(),`${name}: empty review instructions`);
}
const freshEyes = text('references/lenses/fresh-eyes-review.md');
const outputBoundary = '\n## Native output (Actuating only)\n';
assert.equal(freshEyes.split(outputBoundary).length,2,'Fresh Eyes must have one semantic/output boundary');
const freshEyesDoctrine = 'Once again, check over everything again with fresh eyes looking for any blunders, mistakes, errors, oversights, omissions, problems, misconceptions, bugs, etc. Be SUPER thorough and meticulous!';
assert(freshEyes.split(outputBoundary)[0].includes(`\n\n${freshEyesDoctrine}\n\n`),
  'the verbatim Fresh Eyes doctrine must reach both Actuating and Elenctic semantic review inputs');
assert.match(text('references/closure.md'),/\.\.\/SKILL\.md#realization-and-common-proof-obligations/);
console.log('actuating: composition source contracts, native review policy, proof bar, and exact lens bytes passed');
JS
node "$skill_root/tests/test-instruction-routing.mjs"
node "$skill_root/tests/test-construction-core.mjs"
node "$skill_root/../review-fold/tests/test-counterexample-admission.mjs"
node "$skill_root/tests/test-auxiliary-discovery.mjs"
