# Review and Self-Review Loop Examples

Use these examples to keep the visible transcript shape aligned with the diff review loop and the internal self-review loop contract.

## Review loop local-clean after address

```md
**Review loop trace**
- `R1` base_branch=`main`; comparison_sha=`9b75f2cdfff1de7b38f288f8409b5df00e4bd84b`; review_cmd=`git diff 9b75f2cdfff1de7b38f288f8409b5df00e4bd84b`; local_findings=`2`; blocked_findings=`0`; stale_findings=`0`; change_applied=`yes`; result=`continue`
- `R2` base_branch=`main`; comparison_sha=`9b75f2cdfff1de7b38f288f8409b5df00e4bd84b`; review_cmd=`git diff 9b75f2cdfff1de7b38f288f8409b5df00e4bd84b`; local_findings=`0`; blocked_findings=`0`; stale_findings=`0`; change_applied=`no`; result=`local_clean`

**Validation**
- `uv run pytest tests/foo.py::test_bar` -> ok
- `{"baseline_cmd":"uv run pytest tests/foo.py::test_bar","baseline_result":"fail","proof_hook":"uv run pytest tests/foo.py::test_bar","final_cmd":"uv run pytest tests/foo.py::test_bar","final_result":"ok"}`

**Self-review loop trace**
- `S1` prompt=`If you could change one thing about this changeset what would you change?`; answer_summary=Split the overloaded helper so branch choice and post-resume normalization are no longer coupled, even though the baseline bundle was already green.; finding=`F2`; change_applied=`yes`; proof=`uv run pytest tests/foo.py::test_bar`; result=`ok`; stop_reason=`continue`
- `S2` prompt=`If you could change one thing about this changeset what would you change?`; answer_summary=No new actionable self-review changes remain for the current validated changeset.; finding=`none`; change_applied=`no`; proof=`uv run pytest tests/foo.py::test_bar`; result=`ok`; stop_reason=`no_new_actionable_changes`
```

## Review loop local-clean with blocked carry-forward

```md
**Review loop trace**
- `R1` base_branch=`main`; comparison_sha=`9b75f2cdfff1de7b38f288f8409b5df00e4bd84b`; review_cmd=`git diff 9b75f2cdfff1de7b38f288f8409b5df00e4bd84b`; local_findings=`0`; blocked_findings=`1`; stale_findings=`0`; change_applied=`no`; result=`local_clean`

**Residual risks / open questions**
- `src/legacy_api.py:44` — blocked_by=breaking_change — next=choose an additive compatibility path
```

## Review loop stale repeat suppression

```md
**Review loop trace**
- `R1` base_branch=`main`; comparison_sha=`9b75f2cdfff1de7b38f288f8409b5df00e4bd84b`; review_cmd=`git diff 9b75f2cdfff1de7b38f288f8409b5df00e4bd84b`; local_findings=`1`; blocked_findings=`0`; stale_findings=`0`; change_applied=`yes`; result=`continue`
- `R2` base_branch=`main`; comparison_sha=`9b75f2cdfff1de7b38f288f8409b5df00e4bd84b`; review_cmd=`git diff 9b75f2cdfff1de7b38f288f8409b5df00e4bd84b`; local_findings=`0`; blocked_findings=`0`; stale_findings=`1`; change_applied=`no`; result=`local_clean`
```

## Review loop skip reasons

```md
**Review loop trace**
- None (skip_missing_base_context)
```

```md
**Review loop trace**
- None (skip_not_git_repo)
```

## Public surface proof coverage

```md
**Findings (severity order)**
- `F1` `src/with_api.zig:88` — logic — advertised anonymous inferred `!T` form is unproven on a public seam
  - Surface: Tokens=shift.with anonymous inferred !T; PROVEN_USED=yes (README + examples); External=yes; Diff_touch=yes
  - proof_target=anonymous inferred `!T` in `shift.with(...)`
  - Proof: `zig test test/with_api_inferred_errors.zig --test-filter anonymous_inferred_error` -> ok

- `F2` `src/algebraic.zig:144` — logic — algebraic handler-error inference remains unproven on the documented form
  - Surface: Tokens=shift.algebraic.Program handler inferred errors; PROVEN_USED=yes (docs + examples); External=yes; Diff_touch=yes
  - proof_target=handler inferred errors in `shift.algebraic.Program(...)`
  - Proof: `zig test test/algebraic_inferred_errors.zig --test-filter handler_inferred_error` -> ok
```

