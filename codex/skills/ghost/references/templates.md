# Ghost Library Artifact Templates

Ghost libraries ship specifications and tests, not implementation code.

## SPEC.md (outline)
- Title + version
- Overview (what the library does)
- Design principles (deterministic, pure, etc.)
- Type conventions (abstract types and normalization rules)
- Error handling (language-idiomatic, exact error conditions)
- Operations (public API)
  - Operation id
  - Signature
  - Arguments and options
  - Behavior rules and thresholds
  - Edge cases
  - Examples (short, non-exhaustive)
- Testing section (reference tests.yaml format)

## TESTS_SCHEMA.md (outline, optional)

Include this file when `tests.yaml` contains harness semantics that are not obvious from `{name,input,output|error}` alone.

Minimum contents:
- Top-level `tests.yaml` layout (functional vs protocol/CLI)
- Any custom fields used in cases (mutation directives, setup steps, capture variables)
- Callback catalog (if callbacks are referenced by label)
- Side-effect capture requirements (warnings/logs)
- Output assertion semantics (deep equality vs partial/contains)

## tests.yaml (format)

Choose one layout and keep it consistent with `SPEC.md`.

### A) Functional API layout

```yaml
version: "X.Y.Z"  # upstream library version or revision (opaque string)

operation_id:
  - name: "human-readable case"
    input: { ... }  # may also be a scalar/sequence for single-arg operations
    output: ...
  - name: "error case"
    input: { ... }
    error: true
```

### B) Protocol/CLI layout

```yaml
meta:
  protocol: "library-protocol-name"
  version: 1               # test schema version
  source_version: "X.Y.Z"  # upstream library version or revision
  defaults:
    env:
      TZ: UTC
      LC_ALL: C
      LANG: C
    args: ["--json"]

operations:
  cli.op_id:
    - name: "happy path"
      input:
        setup:
          - command: ["init"]
            capture:
              issue_id: "$.id"
        command: ["show", "${issue_id}"]
      output:
        exit_code: 0
        stdout_json_contains:
          id: "${issue_id}"
    - name: "error path"
      input:
        command: ["show", "missing"]
      output:
        exit_code: 1
        stdout_json_contains:
          code: "NOT_FOUND"
```

### Operation ids
- Use stable ids that map cleanly across languages:
  - `foo` (top-level function)
  - `module.foo` (namespaced function)
  - `Class#method` (instance method)
  - `Class.method` (static/class method)

Notes:
- Functional layout: `version` identifies upstream evidence version (SemVer/tag if available; otherwise `git:<short-sha>`).
- Protocol/CLI layout: keep `meta.version` for schema version and use `meta.source_version` for upstream evidence version.
- Use explicit timestamps/values; avoid "now" or system state.
- Inputs must be deterministic and YAML-serializable (scalars, sequences, maps).
- For bytes/buffers, encode as hex or base64 string (document which in `SPEC.md`).
- Avoid YAML-only features (anchors, tags, custom types); quote ambiguous scalars (`yes`, `no`, `on`, `off`, `null`).
- Functional layout: `output` and `error` are mutually exclusive; represent errors with `error: true` only.
- Protocol/CLI layout: assert deterministic outcomes (`exit_code`, machine-readable payload checks, and optional state assertions).
- If a case is skipped, include `skip: "<reason>"` and account for it in `VERIFY.md`.
- For stateful workflows, add multi-step loop scenarios (for example create -> act -> follow-up) and assert continuity fields across steps (ids, chain pointers, persisted context/history).
- Do not rely on operation-isolated cases alone when the public behavior is workflow-driven.

## INSTALL.md (outline)
- Short intro: "This is a ghost library; implement locally"
- Steps:
  1. Read SPEC.md
  2. Parse tests.yaml; generate tests in your language
  3. Implement operations
  4. Run tests until green
  5. Place implementation in target location
- Reminder: all tests.yaml cases must pass

## VERIFY.md (outline)
- Verification policy: adapter-first, sampling fallback
- Source-language adapter runner (preferred)
  - How to run it locally
  - What it asserts (outputs/errors match tests.yaml)
- Sampling fallback (if adapter infeasible)
  - What was sampled and why
  - Known gaps / unverified areas
- Evidence bundle verifier (fail-closed)
  - `verification/evidence/` is present and complete
  - `uv run python scripts/verify_evidence.py --bundle verification/evidence` passes
- Traceability matrix
  - operation/workflow -> case ids -> proof artifact -> adapter run id
- Adapter run ledger
  - run id, mode, command, timestamp, result
- Workflow loop inventory
  - workflow id, cases, continuity assertions, reset assertions (when required)
- Mutation sensitivity gate
  - required mutations, detected failures, pass/fail
- Independent regeneration parity
  - two runs, normalized artifact diff count, pass/fail
- Test inventory (optional)
  - Case counts per operation id

## verification/evidence/ (required files)
- `inventory.json`
  - `public_operations`: list of operation ids
  - `primary_workflows`: list of workflow objects `{id, requires_reset}`
- `traceability.csv`
  - columns: `target_type,target_id,case_id,proof_artifact,adapter_run_id`
- `workflow_loops.json`
  - `workflows`: list of `{id,cases,continuity_assertions,reset_assertions}`
- `adapter_results.jsonl`
  - one JSON object per case execution with `run_id`, `case_id`, `status`, optional `mutated`
- `mutation_check.json`
  - `{required_mutations, detected_failures, pass}`
- `parity.json`
  - `{pass, diff_count, run_a, run_b}`

## README.md (outline)
- One-paragraph description of the ghost library concept
- Operation list with one-line descriptions
- Files included in the repo (SPEC.md, tests.yaml, TESTS_SCHEMA.md when present, INSTALL.md, VERIFY.md, LICENSE*)
- Quick start: point to INSTALL.md

## LICENSE* (guidance)
- Copy the upstream repo's license files verbatim (e.g. `LICENSE`, `LICENSE.md`, `COPYING*`).
- If no license file exists upstream, include a `LICENSE` file stating that no upstream license was found.
