---
name: cas
description: "Run Zig CAS helpers (`cas`, `cas_account`, `cas_goal`, `cas_smoke_check`, `cas_instance_runner`, `cas_review_session`, `cas_session_inquiry`, `cas_trial`, `cas_conformance_suite`) for v2 app-server account status, smoke checks, goal lifecycle control, direct thread/turn execution, detached review control, HCTP one-claim lane execution, review evidence ledger import/validation, session inquiry replay, and multi-instance fanout. For review evidence, distinguish CAS-RER records, pre-review lane transport, real review attempts, normalized tuple-bound review verdicts, account/resource exhaustion, and tuple concurrency guards."
---

# cas (Zig App-Server Control)

## Mission

`$cas` is the Zig-backed app-server control skill. It owns protocol preflight, account/status probes, goal lifecycle control, direct method execution, detached review lifecycle, review evidence normalization into CAS-RER records, and safe session-inquiry replay.

For review work, the governing invariant is:

```text
A lane is not a review.
A managed server is not a review.
A parent thread is not a review.
A review attempt starts only after `review/start` returns `reviewThreadId`.
A tuple verdict exists only after `reviewVerdict` binds base/head/fingerprint.
```

Use this skill when the task mentions `cas`, app-server v2 methods, detached review, `reviewThreadId`, persistent review lanes, multi-instance fanout, account/rate-limit status, or goal lifecycle.

## Native commands

Use the native dispatcher and helpers:

```text
cas capabilities
cas account status
cas goal <resolve|get|set|clear|status|wait>
cas smoke_check
cas instance_runner
cas review_session
cas session_inquiry <preflight|run|start|status|wait|interrupt|receipt|cleanup>
cas trial <preflight|compile-replay|run|status|cleanup|key-info>
cas conformance
```

`cas smoke_check` proves app-server handshake and method reachability. It is never review output.

`cas conformance` probes app-server helper compatibility and retry-policy scenarios.

`cas session_inquiry` owns safe historical replay lifecycle for `$retrace`; see `references/retrace-session-inquiry.md`.

## HCTP trial execution

Before the first native Ledger command in this workflow, load `$ledger` and
complete `$ledger ensure` once. Reuse that readiness for every later Ledger
command.

`cas trial` is an admitted macOS product surface. Probe
`cas capabilities --json` and require only the exact features needed by the
route. Private-v2 direct execution requires:

```text
hylo_trial_runner_v2
hylo_fd_lane_lease_v1
hylo_signed_run_receipt_v2
hylo_private_lane_materialization_fd_v1
hylo_private_receipt_redaction_v1
hylo_target_common_projection_opening_v1
hylo_trial_route_projection_v1
```

Historical execution additionally requires:

```text
hylo_internal_historical_replay_v1
dcp_v2
rip_v1
fir_v1
```

These keys are absent on non-macOS builds. Do not infer historical replay or a
sealed broker from `hylo_trial_runner_v2`. Legacy `hylo_trial_runner_v1` and
`hylo_signed_run_receipt_v1` remain compatibility features only.

Run preflight for each frozen lane:

```bash
cas trial preflight --trial trial.json --lane-id <lane-id> --json
```

Its route projection uses these exact fields:

```text
source_profile_kind
compile_replay_required
replay_preparation_mode
source_profile_body_delivery
execution_route
required_lineage
```

For a direct lane, require `source_profile_kind:"direct"`,
`compile_replay_required:false`, `source_profile_body_delivery:"none"`,
`replay_preparation_mode:"none"`, `execution_route:"direct"`, and
`required_lineage:null`. Skip
`compile-replay`; materialize the visible input, receive the exact lease-bound
Ledger claim through `--materialization-fd`, and invoke `cas trial run` exactly
once.

