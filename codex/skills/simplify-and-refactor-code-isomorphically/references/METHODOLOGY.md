# Simplification Methodology — phase by phase

> The detailed walk-through. SKILL.md is the cheatsheet; this is the playbook.

## Contents

1. [Phase A — Baseline](#phase-a--baseline)
2. [Phase B — Map](#phase-b--map-the-duplication-and-complexity)
3. [Phase C — Score](#phase-c--score-the-candidates)
4. [Phase D — Prove (isomorphism card)](#phase-d--prove-isomorphism-card)
5. [Phase E — Collapse (one lever)](#phase-e--collapse-one-lever)
6. [Phase F — Verify](#phase-f--verify)
7. [Phase G — Ledger and hand-off](#phase-g--ledger-and-hand-off)
8. [Iteration protocol](#iteration-protocol)
9. [Common failure modes per phase](#common-failure-modes-per-phase)

---

## Phase A — Baseline

You cannot simplify what you can't compare against. The baseline is **non-negotiable** — without it, every "improvement" is unfalsifiable.

### A1. Tests baseline

```bash
# Run the full suite, save the output, count passes/failures
cargo test --no-fail-fast 2>&1 | tee refactor/artifacts/baseline_tests.txt
grep -E '(test result|FAILED|ok\.|panicked)' refactor/artifacts/baseline_tests.txt
```

If anything is red or flaky, **stop**. Fix or quarantine first. A refactor on a red baseline produces an undebuggable PR — every reviewer will assume the failures are yours.

### A2. Golden outputs

For programs with deterministic outputs (CLIs, code generators, data pipelines), capture goldens against a representative input set:

```bash
mkdir -p refactor/artifacts/goldens/inputs refactor/artifacts/goldens/outputs
# stage representative inputs (smallest possible that hit each branch)
for input in refactor/artifacts/goldens/inputs/*; do
  ./target/release/your_bin "$input" > "refactor/artifacts/goldens/outputs/$(basename "$input").out" 2>&1
done
( cd refactor/artifacts/goldens/outputs && sha256sum * ) > refactor/artifacts/goldens/checksums.txt
```

For services, the equivalent is a recorded request/response set:
```bash
# Replay 100 representative requests, hash bodies + status codes
./scripts/record_replay.sh > refactor/artifacts/goldens/replay.json
sha256sum refactor/artifacts/goldens/replay.json > refactor/artifacts/goldens/checksums.txt
```

For UI work, the equivalent is a Playwright/VHS visual snapshot suite. See [TECHNIQUES.md §UI snapshot baseline](TECHNIQUES.md#ui-snapshot-baseline).

### A3. LOC + complexity snapshot

```bash
# Lines of code per file/dir
tokei --output json . > refactor/artifacts/loc_before.json
# Or scc, which also gives complexity
scc --by-file --format json . > refactor/artifacts/scc_before.json
# Per-function cyclomatic complexity:
#   - Python: radon cc -s -a -j .
#   - JS/TS:  npx eslint --rule 'complexity:[error,10]' --format json
#   - Rust:   cargo clippy -- -W clippy::cognitive_complexity (no JSON, parse output)
#   - Go:     gocyclo -avg .
#   - C/C++:  lizard -X . > lizard.xml
```

### A4. Typecheck + lint snapshot

```bash
# Capture warning counts as a HARD baseline — they cannot grow after refactor
cargo clippy --all-targets -- -D warnings 2>&1 | tee refactor/artifacts/clippy_before.txt
tsc --noEmit 2>&1 | tee refactor/artifacts/tsc_before.txt
mypy --strict src/ 2>&1 | tee refactor/artifacts/mypy_before.txt
```

### A5. Document

```markdown
## Baseline (YYYY-MM-DD, commit <SHA>)

| Metric            | Value |
|-------------------|-------|
| Test pass count   | N (M failures, K skipped) |
| Total LOC         | X (per-language breakdown in loc_before.json) |
| Avg cyclomatic    | C |
| Clippy warnings   | W |
| Goldens hashed    | yes — refactor/artifacts/goldens/checksums.txt |
| Bundle size (gz)  | B KB (frontend only) |
```

---

## Phase B — Map the duplication and complexity

The goal: produce a **single duplication map** that lists candidates with location, kind (Type I/II/III), span size, and number of clones.

### B1. Run language-appropriate scanners

```bash
# JS / TS / TSX (all variants, including JSX)
jscpd --min-tokens 50 --min-lines 5 --reporters json --output refactor/artifacts/jscpd src/
# similarity-ts (AST-based, sees Type II clones jscpd misses)
similarity-ts -p 80 src/ > refactor/artifacts/similarity-ts.json

# Rust
similarity-rs -p 80 src/ > refactor/artifacts/similarity-rs.json
# fallback: token-based via scc
scc --by-file --format json . | jq '.[] | select(.Lines > 200)' > refactor/artifacts/scc_long_files.json

# Python
pylint --disable=all --enable=duplicate-code --output-format=json src/ > refactor/artifacts/pylint_dup.json
vulture src/ > refactor/artifacts/vulture.txt   # dead code (often duplicated)

# Go
dupl -threshold 50 -plumbing ./... > refactor/artifacts/dupl.txt

# C/C++
simian -threshold=6 -reportDuplicateText src/**/*.{c,cc,cpp,h,hpp} > refactor/artifacts/simian.txt
```

### B2. AST-grep for structural patterns you suspect

When you have a hypothesis ("I bet there are five `parse_X` functions that look the same"), confirm it with ast-grep:

```bash
# Rust: count fn signatures shaped fn parse_*(...) -> Result<...>
ast-grep run -l Rust -p 'fn parse_$NAME($$$ARGS) -> Result<$T, $E> { $$$BODY }' --json | jq length

# TypeScript: find React components named ___Button
ast-grep run -l TypeScript -p 'export function $NAME$_Button($$$P) { return $$$JSX }' --json
```

### B3. Callsite census

For each candidate, count callsites and inspect signatures:

```bash
rg --type rust 'fn (send_text|send_image|send_file)\b' src/ -n
rg --type tsx '<(PrimaryButton|SecondaryButton|DangerButton)\b' src/ -n
```

Record results in the duplication map:

```markdown
| ID | Kind   | Files / Sites             | Lines | Type | Score | Notes |
|----|--------|---------------------------|-------|------|-------|-------|
| D1 | fn     | messaging.rs:42, :88, :134| 3×40  | II   | 10    | same shape, different `kind` literal |
| D2 | comp   | Btn{Primary,Secondary,Danger}.tsx | 3×60 | II | 12    | extract `<Button variant>` |
| D3 | parse  | csv_parse.rs / tsv_parse.rs | 2×95 | III  | 4     | only 1 axis: separator |
```

---

## Phase C — Score the candidates

Apply the Opportunity Matrix from SKILL.md per row. Reject anything below 2.0. The goal is to prevent over-reach: the long tail of "could be slightly cleaner" rarely justifies its risk.

```python
# scripts/score_candidates.py:
# reads refactor/artifacts/duplication_map.md, emits scored candidates
score = (loc_saved * confidence) / risk
# Conventions:
# loc_saved = sum(clone.lines) - estimated_unified.lines
# confidence: scanner agrees + golden diff would catch + tests cover
# risk:       crosses module/async/error boundary; touches public API
```

Pick the top 3–5 candidates and stop. **Don't try to do everything in one pass.**

---

## Phase D — Prove (isomorphism card)

For each candidate, fill the isomorphism card from SKILL.md **before** editing. The act of filling it is the primary debugger.

If you find yourself writing "N/A" for everything, you didn't think hard enough. At minimum, every change has:
- An ordering axis (if it produces a sequence)
- An error-semantics axis (callers catch some Err set)
- A side-effect axis (logs, metrics, allocations visible to GC)
- A type-narrowing axis (TS/Rust)

If you genuinely can't fill a row, the right answer is to add a property test that pins the behavior down before refactoring. That's better than a "N/A" you regret.

Full axis guide: [ISOMORPHISM.md](ISOMORPHISM.md).

---

## Phase E — Collapse (one lever)

### E1. Branch and edit

```bash
git checkout -b refactor/collapse-send-fns
```

Use the `Edit` tool only. **Per AGENTS.md:**
- Never `Write` over an existing file (no rewrites).
- Never run a script/sed/codemod across files (manual or parallel-subagent edits).
- Never delete a file (ask first).
- No new variant filenames (`v2`, `_new`, `_improved`).

### E2. The one-lever discipline

The commit must contain **exactly one** of:
- An extracted function/component + updated callers
- A merged data type + updated readers/writers
- A removed dead branch + removed flag
- An inlined wrapper + updated callers

It must **not** contain:
- A rename (do that in a separate commit before)
- A formatting pass (do that as a separate prep commit)
- An unrelated bug fix discovered along the way (file a beads issue, separate commit)
- A "while we're here" addition

Reviewers (and `git bisect`) need to attribute later regressions to a single change. Two-lever commits are bisect-hostile.

### E3. Use parallel subagents for many similar callsite updates

When extracting a helper changes ≥10 callsites, don't sed:

```
Spawn 4 parallel subagents:
  agent A: callsites in crates/foo/src/{a,b,c}.rs
  agent B: callsites in crates/foo/src/{d,e,f}.rs
  agent C: callsites in crates/bar/src/{x,y}.rs
  agent D: callsites in tests/
Each agent: apply the same Edit pattern, run rustc on its files, report.
```

Per AGENTS.md, this is the approved alternative to brittle regex transformations.

---

## Phase F — Verify

The verifier runs five gates. **Every** one must pass before commit.

```bash
./scripts/verify_isomorphism.sh
# 1. Test pass count: must equal baseline (NOT just "all green")
# 2. Golden checksums: sha256sum -c must succeed
# 3. Typecheck: warnings must not grow (compare to clippy_before.txt)
# 4. LOC delta: actual delta must match the score within ±10%
# 5. Lint: no new disabled rules, no new ignore comments
```

If any gate fails:
- **Tests fewer than baseline:** you skipped something or introduced a panic. Don't blame "flakiness" — investigate.
- **Goldens differ:** behavior changed. Either prove the diff is intentional and re-baseline (rare; needs user approval) or roll back.
- **More warnings:** likely a missed branch in a `match` or a missing return. Don't `#[allow]` your way out.
- **LOC delta off:** maybe you re-introduced complexity by accident. Check for verbose new helper bodies.
- **New `// eslint-disable` or `#[allow]`:** anti-pattern. Real fix or no-fix.

### F2. Behavior-preserving spot checks

```bash
# Diff stdout/stderr/exit-code on a few representative inputs
for input in refactor/artifacts/goldens/inputs/*; do
  diff <(./old_target "$input") <(./new_target "$input") || echo "BEHAVIOR DIFF: $input"
done
```

### F3. Performance smoke test (optional but cheap)

```bash
hyperfine --warmup 3 --runs 10 './old_target sample.in' './new_target sample.in'
```

A simplification that quietly slows the program by 30% is a regression. If the loop got slower, document why or roll back.

---

## Phase G — Ledger and hand-off

### G1. The ledger

Append to `refactor/artifacts/LEDGER.md`:

```markdown
## D1: collapse 3× send_* into send(kind, ...)
- Commit:    abc1234
- LOC:       crates/mcp-agent-mail-tools/src/messaging.rs  221 → 142  (-79)
- Tests:     342 pass / 0 fail / 5 skip  (= baseline)
- Goldens:   sha256sum -c PASS
- Typecheck: 0 new warnings
- Score:     10.0 (predicted -75 LOC; actual -79; within envelope)
```

### G2. Commit message contract

```
refactor: collapse 3 send_* functions into send(kind, ...)

[isomorphism card here, verbatim]

LOC: messaging.rs 221→142 (-79). Tests 342/0/5 unchanged. Goldens identical.
```

### G3. PR description

Include the full ledger plus the duplication map diff (before/after row counts in `jscpd` etc.). A simplification PR without a ledger reads as a stylistic preference; with a ledger it reads as engineering.

---

## Iteration protocol

After each accepted candidate:
1. **Re-baseline** — tests + goldens + LOC + warnings.
2. **Re-scan duplication** — Type I/II clones often surface once Type II noise is removed.
3. **Re-score remaining candidates** — risks may have changed (some risks compound, others vanish).
4. **Repeat** until no candidate scores ≥ 2.0.

Stop. Don't keep going for the sake of it. The marginal LOC saved trends to zero and the risk trends to one.

---

## Common failure modes per phase

| Phase | Failure | How it shows up | Recovery |
|-------|---------|-----------------|----------|
| Baseline | Skipped golden capture | Behavior change discovered weeks later | Re-baseline now; require goldens for all subsequent passes |
| Map | Used only token-based scanner (jscpd) | Missed Type II clones with renamed identifiers | Add similarity-ts / similarity-rs |
| Score | Estimated LOC saved without prototype | Refactor lands at -10 LOC instead of predicted -80 | Lower confidence default; require small spike |
| Prove | "N/A" on every isomorphism row | Quiet behavior change in production | Reject — fill in or write a property test first |
| Collapse | Two levers in one commit | Bisect can't isolate the regression | Split via interactive rebase OR revert + redo |
| Collapse | Used `sed` on 50 files | One file's context was different; quiet bug | Per AGENTS.md: never. Manual or parallel subagents only |
| Verify | Tests "still green" but count dropped | A test was skipped, not removed | Compare counts, not just exit code |
| Verify | Re-baselined goldens to make diff "go away" | Behavior change shipped | Goldens are immutable for the duration of a refactor pass |
| Ledger | No LOC delta recorded | Cannot answer "did this help" | Run `loc_delta.sh HEAD~1 HEAD <path>` |
