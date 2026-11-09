import assert from 'node:assert/strict';
import {test} from 'node:test';
import {assessRelease} from './fixtures/dependency-release.mjs';
import {assessRelease as assessBefore} from './fixtures/dependency-release-before.mjs';

const plan = Object.freeze({
  artifactId: 'package-a', requiredDigest: 'digest-a', requiredBytes: 8,
  destinations: Object.freeze(['east', 'west'])
});
const manifest = digest => ({artifactId: plan.artifactId, digest});
const report = (destinationId, reachable, freeBytes, artifactId = plan.artifactId) =>
  ({artifactId, destinationId, reachable, freeBytes});

function admittedAtoms(input) {
  const {plan: subject, manifest: evidence, observations} = input;
  const digest = evidence?.artifactId === subject.artifactId && typeof evidence.digest === 'string'
    ? evidence.digest === subject.requiredDigest : null;
  const atoms = [digest];
  for (const destinationId of subject.destinations) {
    const applicable = observations.filter(item =>
      item.artifactId === subject.artifactId && item.destinationId === destinationId);
    const observation = applicable.length === 1 ? applicable[0] : null;
    atoms.push(typeof observation?.reachable === 'boolean' ? observation.reachable : null);
    atoms.push(Number.isInteger(observation?.freeBytes)
      ? observation.freeBytes >= subject.requiredBytes : null);
  }
  return atoms;
}

function completeVerdict(atoms) {
  if (!atoms[0]) return false;
  for (let index = 1; index < atoms.length; index += 2)
    if (atoms[index] && atoms[index + 1]) return true;
  return false;
}

function completionOracle(atoms) {
  const outcomes = new Set();
  let completions = 0;
  const enumerate = (index, complete) => {
    if (index === atoms.length) {
      outcomes.add(completeVerdict(complete));
      completions++;
      return;
    }
    for (const value of atoms[index] === null ? [false, true] : [atoms[index]])
      enumerate(index + 1, [...complete, value]);
  };
  enumerate(0, []);
  return {expected: outcomes.size === 1 ? [...outcomes][0] : null, completions};
}

