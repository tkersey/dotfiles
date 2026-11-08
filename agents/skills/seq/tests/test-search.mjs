#!/usr/bin/env node
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const binary = process.argv[2];
assert.ok(binary, 'usage: node test-search.mjs /absolute/path/to/seq');
const definitions = resolve(dirname(fileURLToPath(import.meta.url)), '../definitions/seq');
const temporary = mkdtempSync(join(tmpdir(), 'seq-search-'));
const corpus = join(temporary, 'codex', 'sessions');
const env = { ...process.env, CODEX_HOME: join(temporary, 'codex'), SEQ_CACHE_DIR: join(temporary, 'cache') };
mkdirSync(env.CODEX_HOME);
mkdirSync(corpus);
let checks = 0;

const timestamp = '2026-11-01T10:00:00Z';
const message = (role, text) => ({ type: 'response_item', timestamp, payload: { type: 'message', role, content: [{ type: role === 'user' ? 'input_text' : 'output_text', text }] } });
const tool = (call_id, input) => ({ type: 'response_item', timestamp, payload: { type: 'custom_tool_call', name: 'exec', call_id, input } });

function session(id, entries) {
  const path = join(corpus, `${id}.jsonl`);
  const records = [{ type: 'session_meta', timestamp, payload: { id, cwd: '/fixture' } }, ...entries];
  writeFileSync(path, records.map(record => JSON.stringify(record)).join('\n') + '\n');
  return path;
}

function run(args, success = true) {
  const result = spawnSync(binary, args, { env, encoding: 'utf8', timeout: 15000, maxBuffer: 4 * 1024 * 1024 });
  assert.equal(result.error, undefined, `Seq execution failed: ${result.error}`);
  assert.equal(result.status === 0, success, `${result.status}: ${result.stdout}\n${result.stderr}`);
  checks += 1;
  return JSON.parse(result.stdout);
}

function search(name, needle, extra = [], projection = 'rows') {
  return run(['observe', '--definition', join(definitions, `${name}-search.json`), '--root', corpus,
    '--param', `needle=${needle}`, '--param', 'exclude_session_id=current',
    '--projection', projection, '--format', 'json', ...extra]).data.rows;
}

