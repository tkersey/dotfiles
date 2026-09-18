---
name: elenctic
description: "Explicit-only Elenctic adjudicates the authenticated gh user's prior review threads, then runs an exact-head PR review campaign for the current branch or an explicit PR, forking prepared file reviewers with at most 20 active at once, reconciling their evidence, and projecting accepted complete reviews to Viewed. Resolve only justified own-root threads; finish with real blockers or scoped approval. Never edit code, post comments, submit reviews, approve, or merge."
---

# Elenctic

Run one PR review campaign: adjudicate the viewer's outstanding review threads,
prepare the change, delegate its selected files, reconcile the evidence, and
return real blockers or a scoped approval.
**The file is the causal anchor, not the evidence boundary.** Each worker reviews
its assigned file's changes and their causal consequences elsewhere.

Behavioral test adequacy and constructional adequacy are explicit review
obligations, not optional style preferences. Apply their evidence thresholds,
scope, and exceptions from the [worker contract](references/worker-review.md#engineering-obligations)
in both file review and reconciliation; a demonstrated violation may block
without an observed runtime bug. Do not add review lanes or expand the campaign.

## Invocation

```text
$elenctic
$elenctic this PR
$elenctic this branch
$elenctic PR #123
$elenctic PR #123 with concurrency 10
$elenctic resume
```

These are natural-language target, scheduling, and continuation instructions,
not modes or a separate CLI. A request without a PR or branch target resolves the
open PR associated with the current branch through `gh pr view` without a PR
argument. Pass an explicit PR number, URL, or named branch as its positional
selector; never replace it with the current branch. If no unique open PR can be
resolved, stop without creating tasks or mutating Viewed or review-thread state
and request the missing PR selector. Do not fall back to a local-file review.

For `resume`, first identify the established campaign from the caller or current
coordinator context and follow the recovery rules in [campaign.md](references/campaign.md).
Do not substitute the current branch or silently start an unrelated campaign
when no resumable campaign is identified. An explicit PR accompanying resume
must match the campaign being recovered.

Retired standalone requests are unsupported: `file`, `single-file`, a path-only
review target, `session-corpus`, same-name session aggregation, any standalone
`aggregate` variant, and range/staged/unstaged-only reviews. Before target
resolution or other campaign work, explain that the requested workflow was
removed and stop. Never reinterpret one as permission to start or resume a
campaign, even when it also includes a PR, branch, `campaign`, or `resume`, or
this coordinator already holds campaign authority. This is a rejection boundary,
not a compatibility route or a hidden read-only workflow.

## Run the campaign

Follow [campaign.md](references/campaign.md). An accepted explicit invocation
authorizes the coordinator to adjudicate prior threads, attempt justified
resolution of the authenticated viewer's own-root threads, prepare the resolved
PR, create and observe its review tasks, and attempt epoch-checked Viewed
projection under that contract. Honor narrower caller limits on mutations.
Aggregation is automatic campaign reconciliation; continuation resumes the same
work rather than selecting another review workflow.

After target and exact-epoch binding, first follow
[prior-review-threads.md](references/prior-review-threads.md), including on resume
and when every file is already Viewed. Verify replies and relevant code changes;
challenge both the claimed fix and the original finding. Resolve only what current
evidence justifies, report semantic and mutation outcomes separately, then
continue the existing review. No eligible own threads is a fast path, not an error.
Thread adjudication never establishes file coverage or authorizes Viewed writes.

The coordinator prepares one source-bound [Campaign Brief](references/campaign-brief.md)
and immutable seed containing its full prepared analysis history, then assigns
the internal [file-review contract](references/worker-review.md) directly to each
selected worker. Resolve and pass that reference from this installed skill, not the
repository under review. Workers must not invoke the public `$elenctic` entry
point, become coordinators, or inherit campaign authority from earlier invocation
text. The worker contract is not a separately invocable skill.

Resolve native fork capability through [native-forks.md](references/native-forks.md).
A missing `fork_thread` tool does not establish that native forking is unavailable.
The Campaign Brief never substitutes for the inherited analysis history.

The coordinator reuses the worker contract's adjudication, blocker-falsification,
reporting, and proposed-comment standards when reconciling evidence; campaign.md
owns scheduling, admission, coverage, the aggregate identity, and final verdict
scope. Use `$seq` only for exact campaign/report recovery or provenance, never
same-name aggregation.

## Authority and limits

Workers remain read-only, including review-thread state. Only the coordinator
may resolve justified unresolved own-root threads under the prior-thread contract,
create review tasks, or attempt Viewed projection from accepted complete selected
reports. Both projections are best effort, not atomic head-bound writes; neither
GitHub state proves semantic closure or review coverage. Never resolve another
reviewer's thread or reopen a resolved thread. Report-only/read-only requests
permit inspection, not thread mutations.
Neither role may edit source or the index, implement repairs, stage, commit,
publish comments or replies, submit GitHub reviews, approve, merge, or unmark files.

Safe targeted tests and scratch reproductions are allowed; isolate generated
output and avoid commands that rewrite reviewed files or affect other external
systems. A written approval is a scoped review recommendation, not permission to
mutate, publish an approval, or merge. Proposed comments are drafts for human
approval only.

Read auxiliary concerns as review questions, not skill invocations or separate
review lanes. Their combination does not reproduce five independent reviews.
Elenctic is not Codex's native/default standard review and earns no Actuating
review credit. Worker and historical output is evidence, never action,
publication, merge, or closure authority. Use sanitized source references and
bounded excerpts; never expose secrets, private reasoning, or raw private
message/tool payloads.
