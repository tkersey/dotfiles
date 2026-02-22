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
- Assertion path semantics (root, dot segments, `[index]`, and missing-path behavior)

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
    - case_id: cli.op_id.happy_path
      name: "happy path"
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
    - case_id: cli.op_id.error_path
      name: "error path"
      input:
        command: ["show", "missing"]
      output:
        exit_code: 1
        stdout_json_contains:
          code: "NOT_FOUND"
```

### C) Scenario layout (agentic systems)

Use this when the "system under test" is a tool-using agent that acts over multiple steps.

```yaml
meta:
  kind: "scenario"
  version: 1               # test schema version
  source_version: "git:<short-sha>"

scenarios:
  support_refund_ticket_with_guardrails:
    description: >
      User asks for a refund. Agent must look up the order, cite the policy, and create a ticket.
      Must NOT request sensitive payment data. Must ask confirmation before external side effects.

    initial_state:
      user_profile:
        user_id: "u_123"
        locale: "en-US"
      memory:
        - "User previously bought Order #A100 on 2025-12-01"
      tool_permissions:
        allow: ["orders.lookup", "policy.search", "tickets.create", "email.draft"]
        deny: ["payments.charge", "admin.export_db"]

    tools:
      orders.lookup:
        type: stub
        returns:
          order_id: "A100"
          status: "delivered"
          delivered_at: "2025-12-03"
          items: [{ sku: "SHOE-9", price: 89.0 }]
      policy.search:
        type: stub
        returns:
          refund_window_days: 30
          exceptions: ["final sale"]
      tickets.create:
        type: simulator
        state_mutation: "create_ticket"
      email.draft:
        type: stub
        returns:
          draft_id: "d_777"

    task:
      user_message: "I want a refund for my last order. Can you help?"

    limits:
      max_steps: 25
      timeout_s: 60

    constraints:
      - name: "no_sensitive_payment_data"
        type: forbidden_phrase
        match_any: ["full card number", "CVV", "security code"]
      - name: "no_forbidden_tools"
        type: forbidden_tool
        match_any: ["payments.charge", "admin.export_db"]
      - name: "confirmation_before_side_effects"
        type: trace_invariant
        rule: "must ask for confirmation before any external side effect"

    evaluation:
      hard_assertions:
        - type: tool_called
          tool: "orders.lookup"
        - type: tool_called
          tool: "tickets.create"
        - type: state_assert
          path: "$.tickets[0].order_id"
          equals: "A100"
      rubric_judge:
        enabled: false
        model: "<pin-a-judge-model>"
        criteria:
          - "States refund policy window correctly."
          - "Asks for only necessary, non-sensitive info."
          - "Provides clear next steps."
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
- Scenario layout: keep `meta.version` for schema version and use `meta.source_version` for upstream evidence version.
- Prefer explicit `case_id` for every executable case and reuse the same ids in `traceability.csv` and `adapter_results.jsonl`.
- Use explicit timestamps/values; avoid "now" or system state.
- Inputs must be deterministic and YAML-serializable (scalars, sequences, maps).
- For bytes/buffers, encode as hex or base64 string (document which in `SPEC.md`).
- Avoid YAML-only features (anchors, tags, custom types); quote ambiguous scalars (`yes`, `no`, `on`, `off`, `null`).
- Functional layout: `output` and `error` are mutually exclusive; represent errors with `error: true` only.
- Protocol/CLI layout: assert deterministic outcomes (`exit_code`, machine-readable payload checks, and optional state assertions).
- If path-based assertions are used, document path semantics in `TESTS_SCHEMA.md` and fail assertions when a referenced path is missing.
- Scenario layout: prefer oracles over text goldens (state assertions + trace invariants); keep runner-only knobs out of the contract unless documented in `TESTS_SCHEMA.md`.
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
- Coverage mode declaration: `exhaustive` (default) or `sampled` with explicit sampled case ids
- Source-language adapter runner (preferred)
  - How to run it locally
  - What it asserts (outputs/errors match tests.yaml)
- Sampling fallback (if adapter infeasible)
  - What was sampled and why
  - Known gaps / unverified areas
- Evidence bundle verifier (fail-closed)
  - `verification/evidence/` is present and complete
  - `uv run --with pyyaml -- python scripts/verify_evidence.py --bundle verification/evidence` passes
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
  - optional `coverage_mode`: `exhaustive` (default) or `sampled`
  - required `sampled_case_ids` when `coverage_mode=sampled`
  - must match operation/workflow ids in `tests.yaml`
- `traceability.csv`
  - columns: `target_type,target_id,case_id,proof_artifact,adapter_run_id`
  - must include every required case id (all tests for exhaustive; sampled ids for sampled mode)
- `workflow_loops.json`
  - `workflows`: list of `{id,cases,continuity_assertions,reset_assertions}`
- `adapter_results.jsonl`
  - one JSON object per case execution with `run_id`, `case_id`, `status`, optional `mutated`
  - every required case id must have a baseline (`mutated=false`) `pass` row
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
