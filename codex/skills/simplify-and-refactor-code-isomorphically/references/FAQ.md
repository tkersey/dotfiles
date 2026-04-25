# FAQ — friction points agents hit during a pass

> Real questions. Real answers. When in doubt during a pass, ctrl-F here before
> improvising.

## Contents

1. [Before starting a pass](#before-starting-a-pass)
2. [During mapping and scoring](#during-mapping-and-scoring)
3. [During collapse](#during-collapse)
4. [During verification](#during-verification)
5. [Commits, PRs, and the ledger](#commits-prs-and-the-ledger)
6. [Rare and painful situations](#rare-and-painful-situations)

---

## Before starting a pass

### Q1. Tests are flaky. Can I proceed?

No. A flaky baseline makes the refactor unfalsifiable — every failure after
the pass is either the refactor or the flake, and you can't tell which.
Quarantine flaky tests with `#[ignore]` / `skip` / `t.Skip()` in a
dedicated commit *before* the pass starts, linking each quarantine to a
bead. That quarantine commit is part of the baseline.

### Q2. No golden outputs exist and the program has I/O. Must I capture them?

Yes for any deterministic observable output. For non-deterministic outputs
(timestamps, random IDs, network ports), sanitize at capture time. If you
literally cannot make the output deterministic, drop to property tests
for that surface — see [TESTING.md § Layer 3](TESTING.md).

### Q3. Tests take 45 minutes. Do I really run the full suite each commit?

Yes, but offload. Use [rch](../../rch/SKILL.md) or a remote test runner so
your local workstation isn't blocked. Alternatively, run the fast subset
per-commit and the full suite per-PR — but then the PR body must list the
specific full-suite commit that was green.

### Q4. The codebase has no AGENTS.md. What do I assume?

Assume Rule #1 by default: no file deletion without explicit user approval.
Propose to add AGENTS.md at the start of the pass. If the user declines,
proceed with staging (`_to_delete/`) only.

### Q5. The user said "just do it, don't bother with a card." Do I?

Gently decline. The card is cheap (5-10 min), it's the core safety artifact,
and the horror-story evidence in
[REAL-SESSION-EVIDENCE.md](REAL-SESSION-EVIDENCE.md) shows card-less
collapses are where the worst incidents originate. Offer the 30-second
verbal version: *"Which sites, what's observable, what's the lever, what
would break?"* — and fill a minimal card from their answer.

## During mapping and scoring

### Q6. The scanner reports 500+ candidates. How do I pick?

Don't try to do 500 in one pass. Rank by `LOC_saved × Confidence` and take
the top 8-15 for this pass; defer the rest to the next pass's
`duplication_map.md` (the scanner will re-surface them once noise clears
from this pass). Aim for passes of ≤ 20 accepted candidates.

### Q7. A candidate scores 1.9 — just barely under 2.0. Accept anyway?

No. The threshold is a forcing function — relaxing it once erodes the
discipline. Log in rejection_log.md with score; the candidate will probably
re-surface with a stronger score next pass when a third site appears or
confidence rises.

### Q8. Sites look like Type I exact clones but one has different imports.

If the imports are cosmetic (ordering, named aliases) it's still Type I.
If one site imports a different implementation of the same interface, check
whether the implementation has different observable behavior. Usually this
is a Type V rhyme hiding as Type I — reject.

### Q9. I found an `unwrap()` next to a candidate. Fix it during the collapse?

No. That's a drive-by fix; it violates one-lever-per-commit. Capture it in
the card as "observed during mapping; not in scope"; file a bead; continue.

### Q10. The scanner missed duplication that I can see by eye. Add manually?

Yes. Append to `duplication_map.md` with a note `# added-manually`. Scanner
false-negatives are common (esp. for Type III gapped clones). The scanner
is a seed, not a ceiling.

## During collapse

### Q11. The Edit tool keeps failing because old_string isn't unique.

Expand the context window of `old_string` with 3-5 more lines of surrounding
code. If still not unique, use Read to confirm the file content — a prior
session may have changed it. Never fall back to `sed -i`.

### Q12. I need to rename something in 40 files. Really must I Edit each one?

Yes — or spawn 40 parallel [refactor-extractor](../subagents/refactor-extractor.md)
subagents, one per file, each with a narrow scope. The prohibition on `sed`
/ codemods is precisely because silent find-replace has historically
produced the worst regressions (see HS#2 in
[REAL-SESSION-EVIDENCE.md](REAL-SESSION-EVIDENCE.md)). 40 Edits is boring
but safe.

### Q13. A partial collapse is passing tests but feels ugly. Ship it?

If the card says done, the diff matches the card, and the contract is
preserved — yes, ship it. "Ugly" is a separate lever for a future pass.
Don't let an aesthetic itch turn a one-lever commit into a two-lever commit.

### Q14. The new code is SLOWER than the old. What now?

If measurably slower on a hot path, abort — you've broken the perf
observable contract. See
[PERF-AWARE-REFACTOR.md](PERF-AWARE-REFACTOR.md). If negligibly slower
(< 2σ of baseline) on a cold path, note in the card and continue. The
perf-awareness threshold is project-specific.

### Q15. Collapsing would need a `#[cfg(feature = "x")]` to handle both cases.

You're being asked to introduce a feature flag as part of a refactor. Stop.
That's a new axis of behavior, not a simplification. Either (a) both
branches of the feature flag are Type II parametric (then parameterize
without the flag) or (b) they aren't (then the candidate is actually Type V
rhyme — reject).

## During verification

### Q16. `verify_isomorphism.sh` fails on a golden diff by 1 byte.

1 byte is enough to fail. Read the diff. Usual suspects:
- Trailing whitespace normalization (if your editor stripped it)
- Line-ending differences (CRLF vs LF)
- Timestamp in the output that wasn't sanitized
If the byte-diff is genuinely behavioral (output changed), revert the
collapse and re-audit the card.

### Q17. Tests pass but pass-count is 502 → 501. Is that OK?

No. Tests vanishing from the count usually means the collapse removed a
test file or broke test discovery. Read `git diff tests/ __tests__/`. If a
test is genuinely no longer applicable (the symbol was removed), the test
removal must be its own commit with a separate justification.

### Q18. Warning count grew by 3. Must I fix before commit?

Per R-013 the ceiling can't grow. Three options, pick one:
1. Fix the 3 new warnings in this commit (they're usually `unused_import`
   or `unused_variable` from the collapse — trivial).
2. If the warnings are legitimate signal about a deeper issue, revert the
   collapse and re-do it correctly.
3. If the warnings are intentional (rare), explicitly relax the ceiling:
   `./scripts/lint_ceiling.sh relax refactor/artifacts/warning_ceiling.txt +3`
   and document the reason in the commit body.

## Commits, PRs, and the ledger

### Q19. The PR is large because the collapse touches 12 files. Split it?

No. A single lever touching 12 call sites is still one lever. "One lever"
is conceptual, not file-count. Split ONLY if the diff contains multiple
distinct conceptual changes.

### Q20. Should the commit message reveal which sites were rejected?

No, rejections go in `rejection_log.md`, not commit messages. The commit
describes what WAS done. Rejections are pass-level artifacts.

### Q21. The pass produced 9 shipped collapses. Is that a lot?

Typical is 6-15 per pass for a medium-sized project. See
[BENCHMARKS.md](BENCHMARKS.md) for ratios.

## Rare and painful situations

### Q22. I shipped a collapse yesterday. Prod is on fire.

Immediately → see [ROLLBACK-PLAYBOOK.md](ROLLBACK-PLAYBOOK.md). `git revert`
first, postmortem later, update ledger with REVERTED row and rejection_log
with the specific contract that was missed.

### Q23. The user is watching me work and says "go faster."

You can go faster, not lower-discipline. Skip optional comments in the
card, but keep the contract section. Use subagents in parallel to compress
wall-clock time without compressing attention per step.

### Q24. Two candidates conflict — collapsing both would require reasoning
about both changes together.

They're actually one candidate; merge the card. If after merging the
combined score < 2.0, reject both.

### Q25. I'm in the middle of a pass and the user asks me to add a feature.

Stop the pass. Commit whatever is verified-green. Write a mini-closeout
noting you paused mid-pass. Handle the feature. Resume as a new
`pass-<N>-resumed` run-id.

### Q26. A test that was passing before the pass now fails on main, not my
branch. Is that my problem?

No — but it's the next pass's problem. File a bead. Your pass is still
legitimate; your baseline captured main-green-at-commit-X.

### Q27. Is it OK to run two passes in parallel on the same repo?

No. Passes assume exclusive access to `refactor/artifacts/` and to the
warning ceiling. If two refactor agents run concurrently, they clobber each
other's baselines. Use [agent-mail](../../agent-mail/SKILL.md) file-reservation
to serialize. For true parallelism, split by module and run independent
passes per module.
