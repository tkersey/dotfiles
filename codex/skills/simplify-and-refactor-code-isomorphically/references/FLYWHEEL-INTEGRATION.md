# Flywheel Integration — mining your own patterns to extend this skill

> The [flywheel](../../flywheel/SKILL.md) skill extracts methodology from your own agent sessions and turns it into executable prompts / rules. This skill is itself a candidate for flywheel maintenance: as you run more refactor passes, new pathologies, collapses, and user phrases surface. This file is the contract for feeding those discoveries back into the skill.

## Contents

1. [Why feed back](#why-feed-back)
2. [What signals to capture](#what-signals-to-capture)
3. [The weekly mining pass](#the-weekly-mining-pass)
4. [The monthly pattern-extraction pass](#the-monthly-pattern-extraction-pass)
5. [Gating new patterns into the skill](#gating-new-patterns-into-the-skill)
6. [Retiring obsolete patterns](#retiring-obsolete-patterns)
7. [Using flywheel sessions to generate skill extensions](#using-flywheel-sessions-to-generate-skill-extensions)

---

## Why feed back

Each run of this skill produces artifacts: LEDGER rows, REJECTIONS rows, isomorphism cards, case studies, metrics deltas. Those are data. Over 50 runs, they describe:

- Which pathologies (P1-P40) are most common in *your* codebase.
- Which collapses (M1-M80) actually get chosen.
- Which horror stories you've personally witnessed (S-*).
- Which prompt shapes produce clean PRs vs. ones that need rework.
- Which axes of the isomorphism card catch the most bugs.

This is all training data for the next iteration of the skill.

**Without feedback**, the skill stays generic. **With feedback**, it becomes specific to your codebase's failure modes — which is where 80% of the value lives.

---

## What signals to capture

### Per-run signals

After every pass, log to `refactor/history/`:

```jsonl
{
  "run_id": "2026-06-15-mail-crate-pass-3",
  "date": "2026-06-15",
  "scope": "crates/mcp-agent-mail-tools/",
  "candidates_accepted": 8,
  "candidates_rejected": 3,
  "loc_delta": -412,
  "duration_minutes": 180,
  "pathologies_hit": ["P1", "P8", "P12", "P19", "P23"],
  "micropatterns_applied": ["M-R2", "M-R4", "M-R9", "M-X1"],
  "verify_failures": 1,
  "verify_failures_roots": ["P23-trim-caused-test-regression"],
  "user_interactions": 4,
  "user_interactions_kind": ["approve_delete", "clarify_scope", "approve_delete", "reject_candidate"]
}
```

One JSONL row per run. Append-only; never edit past rows.

### Per-pathology frequency

```bash
# Roll up: which pathologies are dominant across runs
jq -s '
  [.[].pathologies_hit[]] | group_by(.) | map({p: .[0], n: length})
  | sort_by(.n) | reverse
' refactor/history/*.jsonl
```

If P1 (over-defensive try/catch) is hit in every single run, write a project-specific CLAUDE.md rule that blocks new try/catch additions via pre-commit hook. If P19 (N+1) appears only twice, it's not a primary pattern — keep it in the catalog but don't hoist it to top-of-mind.

### Per-horror-story near-misses

Any time the verify gates catch a refactor that would have broken behavior, that's a near-miss. Log:

```jsonl
{
  "run_id": "2026-06-15-mail-crate-pass-3",
  "candidate_id": "D7",
  "verify_gate_tripped": "goldens_diff",
  "root_cause": "removed .trim() that was correct for this field",
  "prevented_horror_story_class": "S-6-equivalent",
  "took_minutes_to_diagnose": 12
}
```

Over 50 runs, patterns emerge: "the .trim() issue caught us 8 times" → promote to pre-commit hook blocking any `.trim()` addition in changed files.

### User-phrase accumulation

Every user prompt that activated the skill:

```jsonl
{
  "run_id": "2026-06-15-mail-crate-pass-3",
  "user_prompt_excerpt": "can you reduce the duplication in the messaging module",
  "matched_trigger": "reduce duplication",
  "phase_reached": "G",
  "outcome": "accepted_by_user"
}
```

After 50 runs, aggregate:

```bash
jq -r '.user_prompt_excerpt' refactor/history/*.jsonl | sort | uniq -c | sort -rn | head -20
```

The top 20 phrases are your **observed** trigger set. If any phrase doesn't appear in SKILL.md's description or KICKOFF-PROMPTS.md exemplars, add it.

---

## The weekly mining pass

15 minutes, every Friday (or whenever).

```bash
# 1. Pull the week's runs
runs=$(ls refactor/artifacts/ | grep "$(date -d '7 days ago' +%Y-%m-%d)")

# 2. Check: any verify failures this week?
for r in $runs; do
  if [[ -f "refactor/artifacts/$r/verify_report.md" ]]; then
    grep -l "FAIL" "refactor/artifacts/$r/verify_report.md" | head
  fi
done

# 3. Check: any new rejection reasons?
for r in $runs; do
  if [[ -f "refactor/artifacts/$r/REJECTIONS.md" ]]; then
    grep "Why rejected" "refactor/artifacts/$r/REJECTIONS.md"
  fi
done

# 4. Check: any new user-phrase triggers not already in the corpus?
grep -h "user_prompt_excerpt" refactor/history/week-*.jsonl \
  | sort -u \
  > this_week_phrases.txt

diff this_week_phrases.txt <(cut -d'"' -f4 refactor/history/all_triggers.txt)
```

If anything new shows up: file a bead `[flywheel-pass] add <finding> to skill`. Low-priority; processed in the monthly pass.

---

## The monthly pattern-extraction pass

An hour, once per month. Uses [flywheel](../../flywheel/SKILL.md) proper.

### Step 1: feed the week's runs to flywheel

```bash
flywheel start --session-type refactor-mining \
  --input "refactor/history/month-$(date -d '30 days ago' +%Y-%m).jsonl" \
  --output "refactor/flywheel-$(date +%Y-%m).md"
```

The flywheel session extracts:
- Recurring themes (e.g., "89% of rejections cited shared-state risk in service/handlers.ts")
- New successful patterns (e.g., "the thiserror-lift pattern was applied 6 times this month")
- Cadence signals (e.g., "avg pass produced -87 LOC; week 3 dropped to -23 LOC")

### Step 2: review the flywheel output with the user

Present findings:

```
Findings from flywheel mining of the last 30 days:

1. Most common pathology: P1 (34 hits). Suggest pre-commit hook to block new try/catch.
2. Most common collapse: M-R4 (generic over parse_X fns). Already in skill, working well.
3. New pattern observed 3+ times: "rename a field in a Prisma schema across the app".
   → Candidate for M-T26 (new micropattern).
4. Horror near-miss: .trim() reflex caught 4 times by verify. Propose CONTINUOUS-REFACTOR hook.
5. User vocabulary: "can you refactor to reduce coupling" appeared 6 times but isn't in
   S-13. Add as trigger.

Suggested updates:
  A. Add M-T26 to ADVANCED-MICROPATTERNS.md
  B. Add pre-commit rule in CONTINUOUS-REFACTOR.md
  C. Add "reduce coupling" to SKILL.md description
  D. Update S-13 in CORPUS.md with the new phrase

Approve A/B/C/D?
```

Await user approval per each. Update the skill files accordingly.

### Step 3: update the triangulated kernel if needed

If the flywheel findings imply a new rule (not just a pattern), add to [TRIANGULATED-KERNEL.md](TRIANGULATED-KERNEL.md) with a new `R-nnn`. Every rule needs ≥2 quote anchors — if you only have one, it goes into the UNIQUE section (U-nnn) or DISPUTED (D-nnn).

---

## Gating new patterns into the skill

Not every observation deserves to be in the skill. Gate by:

| Criterion | Threshold |
|-----------|-----------|
| Frequency | pattern observed in ≥3 runs |
| Reproducibility | same pattern across ≥2 unrelated modules |
| Impact | either ≥20 LOC saved per application OR prevents ≥1 horror story |
| Clarity | can be written in ≤200 words with a before/after code snippet |
| Isomorphism | passes the same axes the rest of the skill enforces |

Patterns that don't pass: log in `refactor/candidates-for-skill.md` as "not yet promoted". Re-evaluate next month.

---

## Retiring obsolete patterns

As the codebase evolves, some patterns become irrelevant:

- P39/P40 (async mismatch) on a project that has fully migrated to async.
- M-R19 (Deref wrapper) on a codebase that standardized on `std::ops::Deref` elsewhere.
- A horror story whose mitigation is now automated (pre-commit hook).

### Retirement process

1. Mark the pattern as DEPRECATED in its home file:
   ```markdown
   ### P39 — [DEPRECATED 2026-08] async added to sync fn
   This pathology no longer applies to our codebase; we've fully migrated to async.
   Kept for historical / onboarding purposes.
   ```
2. Remove from attack-order rollups.
3. Don't delete (per AGENTS.md Rule 1 — even markdown).

### Never retire a horror story

The horror stories (S-1 through S-5) stay forever. They're the reason certain rules exist. Even if a mitigation is now automated, the story explains *why*.

---

## Using flywheel sessions to generate skill extensions

### Template: a flywheel session producing a new reference file

Kickoff:

```
Flywheel session: extend the simplify-and-refactor-code-isomorphically skill.

Scope: mine my last 3 months of refactor passes for patterns specific to
<language | stack | scope>.

Goals:
  1. Identify new pathologies (beyond P1-P40)
  2. Identify new micropatterns (beyond M1-M80)
  3. Identify new kickoff-prompt exemplars
  4. Identify new isomorphism axes that surfaced in verify failures
  5. Identify new rules for the triangulated kernel (each anchored in ≥2 quotes)

Do NOT modify the skill files directly. Produce a proposal doc:
  refactor/flywheel-extension-proposal.md

Structure:
  - Executive summary (1 paragraph)
  - Evidence summary (linked per proposal)
  - Per-proposal: proposed change, evidence anchors, blast radius, deprecations

I will review and approve changes to the skill.
```

### Template: a flywheel session optimizing a specific pass

```
Flywheel session: optimize the simplify-and-refactor weekly 1-hour pass.

Data: my last 12 weekly passes (refactor/history/weekly-*.jsonl).

Analysis:
  - What's the distribution of time across phases (baseline, map, score, edit, verify)?
  - Where is the biggest drag?
  - Which phase failures are most common?
  - Are there phases I consistently skip?

Output: a proposal to tighten CONTINUOUS-REFACTOR.md §"The weekly 1-hour pass".

Do NOT edit the skill directly. Propose changes for my review.
```

### Template: discovering cross-skill patterns

```
Flywheel session: find patterns across simplify-and-refactor-code-isomorphically
and extreme-software-optimization.

Data: my last month of both skill's runs.

Analysis:
  - Are there commits that would have benefited from BOTH skills but only
    ran one?
  - Are there commits where refactor LOC reduction caused perf regressions
    later fixed by optimization? That's Tier-3 warning signal.
  - Are there isomorphism-card axes that both skills emit? If yes, they
    should be in a shared CORPUS anchor.

Output: a CROSS-SKILL.md update proposal.
```

---

## Integration with beads

Each flywheel finding becomes a bead:

```bash
br create --title "[flywheel] add M-T26 Prisma-schema-rename micropattern" \
          --type task --priority 3 --label flywheel --label skill-evolution
br create --title "[flywheel] add pre-commit rule blocking new .trim()" \
          --type task --priority 2 --label flywheel --label continuous-refactor
```

Monthly beads review includes a line: "any open `skill-evolution` beads that have accumulated enough evidence?"

The flywheel discipline ensures this skill doesn't ossify. It stays calibrated to your actual codebase, your actual agents, your actual pathologies. As they change, it changes.
