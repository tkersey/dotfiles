# Native reviews

## Inherit the invoking turn's settings

Before a new review, resolve the invoking turn's effective model and reasoning
effort. An explicit caller override for this review wins for that field; inherit
the other field. A global `model`, `review_model`, or reasoning default is not an
explicit override for this request.

Use the host's exact invoking thread/turn identity and effective settings when
available. In a shell, `CODEX_THREAD_ID` identifies the invoking thread, not its
model or effort. Resolve only that thread through read-only native `thread/read`
or its uniquely matching native session artifact, verifying session identity and
the invoking turn. The native `turn_context` records `model` and `effort`; match
the current invocation, not the newest session, another turn, or saved settings
that a per-turn override superseded. Do not resume a thread merely to inspect it.
Read only the needed metadata, not unrelated conversations or private reasoning.

An absent effort is unresolved unless native effective settings or the selected
model's applicable default establish it. Do not guess `medium`, infer settings
from a model name in prose, or silently fall back to disk configuration. If a
required value cannot be established, report the missing value before dispatch;
an explicit caller selection can supply it. Preserve the selected provider and
endpoint; unavailable model/effort combinations do not authorize substitution.

Set `selected_model` and `selected_effort` to those resolved values. Encode the
configuration strings rather than interpreting their contents as shell code:

```bash
review_model_override=$(uv run --no-project python -c \
  'import json,sys; print("review_model=" + json.dumps(sys.argv[1]))' "$selected_model")
reasoning_override=$(uv run --no-project python -c \
  'import json,sys; print("model_reasoning_effort=" + json.dumps(sys.argv[1]))' "$selected_effort")
```

Pass `--model` and both overrides on every new review invocation below. Pinning
`review_model` prevents a configured review-specific model from overriding the
inherited model. Retain the source thread/turn and resolved settings with the
existing request binding; check native effective execution metadata against them
when admitting the result. Requested flags alone do not prove inheritance.
These settings do not customize the native standard rubric or guarantee coverage.

## Launch the selected review

Use native review, not an ordinary coding prompt that imitates review. Select the
interface before dispatch: `codex exec review` suits a one-shot shell invocation;
[direct app-server](app-server.md) suits related operations needing explicit native
control when a supported persistent client is available. Both use native review;
neither interface promises better reasoning or compaction. Do not synthesize a
transport framework merely to prefer RPC, or switch routes to recover output from
possibly live work. Explicit endpoint and transport selections still govern.

Each independent request starts a fresh native thread; a persistent server need
not share reviewer context. Keep host process/connection observations and private
outputs associated with the caller's exact request. Use a new private output
directory for each attempt; a stale file must not stand in for this execution.
Preserve observed host exit or termination status alongside the existing output,
without inventing an exit observation for a server that is still serving work.

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
  --model "$selected_model" -c "$review_model_override" -c "$reasoning_override" \
  review --base "$base_sha" >"$events" 2>"$diagnostics"
