#!/usr/bin/env node
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const binary = process.argv[2];
assert.ok(binary, 'usage: node test-token-usage.mjs /absolute/path/to/seq');
const definition = resolve(dirname(fileURLToPath(import.meta.url)), '../definitions/seq/token-usage.json');
const temporary = mkdtempSync(join(tmpdir(), 'seq-token-usage-'));
const env = { ...process.env, CODEX_HOME: join(temporary, 'codex'), SEQ_CACHE_DIR: join(temporary, 'cache') };
mkdirSync(env.CODEX_HOME);
let checks = 0;

function run(args) {
  const result = spawnSync(binary, args, { env, encoding: 'utf8', timeout: 15000, maxBuffer: 4 * 1024 * 1024 });
  assert.equal(result.error, undefined, `Seq execution failed: ${result.error}`);
  assert.equal(result.status, 0, `Seq failed (${result.signal ?? result.status}): ${result.stderr}\n${result.stdout}`);
  return JSON.parse(result.stdout);
}

function usage(input, cached, output, reasoning) {
  return { input_tokens: input, cached_input_tokens: cached, output_tokens: output, reasoning_output_tokens: reasoning, total_tokens: input + output };
}

function modern(total = usage(100, 20, 50, 10), last = usage(20, 5, 5, 1)) {
  return { total_token_usage: total, last_token_usage: last };
}

function stamp(second) {
  return `2026-11-01T10:00:${String(second).padStart(2, '0')}Z`;
}

function session(directory, id, observations, parent = null, metadata = {}, tokenOrdinals = []) {
  mkdirSync(directory, { recursive: true });
  const path = join(directory, `${id}.jsonl`);
  const rows = [
    { type: 'session_meta', timestamp: stamp(0), payload: { id, cwd: '/token-fixture', ...(parent === null ? {} : { parent_thread_id: parent }), ...metadata } },
    { type: 'event_msg', timestamp: stamp(1), payload: { type: 'task_started', turn_id: 'turn-1' } },
    ...observations.map((info, index) => ({ type: 'event_msg', ...(tokenOrdinals[index] === undefined ? {} : { ordinal: tokenOrdinals[index] }), timestamp: stamp(index + 2), payload: { type: 'token_count', info } })),
    { type: 'event_msg', timestamp: stamp(59), payload: { type: 'task_complete', turn_id: 'turn-1' } },
  ];
  writeFileSync(path, rows.map(row => JSON.stringify(row)).join('\n') + '\n');
  return path;
}

function observe(selectors) {
  const result = run(['observe', '--definition', definition, '--projection', 'summary', '--format', 'json', ...selectors]);
  assert.equal(result.data.schema, 'seq-token-usage-result/v3');
  assert.equal(result.data.rows.length, 1);
  assert.equal(result.data.rows[0].usage_scope, 'observed-owned-usage');
  return result.data.rows[0];
}

function check(name, observations, expected, selectors = []) {
  const path = session(join(temporary, 'cases'), name, observations);
  const actual = observe(['--path', path, ...selectors]);
  for (const [field, value] of Object.entries(expected)) {
    assert.deepEqual(actual[field], value, `${name}: ${field}\n${JSON.stringify(actual)}`);
  }
  checks += 1;
  return actual;
}

const nullTotals = { input_tokens: null, cached_input_tokens: null, output_tokens: null, reasoning_output_tokens: null, total_tokens: null, cached_percentage: null };
const invalid = { verdict: 'invalid', ...nullTotals };
const unavailable = { verdict: 'unavailable', ...nullTotals };

