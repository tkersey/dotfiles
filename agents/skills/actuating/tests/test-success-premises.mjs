#!/usr/bin/env node
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const paths = ['construction.md', 'tests/construction-comparison.md'];
const sources = Object.fromEntries(paths.map(path =>
  [path, readFileSync(resolve(root, path), 'utf8')]));
const normalized = source => source.replace(/\s+/g, ' ');
const section = (source, heading) => {
  assert.equal(source.split('## ' + heading + '\n').length, 2, heading);
  return source.split('## ' + heading + '\n')[1].split('\n## ')[0];
};

const successPremiseBoundaries = [
  ['construction.md', 'Construction Working Set', [
    'For an admitted counterexample',
    'authority, or effect being granted, not merely a successful return',
    'condition the accepted source requires whenever it is granted',
    'the required-valid behavior',
    'every relevant way of granting that success',
    'source-required domain and evidence lifetime',
    'newly introduced shortcuts and permitted continuations that can invalidate its basis',
    'Follow the implicated operations, not unrelated commands',
    'Preserve the requirement, not an obsolete mechanism',
    'reuse adequate native constructions and direct corrections',
    'Retire displaced weaker success decisions without erasing distinct authorities',
    'Carry this assignment, its source, and deciding evidence through selection, delegation, and resumption, including compaction',
    'subtasks do not discharge the enclosing obligation',
    'without a separate packet, stage, or required presentation'
  ]],
  ['tests/construction-comparison.md', 'Success-premise preservation', [
    'authored, not model-replayed',
    '910a9a5193fb57bf31989ee2df1a96c442560322',
    'Do not substitute a pre-cleanup or patch-only control',
    'Hold the implementing model, effective reasoning effort',
    'Different reviewer settings are a separate detection comparison',
    'Freeze the first successor, no-change decision, or unfinished attempt before later review feedback',
    'Preserve all attempts, including refusals, timeouts, and incomplete verification',
    'Supply the already accepted empty-source condition to both arms',
    'withhold concrete later fixtures, not the known requirement',
    'an obsolete fault hook is not a required operation',
    'Distinct source-backed authorities remain distinct',
    'Reject-all, always-redesign, and always-add-checks policies fail calibration',
    'disclosed cases are calibration material, not untouched holdouts',
    'these trials earn no production review credit'
  ]]
];

function checkSuccessPremises(src) {
  for (const [path, heading, boundaries] of successPremiseBoundaries) {
    const body = normalized(section(src[path], heading));
    for (const boundary of boundaries)
      assert(body.includes(boundary), 'lost success-premise boundary: ' + boundary);
  }
}

function checkSuccessPremiseControls(src) {
  checkSuccessPremises(src);
  let controls = 0;
  for (const [path, heading, boundaries] of successPremiseBoundaries) {
    const original = section(src[path], heading);
    for (const boundary of boundaries) {
      const body = normalized(original).replace(boundary, 'REMOVED');
      const mutant = {...src, [path]: src[path].replace(original, body)};
      assert.notEqual(mutant[path], src[path], 'inactive success-premise mutation: ' + boundary);
      assert.throws(() => checkSuccessPremises(mutant), assert.AssertionError,
        'undetected success-premise mutation: ' + boundary);
      controls++;
    }
  }
  return controls;
}

const controls = checkSuccessPremiseControls(sources);
console.log(`actuating: success-premise source contract and ${controls} mutation controls passed; model behavior not evaluated`);
