# Codex App-Server Control Contract (CLI Notes)

This skill does not assume access to any Codex source repo. Treat your installed `codex` binary as canonical.

`cas` is v2-focused. Deprecated legacy approval requests are intentionally rejected.

## Canonical Schema Source

Generate schemas that exactly match your installed version:

```sh
codex app-server generate-ts --out DIR
codex app-server generate-json-schema --out DIR

# Include experimental methods/fields (e.g. dynamic tools):
codex app-server generate-ts --experimental --out DIR
codex app-server generate-json-schema --experimental --out DIR
```

## Transport and Envelope

- JSONL over stdio: one JSON object per line in both directions.
- JSON-RPC-like envelopes, but omit `"jsonrpc":"2.0"`.

Message kinds (shape-based):

- Request: `{ "method": string, "id": string|number, "params"?: any }`
- Response: `{ "id": string|number, "result": any }` or `{ "id": string|number, "error": any }`
- Notification: `{ "method": string, "params"?: any }`

## Required Handshake

1. Send `initialize` with:

- `clientInfo`: `{ name, title, version }`
- `capabilities`: `{ experimentalApi: true }` (recommended)
- Optional: `capabilities.optOutNotificationMethods: string[]` to suppress specific notification methods for this connection.

2. Send the `initialized` notification (no params) before any other request.

## Core v2 Flow (Thread/Turn)

- Start or resume a thread:
  - `thread/start`
  - `thread/resume`
  - `thread/fork`
- Start a turn:
  - `turn/start` with `threadId` and `input`.
- Steer an in-flight turn:
  - `turn/steer` with `threadId`, `expectedTurnId`, and additional `input`.
- Stream notifications until `turn/completed`.
- Interrupt an in-flight turn:
  - `turn/interrupt`.

Important: the authoritative streaming payload is the notification stream.
Do not rely on `turn.items` being fully populated on `turn/started` / `turn/completed`.

## Notifications (Common)

- `thread/started`
- `thread/archived`
- `thread/unarchived`
- `turn/started`
- `item/started`
- `item/agentMessage/delta`
- `item/commandExecution/outputDelta`
- `item/fileChange/outputDelta`
- `item/completed`
- `turn/completed`

Often present depending on features/config:

- `model/rerouted`
- `fuzzyFileSearch/sessionCompleted`
- `turn/diff/updated`
- `turn/plan/updated`
- `item/plan/delta` (experimental)
- `item/reasoning/*` (experimental)

## Server-Initiated Requests (Must Reply)

Approvals (v2):

- `item/commandExecution/requestApproval`
- `item/fileChange/requestApproval`

Note: `item/commandExecution/requestApproval` may include optional `approvalId`; preserve it in your approval routing so subcommand callbacks remain disambiguated.

Tools:

- `item/tool/call`
- `item/tool/requestUserInput` (experimental)

Auth:

- `account/chatgptAuthTokens/refresh`

Response payloads (see your generated schema for the exact shape):

- `item/tool/call` -> `{ contentItems: [{ type: "inputText", text: "..." }], success: boolean }`
- `item/tool/requestUserInput` -> `{ answers: { [questionId]: { answers: string[] } } }`

Legacy (may appear in older flows; cas rejects these in v2-only mode):

- `execCommandApproval`
- `applyPatchApproval`

## Useful Methods (Non-Exhaustive)

- Thread lifecycle: `thread/start`, `thread/resume`, `thread/fork`
- Session mining: `thread/list`, `thread/read` (`includeTurns:true`)
- Maintenance: `thread/archive`, `thread/unarchive`, `thread/loaded/list`
- Manual compaction: `thread/compact/start` (progress streams as normal `turn/*` + `item/*`)
- Turns: `turn/start`, `turn/steer`, `turn/interrupt`
- Experimental feature discovery: `experimentalFeature/list`
- Review: `review/start`
- One-off exec: `command/exec`
- Skills/apps discovery: `skills/list`, `app/list`
- Auth/account: `account/*`, `mcpServer/oauth/*` (see schema)

Skill/app invocation pattern (v2 input items):

- Include `$skill-name` in a `text` input and add a `skill` input item with `{ name, path }`.
- Include `$app-slug` in a `text` input and add a `mention` input item with `{ name, path: "app://<connector-id>" }`.

## Mining Sessions (Threads)

- Use `thread/list` (cursor pagination) to enumerate stored sessions.
- Use `thread/read` to fetch a thread; pass `includeTurns:true` when you want rollout history.
- Build your own index/search store; the app-server is not a query engine.

## Routing Rule (Avoid Deadlocks)

Inbound messages interleave while you are waiting for any response:

- responses (to your requests)
- notifications
- server-initiated requests (must be answered)

Use one read loop that dispatches by kind and correlates by `id`.

For deterministic behavior, enforce a timeout on forwarded server requests and respond with explicit JSON-RPC errors for unimplemented methods.

## Debugging Tip

To see a full, real JSONL turn stream (without writing a client), use the built-in debug helper:

```sh
codex debug app-server send-message-v2 "run tests and summarize failures"
```
