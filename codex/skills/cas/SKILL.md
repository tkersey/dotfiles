---
name: cas
description: Run a v2-only Node JSONL proxy that spawns `codex app-server` and exposes an automation-friendly stream API. Use when you need to drive the app-server programmatically (automation/orchestration/session mining), have subagents send updates or code patches into live sessions, auto-handle approvals, forward server requests with deterministic timeouts, mine sessions via `thread/*`, steer active turns (`turn/steer`), or run N parallel instances (each instance is one proxy + one app-server child).
---

# cas (App-Server Control)

## Overview

Cas ships a small Node proxy (`scripts/cas_proxy.mjs`) that:

- Spawns `codex app-server`.
- Performs the required handshake (`initialize` -> `initialized`) with `experimentalApi: true` and optional `optOutNotificationMethods`.
- Reads/writes JSONL over stdio.
- Auto-accepts v2 approval requests.
- Forwards v2 server requests to the orchestrator.
- Rejects deprecated legacy approval requests (`execCommandApproval`, `applyPatchApproval`).
- Fails forwarded requests deterministically on timeout (default `30000` ms).
- Emits a lossless, automation-friendly event stream (includes the raw app-server message plus derived routing keys).

This skill assumes `codex` is available on PATH and does not require access to any repo source tree.

## Zig CLI Iteration Repos

When iterating on the Zig-backed `cas` helper CLI path, use these two repos:

- `skills-zig` (`/Users/tk/workspace/tk/skills-zig`): source for the `cas` Zig binaries, build/test wiring, and release tags.
- `homebrew-tap` (`/Users/tk/workspace/tk/homebrew-tap`): Homebrew formula updates/checksum bumps for released `cas` binaries.

## Quick Start

```bash
run_cas_tool() {
  local subcommand="${1:-}"
  if [ -z "$subcommand" ]; then
    echo "usage: run_cas_tool <smoke-check|smoke_check|instance-runner|instance_runner> [args...]" >&2
    return 2
  fi
  shift || true

  local cas_subcommand=""
  local marker=""
  case "$subcommand" in
    smoke-check|smoke_check)
      cas_subcommand="smoke_check"
      marker="cas_smoke_check.zig"
      ;;
    instance-runner|instance_runner)
      cas_subcommand="instance_runner"
      marker="cas_instance_runner.zig"
      ;;
    *)
      echo "unknown cas subcommand: $subcommand" >&2
      return 2
      ;;
  esac

  install_cas_direct() {
    local repo="${SKILLS_ZIG_REPO:-$HOME/workspace/tk/skills-zig}"
    if ! command -v zig >/dev/null 2>&1; then
      echo "zig not found. Install Zig from https://ziglang.org/download/ and retry." >&2
      return 1
    fi
    if [ ! -d "$repo" ]; then
      echo "skills-zig repo not found at $repo." >&2
      echo "clone it with: git clone https://github.com/tkersey/skills-zig \"$repo\"" >&2
      return 1
    fi
    if ! (cd "$repo" && zig build -Doptimize=ReleaseSafe); then
      echo "direct Zig build failed in $repo." >&2
      return 1
    fi
    if [ ! -x "$repo/zig-out/bin/cas" ]; then
      echo "direct Zig build did not produce $repo/zig-out/bin/cas." >&2
      return 1
    fi
    mkdir -p "$HOME/.local/bin"
    install -m 0755 "$repo/zig-out/bin/cas" "$HOME/.local/bin/cas"
  }

  local os="$(uname -s)"
  if command -v cas >/dev/null 2>&1 && cas --help 2>&1 | grep -q "cas.zig"; then
    if cas "$cas_subcommand" --help 2>&1 | grep -q "$marker"; then
      cas "$cas_subcommand" "$@"
      return
    fi
    echo "cas binary found, but marker check failed for subcommand: $cas_subcommand" >&2
    return 1
  fi

  if [ "$os" = "Darwin" ]; then
    if ! command -v brew >/dev/null 2>&1; then
      echo "homebrew is required on macOS: https://brew.sh/" >&2
      return 1
    fi
    if ! brew install tkersey/tap/cas; then
      echo "brew install tkersey/tap/cas failed." >&2
      return 1
    fi
  elif ! (command -v cas >/dev/null 2>&1 && cas --help 2>&1 | grep -q "cas.zig"); then
    if ! install_cas_direct; then
      return 1
    fi
  fi

  if command -v cas >/dev/null 2>&1 && cas --help 2>&1 | grep -q "cas.zig"; then
    if cas "$cas_subcommand" --help 2>&1 | grep -q "$marker"; then
      cas "$cas_subcommand" "$@"
      return
    fi
    echo "cas binary found, but marker check failed for subcommand: $cas_subcommand" >&2
    return 1
  fi
  echo "cas binary missing or incompatible after install attempt." >&2
  if [ "$os" = "Darwin" ]; then
    echo "expected install path: brew install tkersey/tap/cas" >&2
  else
    echo "expected direct path: SKILLS_ZIG_REPO=<skills-zig-path> zig build -Doptimize=ReleaseSafe" >&2
  fi
  return 1
}

run_cas_tool smoke-check --cwd /path/to/workspace --json
```

