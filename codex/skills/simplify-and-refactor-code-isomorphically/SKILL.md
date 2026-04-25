---
name: simplify-and-refactor-code-isomorphically
description: >-
  Shrink and unify code without changing behavior. Use when: simplify, refactor, reduce
  duplication, remove lines, extract helper, reuse component, DRY, collapse, better abstraction.
---

# Simplify and Refactor Code Isomorphically

> **The One Rule:** Prove behavior identical, then remove lines. No proof → no delete. The goal is net-negative LOC with a test suite still green and a golden-output diff still empty.

## Table of Contents

One Rule · The Loop · Pre-Flight · Phase 0 (jsm bootstrap) · Vibe-Coded Pathology Triggers · Duplication Taxonomy · Opportunity Matrix · Isomorphism Proof · Pattern Tiers · Language Cheatsheet · Metrics Dashboard · Agent Coordination · Anti-Patterns · Checklist · Hand-off · [Reference Index](#reference-index)

> In a hurry? Open [references/QUICK-REFERENCE.md](references/QUICK-REFERENCE.md) — one-screen card with the rule, loop, score formula, clone taxonomy, and every commit gate. Then return here for depth.
>
> New to this skill? Skim [references/GLOSSARY.md](references/GLOSSARY.md) first, then [references/FAQ.md](references/FAQ.md). Version: see [CHANGELOG.md](CHANGELOG.md).

This skill is the mirror image of [extreme-software-optimization](../extreme-software-optimization/SKILL.md): same discipline, different axis. Optimization trades structure for speed; simplification trades nothing — it just removes accidental complexity while behavior stays bit-identical. It consumes the same kind of baseline artifacts (golden outputs, test suites, invariants) and emits a **LOC ledger**, a **duplication map**, and a series of small isomorphic commits.

## The Loop (mandatory)

```
0. BOOTSTRAP   → check installed sibling skills; offer jsm install for the missing ones; subscription-gated
1. BASELINE    → test suite green, golden outputs captured, LOC snapshot, typecheck clean
2. MAP         → duplication scan (jscpd/similarity-ts/scc/rg/ast-grep) + callsite census + AI-slop scan
3. MATRIX      → score each candidate: (LOC_saved × Confidence) / Risk ≥ 2.0
4. PROVE       → Isomorphism card per change BEFORE editing (not after); property tests for unknown rows
5. COLLAPSE    → one lever per commit; Edit only, no file rewrites; no script-based codemods
6. VERIFY      → tests green · goldens bit-identical · typecheck clean · LOC delta recorded · lints not grown
7. LEDGER      → metrics dashboard · rejection log · per-candidate row
8. REPEAT      → re-scan (new duplicates surface once noise clears)
```

Each phase emits an artifact under `refactor/artifacts/<run-id>/`. No artifact → phase isn't done. The artifacts are the handoff to reviewers; without them a "this is cleaner" PR is indistinguishable from a drive-by rewrite.

---

## Pre-Flight Checklist

Run through this **before** touching any file. The most common way a simplification PR destroys value is skipping one of these.

- [ ] **Tests baseline is green** — `cargo test` / `pnpm test` / `pytest` / `go test ./...` clean on the commit you're starting from. If tests are red, the refactor will be blamed for breakage that already existed. Fix or quarantine first.
- [ ] **Golden outputs captured** — run the program against a representative input set and `sha256sum` the outputs. See [ISOMORPHISM.md](references/ISOMORPHISM.md).
- [ ] **LOC snapshot** — `tokei` / `scc` / `cloc` before. You must be able to cite "before → after" per path.
- [ ] **Typecheck / lints baseline** — `tsc --noEmit`, `cargo clippy -- -D warnings`, `mypy`, `go vet`. Count warnings. The delta after must not grow.
- [ ] **Duplication scan run** — `jscpd`, `similarity-ts`, `scc --dup`, or `ast-grep` structural patterns. Map is an artifact, not a memory.
- [ ] **One lever per commit** — pick exactly one pattern (e.g. "collapse three send_* functions into one enum-dispatched fn"). Don't stack unrelated cleanups.
- [ ] **No file proliferation, no rewrites** — per AGENTS.md, revise in place. Never `v2`/`_new`/`_improved`. Never use a script to rewrite many files — make the edits manually or via parallel subagents, not regex.
- [ ] **No file deletion without permission** — per AGENTS.md Rule Number 1. A helper that becomes empty gets asked about before it goes away.

If any box is empty, stop and resolve it first. A simplification PR under a broken precondition is worse than no PR — it poisons trust in the whole technique.

---

## Phase 0 — bootstrap sibling skills (jsm)

This skill composes many siblings. Before Phase A, check which are installed; offer to `jsm install` the missing ones. Every referenced skill has an inline fallback — none are prerequisites. Details: [JSM-BOOTSTRAP.md](references/JSM-BOOTSTRAP.md).

```bash
# 1. Detect state
./scripts/check_skills.sh refactor/artifacts/<run-id>
# writes skill_inventory.json; prints a table

# 2. If jsm missing and user wants premium skills:
./scripts/install_jsm.sh      # curl-to-bash, user-consent-gated

# 3. Auth (user-gated; opens browser OAuth or API key)
jsm login

# 4. Install missing siblings (idempotent; graceful on subscription errors)
./scripts/install_missing_skills.sh refactor/artifacts/<run-id>
```

### Sibling siblings used

- `cass` — mine prior refactor precedent
- `ubs` — surface bug-smells while mapping
- `multi-pass-bug-hunting` — depth bug-hunt after a major pass
- `testing-golden-artifacts` / `testing-metamorphic` / `testing-fuzzing` — property & golden patterns
- `multi-model-triangulation` — second opinion on Risk/Confidence
- `ntm` + `agent-mail` + `br` + `bv` + `vibing-with-ntm` — multi-agent swarm
- `codebase-archaeology` — model unfamiliar code first
- `mock-code-finder` — find orphan stubs/mocks
- `cc-hooks` — block `sed`/codemod via PreToolUse hooks
- `extreme-software-optimization` + `profiling-software-performance` — when refactor reveals perf regressions

**Do not block on missing siblings.** Scripts exit 0, log, proceed with inline fallbacks. Full matrix in [JSM-BOOTSTRAP.md §Sibling-skill matrix](references/JSM-BOOTSTRAP.md#sibling-skill-matrix).

---

## Quick Triggers

| User says | First move |
|-----------|------------|
| "remove duplication" / "DRY it up" | Run the duplication scan first; don't eyeball. Many "duplicates" have divergent invariants. |
| "simplify the data types" | Callsite census of every field / variant actually touched; kill what isn't read. |
| "reuse this component" | Extract props schema from all callers; merge by `variant` discriminant, not by inheritance. |
| "remove lines" / "reduce LOC" | Score by Δ LOC × Confidence / Risk; stop at Score < 2.0. Don't chase the last 5%. |
| "create helper functions" | **Rule of 3** — two callsites means note it, three means extract. Two means leave it. |
| "better abstraction" | Resist until you have three concrete cases. One abstraction fits one shape; two fits coincidence; three fits reality. |
| "this file is too long" | Length is a symptom, not a bug. Measure cyclomatic complexity and coupling before splitting. |
| "unify these two implementations" | First prove they have the same contract — invariants match, error semantics match, ordering matches. Otherwise leave both. |

---

## Vibe-Coded Pathology Triggers (AI-generated code smells)

Projects grown via Claude Code / Codex / Cursor / Gemini sessions accumulate a characteristic set of refactor surfaces. These are NOT classic legacy spaghetti — they're the artifacts of plausible autocomplete at scale. Catalogued fully in [VIBE-CODED-PATHOLOGIES.md](references/VIBE-CODED-PATHOLOGIES.md); 40 named patterns total (P1-P40). Most common:

| Pathology | Smell | Detection |
|-----------|-------|-----------|
| P1 over-defensive try/catch | 3+ nested try blocks per 10 LOC, swallowed exceptions | `rg 'except Exception' -t py -c` |
| P2 nullish chain sprawl | `a?.b?.c?.d?.() ?? e ?? f ?? 'default'` | `rg '\?\..*\?\..*\?\.' -t ts` |
| P3 orphan `_v2` / `_new` / `_improved` files | two similarly-named files; one is live, others drifted | `rg --files \| rg -i '_v[0-9]\|_new\|_old\|_improved\|_copy'` |
| P4 `utils.ts` / `helpers.py` dumping ground | 1000+ LOC "common" module imported everywhere | long files + high fan-in |
| P5 `BaseXxxManager<T>` hierarchy | abstract class, 60–90% overrides in concrete classes | `rg 'extends (Base\|Abstract)'` |
| P6 dead feature flags | `if FEATURE_X_ENABLED` that's been `true` in prod for 12+ months | audit config + telemetry |
| P7 re-export webs | 4+ levels of `export * from './index'` | `rg '^export \* from' -t ts -c` |
| P8 pass-through wrappers | `fn a() { b() }; fn b() { c() }` hops with no real body | ast-grep structural match |
| P9 parameter-sprawl helpers | 8+ optional params, 200 lines of flag-conditionals | eyeball long signatures |
| P10 swallowed Promise rejections | `catch { return null }` | `rg 'catch\s*\{\s*return null'` |
| P11 comment-driven programming | `# Step 1: ...; # Step 2: ...; ...` literal task comments | `rg '^\s*(#\|//) (Step\|Phase)'` |
| P12 dead imports | `import { useMemoized }` (doesn't exist); unused imports | `knip`, `ts-unused-exports`, linter |
| P13 stale type exports | interface declares fields never used; or used-fields not declared | type vs runtime audit |
| P14 dead mocks | `__mocks__/api.ts` from prototyping; real API has shipped | mock-code-finder skill |
| P15 `any` that compounds | one boundary `any` → every downstream variable is `any` | `rg ':\s*any\b\|as any'` |
| P19 N+1 from autocomplete | `for x in xs: await fetch(x.id)` | `rg 'for .* await'` |
| P17 prop drilling for singletons | user/theme/locale drilled 5 levels deep | manual scan |
| P18 "everything hook" swamp | `useEverything()` returning 30 fields | fat hook scan |

**Run `./scripts/ai_slop_detector.sh` before Phase B — it emits `slop_scan.md` with all these.** Full detection recipes + collapse recipes + per-pathology isomorphism pitfalls in [VIBE-CODED-PATHOLOGIES.md](references/VIBE-CODED-PATHOLOGIES.md). A recommended attack order (cheap wins first) is given there as "The AI-slop refactor playbook."

**Why these emerge:** session amnesia + prompt-level goals + autocomplete momentum + addition bias. This skill is the direct antidote. See [VIBE-CODED-PATHOLOGIES.md §Why these emerge specifically from AI workflows](references/VIBE-CODED-PATHOLOGIES.md#why-these-emerge-specifically-from-ai-workflows).

---

## Duplication Taxonomy (know what you're merging)

Not all duplication is equal. Merging the wrong kind introduces bugs *and* costs lines.

| Type | Name | Description | Merge? |
|------|------|-------------|--------|
| I | **Exact clone** | Byte-identical spans (often copy-paste) | Yes — extract function |
| II | **Parametric clone** | Same shape, different literals/identifiers | Yes — parameterize |
| III | **Gapped clone** | Same shape, small additions/removals | Maybe — use enum/strategy dispatch, only if variance is bounded |
| IV | **Semantic clone** | Different code, same behavior | **Stop** — different code often encodes different invariants. Prove equivalence before merging. |
| V | **Accidental rhyme** | Looks similar, evolves independently | **Don't merge** — you'd couple two unrelated lifecycles |

**The hardest bugs from "DRY"** come from merging Type IV or V. The second-hardest come from merging Type III too eagerly — the shared function accumulates parameters until it's less readable than the originals.

Full examples and decision tree: [DUPLICATION-TAXONOMY.md](references/DUPLICATION-TAXONOMY.md).

---

## Opportunity Matrix

```
Score = (LOC_saved × Confidence) / Risk

LOC_saved  (1-5): 5 = ≥200 lines, 4 = 50-200, 3 = 20-50, 2 = 5-20, 1 = <5
Confidence (1-5): 5 = duplication scanner + golden diff confirms equivalent
                  3 = looks the same, scanner agrees, but only one callsite tested
                  1 = "these feel similar"
Risk       (1-5): 5 = crosses async/ordering/error-semantics boundary
                  3 = crosses module boundary, shared state
                  1 = single file, single function, pure
```

**Only implement Score ≥ 2.0.** Below that you're likely paying a coupling cost greater than the LOC savings.

| Candidate | LOC | Conf | Risk | Score | Decision |
|-----------|-----|------|------|-------|----------|
| 3× near-identical `send_*` → `send(kind, ...)` | 4 | 5 | 2 | 10.0 | ✅ |
| Merge `<PrimaryButton>` + `<SecondaryButton>` → `<Button variant>` | 3 | 4 | 1 | 12.0 | ✅ |
| Unify `OrderV1` and `OrderV2` types | 4 | 2 | 5 | 1.6 | ❌ (different invariants) |
| Collapse two `parse_*` functions used by one CLI flag each | 2 | 4 | 1 | 8.0 | ✅ |

Full worked example: [METHODOLOGY.md §Phase C — Score the candidates](references/METHODOLOGY.md#phase-c--score-the-candidates).

---

## Isomorphism Proof (per change, written BEFORE the edit)

Every simplification commit must carry this card in its body, filled in before the diff:

```markdown
## Change: [one-line description]

### Equivalence contract
- **Inputs covered:**      [which callers / test cases]
- **Ordering preserved:**  [yes/no + why — e.g. iteration order deterministic since inputs are Vec]
- **Tie-breaking:**        [unchanged / N/A]
- **Error semantics:**     [same Error variants, same thrown types, same panic conditions]
- **Laziness:**            [unchanged / forced — e.g. was Iterator, now materialized to Vec]
- **Short-circuit eval:**  [unchanged — booleans still short-circuit in same order]
- **Floating-point:**      [bit-identical / N/A]
- **RNG / hash order:**    [unchanged / N/A]
- **Observable side-effects:** [logs, metrics, span names, DB writes — identical order + payload]
- **Type narrowing:**      [TS/Rust — discriminant checks still narrow in the same places]
- **Rerender behavior:**   [React — same memo keys, same hook order, same Suspense boundary]

### Verification
- [ ] `sha256sum -c refactor/artifacts/<run>/golden.sha256`  ✓
- [ ] `<test command>`  ✓
- [ ] `./scripts/loc_delta.sh <base> HEAD <path>` shows source-line delta as scored
- [ ] Typecheck / lints: zero new warnings (`tsc --noEmit` / `cargo clippy -- -D warnings`)
```

If you can't fill every row, you don't understand the change well enough to make it safely. Full axis guide: [ISOMORPHISM.md](references/ISOMORPHISM.md).

---

## Pattern Tiers (Quick Reference)

### Tier 1: Mechanical (low risk, high LOC yield)

| Pattern | Shape | Typical Δ LOC | Isomorphism note |
|---------|-------|---------------|------------------|
| **Extract constant** | Magic number/string at ≥3 sites | small | Zero behavior change |
| **Extract function (Rule of 3)** | 3+ near-identical spans | 10–50 | Verify all callers still build |
| **Parameterize (Type II clone)** | Same shape, different literals | 15–80 | Confirm each literal still reachable |
| **Enum dispatch** | `send_foo` / `send_bar` / `send_baz` | 40–150 | One arm per original fn; exhaustiveness checked |
| **Collapse wrapper** | `fn foo(x) { bar(x) }` called once | 5–10 | Inline; kill the hop |
| **Replace conditional with polymorphism / match** | Long if-else chain on type tag | 20–60 | Total match guarantees parity |
| **Remove dead branches** | Flag permanently off / feature shipped | varies | Grep for the flag first |
| **Collapse type alias chain** | `A = B`, `B = C`, `C = concrete` | small | Pure rename, no runtime change |

### Tier 2: Structural (medium risk, high payoff)

| Pattern | Shape | Typical Δ LOC | Isomorphism note |
|---------|-------|---------------|------------------|
| **Unify data model** | `UserDTO` + `UserRow` + `UserAPI` | 50–300 | Only merge if every field means the same thing — check nullability + units |
| **Hoist to higher-order fn** | Same control flow wrapping different bodies | 40–120 | Callbacks must not rely on captured scope from outer fn |
| **Component variants** | `PrimaryButton`, `SecondaryButton`, `DangerButton` | 30–200 | Extract `variant` prop; one style map |
| **Custom hook** (React) | Same `useEffect` + `useState` pair in ≥3 components | 20–80 | Confirm dep arrays stay the same |
| **Generic function** | 4× same logic for `i32`, `i64`, `u32`, `u64` | 30–100 | Trait bounds must encode the actual ops used |
| **Remove boilerplate via derive / macro** | Hand-rolled `PartialEq`/`Display`/`Serialize` | 10–40 | Derived impl must match the hand-rolled semantics exactly |
| **Middleware / decorator extraction** | Logging/retry/tracing at every handler | 30–100 | Order of middleware composition matters |

### Tier 3: Architectural (high risk; require a plan doc)

| Pattern | When | Where it bites |
|---------|------|----------------|
| **Collapse two services into one module** | Services share 80%+ of logic, same deploy | DB migrations, routing, observability |
| **Replace inheritance with composition** | Deep hierarchy with diamond / mixin | Implicit `super()` ordering, LSP violations |
| **Replace ORM with typed query builder** | Reams of scaffolded boilerplate | Query plan changes silently |
| **Monorepo consolidation** | 3+ packages re-publishing same utils | Build graph, CI caching, breaking release cadence |

Full catalog with code: [TECHNIQUES.md](references/TECHNIQUES.md).

---

## Abstraction Ladder (don't climb too fast)

```
Rung 0: Copy-paste            ← two callsites. Leave it.
Rung 1: Extract function      ← three callsites, same shape.
Rung 2: Parameterize          ← three callsites, one axis of variance.
Rung 3: Enum/strategy         ← two+ axes of variance, bounded set.
Rung 4: Trait / interface     ← open set of implementors.
Rung 5: Generic + trait bound ← type-parametric, used across crates.
Rung 6: DSL / macro           ← you've done this exact refactor ≥3 times.
```

**Never skip rungs.** Jumping from rung 0 to rung 4 produces the `AbstractFactoryBeanFactory` nightmare. Rules:

- **Rule of 3** — don't abstract until the third case. One is a unique. Two is a coincidence. Three is a pattern.
- **One axis of variance per rung** — if a shared function takes `kind: Enum, mode: Enum, mode2: Enum, flags: u32`, you climbed too fast.
- **The cost of the abstraction is the sum of the variance it carries** — when variance exceeds shape, the abstraction is worse than the duplication.

Full discussion, with failure case studies: [ABSTRACTION-LADDER.md](references/ABSTRACTION-LADDER.md).

---

## Language Cheatsheet

| Lang | Duplication scan | Common shrink | Grep for sloppiness |
|------|------------------|---------------|---------------------|
| Rust | `similarity-rs` · `tokei` · `ast-grep -l Rust -p 'fn $N($$$A) { $$$B }'` | enum dispatch, `From`/`TryFrom`, generics over 2+ identical fns, derive macros, `?` for match-on-Result ladders | `rg 'match .* Err\(e\) => Err\(e\)' -t rust` (reinvented `?`); `rg 'impl.*for.*\{' -A20 -t rust` (hand-rolled boilerplate) |
| TypeScript/React | `jscpd --min-lines 5` · `similarity-ts` · `ts-morph` refactors | discriminated unions, component `variant` prop, custom hooks, `satisfies`, narrow generic helpers instead of `any` | `rg 'as any\|as unknown as' -t ts`; `rg 'const.*= \(.*\) =>.*useState' -t tsx` (hook dupes) |
| Python | `pylint --disable=all --enable=duplicate-code` · `radon cc` · `vulture` | `@dataclass`, `TypedDict`, `functools.singledispatch`, list/dict/set comprehensions, context managers | `rg 'try:\s*\n\s*.*\s*\n\s*except .*:\s*\n\s*pass' -U -t py` (swallowed exceptions copied) |
| Go | `dupl -threshold 50` · `staticcheck -checks U1000` | generics (1.18+), interface embedding, table-driven tests, `errors.Join` | `rg 'func.*Err\(\) error' -t go` (near-identical error types) |
| C++ | `clang-tidy --checks='modernize-*,readability-*'` · `simian` | CRTP for static polymorphism, `std::variant` over class hierarchy, templates, concepts (C++20), `auto` return | `rg 'typedef .* \*.*_t' -t cpp` (C-style, replace with using); `rg '#define' --type cpp` (macro sprawl) |

Full language guides, including false-positive patterns per tool: [LANGUAGE-GUIDES.md](references/LANGUAGE-GUIDES.md).

---

## Metrics You Report (not optional)

```
LOC:          net delta per-file and per-directory, via tokei/scc
duplication:  clone count + total cloned LOC, via jscpd / similarity-*
complexity:   cyclomatic (radon/gocyclo/lizard) — per-function, before/after
coupling:     imports-in + imports-out per module, before/after
test suite:   pass count before = pass count after (NOT just "green")
typecheck:    warning count before ≥ warning count after
bundle:       (frontend) gzipped JS bytes before/after — a refactor that grows the bundle is suspect
```

**Variance envelope:** if tests are flaky, lock a seed and re-run 5×. A refactor that's passing 4/5 vs. 3/5 was already broken before you touched it.

Ledger template: [ARTIFACTS.md](references/ARTIFACTS.md). Full dashboard template (post-pass reviewer summary): [METRICS-DASHBOARD.md](references/METRICS-DASHBOARD.md).

---

## Metrics Dashboard (the post-pass report)

After the loop terminates, emit `DASHBOARD.md` — the single artifact reviewers and the user consume to know the pass succeeded. Full template and computation recipes: [METRICS-DASHBOARD.md](references/METRICS-DASHBOARD.md).

```markdown
## Summary
| Metric              | Before | After | Δ       | Direction |
|---------------------|--------|-------|---------|-----------|
| LOC                 | 28,413 | 28,062| **−351**| ↓ ✅      |
| Duplication index   | 6.2%   | 3.8%  | −2.4 pp | ↓ ✅      |
| Cyclomatic mean     | 4.2    | 3.9   | −0.3    | ↓ ✅      |
| Test pass count     | 342    | 342   | 0       | = ✅      |
| Typecheck warnings  | 0      | 0     | 0       | = ✅      |
| Bundle (gz)         | 142 KB | 138 KB| −4 KB   | ↓ ✅      |
| Property tests      | 14     | 22    | +8      | ↑ (bonus) |
| Goldens identical   | —      | ✓     | —       | ✅        |
```

**The goal:** most metrics improve, others stay flat, none regress.

### Metric tension signals

| Pattern | Meaning |
|---------|---------|
| LOC down, complexity up | you inlined helpers into a conditional. Re-extract. |
| LOC up, duplication down | new abstraction is bigger than the dup it replaces. Audit. |
| LOC down, test count up | added property tests — virtuous ratio. |
| All improved, perf regressed | watch for `.clone()` introduction or collected iterators. Profile. |

---

## Agent Coordination (multi-agent swarm)

For ≥5 independent candidates across distinct directories, running a swarm finishes in ~N minutes what serial does in ~8N. Requires `ntm` + `agent-mail` + `br` (all optional; fall back to solo sequential if missing).

| Element | Role |
|---------|------|
| `br` beads | own "what to do next"; one bead per accepted candidate; deps between beads |
| `agent-mail` | file reservations (`paths=[...], exclusive=true`) prevent collision |
| `ntm` panes | one agent per candidate; each runs the full loop autonomously |
| `bv` | graph-aware triage picks the right order |
| `vibing-with-ntm` | orchestrator loop + stuck-pane recovery |

Full architecture, launch recipe, collision policy, and recovery playbook: [AGENT-COORDINATION.md](references/AGENT-COORDINATION.md).

**Thread-id convention** (AGENTS.md Agent Mail pattern):
- Mail thread_id: `refactor-<bead-id>`
- Commit trailer: `Beads: <bead-id>`
- File-reservation `reason`: `refactor-<bead-id>`

---

## Anti-Patterns (never do these)

| ✗ | Why |
|---|-----|
| Refactor without a baseline test run | "Still green" means nothing if you didn't check before |
| Collapse two functions with different error types into one | Callers now handle a wider error set than they used to |
| Unify two data models by `any \| null` fields | You just moved the branching to every caller |
| Extract helper from two callsites | That's rung 0 → rung 1 with no third data point. Wait. |
| Replace `if` chain with polymorphism at rung 4 | Jumped past parameterize + enum dispatch. Likely over-engineered |
| Use a script / sed / codemod to "fix all 200 call sites" | Forbidden by AGENTS.md — use parallel subagents or manual edits |
| Create `utils.ts` / `helpers.py` dumping ground | Cross-cutting concern is a package, not a junk drawer |
| Rename during refactor | Two levers per commit; reviewers can't tell what changed |
| Introduce a new abstraction while removing duplication | Climbs the ladder on the same commit — bisect-hostile |
| Delete the "obsolete" old file | NEVER — ask first (Rule Number 1 in AGENTS.md). And often the old file still has unique invariants. Run [DEAD-CODE-SAFETY.md](references/DEAD-CODE-SAFETY.md) gauntlet BEFORE even proposing deletion. |
| Claim "this is more readable" without measuring | Readability is a group judgment, not yours alone. Show LOC / complexity / coupling delta |
| Rewrite the whole module "while we're here" | The only legitimate output is an Edit diff — if you find yourself wanting a Write, stop |

---

## Checklist (before any commit)

- [ ] Baseline captured (tests green, goldens hashed, LOC + complexity + typecheck counts)
- [ ] Duplication map exported (jscpd/similarity-* report path cited)
- [ ] Candidate scored ≥ 2.0 on Opportunity Matrix
- [ ] Isomorphism card filled in, every row answered (no blanks)
- [ ] One lever only (no rename + extract + rewrite in same commit)
- [ ] Edits via `Edit` tool only; no `Write` to existing files; no script-based codemod
- [ ] Tests still pass (same count, not just "green")
- [ ] Golden outputs bit-identical (`sha256sum -c`)
- [ ] Typecheck / clippy / lint warnings did not grow
- [ ] LOC ledger updated — before→after delta per path
- [ ] Commit message contains the isomorphism card verbatim
- [ ] Rollback plan: `git revert <sha>` + any stateful side-effect to undo (DB migration, config)

---

## Hand-off

When the ledger shows no Score ≥ 2.0 candidates left, **stop**. Say:

> Simplification pass complete. Net Δ LOC: -X (Y%); duplication index -Z%; complexity mean -W; all goldens identical; tests still green; typecheck warnings unchanged. Next reviewer can re-open the loop by re-running the duplication scan — most remaining clones are Type IV/V and should be left alone.

Further passes happen after real feature work shifts the surface. New duplicates surface once noise clears, but scanning on the same commit twice is theater.

**Sibling skills** (who consumes what):

| Want to … | Use |
|-----------|-----|
| Identify performance hotspots to target | [profiling-software-performance](../profiling-software-performance/SKILL.md) |
| Apply an optimization after measuring | [extreme-software-optimization](../extreme-software-optimization/SKILL.md) |
| Deep audit for latent bugs before/after refactor | [multi-pass-bug-hunting](../multi-pass-bug-hunting/SKILL.md), [ubs](../ubs/SKILL.md) |
| Mine your own prior solutions for a particular shape | [cass](../cass/SKILL.md) + [flywheel](../flywheel/SKILL.md) |
| Port CLI to Rust (spec-first, preserves invariants) | [porting-to-rust](../porting-to-rust/SKILL.md) |
| Review the resulting PR with multiple models | [multi-model-triangulation](../multi-model-triangulation/SKILL.md) |

Full cross-skill map: [CROSS-SKILL.md](references/CROSS-SKILL.md).

---

## Reference Index

### Quick access (start here)
| Need | File |
|------|------|
| **One-screen dense card** — rule, loop, score formula, clone taxonomy, all gates | [QUICK-REFERENCE.md](references/QUICK-REFERENCE.md) |
| **Glossary** — every term used across the skill with one-line definition | [GLOSSARY.md](references/GLOSSARY.md) |
| **FAQ** — 20+ agent-friction Q&As (flaky tests, no goldens, "just delete it", etc.) | [FAQ.md](references/FAQ.md) |
| **Decision trees** — ASCII flowcharts for ambiguous calls (collapse/leave, rescue/main, stage/keep) | [DECISION-TREES.md](references/DECISION-TREES.md) |
| **Visual diagrams** — ASCII loop, score matrix quadrants, defense-in-depth layers | [VISUAL-DIAGRAMS.md](references/VISUAL-DIAGRAMS.md) |
| **Cookbook** — worked before/after examples per lever (9 recipes across 5 languages) | [COOKBOOK.md](references/COOKBOOK.md) |
| **Formulas** — copy-paste templates for ledger rows, commit messages, PR bodies, subagent prompts | [FORMULAS.md](references/FORMULAS.md) |
| **Selection** — when to use THIS skill vs. siblings (simplify / optimization / archaeology / etc.) | [SELECTION.md](references/SELECTION.md) |
| **Testing** — how to PROVE a refactor is isomorphic (unit / golden / property / replay) | [TESTING.md](references/TESTING.md) |
| **Validation** — runnable self-checks for this skill package | [VALIDATION.md](references/VALIDATION.md) |
| **Structure** — folder layout and artifact map | [STRUCTURE.md](references/STRUCTURE.md) |

### Per-phase and situational guides
| Need | File |
|------|------|
| **Exit criteria + time-boxes** — precise "done" gate per phase and per pass | [EXIT-CRITERIA.md](references/EXIT-CRITERIA.md) |
| **Benchmarks** — what a good pass looks like (LOC deltas, ship/reject ratios, timings) | [BENCHMARKS.md](references/BENCHMARKS.md) |
| **Cold-start** — applying this skill to a project with no baseline | [COLD-START.md](references/COLD-START.md) |
| **Rollback playbook** — what to do when a shipped collapse breaks prod | [ROLLBACK-PLAYBOOK.md](references/ROLLBACK-PLAYBOOK.md) |
| **Reviewer quickstart** — 10-min audit of a skill-produced PR | [REVIEWER-QUICKSTART.md](references/REVIEWER-QUICKSTART.md) |
| **Team adoption** — L0 → L3 maturity ladder for rolling out the discipline | [TEAM-ADOPTION.md](references/TEAM-ADOPTION.md) |

### Guardrail integration (defense-in-depth)
| Need | File |
|------|------|
| **cc-hooks** — Claude Code hooks (PreToolUse / PostToolUse / Stop) | [HOOKS.md](references/HOOKS.md) |
| **git hooks** — native pre-commit / commit-msg / pre-push | [GIT-HOOKS.md](references/GIT-HOOKS.md) |
| **CI/CD integration** — GitHub Actions / GitLab / CircleCI full workflows | [CI-CD-INTEGRATION.md](references/CI-CD-INTEGRATION.md) |
| **Skill self-validation** — frontmatter, links, kernel, corpus, operator cards, script syntax | [VALIDATION.md](references/VALIDATION.md) |

### Core methodology
| Need | File |
|------|------|
| Phase-by-phase method (BASELINE → HAND-OFF) with worked examples | [METHODOLOGY.md](references/METHODOLOGY.md) |
| Full pattern catalog (Tier 1/2/3) with code in Rust/TS/Python/Go/C++ | [TECHNIQUES.md](references/TECHNIQUES.md) |
| 80+ named micropatterns with exact before/after | [MICROPATTERNS.md](references/MICROPATTERNS.md) |
| Rust / TS / Python / Go / C++ specifics + tool invocations | [LANGUAGE-GUIDES.md](references/LANGUAGE-GUIDES.md) |
| Clone types, decision tree, false-positive gallery | [DUPLICATION-TAXONOMY.md](references/DUPLICATION-TAXONOMY.md) |
| Abstraction ladder, Rule of 3, over-abstraction autopsies | [ABSTRACTION-LADDER.md](references/ABSTRACTION-LADDER.md) |
| Full isomorphism axis guide — ordering, errors, laziness, FP, FFI, async, React | [ISOMORPHISM.md](references/ISOMORPHISM.md) |

### Vibe-coded / AI-generated code
| Need | File |
|------|------|
| 40 canonical AI-generated pathologies (P1-P40) + detection + collapse recipes | [VIBE-CODED-PATHOLOGIES.md](references/VIBE-CODED-PATHOLOGIES.md) |
| **Dead-code safety gauntlet** — the 12-step check to prevent the "deleted as dead code" horror story | [DEAD-CODE-SAFETY.md](references/DEAD-CODE-SAFETY.md) |
| Rescue missions for already-broken vibe-coded codebases (stabilize before refactoring) | [RESCUE-MISSIONS.md](references/RESCUE-MISSIONS.md) |
| Continuous-refactor cadence (hooks / CI gates / weekly / monthly) | [CONTINUOUS-REFACTOR.md](references/CONTINUOUS-REFACTOR.md) |
| Property-based tests as the refactor safety net | [PROPERTY-TESTS.md](references/PROPERTY-TESTS.md) |
| **Citations from real indexed agent sessions** — pathology evidence + horror stories + user vocabulary | [REAL-SESSION-EVIDENCE.md](references/REAL-SESSION-EVIDENCE.md) |
| **Quote bank** — every rule anchored to a specific verbatim source | [CORPUS.md](references/CORPUS.md) |
| **Triangulated kernel** — the 30 operational rules, marker-delimited for extraction | [TRIANGULATED-KERNEL.md](references/TRIANGULATED-KERNEL.md) |
| **Prompt engineering** — how to write prompts that get the skill's benefits | [PROMPT-ENGINEERING.md](references/PROMPT-ENGINEERING.md) |
| **Anti-patterns II** — swarm / long-session / rescue / cross-skill / orchestrator anti-patterns | [ANTI-PATTERNS-2.md](references/ANTI-PATTERNS-2.md) |
| **Flywheel integration** — feed session observations back into the skill | [FLYWHEEL-INTEGRATION.md](references/FLYWHEEL-INTEGRATION.md) |

### Kickoff prompts (role library)
| Need | File |
|------|------|
| Ready-to-paste session kickoffs for solo / orchestrator / worker / reviewer / rescue / weekly / monthly / audit / post-incident / handoff | [KICKOFF-PROMPTS.md](references/KICKOFF-PROMPTS.md) |

### Language deep-dives (beyond LANGUAGE-GUIDES.md)
| Need | File |
|------|------|
| Rust: borrow checker, lifetimes, trait bounds, Drop impls, unsafe, workspaces | [RUST-DEEP.md](references/RUST-DEEP.md) |
| Python: async split, dataclass/Protocol, decorators, contextvars, metaclasses, mypy strict | [PYTHON-DEEP.md](references/PYTHON-DEEP.md) |
| Go: interface composition, generics, goroutine ownership, channel idioms, context propagation | [GO-DEEP.md](references/GO-DEEP.md) |
| C++: RAII, Rule of 0/3/5, std::variant, concepts, ranges, constexpr, sanitizers | [CPP-DEEP.md](references/CPP-DEEP.md) |
| **Advanced micropatterns (M41-M80)** — second-tier collapses across all languages | [ADVANCED-MICROPATTERNS.md](references/ADVANCED-MICROPATTERNS.md) |

### Cross-cutting concerns
| Need | File |
|------|------|
| **Monorepo** refactors (Turborepo/Nx/pnpm/Cargo-workspace/Bazel) | [MONOREPO.md](references/MONOREPO.md) |
| **Security-aware** refactors (auth, validation, secrets, RLS, CORS) | [SECURITY-AWARE-REFACTOR.md](references/SECURITY-AWARE-REFACTOR.md) |
| **Performance-aware** refactors + hand-off to optimization skill | [PERF-AWARE-REFACTOR.md](references/PERF-AWARE-REFACTOR.md) |

### Domain-specific deep dives
| Need | File |
|------|------|
| React-specific isomorphism axes, hook extraction, Suspense, RSC | [REACT-DEEP.md](references/REACT-DEEP.md) |
| DB schema + query + migration refactors | [DB-SCHEMAS.md](references/DB-SCHEMAS.md) |
| Type-system shrinks (generics, unions, branded types, phantom types) | [TYPE-SHRINKS.md](references/TYPE-SHRINKS.md) |

### Orchestration
| Need | File |
|------|------|
| Install jsm + sibling skills; graceful degradation | [JSM-BOOTSTRAP.md](references/JSM-BOOTSTRAP.md) |
| Multi-agent swarm via NTM + agent-mail + beads | [AGENT-COORDINATION.md](references/AGENT-COORDINATION.md) |
| The seven metrics; dashboard template; CI integration | [METRICS-DASHBOARD.md](references/METRICS-DASHBOARD.md) |

### Operators, prompts, and artifacts
| Need | File |
|------|------|
| Operator algebra (⊘ Split, ⊞ Merge, 𝓡 Parameterize, 🛡 Isomorphism, …) | [OPERATOR-CARDS.md](references/OPERATOR-CARDS.md) |
| Copy-paste prompts for each operator + end-to-end runs | [PROMPTS.md](references/PROMPTS.md) |
| LOC ledger, duplication map, isomorphism card templates | [ARTIFACTS.md](references/ARTIFACTS.md) |
| Real agent session case studies (Rust / React / Python / Go) | [CASE-STUDIES.md](references/CASE-STUDIES.md) |
| Anti-patterns expanded with failure autopsies | [ANTI-PATTERNS.md](references/ANTI-PATTERNS.md) |
| How to compose with other skills + agent mail + beads | [CROSS-SKILL.md](references/CROSS-SKILL.md) |

### Ready-to-copy templates (`assets/`)
| Need | File |
|------|------|
| Isomorphism card template | [assets/isomorphism_card.md](assets/isomorphism_card.md) |
| Ledger header + scoreboard template | [assets/ledger_header.md](assets/ledger_header.md) |
| Rejection-log entry template | [assets/rejection_log.md](assets/rejection_log.md) |
| Per-pass dashboard skeleton | [assets/dashboard_skeleton.md](assets/dashboard_skeleton.md) |
| PR description body | [assets/pr_description.md](assets/pr_description.md) |
| Beads (br) workflow cheat-commands | [assets/bead_commands.md](assets/bead_commands.md) |

### Role-specialized subagents (`subagents/`)
| Role | File |
|------|------|
| Proposes an Edit-tool plan for a candidate; never executes | [subagents/refactor-extractor.md](subagents/refactor-extractor.md) |
| Audits a refactor diff against its isomorphism card | [subagents/refactor-reviewer.md](subagents/refactor-reviewer.md) |
| Scans the repo and produces a scored duplication_map.md | [subagents/duplication-scanner.md](subagents/duplication-scanner.md) |
| Stress-tests a filled isomorphism card for completeness | [subagents/isomorphism-auditor.md](subagents/isomorphism-auditor.md) |
| Runs the 12-step dead-code safety gauntlet on a target | [subagents/dead-code-checker.md](subagents/dead-code-checker.md) |

### Scripts (zero context cost, run directly)
| Need | File |
|------|------|
| **Bootstrap** — check siblings + jsm state; emit inventory JSON | [scripts/check_skills.sh](scripts/check_skills.sh) |
| **Bootstrap** — run jsm official installer (user-consent-gated) | [scripts/install_jsm.sh](scripts/install_jsm.sh) |
| **Bootstrap** — bulk `jsm install` for missing siblings | [scripts/install_missing_skills.sh](scripts/install_missing_skills.sh) |
| Capture baseline: tests + goldens + LOC + complexity + warnings | [scripts/baseline.sh](scripts/baseline.sh) |
| Run duplication scanners per language and emit unified JSON map | [scripts/dup_scan.sh](scripts/dup_scan.sh) |
| **AI-slop detector** — scan for P1-P40 vibe-code pathologies | [scripts/ai_slop_detector.sh](scripts/ai_slop_detector.sh) |
| Compute source-line delta for a path between two git refs (`--net-only` for CI) | [scripts/loc_delta.sh](scripts/loc_delta.sh) |
| Verify goldens + tests + typecheck + LOC match isomorphism card | [scripts/verify_isomorphism.sh](scripts/verify_isomorphism.sh) |
| Emit the per-commit isomorphism card template | [scripts/isomorphism_card.sh](scripts/isomorphism_card.sh) |
| Rank candidates via Opportunity Matrix from a JSON duplication map | [scripts/score_candidates.py](scripts/score_candidates.py) |
| **Property-test scaffold** — emit language-appropriate skeleton | [scripts/property_test_scaffold.sh](scripts/property_test_scaffold.sh) |
| **Metrics snapshot** — compute the 7 dashboard metrics | [scripts/metrics_snapshot.sh](scripts/metrics_snapshot.sh) |
| **Swarm launcher** — NTM panes + marching orders | [scripts/multi_agent_swarm.sh](scripts/multi_agent_swarm.sh) |
| **Dead-code safety gauntlet** — automated 12-step check | [scripts/dead_code_safety_check.sh](scripts/dead_code_safety_check.sh) |
| **Callsite census** — enumerate every reference to a symbol | [scripts/callsite_census.sh](scripts/callsite_census.sh) |
| **Boundary validator scaffold** — emit zod/pydantic/serde template to eliminate `any` propagation | [scripts/boundary_validator_scaffold.sh](scripts/boundary_validator_scaffold.sh) |
| **Ledger row** — emit a LEDGER.md row from current git state | [scripts/ledger_row.sh](scripts/ledger_row.sh) |
| **Lint ceiling** — enforce warning-count ceiling (R-013) | [scripts/lint_ceiling.sh](scripts/lint_ceiling.sh) |
| **Rescue gate check** — validate rescue-mission exit criterion | [scripts/rescue_phase_check.sh](scripts/rescue_phase_check.sh) |
| **Unpinned deps** — flag floating dependency versions (P37) | [scripts/unpinned_deps.sh](scripts/unpinned_deps.sh) |
| **One-shot session setup** — run check_skills + baseline + dup_scan + slop_detector + metrics | [scripts/session_setup.sh](scripts/session_setup.sh) |
| **Kernel extractor** — print the marker-delimited triangulated kernel | [scripts/extract_kernel.sh](scripts/extract_kernel.sh) |
| **Operator-card validator** — enforce definition/triggers/failures/prompt-module shape | [scripts/validate_operators.py](scripts/validate_operators.py) |
| **Corpus validator** — enforce quote-bank source/tag/verbatim/rule/usage fields | [scripts/validate_corpus.py](scripts/validate_corpus.py) |
| **Skill contract validator** — top-level read-only validation gate | [scripts/validate_skill_contract.py](scripts/validate_skill_contract.py) |

---

## Self-Test

Trigger tests: [SELF-TEST.md](SELF-TEST.md).
