# Simplification Operator Cards

> Named cognitive moves with triggers, failure modes, and copy-paste prompt modules. Pattern lifted from the [profiling-software-performance](../../profiling-software-performance/SKILL.md) operator algebra.

## Contents

1. [Why operator cards](#why-operator-cards)
2. [The operator algebra at a glance](#the-operator-algebra-at-a-glance)
3. [Mapping operators](#mapping-operators)
4. [Decision operators](#decision-operators)
5. [Transformation operators](#transformation-operators)
6. [Guard operators](#guard-operators)
7. [Composition rules](#composition-rules)

---

## Why operator cards

Refactoring is a chain of decisions. "Extract a helper" is a one-line action that hides three sub-decisions: *should* I extract, *what* should the parameter set be, *where* should the helper live. Naming each sub-decision lets you audit the chain.

Every operator must have:
- **Symbol** — a glyph
- **Name** — 2-3 words
- **Definition** — one sentence
- **Triggers** — ≥3 concrete situations
- **Failure modes** — ≥2 ways it goes wrong
- **Prompt module** — copy-paste text an agent can execute

## The operator algebra at a glance

```
Mapping:         🗺 Map               𝛟 Census           ☰ Cluster
Decision:        🎯 Score             ⛔ Reject           🪜 Ladder-Place
Transformation:  ✂ Extract            𝓟 Parameterize     ⊞ Merge
                  𝓘 Inline             🪂 Hoist            ⤬ Unify
Guard:           🛡 Isomorphism       📐 Type-Pin         🔒 Goldens
                  🧪 Property          🚫 No-Codemod      ✋ Ask-Before-Delete

Default chains:
  Bottom-up:  🛡 → 🗺 → 𝛟 → 🎯 → 🪜 → ✂/𝓟/⊞ → 🔒 → next
  Top-down:   🛡 → 🗺 → ☰ → ⊞ (if 🪜 says yes) → 🔒 → next
  Recovery:   ⛔ → 𝓘 → re-evaluate
```

---

## Mapping operators

### 🗺 Map

**Definition**: Produce the duplication map (and complexity/coupling map) before any change.

**Triggers**:
- User says "remove duplication" / "DRY this up" without naming targets
- Reviewing an unfamiliar codebase — you don't know where to look
- Re-entering a module after weeks; a fresh map prevents stale-memory mistakes

**Failure modes**:
- Eyeball-only ("I can see the duplicates"): you'll miss the bigger ones
- Token-only scanner: misses Type II clones with renamed identifiers
- No artifact saved: re-runs are not comparable

**Prompt module**:
```text
[OPERATOR: 🗺 Map]
1) Run the language-appropriate duplication scanner. Save JSON.
2) Sort by (LOC × clones) descending.
3) Save: refactor/artifacts/<run-id>/duplication_map.{json,md}
4) Report top 10 candidates with file:line spans.

Output: duplication_map.md with one row per candidate (ID, kind, locations, LOC, type).
```

### 𝛟 Census

**Definition**: For each candidate, enumerate every callsite and compare contexts.

**Triggers**:
- After 🗺 Map, before scoring
- A function called "from many places" — find out how many and from where
- A type used in many modules — check what each module does with it

**Failure modes**:
- Counting only direct calls: misses dispatch through a trait/interface
- Ignoring tests: tests are callers and matter for refactor risk
- Skipping context: two callsites look identical but live in different invariants

**Prompt module**:
```text
[OPERATOR: 𝛟 Census]
For candidate <ID>:
  rg --type <lang> '<symbol>' -n
  ast-grep run -l <Lang> -p '<pattern>' --json
List for each callsite: file, line, surrounding function, what it passes, what it expects back.
Flag any callsite whose surrounding context (locks held, async/sync, error-handling discipline) differs.
```

### ☰ Cluster

**Definition**: Group near-duplicate sites by similarity-of-shape, naming the dominant axis of variance per cluster.

**Triggers**:
- Many candidates from the same module — likely all instances of one pattern
- A long function with internal repetition
- Scanner output has 20+ small hits that need grouping before scoring

**Failure modes**:
- Clustering across modules with different error/concurrency disciplines
- Treating cross-cluster items as merge candidates

**Prompt module**:
```text
[OPERATOR: ☰ Cluster]
1) Group candidates by repeated shape, not by filename similarity.
2) For each cluster, name exactly one dominant axis of variance.
3) Split any cluster that crosses async, transaction, security, or observability boundaries.

Output: cluster table with cluster ID, members, shared shape, variance axis, and split rationale.
```

---

## Decision operators

### 🎯 Score

**Definition**: Apply the Opportunity Matrix — `(LOC_saved × Confidence) / Risk` — and only proceed on Score ≥ 2.0.

**Triggers**:
- After 𝛟 Census, before any 🪜 Ladder-Place
- When tempted to "just do" a refactor without writing it down
- When the user asks "is it worth it?"

**Failure modes**:
- Inflating Confidence on speculation
- Under-counting Risk when the boundary is async/transactional/observability
- Forgetting to subtract the LOC of the new abstraction from the saved LOC

**Prompt module**:
```text
[OPERATOR: 🎯 Score]
Compute and record:
  LOC_saved  = sum(clone.lines) - estimated_unified.lines
  Confidence = 5 if scanner+goldens confirm; 3 if scanner agrees but only one tested caller; 1 if "feels"
  Risk       = 1 single file pure; 3 cross-module shared state; 5 crosses async/error/observability boundary
  Score      = (LOC_saved × Confidence) / Risk
Reject if Score < 2.0; promote to Tier-3 plan-doc if Score > 10 and Risk > 3.
```

### ⛔ Reject

**Definition**: Refuse a refactor that scored low or whose isomorphism axes can't be filled.

**Triggers**:
- Score < 2.0
- Isomorphism card has multiple "I don't know" rows
- Candidate is Type IV/V (semantic clone or accidental rhyme)

**Failure modes**:
- Soft-rejecting (queue for "later") instead of documenting the rejection — leads to repeat scanner alarms
- Letting estimator bias you back in after rejection

**Prompt module**:
```text
[OPERATOR: ⛔ Reject]
Add to refactor/artifacts/REJECTIONS.md:
  - Candidate ID
  - Why rejected (Score, type IV/V, unknown invariant, etc.)
  - Comment to add at the relevant code site explaining the rejection (so future scans don't re-propose it)
```

### 🪜 Ladder-Place

**Definition**: Pick the lowest abstraction-ladder rung that solves the candidate.

**Triggers**:
- After 🎯 Score; before 𝓟/⊞
- When choosing between extract-fn vs trait vs generic
- When a proposed abstraction has more parameters than the duplicated code had variance

**Failure modes**:
- Skipping rungs (going straight to trait/generic)
- Not asking "rule of 3?" — sometimes the right answer is "wait"

**Prompt module**:
```text
[OPERATOR: 🪜 Ladder-Place]
For candidate <ID>:
  Count concrete callsites: ___
  Count axes of variance:   ___
  Is variance set bounded?  yes/no
  Recommended rung:
    0 (leave) if <3 callsites
    1 (extract fn) if 3+ callsites, 0 axes
    2 (parameterize) if 3+ callsites, 1 axis
    3 (enum/strategy) if 3+ callsites, 2+ axes, bounded
    4+ (trait/generic) only if open set
Pick the LOWEST rung that fits.
```

---

## Transformation operators

### ✂ Extract

**Definition**: Pull a span into a named function/method, leaving callers with a call expression.

**Triggers**:
- Type I clone at ≥3 sites
- Function over the recommended cyclomatic-complexity bound
- Top of an enum-dispatch refactor (extract first, generalize next)

**Failure modes**:
- Extracted function takes 5+ parameters → real abstraction was wrong
- Helper lives in `utils/` (no semantic home) → coupling magnet
- Helper has a non-domain name (`processData`, `transform`)

**Prompt module**:
```text
[OPERATOR: ✂ Extract]
For span at <file:lines>:
  Name the new function in domain terms.
  Place it in the file/module of the most-called caller, NOT in a generic utils file.
  Pass at most 3 parameters; if 4+, return to 🪜 and reconsider.
  Apply via Edit tool only.
```

### 𝓟 Parameterize

**Definition**: Take an existing helper and add one parameter to absorb a variance axis.

**Triggers**:
- Two near-identical helpers differing in one literal/identifier/type
- After ✂ Extract, when more sites match if you generalize
- A helper copy-paste family has exactly one real axis of variance

**Failure modes**:
- Adding a `kind` parameter without enum constraint (stringly-typed) — invites bugs
- Adding a parameter that callers all pass the same value — pseudo-variance

**Prompt module**:
```text
[OPERATOR: 𝓟 Parameterize]
For candidate <ID>:
1) Name the single variance axis.
2) List every current literal/identifier/type value on that axis.
3) Pick the narrowest representation: boolean only for true binary, enum for bounded sets, type parameter only for type-level variance.
4) Reject if a second axis appears.

Output: one proposed signature, callsite rewrite table, and rejection note if variance is not single-axis.
```

### ⊞ Merge

**Definition**: Combine two or more callers/components/types into one with explicit dispatch.

**Triggers**:
- Two components / handlers / parsers with same shell, varying body
- Type II/III clone confirmed bounded
- All variants share lifecycle, error semantics, and ownership boundaries

**Failure modes**:
- Merging Type IV (semantic clones) — quiet behavior change
- Merging when error semantics differ → wider Err set on callers

**Prompt module**:
```text
[OPERATOR: ⊞ Merge]
For candidate <ID>:
1) Fill a variant table: original name, dispatch key, unique behavior, shared behavior.
2) Prove every variant has the same lifecycle and error boundary.
3) Design explicit dispatch (enum/variant prop/match/table) with one arm per original.
4) Reject if any original has a unique invariant that would become an optional flag.

Output: merge design table plus lowest-rung dispatch shape.
```

### 𝓘 Inline

**Definition**: Reverse an extraction. Move a single-call wrapper's body into its sole caller.

**Triggers**:
- Wrapper has one call site
- Wrapper is one expression
- Wrapper exists "in case we need it" but never did

**Failure modes**:
- Inlining a function that's a public API — breaks consumers
- Inlining inside a hot loop without checking the inliner already did it

**Prompt module**:
```text
[OPERATOR: 𝓘 Inline]
For wrapper <symbol>:
1) Run callsite census across source, tests, config, and docs.
2) Confirm the wrapper is not public API, exported symbol, macro target, route handler, or config entry.
3) Inline into the sole caller with the smallest Edit diff.
4) Re-run the census and tests.

Output: census summary, inline diff plan, and public-surface verdict.
```

### 🪂 Hoist

**Definition**: Move repeated work out of a loop / out of every caller into a higher scope.

**Triggers**:
- Pre-compiled regex inside a loop
- Same setup at the top of every test
- Authentication check at every handler

**Failure modes**:
- Hoisting work that depends on per-iteration state
- Hoisting an effectful call (changes side-effect cardinality)

**Prompt module**:
```text
[OPERATOR: 🪂 Hoist]
For repeated work <expr>:
1) Mark each value read by the expression as invariant or variant across the hoist boundary.
2) Confirm the expression is pure or that the side-effect count is intentionally preserved.
3) Hoist only to the nearest scope that dominates all uses.
4) Verify ordering, logs, metrics, and allocation count if observable.

Output: invariant table, target scope, and side-effect cardinality verdict.
```

### ⤬ Unify

**Definition**: Merge two data types / two enums / two interfaces. The riskiest transformation operator.

**Triggers**:
- Two data shapes that *might* represent the same thing
- After confirming every field means the same thing in every consumer (see [TECHNIQUES.md §Data-model unification](TECHNIQUES.md#data-model-unification))
- DTO/interface/model families with duplicated fields and drifted names

**Failure modes**:
- Different units silently combined (cents vs dollars)
- Different nullability semantics (missing = unknown vs missing = zero)
- Different identity / equality

**Prompt module**:
```text
[OPERATOR: ⤬ Unify]
For types <A> and <B>:
1) Build a field equivalence table: name, type, unit, nullability, default, serializer, readers, writers.
2) Mark each row SAME, CONVERTIBLE, or DIFFERENT.
3) Unify only SAME rows. For CONVERTIBLE rows, add an explicit conversion first. For DIFFERENT rows, reject.
4) Preserve serialization and public API behavior unless the commit is explicitly a fix/migration.

Output: field table, survivor type, conversion plan, and reject/split verdict.
```

---

## Guard operators

### 🛡 Isomorphism

**Definition**: Fill the per-change isomorphism card BEFORE editing.

**Triggers**:
- Always, before any transformation operator
- Before merging a PR you didn't review
- Whenever the proposed change claims "no behavior change"

**Failure modes**:
- Skipping rows ("N/A" reflexively)
- Filling after the diff exists ("rationalization mode")

**Prompt module**:
```text
[OPERATOR: 🛡 Isomorphism]
1) Fill the isomorphism card before editing.
2) For every axis, answer SAME, CHANGED, or UNKNOWN. UNKNOWN blocks the edit.
3) Attach the exact proof command for each load-bearing axis.

Output: completed card path plus one-line READY/REJECT verdict.
```

### 📐 Type-Pin

**Definition**: Add type annotations to load-bearing variables before refactoring, to lock inferred types.

**Triggers**:
- Codebases with extensive type inference (Rust, TS with `any`-prone code, modern Python)
- About to refactor across a generic / inference boundary
- A candidate depends on compiler inference that reviewers cannot see in the diff

**Failure modes**:
- Pinning the *wrong* type (use `cargo expand` / `tsc --noEmit --listFiles` to see what compiler infers)
- Pinning too broadly (`any`, `object`, `Box<dyn Any>`) and losing the useful constraint

**Prompt module**:
```text
[OPERATOR: 📐 Type-Pin]
For candidate <ID>:
1) Identify inferred values whose type constrains the refactor.
2) Ask the compiler/tooling for the inferred type where possible.
3) Add the narrowest explicit type annotation as a separate prep commit when risk justifies it.
4) Reject annotations that widen the type.

Output: type-pin table with symbol, inferred type, explicit type, and reason.
```

### 🔒 Goldens

**Definition**: Capture, then verify against, golden outputs for every change.

**Triggers**:
- Before any transformation operator
- Always, when the program produces deterministic output
- Whenever tests assert "green" but not byte-identical output

**Failure modes**:
- Re-baselining goldens to make a diff "go away"
- Capturing goldens *after* the change

**Prompt module**:
```text
[OPERATOR: 🔒 Goldens]
1) Choose representative deterministic inputs before editing.
2) Capture outputs and hashes under refactor/artifacts/<run-id>/goldens/.
3) After the edit, re-run the exact command and compare hashes.
4) Treat any mismatch as behavior change unless explicitly approved as a fix.

Output: golden command, hash file path, before/after verdict.
```

### 🧪 Property

**Definition**: Add property-based tests for invariants the refactor preserves.

**Triggers**:
- Before refactoring something with stochastic / data-shape input
- When goldens can't cover the variation space
- When the candidate's observable behavior is a relation rather than a single output

**Failure modes**:
- Property is too weak (tautological)
- Property covers only happy path

**Prompt module**:
```text
[OPERATOR: 🧪 Property]
For invariant <name>:
1) State the relation in one sentence.
2) Define input generators that include edge cases and shrink well.
3) Run the property against the pre-refactor implementation and save the seed.
4) Run the same property after the refactor.

Output: property name, generator summary, oracle relation, seed, and before/after result.
```

### 🚫 No-Codemod

**Definition**: Refuse to use sed/regex/scripts to bulk-edit code (per AGENTS.md).

**Triggers**:
- Tempted to "just sed this" across many files
- "Simple rename" across modules
- A change touches enough files that an automatic rewrite feels attractive

**Failure modes**:
- Doing it anyway when "the regex is obviously safe"
- (There are no exceptions in this repo. Use parallel subagents instead.)

**Prompt module**:
```text
[OPERATOR: 🚫 No-Codemod]
1) Stop before any sed/perl/python/codemod rewrite.
2) Split the edit into manual Edit chunks or independent subagent-owned files.
3) For identical literal replacement, use the harness Edit tool with exact old/new strings and inspect every hunk.
4) Record the edit method in the card.

Output: manual edit plan with file ownership and verification commands.
```

### ✋ Ask-Before-Delete

**Definition**: Never delete a file or folder without explicit user permission (per AGENTS.md Rule Number 1).

**Triggers**:
- A helper file whose contents are now empty
- An "obviously dead" module after consolidation
- Old test fixtures that look obsolete

**Failure modes**:
- Deleting a file that was used by build / dynamic import / tests you didn't run
- Asking for deletion approval without evidence

**Prompt module**:
```text
[OPERATOR: ✋ Ask-Before-Delete]
Stop. Do not delete <path>.
Move it to refactor/_to_delete/<path> instead, leaving git history.
Then ask:
  "I believe <path> is now unused; here is the evidence (rg, callers, tests). May I delete it?"
Wait for explicit "yes" before unlinking.
```

---

## Composition rules

### Default chain (greenfield refactor of one candidate)

```
🛡 Isomorphism → 🗺 Map → 𝛟 Census → 🎯 Score
   ↓ (if ≥ 2.0)
🪜 Ladder-Place → ✂ Extract / 𝓟 Parameterize / ⊞ Merge / 𝓘 Inline / 🪂 Hoist
   ↓
🔒 Goldens-verify → 📐 Type-Pin → ledger entry → next candidate
```

### Recovery chain (refactor surfaced a problem)

```
verify failed → 𝓘 Inline (revert the change locally) → re-run goldens → diagnose
   ↓ if behavior change was unintentional
roll back → re-evaluate Score (Risk was higher than estimated) → maybe ⛔ Reject
   ↓ if behavior change was intentional
ship as separate "fix:" commit → resume refactor on top
```

### Escalation chain (Tier-3 architectural)

```
🎯 Score > 10 AND Risk ≥ 4 → write planning doc → user review →
  break into smaller candidates → run default chain on each
```

### Anti-chain (don't do)

```
🗺 Map → ✂ Extract     # No score, no isomorphism. The shortest path to bugs.
✂ Extract → 𝓟 Parameterize → ⊞ Merge in one commit  # Two-lever; bisect-hostile.
⊞ Merge → 🛡 Isomorphism  # Backwards. Card after the fact = rationalization.
```

---

## Operator coverage check

Before claiming a refactor pass is done, verify each accepted candidate had:
- 🗺 Map row in duplication_map.md
- 𝛟 Census recorded in artifacts
- 🎯 Score ≥ 2.0 with all three multipliers cited
- 🪜 Ladder-Place justification (rung chosen + why)
- 🛡 Isomorphism card in commit message (every row answered)
- 🔒 Goldens hashed and verified post-commit
- LOC delta in ledger

If any operator was skipped, you owe an explanation in the rejection log or a re-do on that candidate.
