# Reviewer quickstart — 10-minute audit of a skill-produced PR

> You're the PR reviewer, not the refactor-session driver. The skill has
> already shipped a branch. Your job: make sure the diff preserves behavior,
> doesn't sneak in a drive-by, and is revertible. This file gets you done
> in 10 minutes.

## Contents

1. [Before you touch the diff — context](#before-you-touch-the-diff--context)
2. [The 10-minute review checklist](#the-10-minute-review-checklist)
3. [Red flags that auto-fail a PR](#red-flags-that-auto-fail-a-pr)
4. [Verifying locally](#verifying-locally)
5. [How to leave actionable comments](#how-to-leave-actionable-comments)
6. [When in doubt, escalate](#when-in-doubt-escalate)

---

## Before you touch the diff — context

Open, in order:

1. **The isomorphism card.** The PR body should link to
   `refactor/artifacts/<run-id>/cards/<ID>.md`. If no card exists, stop —
   ask the author to add one. Card-less PRs are not reviewable in this
   skill's discipline.
2. **The ledger row** (search `ledger.md` for the candidate ID).
3. **The rejection log** (look for the candidate ID; sometimes prior passes
   rejected it and the author should justify why now is different).

## The 10-minute review checklist

Go in order. Don't skip.

### Minute 0-2: scope

- [ ] Does the diff touch EXACTLY the sites the card lists? If it touches
      more, flag `block: unexpected file changes`.
- [ ] Commit count: should be 1 (or 2 if a pre-refactor quarantine commit
      was needed). > 2 commits = split it.
- [ ] PR title matches `refactor(<area>): <one-lever summary>`.

### Minute 2-5: card vs diff

- [ ] Card says lever `L-EXTRACT`. Is the diff actually an extract? If the
      diff is dispatch, card lied; flag.
- [ ] Card lists N sites. Does the diff visit N sites? Count by eye.
- [ ] For each "hidden difference" in the card, is there a corresponding
      parameter / guard / special-case in the new code?
- [ ] Observable contract fields match: return type, error type, side
      effects, log/metric/trace names.

### Minute 5-7: guardrail checks

Grep the diff for:
- [ ] `any\b` / `as any` / `.unwrap()` / `.expect(` / bare `except:` /
      `@ts-ignore` / `# type: ignore` — new occurrences?
- [ ] `_v2` / `_new` / `tmp_` in added filenames?
- [ ] `catch { }` / empty handler blocks?
- [ ] Feature-flag additions (`process.env.FEATURE_*`, `cfg!(feature = "x")`,
      `if isFeatureEnabled(`)?
- [ ] Deleted tests or modified test assertions?
- [ ] New `pub` exports / `public` members not in the card?

Any hit = `block` or `warn`.

### Minute 7-9: CI artifacts

- [ ] CI warning-ceiling job GREEN
- [ ] CI golden-diff job GREEN (0 bytes of change)
- [ ] CI LOC-delta job shows ≤ 0
- [ ] Test pass count exactly matches main (not just "all green")

### Minute 9-10: revertibility

- [ ] `git revert <sha>` is clean — no subsequent commits have built on
      this one
- [ ] No schema migration in the diff
- [ ] No dependency lockfile change
- [ ] No public-API signature change without an ABI-bump justification

If all boxes pass: `approve`. If any `block` hits: `request changes` with a
one-line justification each.

## Red flags that auto-fail a PR

If you see ANY of these, `request changes` without a second thought:

1. **No isomorphism card linked.** The author skipped the safety artifact.
2. **Card exists but diff-scope mismatch.** Author drifted.
3. **Deleted test cases.** A test going away is a behavioral contract
   change. Must be its own commit with justification.
4. **sed/codemod in session history.** Per [HOOKS.md](HOOKS.md) the hook
   should have blocked; if it got past, the PR isn't trustworthy.
5. **New `_v2.ts` / `parser_new.rs` etc.** Per AGENTS.md Rule #1 and this
   skill's filename policy.
6. **A file deleted without prior user approval in the PR description.**
7. **CI ceiling grew.** Either fix-in-PR or explicit ceiling-relax with
   reason; never silent.
8. **The card's "observable contract" field is one line.** Underspecified;
   the author didn't think it through.
9. **New `unwrap()` on a path that previously had a `?` or a match.**
   Introduced a new panic site.
10. **Commit body doesn't list the lever.** Can't audit what it doesn't
    declare.

## Verifying locally

In < 5 min (with fast tests; longer if the suite is slow, or offload via
[rch](../../rch/SKILL.md)):

```bash
git fetch origin refs/pull/<PR>/head:pr-<PR>
git checkout pr-<PR>

# 1. Re-run the verifier the author should have
./scripts/verify_isomorphism.sh <run-id>

# 2. Diff goldens against main
git diff origin/main -- refactor/artifacts/<run-id>/goldens/

# 3. Warning ceiling check
./scripts/lint_ceiling.sh check

# 4. Spot-check one golden-input manually (the most complex one)
```

If any of those fail locally but CI says green, CI config is lying —
investigate.

## How to leave actionable comments

Good:

> `src/api/users.rs:87` — card says "no side effects" but this line calls
> `audit_log::record(...)`. That's a side effect observable by downstream
> auditors. Either update the card or remove the call.

Bad:

> This feels off.

Every comment should cite file:line, name the contract violation, and
propose a concrete remedy. The reviewer-comments you leave become future
training signal; be rigorous.

## When in doubt, escalate

Cases that aren't your call:

- A collapse crosses a security boundary — ping the security reviewer.
- A collapse is in a hot path — ping whoever owns perf (see
  [PERF-AWARE-REFACTOR.md](PERF-AWARE-REFACTOR.md)).
- A collapse removes ≥ 100 LOC in one commit — pass to a second reviewer
  even if it passes the 10-min check. Big diffs deserve two pairs of eyes.
- A revert of a recent refactor PR — ping the original author plus an
  independent reviewer; read [ROLLBACK-PLAYBOOK.md](ROLLBACK-PLAYBOOK.md).
