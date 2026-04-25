# Kickoff Prompts — role-prompt library for agent sessions

> Following the pattern from [operationalizing-expertise](../../operationalizing-expertise/SKILL.md) `references/KICKOFF.md`: role-specific prompts that bootstrap an agent into a particular stance. Paste verbatim; fill in the `<angle-brackets>` before sending.

## Contents

1. [When to use which prompt](#when-to-use-which-prompt)
2. [Solo refactor session — full loop](#solo-refactor-session--full-loop)
3. [Orchestrator role — multi-agent swarm](#orchestrator-role--multi-agent-swarm)
4. [Worker role — swarm pane](#worker-role--swarm-pane)
5. [Reviewer role — third-party sanity check](#reviewer-role--third-party-sanity-check)
6. [Rescue mission kickoff](#rescue-mission-kickoff)
7. [Weekly 1-hour pass kickoff](#weekly-1-hour-pass-kickoff)
8. [Monthly deep-pass kickoff](#monthly-deep-pass-kickoff)
9. [Hostile refactor audit](#hostile-refactor-audit)
10. [Post-incident refactor kickoff](#post-incident-refactor-kickoff)
11. [Cross-agent handoff](#cross-agent-handoff)

---

## When to use which prompt

| Situation | Use |
|-----------|-----|
| Single agent, healthy codebase, one candidate | [Solo refactor session](#solo-refactor-session--full-loop) |
| ≥5 candidates, independent files, infra available | [Orchestrator role](#orchestrator-role--multi-agent-swarm) + [Worker role](#worker-role--swarm-pane) × N |
| About to land a big refactor PR, want a second opinion | [Reviewer role](#reviewer-role--third-party-sanity-check) |
| Codebase in known-degraded state | [Rescue mission](#rescue-mission-kickoff) |
| Weekly cadence | [Weekly 1-hour pass](#weekly-1-hour-pass-kickoff) |
| Monthly module deep-clean | [Monthly deep pass](#monthly-deep-pass-kickoff) |
| Reviewing an existing PR for smells | [Hostile refactor audit](#hostile-refactor-audit) |
| Cleaning up after a prod incident | [Post-incident refactor](#post-incident-refactor-kickoff) |
| Mid-session baton pass between agents | [Cross-agent handoff](#cross-agent-handoff) |

---

## Solo refactor session — full loop

```text
You are running a solo refactor session using the
simplify-and-refactor-code-isomorphically skill.

Target: <FILE | DIRECTORY | MODULE>
Goal:   <e.g., reduce duplication, collapse sibling components, shrink LOC>
Budget: <time | # of accepted candidates | max LOC-reduction target>

Before any code edit:

1. Read AGENTS.md. Invariants:
   - No file deletion without my explicit approval (DEAD-CODE-SAFETY.md gauntlet)
   - No script-based code changes (Edit tool or parallel subagents only)
   - No overwrite of existing files with Write (Edit only)
   - No new variant filenames (v2 / _new / _improved)
   - No backwards-compat shims — we're in early dev

2. Run Phase 0 (bootstrap):
   ./.claude/skills/simplify-and-refactor-code-isomorphically/scripts/check_skills.sh refactor/artifacts/<run-id>
   ./scripts/install_missing_skills.sh refactor/artifacts/<run-id>   # only if missing siblings + jsm available

3. Run Phase A (baseline):
   ./scripts/baseline.sh <run-id>   # must exit 0; tests green, goldens hashed, LOC/lint snapshots

4. Run Phase B (map):
   ./scripts/dup_scan.sh <run-id> <target-dir>
   ./scripts/ai_slop_detector.sh <target-dir> <run-id>
   Edit refactor/artifacts/<run-id>/duplication_map.md with accepted candidates.

5. Run Phase C (score):
   ./scripts/score_candidates.py refactor/artifacts/<run-id>/duplication_map.md

6. For each ACCEPTED candidate (Score ≥ 2.0):
   a. Fill the isomorphism card BEFORE editing:
      ./scripts/isomorphism_card.sh <id> <run-id>
      Every row answered. "N/A" only with a written reason.
   b. Edit the code (Edit tool only, no Write, one lever).
   c. Run ./scripts/verify_isomorphism.sh <run-id>
      — tests pass count = baseline
      — goldens bit-identical
      — no new lint warnings
      — LOC delta within predicted ±10%
      — no new lint-disable comments
   d. If any gate fails: revert the edit, add a rejection reason, move on.
   e. Commit with the isomorphism card in the message + LOC delta.
   f. Append row to refactor/artifacts/<run-id>/LEDGER.md
   g. Next candidate.

7. Stop when no candidate scores ≥ 2.0 or budget reached.

8. Final:
   ./scripts/metrics_snapshot.sh <run-id> > final_metrics.json
   Generate DASHBOARD.md per METRICS-DASHBOARD.md template.

Report back when the pass is complete with the ledger + dashboard.
```

---

## Orchestrator role — multi-agent swarm

Use this when you have ≥5 accepted candidates across distinct directories, plus `ntm` + `agent-mail` + `br`.

```text
You are the orchestrator for a multi-agent refactor swarm.

Target: <PROJECT ROOT>
Budget: up to <N> parallel worker panes

Responsibilities:
  - Run Phase 0, A, B, C yourself.
  - File one bead per accepted candidate (br create ... --label refactor).
  - Configure bead dependencies (br dep add) so low-risk lands before high-risk.
  - Spawn <N> NTM worker panes.
  - Send each pane the Worker-role marching orders (KICKOFF-PROMPTS.md § Worker role).
  - Monitor progress:
      watch -n 30 'br list --status in_progress --json | wc -l'
  - When a pane is stuck or rate-limited, follow AGENT-COORDINATION.md § Recovery.
  - When all beads closed: run the final metrics snapshot, generate DASHBOARD.md.

DO NOT edit code yourself. Workers do the editing. You coordinate, verify
the aggregate LEDGER, and recover stuck workers.

Start by running Phase 0 + A + B + C and filing beads. Report back with
the bead list before spawning any worker.
```

---

## Worker role — swarm pane

This is the message you send to each NTM pane.

```text
You are refactor-worker-<N> participating in a multi-agent refactor swarm
for <PROJECT>.

Your run: <run-id>
Artifact dir: refactor/artifacts/<run-id>

Loop (autonomous, no user prompts):

1. Pick a bead:
   br ready --json | jq '.beads[] | select(.label // [] | index("refactor"))' | head -1
   If empty: exit.

2. Claim it:
   br update <id> --status=in_progress

3. Reserve files (if agent-mail is available):
   file_reservation_paths(project_key=<abs>, agent_name="refactor-worker-<N>",
                          paths=[<candidate's paths + callers + tests>],
                          ttl_seconds=3600, exclusive=true,
                          reason="refactor-<id>")
   If FILE_RESERVATION_CONFLICT: release the bead back to open, pick another.

4. Apply the skill's loop on that candidate:
   a. ./scripts/isomorphism_card.sh <id> <run-id>
      Fill every row before editing.
   b. Edit the code. Edit tool only. No Write. No sed. One lever.
   c. ./scripts/verify_isomorphism.sh <run-id>
      If any gate fails: revert, add reason to bead, unclaim, pick another.
   d. Commit:
        refactor(<scope>): <title>

        <isomorphism card verbatim>

        LOC: <path> <before>→<after>. Tests unchanged. Goldens identical.
        Beads: <id>
   e. Append to refactor/artifacts/<run-id>/LEDGER.md via flock.
   f. release_file_reservations(...)
   g. br close <id> --reason "Completed; ledger row appended"

5. Loop to 1.

Invariants (AGENTS.md):
  - No file deletion without user approval
  - No script-based changes — parallel with siblings, not sed
  - One lever per commit
  - Never pause on "unexpected changes" (other workers are active)
  - Never steal locks
```

---

## Reviewer role — third-party sanity check

Launch a second agent (can be a different model via [multi-model-triangulation](../../multi-model-triangulation/SKILL.md)) to review a refactor PR before merge.

```text
You are reviewing a refactor PR in <PROJECT> for correctness and hostility.

PR: <branch-or-PR#>
Changed files: (fetch with `git diff --name-only main`)

Do NOT edit. Read and produce a report.

For each commit in the PR:
  1. Read the commit message — does it contain an isomorphism card?
     If not, flag.
  2. Read every row of the card — does it match the diff?
     In particular, check these axes manually:
        - Ordering: does the new code preserve the sequence order?
        - Error semantics: same Err variants under same conditions?
        - Side effects: same log / metric / DB-write / subscription behavior?
        - Type narrowing: same discriminant checks in callers?
        - Resource lifecycle: same Drop / __del__ / defer order?
     If any axis is unchecked in the diff but marked "unchanged" in the
     card, flag.
  3. Check "one lever" discipline: does the commit do exactly one kind of
     change? (rename + extract + style = three levers = flag)
  4. Check for destructive patterns:
     - File deletion without refactor/_to_delete/ staging → flag
     - New `#[allow]` / `// eslint-disable` / `# noqa` → flag
     - Added defensive try/catch, .trim(), or normalization → flag (behavior change)
     - `sed` or codemod tooling in the commit footer → flag
  5. Check for the horror-story pattern (REAL-SESSION-EVIDENCE.md HS#1):
     Any reasoning in the diff like "dead code", "misleading implementation",
     "broken and unused"? If the commit deletes or stages a file for
     deletion, ensure the DEAD-CODE-SAFETY.md 12-step gauntlet is documented.

Produce a report:
  - Commits reviewed: <count>
  - Cards filled correctly: <count>
  - Cards with missing axes: <list>
  - One-lever violations: <list>
  - Destructive-pattern flags: <list>
  - Horror-story risk: <yes/no + evidence>
  - Overall recommendation: approve / request changes

End with a 3-sentence summary the author can action.
```

---

## Rescue mission kickoff

From [RESCUE-MISSIONS.md](RESCUE-MISSIONS.md); repeated here for ease of paste.

```text
Rescue mission for <project>.

The codebase is in a known-degraded state. Goal: reach a healthy baseline
so the standard simplify-and-refactor loop can run. Do NOT start the main
loop yet.

Phase order:
  -1a Red tests      → fix or quarantine with reason
  -1b Broken build   → fix, no mixed commits
  -1c Loud lints     → cap, don't bulk-fix
  0   No tests       → characterization + golden-path integration
  0.5 Type system    → draw boundary validators; cap `any` count

Invariants (this skill's rules, even in rescue):
  - Edit tool only; no Write over existing files
  - Never delete a file without explicit user approval
  - No script-based codemods; parallel subagents or manual
  - One lever per commit
  - File beads for everything you notice; don't try to fix everything

Per phase, write a rescue note to refactor/artifacts/<run>/rescue/<phase>.md
with: what you did, what you found, what beads you filed, current gate
snapshot (tests, warnings, any-count, unwrap-count).

Exit criterion (when to switch to the main loop): the checklist in
RESCUE-MISSIONS.md § "When to run the main loop vs. more triage" shows
all boxes ticked.

Begin with Phase -1a.
```

---

## Weekly 1-hour pass kickoff

```text
Weekly refactor pass for <PROJECT>. Budget: 60 minutes.

1. (5 min) Triage:
   bv --robot-triage --label refactor
   Pick the top 1-2 ready beads. Announce which.

2. (5 min) For the first bead, fill the isomorphism card:
   ./scripts/isomorphism_card.sh <id> weekly-<YYYYMMDD>

3. (20 min) Make the edit. Edit tool only. One lever.

4. (10 min) Verify:
   ./scripts/verify_isomorphism.sh weekly-<YYYYMMDD>
   If any gate fails: revert, add reason to bead, stop (don't try the second).

5. (5 min) Commit + ledger row.

6. (10 min) If time and gate passed, repeat with the second bead.

7. (5 min) Final: metrics snapshot + announce the delta.

Stop at 60 minutes regardless of state. Partial wins ship; full-scope wins
fit in the monthly deep pass.

Invariants: AGENTS.md — no deletion, no scripts, Edit only, one lever.
```

---

## Monthly deep-pass kickoff

```text
Monthly deep refactor pass.

Target: <MODULE | CRATE | FEATURE>
Budget: half-day (~4 hours).

Run the full skill loop:
  Phase 0: ./scripts/check_skills.sh; ./scripts/install_missing_skills.sh
  Phase A: ./scripts/baseline.sh
  Phase B: ./scripts/dup_scan.sh + ./scripts/ai_slop_detector.sh
  Phase C: ./scripts/score_candidates.py (accept ≥ 2.0 only)
  Phase D: isomorphism card per candidate
  Phase E: collapse one-lever-per-commit, optionally multi-agent swarm
           if ≥ 5 candidates (launch via ./scripts/multi_agent_swarm.sh)
  Phase F: verify every commit
  Phase G: DASHBOARD.md + LEDGER.md + history/series.jsonl append

Invariants: AGENTS.md + this skill's loop.

Stop criteria (any one):
  - No candidate scores ≥ 2.0
  - Budget reached
  - Unresolvable verify-gate failures ≥ 3 in a row (means the scoring is off;
    reassess)

Produce at the end:
  1. refactor/artifacts/<run-id>/DASHBOARD.md
  2. refactor/artifacts/<run-id>/LEDGER.md
  3. refactor/artifacts/<run-id>/REJECTIONS.md
  4. Appended row to refactor/history/series.jsonl
  5. New beads for followups (label: followup)

Report back with the dashboard.
```

---

## Hostile refactor audit

For reviewing an existing PR or branch for the "hostile refactor" anti-pattern (RESCUE-MISSIONS.md § The non-hostile refactor rule).

```text
Audit the PR / branch <ref> for hostile refactor patterns.

Hostile characteristics (flag each instance):
  - Renames of widely-imported symbols (count usages in main):
      for s in $(git diff main...<ref> | grep -oP '^-\s+(?:export\s+)?(?:function|class|const|let)\s+\K\w+'); do
        count=$(rg "\b$s\b" --count-matches . 2>/dev/null | awk -F: '{s+=$2} END{print s}')
        echo "$count $s"
      done | sort -rn
      Anything with >20 usages is widely-imported; flag.
  - Files moved between directories (disrupts blame):
      git log --diff-filter=R main...<ref> --name-status
  - Changes to public API (check for `export` signature changes):
      git diff main...<ref> | grep -E '^-export' | wc -l
  - Bulk formatter/linter runs:
      is every changed file touched in ≥3 places? if yes, likely a formatter pass
      → check for prettier/eslint/clippy-fix traces
  - Removed logs/metrics that might power dashboards:
      grep '^-.*\(console\|log\|tracing\|metrics\).*' in the diff

Output: a table with columns [PATTERN, COUNT, FILES, SEVERITY, SUGGESTED FIX].

If severity includes any HIGH: recommend splitting the PR into:
  - A formatting/rename commit (separate PR)
  - A semantic refactor commit
  - A behavior-change fix commit (if any)

Per this skill's "one lever per commit" rule.
```

---

## Post-incident refactor kickoff

After a prod incident, the team often rushes to clean up. Channel the energy with this prompt.

```text
Post-incident refactor kickoff.

Incident summary:
  <paste incident ticket or runbook link>

Root cause:
  <1-2 sentence summary>

Your task: identify refactors that would have PREVENTED this incident,
score them per the skill's Opportunity Matrix, and file beads with a
"post-incident-<DATE>" label.

Do NOT yet refactor. This is a planning pass.

Steps:

1. Re-read the incident. Identify the exact moment behavior went wrong.
2. Find the code that behaved wrong. Read it.
3. Identify the pathology class (P1-P40 in VIBE-CODED-PATHOLOGIES.md):
   - Was the error swallowed (P1, P10)?
   - Was data silently truncated (P23)?
   - Did type narrowing fail (P15, P26)?
   - Was a Drop impl lost (HS#4)?
   - Was a side effect dropped (HS#3)?
   - Was code "dead-code deleted" (HS#1)?
4. For each pathology found, file a bead:
   br create --title "[post-incident] <pathology> in <file>" \
             --type task --priority 1 \
             --label refactor --label post-incident-<YYYYMMDD>
5. In each bead's body, include:
   - Pathology ID
   - Session-evidence citation if applicable
   - The exact line/function in the code
   - Why the existing isomorphism card (if any previous refactor touched this)
     did not catch it
   - Proposed fix
   - Test that would detect recurrence

6. Run the weekly pass or monthly deep pass on these beads first —
   they have highest priority.

Output: a summary of beads filed + a recommendation for whether this
is a weekly-pass-sized or monthly-pass-sized cleanup.
```

---

## Cross-agent handoff

When one agent session hits rate limits or ends, use this to brief the next.

```text
Session handoff for simplify-and-refactor-code-isomorphically pass.

Previous session state:
  Run ID: <id>
  Artifact dir: refactor/artifacts/<id>
  Target: <scope>

Progress so far:
  - Phase A baseline: <complete/partial>
  - Phase B map: <complete/partial> (duplication_map.md status)
  - Phase C scoring: <complete/partial> (scored_candidates.md status)
  - Phase E commits landed: <list of commit SHAs>
  - Beads closed: <list of IDs>
  - Beads in_progress: <list of IDs>  ← needs attention
  - Beads blocked: <list of IDs + reason>

Next steps (do these in order):

1. Read refactor/artifacts/<id>/LEDGER.md — understand what's shipped.
2. For each bead in_progress, check with agent-mail for stale reservations:
     list_reservations(project_key=<abs>)
   Release any owned by the previous agent (force_release_file_reservation).
   Revert those beads to open: br update <id> --status=open
3. Check git status. Any uncommitted changes? If yes: either finish a
   partial commit, write a HANDOFF.md describing the exact state, or pause.
   Do not stash, revert, or overwrite another agent's work.
4. Run ./scripts/check_skills.sh to confirm sibling-skill availability.
5. Pick up the next ready bead per the Solo / Worker role loop.

Invariants unchanged: AGENTS.md — Edit only, no deletion, no scripts,
one lever, ask before deleting.
```

---

## Scenario-specific prompts (added 2026-04-23)

Each prompt below kicks off a narrowly-scoped pass for a specific
situation. Use verbatim, replacing placeholders.

### Orphan sweep

```
Goal: eliminate `_v2` / `_new` / `_improved` / `tmp_` sibling files
created during past AI sessions.

1. Run ./scripts/ai_slop_detector.sh <src> — review P3 findings.
2. For each orphan, run ./scripts/callsite_census.sh on the orphan
   symbol to determine whether callers use the orphan or the canonical.
3. For mixed-use: merge orphan contents into canonical via L-MERGE-FILES,
   update callers, stage orphan to _to_delete/.
4. For unused orphans: gauntlet (dead_code_safety_check.sh), then stage
   to _to_delete/.
5. One commit per orphan. Card must list: canonical file, orphan file,
   callers touched, lever L-MERGE-FILES.

Do NOT delete anything directly. Stage to _to_delete/ and request
explicit user approval to hard-delete in a follow-up PR.
```

### DTO explosion consolidation

```
Goal: consolidate a "DTO explosion" — e.g., UserDTO, UserDTOv2,
UserResponseDTO, UserApiDTO, UserInternalDTO all coexisting.

1. Run ./scripts/callsite_census.sh for each DTO name. Build a table:
   DTO → constructors → consumers.
2. Identify which DTOs serve different observable boundaries (usually
   ≤ 2). Candidates for keeping.
3. The rest: run dead_code_safety_check.sh; confirm unused.
4. For the keepers: extract a shared core if scoring ≥ 2.0. Otherwise
   leave separate and document why in TYPE-SHRINKS.md-style notes.
5. Card must enumerate which DTOs survive, why, and what each boundary
   observes.
```

### Rescue a red CI

```
Goal: return to green CI before starting any main-loop pass. CI is red;
PRs cannot merge.

1. Do NOT run main loop. Per DECISION-TREES.md Tree 2, enter rescue.
2. Run ./scripts/rescue_phase_check.sh — note every failing gate.
3. Triage in order: (a) quarantine flaky tests in a dedicated commit
   with `#[ignore]` + bead link; (b) pin unpinned deps (P37);
   (c) gauntlet obvious orphans; (d) snapshot warning ceiling at
   current state.
4. Re-run rescue_phase_check.sh until all gates green.
5. Only then, start a first real pass with 3 candidates max (cold-
   start discipline — the baseline is thin).
```

### First pass after an AI spree

```
Goal: stabilize a project that was developed for weeks via Claude Code /
Codex / Cursor / Gemini without discipline. Duplication, orphans, slop
are dense.

1. Start with ./scripts/ai_slop_detector.sh — this produces P1-P40
   findings. Review the full output.
2. Cold-start (COLD-START.md) if missing baseline artifacts.
3. Do NOT try to fix everything in one pass. Pick the top 3 pathologies
   by blast radius and attack them as candidates.
4. Expect ship/reject ratio to be unusually high for rejections this
   pass (the slop detector over-reports). Log rejections thoroughly.
5. Second pass: re-run slop detector — noise should drop ~30-50%.
   Repeat. Expect full stabilization over 3-5 passes.
```

### Unpinned deps sweep

```
Goal: pin every `*` / `latest` / unrevved-git dependency (pathology P37)
to its current resolved version.

1. Run ./scripts/unpinned_deps.sh — get the list.
2. For each entry, find the currently-resolved version from the lockfile.
3. One commit per manifest entry with L-PIN-DEP lever.
4. Commit body: `refactor(deps): pin <package> to <version>`.
5. Card is minimal but required — list the package, the observable
   contract (API version used at runtime), and verify no runtime
   behavior change.
6. Exclude intentional floaters (rare; usually dev tools) — document
   in rejection_log.md.
```

### Callsite census for a specific symbol

```
Goal: enumerate every reference to <symbol> across the repo, test files,
SQL, config, YAML, and dependent repos.

1. Run ./scripts/callsite_census.sh <symbol> > /tmp/census-<symbol>.txt.
2. Read the output in full.
3. Spot-check 3 random call sites by running the function to confirm
   the caller's observed contract.
4. Produce a one-page report:
    - Total references
    - Constructors vs consumers
    - Test references
    - SQL / config / YAML references
    - Cross-repo references (if library)
5. Feed the report into the isomorphism card's "Sites" field.
```

### Dead-code gauntlet on a target

```
Goal: prove that <file> / <function> / <config key> is safely removable.

1. Spawn the dead-code-checker subagent:
   Agent(subagent_type="dead-code-checker", prompt="Run the 12-step
   gauntlet on <target>. Report verdict + evidence per step.")
2. Review the returned evidence table. For any "evidence found" row,
   cite the line and decide: genuine usage (KEEP) vs stale comment
   (STAGE with note).
3. If verdict SAFE TO STAGE: commit move to _to_delete/<date>/ with
   L-DELETE-DEAD lever. Do NOT hard-delete.
4. Set a calendar reminder / bead for final delete ≥ 7 days post-deploy
   to staging.
5. Absolute rule per AGENTS.md: no hard-delete without explicit user
   approval citing the staged observation window.
```

### Property-test scaffold for a candidate

```
Goal: add a property test that would catch regressions across the N
sites being collapsed for ISO-<id>.

1. Read the isomorphism card at refactor/artifacts/<run-id>/cards/ISO-<id>.md.
2. Identify the observable contract's invariants (same input → same
   output across sites; same error for same bad input; etc.).
3. Run ./scripts/property_test_scaffold.sh <language> <invariant-name>
   to generate a skeleton.
4. Fill in the generator (inputs), the oracle (what counts as "same"),
   and the shrinker (if using proptest).
5. Run 1000+ iterations in both the pre- and post-collapse states.
   Both should pass identically.
6. Commit the property test AS ITS OWN commit before the collapse
   commit. It's baseline infrastructure, not part of the refactor.
```

### Swarm kickoff for N candidates

```
Goal: fan out a pass across N candidates using parallel subagents.

1. Confirm candidates are independent — no shared files / symbols.
   Conflicting candidates must serialize.
2. Spawn the swarm via ./scripts/multi_agent_swarm.sh <run-id>.
3. Agent Mail (if installed) reserves file locks; otherwise serialize
   manually.
4. Each agent completes Phase D (card) before starting Phase E (edit).
5. The orchestrator (you) waits for all to finish, then runs Phase F
   (verify) on the integrated branch.
6. If any sub-collapse fails Phase F, revert ONLY that one — the others
   can ship.
```

### Review-mode prompt

```
Role: you are the REVIEWER, not the driver. PR #<n> claims to be a
refactor pass output.

1. Apply REVIEWER-QUICKSTART.md's 10-min checklist verbatim. Time it —
   if you exceed 15 min, the PR is too big; request split.
2. Spawn the refactor-reviewer subagent in parallel for independent
   verdict:
   Agent(subagent_type="refactor-reviewer",
   prompt="Audit <PR-URL> against card <card-path>. Report verdict.")
3. If your review AND subagent verdict AGREE on PASS: approve.
4. If DISAGREE: cite the finding line by line in a review comment, ask
   the author.
5. Never approve without reading the isomorphism card.
```

### Ledger review (quarterly retrospective)

```
Goal: review the last quarter of the refactor ledger to detect drift,
patterns, improvement opportunities.

1. Read the ledger rows and rejection_log entries over the last 3 months.
2. Tabulate:
    - Shipped count, reverted count, rejected count
    - Per-lever breakdown
    - Clone-type breakdown
    - Top 5 clusters of rejection reasons
3. Flag: are reverted rows clustered around a specific pattern? That's
   a signal to update the rejection-log heuristics or the scanner.
4. Update rejection_log.md with any newly-permanent "do not propose"
   entries.
5. Write a quarterly retrospective in refactor/artifacts/retro-
   <YYYY-Q>.md. Feed lessons into FLYWHEEL-INTEGRATION.md.
```

### Closeout prompt

```
Goal: close the pass cleanly with a CLOSEOUT.md.

1. Open the template: refactor/artifacts/<run-id>/CLOSEOUT.md. Use
   FORMULAS.md § "Pass-closeout summary".
2. Fill each section:
   - Stats (from ledger rows)
   - Shipped (ledger rows, status=shipped)
   - Reverted (ledger rows, status=reverted)
   - Rejections new-this-pass (rejection_log additions)
   - Follow-ups (open beads filed this pass)
   - Surprises & lessons (3-5 sentences — genuine, not boilerplate)
3. Compare against BENCHMARKS.md — are the numbers "typical"? If
   outside the typical band, explain why.
4. Post closeout in team channel with ledger link.
5. If pass introduced a revert: link ROLLBACK-PLAYBOOK.md and the
   incident postmortem from that revert.
```

### Cold-start pre-flight

```
Goal: prepare a project with no baseline for its first real refactor
pass.

1. Read COLD-START.md in full.
2. Execute Step 1: add smoke test. Commit.
3. Execute Step 2: capture 3-5 goldens. Commit.
4. Execute Step 3: snapshot warning ceiling.
5. Execute Step 4: create AGENTS.md (use COLD-START.md template).
6. Execute Step 5: read-only duplication map — do NOT score or act.
7. Verify exit criterion (Step 5 of COLD-START.md). Every box ticked.
8. Post the cold-start closeout: "Baseline ready. First real pass can
   start now. Recommend ≤ 5 candidates on pass 1."
```

### Second-pass comparison

```
Goal: open a pass-2 after a successful pass-1 — compare deltas to
BENCHMARKS.md expectations.

1. Read refactor/artifacts/<pass-1>/CLOSEOUT.md for the prior baseline.
2. Run session_setup.sh with new run-id pass-2.
3. Compare pass-2 baseline to pass-1 closeout:
    - Has the duplicate-cluster count decreased?
    - Has the warning ceiling decreased?
    - Are the same pathologies surfacing, or new ones?
4. If pass-2 scanner output looks identical to pass-1's (same clusters),
   something's wrong — pass-1 may not have actually collapsed.
   Investigate before proceeding.
5. Otherwise, pick top candidates and run the main loop normally.
```

### ISO-card audit prompt

```
Role: you are auditing an isomorphism card for a candidate someone
else (or past you) filled out. They haven't started editing yet.

1. Spawn the isomorphism-auditor subagent:
   Agent(subagent_type="isomorphism-auditor",
   prompt="Audit <card-path>. Verdict: READY | NEEDS-REVISION | REJECT.")
2. Review the audit verdict.
3. If READY: approve the card; the driver can proceed to Phase E.
4. If NEEDS-REVISION: the driver must fix the flagged fields before
   editing.
5. If REJECT: add to rejection_log.md and move on. Do not force.
```

### Pair-programming handoff

```
Goal: hand off an in-progress pass to a pairing partner (human or
agent).

1. Commit everything verified-green so far.
2. Write refactor/artifacts/<run-id>/HANDOFF.md:
   - Run ID
   - Candidates shipped (IDs + commit SHAs)
   - Candidate currently in Phase D/E (card path)
   - Any blockers or decisions awaiting input
   - Estimated remaining candidates
3. Partner reads HANDOFF.md + CLOSEOUT.md of previous pass.
4. Partner resumes at the current Phase. Switch driver/navigator roles
   per TEAM-ADOPTION.md pair-programming protocol.
5. After handoff session, update HANDOFF.md with "resumed" timestamps.
```
