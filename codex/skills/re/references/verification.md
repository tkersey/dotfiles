# Verification Guidance

This reference exists so the `re` skill can generate a first-class `VERIFY.md` in every ghost repo.

## Minimum checks (always)
- `tests.yaml` parses cleanly.
- Every public operation id has at least one test case.
- Each operation has coverage across success and error paths (when applicable).
- Case counts match or exceed the source test suite (when extracting from tests).

## Adapter Runner (preferred)

Goal: prove the extracted `tests.yaml` matches the original library.

1. Write a temporary adapter runner in the source language.
   - Put it in a scratch directory or an ignored path.
   - Do not ship it in the ghost repo.
2. Load `tests.yaml`.
3. For each `operation_id` and case:
   - Call the real function/method in the source library.
   - If the case has `error: true`, assert it errors.
   - Otherwise, assert the return value equals `output` (deep equality where applicable).
4. Record a short summary in `VERIFY.md` (how to run it, pass/fail, skips).
5. Delete the runner after verification.

Tips:
- Treat `operation_id` as an identifier: keep an explicit dispatch/mapping table.
- Force determinism: set timezone/locale explicitly, avoid system clock access, and document any runtime assumptions.

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
- Source language/runtime: <language + versions>
- Total cases executed: <n>/<total>
- Result: pass|fail

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

## Limitations
- <timezone/locale assumptions>
- <known gaps>
```
