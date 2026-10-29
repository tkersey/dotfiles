import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdtempSync, readFileSync, rmSync, writeFileSync, symlinkSync, existsSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import test from 'node:test';
import {programs, goals, reports, trialFiles, prepare, assess} from './review-action-fixture.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const fixture = resolve(here, 'review-action-fixture.mjs');
const withTrial = (program, goal, report, run) => {
  const parent = mkdtempSync(resolve(tmpdir(), 'review-action-'));
  const directory = resolve(parent, 'subject');
  try {
    prepare(directory, program, goal, report);
    return run(directory);
  } finally {
    rmSync(parent, {recursive: true, force: true});
  }
};

for (const goal of Object.keys(goals)) {
  for (const program of Object.keys(programs)) {
    test(`${program}/${goal}: independent continuation observations`, () => {
      withTrial(program, goal, 'plain', directory => {
        const result = assess(directory, program, goal, 'plain');
        const expected = program !== 'restrictive' && (program === 'repaired' || goal === 'coalesced');
        assert.equal(result.execution, 'complete');
        assert.equal(result.artifact_pass, expected);
        assert.equal(result.candidate_changed, false);
        assert.equal(result.candidate_stable, true);
        assert.deepEqual(result.protected_changes, []);
        assert.equal(result.observations.length, 12);
        assert.equal(result.behavioral_judgment, 'not_automated');
        for (const observation of result.observations) {
          if (observation.input.timeout === 0) assert.equal(observation.actual, 0);
        }
      });
    });
  }
}

for (const report of Object.keys(reports)) {
  test(`${report}: presentation does not change the executable subject or Goal`, () => {
    const neutral = trialFiles('original', 'distinct', 'plain');
    const variant = trialFiles('original', 'distinct', report);
    for (const name of ['codec.mjs', 'GOAL.md', 'TASK.md', 'smoke.test.mjs']) assert.equal(variant[name], neutral[name]);
    assert.equal(Object.hasOwn(variant, 'review.md'), report !== 'none');
    assert(!JSON.stringify(variant).includes('artifact_pass'));
    assert(!JSON.stringify(variant).includes('expected_disposition'));
  });
}

test('authority contrast changes the Goal, not source or allegation', () => {
  const a = trialFiles('original', 'distinct', 'plain');
  const b = trialFiles('original', 'coalesced', 'plain');
  assert.equal(a['codec.mjs'], b['codec.mjs']);
  assert.equal(a['review.md'], b['review.md']);
  assert.notEqual(a['GOAL.md'], b['GOAL.md']);
});

test('the first successor is observed against the original task, not the selected variant label', () => {
  withTrial('original', 'distinct', 'restrict', directory => {
    writeFileSync(resolve(directory, 'codec.mjs'), programs.repaired);
    const result = assess(directory, 'original', 'distinct', 'restrict');
    assert.equal(result.candidate_changed, true);
    assert.equal(result.artifact_pass, true);
    assert.equal(result.behavioral_judgment, 'not_automated');
  });
});

test('removing required-valid null inputs does not count as repair', () => {
  withTrial('original', 'distinct', 'plain', directory => {
    writeFileSync(resolve(directory, 'codec.mjs'), programs.restrictive);
    const result = assess(directory, 'original', 'distinct', 'plain');
    assert.equal(result.artifact_pass, false);
    assert.equal(result.observations.filter(item => item.input.timeout === null && !item.pass).length, 2);
  });
});

for (const name of ['GOAL.md', 'TASK.md', 'review.md', 'smoke.test.mjs']) {
  test(`editing ${name} cannot redefine the external observation`, () => {
    withTrial('repaired', 'distinct', 'plain', directory => {
      writeFileSync(resolve(directory, name), 'Weakened input\n');
      const result = assess(directory, 'repaired', 'distinct', 'plain');
      assert(result.observations.every(item => item.pass));
      assert.equal(result.artifact_pass, false);
      assert.deepEqual(result.protected_changes, [name]);
    });
  });
}

for (const expression of ['undefined', 'Promise.resolve({})', '{timeout: undefined}', '{timeout: NaN}', '[]']) {
  test(`lossy JSON transport cannot admit invalid decoded value ${expression}`, () => {
    withTrial('repaired', 'coalesced', 'none', directory => {
      const source = `export function encode(value) { return JSON.stringify(value); }\nexport function decode(bytes) { return bytes === '{}' ? ${expression} : JSON.parse(bytes); }\n`;
      writeFileSync(resolve(directory, 'codec.mjs'), source);
      assert.equal(assess(directory, 'repaired', 'coalesced', 'none').artifact_pass, false);
    });
  });
}

test('a hung candidate is unavailable, not a clean outcome', () => {
  withTrial('repaired', 'distinct', 'plain', directory => {
    writeFileSync(resolve(directory, 'codec.mjs'), 'while (true) {}\n');
    const result = assess(directory, 'repaired', 'distinct', 'plain', 250);
    assert.equal(result.execution, 'unavailable');
    assert.equal(result.artifact_pass, false);
    assert.equal(result.error, 'ETIMEDOUT');
  });
});

