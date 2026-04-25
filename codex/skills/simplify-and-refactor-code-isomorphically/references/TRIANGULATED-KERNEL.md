# Triangulated Kernel — the skill's operational rules

## Contents

1. [The kernel marker contract](#the-kernel-marker-contract)
2. [The kernel (marker-delimited)](#the-kernel-marker-delimited)
3. [DISPUTED — rules not in consensus](#disputed--rules-not-in-consensus)
4. [UNIQUE — single-source rules included anyway](#unique--single-source-rules-included-anyway)
5. [How to test the kernel against code](#how-to-test-the-kernel-against-code)

---

> Following [operationalizing-expertise](../../operationalizing-expertise/SKILL.md) §"Canonical Markers and Formats": the kernel is the deterministically-parseable distillation of the skill's rules, between START/END markers so downstream tooling can extract it reliably.
>
> Every rule below is anchored to at least one quote in [CORPUS.md](CORPUS.md). Every rule says **what to do**, **when**, and **what happens if you don't**. No narrative prose inside the kernel.

## The kernel marker contract

- Every rule has a stable numeric ID (`R-nnn`) that never changes.
- Every rule cites at least one quote in CORPUS.md.
- The kernel is delimited by `<!-- KERNEL-START -->` and `<!-- KERNEL-END -->` HTML comments for deterministic extraction (`scripts/extract_kernel.sh`).
- Rules that are disputed or unique to one source land in separate sections, never inside the kernel.
- **Changes to the kernel require updating the quote bank first, then the kernel.** Kernel drift from evidence is exactly the failure operationalizing-expertise is designed to prevent.

---

## The kernel (marker-delimited)

<!-- KERNEL-START -->

### R-001 — No file deletion without explicit user approval
**When:** proposing to remove any file, folder, or symbol.
**Do:** run the 12-step dead-code safety gauntlet (DEAD-CODE-SAFETY.md). If all 11 pre-checks pass, stage to `refactor/_to_delete/` and ask the user. Wait for "yes, delete" verbatim.
**If violated:** the horror story S-1 ships in your PR. User's sync-pipeline.ts analog gets destroyed. Restoration is git-archaeological.
**Anchors:** A-1, S-1.

### R-002 — Edit tool only; never Write over existing files
**When:** making any change to a file that already exists in the tree.
**Do:** use the Edit tool (or parallel subagents Edit-ing in their own subtrees).
**If violated:** the original body's invisible behavior (S-2 WebSocket auto-subscribe, S-3 Drop impl) disappears; docstring-driven rewrites lose load-bearing side effects.
**Anchors:** A-2, S-2, S-3.

### R-003 — No script-based code changes
**When:** tempted to `sed`, run a codemod across many files, or auto-rewrite via a script.
**Do:** dispatch to parallel subagents (each takes a sub-tree with identical Edit instructions) or edit manually. The Edit tool's `allow_multiple: true` flag IS sanctioned for literal-string bulk replacement (S-15). sed/regex/custom codemods are not.
**If violated:** regex catches comments, strings, identifier substrings; damage is hard to undo; individual changes can be subtly wrong.
**Anchors:** A-2, S-15.

### R-004 — No new-variant filenames (`_v2`, `_new`, `_improved`)
**When:** tempted to create `main_v2.rs` alongside `main.rs`.
**Do:** revise in place. If the new version genuinely doesn't fit the existing file, it's likely new functionality warranting a differently-named file (not a versioned clone).
**If violated:** orphan files accumulate (VIBE-CODED P3); future agents re-evaluate which is live; the horror story risk compounds.
**Anchors:** A-3.

### R-005 — One lever per commit
**When:** making any change that will land in a commit.
**Do:** a single pattern per commit (an extraction, a merge, a rename, a type change — exactly one). Split mixed commits before landing.
**If violated:** bisect can't isolate the regression; reviewers miss subtle issues; post-incident forensics become impossible.
**Anchors:** K-2, S-4.

### R-006 — Isomorphism card filled BEFORE edit
**When:** before touching code for any candidate with Score ≥ 2.0.
**Do:** fill every row. If a row is genuinely N/A, state why. "I don't know" → write a property test FIRST.
**If violated:** silent behavior changes ship. The WebSocket/Drop/mismatches/DB-config horror stories all had unchecked axes.
**Anchors:** K-3, S-2, S-3, S-4, S-5.

### R-007 — Resource-lifecycle axis is mandatory
**When:** refactoring a type with `impl Drop`, `__del__`, `__exit__`, `defer`, try/finally, or a context-manager body.
**Do:** explicitly list the destructor/cleanup behavior in the isomorphism card. Preserve order-of-operations (LIFO for most languages).
**If violated:** see S-3 — the most-critical-for-debugging path disappears.
**Anchors:** K-3, S-3.

### R-008 — Side-effect axis is mandatory
**When:** refactoring any function that emits logs, metrics, spans, DB writes, file writes, subscriptions, events, or observable state changes.
**Do:** enumerate the side effects in the card. Verify each in the new implementation.
**If violated:** see S-2 — auto-subscribe on connect was a side effect the docstring didn't mention; rewrite from docstring lost it.
**Anchors:** K-3, S-2.

### R-009 — Rule of 3 for abstraction
**When:** tempted to extract a helper/trait/interface from similar code.
**Do:** leave 2 duplicates alone; only extract at the 3rd instance. The 3rd tells you what the axis of variance is.
**If violated:** abstraction at 2 callsites requires guessing the parameter set; the 3rd case then needs a special-case branch; the abstraction is wrong *and* you still have a copy-paste.
**Anchors:** K-1, ABSTRACTION-LADDER.md autopsies.

### R-010 — Opportunity score threshold: 2.0
**When:** ranking candidates from the duplication map.
**Do:** only accept `(LOC_saved × Confidence) / Risk ≥ 2.0`. Reject lower.
**If violated:** long-tail refactors that cost coupling for small LOC savings erode trust in the technique.
**Anchors:** SKILL.md Opportunity Matrix.

### R-011 — Tests pass count = baseline (not just "all green")
**When:** verifying after a refactor commit.
**Do:** compare pass/fail/skip *counts*. "Green" alone allows silent test-skipping.
**If violated:** see S-8 (conformance tests silently `#[ignore]`'d) and S-12 ("tests pass, I'm confident").
**Anchors:** S-8, S-12.

### R-012 — Goldens are immutable for the duration of a pass
**When:** the new output differs from the captured golden.
**Do:** stop. Either (a) the refactor is non-isomorphic and must be reverted, or (b) the change is intentional and ships as a `fix:` commit with an explicit golden re-capture. Never quietly `--update-snapshots`.
**If violated:** behavior changes ship silently; no reviewer can tell.
**Anchors:** K-3.

### R-013 — Lint warning count does not grow
**When:** after any commit.
**Do:** compare warning count to baseline. Must be ≤ baseline. Never add `#[allow]` / `// eslint-disable` / `# noqa` / `# type: ignore` to silence.
**If violated:** pathology accumulation goes unchecked; P12/P15 metrics lie.
**Anchors:** RESCUE-MISSIONS.md §Phase −1c, CONTINUOUS-REFACTOR.md layer 2.

### R-014 — Normalization is a behavior change
**When:** tempted to add `.trim()`, `.toLowerCase()`, whitespace collapse, case normalization, default substitution mid-flow.
**Do:** ship as `fix:` commit (if old behavior was wrong) OR leave alone (if it wasn't). Not isomorphic either way.
**If violated:** see S-6 — `.trim()` strips load-bearing whitespace from message bodies.
**Anchors:** S-6.

### R-015 — Defensive coding for impossible inputs is a smell
**When:** the agent's own reasoning includes the phrase "defensive coding", "just in case", "for robustness".
**Do:** stop. Verify the input can actually take the guarded value. If not, remove the guard. The phrase is rare (25 fleet sessions) but invariably marks this pathology.
**If violated:** accumulated try/catch and null-check ladders obscure real logic.
**Anchors:** S-7.

### R-016 — Conformance oracle cannot be silenced
**When:** a conformance / property / golden / integration test fails after a refactor.
**Do:** fix the refactor; never `#[ignore]` / `.skip()` / `@pytest.mark.skip` the test without a specific reason AND a tracking bead.
**If violated:** see S-8 — the definition difference is precisely what the test exists to catch; silencing it ships the difference.
**Anchors:** S-8.

### R-017 — Owner check before action
**When:** about to touch a file whose top git-blame committer is someone other than yourself / the user.
**Do:** `git log --format='%an' <path> | sort | uniq -c | sort -rn | head -1`. Ask the owner via Agent Mail if the intended change is OK. Costs 30 seconds; prevents horror stories.
**If violated:** you edit someone's intentional-but-undocumented code.
**Anchors:** DEAD-CODE-SAFETY.md step 11.

### R-018 — Siblings are accelerants, not prerequisites
**When:** the skill references `cass`, `ubs`, `multi-pass-bug-hunting`, `testing-golden-artifacts`, etc. and one isn't installed.
**Do:** use the inline fallback. Every reference has one. Log the missing sibling and proceed.
**If violated:** the skill stalls for a missing accelerant; value erodes.
**Anchors:** K-10.

### R-019 — cass via --robot/--json only
**When:** mining session history.
**Do:** `cass search "<term>" --robot --limit N`. Never bare `cass`.
**If violated:** launches a blocking TUI; agent session hangs.
**Anchors:** K-5.

### R-020 — bv via --robot-* only
**When:** triaging beads.
**Do:** `bv --robot-triage`. Never bare `bv`.
**If violated:** blocks the session (same as cass bare-TUI).
**Anchors:** K-6.

### R-021 — UBS before every commit
**When:** finalizing a commit with changed source files.
**Do:** `ubs <changed-files>`. Exit 0 → commit. Exit > 0 → fix and re-run.
**If violated:** known-bug patterns ship; real issues reach production.
**Anchors:** K-7.

### R-022 — Landing the plane (push before session end)
**When:** ending any session with uncommitted or unpushed work.
**Do:** `git status; git add; br sync --flush-only; git add .beads/; git commit; git push; git status` (final status must say "up to date with origin").
**If violated:** work is stranded locally; next session has no continuity.
**Anchors:** K-8.

### R-023 — Treat other-agent edits as your own
**When:** `git status` shows unexpected modifications you didn't make in a multi-agent session.
**Do:** treat them as yours. Do NOT stash, revert, or overwrite.
**If violated:** you destroy another agent's work; the swarm regresses.
**Anchors:** A-5.

### R-024 — No backwards-compat shims
**When:** tempted to keep a deprecated API while adding the new one.
**Do:** change the code directly. We're in early dev. No shims.
**If violated:** tech debt compounds; the reason to refactor diminishes; the codebase becomes the mess the skill exists to clean.
**Anchors:** A-4.

### R-025 — Same-file duplicate detection before ending session
**When:** closing out an agent session that Edited files.
**Do:** `rg 'fn \w+|def \w+|function \w+' -n <edited-files> | awk '{print $NF}' | sort | uniq -c | sort -rn | head`. Catches append-instead-of-edit duplicates (S-9).
**If violated:** two `create_backup` in the same file ship.
**Anchors:** S-9.

### R-026 — Orphan module check
**When:** a new `pub mod X`, `export * from './X'`, or equivalent is added.
**Do:** verify X is registered in the dispatch/registration table (packs/mod.rs, index.ts, plugins.yaml). If not, the module is dead-adjacent.
**If violated:** see S-10 — `pub mod borg` compiled but never registered; feature silently absent from user.
**Anchors:** S-10.

### R-027 — The isomorphism card is a pre-commit artifact
**When:** landing the refactor commit.
**Do:** paste the filled-in card verbatim into the commit message body.
**If violated:** future git-blame / bisect / post-incident forensics can't recover the reasoning; the card becomes lost when the PR merges.
**Anchors:** METHODOLOGY.md Phase G.

### R-028 — LOC delta must match prediction within ±10%
**When:** verifying after the edit.
**Do:** compute actual LOC delta; compare to the score's predicted delta. Mismatch > 10% means the scoring was wrong; recalibrate confidence priors for future scores.
**If violated:** the opportunity matrix degrades into guessing over time.
**Anchors:** SKILL.md Opportunity Matrix, METHODOLOGY.md Phase F.

### R-029 — Rollback plan is mandatory for Tier-3
**When:** shipping any Tier-3 architectural candidate (DB migration, service merge, ORM swap).
**Do:** include a specific rollback runbook in the commit / PR description. Not just "git revert"; the actual stateful steps (DB restore, flag flip, deploy).
**If violated:** rollback happens ad-hoc under pressure; state corruption possible.
**Anchors:** DB-SCHEMAS.md §"Migration rollback patterns".

### R-030 — User vocabulary = trigger phrases
**When:** a user prompt contains any of: "reduce file proliferation", "consolidate", "deduplicate", "simplify", "unify", "over-engineered", "remove lines", "DRY", "extract helper", "reuse component", "prune redundant", "reduce complexity".
**Do:** activate this skill. These are the canonical triggers from fleet evidence.
**If violated:** skill misses its cue; the refactor is ad-hoc rather than disciplined.
**Anchors:** S-13.

<!-- KERNEL-END -->

---

## DISPUTED — rules not in consensus

These rules are reasonable but not anchored in enough evidence to belong in the kernel. Reviewers may disagree.

### D-001 — Every refactor PR should have a reviewer
Rationale: catches hostile patterns. But: slows cadence; for Tier-1 cheap wins the overhead may outweigh the benefit.
**Decision:** not in kernel. Teams opt in via CONTINUOUS-REFACTOR.md layer 3 if they want it.

### D-002 — Always write property tests before refactoring
Rationale: gold standard for invariant preservation. But: overkill for P12 dead-import removal, P30 console.log cleanup, etc.
**Decision:** in kernel only when isomorphism card has "I don't know" rows (R-006).

### D-003 — Target 80% code coverage during rescue
Rationale: common industry benchmark. But: [RESCUE-MISSIONS.md](RESCUE-MISSIONS.md) explicitly warns that coverage-chasing produces tautological tests.
**Decision:** not in kernel. Coverage is the wrong metric; characterization tests + property tests + golden-path integration are right.

### D-004 — Every pathology should have an automatic fix
Rationale: cleaner, faster. But: automatic fixes are exactly the codemod pattern AGENTS.md forbids (A-2).
**Decision:** detection is automated (slop_detector); fixes are manual (one-lever discipline).

---

## UNIQUE — single-source rules included anyway

These rules have only one supporting quote but are included because the consequence of failure is severe.

### U-001 — "Tests pass → done" is the danger signal
Anchor: S-12 only.
Included because: this moment is exactly when every horror story crystallized. Low evidence base, high-stakes rule.
→ This rule is R-011 / R-016 reinforced.

### U-002 — Agents copy-pattern-match from themselves
Anchor: S-14 only.
Included because: encouraging explicit `cass` reach-out (rather than reinvention) is a productivity multiplier.
→ Informs KICKOFF-PROMPTS.md and PROMPT-ENGINEERING.md.

---

## How to test the kernel against code

Every rule in the kernel has an implicit test: "given a PR that violates this rule, would the verify/review/gauntlet process catch it?"

```bash
# Extraction for tooling
awk '/<!-- KERNEL-START -->/,/<!-- KERNEL-END -->/' references/TRIANGULATED-KERNEL.md > /tmp/kernel.md
```

For each rule ID `R-nnn`:
1. Write a minimal PR diff that violates it.
2. Run through the verify pipeline + peer-review simulation.
3. If the violation surfaces, the rule has working enforcement.
4. If not, identify which script/hook/prompt needs to add a check.

**Coverage audit:** a future maintenance task is to confirm every kernel rule has at least one automated or prompt-level enforcement. Missing enforcement means the rule is a wish, not a guarantee.

The `scripts/lint_ceiling.sh`, `dead_code_safety_check.sh`, `verify_isomorphism.sh`, `ai_slop_detector.sh`, and CI-gate suite together cover roughly 80% of the rules. The remaining 20% depend on reviewer judgment + the isomorphism card's honesty.
