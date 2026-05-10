# Closure gates reference

Use these gates together. A single green result does not close the artifact set.

## Direct changed path

This gate is closed only when the changed behavior or claimed bug fix is exercised directly.
Indirect success does not close it.

Statuses:
- `satisfied`
- `open`
- `blocked`
- `conflicting`

## Claimed failure mechanism

This gate is closed when the evidence exercises the mechanism the diagnosis claims to fix.
A passing test on a nearby path is not enough.

Statuses:
- `satisfied`
- `open`
- `blocked`
- `conflicting`

## Regression surface

This gate is closed when at least one plausible adjacent contract, caller, or invariant surface has been checked directly or bounded convincingly.

Statuses:
- `satisfied`
- `open`
- `blocked`
- `conflicting`

## Critical invariants

These are closure blockers unless they are preserved or directly bounded.

Statuses:
- `preserved`
- `strained`
- `broken`
- `unknown`

## Material foot-guns

Use this gate for misuse paths, unsafe defaults, retries, rollbacks, migrations, and operational hazards.
A happy-path pass does not close this gate.

Statuses:
- `bounded`
- `unbounded`
- `unknown`
- `accepted-risk`

## Material complexity hazards

Use this gate only when incidental complexity creates a concrete risk chain: fragility, coupling, lost reviewability, lost testability, or operational burden.

Statuses:
- `bounded`
- `unbounded`
- `unknown`
- `residual-design-risk`

## Negative evidence closure gate

Use this gate for active, current-state-applicable negative evidence: failed hypotheses, reverted routes, no-effect attempts, benchmark regressions, review-rejected fixes, and repeated dead-end hypotheses.

This gate is closed only when active negative evidence does not conflict with the current route, or when reopening criteria are satisfied by current proof.

Fields:
- `status`: `satisfied` | `open` | `blocked` | `unavailable`
- `active_exclusions_count`
- `repeated_failed_route_used`
- `reopening_criteria_satisfied`
- `learnings_hits_applicability_checked`
- `reason`

Statuses:
- `satisfied`: no active applicable negative evidence blocks the route, or reopening criteria are satisfied with proof
- `open`: active applicable negative evidence conflicts with the current route and reopening criteria are not satisfied
- `blocked`: relevant evidence exists but cannot be checked
- `unavailable`: negative-ledger/learnings tooling is unavailable and no in-session evidence can check the relevant source

A passing test suite does not close this gate if the current route repeats a previously disconfirmed path without a new witness.

## Briefing agreement

This gate summarizes reviewer and specialist alignment.
If results materially conflict, do not average them away. Resolve with a check or mark the call indeterminate.

Statuses:
- `aligned`
- `mixed`
- `conflicting`

## External blockers

Use this gate for missing environment, missing secrets, unavailable history, unavailable learnings, inaccessible CI, or user decisions.

Statuses:
- `none`
- `present`
