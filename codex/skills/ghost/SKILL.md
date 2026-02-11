---
name: ghost
description: Create a language-agnostic ghost-library package from an existing library repo by extracting SPEC.md, exhaustive tests.yaml, INSTALL.md, README.md, VERIFY.md, and upstream LICENSE files with provenance and regeneration instructions. Use when prompts say "$ghost", "ghostify this repo", "spec-ify/spec-package this library", "ghost library", or ask to extract portable spec/tests from source tests; do not use for implementation work or editing skills.
---

# ghost

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

## Hard rules (MUST / MUST NOT)
- MUST treat upstream tests as authoritative; if docs/examples disagree, prefer tests and record the discrepancy.
- MUST normalize nondeterminism into explicit inputs/outputs (no implicit "now", random seeds, locale surprises, unordered iteration).
- MUST keep the ghost repo language-agnostic: ship no implementation code, adapter runner, or build tooling.
- MUST paraphrase upstream docs; do not copy text verbatim.
- MUST preserve upstream license files verbatim as `LICENSE*`.
- MUST produce a verification signal and document it in `VERIFY.md` (adapter runner preferred; sampling fallback allowed).
- MUST document provenance and regeneration in `VERIFY.md` (upstream repo + revision, how artifacts were produced, and how to rerun verification).
- MUST choose a `tests.yaml` contract shape that matches the API style (functional vs protocol/CLI) and keep it consistent across `SPEC.md`, `INSTALL.md`, and `VERIFY.md`.
- MUST document the `tests.yaml` harness schema when it is non-trivial (callbacks, mutation steps, warnings, multi-step protocol setup, etc.).
  - Recommended artifact: `TESTS_SCHEMA.md`.
  - `INSTALL.md` MUST reference it when present.
- MUST minimize `skip` cases; only skip when deterministic setup is currently infeasible, and record why.
- MUST assert stable machine-interface fields explicitly (required keys, lengths/counts, and state effects), not only loose partial matches.
- MUST treat human-readable warning/error messages as unstable unless tests prove they are part of the public contract.
  - Prefer structured fields (codes) or substring assertions for message checks.

## Inputs
- Source repo path (git working tree)
- Output repo name/location (default: sibling directory `<repo-name>-ghost`)
- Upstream identity + revision (remote URL if available; tag/commit SHA)
- Public API surface if ambiguous (functions/classes/modules)
- Source language/runtime + how to run upstream tests
- Any required runtime assumptions (timezone, locale, units, encoding)

## Conventions

### Operation ids
`tests.yaml` organizes cases by **operation ids** (stable identifiers for public API entries). Use a naming scheme that survives translation across languages:
- `foo` (top-level function)
- `module.foo` (namespaced function)
- `Class#method` (instance method)
- `Class.method` (static/class method)

Avoid language-specific spellings in ids (e.g., avoid `snake_case` vs `camelCase` wars). Prefer the canonical name used by the source library’s docs.

### Contract shape
Pick one schema and stay consistent:
- **Functional API layout**: operation ids at top-level with `{name,input,output|error}` cases.
- **Protocol/CLI layout**: top-level `meta` + `operations`, where operation ids live under `operations` and cases include command/state assertions.

### `tests.yaml` version
`tests.yaml` MUST include a source version identifier that ties cases to upstream evidence.
- If the upstream library has a release version (SemVer/tag), use it.
- Otherwise, use an immutable source revision identifier (e.g., `git:<short-sha>` or `git describe`).
- Functional layout: use top-level `version`.
- Protocol/CLI layout: keep `meta.version` for test schema version and include `meta.source_version` for upstream evidence version.

## Workflow (tests-first)

### 0) Define scope and contract
- Write a one-line problem statement naming the upstream repo/revision and target ghost output path.
- Choose one `tests.yaml` layout (functional or protocol/CLI) and keep it consistent across `SPEC.md`, `INSTALL.md`, and `VERIFY.md`.
- Set success criteria: deterministic cases for every public operation and a recorded verification signal in `VERIFY.md`.

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
- If the API promises "copy"/"detached" behavior, harvest mutation-isolation evidence (including nested structure mutation, not just top-level fields).
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
- When an operation yields both a "prepared" value and a "persisted delta" (or similar), define the delta derivation mechanically (slice/filter/identity rules) and test it.
- Paraphrase source docs; do not copy text verbatim.
- Use `references/templates.md` for structure.

