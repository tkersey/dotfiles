# Review and Self-Review Loop Examples

Use these examples to keep the visible transcript shape aligned with the fixer-owned `P0 Core Review` pass, the terminal diff review closure loop, and the internal self-review loop contract.

When review context exists, the terminal `Review loop trace` rows are the post-self-review final-diff closure rounds against the unchanged final diff.
`P0 Core Review` iterations belong in `Pass trace`, not `Review loop trace`.
Each `R#` row comes from a fresh `cas review_session start --wait --cwd <cwd> --base <base_branch> --json` invocation after confirming the live merge base still matches the frozen `comparison_sha`.
Runtime pass updates use `Cycle <c>: Pass <n>/<total_planned>: ...`.
Terminal closure requires two consecutive clean `R#` rows on the unchanged final diff within the same cycle.

## P0 local-clean before downstream passes

`P0 Core Review` loops as a fixer-owned pass until no `local_findings` remain, then the remaining core passes and post-self-review rerun continue normally.

```md
**Pass trace**
- `Cycle C1` -> zero_edit_cycle_streak=`0`; edits=`yes`; review_context=`comparison_sha`; fingerprint=`changed`; result=`restart`
- Core passes planned: `4`; core passes executed: `4`
- Delta passes planned: `0`; delta passes executed: `0`
- Total core/delta passes executed: `4`
- `P0 Core Review` -> `done`; edits=`yes`; signal=`uv run pytest tests/foo.py::test_bar`; result=`ok`
- `P1 Safety` -> `done`; edits=`no`; signal=`uv run pytest tests/foo.py::test_bar`; result=`ok`
- `P2 Surface` -> `done`; edits=`no`; signal=`uv run pytest tests/foo.py::test_bar`; result=`ok`
- `P3 Audit` -> `done`; edits=`no`; signal=`uv run pytest tests/foo.py::test_bar`; result=`ok`
- `Post-self-review rerun` -> executed=`yes`; edits=`no`; signal=`uv run pytest tests/foo.py::test_bar`; result=`ok`
```

## Outer fixed-point two-cycle close

Two zero-edit cycles are required even when the first fully clean cycle already made no edits.

