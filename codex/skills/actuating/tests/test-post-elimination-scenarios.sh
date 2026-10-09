#!/bin/sh
set -eu
skill_root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
node --input-type=module - "$skill_root" <<'JS'
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const fixture = JSON.parse(readFileSync(`${process.argv[2]}/tests/fixtures/post-elimination-scenarios.json`, 'utf8'));
assert.equal(fixture.schema, 'actuating-post-elimination-scenarios/v3');
function claimDisposition(w) {
  if (['preference','strengthening'].includes(w.authority)) return 'not-applicable';
  if (w.authority !== 'entailed') return 'authority-required';
  if (w.subject_head !== w.current_head || w.horizon === 'outside' ||
      ['same-law-different-family','different-law'].includes(w.relation) || w.admitted === false)
    return 'not-applicable';
  if (w.relation !== 'same-claim' || w.horizon !== 'inside' || w.admitted !== true ||
      !Number.isFinite(w.value)) return 'unknown';
  return w.value <= 0 ? 'revoked' : 'not-applicable';
}
for (const c of fixture.scenarios) assert.equal(claimDisposition(c.witness), c.expected, c.id);

// Reissue is checked against actual executable candidates and an independently
// fixed finite source domain, not a same-theorem assertion or a repair label.
const candidates = {'positive': x => x > 0, 'not-zero': x => x !== 0, 'reject-all': () => false};
// A scoped claim may remain true while the broader source law still needs work.
// Here a second operation retains the independently chosen weaker predicate;
// a shared construction can resolve it without falsely revoking the first claim.
const perOperation = {artifact:candidates.positive,result:candidates['not-zero']};
const preservesLaw = accept => fixture.source_domain.every(x => accept(x) === (x > 0));
assert(preservesLaw(perOperation.artifact));
assert(!preservesLaw(perOperation.result));
const sibling = -1;
assert(perOperation.result(sibling));
const scopedWitness = fixture.scenarios.find(c => c.id === 'different-family-does-not-falsify-this-claim').witness;
assert.equal(claimDisposition({...scopedWitness,value:sibling}), 'not-applicable');
const sharedConstruction = {artifact:candidates.positive,result:candidates.positive};
assert(Object.values(sharedConstruction).every(preservesLaw));

for (const c of fixture.reissue_scenarios) {
  const accept = candidates[c.candidate]; assert(accept, c.id);
  const behaviorCorrect = c.domain.every(x => accept(x) === (x > 0));
  const coversSource = JSON.stringify([...new Set(c.domain)].sort((a,b)=>a-b)) === JSON.stringify(fixture.source_domain);
  const result = !behaviorCorrect ? 'failed' :
    c.strength === 'exhaustive-finite' ? (coversSource ? 'eliminated' : 'failed') : 'bounded';
  assert.equal(result, c.expected, c.id);
}
assert.equal(new Set([...fixture.scenarios,...fixture.reissue_scenarios].map(c => c.id)).size,
  fixture.scenarios.length + fixture.reissue_scenarios.length);
console.log(`actuating: ${fixture.scenarios.length} revocation scenarios and ${fixture.reissue_scenarios.length} executable reissue cases passed`);
JS
