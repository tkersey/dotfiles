# Exit criteria — precise "done" gates and time-boxes per phase

> Sessions drift when "done" is fuzzy. This file defines, for each phase,
> exactly what must be true to move on — and how long you're allowed to
> spend trying before you escalate.

## Contents

1. [Why time-box](#why-time-box)
2. [Phase-by-phase gates](#phase-by-phase-gates)
3. [Whole-pass exit gate](#whole-pass-exit-gate)
4. [When you blow the time-box](#when-you-blow-the-time-box)
5. [The "red rope" signals](#the-red-rope-signals)

---

## Why time-box

Without a clock, a refactor session sprawls — one candidate becomes a
rewrite, one rewrite becomes a redesign, a redesign becomes "maybe this
isn't the right architecture." The skill's discipline is *small, verifiable
levers*; time-boxes enforce that.

Time-boxes are **guidelines, not fire alarms.** If you blow one by 20%,
you're fine. If you blow one by 2×, stop and reconsider — you're probably
doing the wrong thing.

## Phase-by-phase gates

Numbers below are for a medium-sized project (~50k LOC). Scale linearly for
larger/smaller.

### Phase 0 — Bootstrap

**Exit when:**
- [ ] `skill_inventory.json` exists at `refactor/artifacts/<run-id>/`
- [ ] jsm state recorded (installed / absent / declined)
- [ ] Any missing sibling siblings either installed OR have their fallback
      plan acknowledged

**Time-box: ≤ 10 min.** If sibling installs take longer, defer them —
every sibling has an inline fallback per
[JSM-BOOTSTRAP.md](JSM-BOOTSTRAP.md).

### Phase A — Baseline

**Exit when:**
- [ ] `baseline.md` written
- [ ] `tests_before.txt` captures the full test runner output
- [ ] Test pass count is ≥ 0 failures OR the N failures are named and
      quarantined with a beads reference (no silent failures)
- [ ] Goldens captured for every observable I/O boundary
- [ ] LOC snapshot recorded
- [ ] Warning ceiling snapshot recorded

**Time-box: ≤ 20 min.** If the test suite takes > 20 min to run, offload
via [rch](../../rch/SKILL.md) and do it async while you work on Phase B.

**Red flags:**
- Tests that sometimes pass, sometimes fail → quarantine first (not part
  of this phase's time-box)
- No deterministic outputs exist → drop to property tests, see
  [TESTING.md](TESTING.md)

### Phase B — Map

**Exit when:**
- [ ] `duplication_map.md` has ≥ 1 candidate (even if the answer is "none")
- [ ] `slop_scan.md` exists
- [ ] `unpinned_deps.md` exists
- [ ] Every candidate has an ID, clone type, site list, estimated LOC
      saved, lever suggestion
- [ ] Type-V rhymes are explicitly flagged in a "Do not collapse" section
      BEFORE anything gets scored

**Time-box: ≤ 30 min** (scanner runtime dominates; don't skip the manual
pass after).

**Red flags:**
- > 80 candidates — cap the list and defer the tail; see
  [FAQ.md Q6](FAQ.md)
- 0 candidates in a known-large codebase — the scanner config is wrong;
  check language filters

### Phase C — Score

**Exit when:**
- [ ] Every candidate has a score
- [ ] Every candidate is ACCEPTED, REJECTED, or BLOCKED (awaiting user
      input) — no "unclear" state
- [ ] Each REJECTED has a rejection reason in `rejection_log.md` with
      score and reason-code
- [ ] Top 8-15 ACCEPTED are ordered for the pass; the rest are deferred
      to next-pass with a note

**Time-box: ≤ 15 min.** Scoring is mostly mechanical
(`./scripts/score_candidates.py`); the time goes to the ACCEPT/REJECT calls.

**Red flags:**
- 100% of candidates accepted → you're not rejecting; the threshold is
  too loose or the scanner is under-reporting rhymes
- 0% accepted → either the project really is clean or you're
  risk-averse-misreading; compare against [BENCHMARKS.md](BENCHMARKS.md)

### Phase D — Prove (isomorphism card)

**Exit when (per candidate):**
- [ ] Isomorphism card filled with ALL required fields (identity, sites,
      observable contract, hidden diffs, proof strategy, risk, UBS prompts,
      commit plan)
- [ ] Every site in the card has been READ in full (not just the 20-line
      window)
- [ ] Card is audited by the [isomorphism-auditor subagent](../subagents/isomorphism-auditor.md)
      OR a second agent with READY verdict

**Time-box: ≤ 15 min per candidate.** If a card takes > 30 min, the
candidate is too big — split or reject.

**Red flags:**
- "Observable contract" field is one line — underspecified, will bite
  in review
- No "hidden differences" section — you didn't actually look

### Phase E — Collapse (one lever)

**Exit when (per candidate):**
- [ ] Code edit performed via Edit tool only (no sed/codemod)
- [ ] Single conceptual change matches the card's lever
- [ ] No new `any`/`unwrap`/bare except:/`ignore` in the diff
- [ ] No new feature flags
- [ ] No new `_v2`/`_new`/`tmp_` filenames
- [ ] Commit created with message matching [FORMULAS.md](FORMULAS.md)

**Time-box: ≤ 20 min per candidate.** Bigger means the lever is too big.

**Red flags:**
- Diff touches files not in the card — drive-by fix creeping in
- Diff deletes a test — verboten unless in a separate commit with
  explicit justification

### Phase F — Verify

**Exit when:**
- [ ] `./scripts/verify_isomorphism.sh <run-id>` exits 0
- [ ] Test pass count EXACTLY matches baseline (identical set of failures)
- [ ] Goldens diff byte-identical
- [ ] Warning count ≤ ceiling
- [ ] LOC delta recorded

**Time-box: ≤ 15 min** (mostly test runtime; use rch if slow).

**Red flags:**
- Any gate fails → REVERT. Do not debug forward. Revert → re-audit the
  card → retry.

### Phase G — Ledger and handoff

**Exit when (per candidate):**
- [ ] Ledger row appended via `./scripts/ledger_row.sh`
- [ ] Bead closed with commit-SHA link

**Time-box: ≤ 5 min per candidate.**

## Whole-pass exit gate

Before closing a pass (writing CLOSEOUT.md), confirm:

- [ ] Every ACCEPTED candidate is either SHIPPED or REVERTED
      (no "still in progress")
- [ ] `CLOSEOUT.md` written per [FORMULAS.md template](FORMULAS.md)
- [ ] Dashboard updated
- [ ] LOC delta, ship/reject ratio, warning-ceiling delta recorded
- [ ] Follow-ups filed as beads
- [ ] Surprises-and-lessons section is 3-5 sentences, not empty

**Typical whole-pass duration:** 2-4 hours for 8-15 candidates. If > 6
hours, you're doing two passes worth of work in one — split next time.

## When you blow the time-box

1. **20% over** — keep going, no action needed.
2. **50% over** — pause. Ask yourself: am I doing the right thing? Is this
   candidate too big? Is there a simpler lever?
3. **2× over** — stop. Commit what's verified-green. Write a partial
   closeout. Reconsider the candidate — often it's a type-V rhyme you
   didn't recognize, or a type-III gap that needs its own pass.

Never push through a 2× blow to "finish it." That's how horror-story HS#1
happened (per [REAL-SESSION-EVIDENCE.md](REAL-SESSION-EVIDENCE.md)).

## The "red rope" signals

If any of these fire, pause the whole pass regardless of time-box:

- Test count changed (not just pass count)
- A goldens file appeared or disappeared
- A sibling test file was modified
- `.env` or secrets changed
- A dependency lockfile changed
- A migration file was added
- The diff grew outside `src/` into infra or config

Each signal is a "not just a refactor" indicator. Handle it as a separate
commit with its own justification. See
[ROLLBACK-PLAYBOOK.md](ROLLBACK-PLAYBOOK.md) if you realize this
post-commit.
