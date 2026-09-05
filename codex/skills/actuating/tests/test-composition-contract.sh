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
  "Review and closure": "9e9bf083b07812cb0cb2675d223bc94554fb51cfeecc1f1b7b3ff9edd0752225",
  "Realization and common proof obligations": "df2f70beac4ca71c55ca4e4bc8c6f63c23453aafe8ef7406102832f658055ad8"
};
for (const [name, digest] of Object.entries(protectedSections))
  assert.equal(sha256(section(skill,name)),digest,`protected Actuating section: ${name}`);
const lensBlobs = {
  'soundness-review.md':'58949402e604ee35a2454e64e98532a82825cde4',
  'footgun-review.md':'00d80db3e5f94cc5365594c059c65ec27b737db4',
  'invariant-review.md':'275cc488e082c493463c846ed47ec211ea3565d9',
  'complexity-review.md':'d92f5244415343c9b6bb27c10f09cf991f74bf69',
  'fresh-eyes-review.md':'e927acc958eae56c5ef5f7a0e42697162a114e71'
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
for (const path of ['SKILL.md','references/architecture-reconciliation.md',
  '../universalist/SKILL.md','../universalist/README.md']) {
  const source = text(path);
  for (const result of nominationResults) assert(source.includes(result),`${path}: missing ${result}`);
}
const universalist = section(text('../universalist/SKILL.md'),'Actuating composition');
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
