---
name: cas
description: "Run Zig CAS helpers (`cas`, `cas_account`, `cas_goal`, `cas_smoke_check`, `cas_instance_runner`, `cas_review_session`, `cas_session_inquiry`, `cas_conformance_suite`) for v2 app-server account status, smoke checks, goal lifecycle control, direct thread/turn execution, detached review control, review evidence ledger import/validation, session inquiry replay, and multi-instance fanout. For review evidence, distinguish CAS-RER records, pre-review lane transport, real review attempts, normalized tuple-bound review verdicts, account/resource exhaustion, and tuple concurrency guards."
---

# cas (Zig App-Server Control)

## Mission

`$cas` is the Zig-backed app-server control skill. It owns protocol preflight, account/status probes, goal lifecycle control, direct method execution, detached review lifecycle, review evidence normalization into CAS-RER records, and safe session-inquiry replay.

For review evidence, the doctrine is:

```text
CAS records evidence.
Workflows certify meaning.
```

CAS does not own closeout policy, clean-streak eligibility, architecture hardening mode, PR closure, or semantic reviewer adjudication. Those are workflow-owned projections over CAS review evidence. CAS may maintain coordination hygiene for review reuse, including recording a three-clean reset marker and clearing reusable lock state.

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
cas conformance
```

`cas smoke_check` proves app-server handshake and method reachability. It is never review output.

`cas conformance` probes app-server helper compatibility and retry-policy scenarios.

`cas session_inquiry` owns safe historical replay lifecycle for `$retrace`; see `references/retrace-session-inquiry.md`.

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
cas review_session run --cwd <repo> --base <base> --json --store-root <dir>
CAS_STORE_ROOT=<dir> cas review_session status --latest --json
cas session_inquiry run --cwd <repo> --store-root <dir> ...
```

Repo-local subtrees include:

```text
.ledger/cas/review_sessions/
.ledger/cas/review_sessions/locks/
.ledger/cas/review_ledger/records/
.ledger/cas/session_inquiries/
.ledger/cas/state/clean_streak_resets/
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

### Optional workflow binding

CAS-RER-v1 may carry an additive caller-supplied binding:

~~~json
{
  "workflowBinding": {
    "actuationRunId": "run-id",
    "artifactStateFingerprint": "sha256:...",
    "reviewContractFingerprint": "sha256:...",
    "resolutionDigest": "sha256:...",
    "selectedLenses": ["invariant-ace", "standard"],
    "reviewLane": "standard",
    "lensContract": "standard-review-v1"
  }
}
~~~

`artifactStateFingerprint` binds the producer-native review tuple to the
caller's live worktree state; it is distinct from CAS `targetFingerprint`.
Provide `selectedLenses` already sorted and unique; the producer rejects a
non-canonical list. `reviewLane` identifies the
one lane exercised by this record; `lensContract` binds its exact contract.
Pass the complete object atomically with `--workflow-binding-json JSON|@FILE`.
When present, it participates in tuple-lock and record identity. Unfiltered
`current`/`list` retains every same-artifact/thread binding epoch; supplying
the flag there requests one exact epoch. Import preserves an existing binding
but must never attach or relabel one that the source evidence did not carry.

The binding is observational. CAS still does not decide whether the review
contract is adequate, findings are resolved, a clean suffix qualifies, or
mutation is authorized.

Missing binding does not prevent review execution and does not invalidate a
legacy CAS record. It means `workflow-unbound`. A workflow that requires
actuation closeout must fail closed rather than re-labeling the record after
review. Check installed dispatcher capabilities because older versions may not
emit this object.

Current production helpers:

```bash
cas review_session run --cwd <repo> --base <base> --workflow-binding-json @binding.json --json --fallback none
cas review_session status --latest --json
cas review_session status --path <record.json> --json
cas review_session wait --latest --json
cas review_session receipt normalize --path <receipt.json> --format json --summary
cas review_session receipt classify --path <receipts.jsonl> --format jsonl
```

When available, newer ledger helpers have this shape:

```bash
cas review run --cwd <repo> --base <base> --json --fallback none
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