For a historical lane, require `source_profile_kind:"historical_decision"`,
`compile_replay_required:false`, `replay_preparation_mode:"integrated_run"`,
`execution_route:"historical_replay"`, and the frozen `required_lineage`.
For every v2 historical lane, require
`source_profile_body_delivery:"source_profile_fd"`; the public
`units[*].source_profile` is only the exact validator-defined safe projection,
and extra keys or semantic profile material are invalid. Supply the complete
historical profile directly to `cas trial run --source-profile-fd` from the
admitted materializer. Before claiming the lane, `cas trial run` privately
compiles exactly one DCP and RIP and binds their fingerprints into the claim
and terminal receipt. It then executes one bounded replay; a successful
terminal receipt must join the resulting FIR lineage, while a failed terminal
receipt records FIR unavailability. Embedded delivery is legacy v1 or
standalone diagnostic compatibility, not the v2 execution route.

Every `hylo-trial/v2` lane requires `--materialization-fd`, independently of
source route. The FD carries `hylo-lane-materialization-claim/v2` from
`ledger --source hylo lane-materialization`; it binds the public trial,
registration/start lineage, retained lease, selected treatment commitment, and
private treatment body without disclosing semantic role. It is distinct from
the visible-input, lease, source-profile, and signing-seed descriptors.

That private claim also carries the exact
`hylo-target-common-projection-opening/v1`. CAS accepts no raw
`target_common_projection` alias: it verifies the whole opening against the
public trial's target-common-projection commitment, then verifies the nested
`hylo-target-common-projection/v1` against its public projection fingerprint
before executor preparation. Neither opening nor projection body appears in
the public run receipt.

CAS emits `hylo-run-receipt/v2` for v2 trials. Its public materialization
projection is commitment-only: it may expose the treatment commitment,
visible-input lineage, permitted historical fingerprints, source-profile
delivery mode, and non-disclosure booleans. It must not expose semantic role,
raw target snapshot/materialization identities, target/factor archive paths,
package-tree fingerprints, or private evidence references. Its FIR carrier is
exactly `hylo-fir-public-projection/v1`; the full FIR stays private. Legacy
`hylo-trial/v1` continues to emit `hylo-run-receipt/v1` with its compatible
full-FIR carrier.

The v2 public materialization projection also carries
`materialization_claim_fingerprint`. Before reveal, it must exact-join the
same lane's `hylo-lane-materialization-receipt/v2.claim_fingerprint`. Ledger
requires one matching v2 receipt per lane and rejects changed, missing,
duplicate, or version-mixed per-lane safe-receipt sets before appending reveal.
This join does not apply to the legacy v1 receipt carrier.

Protected lane leases, visible inputs, treatment claims, source profiles, and
signing seeds use distinct anonymous directional descriptors numbered `>=3`.
Do not carry their secret bytes in argv, environment variables, regular files,
normal stdout, the event store, or proof bundles. A started one-claim lane is
never retried as new work; `status` and recovery may only finish or re-emit
already-admitted state.

### Diagnostic `compile-replay`

The standalone `cas trial compile-replay` command is historical-only diagnostic
infrastructure. It rejects direct lanes, case-blind or FD-delivered source
profiles, and `role_separated` or `sealed` assurance. It grants no execution
authority, reports `execution_authority:false`, and must not enter the normal
historical path. `cas trial run` neither consumes its receipt nor its DCP/RIP
files; run performs authoritative integrated preparation before the one-shot
claim.

For an allowed open, embedded historical diagnostic, `--output-dir` must name
a caller-owned canonical private root with no symlink path components and mode
`0700`. CAS creates the lane DCP and RIP as new `0600` files, rejects conflicts,
and revalidates modes, ownership, inode shape, and content fingerprints. Normal
stdout contains only `cas-trial-replay-plan-receipt/v1` metadata and
fingerprints; it never returns the semantic source profile, DCP, or RIP bodies.

### Sealed broker boundary

Sealed assurance requires an explicitly admitted external broker satisfying the
published role, protected-FD, checkpoint, recovery, and non-disclosure
contracts. The repository-owned `hctp-sealed-role-driver` is conformance/test
infrastructure, not an installed product command or capability. Fail closed
before secret generation or trial mutation when no admitted broker exists.
Retain `os_confinement:false`; the macOS route does not claim hostile same-user
process isolation.

## Artifact store

CAS artifacts default to the current repository ledger:

```text
<repo>/.ledger/cas/
```

The default store root is discovered from `--cwd` or the current working
directory by walking to the enclosing git root. If no git root exists, CAS uses
the canonical current working directory's `.ledger/cas`. Do not use global
`~/.codex/cas` as an implicit fallback.

