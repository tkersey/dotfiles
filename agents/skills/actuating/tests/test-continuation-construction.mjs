import assert from 'node:assert/strict';
import {test} from 'node:test';
import {createDispatcher} from './fixtures/continuation-dispatcher.mjs';
import {createDispatcher as createBefore} from './fixtures/continuation-dispatcher-before.mjs';

const cases = [
  ['ordinary', (d, open) => {
    const a = open('a');
    return [d.deliver(a, 7), d.deliver(a, 8)];
  }, [true, false], [['a', 7]]],
  ['reverse', (d, open) => {
    const a = open('a'), b = open('b');
    return [d.deliver(b, 20), d.deliver(a, 10)];
  }, [true, true], [['b', 20], ['a', 10]]],
  ['equal-payload', (d, open) => {
    const a = open('a'), b = open('b');
    return [d.deliver(b, 7), d.deliver(a, 7)];
  }, [true, true], [['b', 7], ['a', 7]]],
  ['replacement', (d, open) => {
    const old = open('a', 'old'), current = open('a', 'current');
    return [d.deliver(old, 1), d.deliver(current, 2)];
  }, [false, true], [['current', 2]]],
  ['stale-cancel', (d, open) => {
    const old = open('a', 'old'), current = open('a', 'current');
    return [d.cancel(old), d.deliver(current, 2)];
  }, [false, true], [['current', 2]]],
  ['cancel-one-owner', (d, open) => {
    const a = open('a'), b = open('b');
    return [d.cancel(a), d.deliver(a, 1), d.deliver(b, 2)];
  }, [true, false, true], [['b', 2]]],
  ['multi-shot', (d, open) => {
    const a = open('a', 'a', true);
    return [d.deliver(a, 7), d.deliver(a, 7), d.cancel(a), d.deliver(a, 8)];
  }, [true, true, true, false], [['a', 7], ['a', 7]]],
  ['replace-multi-shot', (d, open) => {
    const old = open('a', 'old', true), first = d.deliver(old, 1);
    const current = open('a', 'current');
    return [first, d.deliver(old, 2), d.deliver(current, 3)];
  }, [true, false, true], [['old', 1], ['current', 3]]],
  ['foreign-token', (d, open) => {
    const foreign = createDispatcher().start('a', () => {}), current = open('a');
    return [d.deliver(foreign, 1), d.deliver(current, 2)];
  }, [false, true], [['a', 2]]],
  ['mixed', (d, open) => {
    const a = open('a'), b = open('b', 'b', true);
    return [d.deliver(b, 20), d.deliver(a, 10), d.deliver(b, 21), d.cancel(b)];
  }, [true, true, true, true], [['b', 20], ['a', 10], ['b', 21]]]
];

function observe(factory, item) {
  const d = factory(), events = [];
  const open = (key, label = key, multiShot = false) =>
    d.start(key, value => events.push([label, value]), {multiShot});
  return {accepted: item[1](d, open), events};
}
const expected = item => ({accepted: item[2], events: item[3]});

test('continuation construction: source-required ownership and valid continuations', () => {
  assert.equal(cases.length, 10);
  for (const item of cases) assert.deepEqual(observe(createDispatcher, item), expected(item), item[0]);
});

test('continuation construction: completed deliveries can resume the wrong owner', () => {
  for (const item of cases) {
    const actual = observe(createBefore, item);
    assert.deepEqual(actual.accepted, item[2], item[0]);
    if (['reverse', 'equal-payload', 'mixed'].includes(item[0]))
      assert.notDeepEqual(actual.events, item[3], item[0]);
    else assert.deepEqual(actual, expected(item), item[0]);
  }
});

test('continuation construction: rejecting delivery or forcing one-shot loses required behavior', () => {
  const reject = () => ({...createDispatcher(), deliver: () => false});
  const oneShot = () => {
    const d = createDispatcher();
    return {...d, start: (key, callback) => d.start(key, callback)};
  };
  assert.notDeepEqual(observe(reject, cases[0]), expected(cases[0]));
  assert.deepEqual(observe(oneShot, cases[0]), expected(cases[0]));
  for (const item of cases.filter(item => ['multi-shot', 'mixed'].includes(item[0])))
    assert.notDeepEqual(observe(oneShot, item), expected(item));
});
