---
name: puff
description: Launch and manage Codex Cloud tasks from the CLI, including detached background watchers that track completion. Use when users ask to run coding work in cloud/background agents, queue multiple cloud tasks, poll task status, fetch cloud diffs, apply cloud outputs locally, or pair cloud kickoff with `$cas` orchestration.
---

# Puff

## Overview

Use this skill to launch Codex Cloud tasks without blocking the local CLI session. Use `run_puff_tool` to prefer the Zig CLI with script fallback, submit work, detach status watchers, and retain logs/results for later diff/apply actions.

## Quick Start

```bash
CODEX_SKILLS_HOME="${CODEX_HOME:-$HOME/.codex}"
CLAUDE_SKILLS_HOME="${CLAUDE_HOME:-$HOME/.claude}"
PUFF_SCRIPT="$CODEX_SKILLS_HOME/skills/puff/scripts/puff.sh"
[ -f "$PUFF_SCRIPT" ] || PUFF_SCRIPT="$CLAUDE_SKILLS_HOME/skills/puff/scripts/puff.sh"

run_puff_tool() {
  if command -v puff >/dev/null 2>&1 && puff --help 2>&1 | grep -q "puff.zig"; then
    puff "$@"
    return
  fi
  if [ "$(uname -s)" = "Darwin" ] && command -v brew >/dev/null 2>&1; then
    if ! brew install tkersey/tap/puff; then
      echo "brew install tkersey/tap/puff failed; refusing silent fallback." >&2
      return 1
    fi
    if command -v puff >/dev/null 2>&1 && puff --help 2>&1 | grep -q "puff.zig"; then
      puff "$@"
      return
    fi
    echo "brew install tkersey/tap/puff did not produce a compatible puff binary." >&2
    return 1
  fi
  if [ -f "$PUFF_SCRIPT" ]; then
    "$PUFF_SCRIPT" "$@"
    return
  fi
  echo "puff binary missing and fallback script not found: $PUFF_SCRIPT" >&2
  return 1
}
```

## Workflow

1. Ensure ChatGPT auth is present.
`codex login`
2. Run readiness checks.
`run_puff_tool doctor --env <env-id-or-label>`
Optional: print manual environment-creation instructions.
`run_puff_tool create`
3. Launch cloud work with a detached watcher.
`run_puff_tool launch --env <env-id-or-label> --prompt "Implement X"`
Optional: launch the cloud Join operator prompt (`seq -> join`) for PR patch routing.
`run_puff_tool join-operator --env <env-id-or-label> --repo <owner/repo> --patch-inbox <locator>`
Canary mode (single bounded cycle):
`run_puff_tool join-operator --env <env-id-or-label> --repo <owner/repo> --patch-inbox <locator> --canary`
4. Inspect running and completed watcher jobs.
`run_puff_tool jobs`
5. Tail watcher logs when needed.
`tail -f <watch_log_path>`
6. Inspect or apply result when ready.
`codex cloud diff <task-id>`
`codex cloud apply <task-id>`

## Command Selection

Use `launch` for async/background execution.
`launch` runs `doctor` by default; pass `--skip-doctor` to bypass pre-checks.
Use `create` when you need formatted manual environment-creation instructions only.
Use `submit` when only task id/url is needed (it executes a cloud task).
Use `doctor` for explicit auth/environment readiness checks.
Use `watch` for blocking foreground polling.
Use `jobs` and `stop` to manage detached watchers.
Use `join-operator` to generate and launch the cloud join loop prompt that enforces manifest-first routing and `seq -> join` execution.
Use `join-operator --max-cycles <n>` for bounded runs; `--canary` is shorthand for one cycle.

## Interop With `$cas`

Use `$cas` when orchestration requirements exceed simple cloud task lifecycle control.
Use `$puff` for fast cloud kickoff and lifecycle polling.
Use `$cas` directly for proxy lifecycle management (`start`/`stop`) and app-server thread/turn orchestration, steering, forwarding server requests, or complex multi-thread routing.

## Notes

Pass either environment id or unique environment label to `--env`.
Treat `READY` and `APPLIED` as successful terminal states in watch loops.
Treat `ERROR` as terminal failure and inspect with `codex cloud status <task-id>` and `codex cloud diff <task-id>`.
Runtime bootstrap policy for `puff` mirrors `seq`/`cas`/`lift`: prefer the Zig `puff` binary; on macOS with `brew`, treat `brew install tkersey/tap/puff` failure (or incompatible binary) as a hard error; otherwise fallback to local `puff.sh`.

## Resources

- `scripts/puff.sh`: create/submit/watch/launch/jobs/stop wrapper around `codex cloud`.
- `scripts/puff.sh join-operator`: launch helper for cloud join operator prompts.
- `references/commands.md`: command map including optional `$cas` pairing.
