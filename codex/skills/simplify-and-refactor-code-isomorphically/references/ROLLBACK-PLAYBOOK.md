# Rollback playbook — when a shipped collapse breaks prod

> A collapse that passed every gate can still fail in production if the
> gates missed something (usually a contract the card didn't enumerate).
> When this happens, speed and discipline both matter. This playbook is
> the fast-path.

## Contents

1. [Immediate actions (first 10 min)](#immediate-actions-first-10-min)
2. [Stabilization (first 60 min)](#stabilization-first-60-min)
3. [Postmortem (same day)](#postmortem-same-day)
4. [Updating the ledger and rejection log](#updating-the-ledger-and-rejection-log)
5. [Updating the isomorphism card](#updating-the-isomorphism-card)
6. [Updating the scanner / hooks to prevent recurrence](#updating-the-scanner--hooks-to-prevent-recurrence)
7. [Human loop — what to tell the team](#human-loop--what-to-tell-the-team)

---

## Immediate actions (first 10 min)

**Step 1. Revert, don't debug forward.**

```bash
git checkout main
git pull
git revert <sha-of-refactor-commit> --no-edit
git push
```

If the PR contained multiple commits, revert them in reverse order. Do NOT
attempt to fix-forward — a fix-forward under incident pressure is how
horror-story HS#1 happened.

**Step 2. Trigger the deploy.**

Your CD pipeline should deploy the revert automatically. If not, deploy
manually. Wait for the health checks.

**Step 3. Announce.**

Post in the incident channel: *"Reverting
`refactor(<area>): <summary>` (sha <sha>) — <one-line symptom>. Deploy in
progress."*

Keep the announcement factual. No blame, no speculation.

## Stabilization (first 60 min)

Once the revert is deployed and prod is healthy:

- [ ] Verify the alert cleared and metrics returned to baseline.
- [ ] Search for collateral damage — did the bad version poison any cached
      data, queued messages, or async side effects?
- [ ] If yes, triage those separately. The revert doesn't fix persisted bad
      state.
- [ ] Lock the refactor branch from re-merge attempts. Tag it
      `rolled-back-<date>` so a careless bot doesn't re-open it.

## Postmortem (same day)

Write a **blameless** postmortem. Structure:

```markdown
# Postmortem — <incident-id>: <summary>

## Timeline
- HH:MM — PR merged (sha <sha>)
- HH:MM — Deploy to prod
- HH:MM — First alert fired (<metric>)
- HH:MM — Revert merged
- HH:MM — Deploy revert
- HH:MM — All-clear

## Impact
- Users affected: ~N
- Duration: ~N min
- Data affected: <yes/no — description>

## Root cause
<one paragraph — what exactly did the old vs new code do differently that
the card did NOT capture>

## What the card missed
<specific field — usually "observable contract" or "hidden differences" —
and the exact divergence that wasn't listed>

## Why the gates missed it
- Tests: <did the specific case have a test? if not, why not?>
- Goldens: <did any golden input exercise the case?>
- Property tests: <did we have one? did it miss? why?>
- Reviewer: <did they audit the card? did the card mislead them?>

## Action items
1. Update the candidate's isomorphism card with the missed divergence.
2. Update rejection_log.md: this collapse is permanently rejected.
3. Add a regression test that would have caught this.
4. [Optional] Update scanner / hooks to catch future variants.
5. [Optional] Update DUPLICATION-TAXONOMY.md if this is a new kind of
   rhyme.
```

## Updating the ledger and rejection log

**Ledger** (append, don't delete):

```
| ISO-014 | II | 3 | extract helper | 42 | M | green | abc1234 | REVERTED: def5678 |
```

Below, in the REVERTED section:

```
| ISO-014 | abc1234 | def5678 | <incident-id>: <one-line root cause> |
```

**Rejection log** (new permanent entry):

```
### ISO-014 — post-revert permanent rejection
- **Originally shipped:** 2026-05-12 (commit abc1234)
- **Reverted:** 2026-05-13 (commit def5678)
- **Incident:** INC-2026-0042
- **Root cause:** sites diverged in <specific contract aspect> — card's
  "hidden differences" section missed this because <reason>.
- **Classification retroactively:** clone type V (accidental rhyme).
- **Do not re-propose.** The candidate will re-surface in future scans;
  the scanner output must be ignored for these sites.
- **Notes:** if <specific future change> happens, reconsider — but only
  with a new card audited by two independent agents.
```

This row stays forever. Future refactor passes will see it.

## Updating the isomorphism card

Re-save the original card to `cards/ISO-014.md` with a new section:

```markdown
## REVERT ADDENDUM

This card was completed and the collapse shipped on 2026-05-12. The commit
was reverted on 2026-05-13 due to <incident>.

### What the card missed
<exact field and content>

### Why this matters for future cards
<generalized lesson — e.g., "when sites appear to have the same logging
behavior, verify that log-level filters in the ambient config don't
differ between sites">

### Fixture / test that would have caught it
```<language>
<minimal repro code>
```
```

This addendum is the learning artifact. It goes into
[CASE-STUDIES.md](CASE-STUDIES.md) eventually.

## Updating the scanner / hooks to prevent recurrence

If the root cause reveals a detectable pattern, upgrade the tooling so the
next session catches it automatically.

- If the card missed a specific observable (e.g., "log level differs
  silently"), add a check to the
  [isomorphism-auditor subagent](../subagents/isomorphism-auditor.md).
- If the pattern is a new type of rhyme, add a detection heuristic to
  [`ai_slop_detector.sh`](../scripts/ai_slop_detector.sh).
- If a hook would have caught it pre-commit, add to
  [HOOKS.md](HOOKS.md) and [GIT-HOOKS.md](GIT-HOOKS.md).

Each of these is its own commit. Don't bundle the tooling fix with the
revert.

## Human loop — what to tell the team

**During incident:** short, factual status updates. Don't speculate.

**After revert:** one message linking the postmortem draft. Invite
comments for ≥ 24h.

**After postmortem:** circulate the action items. Assign owners. Track in
beads.

**What NOT to do:**
- Do not apologize personally. The refactor followed the discipline; the
  discipline had a gap. Fix the discipline.
- Do not promise "we'll be more careful." Promise the specific tooling
  upgrade that makes this class of bug undetectable-by-tooling impossible
  to ship again.
- Do not retire the skill. One incident is a learning, not a rebuke.

See [TEAM-ADOPTION.md](TEAM-ADOPTION.md) for how to use the postmortem as
a team-wide learning event rather than a blame vector.
