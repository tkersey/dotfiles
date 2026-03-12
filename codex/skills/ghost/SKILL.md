---
name: ghost
description: Create a language-agnostic ghost package (spec + portable tests) from an existing repo by extracting SPEC.md, exhaustive tests.yaml (operations and/or scenarios), INSTALL.md, README.md, VERIFY.md, and upstream LICENSE files with provenance and regeneration instructions. Use when prompts say "$ghost", "ghostify this repo", "spec-ify/spec-package this library", "ghost library", or ask to extract portable spec/tests for libraries or tool-using agent loops (scenario testing); do not use for implementation work or editing skills.
---

# ghost

## Overview
Generate a ghost package (spec + tests + install prompt) from an existing repo.

Preserve behavior, not prose:
- `tests.yaml` is the behavior contract (operation cases and/or scenarios)
- source tests and/or captured traces are the primary evidence
- code/docs/examples only fill gaps (never contradict evidence)

The output is language-agnostic so it can be implemented in any target language or harness.

Scenario testing frame (for agentic systems / tool loops):
- **Given** an initial world state + tool surface + user goal
- **When** the agent runs under realistic constraints and noise
- **Then** it reaches an acceptable outcome without violating invariants (safety, security, cost, latency, policy)

## Fit / limitations
This approach works best when the system’s behavior can be expressed as deterministic data:
- pure-ish operations (input -> output or error)
- a runnable test suite covering the public API

It also works for **agentic systems** when behavior can be expressed as controlled, replayable scenarios:
- a tool sandbox (stubs/record-replay/simulator)
- machine-checkable oracles (state assertions + trace invariants)
- a deterministic debug mode plus a production-like reliability mode (pass rates)

It also works for **layered interface-heavy agentic systems** when the source exposes named runtime seams that must survive extraction:
- explicit interfaces or registries (handlers, provider profiles, adapters, execution environments, extension points)
- persisted runtime artifacts with contract significance (events, checkpoints, status files, ledgers)
- normative acceptance or definition-of-done sections that can be tied to executable cases

It gets harder (but is still possible) when the contract depends on time, randomness, IO, concurrency, global state, or platform details. In those cases, make assumptions explicit in `SPEC.md` + `VERIFY.md`, and normalize nondeterminism into explicit inputs/outputs.

## Hard rules (MUST / MUST NOT)
- MUST treat upstream tests (and for agentic systems: captured traces/eval runs) as authoritative; if docs/examples disagree, prefer evidence and record the discrepancy.
- MUST normalize nondeterminism in the environment/tool surface into explicit inputs/outputs (no implicit "now", random seeds, locale surprises, unordered iteration).
- MUST make model/agent stochasticity explicit and test it as **reliability**: gate on pass rates + invariant-violation-free runs (not exact-text goldens).
- MUST keep the ghost repo language-agnostic: ship no implementation code, adapter runner, or build tooling.
- MUST paraphrase upstream docs; do not copy text verbatim.
- MUST preserve upstream license files verbatim as `LICENSE*`.
- MUST produce a verification signal and document it in `VERIFY.md` (adapter runner preferred; sampling fallback allowed).
- MUST document provenance and regeneration in `VERIFY.md` (upstream repo + revision, how artifacts were produced, and how to rerun verification).
- MUST choose a `tests.yaml` contract shape that matches the system style (functional API vs protocol/CLI vs scenario) and keep it consistent across `SPEC.md`, `INSTALL.md`, and `VERIFY.md`.
- MUST document the `tests.yaml` harness schema when it is non-trivial (callbacks, mutation steps, warnings, multi-step protocol setup, etc.).
  - Recommended artifact: `TESTS_SCHEMA.md`.
  - `INSTALL.md` MUST reference it when present.
- MUST minimize `skip` cases; only skip when deterministic setup is currently infeasible, and record why.
- MUST assert stable machine-interface fields explicitly (required keys, lengths/counts, and state effects), not only loose partial matches.
- MUST treat human-readable warning/error messages as unstable unless tests prove they are part of the public contract.
  - Prefer structured fields (codes) or substring assertions for message checks.
