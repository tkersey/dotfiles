#!/usr/bin/env node
// Source regressions only; test_native_codex.py qualifies the installed executable separately.
import assert from 'node:assert/strict';
import {readFileSync, readdirSync, existsSync} from 'node:fs';
import {dirname, resolve, relative} from 'node:path';
import {fileURLToPath} from 'node:url';

const skills = resolve(dirname(fileURLToPath(import.meta.url)), '../..');
const read = path => readFileSync(resolve(skills, path), 'utf8');
const sources = Object.fromEntries([
  'cas/SKILL.md','cas/reviews.md','cas/app-server.md','cas/runtime-compatibility.md',
  'cas/references/review-proof-boundary.md','elenctic/references/native-forks.md',
  'actuating/references/review-contract.json'
].map(path => [path, read(path)]));
const normalized = text => text.replace(/\s+/g, ' ');
function check(source) {
  const policy = JSON.parse(source['actuating/references/review-contract.json']);
  assert.equal(policy.review_execution.default_mode, 'codex');
  assert.deepEqual(Object.keys(policy.review_execution.modes).sort(), ['codex','subagents']);
  const quality = policy.review_execution.modes.codex.attempt_quality;
  for (const key of ['host_attributed_execution_required','fresh_native_thread_required',
    'native_structured_review_output_required','exact_thread_and_root_turn_required',
    'successful_terminal_execution_required','exact_dispatch_and_instruction_binding_required',
    'current_git_subject_required','raw_result_preserved','executor_fallback_forbidden',
    'fabricated_legacy_receipt_forbidden']) assert.equal(quality[key], true, key);
  assert.equal(quality.process_exit_or_rendered_text_sufficient, false);
  assert.equal(policy.standard_convergence.required_consecutive_clean_attempts, 5);
  assert.equal(policy.review_execution.mixed_mode_credit_forbidden, true);
  const review = normalized(source['cas/reviews.md']);
  for (const law of [
    'no custom instructions argument', 'Do not rewrite shared config',
    'exact parent `thread_id` and root review `turn_id`', 'item.review_output',
    'followed by that root turn\'s `task_complete`',
    'Neither process exit nor rendered prose is enough',
    'Continue observing the same host process when a wait expires',
    'neither is passive review wait', 'A sent interrupt is not observed cancellation',
    'A cancelled request earns no credit',
    'GIT_WORK_TREE', 'old credit is not native credit'
  ]) assert((review + ' ' + normalized(source['cas/SKILL.md'])).includes(law), law);
  assert.match(source['cas/reviews.md'], /codex exec[^\n]+--json/);
  assert.match(source['cas/reviews.md'], /developer_instructions=/);
  assert.match(source['cas/app-server.md'], /codex app-server --listen stdio:\/\//);
  assert.match(source['cas/app-server.md'], /codex app-server --listen ws:\/\/127\.0\.0\.1/);
  assert.match(normalized(source['cas/app-server.md']), /A listener is not a client/);
  assert.match(normalized(source['cas/SKILL.md']), /Existing local schedules, rows, files, run records, memories, and installed scheduler jobs are unchanged/);
  assert.match(normalized(source['elenctic/references/native-forks.md']), /full prepared analysis history/);
  assert.match(source['elenctic/references/native-forks.md'], /"\$codex" app-server --listen stdio:\/\//);
  for (const text of Object.values(source))
    assert(!/\bcas (?:review|app-server|automation|instance_runner|session_inquiry|capabilities|goal|account)\b/.test(text));
}
check(sources);
const mutations = [
  ['legacy default','actuating/references/review-contract.json','"default_mode": "codex"','"default_mode": "cas"'],
  ['count reduced','actuating/references/review-contract.json','"required_consecutive_clean_attempts": 5','"required_consecutive_clean_attempts": 4'],
  ['prose credit','actuating/references/review-contract.json','"process_exit_or_rendered_text_sufficient": false','"process_exit_or_rendered_text_sufficient": true'],
  ['no structured result','actuating/references/review-contract.json','"native_structured_review_output_required": true','"native_structured_review_output_required": false'],
  ['mixed old credit','actuating/references/review-contract.json','"mixed_mode_credit_forbidden": true','"mixed_mode_credit_forbidden": false'],
  ['lost root turn','cas/reviews.md','root review `turn_id`','arbitrary turn'],
  ['false cancellation','cas/reviews.md','A sent interrupt is not observed cancellation','A sent interrupt is cancellation'],
  ['retry on timeout','cas/reviews.md','Continue observing the same host process when a wait expires','Start another review when a wait expires'],
  ['legacy transport','elenctic/references/native-forks.md','"$codex" app-server --listen stdio://','cas app-server session --listen stdio://'],
  ['scheduler destruction','cas/SKILL.md','unchanged. Before the later executable removal','deleted. Before the later executable removal'],
];
for (const [name,path,before,after] of mutations) {
  assert(sources[path].includes(before), 'inactive mutation: ' + name);
  assert.throws(() => check({...sources,[path]:sources[path].replace(before,after)}), assert.AssertionError,name);
}
// Scan active guidance only. Historical eval observations and corpus enum values remain historical.
let inspected = 0;
function walk(directory) {
  for (const item of readdirSync(directory, {withFileTypes:true})) {
    if (item.isSymbolicLink()) continue;
    const path = resolve(directory,item.name);
    if (item.isDirectory()) {
      if (!['tests','evals','definitions'].includes(item.name)) walk(path);
    } else if (/\.(md|yaml)$/.test(path)) {
      const text = readFileSync(path,'utf8');
      assert(!/\bcas (?:review|app-server|automation|instance_runner|session_inquiry|capabilities|goal|account)\b/.test(text), relative(skills,path));
      inspected++;
    }
  }
}
walk(skills);
for (const retired of ['session-inquiry.md','references/automation.md','references/automation-db.md',
  'references/codex_app_server_contract.md','references/codex-app-server-capability-matrix.md',
  'assets/start-wait-normalized-clean.example.json','definitions/ledger/fork-inquiry-receipt.json'])
  assert(!existsSync(resolve(skills,'cas',retired)), 'retired route retained: ' + retired);
const historical = JSON.parse(read('review-fold/definitions/ledger/counterexample-corpus.json'));
assert(JSON.stringify(historical).includes('"cas"'), 'historical provenance must remain readable');
// This .cas.lock is compare-and-swap custody, not the retired executable.
assert(read('ledger/scripts/ensure_custody.py').includes('.cas.lock'));
console.log(`native Codex: routing/evidence boundaries, ${mutations.length} mutation controls, ${inspected} active guidance files, historical provenance and custody distinction passed`);