## Terminology (Instances)

- An "instance" is one `cas_proxy` process plus its spawned app-server child process.
- Each instance has its own JSONL stream and its own `sessionId`.
- "N instances" means N parallel proxy+app-server pairs; it is not N threads/turns inside one instance.
- Isolation tip: for multi-instance runs, prefer per-instance `--state-file` (or the runner's `--state-file-dir`) if you don't want instances to share state.

## Trigger cues

- "instances" / "multi-instance" / "parallel sessions"
- app-server control (JSONL proxy, JSON-RPC methods)
- session mining (thread/turn inventory, export/index)
- steering/resume (`turn/steer`, `thread/resume`)

## Workflow

1. Start the proxy.
   - Run `node scripts/cas_proxy.mjs` from the cas skill directory (or resolve by script path: `CODEX_SKILLS_HOME="${CODEX_HOME:-$HOME/.codex}"; CLAUDE_SKILLS_HOME="${CLAUDE_HOME:-$HOME/.claude}"; CAS_PROXY="$CODEX_SKILLS_HOME/skills/cas/scripts/cas_proxy.mjs"; [ -f "$CAS_PROXY" ] || CAS_PROXY="$CLAUDE_SKILLS_HOME/skills/cas/scripts/cas_proxy.mjs"; node "$CAS_PROXY"`).
   - Optional: pass `--cwd /path/to/workspace` to control where the app-server runs. By default, state is written under `~/.codex/cas/state/<workspace-hash>.json`.
   - Optional: pass `--state-file PATH` to override the default state location.
   - Optional: tune forwarded request fail-fast behavior with `--server-request-timeout-ms <N>` (0 disables timeout).
   - Optional: control v2 approval auto-responses (useful for safe multi-instance workers):
     - `--exec-approval auto|accept|acceptForSession|decline|cancel`
     - `--file-approval auto|accept|acceptForSession|decline|cancel`
     - `--read-only` (shorthand for declining exec + file approvals)
   - Optional: pass one or more `--opt-out-notification-method METHOD` flags to suppress known noisy notifications for the connection.
   - Wait for a `cas/ready` event.

   For N instances in parallel, prefer the instance runner:
   - `run_cas_tool instance-runner --cwd /path/to/workspace --instances N`

2. Drive the app-server by sending requests to the proxy.
   - Send `cas/request` messages (method + params) to proxy stdin.
   - Proxy assigns request ids (unless you supply one), forwards to app-server, and emits `cas/fromServer` responses.
   - Optional smoke check: run `run_cas_tool smoke-check --cwd /path/to/workspace`.

3. Stream and route notifications.
   - Consume `cas/fromServer` events and route by `threadId` / `turnId` / `itemId`.
   - Treat the proxy stream as the source of truth; the raw wire message is always included under `msg`.

4. Handle forwarded server requests.
   - Only reply when cas emits `cas/serverRequest` (these are the server requests cas did not auto-handle).
   - Respond with `cas/respond` using the same `id`.
   - If your response is malformed for a typed v2 request, cas sends a deterministic JSON-RPC error upstream instead of hanging.
   - If you do not reply in time, cas emits `cas/serverRequestTimeout` and fails that request upstream.
   - Approvals are auto-accepted by default (including best-effort execpolicy amendments) and will not block you unless you override approval policy flags.

5. Mine sessions (optional).
   - Use `thread/list` (cursor pagination + optional `modelProviders`/`sourceKinds`/`archived`/`cwd`/`searchTerm` filters), `thread/read` (optionally `includeTurns:true`), and `thread/unsubscribe` to build/maintain your own index and loaded-thread lifecycle.
   - The server is not a search engine; extract data and index externally.

## Dedicated API Helpers

Use `scripts/cas_client.mjs` convenience wrappers when you want typed intent rather than raw method strings:

- `resumeThread(params)` -> `thread/resume`
- `steerTurn(params)` -> `turn/steer`
- `listExperimentalFeatures(params)` -> `experimentalFeature/list`

## Dynamic Tools (Optional)

If you opt into dynamic tools, register them on `thread/start` via `dynamicTools` (experimental API surface).
When the server emits `cas/serverRequest`:
- For `method: "item/tool/call"`, run the tool in your orchestrator and reply with `cas/respond`.
- For `method: "item/tool/requestUserInput"` (experimental), collect answers and return `{ answers: ... }`.
- For `method: "account/chatgptAuthTokens/refresh"`, return refreshed tokens or a deterministic error.

## Proxy I/O Contract (stdin/stdout)

The proxy itself speaks JSONL over stdio.

### stdin -> cas

- `cas/request` sends a JSON-RPC request to `codex app-server`:

```json
{
  "type": "cas/request",
  "clientRequestId": "any-string",
  "method": "thread/start",
  "params": { "cwd": "/path", "experimentalRawEvents": false }
}
```

- `cas/respond` answers a server-initiated request forwarded by cas:

```json
{
  "type": "cas/respond",
  "id": 123,
  "result": {
    "contentItems": [{ "type": "inputText", "text": "..." }],
    "success": true
  }
}
```

- `cas/send` forwards a raw JSON-RPC message to `codex app-server` (advanced escape hatch):

```json
{
  "type": "cas/send",
  "msg": { "method": "thread/list", "id": "raw-1", "params": { "cursor": null } }
}
```

- `cas/state/get` emits the current proxy state.
- `cas/stats/get` emits a stats snapshot (uptime, queue depth, counts).
- `cas/exit` shuts down the proxy.

### stdout <- cas

- `cas/ready` indicates the proxy finished handshake.
- `cas/fromServer` is emitted for every JSON message from `codex app-server`.
- `cas/toServer` is emitted for every JSON message sent to `codex app-server` (includes auto-approvals and handshake).
- `cas/serverRequest` is emitted for server-initiated requests that require an orchestrator response (tool calls, auth refresh, etc.).
- `cas/serverRequestTimeout` is emitted when a forwarded server request is failed due to timeout.
- `cas/stats` and `cas/ioPaused`/`cas/ioResumed` help you monitor backpressure.

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

Read `references/codex_app_server_contract.md` for a control map and the recommended routing/response strategy.

## Resources

### references/

Control notes for fast lookup during implementation.

### scripts/

Runnable Node proxy for orchestration.

Included:
- `scripts/cas_proxy.mjs` (the proxy)
- `scripts/cas_client.mjs` (JS wrapper: spawn proxy + request() + event stream)
- `scripts/budget_governor.mjs` (helpers: rateLimits -> per-window pacing + stricter-tier clamp)
- `scripts/cas_rate_limits.mjs` (CLI: prints normalized `account/rateLimits/read` snapshot)
- `scripts/cas_example_orchestrator.mjs` (example orchestration script)

Runtime bootstrap policy for Zig CLIs mirrors `seq`: require the installed `cas` dispatcher binary (`cas smoke_check` / `cas instance_runner`). On macOS, default to `brew install tkersey/tap/cas`; on other OSes, fallback to direct Zig install from `skills-zig`.