- MUST capture cross-operation state transitions when behavior depends on prior calls (for example session, instance, history, or tool-loop continuity).
- MUST include executable end-to-end loop coverage for each primary stateful workflow (for example create -> act -> persist -> follow-up) with explicit pre/post state assertions.
- MUST treat a stateful workflow as incomplete if only isolated operation cases exist; add scenario coverage in `tests.yaml` and verification proof before calling extraction done.
- MUST include trace-level invariants for agentic scenarios (for example permission boundaries, confirmation-before-side-effects, injection resistance, budget/step limits).
- MUST prefer oracles that score behavior via state + trace (tool calls, side effects) over brittle final-text matching.
- MUST produce a machine-checkable evidence bundle under `verification/evidence/` and fail extraction unless it passes `uv run --with pyyaml -- python scripts/verify_evidence.py --bundle <ghost-repo>/verification/evidence`.
- MUST keep `verification/evidence/inventory.json` synchronized with `tests.yaml`: `public_operations` must match non-workflow operation ids and `primary_workflows` must match workflow/scenario ids (`coverage_mode` defaults to `exhaustive`; when `sampled`, include `sampled_case_ids`).
- MUST ensure every required case id appears in `traceability.csv` and has at least one baseline (`mutated=false`) `pass` row in `adapter_results.jsonl` (all `tests.yaml` cases for `exhaustive`; `inventory.json.sampled_case_ids` for `sampled`).
- MUST enforce fail-closed verification thresholds: 100% mapped public operations, 100% mapped primary workflows, and 100% mapped required case ids (all tests for `exhaustive`; sampled ids for `sampled`), plus mutation sensitivity and independent regeneration parity passes.
- MUST declare verification coverage mode in `VERIFY.md`: default `exhaustive`; `sampled` is allowed only when full adapter execution is infeasible and must list sampled case ids plus rationale (including `inventory.json.sampled_case_ids`).
- MUST treat `coverage_mode=exhaustive` as "all required cases execute and pass"; if a case cannot run, move to `coverage_mode=sampled` with explicit `sampled_case_ids` or remove it from the required set instead of leaving it as an unresolved skip.
- MUST define and enforce conformance profiles in generated artifacts: `Core Conformance`, `Extension Conformance`, and `Real Integration Profile`.
- MUST include `Conformance Profile`, `Validation Matrix`, and `Definition of Done` sections in `SPEC.md`.
- MUST include `Summary`, `Regenerate`, `Validation Matrix`, `Traceability Matrix`, `Mutation Sensitivity`, `Regeneration Parity`, and `Limitations` sections in `VERIFY.md`.
- MUST include typed failure classes for extraction/verification failures (for example missing artifacts, parse failures, and contract mismatches).
- MUST require stateful/scenario ghost specs to include lifecycle structure sections in `SPEC.md`: `State Model`, `Transition Triggers`, `Recovery/Idempotency`, and `Reference Algorithm`.
- MUST classify a source as `layered_agentic` when the public contract materially depends on named runtime seams such as provider-specific interfaces, extension registries, execution environments, event surfaces, or persisted artifact contracts.
- MUST require `verification/evidence/inventory.json.contract_class=layered_agentic` for those extractions and keep `default` behavior unchanged for ordinary ghost packages.
- MUST require `layered_agentic` extractions to produce `verification/evidence/interface_inventory.json` and `verification/evidence/contract_traceability.csv`.
- MUST require `layered_agentic` extractions to map named surfaces, boundary invariants, and persisted artifact contracts to explicit `case_id` values; generated fallback case ids are not sufficient in this mode.
- MUST run the evidence verifier in strict mode by default; legacy bypass is break-glass only (`--legacy-allow --legacy-reason "<rationale>"`) and never default.

## Conformance profiles (required)
- `Core Conformance`:
  - deterministic contract extraction requirements that every ghost package must satisfy
  - strict evidence gates and fail-closed verification
- `Extension Conformance`:
  - optional behaviors implemented by an extraction for stronger fidelity or ergonomics
  - must be explicitly labeled as optional and tested if claimed
- `Real Integration Profile`:
  - environment-dependent checks that validate production-like behavior
  - may be skipped only with explicit rationale in `VERIFY.md`

Profile usage rules:
- `SPEC.md` and `VERIFY.md` must state which profile each validation requirement belongs to.
- `Validation Matrix` and `Definition of Done` must align with the selected profile labels.
- Stateful/scenario workflows must include lifecycle sections regardless of profile.

## Inputs
- Source repo path (git working tree)
- Output repo name/location (default: sibling directory `<repo-name>-ghost`)
- Upstream identity + revision (remote URL if available; tag/commit SHA)
- Public surface if ambiguous:
  - library: functions/classes/modules
  - agentic system: tool names/schemas, permissions, and side-effect boundaries
- Source language/runtime + how to run upstream tests
- Any required runtime assumptions (timezone, locale, units, encoding)

For scenario-heavy (agentic) extractions, also collect:
- scenario catalog (top user goals + failure modes)
- tool error/latency behaviors (timeouts, 500s, malformed payloads)
- explicit invariants (security, safety, cost, latency, policy)