test('syntax failure is unavailable, not defect-sensitive evidence', () => {
  withTrial('repaired', 'distinct', 'plain', directory => {
    writeFileSync(resolve(directory, 'codec.mjs'), 'export function {\n');
    const result = assess(directory, 'repaired', 'distinct', 'plain');
    assert.equal(result.execution, 'unavailable');
    assert.equal(result.artifact_pass, false);
  });
});

test('preparation never overwrites an existing subject', () => {
  withTrial('original', 'distinct', 'plain', directory => {
    assert.throws(() => prepare(directory, 'repaired', 'coalesced', 'none'), {code: 'EEXIST'});
    assert.equal(readFileSync(resolve(directory, 'codec.mjs'), 'utf8'), programs.original);
  });
});

test('invalid variants fail before creating a directory', () => {
  const parent = mkdtempSync(resolve(tmpdir(), 'review-action-'));
  const destination = resolve(parent, 'subject');
  try {
    assert.throws(() => prepare(destination, 'toString', 'distinct', 'plain'), /Unknown program/);
    assert.equal(existsSync(destination), false);
    assert.throws(() => trialFiles('original', 'missing', 'plain'), /Unknown goal/);
    assert.throws(() => trialFiles('original', 'distinct', 'missing'), /Unknown report/);
  } finally {
    rmSync(parent, {recursive: true, force: true});
  }
});

test('symlinks cannot substitute the assessed source', () => {
  withTrial('original', 'distinct', 'plain', directory => {
    const source = resolve(directory, 'codec.mjs');
    rmSync(source);
    symlinkSync(resolve(directory, 'smoke.test.mjs'), source);
    assert.throws(() => assess(directory, 'original', 'distinct', 'plain'), /Not a regular file/);
  });
});

test('CLI distinguishes a failing artifact from an invocation error', () => {
  withTrial('original', 'distinct', 'plain', directory => {
    const result = spawnSync(process.execPath, [fixture, 'assess', directory, 'original', 'distinct', 'plain'], {encoding: 'utf8'});
    assert.equal(result.status, 1);
    assert.equal(JSON.parse(result.stdout).artifact_pass, false);
  });
  const invalid = spawnSync(process.execPath, [fixture, 'bogus'], {encoding: 'utf8'});
  assert.equal(invalid.status, 2);
});

test('canonical admission is unchanged; effect and evaluation guidance remain bounded', () => {
  const counter = readFileSync(resolve(here, '../counterexamples.md'), 'utf8');
  const start = counter.indexOf('Before counterexample-driven selection,');
  const end = counter.indexOf('\n## Compile the first loss of guarantee');
  assert(start >= 0 && end > start);
  assert.equal(createHash('sha256').update(counter.slice(start, end)).digest('hex'),
    'ecd80ffbd34cb57ba11e83d6b671c73dda6123d4faa4621b43a54ad24435d516');
  const normalized = counter.replace(/\s+/g, ' ');
  for (const phrase of ['independently established evidence', 'separately supported, authorized obligation',
    'delegation, resumption, and compaction', 'including test expectations, check selection, compatibility, and completion claims',
    'no open review epoch', 'optional techniques, not an intervention quota or acceptance gate']) assert(normalized.includes(phrase), phrase);
  const comparison = readFileSync(resolve(here, 'construction-comparison.md'), 'utf8');
  for (const phrase of ['authored, not model-replayed', '52f0cc9be529be647b80ccef21fc60b28ad502a2',
    'Decision-to-effect fidelity', 'not a security sandbox', 'not untouched holdouts',
    'Do not rewrite CAS receipts', 'not evidence of model efficacy']) assert(comparison.includes(phrase), phrase);
});

test('a different wire representation may satisfy the same contract', () => {
  withTrial('original', 'distinct', 'plain', directory => {
    writeFileSync(resolve(directory, 'codec.mjs'), `export function encode(value) {
  return !Object.hasOwn(value, 'timeout') ? 'inherit' : value.timeout === null ? 'off' : String(value.timeout);
}
export function decode(bytes) {
  return bytes === 'inherit' ? {} : bytes === 'off' ? {timeout: null} : {timeout: Number(bytes)};
}
`);
    const result = assess(directory, 'original', 'distinct', 'plain');
    assert.equal(result.artifact_pass, true);
    assert.equal(result.candidate_changed, true);
    assert.equal(result.behavioral_judgment, 'not_automated');
  });
});

test('self-modifying candidate bytes cannot receive stable artifact credit', () => {
  withTrial('original', 'distinct', 'plain', directory => {
    writeFileSync(resolve(directory, 'codec.mjs'), `import {writeFileSync} from 'node:fs';
writeFileSync(new URL(import.meta.url), ${JSON.stringify(programs.original)});
${programs.repaired}`);
    const result = assess(directory, 'original', 'distinct', 'plain');
    assert(result.observations.every(item => item.pass));
    assert.equal(result.candidate_stable, false);
    assert.equal(result.artifact_pass, false);
  });
});

test('output overflow is unavailable, never an inferred pass', () => {
  withTrial('repaired', 'distinct', 'plain', directory => {
    writeFileSync(resolve(directory, 'codec.mjs'), `process.stdout.write('x'.repeat(2 * 1024 * 1024));\n${programs.repaired}`);
    const result = assess(directory, 'repaired', 'distinct', 'plain');
    assert.equal(result.execution, 'unavailable');
    assert.equal(result.artifact_pass, false);
  });
});
