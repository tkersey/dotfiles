# Team adoption — rolling this skill out across an engineering org

> A refactor skill used by one agent on one branch is a tool. Adopted
> across a team, it becomes a discipline. This file is the playbook for
> that transition — the maturity ladder, the social patterns, and the
> predictable pushback.

## Contents

1. [Maturity ladder — L0 through L3](#maturity-ladder--l0-through-l3)
2. [L0 → L1 transition](#l0--l1-transition)
3. [L1 → L2 transition](#l1--l2-transition)
4. [L2 → L3 transition](#l2--l3-transition)
5. [Pair-programming protocol](#pair-programming-protocol)
6. [Onboarding a new team member](#onboarding-a-new-team-member)
7. [Handling pushback](#handling-pushback)
8. [Anti-patterns during adoption](#anti-patterns-during-adoption)

---

## Maturity ladder — L0 through L3

**L0 — Ad-hoc.** Nobody uses the skill. Refactors happen inconsistently,
usually as drive-bys inside feature PRs. No cards, no ledger, no rejection
log. This is where most teams start.

**L1 — Per-sprint pass.** One engineer (or agent) runs a refactor pass
each sprint. The pass produces a ledger and closeout. The rest of the team
reviews the PRs but doesn't run their own passes.

**L2 — Per-PR hooks.** Git hooks + CI gates are installed. The skill's
discipline is enforced automatically on every PR. Any engineer can start
a pass; the tooling catches violations regardless of who authored them.
Rejection log is actively maintained.

**L3 — Continuous refactor automation.** Refactor passes are partially
automated. Nightly scans surface candidates. A bot proposes PRs for
unambiguous collapses; humans review. Warning ceiling decays month over
month. The skill is part of the team's operational loop, not a special
event.

Most teams stop at L2. L3 is worth pursuing only for repos with > 200k
LOC and > 10 engineers.

## L0 → L1 transition

**Who:** One senior engineer or a trusted agent.

**Signals you're ready:**
- At least one test suite exists and is mostly green.
- A code reviewer culture exists (PRs aren't auto-merged).
- Team has felt pain from a recent refactor gone wrong.

**How:**
1. Run [COLD-START.md](COLD-START.md) to build the baseline.
2. Announce the first pass in writing: *"This sprint I'm running a
   refactor pass per the simplify skill. Expect ~8-15 small PRs with
   `refactor(...)` titles. Each has a card and a ledger entry. Review
   time per PR should be ≤ 10 min."*
3. Run the first pass. Expect it to take 2× the skill's estimated time
   because you're building muscle memory.
4. Post the closeout summary. Collect feedback.

**What "done" looks like:**
- One full pass closed out.
- Ledger exists with ≥ 5 shipped rows.
- No incidents from the pass.
- Team has seen an isomorphism card.

## L1 → L2 transition

**Who:** The engineer who ran the first L1 pass, plus a tools/infra
engineer.

**Signals you're ready:**
- L1 has been in place for ≥ 2 sprints.
- At least one contributor other than the L1 runner has read SKILL.md.
- Someone has noticed that PRs in this project are subtly better than
  PRs in peer projects.

**How:**
1. Install git hooks per [GIT-HOOKS.md](GIT-HOOKS.md).
2. Install CI gates per [CI-CD-INTEGRATION.md](CI-CD-INTEGRATION.md).
3. Enable cc-hooks per [HOOKS.md](HOOKS.md) for agents working in the
   repo.
4. Add `AGENTS.md` with the refactor protocol if not already present.
5. Run a "dry" refactor pass to verify the gates fire correctly on a
   simulated violation.
6. Announce: *"Refactor gates are now live on every PR. Expect your
   next PR to possibly hit one. See FAQ if it blocks you."*
7. Point people at [FAQ.md](FAQ.md) and [REVIEWER-QUICKSTART.md](REVIEWER-QUICKSTART.md).

**What "done" looks like:**
- A PR has been blocked by a gate (at least once), and the author fixed
  the issue rather than bypassing.
- Rejection log has ≥ 10 entries.
- Warning ceiling has decreased since L1.

## L2 → L3 transition

**Who:** Platform team.

**Signals you're ready:**
- L2 has been stable for ≥ 3 months.
- The refactor-pass cadence is predictable.
- The team trusts the tooling enough that gate-blocked PRs aren't
  manually bypassed.

**How:**
1. Schedule a nightly `dup_scan` + `ai_slop_detector` job. Commit the
   output as a dashboard artifact, not as PRs.
2. Each Monday, an agent (or person) picks the top 3 candidates from
   the nightly scan and proposes PRs for each via the
   [refactor-extractor subagent](../subagents/refactor-extractor.md).
3. Human reviewers approve or reject.
4. Shipped PRs are auto-linked to the ledger via
   [`ledger_row.sh`](../scripts/ledger_row.sh) running in CI.

**What "done" looks like:**
- The refactor cadence is decoupled from any specific human's attention.
- LOC-per-month decreases consistently (see [BENCHMARKS.md](BENCHMARKS.md)).
- The rejection log is a teaching artifact new hires read.

## Pair-programming protocol

When two humans (or a human and an agent) work on the same pass:

1. **Driver** runs the skill's loop and owns the commits.
2. **Navigator** reads the isomorphism card in real time, asks
   questions, proposes audit challenges.
3. Switch roles every candidate. The navigator-who-asks-questions
   becomes the driver-who-answers-them; the role switch itself is
   the knowledge-transfer mechanism.

Agent-as-navigator can be powerful: spawn the
[isomorphism-auditor subagent](../subagents/isomorphism-auditor.md) per
card, and let it challenge your human driver's reasoning.

## Onboarding a new team member

Day-1 reading order (~2 hours):

1. [SKILL.md](../SKILL.md) — first 50 lines, then the rest.
2. [QUICK-REFERENCE.md](QUICK-REFERENCE.md) — memorize the loop and
   scoring formula.
3. [GLOSSARY.md](GLOSSARY.md) — skim.
4. [COOKBOOK.md](COOKBOOK.md) — read one recipe per clone type.
5. [REVIEWER-QUICKSTART.md](REVIEWER-QUICKSTART.md) — in 10 min.
6. Your team's most recent `CLOSEOUT.md`.
7. Your team's `rejection_log.md` — this is where the taste lives.

Day-2-5: have them review 3 skill-produced PRs before driving their own
pass. Use [REVIEWER-QUICKSTART.md](REVIEWER-QUICKSTART.md) and audit the
review against the checklist.

First independent pass: cap at 3-5 candidates. Expect 1 revert — that's
the learning.

## Handling pushback

Common objections and responses:

**"This is over-engineered for our size."**
→ Start with L1, not L2. L1 is maybe 15 min/week of overhead and
produces a ledger that auditors will love.

**"Cards slow me down."**
→ Measure. Cards take ~10 min each. The time-to-rollback when a refactor
breaks prod is often hours. Net-positive.

**"I can tell these two functions are the same, I don't need a card."**
→ Then the card takes 30 seconds. Write it anyway — future-you won't
remember. And the `observable contract` field is where subtle bugs hide;
writing it down often changes your mind about the collapse.

**"The discipline assumes I'm incompetent."**
→ It assumes the system is complex enough that individual competence
isn't enough. Aviation checklists aren't about pilot skill; they're
about recoverable systems. Same argument.

**"This is what CI is for."**
→ CI catches syntactic and numeric violations. The card catches
contract-level violations CI can't see.

## Anti-patterns during adoption

- **Mandating from above without doing a pass yourself first.** Leaders
  who haven't felt the discipline won't understand the pushback or
  know which shortcuts are safe. Run at least one pass before decreeing.
- **Enforcing L2 gates before the team has seen L1.** Gates without
  context feel arbitrary. Let people see the method produce results
  before the gates start rejecting their PRs.
- **Treating the rejection log as a graveyard.** It's a living taste
  document. Re-read it each pass; sometimes the right candidate to
  reconsider is the one rejected 3 passes ago.
- **Skipping `CLOSEOUT.md`.** The closeout is where the learning lives.
  No closeout = no learning = the next pass makes the same mistakes.

See [FLYWHEEL-INTEGRATION.md](FLYWHEEL-INTEGRATION.md) for feeding pass
lessons back into the skill itself.
