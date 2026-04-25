# Corpus — Quote Bank for the Refactor Methodology

## Contents

1. [Quote format](#quote-format)
2. [Tag legend](#tag-legend)
3. [AGENTS.md anchors (A-*)](#agentsmd-anchors-a-)
4. [Real-session-evidence anchors (S-*)](#real-session-evidence-anchors-s-)
5. [Sibling-skill anchors (K-*)](#sibling-skill-anchors-k-)
6. [Triangulation map — rule → quote IDs](#triangulation-map--rule--quote-ids)
7. [How to add a new quote](#how-to-add-a-new-quote)

---

> Following [operationalizing-expertise](../../operationalizing-expertise/SKILL.md) `references/CORPUS.md` and `quote_bank.md` patterns: each load-bearing rule in this skill is anchored to at least one quotable source — a verbatim snippet from indexed agent sessions, a cited passage from the sibling skills this one composes, or the project's own AGENTS.md.
>
> The point of the quote bank is **provenance**. If a future reviewer asks "why does the skill insist on Edit-only?", the answer is a specific quote ID they can audit.

## Quote format

```
### <quote-id> — <short title>
**Source:** <path or URL>
**Tag(s):** <comma-separated tags>
**Verbatim:**
> <exact quoted text, preserving whitespace and typos>

**Rule derived:** <the operational rule this evidence supports>
**Used by:** <where in the skill this quote is cited>
```

---

## Tag legend

- `rule1`       — AGENTS.md Rule Number 1 (no deletion)
- `dead-code`   — the dead-code-deletion horror story and prevention
- `defensive`   — defensive-coding pathology evidence
- `iso-axis`    — isomorphism axis being tested
- `anti-script` — no-script-based-changes evidence
- `one-lever`   — one-lever-per-commit evidence
- `collapse`    — successful collapse / simplification
- `broke`       — behavior-breaking refactor evidence
- `user-phrase` — verbatim user prompt
- `process`     — process-level rule (bootstrap, cadence)
- `sibling`     — cross-skill composition rule

---

## AGENTS.md anchors (A-*)

### A-1 — No file deletion without explicit permission
**Source:** `AGENTS.md` §"RULE NUMBER 1: NO FILE DELETION"
**Tag(s):** `rule1, dead-code`
**Verbatim:**
> **YOU ARE NEVER ALLOWED TO DELETE A FILE WITHOUT EXPRESS PERMISSION.** Even a new file that you yourself created, such as a test code file. You have a horrible track record of deleting critically important files or otherwise throwing away tons of expensive work. As a result, you have permanently lost any and all rights to determine that a file or folder should be deleted.

**Rule derived:** the dead-code-safety 12-step gauntlet never ends in unilateral deletion; it ends in asking the user with evidence.
**Used by:** [DEAD-CODE-SAFETY.md](DEAD-CODE-SAFETY.md), [OPERATOR-CARDS.md](OPERATOR-CARDS.md) ✋ Ask-Before-Delete, SKILL.md Anti-Patterns.

---

### A-2 — No script-based code changes
**Source:** `AGENTS.md` §"Code Editing Discipline → No Script-Based Changes"
**Tag(s):** `anti-script`
**Verbatim:**
> **NEVER** run a script that processes/changes code files in this repo. Brittle regex-based transformations create far more problems than they solve.
> - **Always make code changes manually**, even when there are many instances
> - For many simple changes: use parallel subagents
> - For subtle/complex changes: do them methodically yourself

**Rule derived:** Use Edit tool; split across parallel subagents for scale; never sed/codemod.
**Used by:** SKILL.md Pre-Flight, ANTI-PATTERNS.md, OPERATOR-CARDS.md 🚫 No-Codemod.

---

### A-3 — No file proliferation
**Source:** `AGENTS.md` §"No File Proliferation"
**Tag(s):** `anti-script, one-lever`
**Verbatim:**
> If you want to change something or add a feature, **revise existing code files in place**.
> **NEVER** create variations like:
> - `mainV2.rs`
> - `main_improved.rs`
> - `main_enhanced.rs`

**Rule derived:** No new-variant filenames. Revise in place or create genuinely new functionality.
**Used by:** VIBE-CODED-PATHOLOGIES.md P3, DEAD-CODE-SAFETY.md step 10.

---

### A-4 — No backwards compat in early dev
**Source:** `AGENTS.md` §"Backwards Compatibility"
**Tag(s):** `process`
**Verbatim:**
> We do not care about backwards compatibility—we're in early development with no users. We want to do things the **RIGHT** way with **NO TECH DEBT**.
> - Never create "compatibility shims"
> - Never create wrapper functions for deprecated APIs
> - Just fix the code directly

**Rule derived:** Tier-3 migrations don't need compat shims in this codebase. Rename freely.
**Used by:** TECHNIQUES.md §2.1 data-model unification, DB-SCHEMAS.md.

---

### A-5 — Treat other-agent changes as your own
**Source:** `AGENTS.md` §"Note for Codex/GPT-5.2"
**Tag(s):** `process`
**Verbatim:**
> You NEVER, under ANY CIRCUMSTANCE, stash, revert, overwrite, or otherwise disturb in ANY way the work of other agents. Just treat those changes identically to changes that you yourself made. Just fool yourself into thinking YOU made the changes and simply don't recall it for some reason.

**Rule derived:** In multi-agent swarm mode, never `git stash` or revert uncommitted work from other panes.
**Used by:** AGENT-COORDINATION.md.

---

## Real-session-evidence anchors (S-*)

### S-1 — The "fgucking DELETED" horror story
**Source:** `gemini/151fe631.../2026-01-28T23-46/29ad1602 :: L28` (via `cass` mining, see REAL-SESSION-EVIDENCE.md)
**Tag(s):** `dead-code, broke, user-phrase, rule1`
**Verbatim:**
> **User:** "wait you fgucking DELETED that as dead code instead of USING IT properly????? WHAT THE FUCK"

**Context:** agent had deleted `src/lib/skills/sync-pipeline.ts` + its test file, calling it "dead code with a misleading/broken implementation." The file was the canonical intended implementation path, not yet wired in.

**Rule derived:** "Dead code" is the single most dangerous phrase an agent can compose. Run the full 12-step gauntlet; never decide unilaterally.
**Used by:** CASE-STUDIES.md §"the deleted as dead code" vignette, DEAD-CODE-SAFETY.md, OPERATOR-CARDS.md ✋ Ask-Before-Delete.

---

### S-2 — WebSocket auto-subscribe silently dropped
**Source:** `b7da6852.../2026-01-11T00-48 :: L8`
**Tag(s):** `broke, iso-axis, defensive`
**Verbatim:**
> The original implementation auto-subscribed clients connecting to `/agents/:id/ws`. My initial replacement lost this behavior.

**Rule derived:** Rewrite-from-docstring loses invisible side effects. Edit, don't Write. The ISOMORPHISM.md "side effects" axis must be answered explicitly, not marked N/A.
**Used by:** CASE-STUDIES.md HS#3, ISOMORPHISM.md, VIBE-CODED-PATHOLOGIES.md P10.

---

### S-3 — LogSink panic-flush lost during refactor
**Source:** `37abaf19.../2026-02-02T02-27 :: L8`
**Tag(s):** `broke, iso-axis`
**Verbatim:**
> `LogSink` final flush on panic (often the most critical error) was lost. Fix: I implemented `Drop` for `LogSink` ... to perform a best-effort flush.

**Rule derived:** Resource lifecycle (Drop / __del__ / defer / context-manager __exit__) is invisible in signatures. The isomorphism card's "Resource lifecycle" row must be filled for any refactor of a type with destructors.
**Used by:** CASE-STUDIES.md HS#4, ISOMORPHISM.md, RUST-DEEP.md, PYTHON-DEEP.md.

---

### S-4 — Mismatches variable removed during extract
**Source:** `beads-rust/2026-03-09T20-58-4e990d1a :: L78`
**Tag(s):** `broke, one-lever`
**Verbatim:**
> I've accidentally broken Step 5 by removing the `mismatches` variable. I need to either re-introduce it or refactor Step 5.

**Rule derived:** Extract-function refactors must audit downstream binding dependencies, not just the span being extracted. The block's outputs are part of its contract.
**Used by:** CASE-STUDIES.md HS#2, METHODOLOGY.md Phase E.

---

### S-5 — Provisioning DB regressed to :memory:
**Source:** `597f8f93.../2026-01-15T04-33 :: L6`
**Tag(s):** `broke, iso-axis`
**Verbatim:**
> SQLite database (`:memory:`) because the `DEFAULT_PROVISIONING_CONFIG` was not configured with a file path. This meant all provisioning job state would be lost.

**Rule derived:** Configuration defaults are observable side effects. Refactoring defaults needs an end-to-end "empty-env" test.
**Used by:** CASE-STUDIES.md HS#5, VIBE-CODED-PATHOLOGIES.md P20.

---

### S-6 — Reflex .trim() destroys payload
**Source:** `bca73c52.../2026-03-03T06-09-1f392bdb :: L81`
**Tag(s):** `broke, iso-axis, defensive`
**Verbatim:**
> The `.trim()` call strips all whitespace from message bodies, causing silent data loss.

**Rule derived:** Normalization (`.trim()`, `.toLowerCase()`, whitespace collapse) is a behavior change. If you add it during refactor, it's either a `fix:` commit (if old behavior was wrong) or a bug (if it wasn't). Never isomorphic.
**Used by:** VIBE-CODED-PATHOLOGIES.md P23.

---

### S-7 — Defensive coding is best
**Source:** `gemini/7ed19ce6.../2026-01-15T14-00 :: L134` and 24 other fleet sites
**Tag(s):** `defensive`
**Verbatim:**
> prompts come from a curated registry, **defensive coding is best**.

**Rule derived:** "defensive coding" used to justify adding validation for impossible inputs is a cargo-cult smell. The phrase appears in only 25 fleet sessions but every instance is this pathology — rare, high-signal literal.
**Used by:** VIBE-CODED-PATHOLOGIES.md P1/P7, REAL-SESSION-EVIDENCE.md.

---

### S-8 — Conformance tests #[ignore]'d to paper over drift
**Source:** `beads-rust/2026-01-17T19-35-cbc6379a :: L79-87`
**Tag(s):** `broke, iso-axis`
**Verbatim:**
> adding `#[ignore]` to `conformance_stale_*` tests **because br and bd have different definitions of 'stale' or different default thresholds**.

**Rule derived:** Silencing a conformance oracle to unblock a PR is the isomorphism-violation smoking gun. The difference in definitions is the thing the skill exists to surface and address. Each `#[ignore]` needs a specific reason + a bead for follow-up.
**Used by:** RESCUE-MISSIONS.md §Phase −1a, ANTI-PATTERNS.md.

---

### S-9 — Same-file duplicate function (append instead of edit)
**Source:** `gemini/ad76103.../2026-02-16T02-27 :: L87`
**Tag(s):** `collapse`
**Verbatim:**
> `create_backup` is duplicated in the same file: `src/cli/uninstall.rs` has `create_backup` at line 670 AND at line 760.

**Rule derived:** Agents sometimes append a new version of a function instead of editing the existing one, especially with fuzzy-match Edit tools. Grep function names in-file after each session.
**Used by:** VIBE-CODED-PATHOLOGIES.md P3, CONTINUOUS-REFACTOR.md pre-commit hook.

---

### S-10 — Orphan module compiled but not registered
**Source:** `gemini/6e93ebe2.../2026-01-10T22-42 :: L221`
**Tag(s):** `dead-code, collapse`
**Verbatim:**
> Yes, `pub mod borg;` is there. But is it registered in `src/packs/mod.rs`? I saw `PackEntry::new('backup.restic', ...)`. I did NOT see `backup.borg`.

**Rule derived:** "Orphan module" (`pub mod X`) without registration table is a common refactor-adjacent bug. Detection: grep the registration table and compare to declared modules.
**Used by:** DEAD-CODE-SAFETY.md step 5 (build references), VIBE-CODED-PATHOLOGIES.md P3.

---

### S-11 — Successful N-functions → registry collapse
**Source:** `gemini/b92018ad.../2026-02-12T15-05 :: L30-31`
**Tag(s):** `collapse, user-phrase`
**Verbatim:**
> I'll consolidate all `updateSlider` functions into one clean, registry-driven `setupEventListeners`. ... added `updateSliderUniversal` and restored a simplified `updateStats`. Now, I'll locate and replace the old `setupEventListeners` with a registry-based version to significantly reduce redundant code.

**Rule derived:** The "N near-identical update_X fns → data-driven registry" is a canonical Type-II collapse. Safe at rung 3. ~60 LOC removed on typical UIs.
**Used by:** CASE-STUDIES.md, TECHNIQUES.md, MICROPATTERNS.md M-T1.

---

### S-12 — "Tests pass. I'm confident"
**Source:** `8a6b33f2.../2026-01-10T21-37 :: L35`
**Tag(s):** `broke, one-lever`
**Verbatim:**
> Tests pass. I'm confident. I'll briefly scan `src/search/query.rs` for obvious issues but won't dig deep.

**Rule derived:** The moment the agent says "tests pass → done" is precisely when to keep looking. Tests cover what was tested; the card covers what was unknown.
**Used by:** ANTI-PATTERNS.md, ISOMORPHISM.md §"Checklist of last resort".

---

### S-13 — User phrases (vocabulary)
**Source:** cross-session aggregate; see REAL-SESSION-EVIDENCE.md §"User vocabulary"
**Tag(s):** `user-phrase`
**Verbatim:**
Representative phrases:
> "reduce file proliferation" / "consolidate shared command utilities" / "unify the two diverging conventions" / "deduplicate recipient names before the archive write" / "significantly reduce redundant code" / "prune the redundant code at the end of the file" / "reduce the complexity of `strip_env` by extracting helper functions" / "simplify its construction in tests and mappings" / "over-engineered for a simple character reveal"

**Rule derived:** These 20 phrases are the "Use when" triggers for the skill's description. Activation phrases appear as user prompts at realistic fleet frequency.
**Used by:** SKILL.md frontmatter description, PROMPT-ENGINEERING.md.

---

### S-14 — Agents copy-pattern-match from themselves
**Source:** pattern seen across many sessions, e.g., `gemini/... :: "Wait, I should check ... to see how I implemented it there"`
**Tag(s):** `user-phrase, collapse`
**Verbatim:**
> Wait, I should check ... to see how I implemented it there.

**Rule derived:** Agents frequently want to look at prior implementations. `cass` makes this efficient: `cass search "<pattern>" --robot --limit 5`. Encourage explicit `cass` reach-out in prompts rather than from-scratch reinvention.
**Used by:** KICKOFF-PROMPTS.md, PROMPT-ENGINEERING.md.

---

### S-15 — Bulk-replace with allow_multiple
**Source:** `mcp-agent-mail-rust/session-2026-03-08T21-57 :: L141`
**Tag(s):** `collapse, anti-script`
**Verbatim:**
> bulk replace with `allow_multiple: true` to unify the `redacted: false, redaction_reason: None,` pattern across all relevant files.

**Rule derived:** The Edit tool's `allow_multiple: true` flag is the *sanctioned* path for literal-string bulk replacement — not a codemod exception. It replaces *identical* spans across files. Not a sed/codemod (which were prohibited per AGENTS.md A-2). Acceptable when: (a) the string is truly identical across files, (b) no nearby context differs, (c) one-lever commit.
**Used by:** TECHNIQUES.md, METHODOLOGY.md Phase E, REAL-SESSION-EVIDENCE.md.

---

## Sibling-skill anchors (K-*)

### K-1 — Rule of 3 (extract on the third case)
**Source:** [sw/references/ARCHETYPES.md](../../sw/references/ARCHETYPES.md) and common XP lore
**Tag(s):** `collapse`
**Verbatim:**
> Two is a coincidence; three is a pattern.

**Rule derived:** Never abstract at 2 callsites. Wait for the third — that's the one that tells you what the axis of variance is.
**Used by:** ABSTRACTION-LADDER.md §"The Rule of 3, restated".

---

### K-2 — Profile before optimizing (from extreme-software-optimization)
**Source:** [extreme-software-optimization/SKILL.md](../../extreme-software-optimization/SKILL.md) §"The One Rule"
**Tag(s):** `process, sibling`
**Verbatim:**
> **The One Rule:** Profile first. Prove behavior unchanged. One change at a time.

**Rule derived:** This skill mirrors that discipline in a different axis: measure duplication first. Prove isomorphism for each change. One lever per commit. The mirror of optimization's "one lever per perf change" is refactor's "one lever per simplification."
**Used by:** SKILL.md "The One Rule", METHODOLOGY.md, CROSS-SKILL.md.

---

### K-3 — Isomorphism proof template (from extreme-software-optimization)
**Source:** [extreme-software-optimization/SKILL.md](../../extreme-software-optimization/SKILL.md) §"Isomorphism Proof Template"
**Tag(s):** `iso-axis, sibling`
**Verbatim:**
> Ordering preserved: [yes/no + why]
> Tie-breaking unchanged: [yes/no + why]
> Floating-point: [identical/N/A]
> RNG seeds: [unchanged/N/A]
> Golden outputs: sha256sum -c golden_checksums.txt ✓

**Rule derived:** This skill adopts the same axes + expands to side effects, laziness, type narrowing, React reconciliation, resource lifecycle — the axes that matter for refactors but not necessarily for perf.
**Used by:** SKILL.md "Isomorphism Proof", ISOMORPHISM.md.

---

### K-4 — Skills are for Claude, not humans (from sw)
**Source:** [sw/references/MINDSET.md](../../sw/references/MINDSET.md)
**Tag(s):** `sibling, process`
**Verbatim:**
> Skills are instructions for *you* (the agent). Write what would make YOU understand faster and work better.

**Rule derived:** This skill's prose style is dense-but-clear. No tutorial hand-holding. Every line justifies its token cost.
**Used by:** every reference file's style; also guides the "one-sentence update" tone-of-voice rule.

---

### K-5 — cass usage contract
**Source:** [cass/SKILL.md](../../cass/SKILL.md) §"Robot Mode"
**Tag(s):** `sibling`
**Verbatim:**
> Never run bare `cass` (TUI). Always use `--robot` or `--json`.

**Rule derived:** When the skill instructs agents to search prior sessions for precedent, it's always via `cass search "<term>" --robot --limit N`. Never bare `cass`.
**Used by:** KICKOFF-PROMPTS.md, CROSS-SKILL.md, REAL-SESSION-EVIDENCE.md.

---

### K-6 — bv --robot-* flags only
**Source:** [bv/SKILL.md](../../bv/SKILL.md) §"CRITICAL"
**Tag(s):** `sibling`
**Verbatim:**
> **CRITICAL: Use ONLY `--robot-*` flags. Bare `bv` launches an interactive TUI that blocks your session.**

**Rule derived:** Triage via `bv --robot-triage` only. CI / continuous-refactor automation never hits the TUI.
**Used by:** CONTINUOUS-REFACTOR.md, AGENT-COORDINATION.md.

---

### K-7 — UBS before commit (AGENTS.md + ubs/SKILL.md)
**Source:** `AGENTS.md` §"UBS" and [ubs/SKILL.md](../../ubs/SKILL.md)
**Tag(s):** `process, sibling`
**Verbatim:**
> `ubs <changed-files>` before every commit. Exit 0 = safe. Exit >0 = fix & re-run.

**Rule derived:** Refactor PRs must pass UBS on all changed files. It's wired into `verify_isomorphism.sh`.
**Used by:** scripts/verify_isomorphism.sh, METHODOLOGY.md Phase F.

---

### K-8 — Beads session protocol
**Source:** `AGENTS.md` §"Beads Workflow Integration" + [br/SKILL.md](../../br/SKILL.md)
**Tag(s):** `process, sibling`
**Verbatim:**
> Before ending any session, run this checklist:
> git status; git add <files>; br sync --flush-only; git add .beads/; git commit; git push; git status (MUST show "up to date")

**Rule derived:** Every refactor pass ends with this sequence. The LEDGER.md is staged with `.beads/`. The push is non-negotiable.
**Used by:** SKILL.md Hand-off, AGENT-COORDINATION.md.

---

### K-9 — Operator card format (from operationalizing-expertise)
**Source:** [operationalizing-expertise/references/OPERATORS.md](../../operationalizing-expertise/references/OPERATORS.md)
**Tag(s):** `sibling, process`
**Verbatim:**
> Every operator must have: symbol, name, definition, ≥3 when-to-use triggers, ≥2 failure modes, prompt module.

**Rule derived:** The skill's operator library (OPERATOR-CARDS.md) follows this exact shape. When adding new operators, comply with the template.
**Used by:** OPERATOR-CARDS.md, all operator definitions.

---

### K-10 — jsm graceful degradation invariant (from documentation-website-for-software-project)
**Source:** [documentation-website-for-software-project/references/SKILL-INSTALLATION.md](../../documentation-website-for-software-project/references/SKILL-INSTALLATION.md) §"The graceful-degradation invariant"
**Tag(s):** `sibling, process`
**Verbatim:**
> **No phase of this skill should require any other skill to run.** Every referenced skill has an inline fallback in this repo. The referenced skills are *accelerants*, not prerequisites.

**Rule derived:** This skill references siblings (cass, ubs, multi-pass-bug-hunting, etc.) but never blocks on their absence. Every scripted sibling call has a fallback.
**Used by:** JSM-BOOTSTRAP.md, scripts/check_skills.sh.

---

## Triangulation map — rule → quote IDs

Each load-bearing rule is supported by ≥2 anchors where possible — one general (sibling or AGENTS.md), one specific (session evidence).

| Rule | Supporting quote IDs |
|------|----------------------|
| Never delete without approval | A-1, S-1 |
| Never codemod / sed | A-2, S-15 (the sanctioned alternative) |
| Never create `_v2` / `_new` filenames | A-3 |
| Resource-lifecycle axis must be filled | K-3, S-3 |
| Side-effect axis must be filled | K-3, S-2 |
| Rule of 3 for abstractions | K-1 |
| One lever per commit | K-2, S-4 |
| Normalization is a behavior change | S-6 |
| "Defensive coding is best" is a smell | S-7 |
| `#[ignore]` conformance tests ⇒ isomorphism violation | S-8 |
| Same-file duplicate functions need detection | S-9 |
| Orphan-module-without-registration = dead-adjacent | S-10 |
| Bulk-replace-with-allow_multiple is OK (not a codemod) | S-15, A-2 |
| UBS before commit | K-7 |
| Beads session close with push | K-8 |
| Siblings are accelerants not prerequisites | K-10 |
| Skills are for Claude, dense prose | K-4 |
| cass via --robot/--json only | K-5 |
| bv via --robot-* only | K-6 |
| Treat other-agent edits as your own | A-5 |
| Early-dev = no compat shims | A-4 |
| "Tests pass → done" is the danger signal | S-12, K-3 |
| Operator cards follow the 6-field shape | K-9 |
| Rewrite-from-docstring loses invisible behavior | S-2 |
| Config defaults are observable | S-5 |
| Extract-fn must audit downstream bindings | S-4 |
| User vocabulary = trigger phrases | S-13 |
| Agents copy-pattern from themselves | S-14 |

If any rule lacks anchors, promote an instance of it to a new quote or remove the rule.

---

## How to add a new quote

1. When a future refactor pass discovers a new pathology, horror story, or successful collapse, extract a **verbatim snippet** from the session.
2. Assign a new ID: `S-<n+1>` for session, `K-<n+1>` for sibling, `A-<n+1>` for AGENTS.md.
3. Fill the full entry in this file.
4. Add a row to the triangulation map.
5. In the skill file that cites it, use: *"see quote S-<n> in CORPUS.md"*.

**Why this discipline matters:** the alternative is uncitable lore. When a reviewer asks "why does the skill require the isomorphism card's side-effect axis be non-empty?", the answer is "quote S-2 — the WebSocket auto-subscribe lost because a docstring-based rewrite ignored that axis." Without the anchor, the rule is unenforceable.