```md
Cycle 1: Pass 1/4: P0 Core Review — start; edits=n/a; signal=uv run pytest tests/foo.py::test_bar; result=n/a
Cycle 1: Pass 1/4: P0 Core Review — done; edits=yes; signal=uv run pytest tests/foo.py::test_bar; result=ok
Cycle 2: Pass 1/4: P0 Core Review — start; edits=n/a; signal=uv run pytest tests/foo.py::test_bar; result=n/a
Cycle 2: Pass 1/4: P0 Core Review — done; edits=no; signal=uv run pytest tests/foo.py::test_bar; result=ok
Cycle 3: Pass 1/4: P0 Core Review — start; edits=n/a; signal=uv run pytest tests/foo.py::test_bar; result=n/a
Cycle 3: Pass 1/4: P0 Core Review — done; edits=no; signal=uv run pytest tests/foo.py::test_bar; result=ok

**Pass trace**
- `Cycle C1` -> zero_edit_cycle_streak=`0`; edits=`yes`; review_context=`comparison_sha`; fingerprint=`changed`; result=`restart`
- Core passes planned: `4`; core passes executed: `4`
- Delta passes planned: `0`; delta passes executed: `0`
- Total core/delta passes executed: `4`
- `P0 Core Review` -> `done`; edits=`yes`; signal=`uv run pytest tests/foo.py::test_bar`; result=`ok`
- `P1 Safety` -> `done`; edits=`no`; signal=`uv run pytest tests/foo.py::test_bar`; result=`ok`
- `P2 Surface` -> `done`; edits=`no`; signal=`uv run pytest tests/foo.py::test_bar`; result=`ok`
- `P3 Audit` -> `done`; edits=`no`; signal=`uv run pytest tests/foo.py::test_bar`; result=`ok`
- `Post-self-review rerun` -> executed=`yes`; edits=`no`; signal=`uv run pytest tests/foo.py::test_bar`; result=`ok`
- `Cycle C2` -> zero_edit_cycle_streak=`1`; edits=`no`; review_context=`comparison_sha`; fingerprint=`same`; result=`continue`
- Core passes planned: `4`; core passes executed: `4`
- Delta passes planned: `0`; delta passes executed: `0`
- Total core/delta passes executed: `4`
- `P0 Core Review` -> `done`; edits=`no`; signal=`uv run pytest tests/foo.py::test_bar`; result=`ok`
- `P1 Safety` -> `done`; edits=`no`; signal=`uv run pytest tests/foo.py::test_bar`; result=`ok`
- `P2 Surface` -> `done`; edits=`no`; signal=`uv run pytest tests/foo.py::test_bar`; result=`ok`
- `P3 Audit` -> `done`; edits=`no`; signal=`uv run pytest tests/foo.py::test_bar`; result=`ok`
- `Post-self-review rerun` -> executed=`yes`; edits=`no`; signal=`uv run pytest tests/foo.py::test_bar`; result=`ok`
- `Cycle C3` -> zero_edit_cycle_streak=`2`; edits=`no`; review_context=`comparison_sha`; fingerprint=`same`; result=`close`
- Core passes planned: `4`; core passes executed: `4`
- Delta passes planned: `0`; delta passes executed: `0`
- Total core/delta passes executed: `4`
- `P0 Core Review` -> `done`; edits=`no`; signal=`uv run pytest tests/foo.py::test_bar`; result=`ok`
- `P1 Safety` -> `done`; edits=`no`; signal=`uv run pytest tests/foo.py::test_bar`; result=`ok`
- `P2 Surface` -> `done`; edits=`no`; signal=`uv run pytest tests/foo.py::test_bar`; result=`ok`
- `P3 Audit` -> `done`; edits=`no`; signal=`uv run pytest tests/foo.py::test_bar`; result=`ok`
- `Post-self-review rerun` -> executed=`yes`; edits=`no`; signal=`uv run pytest tests/foo.py::test_bar`; result=`ok`

**Review loop trace**
- `R1` cycle=`C2`; base_branch=`main`; comparison_sha=`9b75f2cdfff1de7b38f288f8409b5df00e4bd84b`; review_cmd=`cas review_session start --wait --cwd <cwd> --base main --json`; local_findings=`0`; blocked_findings=`0`; stale_findings=`0`; overall_correctness=`patch is correct`; change_applied=`no`; result=`local_clean`
- `R2` cycle=`C2`; base_branch=`main`; comparison_sha=`9b75f2cdfff1de7b38f288f8409b5df00e4bd84b`; review_cmd=`cas review_session start --wait --cwd <cwd> --base main --json`; local_findings=`0`; blocked_findings=`0`; stale_findings=`0`; overall_correctness=`patch is correct`; change_applied=`no`; result=`local_clean`
- `R3` cycle=`C3`; base_branch=`main`; comparison_sha=`9b75f2cdfff1de7b38f288f8409b5df00e4bd84b`; review_cmd=`cas review_session start --wait --cwd <cwd> --base main --json`; local_findings=`0`; blocked_findings=`0`; stale_findings=`0`; overall_correctness=`patch is correct`; change_applied=`no`; result=`local_clean`
- `R4` cycle=`C3`; base_branch=`main`; comparison_sha=`9b75f2cdfff1de7b38f288f8409b5df00e4bd84b`; review_cmd=`cas review_session start --wait --cwd <cwd> --base main --json`; local_findings=`0`; blocked_findings=`0`; stale_findings=`0`; overall_correctness=`patch is correct`; change_applied=`no`; result=`local_clean`
```

## Review loop local-clean after address

