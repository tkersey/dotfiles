# Synoptic GitHub action tools

GitHub remains the durable source of truth. These model tools are the only
route from conversation into Synoptic's action broker.

## `synoptic.search_unresolved_threads`

Read-only. Assigned-file unresolved threads are already in initial context.
Call this only when a candidate concern appears cross-file. Use narrow paths
and a semantic query where possible; set `includeWholePullRequest` only when
the cross-file concern requires it. Results are bounded pages. When `next` is
not `null`, call the tool again with its `threadOffset` and `commentOffset`;
continue until `next` is `null` before treating the search as complete.

## `synoptic.prepare_github_action`

Creates an immutable in-memory pending card and performs no GitHub effect.
Call it only after an explicit human request to prepare or take the action,
never during the initial review.

Input fields:

- `slot`: stable session-local logical action identity.
- `kind`: `add_inline_comment`, `reply_thread`, `resolve_thread`,
  `unresolve_thread`, `update_comment`, `delete_comment`, `mark_viewed`,
  `unmark_viewed`, or `graphql`.
- `effectSummary`: exact human-readable effect.
- `payload`: exact typed target/body data, or for `graphql`, the operation name,
  mutation document, variables, and effect summary.

A replacement in the same slot supersedes the prior pending card. The UI card
is not editable; revise through conversation. Confirmation is a separate human
act and execution is server-side through fixed `gh api graphql` argv. Never
claim success from card creation.

For inline comments, bind the current path, RIGHT/LEFT diff side, exact line
and optional start line, and exact body. For replies or thread mutations, use
the exact current thread ID. Transparent GraphQL is allowed only for an
explicitly requested operation and must expose the full mutation and variables
for confirmation.

## `synoptic.complete_file_review`

This is the sole confirmation exception. Call it only when the immediately
governing human instruction unambiguously asks to complete or mark the file
reviewed. A clean review is not authorization. The server will reject stale or
non-official sessions and removes the file from the queue only after GitHub
mutation plus `VIEWED` read-back. The tab stays open.

## `synoptic.close_session`

Call only after an unambiguous human close instruction. It closes the local tab
and session, interrupting an active turn if necessary. It never changes viewed
state.

An action may be `pending`, `superseded`, `rejected`, `executing`, `succeeded`,
`failed`, `outcome-unknown`, or `invalidated`. When mutation delivery is
ambiguous, do not ask for an automatic retry; explain the reconciled evidence
and wait for human direction.
