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
```

If comments are copied from GitHub, preserve thread IDs, comment IDs, file paths,
line numbers, reviewer names, and exact excerpts.

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
- prior session rationale recovered with `$seq`
- project conventions or style guide
- release compatibility constraints
- migration plan
- exact CI status or log excerpts
- specialist packet receipts

## Anti-bloat rule

Do not include the whole repo, long prior-session summaries, or unrelated review
threads by default. Expand context only when it can change grounding, scope,
freshness, concern validity, proposed-fix validity, evidence grade, evidence ref, resolve-selection decision,
or handoff shape.
