#!/bin/sh
set -eu
skill_root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
node --input-type=module - "$skill_root" <<'JS'
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
const root = process.argv[2];
const text = path => readFileSync(resolve(root,path),'utf8');
const section = (s, heading) => {
  assert(s.includes(`## ${heading}\n`), `missing section: ${heading}`);
  return s.split(`## ${heading}\n`)[1].split('\n## ')[0];
};
const sha256 = s => createHash('sha256').update(s).digest('hex');
const canonical = v => Array.isArray(v) ? v.map(canonical) : v && typeof v === 'object'
  ? Object.fromEntries(Object.keys(v).sort().map(k => [k,canonical(v[k])])) : v;
const policy = JSON.parse(text('references/review-contract.json'));
// Protect the accepted review process, not just one count or flag. These
// identities are pinned to the audited policy at a6499e818910; intentional
// policy changes must explicitly update these regression expectations.
const reviewKeys = ["required_lenses", "review_scheduling", "candidate_lifecycle", "review_epoch", "review_entry", "evidence_acquisition", "standard_convergence", "material_change", "transport_recovery", "attempt_quality"];
assert.equal(sha256(JSON.stringify(canonical(Object.fromEntries(reviewKeys.map(k => [k,policy[k]]))))),
  '7a45af557a2c21095e49146d8458990fa3b0ecc87c59f11f2b65a653a2104545', 'review process changed');
const skill = text('SKILL.md');
const protectedSections = {
  "Public routes": "8e2aec586fe33dfc69d573c15a9fdc425547bf8bdf8c4952e5f0fbdd8fb6c222",
  "Review-epoch immutability and evidence acquisition": "1db48d44444f7f346820393de4305a42da9da7e3f4a2ea1acce4563a3867aed4",
  // #300 adds explicit evidence admission without changing review quotas.
  "Review and closure": "a577a29c392abf9ca61f3bb06f958ba03dbf0688b1564b42ce99a48a324256bb",
  "Realization and common proof obligations": "df2f70beac4ca71c55ca4e4bc8c6f63c23453aafe8ef7406102832f658055ad8"
};
// Relocation changes where the section is read, not its accepted bytes.
const protectedSources = {
  "Review-epoch immutability and evidence acquisition": text('review-closeout.md'),
  "Review and closure": text('review-closeout.md')
};
assert(skill.includes('[review-closeout.md](review-closeout.md)'), 'review guide not routed');
for (const [name, digest] of Object.entries(protectedSections))
  assert.equal(sha256(section(protectedSources[name] ?? skill,name)),digest,`protected Actuating section: ${name}`);
// #300 separates no-findings verdicts from validation completeness in all five lenses.
// Pin that intentional correction while retaining every lens search instruction.
const lensBlobs = {
  'soundness-review.md':'bcc7632af93e1d24ac9ad90806eac4a3f152a195',
  'footgun-review.md':'5e03cc4edeb5566fcf18a5f84022d22441de0ba2',
  'invariant-review.md':'0aaf1e6a7ec7a5b79d0b546db82ff0768d5bfcd0',
  'complexity-review.md':'2d0d3e05b49623ccb1435bbe1220009fe06de38e',
  'fresh-eyes-review.md':'29d68a33492533184d103204a586ec3cc7e4800f'
};
for (const [name, digest] of Object.entries(lensBlobs)) {
  const bytes = Buffer.from(text(`references/lenses/${name}`));
  assert.equal(createHash('sha1').update(`blob ${bytes.length}\0`).update(bytes).digest('hex'),
    digest,`review instruction bytes changed: ${name}`);
}
// Source-contract checks below validate the declared handoffs. They do not
// simulate an agent, execute Ledger/CAS, or prove model effectiveness.
const nominationResults = ['candidate','preserve-incumbent','unresolved','obstructed'];
assert.deepEqual(policy.universalist_compilation.allowed_nomination_results,nominationResults);
for (const path of ['SKILL.md',
  '../universalist/SKILL.md','../universalist/README.md']) {
  const source = text(path);
  for (const result of nominationResults) assert(source.includes(result),`${path}: missing ${result}`);
}
assert(text('../universalist/SKILL.md').includes('[actuating-composition.md](actuating-composition.md)'), 'composition guide not routed');
const universalist = section(text('../universalist/actuating-composition.md'),'Actuating composition');
assert.match(universalist,/Return `unresolved` when evidence is missing or adequate candidates remain\s+incomparable/);
assert.match(universalist,/not a new route or mode/);
const fold = text('../review-fold/SKILL.md');
const corpus = text('../review-fold/references/counterexample-corpus.md');
assert.match(fold,/corpus_write_authorized: true \| false # enclosing task; omitted means false/);
assert.match(section(fold,'Effect authority'),/always false in\s+Actuating `analyze`/);
assert.match(section(fold,'Procedure'),/When `corpus_write_authorized` is true, capture/);
assert.match(section(corpus,'Capture after folding'),/corpus_write_authorized = true/);
assert.match(section(corpus,'Effect authority'),/not `ledger transact`/);
assert.match(skill,/corpus_write_authorized: false/);
for (const name of ['challenged_judgment','earliest_failed_premise','claim_strength_consequence'])
  assert(fold.includes(name),`lost judgment-challenge field: ${name}`);
assert.match(fold,/Missing proof alone is not evidence that the behavior is false/);
assert.match(fold,/never rewrites\s+an owner-issued `findings` verdict into `clean`/);
const visibility = text('../cas/references/review-proof-boundary.md');
assert.match(visibility,/does not deliver the hashed context or prove that a reviewer saw it/);
assert.match(visibility,/parent-only conversation premises are not implicitly inherited/);
assert.match(visibility,/adds no context packet, prompt argument, review gate, attempt/);
for (const [name,lens] of Object.entries({
  'invariant-ace':'invariant','footgun-finder':'footgun','complexity-mitigator':'complexity'
})) {
  const composition = section(text(`../${name}/SKILL.md`),'Actuating composition');
  assert(composition.includes(`../actuating/references/lenses/${lens}-review.md`),name);
  assert.match(composition,/takes precedence over/,name);
  assert.match(composition,/unchanged/,name);
}
assert.match(section(text('../invariant-ace/SKILL.md'),'Actuating composition'),/Do not launch authority fanout/);
assert(!text('../complexity-mitigator/SKILL.md').includes('complexity_evidence:'), 'duplicate composition table');
assert.match(text('references/closure.md'),/\.\.\/SKILL\.md#realization-and-common-proof-obligations/);
console.log('actuating: composition source contracts, unchanged modes, review policy, proof bar, and exact lens bytes passed');
JS
node "$skill_root/../review-fold/tests/test-counterexample-admission.mjs"
node "$skill_root/tests/test-auxiliary-discovery.mjs"