Use an explicit store root only for diagnostics, migration, or compatibility:

```bash
cas review_session run --cwd <repo> --base <base> --timeout-ms 2700000 --json --store-root <dir>
CAS_STORE_ROOT=<dir> cas review_session status --latest --json
cas session_inquiry run --cwd <repo> --store-root <dir> ...
```

Repo-local subtrees include:

```text
.ledger/cas/review_sessions/
.ledger/cas/review_sessions/locks/
.ledger/cas/review_ledger/records/
.ledger/cas/session_inquiries/
```

Review session records include `store_root`, `store_scope="repo-local"`,
`repo_root`, and `codex_thread_id` when available.

## Review evidence boundary

Public review consumers should prefer `CAS-RER-v1` records when the installed
dispatcher emits them. On current dispatchers that expose only
`cas review_session`, consume the normalized tuple-bound `reviewVerdict` from
`cas review_session run` as the compatibility projection, and do not pretend a
cached receipt is an independent CAS-RER record. Legacy receipts, raw event
logs, lane records, and parent-session rows are import inputs or attachments,
not peer truth objects.

### Optional opaque request binding

CAS-RER-v1 may carry an additive caller-supplied binding:

~~~json
{
  "workflowBinding": {
    "requestId": "opaque-caller-id",
    "requestFingerprint": "sha256:..."
  }
}
~~~

CAS validates only that both strings are non-empty. It treats their contents as
opaque, includes the complete binding in tuple-lock and record identity, and
returns it unchanged. Unfiltered `current`/`list` retains every
same-artifact/thread binding epoch; supplying the flag requests one exact
binding. Import preserves an existing binding but never attaches or relabels
one that the source evidence did not carry.

Missing binding does not prevent review execution. Pre-0.2.75 binding objects
remain import-only historical evidence and are rejected for new review
commands. Check `cas capabilities` for
`cas_rer_opaque_request_binding_v1=true` and `cas_review_history_v2=true`
before depending on the new shape and history envelope.

CAS 0.2.75 can pair one artifact selector (`--base`, `--commit`, or
`--uncommitted`) with `--custom-instructions`. It transmits the exact supplied
prompt as the custom review target and retains the selector only to compute the
base/head/fingerprint identity used by the lock, record, and recovery paths.
Require `cas_review_scoped_instructions_v1=true` before depending on this
combined surface.

Current production helpers:

```bash
cas review_session run --cwd <repo> --base <base> --workflow-binding-json @binding.json --timeout-ms 2700000 --json --fallback none
cas review list --cwd <repo> --base <base> --codex-thread-id <id> --json
cas review_session status --latest --json
cas review_session status --path <record.json> --json
cas review_session wait --latest --timeout-ms 2700000 --json
cas review_session receipt normalize --path <receipt.json> --format json --summary
cas review_session receipt classify --path <receipts.jsonl> --format jsonl
```

### Review wait budget

Pass `--timeout-ms 2700000` for every real review wait: `review run`,
`review_session run`, `start --wait`, `wait`, and `lane review`. This is the
45-minute real-review wait budget. Production workflow commands must remain
explicit even after the CLI's omitted-timeout default is updated so older
installed binaries cannot shorten the wait. Keep lane smoke and smoke-suite
waits at `300000`.
Do not use a smaller real-review budget unless the user explicitly overrides
it. A timed-out attempt still requires same-handle recovery; never
start a duplicate review for the tuple.

### Per-review terminal reporting

When reviews run concurrently, monitor each attempt's complete receipt JSON and
recorded process exit status (`rc`) independently of the aggregate executor. A
review becomes reportable only when both exist. Report it immediately and exactly once;
do not wait for siblings or for the aggregate command to return. Derive semantic
status and finding count only from `.reviewVerdict`; use `rc` only to describe
command or transport completion. Use an independent artifact
monitor when an executor buffers stdout. Per-review reporting is observational:
it does not cancel siblings or open retry, RF-v2, adjudication, or mutation
barriers.

When available, newer ledger helpers have this shape:

