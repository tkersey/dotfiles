# Native reviews

## Launch the selected review

Use the dedicated `codex exec review` command, not an ordinary coding prompt that
imitates review. Each independent request starts a fresh native thread. Keep the
host-owned process handle and its private stdout, stderr, and final-output files
associated with the caller's exact request. Use a new private output directory for
each attempt; a stale file must not stand in for this execution.

Resolve the repository and immutable base/head before launch and keep that subject
frozen. For committed base/head review, establish that the checkout exposes that
exact diff, not additional uncommitted edits; use a clean checkout of the bound
head where needed without touching unrelated work. `--base` uses Git's merge base
with the current HEAD: require that this is
the caller's bound comparison base. Do not silently change a non-ancestor base or
review another branch. Recheck HEAD and relevant working-tree/index state at result
admission; a clean checkout is not a reason to select `--uncommitted`.

```bash
# Native/default standard. Variables name the caller's frozen subject and new files.
codex exec --cd "$repo" --json --output-last-message "$report" \
  review --base "$base_sha" >"$events" 2>"$diagnostics"
```

Native/default standard adds no custom instructions argument, empty override,
wrapper prompt, copied rubric, or skill-authored instruction file. Preserve
caller-selected model/configuration/permissions; do not add bypass flags or widen
access after a failed check. A named model does not override a configured
`review_model`; preserve or explicitly set that native setting only as authorized.

For a caller-selected auxiliary or file focus, preserve its exact instruction
bytes through a per-invocation `developer_instructions` override. Do not supply the
positional review prompt alongside `--base`, `--commit`, or `--uncommitted`; those
selectors conflict with it. Do not rewrite shared config between concurrent reviews.
For example, encode a UTF-8 file as one TOML-compatible basic string:

```bash
override=$(uv run --no-project python -c \
  'import json,pathlib,sys; sys.stdout.write("developer_instructions=" + json.dumps(pathlib.Path(sys.argv[1]).read_bytes().decode("utf-8"), ensure_ascii=False))' \
  "$instructions")
codex exec --cd "$repo" --json --output-last-message "$report" \
  -c "$override" review --base "$base_sha" >"$events" 2>"$diagnostics"
```

This preserves trailing newlines, quotes, and Unicode without interpreting the
file as shell code. Hash/deliver the same bytes under the caller's existing request
binding. A custom/file review never earns native changeset-standard credit merely
because it used the native reviewer. For options not expressible by the CLI, select
a direct native app-server review before dispatch; do not launch a replacement to
recover output from an already-started attempt.

## Read the native result, not a synthesized receipt

`--json` is execution-event JSONL, not a structured-review-result flag.
`--output-last-message` is rendered text. `--output-schema` does not impose a schema
on the dedicated review task. Neither process exit nor rendered prose is enough
for workflow review credit.

Bind the `thread.started` ID from this invocation to its host process/output. After
terminal execution, locate only that exact thread's native artifact: use an
owner-returned `thread.path` from read-only `thread/read`, or a unique matching
rollout under the selected Codex home's sessions directory. Verify the artifact's
`session_meta.payload.id` and repository against the observed thread and requested
subject. Never select the latest session, a title match, an arbitrary supplied
file, or another review's artifact. Do not read unrelated sessions or publish the
raw rollout. Direct readback of this invocation's owner artifact creates no new
workflow store or corpus report.

For the qualified native rollout shape, require all of:

- This host-attributed execution completed successfully; it was not merely a live
  process, observation timeout, failed turn, or interrupted review.
- An `event_msg` / `item_completed` record with the exact parent `thread_id` and
  root review `turn_id` contains `item.type == "EnteredReviewMode"` and the
  requested Git target. Do not use the delegated reviewer's different turn ID.
- The same thread/turn has `item.type == "ExitedReviewMode"` with a non-null
  `item.review_output`, followed by that root turn's `task_complete`. Resolve
  conflicting failure/interruption evidence; do not choose a favorable older turn.
- The original output contains a `findings` array, `overall_correctness` equal to
  `patch is correct` or `patch is incorrect`, a nonempty `overall_explanation`,
  and finite numeric `overall_confidence_score`; retain complete supported findings.
  Each finding must preserve its title, body, code location/range and confidence;
  malformed findings are not silently dropped to produce an empty clean result.
- The invocation, exact instruction source/absence, effective selected configuration,
  current Git subject, and original result remain attributable to this request.

Use the installed runtime's evidenced equivalent if its native representation
changes. The public app-server `exitedReviewMode.review` projection may be rendered
text only, even when its native artifact retains the structured object. Do not
parse a rendering into invented native fields or mistake parser-fallback prose for
a valid verdict. Missing, ambiguous, malformed, or unavailable evidence earns no
semantic credit. Confidence is not a correctness or admission threshold.

A nonempty findings array remains findings even with `patch is correct`. Empty
findings with `patch is incorrect` is not clean; hold unresolved/contradictory
judgment rather than inventing a finding. Only adequate, current, attributed review
evidence proceeds to the caller's independent adjudication. Provider exhaustion,
a fatal error, unauthorized model rerouting, stale subject, or lost attribution
cannot earn clean credit.

## Observation, recovery, and configuration

Continue observing the same host process when a wait expires. Read exact native
thread/turn state without resuming when outcome is uncertain. `codex exec resume`
and `codex queue --resume` can submit/resume work; neither is passive review wait.
Do not issue another review until the prior attempt is established terminal and
the caller permits a distinct attempt under its existing recovery budget. Retain
original findings even when credit is unavailable.

A sent interrupt is not observed cancellation. In the qualified 0.166.0 runtime,
Ctrl-C can fail with a root/delegate turn-ID mismatch while the review continues.
After authorized cancellation, verify terminal state; when necessary terminate
only the host-owned process/group and confirm it exited before replacement. Never
kill an unrelated daemon or substitute guessed turn IDs. A cancelled request earns
no credit even if a late successful result arrives; preserve that result as evidence.

Keep non-ephemeral execution when recovery requires persisted evidence. Capture
actual runtime identity and exact request bindings in the caller's existing
Working Set; do not invent a CAS backend label, principal attestation, capability
flag, workflow echo, or durable attempt registry. A digest does not establish
instruction delivery or effective settings. Historical receipts retain their
original identity and cannot be relabeled as native observations.

Reported `cwd` is not effective Git-repository attestation. `GIT_DIR`,
`GIT_WORK_TREE`, selected environments, or other configuration can redirect
operations. Establish consistency with the intended subject from relevant native
execution evidence, or withhold dependent credit. Cache environment variables
select paths but do not grant filesystem access; keep paths inside the already
permitted area. Preserve configured secrets privately and never log credential
response bodies.

[Review proof boundary](references/review-proof-boundary.md) separates these
execution facts from finding truth, evidence adequacy, and closure.
