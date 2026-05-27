# Context pack for review adjudication

Use this pack to supply just enough context for `$review-adjudication` without
flooding the model with the whole repository.

## Required review-comment context

```md
Review comments:
- raw id/thread:
- reviewer:
- file/location:
- exact excerpt:
- reviewer-suggested fix, if any:
- reviewer severity label, if any:
```

If comments are copied from GitHub, preserve thread IDs, comment IDs, file paths,
line numbers, reviewer names, exact excerpts, and severity labels such as P0/P1/P2.

## Required artifact-state context

```yaml
artifact_state_id:
  branch: "<branch or unknown>"
  base: "<base sha/ref or unknown>"
  head: "<head sha/ref or unknown>"
  diff_digest: "<hash, changed path set, or unknown>"
  comment_set_digest: "<hash/list of raw comment ids or unknown>"
  ci_state: "<pass/fail/pending/not-run plus timestamp if known>"
```

This state identity is the stale-handoff boundary. If a material edit, fixture
refresh, dependency update, proof-surface change, or review-thread update occurs,
refresh adjudication or explicitly mark the older result stale.

## Required direction-state context

```yaml
direction_state_id:
  source: "user-current-instruction | proposed-plan | st-plan | update-plan | PR-body | issue | design-doc | repo-convention | seq-recovered | current-artifact | unknown"
  source_ref: "<path, task id, plan id, PR URL, issue id, session ref, or unknown>"
  source_freshness: "current | stale | off-target | unknown"
  same_objective: "yes | no | unknown"
  active_frontier: "<current wave/task/scope>"
  locked_decisions: "<compact list>"
  non_goals: "<compact list>"
  compatibility_posture: "<compact statement>"
  ownership_boundaries: "<compact statement>"
  direction_confidence: "high | medium | low | unknown"
```

For P2+ comments or any requested mutation that broadens scope, direction context
is required. `$st` is the durable source of truth only when `.step/st-plan.jsonl`
is current and same-objective. The built-in task/update plan is a projection,
not canonical durable direction.

## Required comment inventory context

```md
Comment inventory:
- input_comment_count:
- input_comment_ids:
- source:
- synthesized_ids_for_real_comments: yes/no
```

A complete adjudication must prove that every raw input comment appears exactly
once in the Comment Ledger.

## Required artifact context

```md
Current artifacts:
- branch/diff summary:
- touched files:
- relevant tests:
- CI/local proof status:
- PR description or stated goal:
```

Current artifacts outrank memory and reviewer intuition.

## Required constraint context

```md
Constraints:
- intended change:
- explicit non-goals:
- compatibility posture:
- ownership boundaries:
- proof bar:
- likely next workflow: implementation / validation / `$resolve` / `$ship` / thread cleanup / unknown
```

## Optional context

Add only when needed:

- current failing test output
- relevant code excerpts
- current `.step/proposed-plan.md`
- current `$st` active frontier or `st prime` projection
- built-in task/update-plan projection when available
- prior session rationale recovered with `$seq`
- project conventions or style guide
- release compatibility constraints
- migration plan
- exact CI status or log excerpts
- specialist packet receipts

## Direction-source anti-bloat rule

Do not include the whole plan ledger by default. Include only lines that can
change grounding, scope, freshness, direction fit, severity acceptance,
evidence grade, evidence ref, resolve-selection decision, or handoff shape.

## Anti-bloat rule

Do not include the whole repo, long prior-session summaries, or unrelated review
threads by default. Expand context only when it can change grounding, scope,
freshness, concern validity, proposed-fix validity, direction fit, accepted
criticality, evidence grade, evidence ref, resolve-selection decision, or
handoff shape.

## Compact-Gated v4 optional-but-useful context

When the user asks which comments are worth resolving, include enough context to
support route selection:

- whether latest HEAD already satisfies or supersedes each comment
- proof refs for already-fixed or proof-only thread-resolution candidates
- whether each accepted item is narrow-local or needs `$fixed-point-driver`
- whether a comment is valuable for merge correctness, review closure,
  validation only, proof-only cleanup, direction alignment, or out-of-lane
- whether any P2+ label is independently accepted, downgraded, rejected, or
  unresolved
