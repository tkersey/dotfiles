---
name: casp
description: Run a v2-only Node JSONL proxy that spawns `codex app-server` and exposes an orchestration-friendly stream API. Use when you need to control Codex programmatically across many threads/turns, have subagents send updates or code patches into live sessions, auto-handle approvals, forward server requests with deterministic timeouts, mine sessions via `thread/*`, steer active turns (`turn/steer`), list experimental features (`experimentalFeature/list`), resume threads (`thread/resume`), or suppress specific notifications via initialize capabilities.
---

# casp (Codex App-Server Protocol)

## Overview

Casp ships a small Node proxy (`scripts/casp_proxy.mjs`) that:

- Spawns `codex app-server`.
- Performs the required handshake (`initialize` -> `initialized`) with `experimentalApi: true` and optional `optOutNotificationMethods`.
- Reads/writes JSONL over stdio.
- Auto-accepts v2 approval requests.
- Forwards v2 server requests to the orchestrator.
- Rejects deprecated legacy approval requests (`execCommandApproval`, `applyPatchApproval`).
- Fails forwarded requests deterministically on timeout (default `30000` ms).
- Emits a lossless, orchestration-friendly event stream (includes the raw app-server message plus derived routing keys).

This skill assumes `codex` is available on PATH and does not require access to any repo source tree.

## Workflow

1. Start the proxy.
   - Run `node scripts/casp_proxy.mjs` from the casp skill directory (example: `node ~/.dotfiles/codex/skills/casp/scripts/casp_proxy.mjs`).
   - Optional: pass `--cwd /path/to/workspace` to control where `codex app-server` runs. By default, state is written under `~/.codex/casp/state/<workspace-hash>.json`.
   - Optional: pass `--state-file PATH` to override the default state location.
   - Optional: tune forwarded request fail-fast behavior with `--server-request-timeout-ms <N>` (0 disables timeout).
   - Optional: pass one or more `--opt-out-notification-method METHOD` flags to suppress known noisy notifications for the connection.
   - Wait for a `casp/ready` event.

2. Drive Codex by sending requests to the proxy.
   - Send `casp/request` messages (method + params) to proxy stdin.
   - Proxy assigns request ids (unless you supply one), forwards to app-server, and emits `casp/fromServer` responses.
   - Optional smoke check: run `node scripts/casp_smoke_check.mjs --cwd /path/to/workspace`.

3. Stream and route notifications.
   - Consume `casp/fromServer` events and route by `threadId` / `turnId` / `itemId`.
   - Treat the proxy stream as the source of truth; the raw wire message is always included under `msg`.

4. Handle forwarded server requests.
   - Only reply when casp emits `casp/serverRequest` (these are the server requests casp did not auto-handle).
   - Respond with `casp/respond` using the same `id`.
   - If your response is malformed for a typed v2 request, casp sends a deterministic JSON-RPC error upstream instead of hanging.
   - If you do not reply in time, casp emits `casp/serverRequestTimeout` and fails that request upstream.
   - Approvals are auto-accepted (including best-effort execpolicy amendments) and will not block you.

5. Mine sessions (optional).
   - Use `thread/list` and `thread/read` (optionally `includeTurns:true`) to build your own index.
   - The server is not a search engine; extract data and index externally.

## Dedicated API Helpers

Use `scripts/casp_client.mjs` convenience wrappers when you want typed intent rather than raw method strings:

- `resumeThread(params)` -> `thread/resume`
- `steerTurn(params)` -> `turn/steer`
- `listExperimentalFeatures(params)` -> `experimentalFeature/list`

## Dynamic Tools (Optional)

If you opt into dynamic tools, register them on `thread/start` via `dynamicTools` (experimental API surface).
When the server emits `casp/serverRequest`:
- For `method: "item/tool/call"`, run the tool in your orchestrator and reply with `casp/respond`.
- For `method: "item/tool/requestUserInput"` (experimental), collect answers and return `{ answers: ... }`.
- For `method: "account/chatgptAuthTokens/refresh"`, return refreshed tokens or a deterministic error.

## Proxy Protocol (stdin/stdout)

The proxy itself speaks JSONL over stdio.

### stdin -> casp

- `casp/request` sends a JSON-RPC request to `codex app-server`:

```json
{
  "type": "casp/request",
  "clientRequestId": "any-string",
  "method": "thread/start",
  "params": { "cwd": "/path", "experimentalRawEvents": false }
}
```

- `casp/respond` answers a server-initiated request forwarded by casp:

```json
{
  "type": "casp/respond",
  "id": 123,
  "result": {
    "contentItems": [{ "type": "inputText", "text": "..." }],
    "success": true
  }
}
```

- `casp/send` forwards a raw JSON-RPC message to `codex app-server` (advanced escape hatch):

```json
{
  "type": "casp/send",
  "msg": { "method": "thread/list", "id": "raw-1", "params": { "cursor": null } }
}
```

- `casp/state/get` emits the current proxy state.
- `casp/stats/get` emits a stats snapshot (uptime, queue depth, counts).
- `casp/exit` shuts down the proxy.

### stdout <- casp

- `casp/ready` indicates the proxy finished handshake.
- `casp/fromServer` is emitted for every JSON message from `codex app-server`.
- `casp/toServer` is emitted for every JSON message sent to `codex app-server` (includes auto-approvals and handshake).
- `casp/serverRequest` is emitted for server-initiated requests that require an orchestrator response (tool calls, auth refresh, etc.).
- `casp/serverRequestTimeout` is emitted when a forwarded server request is failed due to timeout.
- `casp/stats` and `casp/ioPaused`/`casp/ioResumed` help you monitor backpressure.

All events include:

- `seq` (monotonic)
- `ts` (ms since epoch)
- `sessionId` (unique per proxy instance)
- derived keys `threadId` / `turnId` / `itemId` when present
- `msg` (the raw app-server message; lossless)

## Canonical Schema Source

Use your installed `codex` binary to generate schemas that match your version:

```sh
codex app-server generate-ts --out DIR
codex app-server generate-json-schema --out DIR

# If you need experimental methods/fields (e.g. dynamic tools), include:
codex app-server generate-ts --experimental --out DIR
codex app-server generate-json-schema --experimental --out DIR
```

## Local References

Read `references/codex_app_server_protocol.md` for a protocol map and the recommended routing/response strategy.

## Resources

### references/

Protocol notes for fast lookup during implementation.

### scripts/

Runnable Node proxy for orchestration.

Included:
- `scripts/casp_proxy.mjs` (the proxy)
- `scripts/casp_client.mjs` (JS wrapper: spawn proxy + request() + event stream)
- `scripts/casp_example_orchestrator.mjs` (example orchestration script)
- `scripts/casp_instance_runner.mjs` (run one method across many parallel casp sessions/instances)
- `scripts/casp_smoke_check.mjs` (smoke-checks `experimentalFeature/list`, `thread/resume`, `turn/steer`)