```

Native/default standard adds no custom instructions argument, empty override,
wrapper prompt, copied rubric, or skill-authored instruction file. Preserve
caller-selected model/configuration/permissions; do not add bypass flags or widen
access after a failed check. Apply the resolved settings above without editing
shared configuration or changing an already-bound review campaign implicitly.

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
  --model "$selected_model" -c "$review_model_override" -c "$reasoning_override" \
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

Bind the exec `thread.started` ID, or app-server's returned review thread/root
turn, to the actual host dispatch and output. After native terminal execution,
locate only that exact thread's native artifact: use an
owner-returned `thread.path` from read-only `thread/read`, or a unique matching
rollout under the selected Codex home's sessions directory. Verify the artifact's
`session_meta.payload.id` and repository against the observed thread and requested
subject. Never select the latest session, a title match, an arbitrary supplied
file, or another review's artifact. Do not read unrelated sessions or publish the
raw rollout. Direct readback of this invocation's owner artifact creates no new
workflow store or corpus report.

For the qualified native rollout shape, require all of:

- This host-attributed native root review completed successfully; it was not merely
  a live process, observation timeout, failed turn, or interrupted review.
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

Keep result validity, inquiry adequacy, and dispatch authority separate. With empty
findings, a positive native label and a material unresolved gap mean **No defect
established; assigned inquiry incomplete**, not clean completion. Preserve the
original object and its limitations; never change its correctness field to encode
completion. If findings exist, retain them alongside the incomplete-inquiry status.
Caller adjudication, not a confidence value, decides credit.

For deletion-induced findings, preserve the original path/range and bind it to the
base-side changed lines and literal base path. Verify the base source and the
surviving consequence; a missing head file is not grounds to drop a valid finding.
Do not fabricate a side field in native output. Publication must separately use
the provider's base-side location contract; an unpublishable location is a delivery
limitation, not evidence that the finding is false. Missing inquiry is not a bug.

## Observation, recovery, and configuration

Continue observing the same host process when a wait expires. Read exact native
thread/turn state without resuming when outcome is uncertain. `codex exec resume`
and `codex queue --resume` can submit/resume work; neither is passive review wait.
Do not issue another review until the prior attempt is established terminal and
the caller permits a distinct attempt under its existing recovery budget. Retain
original findings even when credit is unavailable. Resolve the original obligation's
attempt history before replacement; configuration or transport changes do not
supply a new allowance. A completed result cannot authorize its own dispatch.

Native task completion and host termination are separate facts. A persistent
server need not exit for a review to complete. If a host handle is lost, exact
native root completion and the original structured result may establish task
completion only when dispatch, target, instructions and effective settings remain
attributable and no failure, interruption, cancellation or conflicting result is
unresolved. Retain **host termination unknown**; disappearance is not successful
exit. Apply every other admission requirement above. If the caller requires a
host-exit observation, that obligation stays held. Do not launch a replacement or
claim cleanup merely because the handle disappeared; resolve possibly live work.

Compaction alone is not terminal failure, a fresh review, or a reset of authority.
Distinguish coordinator, root-review and delegate events before diagnosing a
restart. Continue the established attempt; do not inject manual compaction or
steering into a live native review as a presumed continuity repair. Native
standards remain uncustomized. Custom focused progress belongs to the caller's
focus instructions, not an extra CAS prompt. When diagnosing early compaction,
compare actual model/provider, context-window and compaction settings, not just
model/effort or requested flags. A locally reported effective window is not proof
of provider capacity. Do not enlarge context, change thresholds or select another
model without applicable authority; no maximum-context default is introduced.

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

## Recover incomplete review inquiry

When a terminal review leaves a material observation or reasoning gap and the
caller authorizes recovery, select the [exact-thread follow-up route](queueing.md)
for the required control before submitting work.
This is new work on the original obligation, not passive waiting or another
independent review. Preserve the frozen Git subject, assigned scope/lens,
configuration, permissions, and existing recovery budget. Native standard review
launches remain uncustomized.

A matching thread ID does not establish continuity of the delegated reviewer's
source observations or reasoning. Supply the continuation with the original
assignment and result, the concrete gap, and relevant source-read evidence from
that invocation. Identify the exact commits, paths, delivered ranges, and failed
or truncated reads needed to resume the inquiry. Reuse accessible artifacts;
do not send unrelated logs or private reasoning, or create a coverage registry.
If earlier coverage cannot be established, identify that uncertainty and acquire
the necessary source within the existing scope and budget.

Preserve the original result as immutable history, not a conclusion to defend.
Ask the continuation to complete the missing observation, reassess the dependent
conclusion independently, and overturn it when new evidence warrants. Preserve
original findings with separately attributed confirmations, additions or rebuttals;
never silently erase one. Supply parent-run validation only for a named gap, with
its exact subject, inputs and limitations. Omit broad clean/confidence summaries
that do not help that inquiry; parent validation is not independent reviewer work.

Returned source ranges alone do not establish completed review reasoning. Attribute
follow-up execution and conclusions separately to the same request. A continuation
response is supplemental evidence, not a replacement native verdict or an additional
clean. A bounded continuation may finish its assigned segment while the original
obligation remains held; retain cumulative observations and remaining work until
the required reasoning is reassessed. Do not turn each segment into a new review.

Return unresolved limitations to the caller's existing adjudication. If the
continuation says the inquiry is still incomplete, identify the affected obligation
and its evidence; do not erase the limitation because commands succeeded or all
source ranges are now present. The caller decides whether it is recovered,
covered by applicable evidence, not required for the requested scope, or still
unresolved. When independent reasoning remains missing, parent acquisition alone
does not complete it. CAS supplies attributable evidence, not review credit.

[Review proof boundary](references/review-proof-boundary.md) separates these
execution facts from finding truth, evidence adequacy, and closure.
