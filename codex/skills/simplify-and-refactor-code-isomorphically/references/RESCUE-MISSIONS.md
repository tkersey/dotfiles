# Rescue Missions — applying the skill to already-broken vibe-coded codebases

> The standard skill loop assumes a healthy baseline (tests green, goldens hashable, typecheck clean). Many real-world vibe-coded projects don't have that. This file is the playbook for getting them *to* a healthy baseline so the rest of the skill can run. It's what to do when the user says "this codebase is a mess, help me fix it."

## Contents

1. [The six symptom classes](#the-six-symptom-classes)
2. [Triage priority](#triage-priority)
3. [Phase −1: stabilize](#phase-1-stabilize)
4. [Phase 0: grow a test net](#phase-0-grow-a-test-net)
5. [Phase 0.5: fix the type system](#phase-05-fix-the-type-system)
6. [When to run the main loop vs. more triage](#when-to-run-the-main-loop-vs-more-triage)
7. [The rescue backlog as beads](#the-rescue-backlog-as-beads)
8. [The non-hostile refactor rule](#the-non-hostile-refactor-rule)

---

## The six symptom classes

A vibe-coded project arrives in some combination of these states:

| Symptom | What it looks like | Rescue entry point |
|---------|---------------------|---------------------|
| **Red tests** | tests fail on `main` | Phase −1a: quarantine or fix |
| **No tests** | there aren't any tests | Phase 0: grow a test net |
| **Broken build** | `tsc --noEmit` / `cargo check` fails | Phase −1b: fix build |
| **Loud lints** | hundreds of clippy / eslint / mypy warnings | Phase −1c: clamp warnings, don't bulk-fix |
| **Panic-prone** | crashes in prod; `unwrap` / `as any` everywhere | Phase 0.5: type-system fixes |
| **Architectural rot** | every feature request spawns 10 new pathologies | Full skill loop after the above |

Often all six. Don't panic. Attack one at a time.

---

## Triage priority

```
Decreasing order of urgency:

  1. Red tests on main           — blocks everyone's work
  2. Broken build                — blocks PRs
  3. Prod panic / crash          — blocks users
  4. Loud lints blocking CI      — blocks PRs indirectly
  5. No tests                    — blocks future safety
  6. Architectural rot           — blocks future velocity
```

**Never start with architectural rot if tests are red.** A refactor on a red baseline produces an undebuggable PR (see [METHODOLOGY.md §Phase A](METHODOLOGY.md#phase-a--baseline)).

---

## Phase −1: stabilize

### Phase −1a: red tests

If tests fail on `main`:

1. **Reproduce locally.** Don't trust CI; run the exact command CI runs.
2. **Bisect if unclear.** `git bisect` with `<command>; [[ $? == 0 ]]` as the script — find the commit that introduced the failure.
3. **Decide: fix vs quarantine.**
   - **Fix** if it's a clear recent regression, one owner, one fix.
   - **Quarantine** if it's multiple-root-cause legacy failures you can't untangle in a few hours. Mark the tests with `#[ignore]` / `.skip()` / `@pytest.mark.skip("rescue-q1")` — with a reason.
4. **Commit the quarantine** separately, with a ledger row listing what was quarantined and why.
5. **File a bead per quarantined test** so they aren't forgotten.

**Anti-pattern:** bulk-adding `#[ignore]` across a swath of tests to "get green." That's the pathology from `beads-rust/2026-01-17T19-35 :: L79-87` ([REAL-SESSION-EVIDENCE.md](REAL-SESSION-EVIDENCE.md#conformance-tests-ignored-to-paper-over-semantic-drift)). Each quarantine gets a specific reason and bead.

### Phase −1b: broken build

If the build itself fails:

1. **Scope the break.** One crate? One workspace? One platform? Narrow with `cargo check -p <crate>` / `tsc --noEmit -p tsconfig.json`.
2. **Ask: is this a fresh clone issue?**
   - In a separate clean checkout or disposable CI job, run the install +
     build from scratch. Do not delete local build/cache directories in the
     shared worktree just to test this hypothesis.
   - If it works clean, the issue is stale state, not code. Add to `.gitignore` if appropriate.
3. **If code-level:** one error at a time. Fix the first, check if downstream errors disappear (they often do — chain reactions).
4. **Cap the pass.** Don't fix the build AND refactor in the same PR.

### Phase −1c: loud lints

Hundreds of clippy / eslint / mypy warnings:

**Wrong move:** bulk-fix all warnings.

**Right move:** snapshot the warning count as the ceiling, never allow it to grow, then chip away in small bead-tracked passes:

```bash
# Snapshot
cargo clippy --all-targets 2>&1 | grep -c '^warning:' > refactor/artifacts/warning_ceiling.txt

# CI gate (as a pre-commit or GitHub Action):
new_count=$(cargo clippy --all-targets 2>&1 | grep -c '^warning:')
ceiling=$(cat refactor/artifacts/warning_ceiling.txt)
if (( new_count > ceiling )); then
  echo "warnings grew: $ceiling → $new_count"
  exit 1
fi
```

Then in the main skill loop, include a "reduce warning count" lever. Each accepted candidate should lower the ceiling by 1+. Never silence with `#[allow]` / `// eslint-disable` — that's pathology, not progress.

---

## Phase 0: grow a test net

If no tests exist, the skill's goldens gate is meaningless. Bootstrap coverage:

### Coverage-shaped priorities

**Don't aim for 80% line coverage.** Aim for:

1. **Golden-path integration tests** — the 3–5 user workflows that make the product work. Tests at the system boundary exercising real code, real DB, real API. See [testing-perfect-e2e-integration-tests-with-logging-and-no-mocks](../../testing-perfect-e2e-integration-tests-with-logging-and-no-mocks/SKILL.md).
2. **Invariant-pinning property tests** — one per critical data transformation. See [PROPERTY-TESTS.md](PROPERTY-TESTS.md).
3. **Characterization tests** — for the top 5 functions by lines-of-code-or-complexity. Write tests that capture *current behavior* (not intended behavior) so future changes have an oracle.

### The characterization test

```python
# Take the biggest scariest function. Write a test that captures what it currently does.
def test_characterize_process_order_happy_path():
    order = make_test_order()  # realistic fixture
    result = process_order(order)
    # Pin the current behavior, whatever it is:
    assert result.status == 'accepted'
    assert result.total == Decimal('42.99')
    assert len(result.line_items) == 3
    # etc.
```

Once you have a characterization test, you can refactor `process_order`. If the test fails, either:
- The characterization was wrong → update the test.
- The refactor broke behavior → revert.

Either way, the test is doing its job. The test-suite delta after a major rescue should be strongly positive.

### Don't write bad tests to hit a number

**Anti-pattern:** tests that only call the function and assert it doesn't throw. These are worse than no tests — they give false confidence and resist every real change.

Example of a bad test:
```python
def test_process_order():
    assert process_order(make_test_order()) is not None   # tautology
```

---

## Phase 0.5: fix the type system

For TS / Python (gradual typing) / Rust projects drowning in `any` / `# type: ignore` / `.unwrap()`:

### TS: draw the `any` line

```bash
# Count current `any` / `as any` sites
rg ':\s*any\b|<any>|\bas any\b' -t ts -t tsx -c | sort -t: -k2 -rn
```

Don't bulk-fix. Pick the **boundary modules** (API handlers, request parsers, webhook receivers) and add zod validators there. One boundary per commit.

Add a CI check that the `any` count doesn't grow:
```bash
count=$(rg ':\s*any\b|<any>|\bas any\b' -t ts -t tsx -c | awk -F: '{s+=$2} END{print s}')
ceil=$(cat refactor/artifacts/any_ceiling.txt)
(( count <= ceil )) || { echo "any count grew"; exit 1; }
```

### Python: dial up mypy strictness gradually

```toml
# mypy.ini or pyproject.toml
[[tool.mypy.overrides]]
module = "myproject.critical.*"
strict = true              # strict for modules you've cleaned

[[tool.mypy.overrides]]
module = "myproject.*"
disallow_untyped_defs = false  # lenient default for the rest
```

Add modules to the strict list as you clean them. The `strict` list monotonically grows.

### Rust: `.unwrap()` inventory

```bash
rg '\.unwrap\(\)' -t rust -n > refactor/artifacts/unwrap_inventory.txt
wc -l refactor/artifacts/unwrap_inventory.txt
```

**Audit the top 20** by file. For each:
- Legitimate "truly unreachable"? Replace with `.expect("<reason>")` and move on.
- Panic path that callers should handle? Return `Result` and propagate.
- In a binary `main`? Replace with `anyhow::Result<()>` + `?` (usually the cleanest rescue).

Cap the total at the current count. Chip away.

---

## When to run the main loop vs. more triage

You're ready to run the main skill loop when:

- [ ] Tests pass on `main` (quarantined tests are fine, as long as they're labeled).
- [ ] Build passes clean.
- [ ] At least one golden-path integration test exercises the area you plan to touch.
- [ ] Warning count and `any` / `unwrap` counts are capped at the current level.
- [ ] Git history shows at least one recent clean build + test run (so you trust the baseline).

If any of those are missing, stay in rescue mode. Running the main loop on an unstable baseline will produce a PR the user cannot review.

---

## The rescue backlog as beads

Every rescue discovers 30+ things that need doing. Instead of trying to fix them all, file beads:

```bash
br create --title "[rescue] Characterization test for process_order" --type task --priority 1 --label rescue
br create --title "[rescue] Add zod validator to POST /api/orders" --type task --priority 1 --label rescue
br create --title "[rescue] Replace .unwrap() in src/payment/mod.rs (14 sites)" --type task --priority 2 --label rescue
br create --title "[rescue] Un-quarantine conformance_stale_issue_detection test" --type task --priority 3 --label rescue
```

Then use [bv](../../bv/SKILL.md) to triage: prioritize by (blast-radius × unblocking-potential) / effort. Work the top few per week.

This keeps the rescue from becoming overwhelming, and it leaves a durable audit trail.

---

## The non-hostile refactor rule

**During a rescue, refactors must be non-hostile.**

Hostile refactor characteristics (DO NOT do these during rescue):

- Renaming widely-imported symbols (breaks every developer's working branch)
- Moving files between directories (hits everyone's open PRs)
- Changing public API shapes that consumers rely on
- Bulk formatter/linter runs that touch every file (makes blame useless)
- Removing logs/metrics that might be in dashboards

Non-hostile characteristics (DO these):

- Additive changes (new files, new exports, new tests)
- Per-file internal-only rewrites (contained blast radius)
- Behind-feature-flag new implementations that don't replace old ones
- Adding property tests alongside existing tests
- Capping warning counts without silencing

The non-hostile rule applies until the rescue is complete and the normal skill loop takes over. After stabilization, "hostile" refactors are allowed because the team has capacity to absorb them.

---

## Rescue mission kickoff prompt

Paste this to the agent starting a rescue:

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
