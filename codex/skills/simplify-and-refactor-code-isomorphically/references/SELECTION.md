# Selection — when this skill vs. sibling skills

> Before doing any refactor, check whether another skill is the better fit.
> This skill is *aggressive but precise* — it wants duplication to unify, types to
> shrink, orphans to merge. It is NOT the right tool for debugging, porting,
> performance work, or "make this generally nicer."

## Contents

1. [Use THIS skill when…](#use-this-skill-when)
2. [Use `simplify` (built-in) when…](#use-simplify-built-in-when)
3. [Use `extreme-software-optimization` when…](#use-extreme-software-optimization-when)
4. [Use `codebase-archaeology` when…](#use-codebase-archaeology-when)
5. [Use `multi-pass-bug-hunting` when…](#use-multi-pass-bug-hunting-when)
6. [Use `operationalizing-expertise` when…](#use-operationalizing-expertise-when)
7. [Use `porting-to-rust` when…](#use-porting-to-rust-when)
8. [Use `library-updater` when…](#use-library-updater-when)
9. [Use `ubs` during every commit](#use-ubs-during-every-commit)
10. [Decision table](#decision-table)

---

## Use THIS skill when…

- The user says: *simplify, refactor, reduce duplication, de-dup, unify, collapse,
  DRY this up, remove boilerplate, merge `_v2` files, clean AI slop, kill dead code,
  rescue vibe-coded project, shrink types, pin floating deps.*
- You've seen the same logic in 3+ places.
- An AI session left obvious orphans, `_v2`/`_new` files, layered try/catch, or
  bloated DTOs.
- A project has a baseline (tests pass, goldens exist) and the user wants a
  proof-preserving cleanup pass.

## Use `simplify` (built-in) when…

The built-in `simplify` skill is the Anthropic "review recently-changed code
for reuse and quality" tool. Use it **after** your own edits and **before**
`git commit`, for a lighter touch. This skill supersedes `simplify` when the
task is a planned refactor pass (not just "tidy the diff I just wrote").

## Use `extreme-software-optimization` when…

- The user says *slow, bottleneck, hot path, CPU, memory, latency, throughput*.
- You have a profile and measured regressions.

This skill will happily collapse equivalent code. `extreme-software-optimization`
will introduce NEW code that is faster. These are different jobs; don't try
to optimize during a refactor pass — it violates "one lever per commit".

## Use `codebase-archaeology` when…

You're new to the codebase. Get a working mental model *first*, then refactor.
The isomorphism card requires you to know what "observable contract" means
for each site — archaeology gives you that.

## Use `multi-pass-bug-hunting` when…

You suspect real bugs (wrong behavior, not ugly code). Refactoring on top of a
latent bug will smuggle the bug into the new shape. Fix first.

## Use `operationalizing-expertise` when…

You want to CAPTURE a methodology as a skill (what this very repo does). Not
applicable during a refactor pass.

## Use `porting-to-rust` when…

The goal is a rewrite in a different language. That's not a refactor — the
observable contract is explicitly allowed to change (different runtime, etc.).
Our isomorphism rules don't apply.

## Use `library-updater` when…

Your candidate list is dominated by "bump this dep." Dep updates have their
own gauntlet (semver / changelog / test). `library-updater` handles them.
Unpinned deps (P37) are the one exception we handle inline.

## Use `ubs` during every commit

UBS (Ultimate Bug Scanner) runs on every diff before commit in this skill's
loop. Always. It's a guardrail, not a separate activity.

## Decision table

| Situation                                          | Skill |
|----------------------------------------------------|-------|
| "3 near-identical functions, collapse them"        | simplify-and-refactor-code-isomorphically (this skill) |
| "This endpoint is slow"                            | extreme-software-optimization |
| "I inherited this codebase, orient me"             | codebase-archaeology |
| "This feature is broken sometimes"                 | multi-pass-bug-hunting |
| "I want to write a skill for X"                    | operationalizing-expertise |
| "Rewrite this shell pipeline in Rust"              | porting-to-rust |
| "Bump all deps to latest stable"                   | library-updater |
| "Scan this diff for bugs before committing"        | ubs (invoked from this skill) |
| "Clean up after a 3-month Claude Code spree"       | simplify-and-refactor-code-isomorphically (this skill, starting in RESCUE mode) |
| "Consolidate 7 `UserDTO` types"                    | simplify-and-refactor-code-isomorphically (L-TYPE-SHRINK) |
| "This function is dead code, delete it"            | simplify-and-refactor-code-isomorphically (dead-code gauntlet) |
| "Move logic out of route handlers into services"   | simplify-and-refactor-code-isomorphically (L-EXTRACT) |

If the user's request is ambiguous ("clean this up"), ask once: is the goal
(a) preserve behavior while shrinking, (b) improve performance, or (c) both?
If (c), do (a) first — behavior-preserving shrinking makes performance work
cheaper. Never mix (a) and (b) in the same commit.