```bash
cas review run --cwd <repo> --base <base> --timeout-ms 2700000 --json --fallback none
cas review current --cwd <repo> --base <base> --json
cas review list --cwd <repo> --base <base> --json
cas review import --path <receipt.json> --json
cas review inspect --record <rer.json> --json
cas review validate-record --record <rer.json> --json
```

`cas review run` emits `CAS-RUN-v1` with a `CAS-RER-v1` record and broker decision for normal waited review evidence. `cas review current` and `cas review list` read the ledger records for the requested current tuple. `cas review import` normalizes legacy receipt/session artifacts into `CAS-RER-v1` and writes the record under:

```text
.ledger/cas/review_ledger/records/<record_id>.json
```

Use `cas review inspect` and `cas review validate-record` for diagnostics and schema/invariant validation only.

Acquire exhaustive live review history through the canonical ledger command:

```bash
cas review list --cwd <repo> --base <base> --codex-thread-id <id> --json
```

Discover the installed action surface once per gate invocation. Prefer
`review list`; use `review_session list` only when that exact action is
advertised, and otherwise fail closed. The dispatcher must return one complete
`CAS-LIST-v2` object with matching `records` and `recordRefs`. Do not substitute
`status --latest` or a caller-selected record set.

History lookup reconstructs target identity from the selector and exact prompt.
When the attempt used scoped custom instructions, pass the same
`--custom-instructions` bytes to `current` or `list`.

Use `cas review_session` when low-level detached review lifecycle control matters: persisted `reviewThreadId`, wait/status/interrupt, compatibility diagnostics, approval/runtime overrides, or migration/debug receipts.

For ordinary one-review execution on the current dispatcher, prefer the shipped broker:

```bash
cas review_session run --cwd <repo> --base <base> --timeout-ms 2700000 --json --fallback none
```

The current broker output is the legacy `reviewBrokerDecision + reviewVerdict` surface. Consume it as workflow evidence only when `reviewVerdict.tupleVerdictExists=true` and the base/head/fingerprint match the requested tuple. If the newer `cas review` ledger surface is available, prefer its `CAS-RUN-v1` output: one `CAS-RER-v1` record plus a broker decision.

For local detached review inspection, prefer:

```bash
cas review_session status --latest --json
```

This selects the newest persisted record under `.ledger/cas/review_sessions/`
and reports the same tuple/status fields callers need for proof binding:
`reviewThreadId`, `reviewTurnId`, `recordPath`, `eventLogPath`, `baseSha`,
`headSha`, `targetFingerprint`, `turnStatus`, `reviewResult`, and failure
fields. Use `--review-thread-id <id>` when checking a non-latest session or
when a workflow already owns the handle. Use `--path <record.json>` when the
caller has the `recordPath` from a prior run and may be operating outside the
reviewed repo. Do not use latest-session selection
for destructive control; `interrupt` requires an explicit `reviewThreadId` or
session record `--path`.

For compatibility, session lookup by `--review-thread-id` and `--latest` may
read legacy records from `~/.codex/cas/review_sessions` when no repo-local
record exists. This is lookup-only migration compatibility; new CAS artifacts
must still be written under `.ledger/cas` unless an explicit store root is
provided.

ID selectors are store-scoped. When checking from outside the reviewed repo,
pass `--cwd <repo>`, `--store-root <dir>`, or the emitted `recordPath` through
`--path`; the review thread id alone is not a global locator in the repo-local
store model.

Use `cas review_session lane` only for debugging, migration, or broker backend diagnostics. A persistent lane owns transport reuse only.

If a caller only needs low-level start/wait control, use:

```bash
cas review_session start --wait --cwd <repo> --base <base> --timeout-ms 2700000 --json --fallback none
```

Current `start --wait --json` can emit a `cas-start-wait` `reviewVerdict`
when the waited review reaches terminal state with a trusted review result and
complete tuple identity. Use `receipt normalize` for saved outputs, fixture
summaries, or an explicit requested-tuple recheck, not as the normal review
happy path.

Normalize raw receipts and lifecycle output to tuple-bound `reviewVerdict`, or import them into CAS-RER when the ledger surface exists, before consumption.

## CLI spec order

Implementation specs live under `references/cli-specs/` and must be implemented in order:

