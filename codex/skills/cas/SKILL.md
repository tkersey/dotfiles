---
name: cas
description: "Run Zig CAS helpers (`cas`, `cas_account`, `cas_goal`, `cas_smoke_check`, `cas_instance_runner`, `cas_review_session`, `cas_conformance_suite`) for v2 app-server account status, smoke checks, goal lifecycle control, direct thread/turn execution, detached review control, multi-instance fanout, and `$st` swarm conformance/retry-policy checks. For review sessions, distinguish pre-review lane transport, real review attempts, normalized tuple-bound review verdicts, account/resource exhaustion, and tuple concurrency guards."
---

# cas (Zig App-Server Control)

## Mission

`$cas` is the Zig-backed app-server control skill. It owns protocol preflight, account/status probes, goal lifecycle control, direct method execution, detached review lifecycle, persistent review lanes, receipt normalization, and `$st` conformance probes.

For review work, the governing invariant is:

```text
A lane is not a review.
A managed server is not a review.
A parent thread is not a review.
A review attempt starts only after `review/start` returns `reviewThreadId`.
A tuple verdict exists only after `reviewVerdict` binds base/head/fingerprint.
```

Use this skill when the task mentions `cas`, app-server v2 methods, detached review, `reviewThreadId`, persistent review lanes, multi-instance fanout, account/rate-limit status, goal lifecycle, or `$st` conformance.

## Native commands

Use the native dispatcher and helpers:

```text
cas account status
cas goal <resolve|get|set|clear|status|wait>
cas smoke_check
cas instance_runner
cas review_session
cas conformance
```

`cas smoke_check` proves app-server handshake and method reachability. It is never review output.

`cas conformance` probes `$st` swarm-hardening scenarios. `$st` remains the durable source of truth for claims, resources, fencing, branch epochs, and proof metadata.

## Review session boundary

Use `cas review_session` when detached review lifecycle control matters: persisted `reviewThreadId`, wait/status/interrupt, compatibility diagnostics, approval/runtime overrides, or repeatable review receipts.

Use `cas review_session lane` only when persistent review-lane capability is current for the active `cas`/`codex`/repo tuple. The lane owns transport reuse only. Callers still own review adjudication, clean-streak accounting, proof gates, commits, PR comments, and closure decisions.

If a caller only needs one tuple-bound review and persistent lane smoke is unavailable or recently failed, prefer:

```bash
cas review_session start --wait --cwd <repo> --base <base> --json --fallback none
cas review_session receipt normalize --path <start-wait-output.json> --cwd <repo> --base <base> --format json
```

until `start --wait` natively emits the same normalized `reviewVerdict` surface.

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

If a timeout receipt contains `reviewThreadId`, `reviewTurnId`, `recordPath`, `eventLogPath`, target fingerprint, base SHA, and head SHA, recover by waiting on that same `reviewThreadId`. Do not start another review against the same target while the original may still complete.

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
    "status": "clean|findings|timeout|transport_failure|account_resource_exhausted|parse_mismatch|incomplete|no_attempt",
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

`start --wait` output is useful review evidence but is not a tuple-bound review verdict until normalized into this surface with base/head/fingerprint.

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
```

Store locks under:

```text
~/.codex/cas/review_sessions/locks/<tuple_hash>.json
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
pre_review_start_failed + no reviewThreadId => restart lane/start-wait allowed, but not counted as review evidence
terminal + not normalized => normalize existing receipt; do not re-review
terminal|normalized + --fresh-attempt REASON => start a new same-tuple review attempt
account_resource_exhausted => block same-account retry until reset/override
stale => require explicit takeover
```

Default repeated review commands consume cached terminal evidence; they are not
new independent review runs. For workflows that require multiple independent CAS
reviews on the same tuple, callers must request each additional post-terminal
attempt with `--fresh-attempt REASON` and evaluate the resulting review verdicts
outside CAS. CAS does not own clean streaks, final eligibility, or verdict
strength.

## Hooks, approvals, and fallback

`--hooks inherit` lets Codex hooks run normally. `--hooks off` disables Codex hooks only for CAS-owned app-server processes. `--hooks require-observed` fails closed if no hook notifications are observed.

`--fallback native-review` is explicit degraded verdict preservation. It is not detached CAS review transport and must be reported as `backendClass="cas-native-fallback"` with `fallbackUsed=true`.

Do not infer success from app-server process liveness, `reviewThreadId` creation alone, `start --wait` returning, archived threads, or a terminal turn status. Structured `reviewVerdict` decides caller control flow.

## Tools and examples

Reference validators and classifiers:

```bash
python3 codex/skills/cas/tools/cas_review_verdict_gate.py <receipt.json>
python3 codex/skills/cas/tools/cas_review_tuple_lock_gate.py <lock.json>
python3 codex/skills/cas/tools/cas_review_receipt_classifier.py <receipts.jsonl> --format jsonl
```

Example receipts live under `assets/`.

## Final report

When reporting CAS review work, include:

```text
CAS Review:
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
- CAS reports tuple-bound `reviewVerdict`; caller workflows decide what that means.
- Do not treat `pre_review_lane_transport_lost` as a failed review.
- Do not duplicate a review when an active tuple lock points to an existing `reviewThreadId`.
- Do not treat completed findings as transport failure.
- Do not treat `usageLimitExceeded` as reviewer output or transport failure.
- Do not rely on persistent lane continuity for repeated-review policy until first-review creation smoke is current.
- `start --wait` evidence must be normalized before strict consumers use it as review input.
- `cas smoke_check` is protocol validation, not review output.
- Native fallback is degraded verdict preservation, not detached CAS review transport.
