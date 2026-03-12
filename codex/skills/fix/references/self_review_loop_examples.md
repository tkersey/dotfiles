# Self-Review Loop Examples

Use these examples to keep the visible transcript shape aligned with the internal self-review loop contract.

## Standalone success

```md
**Validation**
- `uv run pytest tests/foo.py::test_bar` -> ok
- `{"baseline_cmd":"uv run pytest tests/foo.py::test_bar","baseline_result":"fail","proof_hook":"uv run pytest tests/foo.py::test_bar","final_cmd":"uv run pytest tests/foo.py::test_bar","final_result":"ok"}`

**Self-review loop trace**
- `S1` prompt=`If you could change one thing about this changeset what would you change?`; answer_summary=Harden the parser boundary even though it broadens the diff beyond the original slice.; finding=`F2`; change_applied=`yes`; proof=`uv run pytest tests/foo.py::test_bar`; result=`ok`; stop_reason=`continue`
- `S2` prompt=`If you could change one thing about this changeset what would you change?`; answer_summary=No new actionable self-review changes remain for the current validated changeset.; finding=`none`; change_applied=`no`; proof=`uv run pytest tests/foo.py::test_bar`; result=`ok`; stop_reason=`no_new_actionable_changes`
```

## Standalone invalidated-then-rerun

```md
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
**Changes applied**
- None

**Self-review loop trace**
- None (skip_gate)
```

## Embedded Fix Record success

```md
**Validation**
- `uv run pytest tests/widget.py::test_safe_default` -> ok
- `{"baseline_cmd":"uv run pytest tests/widget.py::test_safe_default","baseline_result":"ok","proof_hook":"uv run pytest tests/widget.py::test_rejects_invalid_mode","final_cmd":"uv run pytest tests/widget.py::test_safe_default","final_result":"ok"}`

**Self-review loop trace**
- `S1` prompt=`If you could change one thing about this changeset what would you change?`; answer_summary=No further actionable self-review changes remain.; finding=`none`; change_applied=`no`; proof=`uv run pytest tests/widget.py::test_safe_default`; result=`ok`; stop_reason=`no_new_actionable_changes`
```

## Post-fix handoff

After a clean or closed `$fix` pass, broader follow-up should route to another skill instead of continuing under the `$fix` label.

- Use `$parse` for architecture or codebase-purpose analysis.
- Use `$grill-me` for pressure-testing or narrowing the next move.
- Use `$plan` for a decision-complete roadmap.
- Use `$creative-problem-solver` for broader option generation.
