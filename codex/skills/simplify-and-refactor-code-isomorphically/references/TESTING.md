# Testing — how to prove a refactor is isomorphic

> The isomorphism card claims behavior is unchanged. Tests *prove* it. This
> file is the how-to.

## Contents

1. [The four proof layers](#the-four-proof-layers)
2. [Layer 1 — unit tests](#layer-1--unit-tests)
3. [Layer 2 — golden-output tests](#layer-2--golden-output-tests)
4. [Layer 3 — property tests](#layer-3--property-tests)
5. [Layer 4 — production-traffic replay](#layer-4--production-traffic-replay)
6. [What NOT to test against](#what-not-to-test-against)
7. [Flaky tests during a pass](#flaky-tests-during-a-pass)
8. [Modifying test assertions — the rule](#modifying-test-assertions--the-rule)
9. [Sibling-skill handoffs](#sibling-skill-handoffs)

---

## The four proof layers

From cheapest to most-expensive, in the order you add them:

1. **Unit tests** — every collapsed site should already have them; the refactor
   must keep them passing without modifying assertions.
2. **Golden-output tests** — deterministic I/O fixtures. Capture once per
   pass; diffs must be byte-identical after a collapse.
3. **Property tests** — for Type-IV semantic collapses and type-shrinks, express
   the contract as an invariant and run 1k+ inputs against it.
4. **Production-traffic replay** — for high-risk collapses that span a
   perf or security boundary, replay a sanitized window of real traffic
   through before/after binaries and diff responses.

You don't need all four on every candidate. Small Type-I / Type-II collapses
with strong unit coverage can ship on layer 1. The higher the score risk, the
more layers you add.

## Layer 1 — unit tests

Baseline the output **before** any edit:

```bash
# Rust
cargo test --no-fail-fast 2>&1 | tee refactor/artifacts/<run>/tests_before.txt

# Python
pytest -q --tb=short 2>&1 | tee refactor/artifacts/<run>/tests_before.txt

# Node
npm test --silent 2>&1 | tee refactor/artifacts/<run>/tests_before.txt

# Go
go test ./... 2>&1 | tee refactor/artifacts/<run>/tests_before.txt
```

After each commit, re-run and diff the result file. **Acceptance criterion:**
exactly the same pass-count and exactly the same set of failing tests (by name).
A refactor must not silently "fix" a previously-failing test — that's a
behavior change, even if it looks like an improvement. File a separate bead.

## Layer 2 — golden-output tests

For anything with a deterministic I/O boundary (CLI, codegen, serializer,
template renderer), goldens are the cheapest high-coverage proof.

Capture goldens once per run:

```bash
./scripts/baseline.sh <run-id>
# writes refactor/artifacts/<run-id>/goldens/ with input/output pairs
```

After a commit, diff:

```bash
./scripts/verify_isomorphism.sh <run-id>
# fails loudly on any byte difference
```

Rules:

- Goldens must be deterministic. No timestamps, no nondeterministic ordering,
  no random IDs. Sanitize at capture time.
- Inputs should cover every branch of the code being collapsed. Aim for the
  minimum set of inputs that gives full branch coverage.
- Never edit a golden during a refactor. If the output changed, the refactor
  is not isomorphic — revert and reconsider.

## Layer 3 — property tests

Use [PROPERTY-TESTS.md](PROPERTY-TESTS.md) for full guidance. Skeleton:

```rust
#[proptest]
fn refactor_preserves_roundtrip(x: Input) {
    assert_eq!(old_fn(x.clone()), new_fn(x));
}
```

Run 1k+ random inputs via proptest / hypothesis / fast-check. The `new_fn` in
early commits can literally call the old implementation via a feature flag —
but per "one lever per commit," the feature flag itself is a separate commit
and must be removed before the pass closes.

## Layer 4 — production-traffic replay

For collapses that touch request handlers, data pipelines, or any hot path:

1. Capture a sanitized window of real traffic into a replay fixture.
2. Stand up `before` and `after` binaries against the same replay.
3. Diff responses, side effects, and latency histograms.

Any non-zero response diff aborts the commit. Latency regressions above a
threshold (often 2σ of baseline) also abort — see
[PERF-AWARE-REFACTOR.md](PERF-AWARE-REFACTOR.md).

## What NOT to test against

- **Logs** — log lines often change legitimately (function names in stack
  frames, refactored formatting). Only freeze log *shape* if the log is a
  documented contract.
- **Stack traces** — frame count changes legitimately.
- **Internal data structures** — the contract is the *public* behavior. A
  test reading the internal representation is a test of implementation, not
  behavior, and should be updated or deleted.
- **Timing** — timing tests are inherently flaky in refactor contexts. Move
  to perf-layer benchmarks.

## Flaky tests during a pass

Flaky tests are not isomorphism violations; they are prior tech debt that
makes the refactor unfalsifiable. Policy:

1. Do NOT start a pass with flaky tests. Mark them `#[ignore]` or equivalent,
   with a TODO linking the bead, and include the `#[ignore]` commit in the
   baseline. This is the ONE case where modifying test code is allowed inside
   a refactor pass — and it's still its own commit, separate from any collapse.
2. If a test becomes flaky mid-pass, pause. Find out whether the refactor
   caused it (via `git bisect`). If yes, revert the last commit. If no, quarantine
   the flake and continue.

## Modifying test assertions — the rule

**Never** during a refactor pass. The assertion IS the contract. If the
assertion is wrong, that's a separate bug-fix lever, committed separately.

Exception: if the assertion uses a fragile internal representation (see "What
NOT to test against"), rewriting it to assert on public behavior is a
legitimate pre-refactor cleanup. Commit it separately, before the refactor,
and include the before/after in the isomorphism card.

## Sibling-skill handoffs

- For gnarly property-test design: hand off to [PROPERTY-TESTS.md](PROPERTY-TESTS.md).
- For end-to-end testing across services: use [e2e-testing-for-webapps](../../e2e-testing-for-webapps/SKILL.md).
- For "is this test any good" evaluation: use [ubs](../../ubs/SKILL.md)
  to run UBS over the test file.
- For CI wiring that makes goldens a blocking gate: use
  [gh-actions](../../gh-actions/SKILL.md).
