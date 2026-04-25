# Anti-Patterns II — swarm, long-session, and rescue contexts

> [ANTI-PATTERNS.md](ANTI-PATTERNS.md) covers the core anti-patterns. This file adds the ones that only emerge in specific contexts: multi-agent swarms, long-running sessions, rescue missions, and refactors that cross with other skills.

## Contents

1. [Swarm anti-patterns](#swarm-anti-patterns)
2. [Long-session anti-patterns](#long-session-anti-patterns)
3. [Rescue-mission anti-patterns](#rescue-mission-anti-patterns)
4. [Cross-skill anti-patterns](#cross-skill-anti-patterns)
5. [Orchestrator anti-patterns](#orchestrator-anti-patterns)
6. [Meta anti-patterns (how the skill gets misused)](#meta-anti-patterns-how-the-skill-gets-misused)

---

## Swarm anti-patterns

### S-AP-1: Racing for the same bead

Two workers both `br update <id> --status=in_progress` at nearly the same time. Both edit. Commits collide.

**Cause:** workers don't check `br list --status in_progress` before claiming.
**Fix:** `br update --status=in_progress --owner=<me>` is atomic. After claim, verify owner:
```bash
br show <id> --json | jq '.owner' | grep -q "refactor-worker-01" || { echo "conflict"; exit 1; }
```

### S-AP-2: Over-wide file reservations

Worker reserves `src/**` because they don't know what they'll touch. Blocks every other worker for an hour.

**Fix:** start narrow. If a refactor expands scope, release + re-reserve. `renew_file_reservations` extends the TTL without changing paths.

### S-AP-3: Forgetting to release reservations on failure

Worker hits a verify failure, aborts, exits pane. Reservations hang around until TTL expires (up to an hour).

**Fix:** use `defer`/`trap` equivalent:
```bash
trap 'release_file_reservations(...)' EXIT
```
Or in the orchestrator recovery loop, proactively release-on-stuck (per [AGENT-COORDINATION.md](AGENT-COORDINATION.md)).

### S-AP-4: Stealing another worker's reservation

Worker A is slow. Worker B calls `force_release_file_reservation`, takes over, causes a collision when A returns.

**Rule:** only the orchestrator force-releases, and only after confirming the worker is stuck per the recovery playbook.

### S-AP-5: Workers editing without seeing each other's commits

Worker A commits D1; Worker B started D2 before D1 merged. B's working tree doesn't have D1's changes. B's merge conflict is painful.

**Fix:** workers `git pull --rebase` before each commit. Merge conflicts during rebase are fine — resolve per standard practice.

### S-AP-6: LEDGER.md corruption from concurrent appends

Two workers append without `flock`. File ends up truncated or with interleaved lines.

**Fix:** always `flock`:
```bash
flock refactor/artifacts/<run>/LEDGER.md -c "echo '<row>' >> refactor/artifacts/<run>/LEDGER.md"
```

### S-AP-7: Workers disagreeing on the isomorphism card

Worker A fills the card for D1 optimistically. Worker B, reviewing, disagrees. No resolution mechanism.

**Fix:** the orchestrator is the card arbiter. Workers post their card draft to Agent Mail; orchestrator approves or asks questions. Only after approval does the worker edit code.

---

## Long-session anti-patterns

### L-AP-1: Running Phase E without re-running Phase A

Agent has been editing for 2 hours. Started with tests green. Hasn't re-run tests since Phase D. Is the baseline still valid?

**Rule:** if > 30 minutes since the last `baseline.sh` run, re-run before the next commit. Drift is cheap to catch, expensive to discover.

### L-AP-2: Scope creep within a single session

Started: "refactor messaging.rs." Now: "refactor messaging.rs + update error types + rename UserError + fix a TODO in payment.rs."

**Fix:** when the agent notices an out-of-scope improvement, file a bead and keep going. Don't expand the current pass.

### L-AP-3: Cognitive fatigue → incomplete isomorphism cards

By candidate D7, the agent is typing "N/A" on axes it really should consider. Quality degrades with session length.

**Fix:** hard stop at ~8 accepted candidates per session. Or: at candidate D5, explicitly re-read [ISOMORPHISM.md](ISOMORPHISM.md) axes to refresh.

### L-AP-4: Commit-message drift

Early commits have pristine isomorphism cards. Later commits drop to "refactor: simplify foo". Future reviewers can't audit.

**Fix:** the commit message template is mandatory for every refactor commit:
```
refactor(<scope>): <one-line>

[isomorphism card verbatim]

LOC: ...
```

No exceptions. Even the 8th of the session.

### L-AP-5: Not updating the ledger live

Agent fills the card, edits, verifies, commits. Saves the ledger for "end of session." Then forgets one or two rows.

**Fix:** ledger row goes in immediately after verify passes, before the next candidate. Use `scripts/ledger_row.sh`.

---

## Rescue-mission anti-patterns

### R-AP-1: Skipping Phase −1 because "the tests aren't that bad"

Starting the main loop with 15 flaky tests. "They pass most of the time."

**Result:** every refactor commit triggers 1-2 test failures that aren't your fault. Reviewers lose trust; your real bugs slip through because they look like flake.

**Fix:** quarantine first. Specific reason per `#[ignore]`. Bead per quarantine.

### R-AP-2: "Fix all the warnings" as a rescue goal

Hundreds of clippy / eslint warnings. Agent bulk-fixes.

**Result:** a 500-file PR mixing unrelated fixes. Impossible to review. Bugs introduced.

**Fix:** cap the count (RESCUE-MISSIONS.md §Phase −1c). Reduce one per candidate during normal passes. Never bulk-fix warnings during a rescue.

### R-AP-3: Adding new tests using brittle mocks

Rescue needs coverage. Agent generates tests that heavily mock. Tests don't catch real bugs; they pass even when the real system is broken.

**Fix:** per [RESCUE-MISSIONS.md §Phase 0](RESCUE-MISSIONS.md#phase-0-grow-a-test-net): golden-path integration tests (real services) and property tests. Mocks only when genuinely unavoidable.

### R-AP-4: Renaming during rescue

"While I'm here, I'll rename `FooManager` to `FooService`."

**Result:** the rescue PR touches 40 files for a rename that has nothing to do with stabilization. Reviewers can't tell what's fixing and what's renaming.

**Fix:** [RESCUE-MISSIONS.md §"The non-hostile refactor rule"](RESCUE-MISSIONS.md#the-non-hostile-refactor-rule). Renames are hostile during rescue.

### R-AP-5: Extending rescue indefinitely

Rescue goes for 4 weeks. Team has produced zero features. Morale drops.

**Fix:** rescue has exit criteria ([RESCUE-MISSIONS.md §"When to run the main loop vs. more triage"](RESCUE-MISSIONS.md#when-to-run-the-main-loop-vs-more-triage)). When the checklist passes, exit to normal mode. Log remaining issues as beads, don't block.

---

## Cross-skill anti-patterns

### C-AP-1: Refactor + optimization in the same commit

Commit does both a Type II collapse AND a `Vec::with_capacity` perf tweak.

**Fix:** separate. The skill responsible for each is different ([extreme-software-optimization](../../extreme-software-optimization/SKILL.md) for perf). Each deserves its own isomorphism card.

### C-AP-2: Refactor blocked on profiling-first

Agent refuses to refactor anything because "we need to profile first."

**Fix:** profiling is required before *optimization*. Refactoring is allowed without profiling — the isomorphism card preserves behavior, not performance characteristics. If the refactor reveals a perf issue, log a bead; don't block.

### C-AP-3: Security refactor without [security-audit-for-saas](../../security-audit-for-saas/SKILL.md)

Refactoring auth / session / rate-limit code without the security skill's guidance.

**Fix:** see [SECURITY-AWARE-REFACTOR.md](SECURITY-AWARE-REFACTOR.md). Don't refactor security boundaries without the security card.

### C-AP-4: Bypassing [ubs](../../ubs/SKILL.md) because "it's a refactor, no new code"

The skill's `verify_isomorphism.sh` calls UBS automatically. But some agents skip when time-pressed.

**Fix:** UBS is mandatory per AGENTS.md. Exit >0 → don't commit. Period.

### C-AP-5: Running the skill during a multi-pass-bug-hunting session

The agent conflates "clean up" with "fix bugs." The PR has bug fixes AND refactors interleaved.

**Fix:** [multi-pass-bug-hunting](../../multi-pass-bug-hunting/SKILL.md) produces bug fixes. This skill produces refactors. Separate PRs. Or at minimum, separate commits within one PR.

---

## Orchestrator anti-patterns

### O-AP-1: Orchestrator does the editing

The orchestrator is meant to coordinate, not edit. If it starts doing D1 while workers do D2-D5, commits conflict.

**Fix:** strict separation per [KICKOFF-PROMPTS.md §Orchestrator role](KICKOFF-PROMPTS.md#orchestrator-role--multi-agent-swarm): "DO NOT edit code yourself."

### O-AP-2: Orchestrator merges worker PRs without review

Orchestrator ships everything workers produce. Horror stories slip through.

**Fix:** orchestrator reviews per the Reviewer-role prompt before marking bead closed.

### O-AP-3: Single orchestrator pane for 20 beads

One agent can realistically coordinate 3–5 workers. Beyond that, coordination overhead exceeds throughput.

**Fix:** for >5 workers, a second-level orchestrator (coordinator of orchestrators). Or, more realistically, split the backlog into independent swarms.

---

## Meta anti-patterns (how the skill gets misused)

### M-AP-1: Using the skill name as a magic invocation

User: "Use simplify-and-refactor-code-isomorphically on this function."

Agent: jumps to Phase E without Phases A-D. No card. No verify. Ships.

**Fix:** the skill's name triggers the full loop, not just "refactor quickly."

### M-AP-2: Ignoring the opportunity-score threshold

Agent accepts candidates with Score 1.2 "because they seem worth it."

**Fix:** R-010 is a hard threshold. Below 2.0 → reject. Score is the guardrail against over-reach; ignoring it means reinventing the judgment-without-evidence failure mode.

### M-AP-3: Skipping the rejections log

Agent only logs accepted candidates. Six months later, another agent re-evaluates the same rejected candidate and makes the same wrong merge.

**Fix:** every rejected candidate gets a row in REJECTIONS.md. Future agents read it before re-evaluating.

### M-AP-4: Not running the AI-slop detector before scoring

Agent jumps straight to jscpd output. Misses P1/P10/P15/P23 — pathologies that aren't Type I-III duplications but are still refactor candidates.

**Fix:** `ai_slop_detector.sh` runs in Phase B alongside `dup_scan.sh`. Both outputs feed scoring.

### M-AP-5: Treating the skill as optional for "easy" refactors

"This is a 5-LOC change, I don't need the card."

**Fix:** 5-LOC changes are where horror story HS#3 (WebSocket auto-subscribe) happened. Small refactors are exactly where isomorphism discipline matters most, because reviewers glance and miss subtleties.

### M-AP-6: Deleting the ledger / artifacts after a PR merges

Agent cleans up "temporary" artifact dirs once the PR lands.

**Fix:** per R-001, don't delete. The ledger is historical record. `refactor/history/series.jsonl` depends on it.

### M-AP-7: Using the skill to justify a rewrite

"This code is too messy to refactor. Let me do a clean-room rewrite."

**Fix:** the skill's whole thesis is that rewrites are Tier-3 and rarely the right answer. If you genuinely need to rewrite, see [porting-to-rust](../../porting-to-rust/SKILL.md) for spec-first methodology — but first, try one pass of the skill's loop. 90% of "rewrites" were actually "I didn't know how to collapse this."

---

## How to detect an anti-pattern mid-session

If you notice any of these during a live session:

1. **Stop immediately.** Don't try to recover silently.
2. **Name the anti-pattern** in your next message to the user. ("I'm about to S-AP-5 — workers editing without each other's commits.")
3. **Propose the fix** from this doc.
4. **Wait for user approval** before continuing.

This is expensive short-term, cheap long-term. Anti-patterns that go unflagged compound.
