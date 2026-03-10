# Self-Review Loop Examples

Use these examples to keep the visible transcript shape aligned with the internal self-review loop contract.

## Standalone success

```md
**Validation**
- `uv run pytest tests/foo.py::test_bar` -> ok
- `{"baseline_cmd":"uv run pytest tests/foo.py::test_bar","baseline_result":"fail","proof_hook":"uv run pytest tests/foo.py::test_bar","final_cmd":"uv run pytest tests/foo.py::test_bar","final_result":"ok"}`

**Self-review loop trace**
- `S1` prompt=`If you could change one thing about this changeset what would you change?`; answer_summary=Reject malformed enum values earlier at the parser boundary.; finding=`F2`; change_applied=`yes`; proof=`uv run pytest tests/foo.py::test_bar`; result=`ok`; stop_reason=`continue`
- `S2` prompt=`If you could change one thing about this changeset what would you change?`; answer_summary=No new fix-worthy findings remain under the current guardrails.; finding=`none`; change_applied=`no`; proof=`uv run pytest tests/foo.py::test_bar`; result=`ok`; stop_reason=`no_new_fix_worthy_findings`
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
- `S1` prompt=`If you could change one thing about this changeset what would you change?`; answer_summary=No further fix-worthy adjustments remain.; finding=`none`; change_applied=`no`; proof=`uv run pytest tests/widget.py::test_safe_default`; result=`ok`; stop_reason=`no_new_fix_worthy_findings`
```

## Post-fix handoff

After a clean or closed `$fix` pass, broader follow-up should route to another skill instead of continuing under the `$fix` label.

- Use `$parse` for architecture or codebase-purpose analysis.
- Use `$grill-me` for pressure-testing or narrowing the next move.
- Use `$plan` for a decision-complete roadmap.
- Use `$creative-problem-solver` for broader option generation.
