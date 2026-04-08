#!/usr/bin/env -S uv run python
"""Lint contract sections for codex/skills/fix/SKILL.md."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

EXPECTED_MAIN_HEADINGS = [
    "Contract",
    "Review reconciliation",
    "Findings (severity order)",
    "Changes applied",
    "Review loop trace",
    "Pass trace",
    "Validation",
    "Self-review loop trace",
    "Residual risks / open questions",
]

EXPECTED_EMBEDDED_HEADINGS = [
    "Review reconciliation",
    "Findings (severity order)",
    "Changes applied",
    "Review loop trace",
    "Pass trace",
    "Validation",
    "Self-review loop trace",
    "Residual risks / open questions",
]

EXPECTED_VALIDATION_KEYS = [
    "baseline_cmd",
    "baseline_result",
    "proof_hook",
    "final_cmd",
    "final_result",
]

EXPECTED_FINDINGS_LINES = [
    "Provenance: Origin=`<review_seed|p0_core_review|proof_hook|footgun_scan|self_review|terminal_review>`; Seeded review=`<yes|no>`",
    "Proof target: <exact advertised/documented form covered by the proof>",
    "Proof strength: `<characterization|targeted_regression|property_or_fuzz>`",
    "Compatibility impact: `<none|tightening|additive|breaking>`",
]

EXPECTED_RECONCILIATION_LINES = [
    "- `review_seed_count=<N|0>`; `seeded_findings_closed=<N|0>`; `seeded_findings_still_open=<N|0>`; `fix_discovered_count=<N|0>`",
    "- `origin_tally=<review_seed:N,p0_core_review:N,proof_hook:N,footgun_scan:N,self_review:N,terminal_review:N>`",
]

EXPECTED_REVIEW_LINES = [
    "- If skipped: `- None (skip_not_git_repo|skip_missing_base_context)`",
    "- Otherwise: `R#` cycle=`<C#>`; base_branch=`<name>`; comparison_sha=`<sha>`; review_transport=`<native|cas|native_fallback>`; fallback_reason=`<none|missing_cas_dependency|missing_codex_binary|incompatible_codex_review_runtime|review_output_missing|parent_thread_not_materialized|unsafe_parent_thread_state>`; review_start_cmd=`<codex review --base <name>|codex review --commit <sha>|cas review_session start --cwd <cwd> --base <name> --json|cas review_session start --cwd <cwd> --commit <sha> --json|n/a>`; review_wait_cmd=`<cas review_session wait --review-thread-id <reviewThreadId> --timeout-ms <timeout_ms> --json|n/a>`; review_thread_id=`<thr_*|none>`; cas_attempt_key=`<review_target_kind|comparison_sha|resolvedCodexPath|resolvedCodexVersion|none>`; local_findings=`<N>`; blocked_findings=`<N>`; stale_findings=`<N>`; overall_correctness=`<patch is correct|patch is incorrect>`; change_applied=`<yes|no>`; result=`<continue|local_clean>`",
    '- Use `result=local_clean` only when `local_findings=0`, `blocked_findings=0`, `stale_findings=0`, and `overall_correctness="patch is correct"`; otherwise keep `result=continue`.',
    "- Each `R#` row comes from the terminal diff review closure loop in a fresh isolated review invocation on the frozen review context; the fixer does not self-grade that round. Native rows use `codex review --base <base_branch>` or `codex review --commit <sha>`; detached rows use split CAS `start` then `wait` after confirming the live merge base still matches the frozen `comparison_sha`; native fallback rows are allowed only when the immediately preceding detached CAS attempt for the same run-local `cas_attempt_key` failed with an allowed fallback `failureCode`.",
    "- Standard git-backed branch-diff closure rows stay on the same frozen whole diff for native, CAS, and native fallback; do not narrow to touched files or another ad hoc sub-scope unless preflight explicitly chose commit/worktree scope.",
    "- Terminal closure requires one clean row on the unchanged final diff within the same cycle by default, and two consecutive clean rows only after a terminal-review-driven edit or `review_transport=native_fallback`.",
    '- Each terminal closure row must have `local_findings=0`, `blocked_findings=0`, `stale_findings=0`, and `overall_correctness="patch is correct"`.',
]

EXPECTED_PASS_LINES = [
    "- `Cycle C#` -> zero_edit_cycle_streak=`<0|1|2>`; edits=`<yes|no>`; review_context=`<comparison_sha|skip_not_git_repo|skip_missing_base_context>`; fingerprint=`<same|changed|n/a>`; result=`<restart|continue|close>`",
    "- For each executed cycle, include:",
    "  - Core passes planned: `4`; core passes executed: `<4>`",
    "  - Delta passes planned: `<0|2>`; delta passes executed: `<0|2>`",
    "  - Total core/delta passes executed: `<4|6>`",
    "  - `P0 Core Review` -> `<done>`; edits=`<yes|no>`; signal=`<cmd|n/a>`; result=`<ok|fail|n/a>`",
    "  - `P1 Safety` -> `<done>`; edits=`<yes|no>`; signal=`<cmd|n/a>`; result=`<ok|fail|n/a>`",
    "  - `P2 Footguns` -> `<done>`; edits=`<yes|no>`; signal=`<cmd|n/a>`; result=`<ok|fail|n/a>`",
    "  - `P3 Surface + Audit` -> `<done>`; edits=`<yes|no>`; signal=`<cmd|n/a>`; result=`<ok|fail|n/a>`",
    "  - If delta passes executed, also include `P4` and `P5` lines in the same format.",
    "  - `Post-self-review rerun` -> executed=`<yes|no>`; edits=`<yes|no>`; signal=`<cmd|n/a>`; result=`<ok|fail|n/a>`",
]

EXPECTED_SELF_REVIEW_LINES = [
    "- If none: `- None (skip_gate)`",
    "- Otherwise: `S#` prompt=`If you could change one thing about this changeset what would you change?`; answer_summary=<...>; finding=`<F#|none>`; change_applied=`<yes|no>`; proof=`<cmd|n/a>`; result=`<ok|fail|n/a>`; stop_reason=`<continue|no_new_actionable_changes|blocked>`",
]

ALLOWED_BLOCKED_BY = [
    "product_ambiguity",
    "breaking_change",
    "no_repro_or_proof",
    "scope_guardrail",
    "generated_output",
    "external_dependency",
    "perf_unmeasurable",
]

EXPECTED_RESIDUAL_LINE = (
    "- Otherwise: `- <file:line or token> — blocked_by=<"
    + "|".join(ALLOWED_BLOCKED_BY)
    + "> — next=<one action>`"
)

REQUIRED_SELF_LOOP_GUARDRAILS = [
    "MUST include a final `Self-review loop trace` section in the deliverable/Fix Record.",
    "MUST run the final agent-directed self-review loop only after at least one change is applied and validation is passing.",
    "MUST run the self-review loop against the final validated changeset only.",
    "MUST invalidate and rerun the self-review loop if any non-self-review edit occurs after a self-review round, including edits from the post-self-review rerun or final diff review closure loop.",
    "MUST ask internally exactly: `If you could change one thing about this changeset what would you change?`",
    "MUST treat the final agent-directed self-review phase as current-worktree scoped once the first validated changeset exists; do not reject a self-review suggestion solely because it broadens the diff.",
    "MUST, when answering the self-review question, first inventory unresolved review-qualifying findings on the current final diff using `Diff review finding bar (required)`; if any exist, choose the highest-severity unresolved one before considering ergonomic/structural/API-shaping improvements.",
    "MUST, when answering the self-review question, also inventory unresolved actionable footgun findings on the touched surfaces or adjacent seam before considering broader ergonomic/structural/API-shaping improvements.",
    "MUST treat a self-review answer as actionable whenever it identifies a concrete compatible/provable improvement on the current validated changeset, even if the improvement is ergonomic, structural, or API-shaping rather than a baseline bug fix.",
    "MUST answer that question internally, apply at most one new actionable self-review change per self-round, re-run validation, and repeat until a self-round yields no new actionable self-review change or only blocked changes.",
    "MUST, when public/documented surfaces are touched, answer that question by first inventorying which advertised surface remains unproven; `finding=none` is allowed only when every such surface is proved or explicitly blocked and the current final diff yields zero qualifying findings under the diff review bars.",
    "MUST NOT reject a self-review suggestion solely because the baseline is already green, the concern sounds architectural, or the change would reshape a public/API seam; if it can stay backward-compatible and be revalidated locally, implement it.",
    "MUST, when a self-review critique is broader than the smallest bug repair, apply the narrowest compatible/provable slice that materially addresses the critique before considering broader follow-up skills.",
    "MUST rerun the non-self-review `$fix` passes once after the self-review loop reaches `no_new_actionable_changes` or `blocked`.",
    "MUST NOT use `scope_guardrail` as the reason to reject a self-review suggestion once the self-review phase has started.",
    "MUST NOT carry a terminal final-diff review finding as `blocked_by=scope_guardrail`; after self-review starts, treat it as `local_findings` or block it for another allowed reason.",
    "MUST NOT report a self-review answer that was already applied before the final self-review round; record `finding=none` only when the current final validated changeset yields no concrete compatible/provable self-review change and no qualifying diff-review finding remains.",
    "MUST NOT emit `If you could change one thing about this changeset what would you change?` as a user-facing terminal line during normal successful completion.",
    "Precondition gate: run this step only when `Changes applied` is not `None` and the latest validation signal result is `ok`.",
    "Freeze the self-review baseline as the latest validated changeset.",
    "If that rerun edits code, discard the stale self-review state, revalidate, and restart from phase 4 against the new final validated changeset.",
    "If the answer yields no new actionable self-review change, record `stop_reason=no_new_actionable_changes` and continue to phase 5.",
    "If the answer yields only blocked changes, record `stop_reason=blocked`, carry blockers to `Residual risks / open questions`, and continue to phase 5.",
    "Skip gate: if `Changes applied` is `None` or the run is blocked before edits, output `- None (skip_gate)` in `Self-review loop trace` and proceed to phase 7.",
    "`finding=none` is allowed only when every enumerated proof surface is `proved|blocked`, the current final diff yields zero qualifying findings under the diff review bars, and no actionable footgun on the touched surfaces or adjacent seam remains unresolved.",
]

REQUIRED_FOOTGUN_GUARDRAILS = [
    "MUST run `P2 Footguns` as a first-class core pass before `P3 Surface + Audit`.",
    "MUST inspect every touched public/documented surface plus at most one adjacent caller, constructor, parser, wrapper, or config boundary seam when needed to prove or defuse misuse.",
    "MUST, in `P2 Footguns`, produce at least one top-ranked misuse path or an explicit `none_with_reason` for every touched public/documented surface.",
    "MUST treat any concrete compatible/provable footgun mitigation on the touched surface or adjacent seam as a normal finding that blocks closure until it is fixed, proved, or blocked.",
    "### Footgun discovery bar (required)",
    "Treat a footgun as in-scope only when it is a concrete, plausible misuse on a touched public/documented surface or on one adjacent caller, constructor, parser, wrapper, or config boundary seam.",
    "Apply the author-fix-worthiness bar here too: the scenario should be something the original author would likely guard against if shown the misuse path.",
    "For each qualifying footgun, include a minimal misuse snippet or timeline plus the surprising behavior it triggers.",
    "For each touched public/documented surface, produce at least one top-ranked misuse path or an explicit `none_with_reason`.",
]

REQUIRED_REVIEW_LOOP_GUARDRAILS = [
    "MUST include a final `Review loop trace` section in the deliverable/Fix Record.",
    "MUST default git-backed branch-diff and commit review rounds to native `codex review --base <base_branch>` or `codex review --commit <sha>` when the run only needs a one-shot verdict on the frozen review context. Reserve split detached-review lifecycle commands (`cas review_session start ...` plus `wait ...`) for runs that explicitly need detached lifecycle control: persisted `reviewThreadId`, fresh-process polling after launch, explicit interrupt, compatibility diagnostics, or approval/runtime overrides. If an explicitly detached CAS round exits with `failureCode` in `missing_cas_dependency|missing_codex_binary|incompatible_codex_review_runtime|review_output_missing|parent_thread_not_materialized|unsafe_parent_thread_state`, one temporary caller-owned fallback to native `codex review --base <base_branch>` or `codex review --commit <sha>` is allowed; record `review_transport=native_fallback` and `fallback_reason=<failureCode>`.",
    "MUST keep standard git-backed branch-diff review scope on the entire frozen `base_branch`/`comparison_sha` diff. Once preflight freezes a branch-diff review context, neither native review, detached CAS, nor native fallback may be narrowed to touched files, the current uncommitted patch, or another ad hoc sub-scope unless the run was explicitly commit-scoped or explicitly worktree-scoped from preflight.",
    "MUST treat a slow native whole-diff review (`review_transport=native|native_fallback`) as the intended closure lane for standard branch-backed `$fix` runs; do not relabel it as non-convergent or abandon it solely because the branch diff is larger than the immediate fix seam.",
    "MUST run `P0 Core Review` as the first core pass, using the frozen review context's active review transport (`review_transport=native` by default, `review_transport=cas` only for explicit detached-control runs) as a fixer-owned pass that is reported in `Pass trace`, not `Review loop trace`.",
    "MUST classify `P0 Core Review` output into `local_findings` and `blocked_findings` only; `stale_findings` are terminal-review-only.",
    "MUST treat `P0 Core Review` as a single frozen discovery pass per outer cycle; use its output to seed local repair work for that cycle instead of rerunning whole-diff review after each local fix.",
    "MUST run every terminal `R#` review round in a fresh isolated review invocation with no authoring carry-over from the fixer. For branch-diff rounds, first confirm the live merge base still matches the frozen `comparison_sha`; if it drifts, stop blocked and refresh review context in a new `$fix` run. Native rows use fresh `codex review --base <base_branch>` on the frozen whole diff; detached rows use fresh split CAS `start` plus `wait`; native fallback rows are allowed only when the immediately preceding detached CAS attempt for the same run-local `cas_attempt_key` failed with an allowed fallback `failureCode`. The fixer may address findings but must not both author and adjudicate the same review round.",
    "MUST derive `base_branch` and `comparison_sha` from repo state for any git-backed run with a live diff when they are omitted, preferring the branch's actual review base plus merge-base commit whenever derivable (tracked/upstream/default base branch). Reserve a current worktree/HEAD fallback only for explicitly worktree-scoped requests with no broader base. For git-backed live diffs, missing review context after derivation is a blocker, not a successful `skip_missing_base_context` path.",
    "MUST verify `comparison_sha` resolves to a commit before activating `P0 Core Review` or the terminal diff review loop.",
    "MUST keep the terminal diff review loop separate from `Pass trace`; report it in `Review loop trace`.",
    'MUST rerun the isolated review loop against the current final diff after the self-review loop and after any post-self-review rerun edits; by default, close terminal review after one clean round on the unchanged final diff with `local_findings=0`, `blocked_findings=0`, `stale_findings=0`, `overall_correctness="patch is correct"`, and every enumerated proof surface `proved|blocked`. Require a second clean confirmation round only when the same cycle had a terminal-review-driven edit or used `review_transport=native_fallback`.',
    "MUST treat blocked `P0 Core Review` carry-forward as pre-terminal only. A terminal final-diff closure round with any `blocked_findings` or `stale_findings` is not review-clean and does not close `$fix`.",
    "MUST NOT treat a terminal final-diff review round with `blocked_findings>0` as closed or `local_clean`; if a fresh reviewer still emits any finding, `$fix` is not done.",
    "MUST NOT treat a terminal final-diff review round with `stale_findings>0` as closed or `local_clean`; if a fresh reviewer still emits a repeated finding, `$fix` is not done.",
    'MUST use `result=local_clean` only when `local_findings=0`, `blocked_findings=0`, `stale_findings=0`, and `overall_correctness="patch is correct"`; otherwise keep `result=continue`.',
    "MUST require two consecutive clean terminal review rows on the unchanged final diff only when the same cycle had a terminal-review-driven edit or used `review_transport=native_fallback`; otherwise one clean row is sufficient.",
    "MUST suppress a repeated diff-review finding only when its normalized fingerprint and implicated path set did not change across consecutive review rounds and the current proof bundle directly disproves the finding or the implicated diff hunk/form no longer exists; unchanged repetition alone is not enough.",
    "MUST judge diff-review findings by author-fix-worthiness: flag only discrete, actionable bugs introduced by the diff that materially affect correctness, performance, security, or maintainability and that the original author would likely fix if they knew about them.",
    "MUST prefer zero diff-review findings over speculative or assumption-heavy output; do not flag pre-existing issues, intentional behavior changes, or style-only nits.",
    "MUST require every diff-review finding that claims broader impact to name the concrete callers/files/functions that are provably affected, and keep each finding comment to one matter-of-fact paragraph that states the triggering scenario or inputs.",
    "MUST consume CAS `reviewResult` output for diff-review findings and normalize its camelCase fields back into the local bookkeeping with `[P0]`..`[P3]` titles, numeric `priority`, tight diff-overlapping `code_location`, and an `overall_correctness` verdict.",
    "MUST NOT pass steady-state `--custom-instructions` to `cas review_session start` when detached CAS is in use; the `review/start` target owns the reviewer rubric for normal git-backed `$fix` rounds.",
    "MUST NOT fall back to native `codex review` when CAS returns `failureCode=wait_timed_out|review_failed|review_interrupted|approval_denied`; those are transport/runtime failures that must be retried on the same `reviewThreadId` or reported, not masked.",
    "MUST use a cumulative long-poll wait budget before declaring review transport blocked: for detached CAS waits, keep waiting on the same `reviewThreadId` across a run-local timeout ladder of `60000`, `120000`, `300000`, and `600000` ms (total `1080000` ms) before stopping blocked; for native fallback on the same frozen review context, continue polling/waiting up to that same cumulative budget before declaring the review lane blocked.",
    "MUST enumerate every PROVEN_USED external surface touched by code/docs/examples before closing the core-pass phase.",
    "MUST assign each enumerated public/documented surface exactly one dedicated proof hook or one explicit blocker; a sibling or nearby proof hook does not discharge another advertised form.",
    "MUST NOT accept a heuristic fallback or compatibility-sensitive public-seam change as done while the advertised/documented form it changes is still unproven.",
    "MUST NOT mark a diff-review finding stale when it targets a PROVEN_USED external surface that still lacks a dedicated proof hook or explicit blocker.",
]

REQUIRED_DIFF_REVIEW_INTENT_PHRASES = [
    "### Diff review finding bar (required)",
    "Flag only discrete, actionable bugs introduced by the diff that materially impact correctness, performance, security, or maintainability.",
    "Apply the author-fix-worthiness bar: the issue should be something the original author would likely fix if it were pointed out.",
    "Do not rely on unstated assumptions about intent or environment; when claiming broader impact, identify the concrete callers/files/functions that are provably affected.",
    "Prefer no findings over weak findings.",
    "### Diff review comment bar (required)",
    "Keep the body to one paragraph in a matter-of-fact tone. Explain why it is a bug, how severe it is in context, and the scenario or inputs required for it to arise.",
    "### Diff review priority bar (required)",
    "Mirror the title priority in numeric `priority` using `0` for `P0`, `1` for `P1`, `2` for `P2`, and `3` for `P3`.",
    "### Diff review output schema (required)",
    '"overall_correctness": "\\"patch is correct\\" | \\"patch is incorrect\\""',
    "The diff review output is JSON-only: no fences, no prose, no fix patch.",
    "### Review transport selection (required)",
    "Standard branch-backed `$fix` closure reviews the whole frozen branch diff, not just the local fix seam; keep the same review target for native, detached CAS, and native fallback unless preflight explicitly selected commit/worktree scope.",
    "Do not paste the built-in review prompt into this skill or pass steady-state `--custom-instructions`; when detached CAS is selected, the `review/start` target owns the reviewer rubric internally.",
    "Reserve `--custom-instructions` for explicit custom-review runs only; do not use it for normal git-backed `$fix` rounds.",
    "Normalize the chosen review transport's output into the local `local_findings` / `blocked_findings` / `stale_findings` bookkeeping plus `overall_correctness`. When `review_transport=cas`, consume CAS `reviewResult` JSON; when `review_transport=native|native_fallback`, normalize native `codex review` output to that same schema.",
    "If CAS exits with `failureCode=wait_timed_out`, keep waiting on the same `reviewThreadId` across the frozen timeout ladder `60000`, `120000`, `300000`, `600000` until either a verdict arrives or the cumulative `review_wait_budget_ms=1080000` is exhausted.",
    "If `review_transport=native|native_fallback`, keep the native review on that same frozen whole-diff review target and allow it up to the same `review_wait_budget_ms=1080000` wall-clock budget before declaring the lane blocked.",
]

FORBIDDEN_REFINE_ROUTING_PHRASES = [
    "- `$refine`: default path when the task is to improve `fix` itself (or other skills); apply `$refine` workflow and `quick_validate`.",
    "- Run `$refine` when the requested target is a skill artifact (for example `SKILL.md`, `agents/openai.yaml`, skill scripts/references/assets).",
    "MUST route skill-self edits (for example `codex/skills/fix`) through `$refine` and run `quick_validate`.",
    "If the requested target is this skill (or another skill), route through `$refine`:",
]

REQUIRED_REFERENCE_PHRASES = [
    "**Review reconciliation**",
    "Provenance: Origin=`review_seed`; Seeded review=`yes`",
    "Provenance: Origin=`proof_hook`; Seeded review=`no`",
    "post-self-review final-diff closure rounds against the unchanged final diff",
    "`P0 Core Review` iterations belong in `Pass trace`, not `Review loop trace`.",
    "Each `R#` row comes from a fresh isolated review invocation on the frozen review context.",
    "review_wait_budget_ms=1080000",
    "review_wait_timeout_ladder_ms=60000,120000,300000,600000",
    "review_transport=`<native|cas|native_fallback>`",
    "fallback_reason=`<none|missing_cas_dependency|missing_codex_binary|incompatible_codex_review_runtime|review_output_missing|parent_thread_not_materialized|unsafe_parent_thread_state>`",
    "In the terminal final-diff closure round, blocked findings cannot use `scope_guardrail`, and closure still requires `blocked_findings=0`.",
    "Use stale suppression only when a dedicated proof hook/blocker already discharges the repeated finding or the targeted diff hunk/form is gone, and terminal closure still requires `stale_findings=0`.",
    "Use `skip_missing_base_context` only when there is no live git diff and no derivable review target; a live git diff must derive review context or stop blocked.",
    "Cycle <c>: Pass <n>/<total_planned>:",
    "one clean terminal row by default and two consecutive clean `R#` rows only after terminal-review-driven edits or `review_transport=native_fallback`.",
    "`Cycle C1` -> zero_edit_cycle_streak=`0`",
    "**Pass trace**",
    "**Review loop trace**",
    "skip_not_git_repo",
    "skip_missing_base_context",
    "blocked_findings=`1`",
    "stale_findings=`1`",
    "## Public surface proof coverage",
    "## P2 footgun closure on a public surface",
    "## Adjacent seam footgun without widened closure",
    "## Clean close with no actionable footguns",
    "`P2 Footguns` -> `done`",
    "`P3 Surface + Audit` -> `done`",
    "no actionable footguns remain",
    "adjacent seam",
    "Proof target:",
]

REQUIRED_PROOF_COVERAGE_PHRASES = [
    "### Surface proof coverage (deterministic)",
    "A failing/proving hook for one lexical lane does not discharge a different advertised/documented form on the same public surface.",
    "If a public seam fix introduces a heuristic fallback, unresolved-default, or compatibility-sensitive narrowing, treat that seam as unproved until the exact advertised/documented form is covered by a dedicated proof hook or blocker.",
]

REQUIRED_POST_FIX_BOUNDARY_GUARDRAILS = [
    "Stop only after self-review exhausts actionable changes, each full cycle reaches post-self-review rerun plus terminal diff-review closure, and any required confirmation cycles are clean.",
    "Make risky or unclear code safe with the smallest sound, validated change, then keep rerunning the whole `$fix` skill as an outer fixed-point loop until no actionable self-review change remains, no actionable footgun on the touched surfaces or adjacent seam remains unresolved, and the unchanged final diff is review-clean under the frozen whole-diff review context. By default, a cycle closes after one clean terminal diff-review round plus one zero-edit clean cycle on the unchanged fingerprint; require a confirming clean terminal round only when the same cycle had a terminal-review-driven edit or used `review_transport=native_fallback`, and require a second zero-edit clean cycle only when the first clean cycle included self-review edits, terminal-review edits, or `native_fallback`. Broader architecture, product, or roadmap analysis belongs to another skill.",
    "MUST stop `$fix` once no new actionable self-review change remains, no actionable footgun on the touched surfaces or adjacent seam remains unresolved, the current cycle reaches clean terminal final-diff review closure, and any required zero-edit confirmation cycles are complete; do not continue under `$fix` into broader architecture, product, roadmap, or conceptual analysis.",
    "MUST, if the user asks for broader or bolder analysis after a clean or closed `$fix` pass, close the `$fix` deliverable first and recommend the next skill explicitly (`$grill-me`, `$parse`, `$plan`, or `$creative-problem-solver`) instead of continuing under `$fix`.",
    "If a clean or closed `$fix` pass surfaces broader non-fix opportunities, do not continue exploring them under `$fix`.",
    "Do not place those broader opportunities in `Residual risks / open questions` unless a valid blocker from the allowed set applies.",
    '`Review loop trace` includes either a skip line or cycle-annotated `R#` rows. A closing cycle shows one clean terminal final-diff review row on the unchanged final diff by default, and two consecutive clean rows only when the same cycle had a terminal-review-driven edit or used `review_transport=native_fallback`; every closing row still requires `local_findings=0`, `blocked_findings=0`, `stale_findings=0`, and `overall_correctness="patch is correct"`.',
]

REQUIRED_FIXED_POINT_GUARDRAILS = [
    "MUST treat `$fix` as a whole-skill outer fixed-point loop: complete the current cycle through post-self-review rerun plus terminal final-diff review closure, then decide whether to restart from preflight using the same frozen review context.",
    "MUST record `cycle_index`, `cycle_edit_tally`, `zero_edit_cycle_streak`, and `review_context_receipt` for each full cycle; use `git diff --no-ext-diff <comparison_sha>` as the fingerprint source for review-backed cycles.",
    "MUST count a cycle as zero-edit only when `cycle_edit_tally=0` and the cycle's review-context receipt is unchanged (`fingerprint=same` for review-backed runs or the same skip reason for skipped-review runs).",
    "MUST require a second zero-edit full cycle only when the first clean zero-edit cycle included self-review edits, terminal-review edits, or `review_transport=native_fallback`; otherwise the first clean zero-edit cycle is sufficient for closure.",
    "MUST NOT add a new top-level transcript section for cycle reporting; keep cycle visibility inside runtime pass updates, `Pass trace`, and `Review loop trace`.",
    "MUST NOT add an explicit outer-cycle cap; keep looping until the required zero-edit confirmation cycles are complete or another existing blocker stops the run.",
    "4. Runtime pass updates (`Cycle <c>: Pass <n>/<total_planned>: ...`) were emitted during execution.",
]

FORBIDDEN_STALE_SELF_REVIEW_PHRASES = [
    "MUST answer that question internally, apply at most one new fix-worthy change per self-round, re-run validation, and repeat until a self-round yields no new fix-worthy finding or only blocked changes.",
    "MUST stop `$fix` once no new fix-worthy finding remains; do not continue under `$fix` into broader architecture, product, roadmap, or conceptual analysis.",
    "If the answer yields no new fix-worthy finding, record `stop_reason=no_new_fix_worthy_findings` and exit the loop.",
    "stop_reason=`<continue|no_new_fix_worthy_findings|blocked>`",
    "No new fix-worthy findings remain under the current guardrails.",
    "No new fix-worthy findings remain on the final validated changeset.",
    "No further fix-worthy adjustments remain.",
    "Because the best self-review idea was architectural, not fix-shaped.",
    "changing the helper shape would not be a bug repair, it would be a product/API redesign",
    "there was no failing proof hook for that concern, only a readability/ergonomics argument",
]

FORBIDDEN_USER_LOOP_PHRASES = [
    "MUST ask the final user-directed changeset question only after at least one change is applied and validation is passing.",
    "MUST NOT emit `If you could change one thing about this changeset what would you change?` as a standalone first/only response.",
    "MUST, when the user-directed changeset loop precondition gate passes, append the exact question as the final line of the assistant message (after the required sections) and then stop.",
    "MUST run a final user-directed changeset loop: ask `If you could change one thing about this changeset what would you change?`, apply exactly one requested change at a time, re-run validation, and repeat until the user has no more requested changes.",
    "### 7) User-directed changeset loop (required final step when a changeset exists)",
    "If the user-directed changeset loop precondition gate passes (`Changes applied` is not `None` AND the latest validation result is `ok`), append the exact question as the final line after the last section, then stop:",
    "the final line of the message is exactly: `If you could change one thing about this changeset what would you change?`",
]

SECTION_PATTERN = re.compile(r"^\*\*(.+?)\*\*$", re.MULTILINE)
JSON_LINE_PATTERN = re.compile(
    r"^\s*-\s*`(\{.*\})`\s*\(single-line JSON\)\s*$", re.MULTILINE
)


def line_no(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def extract_block(text: str, start_marker: str, end_marker: str) -> tuple[str, int]:
    start = text.find(start_marker)
    if start < 0:
        raise ValueError(f"missing marker: {start_marker!r}")
    end = text.find(end_marker, start)
    if end < 0:
        raise ValueError(f"missing marker: {end_marker!r}")
    return text[start:end], start


def extract_heading_lines(
    block: str, base_offset: int, full_text: str
) -> list[tuple[str, int]]:
    results: list[tuple[str, int]] = []
    for match in SECTION_PATTERN.finditer(block):
        heading = match.group(1).strip()
        results.append((heading, line_no(full_text, base_offset + match.start())))
    return results


def extract_validation_json_keys(
    block: str, base_offset: int, full_text: str, label: str, errors: list[str]
) -> list[str] | None:
    validation_idx = block.find("**Validation**")
    if validation_idx < 0:
        errors.append(f"{label}: missing **Validation** section")
        return None

    post_validation = block[validation_idx:]
    match = JSON_LINE_PATTERN.search(post_validation)
    if not match:
        errors.append(
            f"{label}: missing single-line JSON template under Validation "
            f"(line {line_no(full_text, base_offset + validation_idx)})"
        )
        return None

    raw_json = match.group(1)
    raw_line = line_no(full_text, base_offset + validation_idx + match.start())
    try:
        parsed = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        errors.append(f"{label}: parse_error at line {raw_line}: {exc.msg}")
        return None

    keys = list(parsed.keys())
    if keys != EXPECTED_VALIDATION_KEYS:
        errors.append(
            f"{label}: validation_json_keys mismatch at line {raw_line}: "
            f"expected={EXPECTED_VALIDATION_KEYS} actual={keys}"
        )
    return keys


def check_heading_order(
    found: list[tuple[str, int]], expected: list[str], label: str, errors: list[str]
) -> None:
    found_names = [name for name, _ in found]
    if found_names != expected:
        errors.append(
            f"{label}: heading_order mismatch: expected={expected} actual={found_names}"
        )


def extract_heading_section(
    block: str, heading: str, next_heading: str | None, label: str, errors: list[str]
) -> tuple[str, int] | None:
    start_match = re.search(rf"(?m)^\*\*{re.escape(heading)}\*\*$", block)
    if not start_match:
        errors.append(f"{label}: missing **{heading}** section")
        return None

    start = start_match.start()
    if next_heading is None:
        end = len(block)
    else:
        end_match = re.search(
            rf"(?m)^\*\*{re.escape(next_heading)}\*\*$", block[start + 1 :]
        )
        if not end_match:
            errors.append(
                f"{label}: missing **{next_heading}** section after **{heading}**"
            )
            return None
        end = start + 1 + end_match.start()
    return block[start:end], start


def require_line(
    section: str,
    expected_line: str,
    label: str,
    section_name: str,
    section_line: int,
    errors: list[str],
) -> None:
    if expected_line not in section:
        errors.append(
            f"{label}: missing template line in **{section_name}** "
            f"(line {section_line}): {expected_line}"
        )


def run(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []

    try:
        main_block, main_offset = extract_block(
            text, "## Deliverable format (chat)", "### Fix Record (embedded mode only)"
        )
        embedded_block, embedded_offset = extract_block(
            text, "### Fix Record (embedded mode only)", "## Pitfalls"
        )
    except ValueError as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        return 1

    main_headings = extract_heading_lines(main_block, main_offset, text)
    embedded_headings = extract_heading_lines(embedded_block, embedded_offset, text)
    check_heading_order(main_headings, EXPECTED_MAIN_HEADINGS, "main", errors)
    check_heading_order(
        embedded_headings, EXPECTED_EMBEDDED_HEADINGS, "embedded", errors
    )

    main_keys = extract_validation_json_keys(
        main_block, main_offset, text, "main", errors
    )
    embedded_keys = extract_validation_json_keys(
        embedded_block, embedded_offset, text, "embedded", errors
    )
    if main_keys and embedded_keys and main_keys != embedded_keys:
        errors.append(
            f"validation_json_sync mismatch: main={main_keys} embedded={embedded_keys}"
        )

    for label, block, offset in (
        ("main", main_block, main_offset),
        ("embedded", embedded_block, embedded_offset),
    ):
        reconciliation = extract_heading_section(
            block, "Review reconciliation", "Findings (severity order)", label, errors
        )
        if reconciliation:
            reconciliation_block, reconciliation_start = reconciliation
            reconciliation_line = line_no(text, offset + reconciliation_start)
            for expected_line in EXPECTED_RECONCILIATION_LINES:
                require_line(
                    reconciliation_block,
                    expected_line,
                    label,
                    "Review reconciliation",
                    reconciliation_line,
                    errors,
                )

        findings = extract_heading_section(
            block, "Findings (severity order)", "Changes applied", label, errors
        )
        if findings:
            findings_block, findings_start = findings
            findings_line = line_no(text, offset + findings_start)
            for expected_line in EXPECTED_FINDINGS_LINES:
                require_line(
                    findings_block,
                    expected_line,
                    label,
                    "Findings (severity order)",
                    findings_line,
                    errors,
                )

        review = extract_heading_section(
            block, "Review loop trace", "Pass trace", label, errors
        )
        if review:
            review_block, review_start = review
            review_line = line_no(text, offset + review_start)
            for expected_line in EXPECTED_REVIEW_LINES:
                require_line(
                    review_block,
                    expected_line,
                    label,
                    "Review loop trace",
                    review_line,
                    errors,
                )

        pass_trace = extract_heading_section(
            block, "Pass trace", "Validation", label, errors
        )
        if pass_trace:
            pass_block, pass_start = pass_trace
            pass_line = line_no(text, offset + pass_start)
            for expected_line in EXPECTED_PASS_LINES:
                require_line(
                    pass_block,
                    expected_line,
                    label,
                    "Pass trace",
                    pass_line,
                    errors,
                )

        self_review = extract_heading_section(
            block,
            "Self-review loop trace",
            "Residual risks / open questions",
            label,
            errors,
        )
        if self_review:
            self_review_block, self_review_start = self_review
            self_review_line = line_no(text, offset + self_review_start)
            for expected_line in EXPECTED_SELF_REVIEW_LINES:
                require_line(
                    self_review_block,
                    expected_line,
                    label,
                    "Self-review loop trace",
                    self_review_line,
                    errors,
                )

        residual = extract_heading_section(
            block, "Residual risks / open questions", None, label, errors
        )
        if residual:
            residual_block, residual_start = residual
            residual_line = line_no(text, offset + residual_start)
            require_line(
                residual_block,
                EXPECTED_RESIDUAL_LINE,
                label,
                "Residual risks / open questions",
                residual_line,
                errors,
            )

    for phrase in REQUIRED_SELF_LOOP_GUARDRAILS:
        if phrase not in text:
            errors.append(f"self_loop_guardrail missing required phrase: {phrase}")

    for phrase in REQUIRED_REVIEW_LOOP_GUARDRAILS:
        if phrase not in text:
            errors.append(f"review_loop_guardrail missing required phrase: {phrase}")

    for phrase in REQUIRED_DIFF_REVIEW_INTENT_PHRASES:
        if phrase not in text:
            errors.append(f"diff_review_intent missing required phrase: {phrase}")

    for phrase in REQUIRED_FOOTGUN_GUARDRAILS:
        if phrase not in text:
            errors.append(f"footgun_guardrail missing required phrase: {phrase}")

    for phrase in REQUIRED_PROOF_COVERAGE_PHRASES:
        if phrase not in text:
            errors.append(f"proof_coverage_guardrail missing required phrase: {phrase}")

    for phrase in REQUIRED_POST_FIX_BOUNDARY_GUARDRAILS:
        if phrase not in text:
            errors.append(
                f"post_fix_boundary_guardrail missing required phrase: {phrase}"
            )

    for phrase in REQUIRED_FIXED_POINT_GUARDRAILS:
        if phrase not in text:
            errors.append(f"fixed_point_guardrail missing required phrase: {phrase}")

    for phrase in FORBIDDEN_USER_LOOP_PHRASES:
        if phrase in text:
            errors.append(f"forbidden_user_loop_phrase still present: {phrase}")

    for phrase in FORBIDDEN_STALE_SELF_REVIEW_PHRASES:
        if phrase in text:
            errors.append(f"forbidden_stale_self_review_phrase still present: {phrase}")

    for phrase in FORBIDDEN_REFINE_ROUTING_PHRASES:
        if phrase in text:
            errors.append(f"forbidden_refine_routing_phrase still present: {phrase}")

    reference_path = path.parent / "references" / "self_review_loop_examples.md"
    if not reference_path.exists():
        errors.append(f"reference_examples missing: {reference_path}")
    else:
        reference_text = reference_path.read_text(encoding="utf-8")
        for phrase in REQUIRED_REFERENCE_PHRASES:
            if phrase not in reference_text:
                errors.append(f"reference_examples missing required phrase: {phrase}")
        if re.search(
            r"blocked_findings=`[1-9][0-9]*`.*result=`local_clean`", reference_text
        ):
            errors.append(
                "reference_examples contains blocked_findings>0 with result=local_clean"
            )
        if re.search(
            r"stale_findings=`[1-9][0-9]*`.*result=`local_clean`", reference_text
        ):
            errors.append(
                "reference_examples contains stale_findings>0 with result=local_clean"
            )
        if re.search(
            r"overall_correctness=`patch is incorrect`.*result=`local_clean`",
            reference_text,
        ):
            errors.append(
                "reference_examples contains patch is incorrect with result=local_clean"
            )

    if errors:
        print("[FAIL] fix skill contract lint errors:", file=sys.stderr)
        for err in errors:
            print(f" - {err}", file=sys.stderr)
        return 1

    print(f"[OK] fix skill contract checks passed: {path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint fix skill contract sections.")
    parser.add_argument(
        "path",
        nargs="?",
        default="codex/skills/fix/SKILL.md",
        help="Path to fix SKILL.md (default: codex/skills/fix/SKILL.md)",
    )
    args = parser.parse_args()
    return run(Path(args.path))


if __name__ == "__main__":
    raise SystemExit(main())
