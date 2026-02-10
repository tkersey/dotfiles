# Verification Guidance

This reference exists so the `ghost` skill can generate a first-class `VERIFY.md` in every ghost repo.

## Minimum checks (always)
- `tests.yaml` parses cleanly.
- Every public operation id has at least one test case.
- Every public operation id has at least one executable (non-skip) case unless infeasible; document exceptions.
- Each operation has coverage across success and error paths (when applicable).
- Case counts match or exceed the source test suite (when extracting from tests).
- Skip inventory is explicit (operation/case/reason), with deterministic alternatives attempted first.
- Stable machine-interface fields are asserted (required keys, lengths/counts, and state effects where relevant).
- `VERIFY.md` includes provenance + a regeneration recipe.

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
4. Record a short summary in `VERIFY.md` (how to run it, pass/fail, skips).
   - Include upstream repo identity + exact revision.
   - Include the exact commands used to regenerate artifacts (or one deterministic recipe).
5. Delete the runner after verification.

Tips:
- Treat `operation_id` as an identifier: keep an explicit dispatch/mapping table.
- Force determinism: set timezone/locale explicitly, avoid system clock access, and document any runtime assumptions.
- If the source language has weak YAML tooling (notably Zig), parse `tests.yaml` externally and dispatch into the library via a tiny CLI/FFI shim.
- Re-run the adapter whenever `tests.yaml` or the harness semantics change; the verification summary must match the current test inventory.

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

## Skip Inventory
| operation id | case | reason |
| --- | --- | --- |
| ... | ... | ... |

## Limitations
- <timezone/locale assumptions>
- <known gaps>
```
