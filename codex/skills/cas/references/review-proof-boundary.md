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

This is the only surface proof-sensitive workflows should consume for terminal
holdout or branch-readiness decisions.

Tuple binding is necessary but not sufficient for certification. Closeout proof
also requires `principalProofUsable=true`, derived from account-principal
metadata. If CAS falls back to `unknown-account` or normalizes a legacy receipt
that lacks principal metadata, the receipt remains useful diagnostic evidence
but cannot certify branch readiness by default.

## Clean streak proof

A clean streak is caller policy over proof verdicts, not tuple-lock ownership.
Repeated normalization of one cached receipt is still one review attempt and
must not increment the clean-run counter.

For repeated same-tuple clean-run requirements:

```text
terminal/normalized receipt exists -> use --fresh-attempt REASON for the next independent review
active review lock exists -> wait/recover the existing reviewThreadId
pre-review transport failure -> no attempt exists; ignore for streak and recover transport
```

Use `cas review_session closeout --cwd <repo> --base <base> --json` to certify
the streak from canonical distinct tuple-bound `reviewThreadId` attempts. Use
`--dry-run` when the command must not start missing review attempts.

Reduced-principal attempts do not increment the certified clean streak.
`cas review_session receipt proof --allow-reduced-principal REASON ...` is an
auditable diagnostic downgrade, not closeout certification.