Use `cas review inspect` and `cas review validate-record` for diagnostics and schema/invariant validation only. They have no workflow closeout authority.

Use `cas review_session` when low-level detached review lifecycle control matters: persisted `reviewThreadId`, wait/status/interrupt, compatibility diagnostics, approval/runtime overrides, or migration/debug receipts.

For ordinary one-review closure on the current dispatcher, prefer the shipped broker:

```bash
cas review_session run --cwd <repo> --base <base> --json --fallback none
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

Use `cas review_session lane` only for debugging, migration, or broker backend diagnostics. A persistent lane owns transport reuse only. It is not canonical proof and not a workflow policy backend.

If a caller only needs low-level start/wait control, use:

```bash
cas review_session start --wait --cwd <repo> --base <base> --json --fallback none
```

Current `start --wait --json` can emit a `cas-start-wait` `reviewVerdict`
when the waited review reaches terminal state with a trusted review result and
complete tuple identity. Use `receipt normalize` for saved outputs, fixture
summaries, or an explicit requested-tuple recheck, not as the normal review
happy path.

Do not branch production workflow logic on `receipt gate`, `lane status`, raw `start/wait` output, diagnostic proof/inspect output, or raw receipts. Normalize them to tuple-bound `reviewVerdict`, or import them into CAS-RER when the ledger surface exists, then let the owning workflow apply its policy.

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

`reviewVerdict.status="findings"` is a completed review, not a CAS failure. The caller should reset clean streak and adjudicate the findings.

`reviewVerdict.status="clean"` is a clean completed review fact only when all hold:

```text
backendClass is allowed for this workflow
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
`cas review_session run ...` for the same tuple. CAS will normalize terminal
evidence, block if the old attempt might still be live, or auto-replace only
when dead transport is proven from persisted owner/server liveness.

If the caller lost the handle, first run `cas review_session status --latest
--json` and verify `baseSha`, `headSha`, and `targetFingerprint` match the
intended tuple. If they match, recover with `cas review_session wait --latest
--json` or copy the reported `reviewThreadId` into an explicit wait command.
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

When a completed review emits findings, CAS should expose a stable
per-finding evidence projection so workflow receipts can join later decisions,
patch epochs, proof epochs, and clean-review attempts back to the exact review
row.

CAS owns the identity fields as evidence. It does not decide whether a finding
is accepted, rejected, proof-only, follow-up, blocked, which kernel status it
has, or whether it grants mutation authority.

Each normalized finding row should carry:

```json
{
  "findingId": "cas-finding:<reviewAttemptId>:<ordinal-or-source-id>",
  "findingFingerprint": "best-effort-cross-attempt-hash",
  "reviewAttemptId": "cas-review-attempt-id",
  "lane": "standard|footgun-finder|invariant-ace|complexity-mitigator|other",
  "laneRole": "standard|auxiliary|unknown",
  "contributesToStandardStreak": false,
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
laneRole = standard only when the attempt is the ordinary standard lane
contributesToStandardStreak = true only for normalized clean standard attempts, not finding rows
source_validity = valid only when the attempt is tuple-bound to the intended current artifact
```

If native CAS output cannot provide a source finding ID, compatibility
normalization may synthesize `findingId` from review attempt identity, tuple,
lane, normalized location, title/body hashes, and ordinal. It must still mark
cross-attempt matching as best-effort through `findingFingerprint`.

CAS transports identity; caller workflows own closure accounting. A custom lens
with `base=unknown`, `target_identity_unavailable`, missing head, missing target
fingerprint, or stale tuple binding must be projected as `invalid-proof` for
auxiliary closeout. Dirty invalid-proof findings may still be useful review
pressure after owner-boundary validation, but clean invalid-proof output must not
clear an auxiliary lane or standard clean-review requirement.

