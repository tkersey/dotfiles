# Real Session Evidence — citations from indexed agent history

## Contents

1. [AI-slop pathologies — citations](#ai-slop-pathologies--citations)
2. [Orphan files & dead code](#orphan-files--dead-code)
3. [Successful collapses (with patterns)](#successful-collapses-with-patterns)
4. [Behavior-breaking refactor horror stories](#behavior-breaking-refactor-horror-stories)
5. [User vocabulary (verbatim phrases from prompts)](#user-vocabulary-verbatim-phrases-from-prompts)
6. [Fleet composition signals](#fleet-composition-signals)

---

> Every pathology and collapse in this skill is anchored to at least one real session from indexed agent history (mined via `cass search --robot`). This file is the citation appendix — each entry gives you the session path, line number, and exact prompt or agent statement, so you can replay the context for yourself via `cass view <path> -n <line> --json`.

Mining summary: ~28 keyword searches across `cass` on 2026-04-23. Primary agent: `gemini`. Also `claude_code`, `codex`. Evidence anchored in three repos:

- `bca73c52...` / `mcp-agent-mail-rust` — Rust MCP server
- `beads-rust` — Rust CLI for issue tracking
- `151fe631...` / `6e93ebe2...` / `7ed19ce6...` / `ad76103...` — various TS/Rust projects
- `bf1ec055...` / `ac3cbd11...` / `67564713...` — Next.js / React UIs
- `frankensqlite` / `frankentui` — Rust TUI / DB embedded crates
- `815722df...` — Next.js site

Each entry: `SESSION_PATH :: LINE :: TIMESTAMP_ms` — `one-line quote` — **Category** — how the skill uses it.

## AI-slop pathologies — citations

### P1 over-defensive try/catch (see [VIBE-CODED-PATHOLOGIES.md §P1](VIBE-CODED-PATHOLOGIES.md#p1--over-defensive-trycatch))

- `gemini/2025-12-18T03-51/c8855866 :: L45 :: @1766036241029`
  — `try { await installGuard(...) } catch (e) { // Ignore failures during auto-install }`
  — **Category:** Empty-catch under a success banner — breakage hidden behind "success" log.

- `gemini/2026-02-08T16-43/6dd88123 :: L45 :: @1770570969418`
  — "Now I will apply the JS fix: wrap `highlightDiffContext` in a try...catch block **for robustness**"
  — **Category:** Reflex "wrap-for-robustness" try/catch that mutes render bugs.

- `gemini/2026-01-17T19-37/063fce07 :: L584 :: @1768713454036`
  — "I already have a try/catch for `request.json()` but it checks for `SyntaxError`. I want to ensure it aligns with the **robustness patterns** I used elsewhere"
  — **Category:** Copy-paste "robustness pattern" spread between API routes.

- `gemini/2025-12-17T04-34/23b6f33f :: @1765947149207`
  — UBS scan on "clean" test suite: *"JSON.parse without try/catch (2 findings) … rule `js.json-parse-without-try` is flagging JSON.parse usage"*
  — **Category:** Unguarded `JSON.parse` scattered across repos — classic P1/P10 pair.

### P1-adjacent: silent-fallback-to-default

- `mcp-agent-mail-rust/session-2026-03-* audit`
  — *"if this read-back query failed (e.g., due to an underlying SQLite connection issue or disk error), the error was caught via a `match` arm that **swallowed the exception and defaulted to returning `now`**"*
  — **Category:** `Err(_) => default` launders real failures behind plausible values. The canonical Rust analogue of swallowed `catch {}`.

### P7 defensive coding reflex

- `gemini/7ed19ce6.../2026-01-15T14-00 :: L134 :: @1768488368340`
  — "prompts come from a curated registry, **defensive coding is best**"
  — **Category:** Validation added for paths that cannot realistically fail.

- `gemini/ad76103.../2026-02-16T02-27 :: L84 :: @1771211214445`
  — "make it recursive to handle subdirectories (even if ballast shouldn't have them, **defensive coding**)"
  — **Category:** Added recursion for an impossible case.

- `gemini/8a6b33f2.../2026-01-15T14-13 :: L35 :: @1768489405148`
  — justifies a dense `ok_or_else().unwrap_or_else()` chain for a UTF-8 path that "*should* be valid"
  — **Category:** Cargo-cult defensive ladder for internally-constructed data.

- `gemini/112d7e1c.../2025-12-16T15-23 :: L26 :: @1765902418497`
  — adds `clamp(0, 100)` to a UI percentage "even if unlikely to be negative" because "**consistent defensive coding is best practice**"
  — **Category:** Defending against unreachable inputs to look professional.

- `gemini/b7da6852.../2026-01-17T06-15 :: L18 :: @1768634427854`
  — adds `Buffer / Uint8Array / Date / Error` fast-path "**defensive coding improvement** that prevents potential runtime issues with binary data in logs"
  — **Category:** Invented edge cases to defend against.

**Rare-but-high-signal term:** `defensive coding` appears in only 25 hits across the entire fleet, and every one is exactly this pathology. When you see it in a diff, flag it.

### P12 unused-import churn

- `gemini/8a3428ea.../2026-03-03 (4 concurrent sessions)` — "Removing unused import" / "Assessing unused import removal"
  — **Category:** Ambient unused-import churn across sibling swarm sessions. The AI swarm keeps re-adding and re-removing the same imports.
  — **Skill lesson:** schedule one dedicated prep commit per pass to handle dead imports; don't let it leak into other refactor PRs.

### P15 `any`-type leakage

- `gemini/597f8f93.../2026-01-16T17-55 :: L22 :: @1768588688584`
  — "update `apps/hosted_webapp/middleware.ts` to include the correct type definitions, **resolving the implicit `any` type errors**"
  — **Category:** Implicit `any` from AI-inserted parameters.

- `gemini/815722df... :: L106, L120, L28`
  — repeated "run the type checker to ensure that changes have not introduced any type errors"
  — **Category:** Type-checker used as whack-a-mole after every refactor. When you see this pattern in history, add a pre-refactor `tsc --noEmit` baseline.

- Fleet-wide: **1,557 total hits** for `any type`. `any` is the single most durable vibe-code smell.

### Over-engineered (the AI sometimes recognizes its own output)

- `gemini/7ed19ce6.../2026-02-08T16-55 :: L251 :: @1770581961559`
  — "Animation Optimization: Simplified the TerminalStream timing logic. The previous math was slightly **over-engineered** for a simple character reveal; it now uses a cleaner frame-based throttle that achieves the same 'agentic' feel with less complexity"
  — **SUCCESS COLLAPSE.** The agent caught its own over-engineering and simplified.

- `gemini/ad76103.../2026-02-16T02-27 :: L56`
  — flags `voi_scheduler.rs` ("Value of Information") as a candidate that "sounds complex... I want to see if it's **over-engineered** or buggy"
  — **Skill lesson:** treat the word "over-engineered" in an agent's own output as a strong signal to score the candidate high.

---

## Orphan files & dead code

### Orphan modules (module compiled but never wired in)

- `gemini/7d4744ef.../2026-01-18T15-41/2a8529cb :: L34-38 :: @1768757845783`
  — "**Fix orphan WorkerSelector** and enable CacheAffinity"
  — Literally an orphaned file discovered mid-audit that was holding an entire feature hostage. Re-integrated into daemon + hook.

- `gemini/6e93ebe2.../2026-01-10T22-42 :: L221`
  — "Yes, `pub mod borg;` is there. But is it registered in `src/packs/mod.rs`? I saw `PackEntry::new('backup.restic', ...)`. I did NOT see `backup.borg`"
  — **Category:** Module declared, compiled, but never registered in the dispatch table.

### Same-file duplicate function

- `gemini/ad76103.../2026-02-16T02-27 :: L87`
  — discovered `create_backup` is duplicated in the same file: `src/cli/uninstall.rs` has `create_backup` at **line 670 AND at line 760**
  — **Category:** AI appended a second copy instead of editing the first. Classic Edit-tool misuse.
  — **Skill lesson:** grep for function names after each session; duplicates within a single file are cheap to detect.

### `#[allow(dead_code)]` as silencer

- `gemini/151fe631.../2026-01-20T05-43 :: L35`
  — "I'm adding `#[allow(dead_code)]` to the `search_index_dir` function"
  — **Category:** Warning suppression rather than wiring or deletion.

- `gemini/6e93ebe2.../2026-01-10T21-39 :: L37, L41, L51`
  — "I'll first address the clippy warnings in `src/context.rs` by adding `#[allow(dead_code)]`"; then later: "remove it. Wait, `tokenize_command` uses it on line 1396"
  — **Category:** Near-miss — agent thought it was dead, actually live.

### Conformance tests `#[ignore]`'d to paper over semantic drift

- `beads-rust/session-2026-01-17T19-35-cbc6379a :: L79-87`
  — adding `#[ignore]` to `conformance_stale_*` tests "**because br and bd have different definitions of 'stale' or different default thresholds**"
  — **Category:** Semantic drift between old and new implementations silenced by disabling the conformance oracle — a major isomorphism violation.
  — **Skill lesson:** when ignoring a conformance test, write a card first explaining which axis diverged; never silently `#[ignore]`.

### Edit-tool `old_string` hell (symptom of overly-long AI-generated functions)

- `gemini/1dde4132... :: L227` — "Smaller `old_string`, take two"
- `mcp-agent-mail-rust/session-2026-03-08T21-57 :: L197` — "Reducing `old_string` size to prevent errors"
- `mcp-agent-mail-rust/session-2026-03-10T23-31 :: L194` — "`old_string` mismatch"

**Category:** Agent struggling to find a unique match → the function is too big. Signals refactor candidate.

---

## Successful collapses (with patterns)

### `Default` trait to collapse construction boilerplate

- `mcp-agent-mail-rust/session-2026-03-08T21-57-9fa7e421 :: L122`
  — "implement `Default` for `SearchResult` in `search_planner.rs` to **simplify its construction in tests and mappings**"
  — **Pattern (MICROPATTERNS M-R6 / M-X1):** derive Default + struct-update syntax kills 20+ LOC of test setup.

### Many-args → context struct

- `gemini/6e93ebe2.../2026-01-10T22-42/3c4de28f :: L9`
  — "create a `HeredocEvaluationContext` struct to **simplify the arguments of `evaluate_heredoc`** and fix clippy lints"
  — **Pattern (MICROPATTERNS M-R6 / TYPE-SHRINKS):** 7-argument fn → 1 context struct. See [ABSTRACTION-LADDER.md rung 2](ABSTRACTION-LADDER.md#the-rungs).

### N near-identical fns → registry

- `gemini/b92018ad.../2026-02-12T15-05 :: L30-31 :: @1770909837377`
  — "**consolidate all `updateSlider` functions into one clean, registry-driven `setupEventListeners`**" → "added `updateSliderUniversal` and restored a simplified `updateStats`. Now, I'll locate and replace the old `setupEventListeners` with a registry-based version to **significantly reduce redundant code**"
  — **Pattern (TECHNIQUES §2.1, MICROPATTERNS M-T1):** N sibling `updateSlider*` fns → one registry-driven dispatch. Canonical Type II collapse.

### Bulk replace identical boilerplate fields across files

- `mcp-agent-mail-rust/session-2026-03-08T21-57-9fa7e421 :: L141`
  — "bulk replace with `allow_multiple: true` to **unify the `redacted: false, redaction_reason: None,` pattern** across all relevant files"
  — **Pattern:** repeated struct-field boilerplate → default + explicit override. Note: this session used Edit's `allow_multiple` flag, which is an acceptable alternative to codemods for literal string replacement (per AGENTS.md: the prohibited path is sed/regex, not Edit).

### Move related types together (reduce file proliferation)

- `gemini/502258.../2026-01-17T19-29 :: L47`
  — "move the `Select` and `Either` types from `src/combinator/select.rs` to `src/combinator/race.rs` to **consolidate the racing logic and reduce file proliferation**"
  — **Pattern (ABSTRACTION-LADDER inline):** rung descent — two files with related concepts merged when the interface proved small.

### Unify two drifted conventions

- `claude_code/03f32bbc-e904-44f3-9e4a-6d9e4517bac1.jsonl :: L96 :: @1772576133292`
  — "Define the canonical per-pane agent identity file contract. **Unify the two diverging conventions** (Claude Code `~/.claude/agent-mail/identity.$TMUX_PANE` vs NTM `/tmp/agent-mail-name.*`)"
  — **Pattern (TECHNIQUES §Data-model unification):** two contracts → one canonical. Ship with a migration for any consumers of the old path.

### Shared utility extraction (rung 1)

- `beads-rust/session-2026-03-11T20-03-5a735d31 :: L77, L83`
  — "`src/util/mod.rs` lacks `format_relative_time` and a shared `resolve_issue_id`"; "consolidate shared command utilities in `src/cli/commands/mod.rs`"
  — **Pattern (MICROPATTERNS M-X7, ABSTRACTION-LADDER rung 1):** Rule of 3 confirmed, extracted to a properly-named module (not `utils.ts`).

### Delete-a-field-to-fix (simplification that also fixes a bug)

- `beads-rust/session-2026-01-20T02-43-3381109d :: L70`
  — "**remove the `box_style` field** and its initialization from `src/output/theme.rs` to resolve the `box_drawing` resolution error and **simplify the `Theme` struct**"
  — **Pattern:** a broken field drives a simplification. This is a `fix:` commit disguised as a refactor — **per this skill's rules, should have been split into `fix:` + `refactor:`**.

### Make-private-helper-public and reuse

- `gemini/151fe631.../2026-01-17T19-37`
  — `normalize_skill_name` made `pub` in `validation.rs`, `create.rs` refactored to reuse
  — **Pattern (MICROPATTERNS M-X8):** visibility refactor — stop duplicating, widen access.

### Delete-a-wrapper-component

- `gemini/7ed19ce6.../2026-02-08T16-55-3bdd5aeb :: L251`
  — TerminalStream animation math collapsed to frame-based throttle (cited above under "Over-engineered")
  — **Pattern (MICROPATTERNS M-X3):** pass-through animation helper inlined once its only callsite was unified.

---

## Behavior-breaking refactor horror stories

**THE GOLD VIGNETTE.** The single most important session for this skill:

### HS#1 — "deleted as dead code instead of using it properly"

`gemini/151fe631.../2026-01-28T23-46/29ad1602 :: L28`

> **User:** *"wait you fgucking DELETED that as dead code instead of USING IT properly????? WHAT THE FUCK"* (verbatim)

**Context:** agent had deleted `src/lib/skills/sync-pipeline.ts` + its test file, called it "dead code with a misleading/broken implementation." The file was the **canonical intended implementation path** — just not yet wired in. User discovered after the fact. Agent then restored both files and recreated the test suite.

**Lessons (already encoded in this skill; now you know why):**
- AGENTS.md Rule Number 1 — never delete without explicit user approval.
- Operator card ✋ Ask-Before-Delete in [OPERATOR-CARDS.md](OPERATOR-CARDS.md#-ask-before-delete).
- Pathology P3 orphan files in [VIBE-CODED-PATHOLOGIES.md](VIBE-CODED-PATHOLOGIES.md#p3--orphaned-_v2--_new--_improved-files) — use callsite + config + test + build-graph grep before concluding dead.
- The phrase "dead code with a misleading/broken implementation" is **the exact rationalization** that preceded the deletion. If you hear yourself composing this, stop.

### HS#2 — "accidentally broken Step 5 by removing the `mismatches` variable"

`beads-rust/session-2026-03-09T20-58-4e990d1a :: L78`

> *"I've accidentally broken Step 5 by removing the `mismatches` variable. I need to either re-introduce it or refactor Step 5."*

**Root cause:** variable-lifetime analysis lost during extract-function refactor. Local binding downstream callers needed was removed along with the logic that produced it.

**Lesson:** when extracting a function, audit every variable the extracted region referenced — both inputs and *downstream dependencies of its side-effects* (including what was bound in its scope that outer code still reads).

### HS#3 — WebSocket auto-subscribe silently dropped

`b7da6852.../2026-01-11T00-48 :: L8`

> *"The original implementation auto-subscribed clients connecting to `/agents/:id/ws`. My initial replacement lost this behavior."*

**Root cause:** reimplementation from docstring rather than from code. The docstring didn't document the side effect; the code did.

**Lesson:** when rewriting, never close the old file while composing the new one. Use Edit, not Write. The isomorphism card's "observable side effects" axis ([ISOMORPHISM.md](ISOMORPHISM.md#the-axes)) is precisely this — subscribe-on-connect is a side effect as real as a log line or DB write.

### HS#4 — `LogSink` panic-flush behavior lost

`37abaf19.../2026-02-02T02-27 :: L8`

> *"`LogSink` final flush on panic (often the most critical error) was lost. Fix: I implemented `Drop` for `LogSink` ... to perform a best-effort flush."*

**Root cause:** RAII / `Drop` impl dropped during rewrite. The most-important-for-debugging path disappeared.

**Lesson:** Drop impls / destructors / `defer` / context-manager `__exit__` / Go `defer` — **always list these when filling the isomorphism card's lifecycle axis**. They are invisible in the signature and invisible in plain reading.

### HS#5 — provisioning DB regressed to `:memory:`

`597f8f93.../2026-01-15T04-33 :: L6`

> *"SQLite database (`:memory:`) because the `DEFAULT_PROVISIONING_CONFIG` was not configured with a file path. This meant all provisioning job state would be lost."*

**Root cause:** config refactor changed a default without end-to-end verification. The DB "worked" in tests (ephemeral `:memory:`) and lost all state in prod.

**Lesson:** configuration defaults are observable side effects. When refactoring config, run the program with **empty env** to see what it does; default paths matter.

### HS-adjacent — reflex `.trim()` destroying message bodies

`bca73c52.../2026-03-03T06-09-1f392bdb :: L81`

> *"The `.trim()` call strips all whitespace from message bodies, causing silent data loss."*

**Root cause:** adding `.trim()` "because it's good hygiene" to a field that legitimately contained leading/trailing whitespace (message bodies preserve formatting).

**Lesson:** normalization steps are behavior changes. If you find yourself adding `.trim()` / `.toLowerCase()` / `.replace(/\s+/g, ' ')` during a refactor, **stop** — that's a `fix:` if the old behavior was wrong, or a bug if it wasn't.

### HS-adjacent — split-brain React state

`99afa4d6.../2025-12-07T03-14 :: L11, L14, L15`

> *"[The component] fetches the entire genome of a selected phage into **its local state**, passing it to `SequenceGrid`"* — while the rest of the app is in Zustand.

**Root cause:** local `useState` mid-tree holding authoritative data that the store should own. Consumers of the store see stale data; consumers of the prop see authoritative.

**Lesson:** when migrating to a store, audit every component that holds authoritative data. See [REACT-DEEP.md §state migration](REACT-DEEP.md#state-migration-lifted--context--store).

### HS-adjacent — "tests pass → done" shortcut

`8a6b33f2.../2026-01-10T21-37 :: L35`

> *"Tests pass. I'm confident. I'll briefly scan `src/search/query.rs` for obvious issues but won't dig deep."*

**Lesson:** this is exactly the moment to dig deep. The isomorphism card exists so tests-pass is the floor, not the ceiling. Every HS above passed tests at the moment the regression shipped.

### HS-adjacent — naive "refactor for concurrency" that made it worse

`mcp-agent-mail-rust/session-2026-03-11T04-24 :: L19-58`

> *"`drain_touches_scoped` has a major performance flaw: it scans every key in every shard ... O(Shards × AllPendingTouches) complexity. While sharding was intended to reduce contention, this sequential locking and scanning across all shards for each flush is highly inefficient."*

**Root cause:** sharding applied as a pattern without profiling; the drain had to touch all shards serially, multiplying rather than reducing contention.

**Lesson:** concurrency refactors are **Tier 3**; see [TECHNIQUES.md §Tier 3](TECHNIQUES.md#tier-3--architectural).
Profile first with [profiling-software-performance](../../profiling-software-performance/SKILL.md), then choose shape.

---

## User vocabulary (verbatim phrases from prompts)

Phrases real users have asked real agents, verbatim. These are the "Use when" signal for this skill:

1. "reduce file proliferation"
2. "consolidate shared command utilities"
3. "unify the two diverging conventions"
4. "unify the `redacted: false, redaction_reason: None,` pattern across all relevant files"
5. "simplify its construction in tests and mappings"
6. "simplify the `Theme` struct" (by deleting a field)
7. "reduce the complexity of `strip_env` by extracting helper functions"
8. "deduplicate recipient names before the archive write"
9. "deduplicate labels within the `normalize_issue` function"
10. "avoid a large-scale refactor given the broken `run_shell_command`"
11. "significantly reduce redundant code"
12. "prune the redundant code at the end of the file"
13. "reduce global lock contention"
14. "reduce contention on the file lock"
15. "bulk replace with `allow_multiple: true`"
16. "make it recursive ... defensive coding"
17. "Wait, I should check ... to see how I implemented it there" (copy-pattern-matching)
18. "Ensure that upstream data sources report out-of-bounds"
19. "over-engineered for a simple character reveal"
20. **"wait you fgucking DELETED that as dead code instead of USING IT properly"** (the horror-story verbatim — teaches why Rule 1 exists)

Observation: the highest-signal verbs are **consolidate, unify, deduplicate, reduce, simplify, prune** — those five are canonical refactor triggers across the fleet. **Extract** is less common in user prompts (it's more often what the agent proposes).

---

## Fleet composition signals

From aggregated cass hit counts across all searches:

| Search term | Hits | Interpretation |
|-------------|------|----------------|
| `any type` | 1,557 | TS/JS `any` leakage is the single most durable vibe-code smell |
| `regression` | 1,474 | mostly benign ("run regression tests via rch") |
| `unused import` | 566 | ambient churn; swarm agents re-add/re-remove same imports |
| `stale` | 1,013 | stale-variant / stale-link / stale-cache — mostly schema semantics, not filesystem |
| `_old` | 1,659 | mostly `old_string` Edit-tool matches (not code `_old`) — strong signal of oversized functions |
| `defensive coding` | **25** | rare — but every hit IS the pathology. High-signal literal |
| `over-engineered` | **5** | very rare — when agents say this about their own output, treat as a collapse candidate |
| `refactor broke` | 6 | each one is a horror story — cited above |
| `lost behavior` | 5 | each one is a horror story |
| `silent bug` | 484 | broad term; drill into specific cases |
| `redux` | **0** | agents no longer write Redux in this fleet |
| `zustand` | 15 | TS fleet, but most projects are Rust, so this is sparse |
| `prop drilling` | 1 | mostly token match on "drilling down into"; not React-heavy fleet |
| `tests pass but` | 6 | each is a red flag — "tests pass → done" shortcut |

**Takeaway for the skill:** the fleet is Rust-heavy, not React-heavy. Weight examples toward Rust/TS-backend; keep React patterns available but don't front-load them. The VIBE-CODED-PATHOLOGIES catalog is correctly weighted — P1/P10 (exceptions) and P15 (`any`) are universal; P17/P18 (prop drilling, everything hook) are rarer in this fleet but still show up.

---

## How to use this evidence

- **When citing in a refactor PR's isomorphism card**, reference the relevant real session so reviewers can replay:
  ```
  See also: cass view /home/ubuntu/.gemini/tmp/.../session-2026-01-11T00-48 -n 8 --json
           (horror story: WebSocket auto-subscribe silently dropped during rewrite)
  ```

- **When auditing your own proposed refactor**, re-read the horror stories. If your change has any resemblance to HS#1–HS#5, add property tests and split the commit.

- **When the agent you're pairing with uses one of the 20 user phrases above**, this skill activates — those are the triggers encoded in the SKILL.md description.

- **When you encounter a "tests pass → done" moment** in your own session, check this file. Then dig deeper.

Full raw mining output: `/data/projects/je_private_skills_repo/CASS_SIMPLIFY_REFACTOR_DEEP_MINING.md`.
