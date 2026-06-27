# Review Proof Boundary

A CAS review proof has three distinct layers:

```text
transport layer       lane/process/websocket/account setup
attempt layer         review/start returned reviewThreadId
proof layer           reviewVerdict binds base/head/fingerprint
```

Failures in those layers must not share one caller state.

## Non-review transport failure

A persistent lane can die before a review attempt exists. This is detectable when:

```text
reviewCount = 0
lastReviewThreadId = null
lastHeadSha = null
reviewThreadId = null
reviewVerdict = null
```

Classify this as `pre_review_lane_transport_lost`.

## Review attempt

A review attempt exists when `reviewThreadId` exists. Timeouts and reconnectable transport loss after that point should preserve the handle and tell the caller to wait/recover the same attempt.

## Review proof

A proof verdict exists only when `reviewVerdict` binds the requested tuple:

```text
baseSha
headSha
targetFingerprint
reviewThreadId
reviewTurnId
```

This is the only surface `$resolve` or other proof-sensitive workflows should consume for clean streak, terminal holdout, or branch-readiness decisions.
