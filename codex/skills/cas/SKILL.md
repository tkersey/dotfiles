---
name: cas
description: Run Zig CAS helpers (`cas`, `cas_smoke_check`, `cas_instance_runner`, `cas_review_session`, `cas_conformance_suite`) for v2 app-server smoke checks, direct thread/turn request execution, detached review-session control, multi-instance fanout, and swarm conformance checks around `$st` claim sets and `$mesh` reconciliation.
---

# cas (Zig App-Server Control)

## Overview

`$cas` is Zig-only in this repo.

Use the native `cas` dispatcher and subcommands:

- `cas conformance` for swarm conformance checks around `$st` claims, `$mesh` reconciliation, and retry policy.
- `cas smoke_check` for protocol/API smoke checks.
- `cas instance_runner` for method execution across one or many isolated instances.
- `cas review_session` for detached `review/start` lifecycle control with persisted `reviewThreadId` handles.
- `run_cas_tool request` (helper alias) for single-request flows via `instance_runner --instances 1`.

Current `cas smoke_check` verifies the native client can complete the v2 handshake and reach `experimentalFeature/list`, `thread/start`, `thread/resume`, and `turn/steer`.

Current `cas conformance` covers these swarm-hardening scenarios:

- `claim_safe_wave`: verify two disjoint `$st` claims can run in parallel without overlapping lock roots
- `stale_claim_reclaim`: verify expired held claims become stale and return to pending
- `mesh_row_accountability`: verify imported mesh output completes only reported rows and leaves missing rows outstanding
- `overload_backoff`: verify the bounded retry/backoff policy with a deterministic synthetic overload script

`cas conformance` is the harness; it is not the owner of durable claims or mesh state. `$st` remains the source of truth for claims/runtime/proof metadata.

Current `cas review_session` is the review-control lane:

- `start` launches detached `review/start` on a supplied or freshly created parent thread
- `wait` is the primary completion path: poll the detached review thread until terminal state and consume the normalized `reviewResult` payload when available
- `start --wait` is a convenience wrapper over the same `start` then `wait` lifecycle; it is not a separate stronger contract
- `status` reads the detached review thread from a fresh CAS process
- `interrupt` sends `turn/interrupt` for the persisted detached review turn

`reviewThreadId` is the recoverable handle. Session records live under `~/.codex/cas/review_sessions/`, and CAS appends raw request/response artifacts to a per-review NDJSON log beside that record.

When `start`, `start --wait`, `status`, or `wait` emit JSON, the output includes the detached review handle/result fields plus launch compatibility metadata:

- `resolvedCodexPath`
- `resolvedCodexVersion`
- `compatibilityVerdict`
- `failureCode`
- `failureHint`
- `reviewResultAvailable`
- `reviewResultSource`
- `reviewResult`
  - `findings`
  - `overallCorrectness`
  - `overallExplanation`
  - `overallConfidenceScore`

Use the fields this way:

- `compatibilityVerdict="compatible"` means the detached review launch path succeeded under the resolved `codex` binary
- `compatibilityVerdict="incompatible"` means CAS identified a detached-review runtime mismatch and failed closed
- `compatibilityVerdict="not_checked"` means no compatibility verdict was persisted for that record yet (older session record or pre-launch failure)
- `failureCode="wait_timed_out"` means retry `cas review_session wait` on the same `reviewThreadId` or increase `--timeout-ms`; it is not a successful review
- `failureCode="review_result_unavailable"` means the review turn reached terminal state without a materialized `reviewResult`; callers may choose a documented fallback, but CAS itself stays strict