1. `01-review-attempt-phase.md` — shared phase model.
2. `02-pre-review-lane-transport.md` — pre-review lane death classification.
3. `03-normalized-review-verdict.md` — tuple-bound `reviewVerdict` for all review backends.
4. `04-account-resource-exhaustion.md` — `usageLimitExceeded` as account/resource terminal class.
5. `05-review-tuple-lock.md` — one active attempt per repo/base/head/account tuple.
6. `06-lane-smoke.md` — first-review creation smoke for persistent lanes.
7. `07-seq-cas-review-audit-projection.md` — audit projection for local-session evidence.

## Review attempt phases

Every review-session JSON surface should include transport facts:

```text
reviewAttemptPhase:
  pre_lane_start
  lane_started
  pre_review_start
  review_started
  review_waiting
  review_terminal
  normalized_verdict

reviewAttemptExists: bool
reviewThreadId: string|null
reviewTurnId: string|null
baseSha: string|null
headSha: string|null
targetFingerprint: string|null
```

Rule:

```text
reviewAttemptExists = reviewThreadId != null
```

A lane with `reviewCount=0`, no `lastReviewThreadId`, no `lastHeadSha`, and no verdict is not a failed review. It is pre-review lane transport failure.

## Failure taxonomy

### Completed review verdicts

`reviewVerdict.status="findings"` is a completed review, not a CAS failure.

`reviewVerdict.status="clean"` is a clean completed review fact only when all hold:

```text
reviewThreadId exists
baseSha/headSha/targetFingerprint match the requested tuple
findingCount = 0
failureCode = null
```

### Pre-review lane transport

Use `failureCode="pre_review_lane_transport_lost"` when persistent-lane transport fails before `review/start` creates `reviewThreadId`.

Required fields include:

```text
reviewAttemptPhase = pre_review_start
reviewAttemptExists = false
reviewThreadId = null
reviewTurnId = null
laneId
managedServerPid
managedServerListenUrl
serverExitStatus
stderrLogPath
reviewCount
lastReviewThreadId
baseSha
headSha
targetFingerprint
```

Legal next actions: restart lane, run lane smoke, use `start --wait`, or use explicit fallback. Do not count this as review evidence and do not start duplicate reviews for the same tuple without a tuple-lock decision.

### Review-attempt transport

Use `failureCode="review_transport_lost"` only after `reviewThreadId` exists and the review attempt loses transport while waiting or reconnecting.

If a timeout or transport-loss receipt contains `reviewThreadId`, `reviewTurnId`,
`recordPath`, `eventLogPath`, target fingerprint, base SHA, and head SHA, prefer
`cas review_session run ... --timeout-ms 2700000` for the same tuple. CAS will normalize terminal
evidence, block if the old attempt might still be live, or auto-replace only
when dead transport is proven from persisted owner/server liveness.

If the caller lost the handle, first run `cas review_session status --latest
--json` and verify `baseSha`, `headSha`, and `targetFingerprint` match the
intended tuple. If they match, recover with `cas review_session wait --latest
--timeout-ms 2700000 --json` or copy the reported `reviewThreadId` into an explicit wait command.
This is diagnostic recovery; normal workflows should start from `run`.

### Account/resource exhaustion

If event logs, turn errors, or output contain `usageLimitExceeded`, emit:

```text
failureCode = account_resource_exhausted
failureClass = account_resource
retryableSameTupleNow = false
```

This is not reviewer-quality evidence and not transport evidence. It blocks same-account retry until limits reset, account changes, or a human explicitly overrides the tuple lock.

### Output missing and parse mismatch

`review_output_missing` means a review attempt reached terminal state without structured review output. It is not a clean review verdict.

`review_parse_mismatch` means structured findings and rendered review-text parsing disagree. Treat it as a completed but untrusted receipt until adjudicated or normalized.

## Normalized `reviewVerdict`

All review backends should produce one caller-facing surface:

