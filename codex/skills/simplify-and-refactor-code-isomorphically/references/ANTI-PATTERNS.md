# Anti-Patterns — failure modes with autopsies

> Each pattern names something that *looks* like good simplification work but ships bugs, churn, or trust loss.

## Contents

1. [Process anti-patterns](#process-anti-patterns)
2. [Code anti-patterns](#code-anti-patterns)
3. [Communication anti-patterns](#communication-anti-patterns)
4. [Tool anti-patterns](#tool-anti-patterns)

---

## Process anti-patterns

### "I'll fix tests after"

**Symptom:** The refactor is "almost done"; a few tests are red; you plan to fix them last.

**Why it fails:** You've now coupled the refactor with un-debugged failures. When you "fix" them, you'll either lose information about what the refactor broke (because you adjusted the test to match the new behavior) or compound debt (because you `#[ignore]` them).

**Recovery:** Roll back. Re-run baseline. Refactor in a way that doesn't break tests. If the refactor *requires* changing test behavior, it isn't isomorphic — split into a behavior-change commit + a refactor commit.

### "Let me just clean up while I'm here"

**Symptom:** Started with one duplication candidate. Diff now shows seven unrelated cleanups across four files.

**Why it fails:** Bisect-hostile. Reviewer-hostile. If a regression appears, you don't know which change caused it.

**Recovery:** `git reset --soft HEAD` and stage the changes by intent. One commit per lever. If that's painful, that's the signal: never let it happen again.

### "We can re-baseline goldens"

**Symptom:** Goldens differ after the refactor. You re-record them and call it done.

**Why it fails:** The whole point of goldens is to be the immutable contract. Re-recording them silently moves the goalpost. Behavior changed; the change is now invisible.

**Recovery:** If a golden diff is intentional, ship it as a separate "fix:" commit with the diff in the message, and re-baseline in that commit. Then continue the refactor on top.

### "I'll do all the work in one big PR"

**Symptom:** A 3000-line refactor PR that's "all related, please review together."

**Why it fails:** Nobody reviews 3000 lines well. Reviewers rubber-stamp. Bugs ship. Future bisect points to a single commit covering everything.

**Recovery:** Stack of PRs (one per lever) or a series of commits the reviewer can step through. The cost is yours, not theirs.

### "Skipping the duplication scanner — I can see the duplicates"

**Symptom:** You "spot-checked" and found 3 duplicates worth merging.

**Why it fails:** You missed the bigger ones. You also have no map to validate against later — was this 80% of duplication or 20%?

**Recovery:** Run the scanner. The map is also the artifact reviewers use to confirm the work has bounds.

### "Tests are flaky, just rerun until green"

**Symptom:** CI red. You rerun, it goes green. Ship.

**Why it fails:** A flaky test that gets *more* flaky after your refactor was made worse by your refactor. You've masked it.

**Recovery:** Run with `--repeat 50` locally. If the failure rate increased over baseline, your refactor caused it. (Many concurrency bugs land this way.)

---

## Code anti-patterns

### `utils.ts` / `helpers.py` / `lib/common.go` dumping ground

**Symptom:** All extracted helpers go into one file. After three rounds, the file is 1500 LOC of unrelated functions.

**Why it fails:** "Common" is not a domain. Helpers belong with the thing they help. Date helpers go in `date.ts`; auth helpers in `auth.ts`. Otherwise the central `utils.ts` becomes a coupling magnet — every test imports it, every change ripples.

**Better:** Group by what the function operates on, not by what kind of thing it is. `time.ts` (parses, formats, compares times). `currency.ts`. `fraction.ts`.

### `BaseFooManager` / `AbstractServiceImpl` / `IFooFactory`

**Symptom:** Inheritance abstractions named after their position in a pattern, not the domain they serve.

**Why it fails:** The name carries no information about behavior. You're inheriting from "Base" — but "Base what?" The implementation has nothing to do with the domain; it's all dispatch glue.

**Better:** Name abstractions by what they *do* in the domain. If you can't find a domain-meaningful name, that's a signal the abstraction is premature.

### Helper extracted from 2 callsites

**Symptom:** "I noticed these two functions look the same, so I extracted a helper."

**Why it fails:** Rule of 3 violation. With two examples you don't know what the variance axis is. The third caller will likely need a new parameter; you'll add it; the helper is now harder to read than two copies would have been.

**Better:** Leave it. If the third caller appears, evaluate then. Until it does, two copies cost less than one wrong abstraction.

### Renamed variables to "make the merge work"

**Symptom:** While merging two functions, you renamed `userId` → `id`, `count` → `n`, etc. to make the bodies textually identical so the extraction is "obvious."

**Why it fails:** Lost information. The variable names encoded what the body was operating on. After the rename, every reader has to context-switch to figure out whether `n` is a user count, a byte count, or an iteration count.

**Better:** Pass the well-named variable into the helper. Use parameter names that match the most common caller's vocabulary.

### `if let Some(_) = x { foo() } else { bar() }` instead of `match`

**Symptom:** "Simplified" `match` into nested `if let`s.

**Why it fails:** Loses exhaustiveness. When a new variant is added, the compiler doesn't tell you. You discover the bug in production.

**Better:** Keep `match` for sum types. The few extra characters buy compile-time correctness.

### Replaced `match` with method dispatch on a trait you just added

**Symptom:** Five-arm `match` "felt OO," so you added a trait with five impls.

**Why it fails:** Spread the logic across five files. Reader can no longer see the dispatch as a unit. Vtable cost in hot paths. Closed set is now open (you might add an unintended impl from outside).

**Better:** Keep the `match`. It's the right tool for closed sets.

### "Cleaner" map/filter chains that allocate intermediate Vecs

**Symptom:** Replaced an imperative loop with `xs.iter().filter(...).map(...).collect::<Vec<_>>().iter().filter(...).collect()`.

**Why it fails:** Each `.collect()` allocates and materializes. The original loop did one pass; the "cleaner" version does N.

**Better:** Keep iterators chained without intermediate `.collect()`. Or, if it really wants to be one expression, fuse with `filter_map`/`flat_map`.

### Removed "redundant" type annotations

**Symptom:** `let x: Vec<u32> = ...` simplified to `let x = ...`.

**Why it fails:** The annotation often pinned an inference choice. Without it, the inferred type may be `Vec<i32>` or `&Vec<u32>` — silently changing arithmetic semantics or borrow behavior.

**Better:** Leave annotations alone unless you've checked the inferred type matches.

### Used `any` to "simplify" generics

**Symptom:** Generic gymnastics felt complicated; you typed the parameter as `any` (TS) or `Box<dyn Any>` (Rust).

**Why it fails:** Lost type safety. You moved the error from a complex compile-time signature to a wide runtime crash surface.

**Better:** Either keep the generics or extract a typed boundary. `any` should be a last resort, not a simplification tool.

### Replaced `dataclass` with `dict`

**Symptom:** "It's just three fields, why use a dataclass."

**Why it fails:** Lost field validation, lost editor autocomplete, lost the ability to add `__slots__`, lost `__eq__` semantics, lost the type checker's help.

**Better:** Keep the dataclass. Three fields takes one line with `@dataclass`.

---

## Communication anti-patterns

### "This is more readable" without measurement

**Symptom:** Argued that a refactor improves readability without showing complexity / coupling / LOC numbers.

**Why it fails:** Readability is a group judgment. Your "cleaner" may be the next reader's "where did everything go?" Without numbers, the conversation is vibes.

**Better:** Show the numbers. `radon cc -a` mean drops from 8 to 4. LOC drops 30%. Coupling (imports out) drops 15%. Then the case is made.

### Claiming behavior preservation without evidence

**Symptom:** Commit message says "refactor, no behavior change." No goldens, no isomorphism card.

**Why it fails:** Reviewers and future bisects can't trust you. When something breaks two months later, your "no behavior change" claim is the first suspect.

**Better:** Attach the isomorphism card in the commit message. Cite the verifier output.

### Bundling bug fixes into refactors

**Symptom:** "While refactoring, I noticed and fixed bug X."

**Why it fails:** The bug fix is now invisible — buried in a refactor diff. Release notes miss it. Bisect points at the refactor for a regression unrelated to the bug fix. CHANGELOG omission.

**Better:** Two commits. Or two PRs. The bug fix is the more interesting one anyway.

### "I removed the unused file"

**Symptom:** Deleted a file you concluded was unused.

**Why it fails:** Per AGENTS.md Rule 1, file deletion requires explicit user permission. You may also be wrong: many "unused" files are imported via dynamic paths, by config files, by build scripts. Or they encode invariants that the in-memory representation doesn't.

**Better:** Move the file to `_unused/` (still in repo) and ask. Wait for explicit approval before removing.

---

## Tool anti-patterns

### Used `sed` to rename across 200 files

**Symptom:** "It's a simple rename — I used sed."

**Why it fails:** Per AGENTS.md, script-based code changes are forbidden in this repo. The reasons: regexes catch comments, strings, identifier substrings, and unrelated occurrences. The damage is hard to undo because individual changes can be subtly wrong.

**Better:** Use parallel subagents (each takes a subdirectory with the same Edit instruction) or do it manually. Slow is the price of correct.

### Used `cargo fmt` / `prettier` mid-refactor

**Symptom:** "While I was refactoring, I also ran the formatter."

**Why it fails:** The diff now shows formatting changes interleaved with semantic changes. Reviewers can't see the actual edit. Bisect can't isolate.

**Better:** Run formatter as a separate prep commit *before* the refactor. The refactor's diff is then small and readable.

### "I ran the linter and used `--fix`"

**Symptom:** Ran `eslint --fix` or `cargo clippy --fix` on the codebase as part of the refactor.

**Why it fails:** Same as above + auto-fixers are sometimes wrong. They've been known to introduce bugs (e.g., `await`-in-promise-chain auto-fixes that change cancellation semantics).

**Better:** Run auto-fixers in a dedicated commit. Eyeball every change. Run tests. Then continue.

### Profiled and optimized in the same PR

**Symptom:** Conflated simplification with performance work.

**Why it fails:** Different skills, different tradeoffs. A "simplification" that quietly speeds up code is suspect — likely you removed a side-effect that mattered.

**Better:** This skill (`simplify-and-refactor-code-isomorphically`) for behavior-preserving shrinkage. [extreme-software-optimization](../../extreme-software-optimization/SKILL.md) for performance. Cross [profiling-software-performance](../../profiling-software-performance/SKILL.md) before either.

### Used `--no-verify` to skip pre-commit hooks

**Symptom:** Pre-commit hook (UBS, ESLint, type check) failed; you used `--no-verify`.

**Why it fails:** The hook caught something. Bypassing it ships the something. Also: per default Claude Code instructions, `--no-verify` requires explicit user permission.

**Better:** Read the hook output. Fix the issue. If you genuinely think it's a false positive, escalate (file an issue, get approval) — don't bypass.