Compatibility note: if detached review on a freshly created parent thread still fails with `no rollout found`, the installed `codex` binary is older than the parent-rollout fix. In that case, upgrade `codex` or pass `--parent-thread-id` for an already materialized parent thread.

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
    echo "usage: run_cas_tool <conformance|conformance-suite|smoke-check|smoke_check|instance-runner|instance_runner|review-session|review_session|request> [args...]" >&2
    return 2
  fi
  shift || true

  local cas_subcommand=""
  local marker=""
  local -a pre_args=()
  case "$subcommand" in
    conformance|conformance-suite|conformance_suite)
      cas_subcommand="conformance"
      marker="cas_conformance_suite.zig"
      ;;
    smoke-check|smoke_check)
      cas_subcommand="smoke_check"
      marker="cas_smoke_check.zig"
      ;;
    instance-runner|instance_runner)
      cas_subcommand="instance_runner"
      marker="cas_instance_runner.zig"
      ;;
    review-session|review_session)
      cas_subcommand="review_session"
      marker="cas_review_session.zig"
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
    if [ ! -x "$repo/zig-out/bin/cas" ] || [ ! -x "$repo/zig-out/bin/cas_review_session" ] || [ ! -x "$repo/zig-out/bin/cas_smoke_check" ] || [ ! -x "$repo/zig-out/bin/cas_instance_runner" ] || [ ! -x "$repo/zig-out/bin/cas_conformance_suite" ]; then
      echo "direct Zig build did not produce the full CAS binary set in $repo/zig-out/bin." >&2
      return 1
    fi
    mkdir -p "$HOME/.local/bin"
    install -m 0755 "$repo/zig-out/bin/cas" "$HOME/.local/bin/cas"
    install -m 0755 "$repo/zig-out/bin/cas_review_session" "$HOME/.local/bin/cas_review_session"
    install -m 0755 "$repo/zig-out/bin/cas_smoke_check" "$HOME/.local/bin/cas_smoke_check"
    install -m 0755 "$repo/zig-out/bin/cas_instance_runner" "$HOME/.local/bin/cas_instance_runner"
    install -m 0755 "$repo/zig-out/bin/cas_conformance_suite" "$HOME/.local/bin/cas_conformance_suite"
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
run_cas_tool review-session start --cwd /path/to/workspace --uncommitted --json
```

## Terminology (Instances)

- An "instance" is one `cas_proxy_client`-managed `codex app-server` child process.
- Each instance executes one request path with isolated client metadata and optional state-file isolation.
- "N instances" means N parallel client+app-server pairs in `cas instance_runner`.

## Trigger Cues

- "instances" / "multi-instance" / "parallel sessions"
- "review session" / "detached review" / "reviewThreadId" / "interrupt review"
- "swarm conformance" / "claim-safe wave" / "stale-claim reclaim" / "mesh row accountability"
- app-server method checks (`thread/start`, `thread/resume`, `thread/fork`, `thread/read`, `thread/list`, `thread/archive`, `thread/unarchive`, `thread/rollback`, `turn/start`, `turn/steer`, `turn/interrupt`, `review/start`)
- command/file approval behavior, especially `availableDecisions`
- session mining through direct app-server method execution
- protocol sanity checks before orchestration

## Workflow

1. Validate basic app-server wiring first.
   - `run_cas_tool smoke-check --cwd /path/to/workspace --json`
   - Treat this as a protocol preflight before any fanout run.

2. Use `review_session` when the real job is detached review lifecycle control rather than one-shot probing.
   - Start detached review:
     - `cas review_session start --cwd /path/to/workspace --uncommitted --json`
     - `cas review_session start --cwd /path/to/workspace --base main --json`
     - `cas review_session start --cwd /path/to/workspace --commit <sha> --title "<subject>" --json`
     - `cas review_session start --cwd /path/to/workspace --custom-instructions @review.txt --json`
   - Read current status from a fresh process:
     - `cas review_session status --review-thread-id <reviewThreadId> --json`
   - Wait for the detached review turn to settle:
     - `cas review_session wait --review-thread-id <reviewThreadId> --timeout-ms 300000 --json`
   - Convenience wrapper when you truly want one process:
     - `cas review_session start --wait --cwd /path/to/workspace --base main --json`
   - Interrupt the detached review turn:
     - `cas review_session interrupt --review-thread-id <reviewThreadId> --json`
   - `reviewThreadId` is the handle; do not invent a second review session id.

3. Detached review is the public review-control path; do not route review-session control through `instance_runner`.
   - `instance_runner` remains a method probe lane and is still useful for schema sanity checks.
   - `review_session` owns persisted review handles, fresh-process status polling, wait loops, and interruption.
   - For workflows that need the actual review verdict, prefer `start ... --json`, keep the returned `reviewThreadId`, then call `wait ... --json`; reserve `start --wait` as a convenience wrapper over that same path.
   - Treat `failureCode` as authoritative. CAS never silently falls back to native `codex review`; callers that want a temporary fallback must do it explicitly at their own layer.

4. For swarm-hardening runs, treat `$st` as the durable source of truth before any worker starts.
   - `st import-orchplan --file .step/st-plan.jsonl --input .step/orchplan.yaml`
   - `st claim --file .step/st-plan.jsonl --wave w1 --executor teams`
   - CAS probes the wave; it does not replace the durable claim ledger.

5. Enforce handshake assumptions when diagnosing failures.
   - Confirm the session completed `initialize` then `initialized` before method calls.
   - If you see `"Not initialized"` or `"Already initialized"`, treat it as connection-lifecycle error, not a method payload error.

6. Run one direct method request (single-request lane).
   - `run_cas_tool request --cwd /path/to/workspace --method thread/start --params-json '{"cwd":"/path/to/workspace","experimentalRawEvents":false}' --json`

7. Run fanout/multi-instance requests.
   - `run_cas_tool instance-runner --cwd /path/to/workspace --instances 12 --method thread/list --params-json '{"cursor":null,"limit":1}' --json`

8. Run the conformance suite when you need repeatable swarm checks around claims, mesh closeout, or retry policy.
   - `cas conformance --cwd /path/to/workspace --json`
   - Narrow to one scenario when debugging: `cas conformance --cwd /path/to/workspace --scenario mesh_row_accountability --json`
   - Use `--skip-smoke-check` only when you intentionally want the local `$st`/mesh scenarios without the live CAS preflight.

9. Apply overload handling on request saturation.
   - If app-server returns JSON-RPC error code `-32001` (`"Server overloaded; retry later."`), retry with exponential backoff and jitter.
   - Do not treat `-32001` as a permanent protocol mismatch.
   - In `cas conformance`, the retry policy scenario is currently synthetic and should be treated as retry-policy proof, not live saturation proof.

10. Drive specific thread/turn methods as needed.
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

11. Use method-specific params for list/mine flows.
   - `thread/list` supports filter params (`cursor`, `limit`, `searchTerm`, `cwd`, etc.) as provided by your app-server version.
   - `turn/steer` requires `expectedTurnId`.

12. After a mesh batch, reconcile the exported CSV back into `$st`.
    - `st import-mesh-results --file .step/st-plan.jsonl --input .step/mesh-output.csv`
    - CAS may validate the wave around that closeout, but it does not own the CSV reconciliation.

13. Gate experimental methods and payload fields explicitly.
   - Experimental surfaces such as `thread/backgroundTerminals/clean`, `thread/realtime/*`, and `thread/start` dynamic-tool fields require `initialize.params.capabilities.experimentalApi = true`.
   - If omitted, treat failures as capability negotiation errors.

14. Respect native CAS server-request limits.
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
- `cas review_session` persists raw request/response artifacts and detached review handles; it is not a generalized streaming event mirror for all app-server notifications.

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
  - `cas conformance`
  - `cas review_session`
  - `cas smoke_check`
  - `cas instance_runner`
- `cas_conformance_suite` binary: swarm conformance around `$st` claims, `$mesh` closeout, and retry policy.
- `cas_review_session` binary: detached review start/status/wait/interrupt with persisted `reviewThreadId` handles.
- `cas_smoke_check` binary: protocol/API smoke validation.
- `cas_instance_runner` binary: single or multi-instance method execution.

Runtime bootstrap policy mirrors `seq`: require installed `cas` Zig binaries, default to `brew install tkersey/tap/cas` on macOS, and fallback to direct Zig install from `skills-zig` on non-macOS.
