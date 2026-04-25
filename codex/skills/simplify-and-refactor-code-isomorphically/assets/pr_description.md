# PR: `refactor(<area>): <one-lever summary>`

> One lever per PR. If this PR moves more than one lever, split it — reviewers
> can't isomorphism-check a grab-bag.

## What changed

<one paragraph — the lever, in plain English, no commentary on old code>

## Observable behavior

- [ ] No change to public API signatures (or list exactly what changed)
- [ ] No change to error types / messages escaping the module
- [ ] No change to log / metric / trace field names
- [ ] Goldens byte-identical (or list deltas with justification)
- [ ] No feature-flag added

## LOC and complexity delta

```
Before: <n> LOC in src/
After:  <n> LOC in src/
Δ:      <-n> LOC (-<pct>%)
```

## Isomorphism card

See `refactor/artifacts/<run-id>/cards/<id>.md`.

## Proof

- [ ] Full test suite passes before: `<commit-sha-before>`
- [ ] Full test suite passes after: `<commit-sha-after>`
- [ ] Warning ceiling not exceeded: `<ceiling>` → `<new>`
- [ ] Property test added (if applicable): `<test name>`
- [ ] Goldens diffed: `git diff refactor/artifacts/<run-id>/goldens/`

## Reviewer checklist

- [ ] I verified the isomorphism card matches the diff
- [ ] I re-ran the failing-mode tests in §6 of the card
- [ ] I checked for the pathologies listed in [ANTI-PATTERNS.md](../references/ANTI-PATTERNS.md)
- [ ] I confirmed no `_v2`/`_new` sibling files and no parallel old/new pathway

## Rollback plan

`git revert <this-sha>` is safe because: <why>. If downstream consumers
cached types, they'll need a fresh build but not a schema migration.
