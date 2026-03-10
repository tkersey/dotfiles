---
name: cas
description: Run Zig CAS helpers (`cas`, `cas_smoke_check`, `cas_instance_runner`) for v2 app-server smoke checks, direct thread/turn request execution, and multi-instance fanout when validating method or approval behavior.
---

# cas (Zig App-Server Control)

## Overview

`$cas` is Zig-only in this repo.

Use the native `cas` dispatcher and subcommands:

- `cas smoke_check` for protocol/API smoke checks.
- `cas instance_runner` for method execution across one or many isolated instances.
- `run_cas_tool request` (helper alias) for single-request flows via `instance_runner --instances 1`.

Current `cas smoke_check` verifies the native client can complete the v2 handshake and reach `experimentalFeature/list`, `thread/start`, `thread/resume`, and `turn/steer`.

Node runtime paths (`cas_proxy.mjs`, `cas_client.mjs`, and related wrappers) are removed from this skill and must not be used.

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
    echo "usage: run_cas_tool <smoke-check|smoke_check|instance-runner|instance_runner|request> [args...]" >&2
    return 2
  fi
  shift || true

  local cas_subcommand=""
  local marker=""
  local -a pre_args=()
  case "$subcommand" in
    smoke-check|smoke_check)
      cas_subcommand="smoke_check"
      marker="cas_smoke_check.zig"
      ;;
    instance-runner|instance_runner)
      cas_subcommand="instance_runner"
      marker="cas_instance_runner.zig"
      ;;
    request)
      cas_subcommand="instance_runner"
      marker="cas_instance_runner.zig"
      pre_args=(--instances 1 --sample 1)
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
      cas "$cas_subcommand" "${pre_args[@]}" "$@"
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
      cas "$cas_subcommand" "${pre_args[@]}" "$@"
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

- An "instance" is one `cas_proxy_client`-managed `codex app-server` child process.
- Each instance executes one request path with isolated client metadata and optional state-file isolation.
- "N instances" means N parallel client+app-server pairs in `cas instance_runner`.

## Trigger Cues

- "instances" / "multi-instance" / "parallel sessions"
- app-server method checks (`thread/start`, `thread/resume`, `thread/fork`, `thread/read`, `thread/list`, `thread/archive`, `thread/unarchive`, `thread/rollback`, `turn/start`, `turn/steer`, `turn/interrupt`, `review/start`)
- command/file approval behavior, especially `availableDecisions`
- session mining through direct app-server method execution
- protocol sanity checks before orchestration

## Workflow

1. Validate basic app-server wiring first.
   - `run_cas_tool smoke-check --cwd /path/to/workspace --json`
   - Treat this as a protocol preflight before any fanout run.

2. Enforce handshake assumptions when diagnosing failures.
   - Confirm the session completed `initialize` then `initialized` before method calls.
   - If you see `"Not initialized"` or `"Already initialized"`, treat it as connection-lifecycle error, not a method payload error.

3. Run one direct method request (single-request lane).
   - `run_cas_tool request --cwd /path/to/workspace --method thread/start --params-json '{"cwd":"/path/to/workspace","experimentalRawEvents":false}' --json`

4. Run fanout/multi-instance requests.
   - `run_cas_tool instance-runner --cwd /path/to/workspace --instances 12 --method thread/list --params-json '{"cursor":null,"limit":1}' --json`

5. Apply overload handling on request saturation.
   - If app-server returns JSON-RPC error code `-32001` (`"Server overloaded; retry later."`), retry with exponential backoff and jitter.
   - Do not treat `-32001` as a permanent protocol mismatch.