For `layered_agentic` extractions, also collect:
- normative source sections (which sections are binding vs explanatory)
- named interface surfaces and extension points
- provider-specific boundary rules that must stay explicit
- persisted artifact contracts (for example checkpoints, event payloads, status files)

## Conventions

### Operation ids
`tests.yaml` organizes cases by **operation ids** (stable identifiers for public API entries). Use a naming scheme that survives translation across languages:
- `foo` (top-level function)
- `module.foo` (namespaced function)
- `Class#method` (instance method)
- `Class.method` (static/class method)

Avoid language-specific spellings in ids (e.g., avoid `snake_case` vs `camelCase` wars). Prefer the canonical name used by the source library’s docs.

For agentic scenario suites, operation ids SHOULD match tool names as the agent sees them (e.g. `orders.lookup`, `tickets.create`).

### Scenario ids
When using scenario testing, keep **scenario ids** stable and descriptive:
- `refund.create_ticket_with_guardrails`
- `calendar.reschedule_with_rate_limit`
- `security.prompt_injection_from_tool_output`

### Case ids
Every executable case SHOULD carry a stable `case_id` and use it as the primary key across evidence artifacts.
- Prefer `<operation-id>.<behavior>` for operation cases.
- For single-case workflow/scenario targets, reusing the workflow/scenario id as `case_id` is acceptable.
- `traceability.csv` and `adapter_results.jsonl` MUST use the same `case_id` tokens.
- `layered_agentic` extractions MUST provide explicit `case_id` on every executable case.

### Contract shape
Pick one schema and stay consistent:
- **Functional API layout**: operation ids at top-level with `{name,input,output|error}` cases.
- **Protocol/CLI layout**: top-level `meta` + `operations`, where operation ids live under `operations` and cases include command/state assertions.
- **Scenario layout (agentic systems)**: top-level `meta` + `scenarios`, where scenario ids live under `scenarios` and each scenario defines environment + tools + goal + oracles.

### `tests.yaml` version
`tests.yaml` MUST include a source version identifier that ties cases to upstream evidence.
- If the upstream library has a release version (SemVer/tag), use it.
- Otherwise, use an immutable source revision identifier (e.g., `git:<short-sha>` or `git describe`).
- Functional layout: use top-level `version`.
- Protocol/CLI layout: keep `meta.version` for test schema version and include `meta.source_version` for upstream evidence version.
- Scenario layout: keep `meta.version` for schema version and include `meta.source_version` for upstream evidence version.

## Workflow (tests-first)

### 0) Define scope and contract
- Write a one-line problem statement naming the upstream repo/revision and target ghost output path.
- Choose one `tests.yaml` layout (functional, protocol/CLI, or scenario) and keep it consistent across `SPEC.md`, `INSTALL.md`, and `VERIFY.md`.
- Set success criteria: deterministic cases for every public operation, executable loop coverage for primary stateful workflows, and a recorded verification signal in `VERIFY.md`.

For agentic systems, define success criteria as:
- critical scenarios expressed in a controlled tool sandbox
- hard oracles + trace-level invariants (no critical violations)
- reliability gates (pass rate thresholds) for production-like runs

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
- Identify primary user-facing workflows (especially stateful loops) and map each workflow to required operation sequences and state boundaries.

For agentic systems:
- Identify the tool surface (names, schemas, permissions, rate limits).
- Identify the environment/state (what changes when tools are called).
- Identify invariants (safety/security/cost/latency/policy) that must hold across the full trace.
- Build a coverage matrix (functional, robustness, safety/security/abuse, cost/latency).
- Decide the output directory as a new sibling repo unless the user overrides.

For `layered_agentic` systems:
- Classify the run as `contract_class=layered_agentic` only when the contract materially depends on named interfaces, extension seams, or persisted artifacts.
- Inventory each named surface as one of: `interface`, `provider_edge`, `extension_point`, `event_surface`, or `artifact_boundary`.
- Record which source sections are normative enough to cite as the contract of each surface or invariant.

### 2) Harvest behavior evidence
- Extract test cases and expected outputs (or scenario traces); treat evidence as authoritative.
- When tests are silent, read code/docs to infer behavior and record the inference.
- Note all boundary values, rounding rules, encoding rules, and error cases.
- If the API promises "copy"/"detached" behavior, harvest mutation-isolation evidence (including nested structure mutation, not just top-level fields).
- For stateful APIs, harvest continuity evidence across steps (persisted ids, history chains, context/tool carry-forward, and reset semantics).
- Normalize environment assumptions:
  - eliminate dependency on current time (use explicit timestamps)
  - force timezone/locale rules if relevant
  - remove nondeterminism (random seeds, unordered iteration)

