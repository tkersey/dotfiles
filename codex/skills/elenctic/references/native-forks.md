# Native forks and prepared history

Use this reference when resolving campaign capabilities, creating the prepared
seed, or forking a reviewer. Preserve the coordinator's full prepared analysis
history. A copied Campaign Brief, fresh task, or fork of the evolving coordinator
does not satisfy that requirement.

## Resolve the operation, not just the tool name

Inspect the actual tool schema and history semantics. `spawn_agent` with
`fork_turns: "all"` inherits its caller's history; it does not select an immutable
seed by ID. It is not the campaign's explicit-seed operation.

Codex 0.153.4 distinguishes three surfaces:

- The TUI disables its thread tools in embedded mode. The non-MCP dynamic
  surface also removes delegation tools, including `fork_thread`; the TUI MCP
  surface exposes them. The executable version alone does not select the surface.
- The TUI `fork_thread` wrapper copies completed history only. A self-fork cuts
  before the calling turn, so it omits analysis and a brief prepared in that turn.
- Native app-server `thread/fork` accepts a source `threadId`, copies stored
  history, and returns `forkedFromId`. Without a history cut, it can retain the
  persisted preparation in an unfinished turn, recording interruption in the
  child. Verify the retained history; do not mistake that marker for missing work.

These are version-bound observations, not permanent feature assumptions. Sources:
[TUI transport](https://github.com/openai/codex/blob/rust-v0.153.4/codex-rs/tui/src/dynamic_tools_mcp.rs),
[TUI selection](https://github.com/openai/codex/blob/rust-v0.153.4/codex-rs/tui/src/app_server_session.rs),
[fork wrapper](https://github.com/openai/codex/blob/rust-v0.153.4/codex-rs/tui/src/dynamic_tools.rs),
and [app-server protocol](https://learn.chatgpt.com/docs/app-server#start-or-resume-a-thread).
Inspect the installed schema and actual source history on other versions.

Use an exposed wrapper only when its cut includes all preparation, its reads
expose complete retained history, and its input limit accepts the canonical
assignment unchanged. If any condition fails, load `$cas` and use its native
app-server transport. The 0.153.4 TUI message wrapper limits input to 1,000 UTF-8
bytes; use native `turn/start` instead of shortening an oversized assignment.
Do not change global Codex settings, switch models, or start summary-based
sessions to obtain a tool name.

## Use CAS's existing app-server transport

Follow CAS's compatibility gate for the exact executable and selected transport.
For a stateful local stream:

```bash
cas app-server preflight --cwd <repo> --profile core --app-server-transport stdio --json
cas app-server session --listen stdio://
```

Keep that session alive for requests, notifications, and running worker turns.
Initialize the connection once, including `experimentalApi: true` when using
pagination or `excludeTurns`, and send `initialized` before other requests.
For an explicit remote endpoint, use CAS's corresponding transport and prove
that endpoint can read the source; a fresh local server is not its substitute.

Resolve the coordinator's actual source thread ID from the runtime or
`CODEX_THREAD_ID`, then verify it with `thread/read`. Never guess the source from
a title, current directory, latest-session search, or another thread's ID.
Capability discovery happens before deep preparation; history verification
happens after preparation and before reviewer launch.

Use these native operations on the same connection:

| Operation | Request and required result |
|---|---|
| Read source | `thread/read` with the exact `threadId`; read all preparation items, using `includeTurns: true` or complete turn/item pagination. |
| Create seed | `thread/fork` with the coordinator's `threadId`; require a fresh ID and `forkedFromId` equal to the coordinator. |
| Create reviewer | `thread/fork` with the unchanged seed's `threadId`; require a fresh ID and `forkedFromId` equal to the seed. |
| Assign reviewer | `turn/start` with the verified reviewer's ID and the canonical assignment as text input; retain the returned turn ID. |
| Collect | Consume the matching `turn/completed` notification, then read that exact worker turn and report; bound waits and replenish the existing sliding window. |

For seed creation after current-turn preparation, omit `lastTurnId` and
`beforeTurnId`; either can cut off the analysis. A completed-boundary selector
is valid only when that completed turn already includes all preparation.
`excludeTurns: true` omits history from the response, not the fork's context;
read back the retained history separately. Prefer persistent seeds and workers
so recovery does not depend on one in-memory connection.

Native forks load configuration as well as history. Preserve the prepared
source's resolved model and reasoning effort explicitly when server defaults
differ, and verify the realized repository and permission settings before
assignment. Repeating the existing selection is not authority to choose a new
model, weaken permissions, or replace inherited instructions.

`cas instance_runner --instances 1` can perform isolated stored-thread reads or
forks. Its `--raw-sample` result is JSON text inside `sample_results[].raw_result`;
decode it before inspecting fields. It executes one request and exits, so do not
use it to own a worker's `turn/start` lifecycle. Use the persistent session above.

Capture raw replies in private scratch storage and inspect them without echoing
inherited messages, reasoning payloads, or raw tool output. Expose only sanitized
IDs, statuses, counts, digests, and admitted report excerpts. Handle server
requests under CAS's existing policy; never grant worker-requested permission
or answer user questions on the user's behalf. If the connection is lost, recover
exact worker and turn state before any retry; do not duplicate assignments.

## Verify the actual prepared context

Before seed creation, identify the source history through the complete analysis
and exact Campaign Brief. After the native fork, verify the source-to-seed edge
and retention of that history, including the preparation turn. Before assigning
each reviewer, verify its seed-to-worker edge and identical retained seed history.
Compare ordered turn/item identities and content, excluding runtime status and
timing fields that change across a fork; metadata-only reads are insufficient.
Use complete pagination when needed. Check the exact brief bytes as well.

A brief hash verifies the brief only. Do not claim to inspect opaque reasoning
internals: native history inheritance preserves them, while readback checks the
observable retained history. Never reconstruct missing analysis from a summary.

The seed receives no assignment or result. Later coordinator findings must not
enter any reviewer's starting history. Preserve the campaign's exact PR epoch,
worker contract, model choice, concurrency, report identities, and admission
rules across either native transport.

If the actual source is inaccessible, a native request fails, provenance is
missing, or preparation is absent from the fork, withhold worker launch and name
that specific failure. An absent wrapper alone is not an `INCOMPLETE` verdict.