```md
**Review loop trace**
- `R1` cycle=`C1`; base_branch=`main`; comparison_sha=`9b75f2cdfff1de7b38f288f8409b5df00e4bd84b`; review_cmd=`cas review_session start --wait --cwd <cwd> --base main --json`; local_findings=`1`; blocked_findings=`0`; stale_findings=`0`; overall_correctness=`patch is incorrect`; change_applied=`yes`; result=`continue`
- `R2` cycle=`C1`; base_branch=`main`; comparison_sha=`9b75f2cdfff1de7b38f288f8409b5df00e4bd84b`; review_cmd=`cas review_session start --wait --cwd <cwd> --base main --json`; local_findings=`0`; blocked_findings=`0`; stale_findings=`0`; overall_correctness=`patch is correct`; change_applied=`no`; result=`local_clean`
- `R3` cycle=`C1`; base_branch=`main`; comparison_sha=`9b75f2cdfff1de7b38f288f8409b5df00e4bd84b`; review_cmd=`cas review_session start --wait --cwd <cwd> --base main --json`; local_findings=`0`; blocked_findings=`0`; stale_findings=`0`; overall_correctness=`patch is correct`; change_applied=`no`; result=`local_clean`

**Validation**
- `uv run pytest tests/foo.py::test_bar` -> ok
- `{"baseline_cmd":"uv run pytest tests/foo.py::test_bar","baseline_result":"fail","proof_hook":"uv run pytest tests/foo.py::test_bar","final_cmd":"uv run pytest tests/foo.py::test_bar","final_result":"ok"}`

**Self-review loop trace**
- `S1` prompt=`If you could change one thing about this changeset what would you change?`; answer_summary=The current final diff still leaves the overloaded helper coupling branch choice with post-resume normalization, which is the highest-severity remaining review-qualifying maintainability risk on the validated changeset.; finding=`F2`; change_applied=`yes`; proof=`uv run pytest tests/foo.py::test_bar`; result=`ok`; stop_reason=`continue`
- `S2` prompt=`If you could change one thing about this changeset what would you change?`; answer_summary=No new actionable self-review changes remain and the current final diff is review-clean under the diff review bars.; finding=`none`; change_applied=`no`; proof=`uv run pytest tests/foo.py::test_bar`; result=`ok`; stop_reason=`no_new_actionable_changes`
```

## Review loop blocked carry-forward

In the terminal final-diff closure round, blocked findings cannot use `scope_guardrail`, and closure still requires `blocked_findings=0`.

```md
**Review loop trace**
- `R1` cycle=`C1`; base_branch=`main`; comparison_sha=`9b75f2cdfff1de7b38f288f8409b5df00e4bd84b`; review_cmd=`cas review_session start --wait --cwd <cwd> --base main --json`; local_findings=`0`; blocked_findings=`1`; stale_findings=`0`; overall_correctness=`patch is incorrect`; change_applied=`no`; result=`continue`

**Residual risks / open questions**
- `src/legacy_api.py:44` — blocked_by=breaking_change — next=choose an additive compatibility path
```

## Review loop stale repeat suppression

Use stale suppression only when a dedicated proof hook/blocker already discharges the repeated finding or the targeted diff hunk/form is gone, and terminal closure still requires `stale_findings=0`.

```md
**Review loop trace**
- `R1` cycle=`C1`; base_branch=`main`; comparison_sha=`9b75f2cdfff1de7b38f288f8409b5df00e4bd84b`; review_cmd=`cas review_session start --wait --cwd <cwd> --base main --json`; local_findings=`1`; blocked_findings=`0`; stale_findings=`0`; overall_correctness=`patch is incorrect`; change_applied=`yes`; result=`continue`
- `R2` cycle=`C1`; base_branch=`main`; comparison_sha=`9b75f2cdfff1de7b38f288f8409b5df00e4bd84b`; review_cmd=`cas review_session start --wait --cwd <cwd> --base main --json`; local_findings=`0`; blocked_findings=`0`; stale_findings=`1`; overall_correctness=`patch is incorrect`; change_applied=`no`; result=`continue`
```

## Review loop skip reasons

Use `skip_missing_base_context` only when there is no live git diff and no derivable review target; a live git diff must derive review context or stop blocked.

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
  - Proof target: anonymous inferred `!T` in `shift.with(...)`
  - Proof: `zig test test/with_api_inferred_errors.zig --test-filter anonymous_inferred_error` -> ok