For scenario suites, also harvest:
- realistic tool failures (timeouts/500s/malformed JSON/partial results) and backoff/retry behavior
- prompt-injection-like tool outputs and required refusal/ignore behavior
- stop conditions (max steps, budget) and graceful halts

For `layered_agentic` suites, also harvest:
- cross-document boundary rules (which spec or test owns each seam)
- persisted artifact field contracts and lifecycle expectations
- provider-specific behaviors that must remain explicit rather than normalized away

### 3) Write `SPEC.md` (strict, language-agnostic)
- Include `Conformance Profile`, `Validation Matrix`, and `Definition of Done` sections.
- Describe types abstractly (number/string/object/timestamp/bytes/etc.).
- For bytes/buffers, define a canonical encoding (hex or base64) and use it consistently in `tests.yaml`.
- Define normalization rules (e.g., timestamp parsing, string trimming, unicode, case folding).
- Specify error behavior precisely (conditions), but keep the *mechanism* language-idiomatic.
- Include typed failure classes in the spec surface (machine-checkable failure names/codes where possible).
- Specify every public operation with inputs, outputs, rules, and edge cases.
- When an operation yields both a "prepared" value and a "persisted delta" (or similar), define the delta derivation mechanically (slice/filter/identity rules) and test it.
- Specify cross-operation invariants for primary workflows (state transitions, required ordering, and continuity guarantees).
- For scenarios, specify:
  - state model and transition triggers
  - recovery/idempotency behavior
  - reference algorithm overview (language-agnostic)
  - environment state model and reset semantics
  - tool surface contracts (schemas, permissions, rate limits)
  - invariants as explicit, testable rules (trace-level)
- For `layered_agentic` specs, also include:
  - `Interface Surfaces` with named surfaces, kinds, layers, and source references
  - `Boundary Contracts` describing the explicit cross-surface rules that implementations must preserve
  - `Extension Points` describing registries, hooks, or provider-specific seams that are part of the public contract
  - `Persistent Artifacts` describing contract-bearing files or event payloads and their required fields
- Paraphrase source docs; do not copy text verbatim.
- Use `references/templates.md` for structure.

### 4) Generate `tests.yaml` (exhaustive)
- Convert each source test into a YAML case under its operation id.
- Include the source version identifier (`version` or `meta.source_version`).
- Schema is intentionally strict and portable; choose the contract shape from Conventions:
  - Functional layout:
    - each case has `name`, `input`, and a stable `case_id` (recommended)
    - each case has exactly one of `output` or `error: true`
  - Protocol/CLI layout:
    - top-level `meta` + `operations`
    - each case has `case_id`, `name`, `input`, and deterministic expected outcomes (for example `exit_code`, machine-readable stdout assertions, and state assertions)
  - keep to a portable YAML subset (no anchors/tags/binary) so it is easy to parse in many languages
  - quote ambiguous scalars (`yes`, `no`, `on`, `off`, `null`) to avoid parser disagreements
- Normalize inputs to deterministic values (avoid "now"; use explicit timestamps).
- Keep or improve coverage across all public operations and failure modes.
- Add scenario cases for primary stateful workflows so the contract proves end-to-end loop behavior, not only per-operation correctness.
- For agentic systems, prefer the scenario layout and define each scenario as:
  - initial state (what the agent knows + world state)
  - tool sandbox (stubs/record-replay/simulator) and permissions
  - dynamics (how the world responds to tool calls, including failures/delays)
  - success criteria (final state and/or required tool side effects)
  - oracles (hard assertions + trace invariants; optional rubric judge)
- Prefer exact/value-complete assertions for stable output fields; use partial assertions only when fields are intentionally volatile.
- If assertions use path lookups, define path resolver semantics in `TESTS_SCHEMA.md` (root object, dot segments, `[index]` arrays, and "missing path fails assertion").
- For warning/error message checks, prefer substring assertions unless the exact wording is itself part of the upstream contract.
- If `tests.yaml` includes harness directives beyond basic `{name,input,output|error}` (e.g. callbacks by label, mutation steps, warning sinks, setup scripts), document them in `TESTS_SCHEMA.md`.
- Keep `skip` rare; every skip must include a concrete reason and be accounted for in `VERIFY.md`.
- If the extraction is `layered_agentic`, require explicit `case_id` on every executable case and map those ids into surface/invariant/artifact evidence; do not rely on verifier-generated fallback ids.
- If the source returns floats, prefer defining stable rounding/formatting rules so `output` is exact.
- Follow the format in `references/templates.md`.

