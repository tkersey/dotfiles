# Review and Self-Review Loop Examples

Use these examples to keep the visible transcript shape aligned with the fixer-owned remediation cycles, the terminal native-review saturation loop, and the internal review-reconciliation contract. When review context exists, the terminal `Review loop trace` rows are fresh isolated native `codex review` invocations on the unchanged final diff. `P0 Core Review` iterations belong in `Pass trace`, not `Review loop trace`.

Each `R#` row comes from a fresh isolated review invocation on the frozen review context. Native `codex review --base <base_branch>` or `codex review --commit <commit_sha>` is the default for ordinary one-shot review rows. Detached CAS rows use fresh split `cas review_session start ...` plus `wait ...` only when explicit lifecycle control is required, and only after confirming the live merge base still matches the frozen `comparison_sha`.

Use `review_transport=<...>`, `fallback_reason=<...>`, `review_thread_id=...`, and `cas_attempt_key=...` on every review-loop row. Standard git-backed branch-diff closure reviews stay on the same frozen whole diff for native, CAS, and native fallback; do not narrow to touched files or another ad hoc sub-scope unless preflight explicitly chose commit/worktree scope.

Terminal closure requires **two consecutive clean** `R#` rows on the **unchanged artifact state** by default. The first clean row is `candidate_clean`; it never closes by itself. Any actionable finding after `candidate_clean` resets the clean streak and must classify each finding in `**Review reconciliation**` as `recurring_seeded`, `recurring_fix_discovered`, or `fresh_review`.

`P2 Footguns` must either fix, prove, or block any actionable misuse on the touched public/documented surfaces or adjacent seam before closure. Every complete deliverable or Fix Record also includes `**Review reconciliation**` plus per-finding provenance in the form `Provenance: Origin=review_seed|proof_hook|adjacent_seam|validation_gap|fresh_review`.

## Native-first saturation on the frozen whole diff

```md
**Review loop trace**
- `R1` cycle=`C3`; base_branch=`main`; comparison_sha=`9b75f2cdfff1de7b38f288f8409b5df00e4bd84b`; review_transport=`native`; fallback_reason=`none`; review_start_cmd=`codex review --base main`; review_wait_cmd=`n/a`; review_thread_id=`none`; cas_attempt_key=`none`; local_findings=`0`; blocked_findings=`0`; stale_findings=`0`; overall_correctness=`patch is correct`; change_applied=`no`; result=`candidate_clean`; clean_streak=`1/2`
- `R2` cycle=`C3`; base_branch=`main`; comparison_sha=`9b75f2cdfff1de7b38f288f8409b5df00e4bd84b`; review_transport=`native`; fallback_reason=`none`; review_start_cmd=`codex review --base main`; review_wait_cmd=`n/a`; review_thread_id=`none`; cas_attempt_key=`none`; local_findings=`0`; blocked_findings=`0`; stale_findings=`0`; overall_correctness=`patch is correct`; change_applied=`no`; result=`native_saturated`; clean_streak=`2/2`
- Both rows used fresh native `codex review --base main` invocations on the same frozen `main...comparison_sha` branch diff, with no edits between them.
```

## Candidate clean reopens with a new issue

```md
**Review loop trace**
- `R4` cycle=`C5`; base_branch=`main`; comparison_sha=`9b75f2cdfff1de7b38f288f8409b5df00e4bd84b`; review_transport=`native`; fallback_reason=`none`; review_start_cmd=`codex review --base main`; review_wait_cmd=`n/a`; review_thread_id=`none`; cas_attempt_key=`none`; local_findings=`0`; blocked_findings=`0`; stale_findings=`0`; overall_correctness=`patch is correct`; change_applied=`no`; result=`candidate_clean`; clean_streak=`1/2`
- `R5` cycle=`C5`; base_branch=`main`; comparison_sha=`9b75f2cdfff1de7b38f288f8409b5df00e4bd84b`; review_transport=`native`; fallback_reason=`none`; review_start_cmd=`codex review --base main`; review_wait_cmd=`n/a`; review_thread_id=`none`; cas_attempt_key=`none`; local_findings=`1`; blocked_findings=`0`; stale_findings=`0`; overall_correctness=`needs work`; change_applied=`no`; result=`reopen`; clean_streak=`0/2`

**Review reconciliation**
- `F7` fingerprint=`api:parse:empty-config`; classification=`fresh_review`; Provenance: Origin=`fresh_review`; Seeded review=`none`
- The candidate clean did not close the run. The reopening finding reset the clean streak and seeded the next fixer cycle.
```

## Recurring seeded finding blocks for non-convergence

```md
**Review loop trace**
- `R7` cycle=`C6`; base_branch=`main`; comparison_sha=`9b75f2cdfff1de7b38f288f8409b5df00e4bd84b`; review_transport=`native`; fallback_reason=`none`; review_start_cmd=`codex review --base main`; review_wait_cmd=`n/a`; review_thread_id=`none`; cas_attempt_key=`none`; local_findings=`1`; blocked_findings=`0`; stale_findings=`0`; overall_correctness=`needs work`; change_applied=`no`; result=`reopen`; clean_streak=`0/2`

**Review reconciliation**
- `F2` fingerprint=`cache:flush:error-path`; classification=`recurring_seeded`; Provenance: Origin=`review_seed`; Seeded review=`R6`
- Because the same seeded finding reappeared and the immediately preceding remediation did not materially change the implicated code or materially improve validation, the run stops `blocked` for non-convergence instead of looping forever.
```