6. Drive specific thread/turn methods as needed.
   - Start thread:
     - `run_cas_tool request --cwd /path/to/workspace --method thread/start --params-json '{"cwd":"/path/to/workspace","experimentalRawEvents":false}' --json`
   - Start turn:
     - `run_cas_tool request --cwd /path/to/workspace --method turn/start --params-json '{"threadId":"thr_123","input":[{"type":"text","text":"summarize the repo status"}]}' --json`
   - Thread read:
     - `run_cas_tool request --cwd /path/to/workspace --method thread/read --params-json '{"threadId":"thr_123","includeTurns":true}' --json`
   - Resume thread:
     - `run_cas_tool request --cwd /path/to/workspace --method thread/resume --params-json '{"threadId":"thr_123"}' --json`
   - Steer turn:
     - `run_cas_tool request --cwd /path/to/workspace --method turn/steer --params-json '{"threadId":"thr_123","expectedTurnId":"turn_abc","input":[{"type":"text","text":"continue"}]}' --json`
   - Interrupt turn:
     - `run_cas_tool request --cwd /path/to/workspace --method turn/interrupt --params-json '{"threadId":"thr_123","turnId":"turn_abc"}' --json`

7. Use method-specific params for list/mine flows.
   - `thread/list` supports filter params (`cursor`, `limit`, `searchTerm`, `cwd`, etc.) as provided by your app-server version.
   - `turn/steer` requires `expectedTurnId`.

8. Gate experimental methods and payload fields explicitly.
   - Experimental surfaces such as `thread/backgroundTerminals/clean`, `thread/realtime/*`, and `thread/start` dynamic-tool fields require `initialize.params.capabilities.experimentalApi = true`.
   - If omitted, treat failures as capability negotiation errors.

9. Respect native CAS server-request limits.
   - The current Zig client auto-answers `item/commandExecution/requestApproval`, `item/fileChange/requestApproval`, `item/permissions/requestApproval`, `item/tool/requestUserInput`, `mcpServer/elicitation/request`, and `item/tool/call`.
   - Default native behavior is conservative: permissions requests are denied, request-user-input questions use the first option label when present, MCP elicitations are declined, and dynamic tool calls return `success: false` unless you override with explicit CLI flags.

## Approval and Request Semantics

- Exec/file approval decisions are handled by the Zig client (`--exec-approval`, `--file-approval`, `--read-only`).
- Permission approvals can be controlled with `--permissions-approval deny|grant-turn|grant-session`.
- `item/tool/requestUserInput`, `mcpServer/elicitation/request`, and `item/tool/call` can be overridden with `--request-user-input-response-json`, `--elicitation-action` plus `--elicitation-content-json`, and `--dynamic-tool-response-json`.
- For command approvals, CAS resolves decisions against server-provided `availableDecisions` when present.
- Unknown server-request methods are rejected fail-closed in native mode to prevent deadlocks.
- For overload responses (`-32001`), CAS callers should retry with exponential backoff and jitter.

## Scope Boundaries (Zig-Only Cutover)

- This skill no longer exposes a Node JSONL proxy lifecycle.
- Legacy message envelopes (`cas/request`, `cas/respond`, `cas/send`, `cas/state/get`, `cas/stats/get`) are removed from this skill contract.
- Dynamic tool reply loops are supported only through static response payloads passed on the CAS CLI; native CAS is not a full interactive tool-runtime host.

## Canonical Schema Source

Use your installed `codex` binary to generate schemas that match your version:

```sh
codex app-server generate-ts --out DIR
codex app-server generate-json-schema --out DIR

# If you need experimental methods/fields, include:
codex app-server generate-ts --experimental --out DIR
codex app-server generate-json-schema --experimental --out DIR
```

## Local References

Read `references/codex_app_server_contract.md` for API/method notes that inform CAS request usage.

## Resources

- `cas` binary dispatcher:
  - `cas smoke_check`
  - `cas instance_runner`
- `cas_smoke_check` binary: protocol/API smoke validation.
- `cas_instance_runner` binary: single or multi-instance method execution.

Runtime bootstrap policy mirrors `seq`: require installed `cas` Zig binaries, default to `brew install tkersey/tap/cas` on macOS, and fallback to direct Zig install from `skills-zig` on non-macOS.