function cases() {
  const result = [];
  const values = [false, true, null];
  for (let number = 0; number < 243; number++) {
    let rest = number;
    const atoms = Array.from({length: 5}, () => {
      const value = values[rest % 3];
      rest = Math.floor(rest / 3);
      return value;
    });
    const capacity = atom => atom === null ? null : atom ? 8 : 7;
    const input = {
      plan,
      manifest: manifest(atoms[0] === null ? null : atoms[0] ? 'digest-a' : 'digest-other'),
      observations: [report('east', atoms[1], capacity(atoms[2])),
        report('west', atoms[3], capacity(atoms[4]))]
    };
    assert.deepEqual(admittedAtoms(input), atoms);
    result.push({name: `matrix-${String(number).padStart(3, '0')}`, input, atoms,
      ...completionOracle(atoms)});
  }
  const add = (name, expected, evidence, observations, subject = plan) => {
    const input = {plan: subject, manifest: evidence, observations};
    const atoms = admittedAtoms(input);
    const oracle = completionOracle(atoms);
    assert.equal(oracle.expected, expected, name);
    result.push({name, input, atoms, ...oracle});
  };
  add('reported-counterexample', false, manifest('digest-other'), []);
  add('missing-manifest', null, null, [report('east', true, 8)]);
  add('foreign-negative-manifest', null, {artifactId: 'package-other', digest: 'digest-other'},
    [report('east', true, 8), report('west', false, 7)]);
  add('foreign-positive-manifest', null, {artifactId: 'package-other', digest: 'digest-a'},
    [report('east', true, 8), report('west', false, 7)]);
  add('foreign-observation-does-not-duplicate', true, manifest('digest-a'),
    [report('east', true, 8), report('east', false, 0, 'package-other')]);
  add('foreign-negative-observations', null, manifest('digest-a'),
    [report('east', false, 0, 'package-other'), report('west', false, 0, 'package-other')]);
  add('unplanned-positive-observation', null, manifest('digest-a'),
    [report('archive', true, 100)]);
  add('unplanned-duplicates', true, manifest('digest-a'),
    [report('east', true, 8), report('archive', false, 0), report('archive', false, 0)]);
  add('missing-required-destination', null, manifest('digest-a'),
    [report('east', false, 0)]);
  add('conflicting-applicable-duplicates', null, manifest('digest-a'),
    [report('east', true, 8), report('east', false, 0), report('west', false, 0)]);
  add('identical-applicable-duplicates', null, manifest('digest-a'),
    [report('east', false, 0), report('east', false, 0), report('west', false, 0)]);
  add('duplicate-branch-with-independent-witness', true, manifest('digest-a'),
    [report('east', true, 8), report('east', false, 0), report('west', true, 8)]);
  add('duplicate-branch-with-digest-failure', false, manifest('digest-other'),
    [report('east', true, 8), report('east', false, 0)]);
  add('all-destinations-ruled-out-without-manifest', false, null,
    [report('east', null, 7), report('west', false, null)]);
  add('cross-destination-facts-do-not-combine', false, manifest('digest-a'),
    [report('east', true, 7), report('west', false, 8)]);
  add('inclusive-capacity-threshold', true, manifest('digest-a'),
    [report('east', true, 8)], {...plan, destinations: ['east']});
  add('capacity-failure-without-reachability', false, manifest('digest-a'),
    [report('east', null, 7)], {...plan, destinations: ['east']});
  add('renamed-plan-three-destinations', true, {artifactId: 'bundle-x', digest: 'digest-x'},
    [{artifactId: 'bundle-x', destinationId: 'c', reachable: true, freeBytes: 31}],
    {artifactId: 'bundle-x', requiredDigest: 'digest-x', requiredBytes: 31,
      destinations: ['a', 'b', 'c']});
  add('omitted-independent-measurements', false, manifest('digest-a'),
    [{artifactId: 'package-a', destinationId: 'east', reachable: false},
      {artifactId: 'package-a', destinationId: 'west', freeBytes: 7}]);
  add('omitted-manifest-digest-with-no-destination', false, {artifactId: 'package-a'},
    [report('east', false, 100), report('west', true, 7)]);
  add('repeated-foreign-reports-do-not-duplicate', true, manifest('digest-a'),
    [report('east', true, 8), report('east', false, 0, 'package-other'),
      report('east', false, 0, 'package-other')]);
  add('reordered-observations', false, manifest('digest-a'),
    [report('west', false, 8), report('east', true, 7)]);
  return result;
}

const inventory = cases();
const matrix = inventory.slice(0, 243);

test('dependency construction: exhaustive partial source domain and scope controls', () => {
  assert.equal(inventory.length, 265);
  assert.equal(inventory.length - matrix.length, 22);
  assert.equal(new Set(matrix.map(item => JSON.stringify(item.atoms))).size, 243);
  assert.equal(matrix.reduce((sum, item) => sum + item.completions, 0), 1024);
  assert.equal(matrix.filter(item => item.atoms.every(atom => atom !== null)).length, 32);
  assert.deepEqual(completionOracle([false, null, null, null, null]), {expected: false, completions: 16});
  assert.deepEqual(completionOracle([true, true, true, null, null]), {expected: true, completions: 4});
  assert.deepEqual(completionOracle([true, true, false, false, true]), {expected: false, completions: 1});
  assert.deepEqual(completionOracle([null, true, true, null, null]), {expected: null, completions: 8});
});

test('dependency construction: release follows every bounded source completion and preserves inputs', () => {
  for (const item of inventory) {
    const input = structuredClone(item.input);
    const before = structuredClone(input);
    assert.equal(assessRelease(input.plan, input.manifest, input.observations), item.expected, item.name);
    assert.deepEqual(input, before, item.name);
  }
});

test('dependency construction: predecessor retains complete observations but loses independent decisions', () => {
  for (const item of matrix.filter(item => item.atoms.every(atom => atom !== null))) {
    const input = structuredClone(item.input);
    assert.equal(assessBefore(input.plan, input.manifest, input.observations), item.expected, item.name);
  }
  for (const name of ['reported-counterexample', 'all-destinations-ruled-out-without-manifest',
    'capacity-failure-without-reachability', 'duplicate-branch-with-independent-witness',
    'renamed-plan-three-destinations']) {
    const item = inventory.find(item => item.name === name);
    assert(item, name);
    const input = structuredClone(item.input);
    assert.notEqual(assessBefore(input.plan, input.manifest, input.observations), item.expected, name);
  }
});
