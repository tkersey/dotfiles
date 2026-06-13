# CAS Review Backend Contract

`$resolve` is CAS-first. Native review is fallback-only.

`$resolve` owns streak state, base/head pinning, validation, commit/push, and PR sweep. `$cas` owns lane command shape, version gates, receipt semantics, timeout recovery, and fallback classification.

Switching backend class resets the clean-review streak.

Required review receipt fields include backend class, base ref/SHA, head SHA, target fingerprint when available, command, raw receipt, parsed findings, and verdict.