### 4) Generate `tests.yaml` (exhaustive)
- Convert each source test into a YAML case under its operation id.
- Include the source version identifier (`version` or `meta.source_version`).
- Schema is intentionally strict and portable; choose the contract shape from Conventions:
  - Functional layout:
    - each case has `name` and `input`
    - each case has exactly one of `output` or `error: true`
  - Protocol/CLI layout:
    - top-level `meta` + `operations`
    - each case has `name`, `input`, and deterministic expected outcomes (for example `exit_code`, machine-readable stdout assertions, and state assertions)
  - keep to a portable YAML subset (no anchors/tags/binary) so it is easy to parse in many languages
  - quote ambiguous scalars (`yes`, `no`, `on`, `off`, `null`) to avoid parser disagreements
- Normalize inputs to deterministic values (avoid "now"; use explicit timestamps).
- Keep or improve coverage across all public operations and failure modes.
- Prefer exact/value-complete assertions for stable output fields; use partial assertions only when fields are intentionally volatile.
- For warning/error message checks, prefer substring assertions unless the exact wording is itself part of the upstream contract.
- If `tests.yaml` includes harness directives beyond basic `{name,input,output|error}` (e.g. callbacks by label, mutation steps, warning sinks, setup scripts), document them in `TESTS_SCHEMA.md`.
- Keep `skip` rare; every skip must include a concrete reason and be accounted for in `VERIFY.md`.
- If the source returns floats, prefer defining stable rounding/formatting rules so `output` is exact.
- Follow the format in `references/templates.md`.

### 5) Add `INSTALL.md` + `README.md` + `VERIFY.md` + `LICENSE*`
- `INSTALL.md`: a short prompt for implementing the library in any language, referencing `SPEC.md` and `tests.yaml`.
- `README.md`: explain what the ghost library is, list operations, and describe the included files.
- `TESTS_SCHEMA.md` (when needed): define the `tests.yaml` harness schema and any callback catalogs or side-effect capture requirements.
- `VERIFY.md`: describe provenance + how the ghost artifacts were produced and verified against the source library (adapter-first; sampling fallback).
  - include upstream repo identity + exact revision (tag or commit)
  - include the exact commands used to produce each artifact (or a single deterministic regeneration recipe)
  - include the exact commands used to run verification and the resulting pass/skip counts
  - include any environment normalization assumptions
- `LICENSE*`: preserve the upstream repo’s license files verbatim.
  - copy common files like `LICENSE`, `LICENSE.md`, `COPYING*`
  - if no license file exists upstream, include a `LICENSE` file stating that no upstream license was found

### 6) Verify fidelity (must do)
- Ensure `tests.yaml` parses and case counts match or exceed the source tests covering the public API.
- Ensure every operation id has at least one executable (non-`skip`) case unless infeasible, and list any exceptions in `VERIFY.md`.
- Preferred: create a temporary adapter runner in the source language to run `tests.yaml` against the existing library.
  - if the source language has weak YAML tooling, parse YAML externally and dispatch into the library via a tiny CLI/FFI shim
  - assert expected outcomes match exactly (outputs/errors for functional layout; exit/status/payload/state assertions for protocol layout)
  - delete the adapter afterward; do not ship it in the ghost repo
  - summarize how to run it (and results) in `VERIFY.md`
- If a full adapter is infeasible:
  - run a representative sample across all operation ids (typical + boundary + error)
  - document the limitation clearly in `VERIFY.md`
- Use `references/verification.md` for a checklist and `VERIFY.md` template.

## Reproducibility and regen policy
- The ghost repo must be reproducible: a future developer should be able to point at the upstream revision and rerun the extraction + verification.
- Do not add regeneration scripts as tracked files unless the user explicitly asks; put the recipe in `VERIFY.md` instead.

## Output
Produce only these artifacts in the ghost repo:
- `README.md`
- `SPEC.md`
- `tests.yaml`
- `TESTS_SCHEMA.md` (optional; include when tests.yaml has non-trivial harness semantics)
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
- Errors:
  - Functional layout: keep `tests.yaml` strict (`error: true` only); in a Zig adapter, treat "any error return" as a passing error case and rely on `SPEC.md` for exact conditions.
  - Protocol/CLI layout: prefer explicit machine-readable error payload assertions plus exit codes.
- YAML tooling: Zig stdlib has JSON but not YAML; for adapters/implementations it’s fine to convert `tests.yaml` to JSON (or JSONL) as an intermediate and have a Zig runner parse it via `std.json`.

## Resources
- `references/templates.md` (artifact outlines and YAML format)
- `references/verification.md` (verification checklist + `VERIFY.md` template)
