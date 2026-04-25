# Prompt Engineering for Refactor Sessions

> Meta-level: how to write prompts that get the skill's benefits and avoid the AI-slop pitfalls. This file is for the human-in-the-loop (or the orchestrator agent) who is *starting* a refactor session. The prompt is the first lever; get it wrong and every downstream step compounds the mistake.

## Contents

1. [The prompt-shape typology](#the-prompt-shape-typology)
2. [The six dangerous prompt shapes](#the-six-dangerous-prompt-shapes)
3. [The six recommended prompt shapes](#the-six-recommended-prompt-shapes)
4. [Nudges that change refactor behavior](#nudges-that-change-refactor-behavior)
5. [Explicit invariant reminders](#explicit-invariant-reminders)
6. [The five-sentence universal opener](#the-five-sentence-universal-opener)
7. [Anti-prompts — what the agent should push back on](#anti-prompts--what-the-agent-should-push-back-on)
8. [Exemplar pack](#exemplar-pack)

---

## The prompt-shape typology

Refactor prompts fall into shapes. The shape constrains what the agent will do more than the literal instruction.

```
Shape axes:
  A. Specificity:   loose ...... specific ...... hyper-specific
  B. Scope:         open ....... bounded ....... pinned
  C. Success def:   implicit ... explicit ...... measurable
  D. Invariants:    unstated ... stated ........ enforced
  E. Stopping:      at-agent ... at-budget ..... at-verify
```

Good prompts are specific, bounded, measurable, with stated invariants, stopped at verify. Bad prompts are loose, open, implicit, unstated, stopped when the agent feels done.

---

## The six dangerous prompt shapes

### D-1: "Clean this up"

```
Clean up this file.
```

**Why it's dangerous:**
- "Clean" is undefined. The agent picks what looks messy to it.
- Likely produces defensive try/catch (S-7), renamed variables, reformatted code, removed "unused" imports.
- No isomorphism card. No verification.
- Nearly always mixes ≥3 levers.

**Fix:**
```
Reduce LOC in this file by 20%+ via the simplify-and-refactor-code-isomorphically skill.
Fill isomorphism cards; one lever per commit; verify each. Stop at 20% or when
no candidate scores ≥ 2.0.
```

### D-2: "Refactor to use <pattern>"

```
Refactor this to use the observer pattern.
```

**Why it's dangerous:**
- Pattern-driven refactoring skips the "do you need the pattern?" question.
- Jumps up the abstraction ladder.
- Almost always over-engineered.

**Fix:**
```
These 3 functions send similar events to similar handlers. Is there a Type II
duplication here? Score it. If accepted, collapse at the lowest rung that fits.
```

### D-3: "Simplify this function"

```
Simplify this function.
```

**Why it's dangerous:**
- Vague verb. Might mean inline, extract, rename, reformat.
- Agent picks the shortest path, often inlining where it shouldn't or extracting where it shouldn't.

**Fix:**
```
Function foo() has cyclomatic complexity 18 (radon). Reduce to ≤10 via
extract-function, without changing behavior. Apply the skill's loop.
```

### D-4: "Make this more idiomatic"

```
Make this Rust code more idiomatic.
```

**Why it's dangerous:**
- "Idiomatic" is a fashion target. Rust idioms change across versions.
- Likely produces a sweep across many files, mixed levers, and possibly net LOC growth.

**Fix:**
```
Scan src/ with `cargo clippy --all-targets -- -W clippy::pedantic`. Triage the top
10 non-style clippy suggestions by blast radius. Apply one per commit with an
isomorphism card. Stop after 10 or when any suggestion requires behavior change.
```

### D-5: "Remove duplication"

```
This codebase has too much duplication. Fix it.
```

**Why it's dangerous:**
- No map. Agent eyeballs; misses the big duplicates, merges accidental rhymes (Type V).
- Risks Type IV merges (semantic clones with different invariants).

**Fix:**
```
Run phase B of the simplify-and-refactor skill: scripts/dup_scan.sh + ai_slop_detector.sh.
Produce duplication_map.md. Score candidates. Do NOT merge anything until I've
seen the map. Present top 10 with types (I/II/III/IV/V) and scores.
```

### D-6: "Make tests pass"

```
The tests are failing. Refactor until they pass.
```

**Why it's dangerous:**
- Might produce `#[ignore]` across the board (S-8).
- Might rewrite tests to match broken code.
- The refactor now has an unfalsifiable success criterion.

**Fix:**
```
Tests X, Y, Z are failing. For each: (a) identify whether the test or the code
is wrong, (b) fix the correct side with a `fix:` commit, (c) never refactor and
test-adjust in the same commit. If the tests were correct, the refactor was wrong.
```

---

## The six recommended prompt shapes

### R-1: The loop-activation prompt

Use when: starting a solo refactor pass.
```
Apply simplify-and-refactor-code-isomorphically to <PATH>.
Goal: <concrete measurable, e.g., -20% LOC in this module>.
Budget: <time or candidate count>.

Phase 0..G per SKILL.md. Stop when budget reached or no candidate scores ≥ 2.0.
Invariants: AGENTS.md (Edit only, one lever, no deletion without approval).
```

### R-2: The scoped-candidate prompt

Use when: you've already identified the candidate and want the agent to execute.
```
Candidate: collapse 3x send_{text,image,file} into one send(kind, ...) per
TECHNIQUES.md §1.2.

Fill the isomorphism card BEFORE editing. Edit tool only. Verify per
scripts/verify_isomorphism.sh. Commit with the card verbatim in the body.
```

### R-3: The exploratory-map prompt

Use when: you want to see the landscape before committing.
```
I don't know where to start. Produce Phase B artifacts for this repo (or
<scope>):
  - scripts/dup_scan.sh output
  - scripts/ai_slop_detector.sh output
  - scripts/metrics_snapshot.sh snapshot

Then rank findings by predicted opportunity (LOC × Confidence / Risk).
DO NOT edit code. Just produce the map. I'll pick from there.
```

### R-4: The rescue-kickoff prompt

Use when: the codebase is degraded.
```
[Paste RESCUE-MISSIONS.md kickoff prompt.]
Target: <scope>. Start with Phase -1a.
```

### R-5: The review-request prompt

Use when: you want a second agent (or a different model) to audit a PR.
```
[Paste the Reviewer-role prompt from KICKOFF-PROMPTS.md.]
PR: <ref>. Focus especially on the horror-story pattern S-1 (DEAD-CODE-SAFETY.md).
```

### R-6: The handoff prompt

Use when: continuing a session another agent started.
```
[Paste Cross-agent handoff from KICKOFF-PROMPTS.md.]
Previous run: <run-id>. Previous LEDGER has <n> rows. Pick up after the last
verified commit.
```

---

## Nudges that change refactor behavior

Small phrase additions that measurably change agent behavior:

| Nudge | Effect |
|-------|--------|
| "Before editing, fill the isomorphism card." | agent slows and considers axes |
| "Paste the card verbatim in the commit message." | card survives into git history |
| "One lever per commit." | refactor and rename don't combine |
| "Do NOT delete any file. Move to `refactor/_to_delete/`." | prevents S-1 |
| "Before concluding a file is dead, run `./scripts/dead_code_safety_check.sh`." | prevents S-1 |
| "No defensive coding — if the input can't take that value, don't guard it." | prevents S-7 |
| "No normalization (`.trim()`, `.toLowerCase()`) mid-flow." | prevents S-6 |
| "If you want to use `sed`, stop and use parallel subagents instead." | enforces A-2 |
| "Check for same-file duplicate functions after each edit." | catches S-9 |
| "If the orchestrator edits between your commits, treat them as yours." | prevents swarm-disruption |

These are **reinforcements**, not the core instruction. They go at the end of the prompt after the main task.

---

## Explicit invariant reminders

Some invariants are so load-bearing they deserve to be called out even when the agent has read AGENTS.md:

```
Invariants (AGENTS.md; repeated here because they're load-bearing):
  1. No file deletion without my explicit approval (Rule 1).
  2. No sed/codemod — use parallel subagents or Edit.
  3. No `_v2` / `_new` / `_improved` filenames.
  4. No backwards-compat shims.
  5. UBS before commit.
  6. Treat other agents' edits as your own.

Invariants (this skill):
  7. Isomorphism card before edit. Every axis.
  8. One lever per commit.
  9. Goldens immutable for the pass.
  10. Lint warning count ≤ baseline.
  11. No test silencing (`#[ignore]`) without a tracking bead.
```

A prompt that calls these out explicitly catches ~70% of would-be violations before they happen. Token cost: ~150 tokens. Worth it.

---

## The five-sentence universal opener

For any refactor prompt, prefix with this:

```
1. Read AGENTS.md. Honor its invariants.
2. Read references/TRIANGULATED-KERNEL.md if uncertain about a rule.
3. Before any edit, fill the relevant isomorphism card.
4. One lever per commit. Edit tool only. No deletion without my "yes".
5. At pass end: metrics dashboard + ledger + push.
```

Five sentences, ~40 tokens. Frames the session correctly.

---

## Anti-prompts — what the agent should push back on

When a user's prompt matches one of these shapes, the agent should **push back** rather than execute:

### AP-1: "Delete all the dead code"
**Push back:** "Per AGENTS.md Rule 1, I can't delete files without your explicit approval. I can run the 12-step dead-code safety gauntlet on candidates you identify. Want me to start with a specific file, or produce a list of candidates for you to approve?"

### AP-2: "Just use sed to rename foo to bar everywhere"
**Push back:** "Per AGENTS.md, script-based changes aren't allowed. Options: (a) I can dispatch parallel subagents each Edit-ing their subtree, or (b) I can do it manually file by file. Subagents is faster for this. OK to proceed with (a)?"

### AP-3: "Run this big refactor and push to main without a PR"
**Push back:** "That skips review, which is the main way the isomorphism guarantee is audited. I'd rather: (a) open a PR branch, (b) run the full loop with commit-level isomorphism cards, (c) ask for your approval before merge. OK?"

### AP-4: "Just make the tests pass; use `#[ignore]` if needed"
**Push back:** "Per R-016, silencing conformance oracles papers over what the test was designed to catch. I'd rather identify which test is catching a real bug vs. which test has drifted from intent. Can you tell me which failing test(s) you've investigated? I'll start there."

### AP-5: "This file is dead code, delete it"
**Push back:** "Can I run the 12-step safety gauntlet first (`./scripts/dead_code_safety_check.sh <file>`)? It takes ~5 seconds and catches the horror-story pattern (S-1). If all 11 pre-checks pass, I'll stage to `refactor/_to_delete/` and ask before `rm`."

### AP-6: "Add try/catch to be safe"
**Push back:** "Per S-7, that's the defensive-coding reflex. Can you tell me: (a) which specific exception you're worried about, (b) which caller would handle it differently than the current behavior? If both answers are 'none', the try/catch will just hide bugs. If you have specific answers, we can wrap accordingly."

---

## Exemplar pack

Concrete prompts that have worked in real sessions.

### Exemplar 1: UI component unification

```
The frontend has ~12 button-like components: PrimaryButton, SecondaryButton,
DangerButton, GhostButton, LinkButton, IconButton, etc. Suspected heavy
duplication.

Phase B:
  1. Run `jscpd` and `similarity-ts` on src/components/buttons/.
  2. Produce a duplication map. Classify each pair as Type I/II/III/IV/V.
  3. For Type IV (semantic-but-differ), do NOT propose merge.
  4. For Type V (accidental rhyme), do NOT propose merge.
  5. Present candidates with scores.

Do NOT edit yet. I'll approve candidates from the map.
```

### Exemplar 2: Rust error-enum consolidation

```
Three crates each define their own error enums (UserError, OrderError,
PostError) with overlapping variants (DbRead, NotFound, Invalid).

Goal: lift common variants to a shared DomainError, keep feature-specific
variants in per-crate enums that wrap DomainError.

Apply the skill's loop. Per crate: one commit. Isomorphism card must address:
  - `From` impl semantics (widening?)
  - `match` exhaustiveness in callers
  - `Display` format output (any log-parsing downstream?)

If Display format changes, ship as `fix:` then `refactor:`.
```

### Exemplar 3: Dead-code evaluation

```
File `src/services/oldPaymentProcessor.ts` looks unused to me. Can you run the
12-step safety gauntlet (`./scripts/dead_code_safety_check.sh`) and report the
results? Do NOT delete or stage; just run the check and show me the table.

If any check fails, leave the file alone and file a bead for my review.
```

### Exemplar 4: The slop cleanup

```
Apply the simplify-and-refactor-code-isomorphically skill in AI-SLOP-CLEANUP
mode:

  1. Run scripts/ai_slop_detector.sh. Save slop_scan.md.
  2. For each pathology (P1-P40), score candidates and accept Score ≥ 2.0.
  3. Follow the attack order in VIBE-CODED-PATHOLOGIES.md §"Updated attack order".
  4. First pass: Tier-1 cheap wins only (P11, P12, P30, etc.).
  5. Second pass: behavior-preserving structural (P3, P8, P25, P35, P38).
  6. STOP after 20 commits. Report metrics delta.

Invariants: all AGENTS.md rules. No behavior changes without split commits.
```

### Exemplar 5: The weekly pass

```
Weekly refactor pass, budget 60 minutes.

1. `bv --robot-triage --label refactor` — pick top 2 ready beads.
2. For each: fill isomorphism card, edit, verify, commit, ledger.
3. If verify fails on bead 1: revert, add reason to the bead, still try bead 2.
4. Stop at 60 min regardless.

Report: (a) what shipped, (b) what was blocked, (c) current metrics delta
vs. prior week's snapshot.
```

### Exemplar 6: Post-incident

```
Post-incident refactor planning for INC-4823 (payment processor returned
success on a failed API call due to swallowed exception).

Do NOT refactor yet. This is planning.

1. Read the incident timeline: <paste link or text>.
2. Find the exact line where behavior went wrong.
3. Identify the pathology class. P1 (over-defensive try/catch)? P10
   (swallowed Promise rejection)?
4. File a bead `[post-incident INC-4823] <pathology> in <file>` with:
   - pathology ID
   - line reference
   - proposed fix
   - test that would detect recurrence
5. Suggest whether this is weekly-pass-sized or monthly-pass-sized.

Output: a plan, not commits.
```

---

## When to write your own prompt vs. use an exemplar

- **Exemplar fits**: use it verbatim, plug in variables.
- **Exemplar is close but doesn't fit**: remix exemplars. Most real prompts are 2–3 exemplars braided.
- **No exemplar fits**: write a new prompt using the universal opener + recommended shape + nudges + invariants.

After running 5+ refactor sessions, file your own prompts that worked into `PROMPT-ENGINEERING.md` under a new "Exemplar pack" section. The skill grows through use.
