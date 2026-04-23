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

## Briefing agreement

This gate summarizes reviewer and specialist alignment.
If results materially conflict, do not average them away. Resolve with a check or mark the call indeterminate.

Statuses:
- `aligned`
- `mixed`
- `conflicting`
