---
name: ghost
description: "Create a language-agnostic Ghost package from an existing repository: SPEC.md, tests.yaml, INSTALL.md, README.md, VERIFY.md, and license/provenance material. Preserve behavior from tests and captured traces, normalize nondeterminism, and prove the portable contract through adapter evidence. Use $lean only when formal assurance is explicitly requested. Not for implementation or skill edits."
---
# Ghost

## Mission

Extract a portable behavior contract that can be reimplemented in another
language or harness without copying the source implementation.

`tests.yaml` is the executable behavior contract. Source tests and captured
traces outrank prose, examples, and inferred intent.

## Common path

1. Bind the upstream repository and immutable revision.
2. Identify the public operations or primary scenarios.
3. Choose one consistent contract shape:
   `functional`, `protocol/CLI`, or `scenario`.
4. Normalize time, randomness, locale, ordering, I/O, and other hidden inputs
   into explicit contract data.
5. Produce:
   - `SPEC.md`;
   - exhaustive or explicitly sampled `tests.yaml`;
   - `INSTALL.md`;
   - `README.md`;
   - `VERIFY.md`;
   - preserved upstream `LICENSE*`;
   - an evidence bundle that maps public surfaces and case IDs.
6. For stateful behavior, include lifecycle, transition, recovery/idempotency,
   and end-to-end workflow cases.
7. Prefer state and trace oracles over brittle final-text matching.
8. Verify mapping completeness, baseline pass evidence, mutation sensitivity,
   and independent regeneration parity.
9. Record provenance, limitations, and the exact regeneration procedure.

The Ghost package contains no target implementation, adapter runner, or build
system.

## Contract invariants

- Upstream evidence wins over documentation.
- Every executable case has a stable identity across contract and evidence.
- Unsupported or skipped cases are explicit; exhaustive mode means all required
  cases execute and pass.
- Human-readable messages are non-contractual unless evidence proves otherwise.
- Stochastic agent behavior is graded by reliability and invariant-free runs,
  not exact text.
- No claim exceeds the verified boundary.

## Conditional disclosure

The complete pre-split contract is preserved byte-for-byte in
[FULL_CONTRACT.md](FULL_CONTRACT.md). Do not load it for ordinary deterministic
library extraction.

Load it when any of these routes is live:

- layered or interface-heavy agentic extraction;
- full evidence-bundle schemas and strict verifier mechanics;
- conformance profiles or production integration profiles;
- sampled-coverage exception handling;
- scenario mutation and trace-invariant catalogs;
- Lean-aided formal model, theorem, trust, or workbench requirements;
- an unported edge route.

When formal assurance is requested, `$ghost` remains artifact authority and
`$lean` owns Lean-specific modeling and proof. Lean normally proves the Ghost
model, not the upstream implementation.

Its frontmatter is archived source, not a second skill definition.

## Guardrails

- Do not copy upstream documentation verbatim except license files.
- Do not fill evidence gaps with invented behavior.
- Do not call extraction complete with isolated cases but no primary workflow
  coverage.
- Do not claim the upstream implementation is formally proved without a checked
  refinement link.