## Standalone invalidated-then-rerun

```md
**Review loop trace**
- None (skip_missing_base_context)

**Validation**
- `uv run pytest tests/flow.py::test_scope_lock` -> ok
- `{"baseline_cmd":"uv run pytest tests/flow.py::test_scope_lock","baseline_result":"ok","proof_hook":"uv run pytest tests/flow.py::test_scope_lock","final_cmd":"uv run pytest tests/flow.py::test_scope_lock","final_result":"ok"}`

**Self-review loop trace**
- `S1` prompt=`If you could change one thing about this changeset what would you change?`; answer_summary=Preserve the CLI entrypoint while widening into the adjacent helper the original diff did not touch.; finding=`F3`; change_applied=`yes`; proof=`uv run pytest tests/flow.py::test_scope_lock`; result=`ok`; stop_reason=`continue`
- `S2` prompt=`If you could change one thing about this changeset what would you change?`; answer_summary=No new actionable self-review changes remain for the current validated changeset.; finding=`none`; change_applied=`no`; proof=`uv run pytest tests/flow.py::test_scope_lock`; result=`ok`; stop_reason=`no_new_actionable_changes`
- `S3` prompt=`If you could change one thing about this changeset what would you change?`; answer_summary=Prior self-review state invalidated by the post-self-review core-pass rerun; rerunning against the new final validated changeset.; finding=`none`; change_applied=`no`; proof=`uv run pytest tests/flow.py::test_scope_lock`; result=`ok`; stop_reason=`continue`
- `S4` prompt=`If you could change one thing about this changeset what would you change?`; answer_summary=No new actionable self-review changes remain on the final validated changeset after the rerun.; finding=`none`; change_applied=`no`; proof=`uv run pytest tests/flow.py::test_scope_lock`; result=`ok`; stop_reason=`no_new_actionable_changes`
```

## Standalone skip gate

```md
**Review loop trace**
- None (skip_not_git_repo)

**Changes applied**
- None

**Self-review loop trace**
- None (skip_gate)
```

## Embedded Fix Record success

```md
**Review loop trace**
- `R1` base_branch=`main`; comparison_sha=`9b75f2cdfff1de7b38f288f8409b5df00e4bd84b`; review_cmd=`git diff 9b75f2cdfff1de7b38f288f8409b5df00e4bd84b`; local_findings=`1`; blocked_findings=`0`; stale_findings=`0`; change_applied=`yes`; result=`continue`
- `R2` base_branch=`main`; comparison_sha=`9b75f2cdfff1de7b38f288f8409b5df00e4bd84b`; review_cmd=`git diff 9b75f2cdfff1de7b38f288f8409b5df00e4bd84b`; local_findings=`0`; blocked_findings=`0`; stale_findings=`0`; change_applied=`no`; result=`local_clean`

**Validation**
- `uv run pytest tests/widget.py::test_safe_default` -> ok
- `{"baseline_cmd":"uv run pytest tests/widget.py::test_safe_default","baseline_result":"ok","proof_hook":"uv run pytest tests/widget.py::test_rejects_invalid_mode","final_cmd":"uv run pytest tests/widget.py::test_safe_default","final_result":"ok"}`

**Self-review loop trace**
- `S1` prompt=`If you could change one thing about this changeset what would you change?`; answer_summary=Inline the ambiguous fallback path into the explicit safe-default seam so the public helper is easier to audit.; finding=`F4`; change_applied=`yes`; proof=`uv run pytest tests/widget.py::test_safe_default`; result=`ok`; stop_reason=`continue`
- `S2` prompt=`If you could change one thing about this changeset what would you change?`; answer_summary=No further actionable self-review changes remain.; finding=`none`; change_applied=`no`; proof=`uv run pytest tests/widget.py::test_safe_default`; result=`ok`; stop_reason=`no_new_actionable_changes`
```

## Post-fix handoff

After a clean or closed `$fix` pass, broader follow-up should route to another skill instead of continuing under the `$fix` label.

- Use `$parse` for architecture or codebase-purpose analysis.
- Use `$grill-me` for pressure-testing or narrowing the next move.
- Use `$plan` for a decision-complete roadmap.
- Use `$creative-problem-solver` for broader option generation.
