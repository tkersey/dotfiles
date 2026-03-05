# Codex App-Server Control Contract (CLI Notes)

This skill does not assume access to any Codex source repo. Treat your installed `codex` binary as canonical.

`cas` is v2-focused. Deprecated legacy approval requests are intentionally rejected.

## Canonical Schema Source

Generate schemas that exactly match your installed version:

```sh
codex app-server generate-ts --out DIR
codex app-server generate-json-schema --out DIR

# Include experimental methods/fields:
codex app-server generate-ts --experimental --out DIR
codex app-server generate-json-schema --experimental --out DIR
```

## Connection Lifecycle (Required)

Every connection must complete this sequence exactly once:

1. Send `initialize` with `clientInfo` and optional capabilities.
2. Send the `initialized` notification.
3. Only then issue method requests.

If this contract is violated, expect lifecycle errors:

- `"Not initialized"`: request sent before handshake finished.
- `"Already initialized"`: repeated initialize on same connection.

Recommended initialize payload baseline:

- `clientInfo: { name, title, version }`
- `capabilities: { experimentalApi: true }` when you need experimental methods/fields.
- Optional: `capabilities.optOutNotificationMethods` for per-connection suppression.

## Transport and Envelope

- Default transport: stdio JSONL (`--listen stdio://`), one JSON object per line.
- WebSocket transport exists but is experimental/unsupported for production.
- JSON-RPC-like envelopes omit `"jsonrpc":"2.0"`.

Message kinds (shape-based):

- Request: `{ "method": string, "id": string|number, "params"?: any }`
- Response: `{ "id": string|number, "result": any }` or `{ "id": string|number, "error": any }`
- Notification: `{ "method": string, "params"?: any }`

## Backpressure and Retry Policy

When ingress is saturated, app-server may reject requests with:

- JSON-RPC error code `-32001`
- Message: `"Server overloaded; retry later."`

Treat this as retryable, not fatal. Use exponential backoff with jitter. Do not classify `-32001` as protocol drift.

## Experimental API Capability Gate

`capabilities.experimentalApi = true` on `initialize` is required to use experimental methods and fields.

Examples that require opt-in:

- `tool/requestUserInput`
- `thread/backgroundTerminals/clean`
- `thread/realtime/*`
- `item/tool/call` dynamic tool flow

If opt-in is missing, treat failures as capability negotiation errors before debugging payload shapes.

## Core v2 Thread/Turn Flow

1. Open conversation context:

- `thread/start` or `thread/resume` or `thread/fork`

2. Start turn:

- `turn/start` with `threadId` and `input`

3. Optional steer:

- `turn/steer` with `threadId`, required `expectedTurnId`, and additional `input`

4. Stream notifications until `turn/completed`.

5. Optional interruption:

- `turn/interrupt`

The notification stream is authoritative for item lifecycle and tool events.

## Server-Initiated Requests (Must Reply)

Approvals:

- `item/commandExecution/requestApproval`
- `item/fileChange/requestApproval`

Tool requests:

- `item/tool/call`
- `item/tool/requestUserInput` (experimental)

Auth:

- `account/chatgptAuthTokens/refresh`

For command approvals, preserve optional `approvalId` in routing to avoid callback ambiguity.

## requestUserInput Semantics

`item/tool/requestUserInput` responses must use answer-map structure:

- `{ answers: { [questionId]: { answers: string[] } } }`

After responding (or when pending request is cleared by turn lifecycle), server emits:

- `serverRequest/resolved` with `{ threadId, requestId }`

Plan for cleanup-resolution events on turn start/complete/interrupt.

## Notifications (Common)

Frequently observed:

- `thread/started`
- `turn/started`
- `item/started`
- `item/agentMessage/delta`
- `item/completed`
- `turn/completed`

Common depending on features/config:

- `model/rerouted`
- `turn/diff/updated`
- `turn/plan/updated`
- `skills/changed`
- `thread/status/changed`

## Useful Methods (Non-Exhaustive)

- Thread/session: `thread/list`, `thread/read`, `thread/archive`, `thread/unarchive`, `thread/loaded/list`, `thread/rollback`
- Turn control: `turn/start`, `turn/steer`, `turn/interrupt`
- Review: `review/start`
- Utility: `command/exec`
- Discovery: `skills/list`, `app/list`, `model/list`, `collaborationMode/list`
- Experimental: `experimentalFeature/list`, `thread/backgroundTerminals/clean`, `tool/requestUserInput`

## Routing Rule (Avoid Deadlocks)

Inbound messages can interleave while waiting for responses:

- responses (your request IDs)
- notifications
- server-initiated requests requiring replies

Use one read loop that dispatches by envelope kind and correlates by `id`. Add explicit timeouts for forwarded server requests and return structured errors for unsupported methods.

## Debugging Commands

Smoke and stream visibility:

```sh
run_cas_tool smoke-check --cwd /path --json
run_cas_tool request --cwd /path --method thread/list --params-json '{"cursor":null,"limit":5}' --json
codex debug app-server send-message-v2 "run tests and summarize failures"
```

When diagnosing failures, check in order:

1. handshake completed (`initialize` then `initialized`)
2. capability gate for experimental surfaces
3. overload behavior (`-32001`) and retry strategy
4. request/response correlation and timeout handling
