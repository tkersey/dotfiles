---
name: re
description: Create a ghost-library repo from an existing library git repo by extracting a strict SPEC.md, exhaustive tests.yaml, INSTALL.md, README.md, VERIFY.md, and preserving upstream LICENSE files. Use only when a user explicitly asks to ghostify/spec-ify a repo, extract language-agnostic specs/tests, or invokes $re / "re" / "ghost library" / "spec package" for a codebase.
---

# re

## Overview
Generate a ghost-library package (spec + tests + install prompt) from an existing library repo (in any source language).

Preserve behavior, not prose:
- `tests.yaml` is the behavior contract
- source tests are the primary evidence
- code/docs/examples only fill gaps (never contradict tests)

The output is language-agnostic so the library can be implemented in any target language.

## Fit / limitations
This approach works best when the library’s behavior can be expressed as deterministic data:
- pure-ish operations (input -> output or error)
- a runnable test suite covering the public API

It gets harder (but is still possible) when the contract depends on time, randomness, IO, concurrency, global state, or platform details. In those cases, make assumptions explicit in `SPEC.md` + `VERIFY.md`, and normalize nondeterminism into explicit inputs/outputs.

## Inputs
- Source repo path (git working tree)
- Output repo name/location (default: sibling directory `<repo-name>-ghost`)
- Public API surface if ambiguous (functions/classes/modules)
- Source language/runtime + how to run upstream tests
- Any required runtime assumptions (timezone, locale, units, encoding)

## Conventions

### Operation ids
`tests.yaml` keys are **operation ids** (stable identifiers for public API entries). Use a naming scheme that survives translation across languages:
- `foo` (top-level function)
- `module.foo` (namespaced function)
- `Class#method` (instance method)
- `Class.method` (static/class method)

Avoid language-specific spellings in ids (e.g., avoid `snake_case` vs `camelCase` wars). Prefer the canonical name used by the source library’s docs.

## Workflow (tests-first)

### 1) Scope the source
- Locate the test suite(s), examples, and primary docs (README, API docs, docs site).
- Identify the **public API** and map each public operation to an operation id.
- Use export/visibility cues to confirm what’s public:
  - JS/TS: package entrypoints + exports/re-exports
  - Python: top-level module + `__all__`
  - Rust: `pub` items re-exported from `lib.rs`
  - Zig: `build.zig` module graph (`root_source_file`, `addModule`, `pub usingnamespace`) is source of truth; defaults are often `src/root.zig` (library) and `src/main.zig` (exe) but repos vary; treat C ABI `export` as public only if documented
  - C/C++: installed public headers + exported symbols; include macros/constants only if documented as API
  - Go: exported identifiers (Capitalized)
  - Java/C#: `public` types/members in the target package/namespace
  - Other: use the language’s visibility/export mechanism + published package entrypoints
- Confirm which functions/classes are *in* scope:
  - public API + tests covering it
  - exclude internal helpers unless tests prove they are part of the contract
- Decide the output directory as a new sibling repo unless the user overrides.

### 2) Harvest behavior evidence
- Extract test cases and expected outputs; treat tests as authoritative.
- When tests are silent, read code/docs to infer behavior and record the inference.
- Note all boundary values, rounding rules, encoding rules, and error cases.
- Normalize environment assumptions:
  - eliminate dependency on current time (use explicit timestamps)
  - force timezone/locale rules if relevant
  - remove nondeterminism (random seeds, unordered iteration)

### 3) Write `SPEC.md` (strict, language-agnostic)
- Describe types abstractly (number/string/object/timestamp/bytes/etc.).
- For bytes/buffers, define a canonical encoding (hex or base64) and use it consistently in `tests.yaml`.
- Define normalization rules (e.g., timestamp parsing, string trimming, unicode, case folding).
- Specify error behavior precisely (conditions), but keep the *mechanism* language-idiomatic.
- Specify every public operation with inputs, outputs, rules, and edge cases.
- Paraphrase source docs; do not copy text verbatim.
- Use `references/templates.md` for structure.

### 4) Generate `tests.yaml` (exhaustive)
- Convert each source test into a YAML case under its operation id.
- Schema is intentionally strict (modeled after `whenwords`):
  - each case has `name` and `input`
  - each case has exactly one of `output` or `error: true`
  - keep to a portable YAML subset (no anchors/tags/binary), so it’s easy to parse in many languages
- Normalize inputs to deterministic values (avoid “now”; use explicit timestamps).
- Keep or improve coverage across all public operations and failure modes.
- If the source returns floats, prefer defining stable rounding/formatting rules so `output` is exact.
- Follow the format in `references/templates.md`.

### 5) Add `INSTALL.md` + `README.md` + `VERIFY.md` + `LICENSE*`
- `INSTALL.md`: a short prompt for implementing the library in any language, referencing `SPEC.md` and `tests.yaml`.
- `README.md`: explain what the ghost library is, list operations, and describe the included files.
- `VERIFY.md`: describe how the ghost artifacts were verified against the source library (adapter-first; sampling fallback).
- `LICENSE*`: preserve the upstream repo’s license files verbatim.
  - copy common files like `LICENSE`, `LICENSE.md`, `COPYING*`
  - if no license file exists upstream, include a `LICENSE` file stating that no upstream license was found

### 6) Verify fidelity (must do)
- Ensure `tests.yaml` parses and case counts match or exceed the source tests covering the public API.
- Preferred: create a temporary adapter runner in the source language to run `tests.yaml` against the existing library.
  - if the source language has weak YAML tooling, parse YAML externally and dispatch into the library via a tiny CLI/FFI shim
  - assert outputs/errors match exactly
  - delete the adapter afterward; do not ship it in the ghost repo
  - summarize how to run it (and results) in `VERIFY.md`
- If a full adapter is infeasible:
  - run a representative sample across all operation ids (typical + boundary + error)
  - document the limitation clearly in `VERIFY.md`
- Use `references/verification.md` for a checklist and `VERIFY.md` template.

## Output
Produce only these artifacts in the ghost repo:
- `README.md`
- `SPEC.md`
- `tests.yaml`
- `INSTALL.md`
- `VERIFY.md`
- `LICENSE*` (copied from upstream)
- `.gitignore` (optional, minimal)

## Notes
- Prefer precision over verbosity; rules should be unambiguous and testable.
- Keep the ghost repo free of implementation code and packaging scaffolding.

## Zig notes
- Running upstream tests: prefer `zig build test` (if `build.zig` defines tests); otherwise `zig test path/to/file.zig` for the library root and any test entrypoints.
- Operation ids for methods: treat a first parameter named `self` of type `T`/`*T` as an instance method (`T#method`); otherwise use `T.method`.
- `comptime` parameters: record allowed values in `SPEC.md`, and represent them as ordinary fields in `tests.yaml` inputs.
- Allocators/buffers: if the API takes `std.mem.Allocator` or caller-provided buffers, specify ownership and mutation rules; assume allocations succeed unless tests cover OOM.
- Errors: keep `tests.yaml` strict (`error: true` only); in a Zig adapter, treat “any error return” as a passing error case, and rely on `SPEC.md` to pin the exact error conditions.
- YAML tooling: Zig stdlib has JSON but not YAML; for adapters/implementations it’s fine to convert `tests.yaml` to JSON (or JSONL) as an intermediate and have a Zig runner parse it via `std.json`.

## Resources
- `references/templates.md` (artifact outlines and YAML format)
- `references/verification.md` (verification checklist + `VERIFY.md` template)