Downstream aliases may convert these fields to snake_case (`finding_id`,
`finding_fingerprint`, `review_attempt_id`, and so on), but CAS should preserve
the tuple and thread fields needed by `$review-fold`, `$actuating`, and `$seq`
to cite evidence without re-parsing review prose.

## Codex thread scoping

CAS review reuse is scoped by the Codex session/thread id in addition to the
repo/base/head/account tuple. Pass it explicitly when the caller can resolve it:

```bash
cas review_session run --cwd <repo> --base <base> --json --codex-thread-id <id>
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

## Persistent lane policy

Persistent lane is canonical only when:

```text
cas review_session lane smoke passes for the current repo/codex/cas tuple
cas --version and cas review_session --version meet the caller's required version
lane review emits normalized reviewVerdict
lane failure surfaces include reviewAttemptPhase and reviewAttemptExists
```

If smoke is missing or recently failed with `pre_review_lane_transport_lost`, do not rely on persistent lane continuity for repeated-review policy. Use `start --wait`, normalized receipts, or explicit native fallback as caller-owned review facts.

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

Default repeated review commands consume cached terminal evidence; they are not
new independent review runs. For workflows that require multiple independent CAS
reviews on the same tuple, callers must request each additional post-terminal
attempt with `--fresh-attempt REASON` and evaluate the resulting CAS-RER records
or tuple-bound compatibility projections outside CAS. CAS does not own final
eligibility or closeout strength.

When the same Codex thread records three consecutive reusable clean terminal
reviews for the same tuple lock, CAS writes:

```text
.ledger/cas/state/clean_streak_resets/<tuple_hash>-<timestamp>.json
```

Then CAS removes only the reusable tuple lock. The three clean review records
remain in `.ledger/cas/review_sessions/` and/or `.ledger/cas/review_ledger/`.
This preserves evidence of the clean streak while allowing a later Codex session
or next run to review again instead of being permanently satisfied by a prior
three-clean state. A findings verdict resets the clean counter.

## Hooks, approvals, and fallback

`--hooks inherit` lets Codex hooks run normally. `--hooks off` disables Codex hooks only for CAS-owned app-server processes. `--hooks require-observed` fails closed if no hook notifications are observed.

`--fallback native-review` is explicit degraded verdict preservation. It is not detached CAS review transport and must be reported as `backendClass="cas-native-fallback"` with `fallbackUsed=true`.

Do not infer success from app-server process liveness, `reviewThreadId` creation alone, `start --wait` returning, archived threads, or a terminal turn status. A `CAS-RER-v1` record, or a normalized tuple-bound `reviewVerdict` compatibility projection, is the workflow-consumable evidence surface.

## Tools and examples

Reference validators and classifiers:

```bash
cas review_session status --latest --json
cas review_session wait --latest --json
cas review_session run --cwd <repo> --base <base> --json
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

## Hard rules

- A lane is not a review.
- A review starts at `reviewThreadId`.
- CAS records tuple-bound review evidence; caller workflows decide what that means.
- Use `cas review_session run` as the current normal one-review path unless the installed dispatcher exposes `cas review run`.
- Do not treat `pre_review_lane_transport_lost` as a failed review.
- Do not duplicate a review when an active tuple lock points to an existing `reviewThreadId`.
- Do not manually list and `jq` review-session records when latest-session status is enough; use `cas review_session status --latest --json`, then verify tuple fields before acting.
- Do not treat completed findings as transport failure.
- Do not treat per-finding identity as acceptance, rejection, kernel status, clean-streak authority, or mutation authority.
- Do not treat `usageLimitExceeded` as reviewer output or transport failure.
- Do not rely on persistent lane continuity for repeated-review policy until first-review creation smoke is current.
- `start --wait` evidence is workflow input only after it is represented as tuple-bound review evidence; otherwise import, normalize, or recover first.
- `cas smoke_check` is protocol validation, not review output.
- Native fallback is degraded verdict preservation, not detached CAS review transport.