### 5) Add `INSTALL.md` + `README.md` + `VERIFY.md` + `LICENSE*`
- `INSTALL.md`: a short prompt for implementing the library in any language, referencing `SPEC.md` and `tests.yaml`.
- `README.md`: explain what the ghost library is, list operations, and describe the included files.
- `TESTS_SCHEMA.md` (when needed): define the `tests.yaml` harness schema and any callback catalogs or side-effect capture requirements.
- `VERIFY.md`: describe provenance + how the ghost artifacts were produced and verified against the source library (adapter-first; sampling fallback).
  - include `Summary`, `Regenerate`, `Validation Matrix`, `Traceability Matrix`, `Mutation Sensitivity`, `Regeneration Parity`, and `Limitations` sections
  - for `layered_agentic` extractions, also include `Normative Source Map`, `Surface Coverage Matrix`, `Boundary Invariants`, and `Artifact Contract Coverage`
  - include upstream repo identity + exact revision (tag or commit)
  - include the exact commands used to produce each artifact (or a single deterministic regeneration recipe)
  - include the exact commands used to run verification and the resulting pass/skip counts
  - include any environment normalization assumptions
  - include a summary of `verification/evidence/` and the verifier command/result
  - if legacy verifier bypass is used, include explicit break-glass rationale and follow-up remediation plan
- `LICENSE*`: preserve the upstream repo’s license files verbatim.
  - copy common files like `LICENSE`, `LICENSE.md`, `COPYING*`
  - if no license file exists upstream, include a `LICENSE` file stating that no upstream license was found

### 6) Verify fidelity (must do)
- Ensure `tests.yaml` parses and case counts match or exceed the source tests covering the public API.
- Ensure every operation id has at least one executable (non-`skip`) case unless infeasible, and list any exceptions in `VERIFY.md`.
- Preferred: create a temporary adapter runner in the source language to run `tests.yaml` against the upstream system (library or agent).
  - if the source language has weak YAML tooling, parse YAML externally and dispatch into the library via a tiny CLI/FFI shim
  - assert expected outcomes match exactly (outputs/errors for functional layout; exit/status/payload/state assertions for protocol layout)
  - for stateful workflows, execute end-to-end loop scenarios and assert continuity/persistence effects across steps
  - delete the adapter afterward; do not ship it in the ghost repo
  - summarize how to run it (and results) in `VERIFY.md`
- Build a fail-closed evidence bundle in `verification/evidence/`:
  - `inventory.json` (public operations + primary workflows, including reset requirements; optional `coverage_mode`, and `sampled_case_ids` when `coverage_mode=sampled`; optional `contract_class=default|layered_agentic`, defaulting to `default`)
  - `traceability.csv` (operation/workflow -> case ids -> proof artifact -> adapter run id)
  - `workflow_loops.json` (loop cases + continuity assertions + reset assertions when required)
  - `adapter_results.jsonl` (case-level results with `run_id`, `case_id`, `status`, and mutation marker)
  - `mutation_check.json` (required mutation count + detected failures + pass/fail)
  - `parity.json` (independent regeneration parity verdict + diff count)
  - `interface_inventory.json` (`layered_agentic` only: `surfaces`, `boundary_invariants`, and `artifact_contracts`, each with `source_refs` and `required_case_ids`)
  - `contract_traceability.csv` (`layered_agentic` only: `target_type,target_id,case_id,proof_artifact,adapter_run_id`, where `target_type` is `surface|invariant|artifact`)
- Run `uv run --with pyyaml -- python scripts/verify_evidence.py --bundle <ghost-repo>/verification/evidence`; non-zero exit means extraction is incomplete.
- Strict mode is default and fail-closed. Use `--legacy-allow --legacy-reason "<rationale>"` only for explicit manual break-glass migrations.
- For stochastic agentic systems:
  - run scenarios in two modes:
    - deterministic debug mode (stable tool outputs; fixed seed when possible)
    - production-like mode (real sampling settings)
  - run each critical scenario N times and record pass rate + cost/latency distributions
  - release gates: **no critical invariant violations** and pass rate meets threshold
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
- `verification/evidence/inventory.json`
- `verification/evidence/traceability.csv`
- `verification/evidence/workflow_loops.json`
- `verification/evidence/adapter_results.jsonl`
- `verification/evidence/mutation_check.json`
- `verification/evidence/parity.json`
- `verification/evidence/interface_inventory.json` (`layered_agentic` only)
- `verification/evidence/contract_traceability.csv` (`layered_agentic` only)
- `verification/evidence/structure_contract.json` (optional, recommended for explicit structure policy)
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