- `F2` `src/algebraic.zig:144` — logic — algebraic handler-error inference remains unproven on the documented form
  - Surface: Tokens=shift.algebraic.Program handler inferred errors; PROVEN_USED=yes (docs + examples); External=yes; Diff_touch=yes
  - Proof target: handler inferred errors in `shift.algebraic.Program(...)`
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
- `S2` prompt=`If you could change one thing about this changeset what would you change?`; answer_summary=No new actionable self-review changes remain for the current validated changeset and every proof surface is proved or blocked.; finding=`none`; change_applied=`no`; proof=`uv run pytest tests/flow.py::test_scope_lock`; result=`ok`; stop_reason=`no_new_actionable_changes`
- `S3` prompt=`If you could change one thing about this changeset what would you change?`; answer_summary=Prior self-review state invalidated by the post-self-review core-pass rerun; rerunning against the new final validated changeset.; finding=`none`; change_applied=`no`; proof=`uv run pytest tests/flow.py::test_scope_lock`; result=`ok`; stop_reason=`continue`
- `S4` prompt=`If you could change one thing about this changeset what would you change?`; answer_summary=No new actionable self-review changes remain on the final validated changeset after the rerun, and every proof surface is proved or blocked.; finding=`none`; change_applied=`no`; proof=`uv run pytest tests/flow.py::test_scope_lock`; result=`ok`; stop_reason=`no_new_actionable_changes`
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
**Pass trace**
- `Cycle C1` -> zero_edit_cycle_streak=`0`; edits=`yes`; review_context=`comparison_sha`; fingerprint=`changed`; result=`restart`
- Core passes planned: `4`; core passes executed: `4`
- Delta passes planned: `0`; delta passes executed: `0`
- Total core/delta passes executed: `4`
- `P0 Core Review` -> `done`; edits=`yes`; signal=`uv run pytest tests/widget.py::test_safe_default`; result=`ok`
- `P1 Safety` -> `done`; edits=`no`; signal=`uv run pytest tests/widget.py::test_safe_default`; result=`ok`
- `P2 Surface` -> `done`; edits=`no`; signal=`uv run pytest tests/widget.py::test_safe_default`; result=`ok`
- `P3 Audit` -> `done`; edits=`no`; signal=`uv run pytest tests/widget.py::test_safe_default`; result=`ok`
- `Post-self-review rerun` -> executed=`yes`; edits=`no`; signal=`uv run pytest tests/widget.py::test_safe_default`; result=`ok`

**Review loop trace**
- `R1` cycle=`C1`; base_branch=`main`; comparison_sha=`9b75f2cdfff1de7b38f288f8409b5df00e4bd84b`; review_cmd=`cas review_session start --wait --cwd <cwd> --base main --json`; local_findings=`1`; blocked_findings=`0`; stale_findings=`0`; overall_correctness=`patch is incorrect`; change_applied=`yes`; result=`continue`
- `R2` cycle=`C1`; base_branch=`main`; comparison_sha=`9b75f2cdfff1de7b38f288f8409b5df00e4bd84b`; review_cmd=`cas review_session start --wait --cwd <cwd> --base main --json`; local_findings=`0`; blocked_findings=`0`; stale_findings=`0`; overall_correctness=`patch is correct`; change_applied=`no`; result=`local_clean`
- `R3` cycle=`C1`; base_branch=`main`; comparison_sha=`9b75f2cdfff1de7b38f288f8409b5df00e4bd84b`; review_cmd=`cas review_session start --wait --cwd <cwd> --base main --json`; local_findings=`0`; blocked_findings=`0`; stale_findings=`0`; overall_correctness=`patch is correct`; change_applied=`no`; result=`local_clean`

**Validation**
- `uv run pytest tests/widget.py::test_safe_default` -> ok
- `{"baseline_cmd":"uv run pytest tests/widget.py::test_safe_default","baseline_result":"ok","proof_hook":"uv run pytest tests/widget.py::test_rejects_invalid_mode","final_cmd":"uv run pytest tests/widget.py::test_safe_default","final_result":"ok"}`

**Self-review loop trace**
- `S1` prompt=`If you could change one thing about this changeset what would you change?`; answer_summary=Inline the ambiguous fallback path into the explicit safe-default seam so the public helper is easier to audit.; finding=`F4`; change_applied=`yes`; proof=`uv run pytest tests/widget.py::test_safe_default`; result=`ok`; stop_reason=`continue`
- `S2` prompt=`If you could change one thing about this changeset what would you change?`; answer_summary=No further actionable self-review changes remain and the current final diff is review-clean under the diff review bars.; finding=`none`; change_applied=`no`; proof=`uv run pytest tests/widget.py::test_safe_default`; result=`ok`; stop_reason=`no_new_actionable_changes`
```

## Post-fix handoff

After a clean or closed `$fix` pass, broader follow-up should route to another skill instead of continuing under the `$fix` label.

- Use `$parse` for architecture or codebase-purpose analysis.
- Use `$grill-me` for pressure-testing or narrowing the next move.
- Use `$plan` for a decision-complete roadmap.
- Use `$creative-problem-solver` for broader option generation.
