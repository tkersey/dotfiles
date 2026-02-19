# Verification Guidance

This reference exists so the `ghost` skill can generate a first-class `VERIFY.md` in every ghost repo.

## Minimum checks (always)
- `tests.yaml` parses cleanly.
- Every public operation id (or tool id for scenario suites) has at least one test case.
- Every public operation id (or tool id) has at least one executable (non-skip) case unless infeasible; document exceptions.
- Each operation has coverage across success and error paths (when applicable).
- Each primary stateful workflow (or scenario) has at least one executable end-to-end loop scenario with continuity assertions.
- Verification evidence bundle exists under `verification/evidence/` with all required files.
- 100% of public operations are mapped in traceability evidence.
- 100% of primary workflows are mapped in traceability evidence and loop inventory evidence.
- Mutation sensitivity gate passes (required mutations detected as failures).
- Independent regeneration parity passes with zero normalized artifact diffs.
- Case counts match or exceed the source test suite (when extracting from tests).
- Skip inventory is explicit (operation/case/reason), with deterministic alternatives attempted first.
- Stable machine-interface fields are asserted (required keys, lengths/counts, and state effects where relevant).
- `VERIFY.md` includes provenance + a regeneration recipe.

Scenario-suite extras (when `tests.yaml` uses scenario layout):
- Each critical scenario has explicit **hard oracles** (final state / side effects) and **trace invariants** (forbidden tools, confirmation-before-side-effects, budget/step limits, injection resistance).
- If the agent is stochastic in production, `VERIFY.md` records reliability runs (N trials), pass rates, and the rule that critical invariant violations are release-blocking.

## Evidence Bundle Contract (fail-closed)

Bundle path: `verification/evidence/`

Required files:
- `inventory.json`
  - `public_operations`: list of operation ids
  - `primary_workflows`: list of `{id, requires_reset}`
- `traceability.csv`
  - columns: `target_type,target_id,case_id,proof_artifact,adapter_run_id`
  - `target_type` must be `operation` or `workflow`
- `workflow_loops.json`
  - `workflows`: list of `{id,cases,continuity_assertions,reset_assertions}`
- `adapter_results.jsonl`
  - one JSON object per executed case: `run_id`, `case_id`, `status`, optional `mutated`
- `mutation_check.json`
  - `{required_mutations, detected_failures, pass}`
- `parity.json`
  - `{pass, diff_count, run_a, run_b}`

Verifier command:
- from the ghost skill directory: `uv run python scripts/verify_evidence.py --bundle <ghost-repo>/verification/evidence`
- non-zero exit means extraction quality gate failed

Notes for scenario suites:
- Interpret `public_operations` as tool ids (what the agent can call).
- Interpret `primary_workflows` as scenario ids (critical end-to-end loops).

## Adapter Runner (preferred)

Goal: prove the extracted `tests.yaml` matches the original library.

1. Write a temporary adapter runner in the source language.
   - Put it in a scratch directory or an ignored path.
   - Do not ship it in the ghost repo.
2. Load `tests.yaml`.
3. For each `operation_id` and case:
   - Call the real surface in the source library.
   - Functional layout: assert `error: true` vs `output` semantics.
   - Protocol/CLI layout: assert exit/status/payload/state semantics.
   - Stateful workflows: assert continuity across steps (persisted ids/chains/context) and reset behavior where applicable.
4. Record a short summary in `VERIFY.md` (how to run it, pass/fail, skips).
   - Include upstream repo identity + exact revision.
   - Include the exact commands used to regenerate artifacts (or one deterministic recipe).
5. Delete the runner after verification.

Tips:
- Treat `operation_id` as an identifier: keep an explicit dispatch/mapping table.
- Force determinism: set timezone/locale explicitly, avoid system clock access, and document any runtime assumptions.
- If the source language has weak YAML tooling (notably Zig), parse `tests.yaml` externally and dispatch into the library via a tiny CLI/FFI shim.
- Re-run the adapter whenever `tests.yaml` or the harness semantics change; the verification summary must match the current test inventory.
- Record each adapter/sample execution in `adapter_results.jsonl` and keep run ids stable enough to join with `traceability.csv`.

Scenario adapter notes:
- Treat the environment as a state machine: tool calls emit trace events; state updates; agent observes.
- Prefer assertions over final-text matching: state assertions + trace invariants + forbidden-action checks.
- For production-like reliability, run scenarios multiple times and record pass rates + cost/latency distributions in `VERIFY.md` and evidence artifacts.

## Sampling Fallback (if adapter infeasible)

If a full adapter runner is infeasible:
- Run a representative sample across *all* operation ids (typical + boundary + error cases).
- Document exactly what was sampled and why full verification was infeasible.
- Call out any behaviors inferred from docs/code rather than executed tests.

## `VERIFY.md` Template

```markdown
# Verification

## Summary
- Source verification: adapter|sampling
- tests.yaml layout: functional|protocol
- Source repo: <url/path>
- Source revision: <tag/sha>
- `tests.yaml` source version: <string>
- Source language/runtime: <language + versions>
- Total cases: <total>
- Executed: <n>
- Skipped: <k>
- Loop scenarios executed: <count>
- Verifier command: `uv run python scripts/verify_evidence.py --bundle verification/evidence`
- Verifier result: pass|fail
- Result: pass|fail

## Regenerate (artifact production)
This ghost repo should be reproducible from the upstream revision.

- Preconditions: <tooling needed; env normalization>
- Upstream checkout:
  - <exact commands to obtain upstream at the pinned revision>
- Extract/update artifacts:
  - `SPEC.md`: <how it was produced>
  - `tests.yaml`: <how it was produced>
  - `INSTALL.md` / `README.md`: <how they were produced>
  - `LICENSE*`: <what was copied>
- Verify:
  - <exact commands to run verification>

## Adapter Runner (preferred)
- How to run: <exact command>
- What it validates: outputs/errors match `tests.yaml`
- Skips/notes: <if any>

## Sampling (fallback)
- Sampled cases: <what, how many, why these>
- Not verified: <what remains, why>

## Test Inventory
| operation id | cases | error cases |
| --- | ---: | ---: |
| ... | ... | ... |

## Workflow Loop Inventory
| workflow id | cases | continuity assertions |
| --- | ---: | --- |
| ... | ... | ... |

## Traceability Matrix
| target type | target id | case id | proof artifact | adapter run id |
| --- | --- | --- | --- | --- |
| ... | ... | ... | ... | ... |

## Adapter Run Ledger
| run id | mode | command | result |
| --- | --- | --- | --- |
| ... | ... | ... | ... |

## Mutation Sensitivity
| required mutations | detected failures | pass |
| ---: | ---: | --- |
| ... | ... | ... |

## Regeneration Parity
| run a | run b | normalized diff count | pass |
| --- | --- | ---: | --- |
| ... | ... | ... | ... |

## Skip Inventory
| operation id | case | reason |
| --- | --- | --- |
| ... | ... | ... |

## Limitations
- <timezone/locale assumptions>
- <known gaps>
```
