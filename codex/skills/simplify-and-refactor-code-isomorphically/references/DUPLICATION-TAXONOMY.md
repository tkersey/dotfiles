# Duplication Taxonomy

> Not all duplication is equal. The wrong merge is worse than the duplication it removes.

## Contents

1. [The five types](#the-five-types)
2. [Decision tree](#decision-tree)
3. [False-positive gallery](#false-positive-gallery)
4. [Tool calibration](#tool-calibration)
5. [The DRY heuristic correction](#the-dry-heuristic-correction)

---

## The five types

| Type | Name | Definition | Default action |
|------|------|------------|---------------|
| **I** | Exact clone | Token-by-token identical (often paste) | **Merge** — extract function |
| **II** | Parametric clone | Same shape, different identifiers / literals | **Merge** — parameterize |
| **III** | Gapped clone | Same shape, small additions/removals | **Maybe merge** — enum/strategy if variance bounded |
| **IV** | Semantic clone | Different code, equivalent behavior | **Stop** — prove equivalence first |
| **V** | Accidental rhyme | Looks similar, evolves independently | **Don't merge** — coupling cost > LOC savings |

### Type I — Exact

The classic. Two ten-line spans that are byte-equal. Nothing to think about: extract a function. The only failure mode is over-extracting (rung-skipping the [abstraction ladder](ABSTRACTION-LADDER.md)).

### Type II — Parametric

```rust
// Site A
let user = db.get::<User>(id).map_err(|e| Error::DbRead(e))?;
// Site B
let post = db.get::<Post>(id).map_err(|e| Error::DbRead(e))?;
```

The variance is in the type and the literal. Parameterize:

```rust
fn fetch<T: FromRow>(db: &Db, id: Id) -> Result<T, Error> {
    db.get::<T>(id).map_err(Error::DbRead)
}
```

Risk: low. Verify with type-checker that callers still infer the right `T`.

### Type III — Gapped

```python
# Site A
def handle_create(req):
    validate(req)
    log("create requested")
    obj = build(req)
    db.insert(obj)
    audit("create", obj.id)
    return obj

# Site B
def handle_update(req):
    validate(req)
    log("update requested")
    obj = build(req)
    obj.id = req.id   # <-- the gap
    db.update(obj)
    audit("update", obj.id)
    return obj
```

Tempting to merge. The right move depends on:
- **How many gaps?** One = parameterize the gap. Many = don't merge.
- **How likely to grow?** If `handle_delete` is coming next with three gaps, leave them all separate; you don't yet know the abstraction's shape.

A common bad merge:
```python
def handle(action, req):
    validate(req)
    log(f"{action} requested")
    obj = build(req)
    if action == 'update': obj.id = req.id
    {'create': db.insert, 'update': db.update}[action](obj)
    audit(action, obj.id)
    return obj
```
Now every reader has to mentally branch. The original was clearer because the branches were physically separate. Net loss.

### Type IV — Semantic

Two implementations that produce the same result via different code:

```typescript
// implementation A (set-based)
function uniq<T>(xs: T[]): T[] { return [...new Set(xs)]; }
// implementation B (sort-and-uniq)
function uniq<T>(xs: T[]): T[] {
  const sorted = [...xs].sort();
  return sorted.filter((v, i) => i === 0 || v !== sorted[i-1]);
}
```

These look interchangeable. They're not:
- A preserves insertion order; B does not.
- B fails on objects without comparable orderings.
- A throws if `T` doesn't hash; B throws if `T` doesn't compare.

**Rule:** never merge two Type IV implementations until you've written tests that pin every observable difference. Often the right answer is to delete one and update its callers — but that's a behavior change, not a refactor.

### Type V — Accidental rhyme

```rust
fn ms_to_seconds(ms: u64) -> u64 { ms / 1000 }
fn bytes_to_kib(b: u64) -> u64   { b / 1000 }
```

Same shape, totally unrelated. Merging them into `divide_by_1000(x)` would be insane — you'd couple the unit-conversion lifetimes. When KiB-conversion is corrected to `b / 1024`, the change cannot be made without touching ms-to-seconds.

This sounds obvious. But scanners flag it. Reviewers reject it. Then the next agent runs the scanner again and proposes the same merge. Document the rejection in a comment so it stops cycling:

```rust
// Note: shape rhymes with ms_to_seconds but unrelated; do not merge.
fn bytes_to_kib(b: u64) -> u64 { b / 1000 }
```

---

## Decision tree

```
Found a duplicate. Should I merge?

├─ Are they byte-identical (Type I)?
│  ├─ At ≥3 callsites? → MERGE (extract function)
│  └─ At 2 callsites?  → LEAVE (Rule of 3)
│
├─ Is the variance bounded and named (Type II)?
│  ├─ One axis of variance? → MERGE (parameterize)
│  ├─ Two axes, finite set?  → MERGE (enum dispatch)
│  └─ Many axes / open set?  → LEAVE
│
├─ Are there gaps in the middle (Type III)?
│  ├─ One gap, single axis?  → MERGE if the gap is itself a clean parameter
│  ├─ Many gaps?              → LEAVE — readers want the branches separate
│  └─ Gaps are growing?       → LEAVE — wait for shape to stabilize
│
├─ Different code, same behavior (Type IV)?
│  ├─ Have property tests?   → Pick best, delete others (after asking)
│  └─ No tests?              → WRITE TESTS FIRST. Don't merge yet.
│
└─ Looks similar, semantically unrelated (Type V)?
   └─ ALWAYS LEAVE. Add a comment explaining the rejection.
```

---

## False-positive gallery

Patterns scanners flag that are usually NOT duplication you should merge.

### Test setup boilerplate

Five tests with the same `setUp` lines. Don't extract — fixtures should be readable in place. If they're truly identical, use the framework's `setUp` / `BeforeAll` instead of pulling into a shared helper.

### Error formatting strings

Every handler has `log.error("failed to X: %v", err)`. The strings are similar; the meanings are not. Each handler logs at a specific point with specific context. Don't extract a `logFailure(action, err)` — you lose the call-site location and the handler-specific context. (And good logging libraries already capture caller info.)

### SQL queries

Six SELECTs that share a JOIN clause. Tempting to extract. Resist:
- Different SELECT columns mean different network bytes.
- Different WHERE clauses mean different query plans.
- Future changes (adding an index, changing a JOIN type) need to consider only the queries actually affected.

A shared `_join_user_orders()` helper that returns a query fragment usually causes more harm than good. Use a query builder if the shape is genuinely identical.

### Exception handlers

```python
try:
    do_stuff()
except FooError as e:
    log.warning(...); record_metric(...); raise
```

If five callers have this exact block, that's a *handler* — extract a decorator or context manager. But check: is each caller doing slightly different metric tagging or different log fields? If yes, leave them.

### Validation snippets

```typescript
if (!user) throw new Error('user not found');
```

This appears at 30 sites. Don't extract `assertUser(user)` — TypeScript narrowing is the better fix. Use a `User | null` discriminator and let the type system enforce it. Or use `zod` at the boundary. The "duplication" is a symptom of weak types.

### Imports

`jscpd` will sometimes flag long import blocks as duplicates. Ignore. Imports are inherently local.

---

## Tool calibration

### `jscpd` (token-based)

- Strong on Type I, weak on Type II.
- Default `--min-tokens 50` is reasonable; lowering to 30 floods you with imports/boilerplate.
- For TSX, set `--reporters json,html --gitignore` and review the HTML report — the visual side-by-side is faster than reading JSON.
- False positive: tightly-typed enums often look duplicate; check before merging.

### `similarity-ts` / `similarity-rs` / `similarity-py` (AST-based)

- Catches Type II well (renamed identifiers, swapped literals).
- Threshold `-p 80` typical; `-p 90` for high-precision review.
- Output is per-function-pair; deduplicate yourself with `jq` if needed.

### `pylint --enable=duplicate-code`

- Older, less precise than similarity-py.
- Useful for projects that already use pylint.
- Tunable via `min-similarity-lines`.

### `dupl` (Go)

- Token-based, fast.
- `-threshold 50` typical (50 tokens, ~20 LOC).

### `simian` (multi-language)

- Predates the others; still works.
- Best for C/C++/Java legacy.
- Configure `-threshold=6` for tight matches.

### `ast-grep` (structural patterns)

- Use when you have a hypothesis to confirm.
- Not a scanner per se — it's pattern-matching, requires writing the pattern.
- The right tool when the scanner says "no clones" but you suspect a structural family.

### `scc --by-file`

- Not a duplication tool. Sorts files by LOC and complexity.
- Use to find candidates: longest files often hide duplication.

### Manual reading

Scanners miss intent-based duplication: two functions that both *implement business rule X* but spell it differently. Reading is the only tool that catches them. Budget time for it.

---

## The DRY heuristic correction

The original DRY ("Don't Repeat Yourself", Hunt & Thomas, 1999) was about **knowledge**, not code:

> "Every piece of *knowledge* must have a single, unambiguous, authoritative representation within a system."

The colloquial version drifted to "every piece of code must have a single representation." This is wrong, and most of the bad refactors in the wild come from following the wrong version.

**The right test:** if you ask "would changing X require updating both sites in the same way?" — yes means duplicate knowledge (Type I/II/III; merge). No means coincident code (Type V; leave).

Two functions that compute taxes for two different jurisdictions look similar today; tomorrow they'll diverge as the laws change. Merging them gets undone the first time California raises its sales tax rate.

Two functions that format a date for display in two different parts of the UI may be identical now and forever — if both are showing "user-facing date in the user's locale," they encode one piece of knowledge and should be merged.

The refactor's success isn't measured in LOC removed. It's measured in *changes that now touch one place where they used to touch many*. LOC is a proxy.
