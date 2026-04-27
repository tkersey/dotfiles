# Risk Tiering Reference

## Tier 0: Mechanical

Formatting, comments, obvious generated-file updates, compiler-assisted rename, dead-code removal with coverage.

Verification: inspect diff, run formatting/lint/build if relevant. Output: one short verification note, not a full report.

## Tier 1: Local behavioral

Single-function behavior, isolated bug fix, targeted UI behavior, parser/validator adjustment.

Verification: inspect callers, add/update focused tests, run targeted test suite. Output: compact report.

## Tier 2: System-affecting

API contract, schema or migration, queue/worker behavior, caching, cron, feature flags, auth-adjacent paths, billing-adjacent paths, performance-sensitive logic.

Verification: plan first, map blast radius, add regression and integration tests. Output: full Verification Gap Report with rollout/rollback notes.

## Tier 3: High-risk or irreversible

Payments, billing, security controls, permissions, data deletion, privacy/compliance, public API breakage, production infrastructure, irreversible migrations.

Verification: produce a plan, identify approval points, avoid irreversible actions unless explicitly authorized. Output: full Verification Gap Report with strong rollback and monitoring guidance.
