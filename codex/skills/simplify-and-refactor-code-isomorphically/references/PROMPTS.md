# Copy-paste prompts

> The exact prompts to give an agent (or the model itself) for each phase. Each prompt has been written so it stands alone — paste it without context and the agent has enough to act.

## Contents

1. [Whole-skill prompt (kicks off the loop)](#whole-skill-prompt-kicks-off-the-loop)
2. [Per-phase prompts](#per-phase-prompts)
3. [Per-language prompts](#per-language-prompts)
4. [Per-target prompts](#per-target-prompts)
5. [Recovery / triage prompts](#recovery--triage-prompts)

---

## Whole-skill prompt (kicks off the loop)

```
Apply the simplify-and-refactor-code-isomorphically skill to <PATH>.

Goal: maximize LOC removed while preserving behavior bit-identically. The
artifacts of success are a duplication map, a ledger of accepted candidates
with isomorphism cards, and a series of small commits each with one lever.

Scope: <FILE/DIR/MODULE>. Languages present: <RUST/TS/PY/GO/CPP>.

Constraints (from AGENTS.md):
- No file deletion without my explicit approval.
- No script-based code changes (sed, codemods); use Edit tool or parallel subagents.
- Never overwrite an existing file with Write; only Edit.
- No "v2"/"_new"/"_improved" filenames; revise in place.
- Backwards compatibility is NOT a goal — early development, do it the right way.

Run the loop:
  1. BASELINE  — tests green, goldens hashed, LOC + complexity + warning counts.
  2. MAP       — duplication scan + callsite census.
  3. SCORE     — Opportunity Matrix; only candidates ≥ 2.0.
  4. PROVE     — isomorphism card BEFORE editing (not after).
  5. COLLAPSE  — one lever per commit, Edit only.
  6. VERIFY    — tests + goldens + typecheck + LOC + lints.
  7. REPEAT    — re-scan; new clones surface once noise clears.

Stop when no candidate scores ≥ 2.0. Hand off with a ledger summary.
```

---

## Per-phase prompts

### Phase A — Baseline

```
[Phase A — Baseline]

Capture and save under refactor/artifacts/<run-id>/:

1. Test pass count
   <run the test command for this project> 2>&1 | tee tests_before.txt
   Record: pass / fail / skip counts.

2. Golden outputs
   - Stage representative inputs (smallest set that hits each branch).
   - For each, run the program; redirect stdout, stderr, exit code.
   - sha256sum every output. Save checksums.txt.

3. LOC snapshot
   tokei --output json . > loc_before.json
   scc --by-file --format json . > scc_before.json

4. Typecheck/lint counts
   <linter --strict | tee linter_before.txt>
   Record warning count.

5. Document baseline.md with the table from METHODOLOGY.md §A5.

Stop and report when done. Do not proceed to Phase B until I confirm.
```

### Phase B — Map

```
[Phase B — Map]

Produce refactor/artifacts/<run-id>/duplication_map.md.

Run the language-appropriate scanner(s) for <LANG>:
- Rust:   similarity-rs, tokei, ast-grep
- TS:     jscpd, similarity-ts
- Python: pylint --enable=duplicate-code, similarity-py, vulture
- Go:     dupl, staticcheck
- C++:    clang-tidy modernize/readability, simian, lizard

For each clone family found:
- Assign an ID (D1, D2, ...)
- Record locations (file:line for every site)
- Estimate LOC
- Classify Type (I/II/III/IV/V) per DUPLICATION-TAXONOMY.md
- Note callsite count

Stop. Produce the map. Do not score yet.
```

### Phase C — Score

```
[Phase C — Score]

For each candidate in duplication_map.md, fill the Opportunity Matrix:

  Score = (LOC_saved × Confidence) / Risk

  LOC_saved (1-5):
    5: ≥200, 4: 50-200, 3: 20-50, 2: 5-20, 1: <5
  Confidence (1-5):
    5: scanner agrees + goldens cover + tests cover all callers
    3: scanner agrees, only one tested caller
    1: "feels similar"
  Risk (1-5):
    1: single file, single function, pure
    3: cross-module, shared state
    5: crosses async/ordering/error/observability boundary

Reject < 2.0. For accepted, also choose abstraction-ladder rung
(0 leave / 1 extract / 2 parameterize / 3 enum / 4 trait / 5 generic).
Pick the LOWEST rung that fits.

Save scored_candidates.md. Stop. Wait for my approval before any edit.
```

### Phase D — Prove (isomorphism card)

```
[Phase D — Prove]

For candidate <ID>, fill the isomorphism card BEFORE editing:

## Change: [one-line description]

### Equivalence contract
- Inputs covered: [list of callers and tests]
- Ordering preserved: [yes/no + why]
- Tie-breaking: [unchanged/N/A]
- Error semantics: [same Err variants under same conditions]
- Laziness: [unchanged/forced]
- Short-circuit eval: [unchanged]
- Floating-point: [bit-identical/N/A]
- RNG/hash order: [unchanged/N/A]
- Observable side-effects: [logs/metrics/spans/DB writes — identical order + payload]
- Type narrowing: [TS/Rust — narrowing preserved]
- Rerender behavior: [React — hooks order, memo keys, Suspense]
- Public API / ABI / FFI: [unchanged or document break]

If any row is "I don't know", STOP. Either inspect deeper or write a property test
to pin the behavior, then refill.

Save card to refactor/artifacts/<run-id>/cards/<ID>.md.
```

### Phase E — Collapse

```
[Phase E — Collapse]

Implement candidate <ID>.

Constraints:
- Use Edit tool only. No Write to existing files.
- ONE LEVER per commit. No rename + extract + cleanup mixed.
- For ≥10 callsites, split work across parallel subagents (each takes a sub-tree),
  not sed/codemod.
- If a file becomes empty, do NOT delete it. Move to refactor/_to_delete/ and ask.

Commit message format:
  refactor: <one-line>
  <isomorphism card verbatim>
  LOC: <path> <before>→<after> (<delta>). Tests <pass>/<fail>/<skip> unchanged.
```

### Phase F — Verify

```
[Phase F — Verify]

Run all five gates. Each must pass:

1. Tests
   <test command>
   Compare pass/fail/skip count to baseline. MUST be equal (not just "all green").

2. Goldens
   For each input file:
     diff <(./bin "$f") "refactor/artifacts/<run>/goldens/out/$(basename $f).stdout"
   Then: sha256sum -c refactor/artifacts/<run>/goldens/checksums.txt

3. Typecheck/lint
   <linter --strict>
   Compare warning count to baseline. MUST not grow.

4. LOC delta
   tokei --output json . > loc_after.json
   Compare to loc_before.json. Δ should match the prediction within ±10%.

5. Lints
   No new `#[allow]`, `// eslint-disable`, `# type: ignore`, `# noqa`.

Report the table. Append to refactor/artifacts/<run>/LEDGER.md.
```

---

## Per-language prompts

### Rust

```
Apply the skill to <PATH> in this Rust crate.

Targets I want you to look for:
- `match Err(e) => Err(e)` ladders that should be `?`
- Hand-rolled `impl PartialEq/Hash/Default/Display/Debug` that could be derived
- Sibling `fn parse_u32 / parse_i32 / parse_f64` that should be one generic `fn parse<T: FromStr>`
- `Box<dyn Trait>` for closed sets (replace with enum)
- Repeated error variants + From impls (collapse with `thiserror`)
- Two near-identical `fn send_*` collapsed into one with an enum payload

Run cargo test before and after. Verify clippy warnings did not grow:
  cargo clippy --all-targets -- -D warnings 2>&1 | tee clippy_after.txt
  diff clippy_before.txt clippy_after.txt
```

### TypeScript / React

```
Apply the skill to <PATH> in this Next.js / React project.

Targets I want you to look for:
- Sibling components like Xxx{Primary,Secondary,Danger} → unify with `variant`
- Same fetch+state+effect block in 3+ components → custom hook
- Function overloads that could be one generic
- `as any` / `as unknown as` (often hides earlier "simplifications")
- jscpd hits with min-tokens 50

Run before/after:
  pnpm test
  pnpm tsc --noEmit
  pnpm next build (capture bundle size)
  npx playwright test (if visual goldens exist)

Compare bundle size — a "simplification" that grows the bundle by >5% is suspect.
```

### Python

```
Apply the skill to <PATH> in this Python project.

Targets I want you to look for:
- Repeated try/finally cleanup → @contextmanager
- Class with only __init__ + fields → @dataclass(frozen=True, slots=True)
- if/elif on type → match (3.10+) or singledispatch
- Manual __eq__/__hash__ → @dataclass(eq=True, frozen=True)
- 6× repeated validation patterns → pydantic / attrs

Run before/after:
  pytest -q
  mypy --strict src/
  pylint --disable=all --enable=duplicate-code src/

Make sure mypy warning count does not grow.
```

### Go

```
Apply the skill to <PATH> in this Go module.

Targets I want you to look for:
- Sibling Max/Min/Clamp by type → generics (1.18+)
- Three near-identical structs sharing logger/metrics → embed BaseHandler
- Manual table-test boilerplate → t.Run loop
- Hand-rolled Stringer/MarshalJSON for trivial cases

DO NOT collapse `if err != nil { return err }` blocks — that is Go's `?`.
Don't replace with `must` helpers.

Run:
  go test ./...
  go vet ./...
  staticcheck ./...
  dupl -threshold 50 -plumbing ./...   (compare counts before/after)
```

### C++

```
Apply the skill to <PATH> in this C++ project.

Targets I want you to look for:
- Raw new/delete pairs → std::unique_ptr / std::make_unique
- Class hierarchy (closed set) → std::variant + std::visit
- C-style typedef → using
- Macro-based polymorphism → templates / concepts (C++20)
- Repeated SFINAE → concepts

Run before/after:
  cmake --build build
  ctest --output-on-failure
  clang-tidy -checks='modernize-*,readability-*' -p build src/...

If using ASAN/UBSAN/MSAN sanitizers, run after the change to catch life-cycle changes
introduced by RAII conversions.
```

---

## Per-target prompts

### "Reduce LOC by N%"

```
Apply the skill to <PATH> aiming for ~<N>% LOC reduction.

Strategy:
1. Run dup scan and complexity scan; rank candidates by predicted LOC saved.
2. Implement candidates in score order until accumulated reduction reaches <N>%.
3. STOP at the target. Do not chase the last 5% with risky merges.

Report:
- LOC before / after / delta / percent
- Number of accepted candidates / number rejected
- Tests / goldens / typecheck status
```

### "Make this folder reusable"

```
Apply the skill to <PATH> with a "make-reusable" lens.

For each module/component:
- Identify which symbols are used externally (callsite census across the repo).
- Identify which symbols are used only within the module (collapse candidates).
- Identify which symbols are duplicated in nearby modules (lift candidates).

Score candidates with extra weight on Confidence when callers form a clean public API.
Produce a "public surface" doc listing what stays and what becomes private.
```

### "Make these two files share more logic"

```
Apply the skill to <FILE_A> and <FILE_B>.

1. Diff the two files structurally (similarity-* tool).
2. List shared sections (Type I/II) and divergent sections (Type III).
3. For shared sections, decide:
   - Pull into a third file (semantic home: name it after the domain)
   - Or: pull as a method on a shared trait/interface
4. For divergent sections, leave alone.
5. Specifically check for false positives (Type IV/V).

Report a before/after diff and the rationale per section.
```

---

## Recovery / triage prompts

### "Verify failed: tests went from 342 to 339 passing"

```
[Recovery — verify failed]

Tests dropped from 342/0/5 to 339/0/8 after candidate <ID>.

Diagnose:
1. Which 3 tests now skip? (If skipped, they may be conditional on something the refactor changed.)
2. Which tests would have failed if not skipped? Run them with the skip removed.
3. Was a fixture broken? An import? A type narrowing change?

Do NOT mark tests as skipped to "make them pass". Roll back the refactor.
Re-evaluate 🎯 Score with the new evidence (Risk was higher than thought).
```

### "Goldens differ but the diff looks intentional"

```
[Recovery — golden diff]

Goldens differ post-refactor on input <PATH>.

Inspect the diff:
  diff <(./new "$input") refactor/artifacts/<run>/goldens/out/$(basename $input).stdout

Decide:
- Diff is unintended → roll back the refactor.
- Diff is a bug fix incidentally caused → split into:
    Commit A: "fix: <what changed>" (just the behavior change, smallest possible)
    Commit B: "refactor: <original simplification>" (now isomorphic to fixed behavior)
  Re-baseline goldens in commit A's body, with diff explanation.
- Diff is "obviously fine" → STOP. Goldens are immutable for the duration of a pass.
  If you really want to re-baseline, get user approval and document the reason.
```

### "Predicted -80 LOC, got -3 LOC"

```
[Recovery — score failed]

Candidate <ID> predicted LOC_saved=4, delta=80; actual delta=3.

Diagnose:
- Did the new helper end up larger than expected? Check it for parameter sprawl
  (>3 params is a smell).
- Did callers grow because of new boilerplate?
- Did unrelated callers also need updates that weren't in the prediction?

If LOC outcome doesn't justify the change, consider 𝓘 Inline to revert.
Update Confidence priors so future scores are more honest.
```
