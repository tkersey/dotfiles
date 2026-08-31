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
