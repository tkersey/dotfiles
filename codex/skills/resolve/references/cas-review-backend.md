# CAS Review Backend Contract

`$resolve` is CAS-first. Native review is fallback-only.

## Ownership split

- `$resolve` owns review streak state, base/head pinning, completion, validation, commit/push, and PR sweep.
- `$cas` owns lane command shape, version gates, receipt field meanings, timeout recovery semantics, and fallback classification.

Load `$cas` guidance before CAS preflight.

## CAS preflight

Before using CAS as review backend, confirm:

1. `cas --version` and `cas review_session --version` are compatible with lane review.
2. `cas review_session --help` exposes lane start/review/status/stop, JSON output, timeout, fallback flags, and verdict-only/receipt surfaces when needed.
3. A lane can start for the target repo and return a `laneId`.
4. Lane status proves the process is alive.
5. The lane can stop cleanly.
6. A review receipt can normalize into `$resolve`'s `review_result`.

If any step fails, record the failed CAS step and use native fallback only when available.

## Backend classes

- `cas-lane`: CAS lane review with managed websocket transport, fallback disabled, structured result available, parse match, no blocking failure, and zero findings.
- `cas-native-fallback`: CAS degraded to native review; not persistent-lane proof. Count only after native output normalizes to a clean `review_result`.
- `native-cli`: direct native Codex review through `$resolve`'s fallback driver after recorded CAS fallback condition.

Switching backend class resets `clean_review_streak`.

## Review invocation

Default ordinary review attempt:

```text
cas review_session lane review --lane-id <laneId> --base <base-ref-or-sha> --timeout-ms 1800000 --json --fallback none
```

Consume `.reviewVerdict` first. The full CAS receipt is audit evidence; `.reviewVerdict` is control-flow evidence.

Do not let `set -e` hide verdicts. Capture exit status explicitly before classifying.

## Timeout recovery

If CAS review times out, inspect receipt before fallback.

A recoverable timeout must include enough same-handle fields to wait on the original review attempt, including review thread/turn IDs, record/event log paths, target/fingerprint, base SHA, and head SHA.

Recover with the same review handle. Do not start duplicate `lane review` for the same backend/base/head/fingerprint tuple while a recoverable review handle exists.

## Required receipts

For each CAS-backed review invocation, record:

- CAS version and resolved binary path;
- exact command and receipt path;
- `reviewVerdict`;
- lane/review/thread/turn IDs when available;
- target fingerprint, base SHA, head SHA;
- selected transport, fallback use, failure code/hint, result availability/source, parse verdict;
- normalized finding count and backend class.
