#!/usr/bin/env node
// Source-contract regressions, not an agent simulation or runtime qualification.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const skills = resolve(dirname(fileURLToPath(import.meta.url)), '../..');
const paths = [
  'cas/SKILL.md', 'cas/reviews.md', 'cas/app-server.md', 'cas/queueing.md',
  'actuating/review-closeout.md', 'actuating/references/focused-file-review.md',
  'cas/evals/scenarios.md',
];
const sources = Object.fromEntries(paths.map(path => [path,
  readFileSync(resolve(skills, path), 'utf8').replace(/\s+/g, ' ')]));

const rules = [
  ['route selection', 'cas/reviews.md',
    'Select the interface before dispatch:', 'Select another interface after timeout:'],
  ['no transport miracle', 'cas/reviews.md',
    'neither interface promises better reasoning or compaction', 'RPC guarantees better compaction'],
  ['native standard intact', 'cas/reviews.md',
    'Native/default standard adds no custom instructions argument', 'Native/default standard adds custom instructions'],
  ['fresh thread on persistent server', 'cas/reviews.md',
    'Each independent request starts a fresh native thread', 'Independent requests share the last reviewer thread'],
  ['original structured object', 'cas/reviews.md',
    'never change its correctness field to encode completion', 'change its correctness field to encode completion'],
  ['findings survive incomplete inquiry', 'cas/reviews.md',
    'If findings exist, retain them alongside the incomplete-inquiry status', 'Discard findings when inquiry is incomplete'],
  ['native versus host lifecycle', 'cas/reviews.md',
    'Native task completion and host termination are separate facts', 'Native task completion establishes host termination'],
  ['missing host observation', 'cas/reviews.md',
    'disappearance is not successful exit', 'disappearance is successful exit'],
  ['caller host requirement', 'cas/reviews.md',
    'If the caller requires a host-exit observation, that obligation stays held', 'Ignore caller host-exit requirements'],
  ['conflicting native evidence', 'cas/reviews.md',
    'no failure, interruption, cancellation or conflicting result is unresolved', 'a favorable old turn exists'],
  ['compaction is not replacement', 'cas/reviews.md',
    'Compaction alone is not terminal failure, a fresh review, or a reset of authority', 'Compaction starts a fresh allowance'],
  ['no active compact injection', 'cas/reviews.md',
    'do not inject manual compaction or steering into a live native review', 'inject manual compaction into a live native review'],
  ['capacity is not provider proof', 'cas/reviews.md',
    'A locally reported effective window is not proof of provider capacity', 'A local window proves provider capacity'],
  ['original evidence not fixed answer', 'cas/reviews.md',
    'overturn it when new evidence warrants', 'preserve its correctness conclusion'],
  ['parent execution not independent', 'cas/reviews.md',
    'parent validation is not independent reviewer work', 'parent validation is independent reviewer work'],
  ['bounded continuations are not votes', 'cas/reviews.md',
    'Do not turn each segment into a new review', 'Count each completed segment as a new review'],
  ['allowance remains with obligation', 'actuating/review-closeout.md',
    'does not reset the allowance', 'resets the allowance'],
  ['second verdictless terminal blocks', 'actuating/review-closeout.md',
    'a second verdictless terminal blocks', 'a second verdictless terminal permits another try'],
  ['unknown attempt history blocks', 'actuating/review-closeout.md',
    'withhold replacement rather than assume an unused allowance', 'assume an unused allowance'],
  ['model choice is not waiver', 'actuating/review-closeout.md',
    'A user choice about model or effort alone does not waive an exhausted limit', 'A model choice waives the retry limit'],
  ['no retroactive authorization', 'actuating/review-closeout.md',
    'without calling the dispatch compliant or using later success to retroactively authorize it', 'and use later success to authorize it'],
  ['incomplete inquiry not clean', 'actuating/review-closeout.md',
    'hold the obligation, rather than report clean completion', 'report clean completion'],
  ['no queue to RPC duplicate', 'cas/queueing.md',
    'A route switch must not send the same possibly accepted assignment again through `turn/start`', 'Switch routes and send the assignment again'],
  ['RPC preserves original settings', 'cas/app-server.md',
    "a changed invoking turn is not that authorization", 'use the invoking turn defaults'],
  ['resume effects observed', 'cas/app-server.md',
    'Verify what resumed before issuing another assignment', 'Always start a new turn immediately after resume'],
  ['ordinary turn is supplemental', 'cas/app-server.md',
    'not a resumed native review delegate or a new native standard', 'a new native standard'],
  ['delivery is not host capture', 'actuating/references/focused-file-review.md',
    'Host-captured output can exceed model-visible delivery', 'Host capture proves model delivery'],
  ['preserve investigative progress', 'actuating/references/focused-file-review.md',
    'resolved suspicions with decisive counterevidence, unresolved dependencies', 'only the highest line number read'],
  ['continuity not restart', 'actuating/references/focused-file-review.md',
    'do not restart at the beginning solely because compaction occurred', 'restart at the beginning after every compaction'],
  ['full-file obligation retained', 'actuating/references/focused-file-review.md',
    'Read the full base/head file and its diff', 'Read only selected changed hunks'],
  ['deletion base-side binding', 'actuating/references/focused-file-review.md',
    'anchor the original path/range in the changed base-side source', 'assign every finding to a head-side path'],
  ['no synthetic native side', 'cas/reviews.md',
    'Do not fabricate a side field in native output', 'Add a native side field'],
  ['experimental retirement policy', 'cas/evals/scenarios.md',
    'Retirement-specific completeness remains an experiment, not active policy', 'Retirement-specific completeness is the new default'],
  ['behavioral evidence remains unrun', 'cas/evals/scenarios.md',
    'These behavioral cases are **unrun**', 'These behavioral cases all passed'],
];

function check(source) {
  for (const [name, path, required] of rules)
    assert(source[path].includes(required), `${name}: ${path}`);
  const route = source['cas/SKILL.md'];
  assert(route.includes('`codex exec review` or direct app-server `review/start`'));
  assert(route.includes('enqueue and optional resume') || route.includes('select queueing or direct RPC'));
  const review = source['cas/reviews.md'];
  for (const retained of ['item.review_output', "followed by that root turn's `task_complete`",
    'exact parent `thread_id` and root review `turn_id`',
    'A cancelled request earns no credit', 'Neither process exit nor rendered prose is enough'])
    assert(review.includes(retained), retained);
  const closeout = source['actuating/review-closeout.md'];
  assert(closeout.includes('five consecutive distinct changeset standard cleans'));
  assert(closeout.includes('up to 24 requests'));
  assert(closeout.includes('the next four run serially'));
  assert(source['actuating/references/focused-file-review.md'].includes('Continue after the first finding'));
}

check(sources);
for (const [name, path, required, changed] of rules) {
  assert.equal(sources[path].split(required).length - 1, 1, `ambiguous mutation: ${name}`);
  assert.throws(() => check({...sources, [path]: sources[path].replace(required, changed)}),
    assert.AssertionError, `undetected source mutation: ${name}`);
}
console.log(`review continuity: source boundaries and ${rules.length} mutation controls passed; behavioral trials not run`);