try {
  assert.equal(run(['definition', 'check', '--definition', definition, '--format', 'json']).valid, true);
  assert.equal(run(['explain', '--definition', definition, '--projection', 'summary', '--format', 'json']).strategy.kind, 'partition-lineage-stream');

  check('modern', [modern()], { verdict: 'valid', transition_count: 1, input_tokens: 20, cached_input_tokens: 5, output_tokens: 5, reasoning_output_tokens: 1, total_tokens: 25, cached_percentage: 25 });
  check('exact-repeats', [modern(), modern(), modern()], { verdict: 'valid', candidate_count: 1, transition_count: 1, total_tokens: 25 });
  check('observed-zero', [modern(usage(0, 0, 0, 0), usage(0, 0, 0, 0))], { verdict: 'valid', transition_count: 1, input_tokens: 0, output_tokens: 0, total_tokens: 0, cached_percentage: null });
  check('no-events', [], { ...unavailable, candidate_count: 0, transition_count: 0 });
  check('null-info', [null], { ...unavailable, candidate_count: 1, no_usage_observation_count: 1 });
  check('mixed-null-info', [modern(), null], { verdict: 'valid', total_tokens: 25, transition_count: 1, no_usage_observation_count: 1 });
  check('zero-with-null-info', [modern(usage(0, 0, 0, 0), usage(0, 0, 0, 0)), null], { verdict: 'valid', total_tokens: 0, transition_count: 1, no_usage_observation_count: 1 });
  check('unanchored-last', [{ last_token_usage: usage(20, 5, 5, 1) }], { ...unavailable, unanchored_observation_count: 1 });

  for (const tuple of ['total_token_usage', 'last_token_usage']) {
    for (const counter of ['input_tokens', 'output_tokens', 'total_tokens']) {
      const info = modern();
      delete info[tuple][counter];
      check(`missing-${tuple}-${counter}`, [info], { ...unavailable, missing_core_observation_count: 1 });
    }
    for (const counter of ['cached_input_tokens', 'reasoning_output_tokens']) {
      const info = modern();
      delete info[tuple][counter];
      check(`missing-${tuple}-${counter}`, [info], { ...unavailable, invalid_observation_count: 0, missing_detail_observation_count: 1 });
    }
    for (const counter of ['input_tokens', 'cached_input_tokens', 'output_tokens', 'reasoning_output_tokens', 'total_tokens']) {
      const info = modern();
      info[tuple][counter] = -1;
      check(`negative-${tuple}-${counter}`, [info], invalid);
    }
  }

  check('cached-over-input', [modern(usage(100, 90, 50, 10), usage(5, 10, 5, 1))], invalid);
  check('reasoning-over-output', [modern(usage(100, 20, 50, 10), usage(20, 5, 5, 6))], invalid);
  check('cached-predecessor', [modern(usage(100, 90, 50, 10), usage(90, 0, 5, 1))], invalid);
  check('reasoning-predecessor', [modern(usage(100, 20, 50, 40), usage(20, 5, 40, 0))], invalid);
  for (const tuple of ['total_token_usage', 'last_token_usage']) {
    const info = modern();
    info[tuple].total_tokens += 1;
    check(`inconsistent-${tuple}`, [info], invalid);
  }

  const initial = modern(usage(10, 0, 2, 0), usage(10, 0, 2, 0));
  const contradicting = modern(usage(10, 0, 2, 0), usage(20, 0, 2, 0));
  check('invalid-after-repeat', [initial, initial, contradicting], { ...invalid, invalid_observation_count: 1, transition_count: 0 });
  check('invalid-before-repeat', [contradicting, initial, initial], { ...invalid, invalid_observation_count: 1, transition_count: 0 });
  check('conflict-outside-window', [initial, contradicting], { ...invalid, invalid_observation_count: 1 }, ['--until', stamp(3)]);
  check('different-plausible-last', [modern(), modern(usage(100, 20, 50, 10), usage(15, 5, 5, 1))], { ...unavailable, ambiguous_observation_count: 1, invalid_observation_count: 0 });
  const partial = modern();
  delete partial.last_token_usage.cached_input_tokens;
  check('partial-enrichment', [partial, modern()], { ...unavailable, ambiguous_observation_count: 1, invalid_observation_count: 0 });
  check('partial-exact-repeats', [partial, partial], { ...unavailable, candidate_count: 1, ambiguous_observation_count: 0 });

  check('legacy-increasing', [{ total_token_usage: usage(10, 0, 0, 0) }, { total_token_usage: usage(30, 0, 0, 0) }], { ...unavailable, legacy_observation_count: 2 });
  check('legacy-exact-repeats', [{ total_token_usage: usage(10, 0, 0, 0) }, { total_token_usage: usage(10, 0, 0, 0) }], { ...unavailable, legacy_observation_count: 1 });
  check('legacy-modern-same-total', [{ total_token_usage: usage(100, 20, 50, 10) }, modern()], { ...unavailable, legacy_observation_count: 1, transition_count: 1 });

  const timelessPath = session(join(temporary, 'cases'), 'timeless', [modern()]);
  const timelessRows = readFileSync(timelessPath, 'utf8').trim().split('\n').map(line => JSON.parse(line));
  delete timelessRows[2].timestamp;
  writeFileSync(timelessPath, timelessRows.map(row => JSON.stringify(row)).join('\n') + '\n');
  assert.equal(observe(['--path', timelessPath]).total_tokens, 25, 'unbounded accounting does not invent a timestamp requirement');
  for (const selector of ['--since', '--until']) {
    const timeless = observe(['--path', timelessPath, selector, stamp(3)]);
    assert.equal(timeless.verdict, 'unavailable', 'unknown event time cannot establish membership in a bounded window');
    assert.equal(timeless.total_tokens, null);
    assert.equal(timeless.unresolved_time_observation_count, 1);
  }
  checks += 3;

  const timelessNeutralPath = session(join(temporary, 'cases'), 'timeless-neutral', [modern(), null]);
  const timelessNeutralRows = readFileSync(timelessNeutralPath, 'utf8').trim().split('\n').map(line => JSON.parse(line));
  delete timelessNeutralRows[3].timestamp;
  writeFileSync(timelessNeutralPath, timelessNeutralRows.map(row => JSON.stringify(row)).join('\n') + '\n');
  for (const selectors of [['--since', stamp(2)], ['--until', stamp(3)]]) {
    const neutral = observe(['--path', timelessNeutralPath, ...selectors]);
    assert.equal(neutral.verdict, 'valid', 'timestampless neutral metadata must not poison observed usage');
    assert.equal(neutral.total_tokens, 25);
    assert.equal(neutral.unresolved_time_observation_count, 0);
    assert.equal(neutral.no_usage_observation_count, 0, 'unknown-time metadata is not asserted to lie in the selected window');
    assert.equal(neutral.unplaced_no_usage_observation_count, 1);
  }
  checks += 2;

  const large = (marker) => ({ input_tokens: marker, cached_input_tokens: 0, output_tokens: 0, reasoning_output_tokens: 0, total_tokens: marker });
  const largePath = session(join(temporary, 'cases'), 'adjacent-i64', [modern(large('FIRST_I64'), usage(1, 0, 0, 0)), modern(large('NEXT_I64'), usage(1, 0, 0, 0))]);
  writeFileSync(largePath, readFileSync(largePath, 'utf8').replaceAll('"FIRST_I64"', '9007199254740992').replaceAll('"NEXT_I64"', '9007199254740993'));
  const largeTotals = observe(['--path', largePath]);
  assert.equal(largeTotals.verdict, 'valid');
  assert.equal(largeTotals.transition_count, 2, 'distinct cumulative i64 tuples are not collapsed by floating-point conversion');
  assert.equal(largeTotals.total_tokens, 2);
  checks += 1;

  const tree = join(env.CODEX_HOME, 'sessions');
  const first = modern(usage(10, 0, 0, 0), usage(10, 0, 0, 0));
  const next = modern(usage(20, 0, 0, 0), usage(10, 0, 0, 0));
  session(tree, 'root', [first]);
  const child = session(tree, 'child', [first, next], 'root', { subagent_history_start_ordinal: 50 }, [41, 51]);
  session(tree, 'sibling', [first, next], 'root', { subagent_history_start_ordinal: 50 }, [41, 51]);
  session(tree, 'independent', [first]);
  assert.equal(observe(['--root', tree]).total_tokens, 40, 'strict ancestor replay excluded; sibling and independent ownership retained');
  assert.equal(observe(['--root', tree, '--session-id', 'root']).total_tokens, 30, 'selected root includes its descendants only');
  assert.equal(observe(['--path', child]).total_tokens, 10, 'selected child excludes replay owned outside selection');
  assert.equal(observe(['--root', tree, '--since', stamp(3)]).total_tokens, 20, 'ownership precedes time filtering');
  assert.equal(observe(['--root', tree, '--until', stamp(3)]).total_tokens, 20, 'until is exclusive');
  checks += 5;

  const splitTree = join(tree, 'split-tree');
  const controller = session(splitTree, 'controller', [modern(usage(50, 0, 0, 0), usage(50, 0, 0, 0))]);
  session(splitTree, 'history-parent', [first]);
  session(splitTree, 'fork-child', [first, next], 'controller', { forked_from_id: 'history-parent', subagent_history_start_ordinal: 50 }, [41, 51]);
  const third = modern(usage(30, 0, 0, 0), usage(10, 0, 0, 0));
  session(splitTree, 'grandchild', [first, next, third], 'fork-child', { forked_from_id: 'fork-child', subagent_history_start_ordinal: 60 }, [41, 51, 61]);
  assert.equal(observe(['--root', splitTree]).total_tokens, 80);
  assert.equal(observe(['--root', splitTree, '--session-id', 'controller']).total_tokens, 70,
    'control descendants count while external history ancestors only establish ownership');
  assert.equal(observe(['--path', controller]).total_tokens, 70,
    'path and ID selectors preserve the same control scope');
  assert.equal(observe(['--root', splitTree, '--session-id', 'fork-child']).total_tokens, 20);
  checks += 4;

  const collisionTree = join(temporary, 'counter-collision-tree');
  const fourth = modern(usage(40, 0, 0, 0), usage(10, 0, 0, 0));
  session(collisionTree, 'collision-root', [first, next], null, {}, [10, 60]);
  session(collisionTree, 'collision-child', [first, next, third], 'collision-root', {
    forked_from_id: 'collision-root',
    forked_from_ordinal_exclusive: 40,
    subagent_history_start_ordinal: 50,
  }, [41, 51, 61]);
  session(collisionTree, 'collision-grandchild', [first, next, third, fourth], 'collision-child', {
    forked_from_id: 'collision-child',
    subagent_history_start_ordinal: 70,
  }, [41, 51, 61, 71]);
  assert.equal(observe(['--root', collisionTree]).total_tokens, 50,
    'proven child progress survives an identical tuple recorded later by its ancestor');
  assert.equal(observe(['--root', collisionTree, '--session-id', 'collision-child']).total_tokens, 30);
  assert.equal(observe(['--root', collisionTree, '--session-id', 'collision-grandchild']).total_tokens, 10,
    'a positively owned child transition remains indexed for grandchild replay removal');
  checks += 3;

  const repeatedBaselineTree = join(temporary, 'repeated-baseline-tree');
  session(repeatedBaselineTree, 'baseline-root', [first]);
  session(repeatedBaselineTree, 'baseline-child', [first, first, next], 'baseline-root', {
    subagent_history_start_ordinal: 50,
  }, [41, 51, 61]);
  assert.equal(observe(['--root', repeatedBaselineTree]).total_tokens, 20,
    'a baseline repeated after the own-record boundary remains one inherited profile');
  assert.equal(observe(['--root', repeatedBaselineTree, '--session-id', 'baseline-child']).total_tokens, 10);
  checks += 2;

  const unknownCases = [
    ['legacy-position', {}, [], [first, next]],
    ['missing-recorded-ordinal', { subagent_history_start_ordinal: 50 }, [], [first, next]],
    ['missing-history-boundary', {}, [41, 51], [first, next]],
    ['omitted-prefix-baseline', { subagent_history_start_ordinal: 50 }, [51], [first]],
    ['omitted-prefix-different-tuple', { subagent_history_start_ordinal: 50 }, [51], [next]],
    ['unmatched-inherited-profile', { subagent_history_start_ordinal: 50 }, [41], [next]],
  ];
  for (const [name, metadata, ordinals, observations] of unknownCases) {
    const directory = join(temporary, name);
    session(directory, `${name}-root`, [first]);
    session(directory, `${name}-child`, observations, `${name}-root`, metadata, ordinals);
    const unknown = observe(['--root', directory, '--session-id', `${name}-child`]);
    assert.equal(unknown.verdict, 'unavailable', `${name}: positions and baseline evidence cannot be invented`);
    assert.equal(unknown.total_tokens, null);
    assert.ok(unknown.unavailable_observation_count > 0);
    checks += 1;
  }

  const resetTree = join(temporary, 'counter-reset-tree');
  const five = modern(usage(5, 0, 0, 0), usage(5, 0, 0, 0));
  session(resetTree, 'reset-root', [five]);
  session(resetTree, 'reset-child', [five, modern(usage(20, 0, 0, 0), usage(15, 0, 0, 0)), modern(usage(10, 0, 0, 0), usage(5, 0, 0, 0))], 'reset-root', {
    subagent_history_start_ordinal: 50,
  }, [41, 51, 61]);
  const reset = observe(['--root', resetTree, '--session-id', 'reset-child']);
  assert.equal(reset.verdict, 'unavailable', 'an older compatible snapshot cannot hide a reset from the latest snapshot');
  assert.equal(reset.total_tokens, null);
  assert.equal(reset.invalid_observation_count, 0, 'ownership uncertainty is distinct from a malformed counter tuple');
  checks += 1;

  for (const [name, last] of [['cached-progress', usage(10, 4, 10, 4)], ['reasoning-progress', usage(10, 5, 10, 3)]]) {
    const directory = join(temporary, name);
    const baseline = modern(usage(10, 2, 10, 3), usage(10, 2, 10, 3));
    session(directory, `${name}-root`, [baseline]);
    session(directory, `${name}-child`, [baseline, modern(usage(20, 7, 20, 7), last)], `${name}-root`, {
      subagent_history_start_ordinal: 50,
    }, [41, 51]);
    const mismatched = observe(['--root', directory, '--session-id', `${name}-child`]);
    assert.equal(mismatched.verdict, 'unavailable', `${name}: predecessor equality includes every reported component`);
    assert.equal(mismatched.total_tokens, null);
    assert.equal(mismatched.invalid_observation_count, 0);
    checks += 1;
  }

  const incompleteTree = join(temporary, 'incomplete-tree');
  session(incompleteTree, 'orphan', [first], 'missing-ancestor');
  session(incompleteTree, 'orphan-child', [first, next], 'orphan');
  for (const selectors of [[], ['--session-id', 'orphan-child'], ['--since', stamp(3)]]) {
    const missingParent = observe(['--root', incompleteTree, ...selectors]);
    assert.equal(missingParent.verdict, 'unavailable', 'missing historical evidence cannot become valid usage');
    assert.equal(missingParent.total_tokens, null);
    assert.ok(missingParent.unresolved_ancestry_observation_count > 0);
  }
  checks += 3;

  const repoTree = join(temporary, 'repo-tree');
  const insideRepo = join(temporary, 'inside-repo');
  const outsideRepo = join(temporary, 'outside-repo');
  mkdirSync(insideRepo);
  mkdirSync(outsideRepo);
  session(repoTree, 'outside-history', [first], null, { cwd: outsideRepo });
  session(repoTree, 'inside-child', [first, next], 'outside-history', { cwd: insideRepo, subagent_history_start_ordinal: 50 }, [41, 51]);
  const repoLimited = observe(['--root', repoTree, '--repo', insideRepo]);
  assert.equal(repoLimited.verdict, 'unavailable', 'repo selection cannot hide an unread ancestor');
  assert.equal(repoLimited.total_tokens, null);
  assert.ok(repoLimited.unresolved_ancestry_observation_count > 0);
  assert.equal(observe(['--root', repoTree, '--session-id', 'inside-child']).total_tokens, 10);
  checks += 2;

  const conflictingTree = join(temporary, 'conflicting-tree');
  session(conflictingTree, 'known-history', [first]);
  session(conflictingTree, 'conflicted-child', [first, next], 'controller-one', {
    forked_from_id: 'known-history',
    subagent_history_start_ordinal: 50,
    source: { subagent: { thread_spawn: { parent_thread_id: 'controller-two' } } },
  }, [41, 51]);
  const conflictingParent = observe(['--root', conflictingTree, '--session-id', 'conflicted-child']);
  assert.equal(conflictingParent.verdict, 'unavailable', 'contradictory declarations of one parent relation remain unresolved');
  assert.equal(conflictingParent.total_tokens, null);
  assert.ok(conflictingParent.unresolved_ancestry_observation_count > 0);
  checks += 1;

  const neutralTree = join(temporary, 'neutral-tree');
  session(neutralTree, 'neutral-grandparent', [first]);
  session(neutralTree, 'neutral-root', [null], 'neutral-grandparent');
  session(neutralTree, 'neutral-child', [first, next], 'neutral-root', { subagent_history_start_ordinal: 50 }, [41, 51]);
  const neutralChild = observe(['--root', neutralTree, '--session-id', 'neutral-child']);
  assert.equal(neutralChild.verdict, 'unavailable', 'neutral ancestor records cannot establish transition ownership');
  assert.equal(neutralChild.total_tokens, null);
  assert.ok(neutralChild.unresolved_ancestry_observation_count > 0);
  checks += 1;

  const emptyAncestorTree = join(temporary, 'empty-ancestor-tree');
  session(emptyAncestorTree, 'empty-grandparent', [first]);
  session(emptyAncestorTree, 'empty-root', [], 'empty-grandparent');
  session(emptyAncestorTree, 'empty-root-child', [first, next], 'empty-root', { subagent_history_start_ordinal: 50 }, [41, 51]);
  const emptyAncestor = observe(['--root', emptyAncestorTree, '--session-id', 'empty-root-child']);
  assert.equal(emptyAncestor.verdict, 'unavailable', 'a readable ancestor with no counters is insufficient ownership evidence');
  assert.equal(emptyAncestor.total_tokens, null);
  checks += 1;

  const replayTree = join(temporary, 'replay-tree');
  session(replayTree, 'replay-root', [first]);
  session(replayTree, 'replay-only-parent', [first], 'replay-root', { subagent_history_start_ordinal: 50 }, [41]);
  session(replayTree, 'replay-grandchild', [first, next], 'replay-only-parent', { subagent_history_start_ordinal: 50 }, [41, 51]);
  assert.equal(observe(['--root', replayTree, '--session-id', 'replay-only-parent']).total_tokens, 10,
    'observed replayed counters remain parent evidence even when they contribute no owned usage');
  assert.equal(observe(['--root', replayTree, '--session-id', 'replay-grandchild']).total_tokens, 10);
  checks += 2;

  const zeroAncestorTree = join(temporary, 'zero-ancestor-tree');
  const zeroTuple = modern(usage(0, 0, 0, 0), usage(0, 0, 0, 0));
  session(zeroAncestorTree, 'zero-root', [zeroTuple]);
  session(zeroAncestorTree, 'zero-root-child', [zeroTuple, first], 'zero-root', { subagent_history_start_ordinal: 50 }, [41, 51]);
  assert.equal(observe(['--root', zeroAncestorTree, '--session-id', 'zero-root-child']).total_tokens, 10,
    'an observed zero is evidence, unlike no assertion');
  checks += 1;

  const neutralLeafTree = join(temporary, 'neutral-leaf-tree');
  session(neutralLeafTree, 'observed-root', [first]);
  session(neutralLeafTree, 'neutral-leaf', [null], 'observed-root');
  assert.equal(observe(['--root', neutralLeafTree]).total_tokens, 10,
    'neutral leaves do not invalidate known observed transitions');
  checks += 1;

  const uncertainTree = join(temporary, 'uncertain-tree');
  const missingDetails = modern(usage(10, 0, 0, 0), usage(10, 0, 0, 0));
  delete missingDetails.total_token_usage.cached_input_tokens;
  delete missingDetails.last_token_usage.cached_input_tokens;
  session(uncertainTree, 'uncertain-root', [missingDetails, missingDetails]);
  session(uncertainTree, 'known-child', [first, next], 'uncertain-root', { subagent_history_start_ordinal: 50 }, [41, 51]);
  const uncertain = observe(['--root', uncertainTree]);
  assert.equal(uncertain.verdict, 'unavailable', 'unknown ancestor subcounter is not observed zero');
  assert.equal(uncertain.total_tokens, null, 'ambiguous ownership must not sum matching core deltas');
  assert.equal(uncertain.missing_detail_observation_count, 1, 'exact repeats preserve the same missingness once');
  for (const selectors of [['--session-id', 'known-child'], ['--since', stamp(3)]]) {
    const childOnly = observe(['--root', uncertainTree, ...selectors]);
    assert.equal(childOnly.verdict, 'unavailable', 'selection cannot remove unresolved ancestor ownership');
    assert.equal(childOnly.total_tokens, null);
    assert.ok(childOnly.unresolved_ancestry_observation_count > 0);
  }
  checks += 3;

  // Per-request accounting (Claude Code transcripts): each request reports its own usage and is
  // owned by the transcript that recorded its request; copies never own usage.
  const claudeVersion = '2.1.325';
  const claudeStamp = (second) => `2026-11-01T10:${String(Math.floor(second / 60)).padStart(2, '0')}:${String(second % 60).padStart(2, '0')}.000Z`;
  const claudeUsage = (input, read, write, output) => ({ input, read, write, output });
  function claudeSession(directory, id, entries, version = claudeVersion, cwd = '/claude-fixture') {
    const project = join(directory, '-claude-fixture');
    mkdirSync(project, { recursive: true });
    const rows = [];
    let parent = null;
    for (const entry of entries) {
      const at = entry.at;
      if (entry.unanswered) {
        rows.push({ type: 'api-request', id: `rq-${entry.key}`, sessionId: id, timestamp: claudeStamp(at), querySource: 'sdk', requestDigest: `dg-${entry.key}`, version });
        continue;
      }
      const common = { isSidechain: false, sessionId: id, cwd, gitBranch: 'main', userType: 'external', version };
      rows.push({ type: 'user', uuid: `u-${entry.key}`, parentUuid: parent, ...common, timestamp: claudeStamp(at), message: { role: 'user', content: 'Do the task.' }, turnOrigin: 'human' });
      if (entry.authored) {
        rows.push({ type: 'api-request', id: `rq-${entry.key}`, sessionId: id, timestamp: claudeStamp(at + 1), querySource: 'sdk', requestDigest: `dg-${entry.key}`, version });
      }
      const message = { model: 'claude-test-model', type: 'message', role: 'assistant', id: entry.key, stop_reason: entry.final === false ? null : 'end_turn', stop_sequence: null, content: [{ type: 'text', text: 'Done.' }] };
      if (entry.usage) {
        const { input, read, write, output } = entry.usage;
        const counters = { input_tokens: input, cache_read_input_tokens: read, cache_creation_input_tokens: write, output_tokens: output };
        message.usage = { ...counters, service_tier: 'standard', iterations: [{ type: 'message', ...counters }] };
        if (entry.dropOutput) {
          delete message.usage.output_tokens;
          delete message.usage.iterations[0].output_tokens;
        }
      }
      rows.push({ type: 'assistant', uuid: `a-${entry.key}`, parentUuid: `u-${entry.key}`, ...common, timestamp: claudeStamp(at + 2), message,
        ...(entry.linked === false ? {} : { requestRef: `rq-${entry.key}`, requestId: `req_rq-${entry.key}`, apiBlockIndex: 0 }) });
      parent = `a-${entry.key}`;
    }
    const path = join(project, `${id}.jsonl`);
    writeFileSync(path, rows.map(row => JSON.stringify(row)).join('\n') + '\n');
    return path;
  }
  const claudeId = (n) => `c${String(n).padStart(7, '0')}-0000-4000-8000-000000000000`;
  const qa = claudeUsage(4, 0, 40, 6);    // input 44, cached 0, cache writes 40, total 50
  const qb = claudeUsage(5, 40, 8, 9);    // input 53, cached 40, cache writes 8, total 62
  const qc = claudeUsage(6, 53, 9, 4);    // input 68, cached 53, cache writes 9, total 72
  const authored = (key, usage, at, extra = {}) => ({ key, usage, at, authored: true, ...extra });
  const copied = (key, usage, at, extra = {}) => ({ key, usage, at, authored: false, ...extra });
  function perRequest(name, sessions, selectors = []) {
    const directory = join(temporary, 'claude', name);
    const paths = sessions.map(([id, entries]) => claudeSession(directory, id, entries));
    return { paths, result: observe(['--root', directory, ...selectors]) };
  }
  function expectRequests(name, actual, expected) {
    for (const [field, value] of Object.entries(expected)) {
      assert.deepEqual(actual[field], value, `${name}: ${field}\n${JSON.stringify(actual)}`);
    }
    checks += 1;
  }

  const single = perRequest('authored', [[claudeId(1), [authored('msg_a', qa, 0), authored('msg_b', qb, 10)]]]).result;
  expectRequests('authored', single, {
    verdict: 'valid', usage_count: 2, request_count: 2, transition_count: 0,
    input_tokens: 97, cached_input_tokens: 40, cache_creation_input_tokens: 48, output_tokens: 15, total_tokens: 112,
    cached_percentage: 40 / 97 * 100, unresolved_ancestry_observation_count: 0, unanchored_observation_count: 0,
  });

  const forkSessions = [
    [claudeId(2), [authored('msg_p1', qa, 0), authored('msg_p2', qb, 10)]],
    [claudeId(3), [copied('msg_p1', qa, 0), copied('msg_p2', qb, 10), authored('msg_c1', qc, 70)]],
  ];
  const fork = perRequest('fork', forkSessions);
  expectRequests('fork-root', fork.result, { verdict: 'valid', request_count: 3, total_tokens: 184, replayed_observation_count: 2 });
  expectRequests('fork-child-path', observe(['--path', fork.paths[1]]),
    { verdict: 'valid', request_count: 1, total_tokens: 72, replayed_observation_count: 2, unresolved_ancestry_observation_count: 0 });
  expectRequests('fork-parent-path', observe(['--path', fork.paths[0]]), { verdict: 'valid', request_count: 2, total_tokens: 112 });
  expectRequests('fork-child-alone', perRequest('fork-child-alone', [forkSessions[1]]).result,
    { verdict: 'valid', request_count: 1, total_tokens: 72, replayed_observation_count: 2 });
  expectRequests('fork-window', perRequest('fork-window', forkSessions, ['--since', claudeStamp(60)]).result,
    { verdict: 'valid', request_count: 1, total_tokens: 72 });
  expectRequests('fork-until', perRequest('fork-until', forkSessions, ['--until', claudeStamp(12)]).result,
    { verdict: 'valid', request_count: 1, total_tokens: 50 });

  for (const [label, extra] of [['unplaced', {}], ['unlinked', { linked: false }]]) {
    const shared = [
      [claudeId(4), [copied('msg_u', qa, 0, extra)]],
      [claudeId(5), [copied('msg_u', qa, 0, extra)]],
    ];
    const copies = perRequest(`${label}-copies`, shared);
    expectRequests(`${label}-copies-root`, copies.result, { verdict: 'valid', request_count: 1, total_tokens: 50 });
    expectRequests(`${label}-copies-split`, observe(['--root', join(temporary, 'claude', `${label}-copies`), '--session-id', claudeId(4)]),
      { verdict: 'unavailable', total_tokens: null, unresolved_ownership_observation_count: 1 });
    expectRequests(`${label}-copies-path`, observe(['--path', copies.paths[1]]),
      { verdict: 'unavailable', total_tokens: null, unresolved_ownership_observation_count: 1 });
    expectRequests(`${label}-conflicting-copies`, perRequest(`${label}-conflict`, [
      [claudeId(6), [copied('msg_v', qa, 0, extra)]],
      [claudeId(7), [copied('msg_v', qb, 0, extra)]],
    ]).result, { verdict: 'unavailable', total_tokens: null, ambiguous_observation_count: 1 });
  }

  expectRequests('two-authors', perRequest('two-authors', [
    [claudeId(8), [authored('msg_k', qa, 0)]],
    [claudeId(9), [authored('msg_k', qa, 0)]],
  ]).result, { verdict: 'unavailable', total_tokens: null, unresolved_ownership_observation_count: 1 });

  expectRequests('provisional', perRequest('provisional', [[claudeId(10), [authored('msg_a', qa, 0), authored('msg_q', qb, 10, { final: false })]]]).result,
    { verdict: 'valid', request_count: 1, total_tokens: 50, provisional_observation_count: 1 });
  expectRequests('only-provisional', perRequest('only-provisional', [[claudeId(11), [authored('msg_q', qb, 0, { final: false })]]]).result,
    { verdict: 'unavailable', usage_count: 0, total_tokens: null, provisional_observation_count: 1 });
  expectRequests('no-usage', perRequest('no-usage', [[claudeId(12), [authored('msg_a', qa, 0), authored('msg_n', null, 10)]]]).result,
    { verdict: 'valid', request_count: 1, total_tokens: 50, no_usage_observation_count: 1 });
  expectRequests('unanswered', perRequest('unanswered', [[claudeId(13), [authored('msg_a', qa, 0), { key: 'msg_x', at: 10, unanswered: true }]]]).result,
    { verdict: 'valid', request_count: 1, total_tokens: 50, no_usage_observation_count: 1 });
  expectRequests('incomplete-usage', perRequest('incomplete-usage', [[claudeId(14), [authored('msg_a', qa, 0), authored('msg_m', qb, 10, { dropOutput: true })]]]).result,
    { verdict: 'unavailable', total_tokens: null, missing_core_observation_count: 1 });
  expectRequests('invalid-usage', perRequest('invalid-usage', [[claudeId(15), [authored('msg_a', qa, 0), authored('msg_i', claudeUsage(5, 0, 0, -1), 10)]]]).result,
    { verdict: 'invalid', total_tokens: null, invalid_observation_count: 1 });
  expectRequests('empty-claude', perRequest('empty-claude', [[claudeId(16), [{ key: 'msg_x', at: 0, unanswered: true }]]]).result,
    { verdict: 'unavailable', usage_count: 0, total_tokens: null });

  const claudeRepo = join(temporary, 'claude-repo');
  mkdirSync(claudeRepo);
  const repoRoot = join(temporary, 'claude', 'repo-scope');
  claudeSession(repoRoot, claudeId(17), [authored('msg_r', qa, 0)], claudeVersion, claudeRepo);
  claudeSession(repoRoot, claudeId(18), [authored('msg_s', qb, 0)]);
  expectRequests('repo-authored', observe(['--root', repoRoot, '--repo', claudeRepo]), { verdict: 'valid', request_count: 1, total_tokens: 50 });
  claudeSession(repoRoot, claudeId(19), [copied('msg_w', qc, 0)], claudeVersion, claudeRepo);
  expectRequests('repo-unplaced', observe(['--root', repoRoot, '--repo', claudeRepo]),
    { verdict: 'unavailable', total_tokens: null, unresolved_ownership_observation_count: 1 });
  expectRequests('root-unplaced', observe(['--root', repoRoot]), { verdict: 'valid', request_count: 3, total_tokens: 184 });

  // Per-request accounting (Pi sessions): Pi records no request-side authorship, so a forked or imported
  // copy keeps its key; corpus totals deduplicate by key while narrowed selections stay unresolved.
  const piRoot = join(temporary, 'pi');
  const piEntry = (id, second, usage, extra = {}) => ({ type: 'message', id, parentId: null, timestamp: `2026-11-01T10:00:${String(second).padStart(2, '0')}Z`,
    message: { role: 'assistant', content: [{ type: 'text', text: 'Done.' }], provider: 'fixture', model: 'fixture-model', usage, stopReason: 'stop', ...extra } });
  const piUsage = (input, output, cacheRead, cacheWrite) => ({ input, output, cacheRead, cacheWrite, totalTokens: input + output + cacheRead + cacheWrite });
  function piSession(name, entries, header = {}) {
    mkdirSync(piRoot, { recursive: true });
    const path = join(piRoot, `${name}.jsonl`);
    const rows = [{ type: 'session', version: 3, id: name, timestamp: '2026-11-01T10:00:00Z', cwd: '/pi-fixture', ...header }, ...entries];
    writeFileSync(path, rows.map(row => JSON.stringify(row)).join('\n') + '\n');
    return path;
  }
  const piOriginal = piSession('pi-original', [piEntry('p1', 1, piUsage(10, 4, 2, 3)), piEntry('p2', 2, piUsage(20, 5, 0, 0))]);
  piSession('pi-fork', [piEntry('p1', 1, piUsage(10, 4, 2, 3)), piEntry('f1', 9, piUsage(30, 6, 0, 0))], { parentSession: piOriginal });
  const piProbe = spawnSync(binary, ['observe', '--definition', definition, '--projection', 'summary', '--format', 'json', '--root', piRoot], { env, encoding: 'utf8', timeout: 15000 });
  const piError = piProbe.status === 0 ? null : JSON.parse(piProbe.stdout).code;
  if (piError === 'PiCumulativeTokenEventsUnavailable') {
    console.log('Skipped Pi per-request cases: this Seq does not emit Pi token events.');
  } else {
    expectRequests('pi-corpus', observe(['--root', piRoot]),
      { verdict: 'valid', request_count: 3, input_tokens: 15 + 20 + 30, cached_input_tokens: 2, cache_creation_input_tokens: 3, output_tokens: 15, total_tokens: 80 });
    expectRequests('pi-window', observe(['--root', piRoot, '--since', '2026-11-01T10:00:05Z']), { verdict: 'valid', request_count: 1, total_tokens: 36 });
    expectRequests('pi-path', observe(['--path', piOriginal]), { verdict: 'unavailable', total_tokens: null, unresolved_ownership_observation_count: 2 });
  }

  const codexOnly = observe(['--root', tree]);
  assert.equal(codexOnly.cache_creation_input_tokens, null, 'cumulative counters do not report cache writes; unknown is not zero');
  assert.equal(codexOnly.request_count, 0);
  assert.equal(codexOnly.usage_count, codexOnly.transition_count);
  checks += 1;

  console.log(`Passed ${checks} token-usage regression cases.`);
} finally {
  rmSync(temporary, { recursive: true, force: true });
}
