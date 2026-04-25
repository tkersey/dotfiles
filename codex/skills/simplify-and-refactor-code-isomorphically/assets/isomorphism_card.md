# Isomorphism Card — <candidate-id>

> Fill this out **before** editing any code. If any field is unknown, go answer it first.
> See [ISOMORPHISM.md](../references/ISOMORPHISM.md) for the proof rubric.

## 1. Identity

- **Candidate ID:** <e.g. ISO-014>
- **Run ID:** <yyyy-mm-dd-pass-N>
- **Clone type:** I (exact) / II (parametric) / III (gapped) / IV (semantic) / V (accidental)
- **Expected LOC saved:** <n>
- **Score:** (LOC_saved × Confidence) / Risk = <computed>

## 2. Sites

List every call site / usage. If `>10`, link to `callsite_census.sh` output.

```
path/to/fileA.rs:42
path/to/fileB.rs:117
path/to/fileC.rs:203
```

## 3. Observable contract

For each site, state what the caller observes. The refactor must preserve:

- [ ] Return value / output for every input in the test corpus
- [ ] Side effects (what gets written, logged, sent; in what order)
- [ ] Error modes (which errors escape, with which type/message)
- [ ] Timing guarantees (sync vs async, ordering, atomicity)
- [ ] Observability hooks (metrics names, tracing spans, log fields)

## 4. Hidden differences between sites

Put every tiny divergence you noticed. This is where isomorphism dies.

- Site A: <e.g. swallows SQLITE_BUSY>
- Site B: <e.g. retries 3x>
- Site C: <e.g. logs at WARN, others at ERROR>

Strategy for each difference:
- [ ] Parameter (pass a flag)
- [ ] Decorate (wrap at the call site)
- [ ] Leave separate (don't collapse — this is clone type V, accidental rhyme)

## 5. Proof strategy

- [ ] Unit tests cover every branch: <list test names>
- [ ] Golden outputs captured for: <list commands/inputs>
- [ ] Property test added (if applicable): <property name>
- [ ] `cargo test --no-fail-fast` / `pytest -q` / `npm test` passes before and after

## 6. Risk

- **Reversibility:** Can this be reverted with `git revert HEAD`? yes / no / complicated-because-<x>
- **Blast radius:** <list downstream consumers if type signature changes>
- **Concurrency hazard:** does the collapse introduce shared mutable state?

## 7. UBS (Ultimate Bug Scanner) prompts

Before commit, run mental/scripted UBS over the diff. Flag:

- [ ] Any `unwrap()` / `as any` / `ignore` added
- [ ] Any `catch { }` / bare `except:`
- [ ] Any feature-flag / env-var branching added
- [ ] Any deleted test cases
- [ ] Any dependency pin moved

## 8. Commit plan

- Commit 1: `refactor(<area>): extract <name>` (one lever only — no drive-by fixes)
- Verify: `./scripts/verify_isomorphism.sh <run-id>`
- Ledger row: `./scripts/ledger_row.sh <run-id> <id>`