```json
{
  "reviewVerdict": {
    "status": "clean|findings|timeout|pre_review_transport_failure|review_transport_failure|account_resource_exhausted|parse_mismatch|review_untrusted_source|incomplete",
    "reviewAttemptPhase": "pre_lane_start|lane_started|pre_review_start|review_started|review_waiting|review_terminal|normalized_verdict",
    "reviewAttemptExists": false,
    "tupleVerdictExists": false,
    "backendClass": "cas-lane|cas-start-wait|cas-native-fallback|cas-receipt-normalized",
    "clean": false,
    "findingCount": 0,
    "failureCode": null,
    "failureHint": null,
    "baseSha": null,
    "headSha": null,
    "targetFingerprint": null,
    "reviewThreadId": null,
    "reviewTurnId": null,
    "recordPath": null,
    "eventLogPath": null,
    "findings": []
  }
}
```

## Per-finding identity projection

When a completed review emits findings, CAS should expose a stable per-finding
evidence projection so consumers can join later observations to the exact
review row.

Each normalized finding row should carry:

```json
{
  "findingId": "cas-finding:<reviewAttemptId>:<ordinal-or-source-id>",
  "findingFingerprint": "best-effort-cross-attempt-hash",
  "reviewAttemptId": "cas-review-attempt-id",
  "reviewThreadId": "thread-id",
  "reviewTurnId": "turn-id",
  "baseSha": "base",
  "headSha": "head",
  "targetFingerprint": "diff-fingerprint",
  "titleHash": "sha256:title",
  "bodyHash": "sha256:body",
  "normalizedLocation": {
    "path": "src/file.ext",
    "line": 1,
    "side": "RIGHT|LEFT|unknown"
  },
  "severity": "info|low|medium|high|unknown",
  "verdictStatus": "findings"
}
```

Identity semantics:

```text
findingId = exact emitted finding row in one CAS review attempt
findingFingerprint = best-effort same issue across attempts
reviewAttemptId = stable attempt row or compatibility projection ID
```

If native CAS output cannot provide a source finding ID, compatibility
normalization may synthesize `findingId` from review attempt identity, tuple,
normalized location, title/body hashes, and ordinal. It must still mark
cross-attempt matching as best-effort through `findingFingerprint`.

Downstream aliases may convert these fields to snake_case (`finding_id`,
`finding_fingerprint`, `review_attempt_id`, and so on), but CAS preserves the
tuple and thread fields needed to cite evidence without re-parsing review prose.

## Codex thread scoping

CAS review reuse is scoped by the Codex session/thread id in addition to the
repo/base/head/account tuple. Pass it explicitly when the caller can resolve it:

```bash
cas review_session run --cwd <repo> --base <base> --timeout-ms 2700000 --json --codex-thread-id <id>
```

`CODEX_THREAD_ID` and `CODEX_SESSION_ID` are accepted environment fallbacks. If
none is provided, CAS uses a stable reduced id (`reduced-unspecified`) so plain
CLI `run/current/list` calls can still agree. Workflows that need session
isolation must pass the real Codex thread id.

Wrappers may resolve the current session with `$seq` and pass the result into
CAS, for example:

```bash
seq find-session \
  --prompt 'Use $seq to tell me the session id of this current session.' \
  --since <local-day-start> \
  --limit 1 \
  --format json
```

The CAS core must not depend silently on `seq`; session id discovery belongs in
the wrapper/workflow layer.

`run` and `start --wait` output is tuple-bound review evidence only when its emitted
`reviewVerdict` has `tupleVerdictExists=true`, a terminal tuple status
(`clean`, `findings`, or `account_resource_exhausted`), and matching
base/head/fingerprint. Otherwise normalize the receipt or recover/wait on the
same review attempt.

## Persistent lane readiness

Persistent lane is canonical only when:

```text
cas review_session lane smoke passes for the current repo/codex/cas tuple
cas --version and cas review_session --version meet the caller's required version
lane review emits normalized reviewVerdict
lane failure surfaces include reviewAttemptPhase and reviewAttemptExists
```

If smoke is missing or recently failed with `pre_review_lane_transport_lost`, do not rely on persistent lane continuity for repeated independent attempts. Use `start --wait`, normalized receipts, or explicit native fallback.

## Tuple concurrency guard

There must be at most one active review attempt per tuple:

```text
repo_realpath
base_sha
head_sha
target_fingerprint
resolved_codex_path
resolved_codex_version
account_fingerprint
codex_thread_id
```

