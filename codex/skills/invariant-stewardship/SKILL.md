---
name: invariant-stewardship
description: "Use before local patching when bugs, regressions, malformed state, crashes, parser failures, migrations, cache drift, protocol problems, compatibility requests, tolerant readers, fallbacks, coercions, retries, catch-and-continue logic, or local workarounds may broaden accepted invalid state."
---

# Invariant Stewardship

## Mission

Coding agents tend to fix local symptoms by adding local tolerance. Prefer global contract preservation: reduce invalid states, enforce the right boundary, and keep the long-term maintenance surface small.

Use `invariant-ace` for full invariant design. Use this skill as the fast preflight that decides whether the repair belongs at a producer, transition, boundary, migration, compatibility surface, or upstream owner.

## Required reasoning before bug fixes

Before changing code for a bug, regression, malformed state, crash, parser failure, migration problem, cache issue, protocol problem, or compatibility request, identify:

1. The observed failure.
2. The state involved.
3. Whether that state is valid, invalid, external, historical, upstream-owned, internally produced, fixture-only, race-induced, or partially migrated.
4. The invariant that should hold.
5. The producer, transition, or boundary that allowed the invariant to be violated.
6. The boundary where the invariant should be enforced.
7. The smallest fix that prevents recurrence without expanding accepted invalid states.

Prefer fixes that make invalid states impossible. Do not merely make the downstream consumer tolerate invalid internal state unless historical data, external input boundaries, or explicit product requirements make that necessary.

## State classification

| State kind | Meaning | Preferred action |
|---|---|---|
| Valid domain state | State is part of the intended model | Support it directly and test the contract |
| Invalid internal state | This repo produced impossible state | Fix the writer/transition; add invariant tests |
| Historical persisted bad state | Old releases may already have written it | Prevent future writes; add narrow migration or repair path |
| External untrusted input | User/service input may be malformed | Validate at the boundary; return clear errors |
| Public API legacy input | Compatibility is a product/API promise | Add documented compatibility path with tests |
| Upstream-owned state | Dependency/gateway/protocol produced it | Prefer upstream fix/report; local workaround only with explicit tradeoff |
| Fixture-only state | Test setup created impossible production state | Fix the fixture; do not expand production behavior |
| Race/partial-write state | Ordering or atomicity allowed intermediate state | Fix atomicity/ordering; avoid retrying everywhere |
| Partially migrated state | Migration path can leave mixed versions | Make migration idempotent/narrow; preserve invariant after migration |

## Complexity budget

Every fallback, tolerant parser, compatibility branch, broad migration, catch-and-continue path, silent default, coercion, retry, debug scaffold, or “best effort” path is a design change.

Before adding one, answer:

- What new state, format, or behavior becomes accepted?
- Does this hide a producer bug?
- Does this create a backward-compatibility obligation?
- Will future writers, readers, exporters, compactors, analyzers, or docs need to preserve this behavior?
- Is the complexity temporary, explicit, and tested?
- Is there a smaller invariant-preserving fix instead?

Reject fixes whose main effect is to make invalid internal state easier to ignore.

## Invariant-oriented tests

A passing test is not enough. The test must encode the intended invariant, not merely prove the local symptom no longer crashes.

For bug fixes, tests should usually prove one of:

- the invalid state can no longer be produced;
- the boundary rejects invalid input clearly;
- historical invalid data is migrated narrowly;
- the upstream workaround is isolated and documented;
- the state transition preserves the invariant;
- the repair does not broaden accepted malformed state.

## Output contract

When this skill materially affects the route, leave an invariant receipt:

```text
Invariant Receipt:
- observed failure:
- state classification:
- invariant:
- owner/boundary:
- rejected tolerance path:
- repair:
- proof:
```
