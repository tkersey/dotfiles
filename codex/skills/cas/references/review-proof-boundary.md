# CAS Review Transport Boundary

`$cas` is review transport. It can start, wait for, normalize, and report review attempts and review verdict facts. It must not own closure approval, enforce clean-review streaks, or reject review execution because of evidence-tracking metadata.

Callers that need repeated clean reviews own that policy outside CAS. They may request additional independent attempts with `--fresh-attempt REASON`, then count and evaluate the resulting review verdicts themselves.

CAS receipt normalization may expose transport facts such as `reviewAttemptPhase`, `reviewAttemptExists`, `reviewThreadId`, `reviewTurnId`, `baseSha`, `headSha`, `targetFingerprint`, `reviewVerdict.status`, `findingCount`, and failure fields. These fields are observational and are not guarantees.