Store locks under:

```text
.ledger/cas/review_sessions/locks/<tuple_hash>.json
```

States:

```text
starting_lane
pre_review_start_failed
review_started
waiting
terminal
normalized
account_resource_exhausted
stale
```

Rules:

```text
review_started|waiting + reviewThreadId => return existing handle; do not start duplicate
run + review_started|waiting + review_transport_lost + dead owner/server => auto-replace same tuple
pre_review_start_failed + no reviewThreadId => restart lane/start-wait allowed, but not counted as review evidence
terminal + not normalized => normalize existing receipt; do not re-review
terminal|normalized + run => normalize and return existing tuple verdict
terminal|normalized + --fresh-attempt REASON => start a new same-tuple review attempt
account_resource_exhausted => block same-account retry until reset/override
stale => require explicit takeover
```

A terminal or normalized tuple lock returns its existing verdict. Supply
`--fresh-attempt REASON` to start another independent attempt on the same tuple.

## Hooks, approvals, and fallback

`--hooks inherit` lets Codex hooks run normally. `--hooks off` disables Codex hooks only for CAS-owned app-server processes. `--hooks require-observed` fails closed if no hook notifications are observed.

`--fallback native-review` is explicit degraded verdict preservation. It is not detached CAS review transport and must be reported as `backendClass="cas-native-fallback"` with `fallbackUsed=true`.

Do not infer success from app-server process liveness, `reviewThreadId` creation alone, `start --wait` returning, archived threads, or a terminal turn status. A `CAS-RER-v1` record, or a normalized tuple-bound `reviewVerdict` compatibility projection, is the workflow-consumable evidence surface.

## Tools and examples

Reference validators and classifiers:

```bash
cas review_session status --latest --json
cas review_session wait --latest --timeout-ms 2700000 --json
cas review_session run --cwd <repo> --base <base> --timeout-ms 2700000 --json
cas review_session lock gate --path <lock.json> --format json
cas review_session receipt normalize --path <receipt.json> --format json --summary
cas review_session receipt classify --path <receipts.jsonl> --format jsonl
```

Use `cas review <run|current|list|import|inspect|validate-record>` only after
`cas --help` or `cas capabilities` confirms that subcommand exists in the
installed dispatcher.

`cas review_session receipt gate` is compatibility-only. Do not use it as a production gate; normalize or import to tuple-bound evidence instead.

Example receipts live under `assets/`.

## Final report

When reporting CAS review work, include:

```text
CAS Review:
- recordId / schema, if emitted:
- backend:
- reviewAttemptPhase:
- reviewAttemptExists:
- principalStrength:
- reviewThreadId / reviewTurnId:
- base/head/fingerprint:
- verdict status / finding count:
- failure class / failure code:
- tuple lock:
- fallback/degraded verdict:
- next legal action:
```

Emit this block when each review becomes reportable. A later aggregate summary
may cite it, but must not be the first completion report.

## Hard rules

- A lane is not a review.
- A review starts at `reviewThreadId`.
- CAS records tuple-bound review evidence and opaque request identity.
- Use a 45-minute real-review wait budget; keep smoke/control waits at 5 minutes.
- Report each review immediately and exactly once after its complete receipt JSON
  and process exit status (`rc`) exist; never delay it behind an aggregate wait.
- Use `cas review_session run` as the current normal one-review path unless the installed dispatcher exposes `cas review run`.
- Do not treat `pre_review_lane_transport_lost` as a failed review.
- Do not duplicate a review when an active tuple lock points to an existing `reviewThreadId`.
- Do not manually list and `jq` review-session records when latest-session status is enough; use `cas review_session status --latest --json`, then verify tuple fields before acting.
- Do not treat completed findings as transport failure.
- Per-finding identity is transport provenance.
- Do not treat `usageLimitExceeded` as reviewer output or transport failure.
- Treat persistent-lane continuity as current only after first-review creation smoke passes.
- `start --wait` evidence is workflow input only after it is represented as tuple-bound review evidence; otherwise import, normalize, or recover first.
- `cas smoke_check` is protocol validation, not review output.
- Native fallback is degraded verdict preservation, not detached CAS review transport.