try {
  const longText = 'MARKER ' + 'a'.repeat(504) + '🌱 faraway';
  const currentPath = session('current', [message('user', 'marker current audit prompt'), tool('current-call', 'marker current input')]);
  const selectedPath = session('history', [
    message('user', longText),
    message('assistant', 'Marker assistant answer'),
    message('user', '<skill name="seq">marker injected skill text</skill>'),
    { type: 'response_item', timestamp, payload: { type: 'reasoning', summary: [{ type: 'summary_text', text: 'marker PRIVATE' }] } },
    tool('alpha', 'marker input ' + 'b'.repeat(600) + ' faraway'),
    tool('zeta', 'marker another input'),
    { type: 'response_item', timestamp, payload: { type: 'function_call', name: 'functions.exec_command', call_id: 'command', arguments: JSON.stringify({ cmd: 'marker command' }) } },
    { type: 'response_item', timestamp, payload: { type: 'function_call', name: 'example.lookup', call_id: 'arguments', arguments: JSON.stringify({ query: 'marker arguments' }) } },
  ]);

  const users = search('message', 'marker', ['--param', 'role=user']);
  assert.equal(users.length, 2, JSON.stringify(users));
  assert.ok(users.every(row => row.role === 'user' && row.session_id === 'history'));
  assert.ok(users.some(row => row.excerpt.includes('injected skill text')));
  const long = users.find(row => row.excerpt.startsWith('MARKER '));
  assert.equal(Buffer.byteLength(long.excerpt), 511);
  assert.equal(long.excerpt, longText.slice(0, 511));
  assert.equal(long.excerpt_truncated, true);
  assert.ok(!Object.hasOwn(long, 'text'));

  const assistants = search('message', 'marker', ['--param', 'role=assistant']);
  assert.equal(assistants.length, 1);
  assert.equal(assistants[0].excerpt, 'Marker assistant answer');
  assert.equal(assistants[0].excerpt_truncated, false);
  assert.equal(search('message', 'marker').length, 3);
  assert.equal(search('message', 'absent').length, 0);
  assert.equal(search('message', 'faraway').length, 1);
  const rawMessages = search('message', 'marker', [], 'rows-raw');
  assert.equal(rawMessages.length, 3);
  assert.ok(rawMessages.some(row => row.text === longText));
  assert.ok(rawMessages.every(row => row.private === false && !row.text.includes('PRIVATE')));

  const tools = search('tool', 'marker');
  assert.equal(tools.length, 4);
  assert.ok(tools.every(row => row.session_id === 'history' && !Object.hasOwn(row, 'output_text') && !Object.hasOwn(row, 'input_text')));
  const longInput = tools.find(row => row.call_id === 'alpha');
  assert.equal(longInput.request_kind, 'input_text');
  assert.equal(Buffer.byteLength(longInput.request_excerpt), 512);
  assert.equal(longInput.request_excerpt_truncated, true);
  assert.equal(tools.find(row => row.call_id === 'command').request_kind, 'command_text');
  assert.equal(tools.find(row => row.call_id === 'command').request_excerpt, 'marker command');
  assert.equal(tools.find(row => row.call_id === 'arguments').request_kind, 'arguments_json');
  assert.ok(tools.find(row => row.call_id === 'arguments').request_excerpt.includes('marker arguments'));
  assert.equal(search('tool', 'faraway').length, 1);
  assert.ok(search('tool', 'faraway', [], 'rows-raw')[0].input_text.endsWith('faraway'));
  assert.deepEqual(search('tool', 'marker').map(row => row.call_id), tools.map(row => row.call_id));

  for (const name of ['message', 'tool']) {
    const definition = join(definitions, `${name}-search.json`);
    const plan = run(['explain', '--definition', definition, '--param', 'needle=marker',
      '--param', 'exclude_session_id=current', '--projection', 'rows', '--format', 'json']);
    assert.equal(plan.strategy.kind, 'bounded-native-prefix');
    const missing = run(['observe', '--definition', definition, '--path', selectedPath,
      '--param', 'needle=marker', '--projection', 'rows', '--format', 'json'], false);
    assert.equal(missing.code, 'MissingParameter');
    for (const projection of ['rows', 'rows-raw']) {
      const excluded = run(['observe', '--definition', definition, '--path', selectedPath,
        '--param', 'needle=marker', '--param', 'exclude_session_id=history',
        '--projection', projection, '--format', 'json']);
      assert.equal(excluded.data.rows.length, 0);
    }
    const deliberate = run(['observe', '--definition', definition, '--path', selectedPath,
      '--param', 'needle=marker', '--param', 'exclude_session_id=', '--projection', 'rows', '--format', 'json']);
    assert.ok(deliberate.data.rows.length > 0);
  }

  session('page', Array.from({ length: 103 }, (_, index) => message('user', `page marker ${index}`)));
  const page = search('message', 'page marker');
  assert.equal(page.length, 100);
  assert.deepEqual(search('message', 'page marker').map(row => row.message_id), page.map(row => row.message_id));

  for (const [id, date] of [['old', '2026-10-31T10:00:00Z'], ['inside', timestamp], ['future', '2026-11-02T10:00:00Z']]) {
    session(`window-${id}`, [
      { ...message('user', `window marker ${id}`), timestamp: date },
      { ...tool(`window-${id}`, `window marker ${id}`), timestamp: date },
    ]);
  }
  for (const name of ['message', 'tool']) {
    const window = search(name, 'window marker', ['--since', '2026-11-01T00:00:00Z', '--until', '2026-11-02T00:00:00Z']);
    assert.equal(window.length, 1, `${name}: time bounds must select source rows`);
    assert.equal(window[0].session_id, 'window-inside');
    assert.equal(search(name, 'marker', ['--session-id', 'current']).length, 0, `${name}: selected current session is excluded`);
    const pathResult = run(['observe', '--definition', join(definitions, `${name}-search.json`),
      '--path', currentPath, '--param', 'needle=marker', '--param', 'exclude_session_id=',
      '--projection', 'rows', '--format', 'json']);
    const pathRows = pathResult.data.rows;
    assert.equal(pathRows.length, 1, `${name}: exact file selection must not include other default-corpus files`);
    assert.equal(pathRows[0].session_id, 'current');
    assert.equal(pathResult.selection.path, currentPath);
    assert.equal(pathResult.selection.root, null);
    assert.equal(pathResult.selection.archive_root, null);
    assert.equal(pathResult.corpus.files, 1);
  }

  for (let index = 0; index < 4; index += 1) {
    session(`large-${index}`, Array.from({ length: 25001 }, () => message('assistant', 'streaming marker excluded by role')));
  }
  session('large-match', [message('user', 'streaming marker selected user')]);
  const large = run(['observe', '--definition', join(definitions, 'message-search.json'),
    '--root', corpus, '--param', 'needle=streaming marker', '--param', 'exclude_session_id=current',
    '--param', 'role=user', '--projection', 'rows', '--format', 'json']);
  assert.equal(large.data.rows.length, 1);
  assert.equal(large.data.rows[0].session_id, 'large-match');
  assert.ok(large.stats.rows_scanned > 100000);
  assert.ok(large.stats.rows_materialized < 1000);
  console.log(`Passed ${checks} search regression invocations.`);
} finally {
  rmSync(temporary, { recursive: true, force: true });
}
