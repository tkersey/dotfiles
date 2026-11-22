import assert from 'node:assert/strict';
import {mkdtempSync, readFileSync, writeFileSync, readdirSync, rmSync, existsSync, symlinkSync, realpathSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {test} from 'node:test';
import {preparePair, assessPair} from './codec-handoff-fixture.mjs';
import {programs} from '../../actuating/tests/review-action-fixture.mjs';

const cli = fileURLToPath(new URL('./codec-handoff-fixture.mjs', import.meta.url));
const passed = arm => arm.artifact_assessment.observations.filter(item => item.pass).length;

function inputs(t, checkpoint = programs.repaired, report = 'none') {
  const root = mkdtempSync(resolve(realpathSync(tmpdir()), 'codec-handoff-'));
  t.after(() => rmSync(root, {recursive: true, force: true}));
  const checkpointFile = resolve(root, 'checkpoint.mjs');
  const summaries = [resolve(root, 'left.md'), resolve(root, 'right.md')];
  writeFileSync(checkpointFile, checkpoint);
  writeFileSync(summaries[0], 'Résumé 🔁\r\nContinue from the available source.\n');
  writeFileSync(summaries[1], 'Read the source and complete the task.\n');
  return {root, directory: resolve(root, 'subjects'), program: 'original', goal: 'distinct', report, checkpointFile, summaries};
}

test('both subjects receive one checkpoint and equal source access; only actual summary bytes differ', t => {
  const options = inputs(t);
  const record = preparePair(options);
  const [left, right] = record.arms.map(arm => arm.directory);
  assert.deepEqual(readdirSync(left), readdirSync(right));
  for (const name of readdirSync(left)) {
    const a = readFileSync(resolve(left, name));
    const b = readFileSync(resolve(right, name));
    if (name === 'HANDOFF.md') assert.notDeepEqual(a, b);
    else assert.deepEqual(a, b, name);
  }
  record.arms.forEach((arm, index) => assert.deepEqual(
    readFileSync(resolve(arm.directory, 'HANDOFF.md')), readFileSync(options.summaries[index])
  ));
  assert.deepEqual(readFileSync(resolve(left, 'codec.mjs')), readFileSync(options.checkpointFile));
  assert.deepEqual(readFileSync(resolve(left, 'CHECKPOINT.mjs')), readFileSync(options.checkpointFile));
  assert.equal(existsSync(resolve(left, 'review.md')), false);
  assert.equal(existsSync(resolve(left, 'record.json')), false);
  assert.equal(readFileSync(resolve(left, 'RESUME.md'), 'utf8').includes('12/12'), false);
});

test('a valid no-change checkpoint remains admissible and observations do not grade behavior', t => {
  const record = preparePair(inputs(t));
  const result = assessPair(record);
  assert.equal(result.comparison_valid, true);
  assert.equal(result.behavioral_judgment, 'not_automated');
  for (const arm of result.arms) {
    assert.equal(passed(arm), 12);
    assert.equal(arm.artifact_assessment.artifact_pass, true);
    assert.equal(arm.changed_since_checkpoint, false);
  }
  for (const field of ['complete', 'qualified', 'better', 'latency_ms']) assert.equal(Object.hasOwn(result, field), false);
});

test('a regression and its later repair are observed against the same original contract', t => {
  const record = preparePair(inputs(t, programs.zeroLoss, 'plain'));
  const before = assessPair(record);
  assert.equal(before.comparison_valid, true);
  assert.deepEqual(before.arms.map(passed), [10, 10]);
  assert.equal(before.arms[0].artifact_assessment.artifact_pass, false);
  for (const arm of record.arms) writeFileSync(resolve(arm.directory, 'codec.mjs'), programs.repaired);
  const after = assessPair(record);
  assert.equal(after.comparison_valid, true);
  assert.deepEqual(after.arms.map(passed), [12, 12]);
  assert.ok(after.arms.every(arm => arm.changed_since_checkpoint));
  assert.deepEqual(before.arms.map(arm => arm.artifact_assessment.goal_sha256), after.arms.map(arm => arm.artifact_assessment.goal_sha256));
});

test('a different valid wire representation is accepted', t => {
  const record = preparePair(inputs(t));
  const alternate = `export function encode(value) {
    return !Object.hasOwn(value, 'timeout') ? 'i' : value.timeout === null ? 'x' : String(value.timeout);
  }
  export function decode(bytes) {
    return bytes === 'i' ? {} : {timeout: bytes === 'x' ? null : Number(bytes)};
  }\n`;
  writeFileSync(resolve(record.arms[1].directory, 'codec.mjs'), alternate);
  const result = assessPair(record);
  assert.equal(result.comparison_valid, true);
  assert.deepEqual(result.arms.map(passed), [12, 12]);
});

test('changes to fixed evidence invalidate the comparison independently of codec behavior', t => {
  const record = preparePair(inputs(t));
  const dir = record.arms[0].directory;
  for (const name of ['HANDOFF.md', 'CHECKPOINT.mjs', 'RESUME.md', 'GOAL.md', 'TASK.md', 'smoke.test.mjs', 'review.md']) {
    const path = resolve(dir, name);
    const previous = existsSync(path) ? readFileSync(path) : null;
    writeFileSync(path, 'changed\n');
    const result = assessPair(record);
    assert.equal(result.comparison_valid, false, name);
    assert.ok(result.integrity_errors.some(error => error.includes(name)), name);
    assert.equal(result.arms[0].assessment, 'not_run_integrity', name);
    assert.equal(result.arms[0].artifact_assessment, null, name);
    if (previous === null) rmSync(path); else writeFileSync(path, previous);
  }
});

test('malformed records, swapped subjects and changed selectors cannot redirect assessment', t => {
  const record = preparePair(inputs(t));
  const mutations = [
    r => { r.version = 2; },
    r => { r.program = 'repaired'; },
    r => { r.goal = 'coalesced'; },
    r => { r.report = {}; },
    r => { r.fixture_sha256 = '0'.repeat(64); },
    r => { r.checkpoint_sha256 = 'bad'; },
    r => { r.arms.reverse(); },
    r => { r.arms[1].directory = r.arms[0].directory; },
    r => { r.arms[0].handoff_bytes = -1; }
  ];
  for (const mutate of mutations) {
    const changed = structuredClone(record);
    mutate(changed);
    assert.throws(() => assessPair(changed));
  }
  writeFileSync(resolve(record.arms[0].directory, 'record.json'), JSON.stringify({...record, goal: 'coalesced'}));
  assert.equal(assessPair(record).comparison_valid, true);
});

test('preparation validates inputs first and never overwrites an existing destination', t => {
  const options = inputs(t);
  assert.throws(() => preparePair({...options, goal: 'unknown'}));
  assert.equal(existsSync(options.directory), false);
  assert.throws(() => preparePair({...options, summaries: [options.summaries[0], resolve(options.root, 'missing')]}));
  assert.equal(existsSync(options.directory), false);
  preparePair(options);
  const path = resolve(options.directory, 'a', 'codec.mjs');
  writeFileSync(path, 'owned work');
  assert.throws(() => preparePair(options));
  assert.equal(readFileSync(path, 'utf8'), 'owned work');
});

test('symlinked input, candidate and subject directory are rejected', t => {
  const options = inputs(t);
  const link = resolve(options.root, 'summary-link');
  symlinkSync(options.summaries[0], link);
  assert.throws(() => preparePair({...options, summaries: [link, options.summaries[1]]}));
  const record = preparePair(options);
  const candidate = resolve(record.arms[0].directory, 'codec.mjs');
  rmSync(candidate);
  symlinkSync(options.checkpointFile, candidate);
  assert.throws(() => assessPair(record));
  rmSync(record.arms[0].directory, {recursive: true});
  symlinkSync(record.arms[1].directory, record.arms[0].directory, 'dir');
  assert.throws(() => assessPair(record));
});

test('both successors are frozen before either assessment can modify its sibling', t => {
  const record = preparePair(inputs(t, programs.zeroLoss));
  const rewritten = `import {writeFileSync} from 'node:fs';\nwriteFileSync(new URL('../unexpected-execution', import.meta.url), 'ran');\n${programs.repaired}`;
  writeFileSync(resolve(record.arms[0].directory, 'codec.mjs'),
    `import {writeFileSync} from 'node:fs';\nwriteFileSync(new URL('../b/codec.mjs', import.meta.url), ${JSON.stringify(rewritten)});\n${programs.repaired}`);
  const result = assessPair(record);
  assert.equal(passed(result.arms[0]), 12);
  assert.equal(result.comparison_valid, false);
  assert.ok(result.integrity_errors.includes('b: frozen successor changed during assessment'));
  assert.equal(result.arms[1].assessment, 'not_run_integrity');
  assert.equal(result.arms[1].artifact_assessment, null);
  assert.equal(existsSync(resolve(record.directory, 'unexpected-execution')), false);
});

test('changes to the other subject evidence during execution are retained', t => {
  const record = preparePair(inputs(t));
  writeFileSync(resolve(record.arms[0].directory, 'codec.mjs'),
    `import {writeFileSync} from 'node:fs';\nwriteFileSync(new URL('../b/HANDOFF.md', import.meta.url), 'replaced');\n${programs.repaired}`);
  const result = assessPair(record);
  assert.equal(result.comparison_valid, false);
  assert.ok(result.integrity_errors.includes('b: changed HANDOFF.md'));
});

test('unavailable executions remain unavailable', t => {
  const record = preparePair(inputs(t));
  writeFileSync(resolve(record.arms[0].directory, 'codec.mjs'), 'while (true) {}');
  const result = assessPair(record, {timeout: 5000});
  assert.equal(result.arms[0].artifact_assessment.execution, 'unavailable');
  assert.equal(result.arms[0].artifact_assessment.artifact_pass, false);
  assert.equal(result.behavioral_judgment, 'not_automated');
  assert.equal(passed(result.arms[1]), 12);
});

test('CLI round-trips the evaluator-held record and rejects a subject-local record', t => {
  const options = inputs(t);
  const prepared = spawnSync(process.execPath, [cli, 'prepare', options.directory, options.program,
    options.goal, options.report, options.checkpointFile, ...options.summaries], {encoding: 'utf8'});
  assert.equal(prepared.status, 0, prepared.stderr);
  const record = JSON.parse(prepared.stdout);
  const outside = resolve(options.root, 'pair.json');
  writeFileSync(outside, prepared.stdout);
  const assessed = spawnSync(process.execPath, [cli, 'assess', outside], {encoding: 'utf8'});
  assert.equal(assessed.status, 0, assessed.stderr);
  assert.equal(JSON.parse(assessed.stdout).behavioral_judgment, 'not_automated');
  const inside = resolve(record.arms[0].directory, 'record.json');
  writeFileSync(inside, prepared.stdout);
  const invalid = spawnSync(process.execPath, [cli, 'assess', inside], {encoding: 'utf8'});
  assert.equal(invalid.status, 2);
  assert.match(invalid.stderr, /outside both subjects/);
  writeFileSync(resolve(record.arms[0].directory, 'codec.mjs'), programs.zeroLoss);
  assert.equal(spawnSync(process.execPath, [cli, 'assess', outside]).status, 1);
  writeFileSync(resolve(record.arms[0].directory, 'HANDOFF.md'), 'changed');
  assert.equal(spawnSync(process.execPath, [cli, 'assess', outside]).status, 2);
});
