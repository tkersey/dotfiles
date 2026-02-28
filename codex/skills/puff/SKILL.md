---
name: puff
description: Launch and manage Codex Cloud tasks from the CLI, including detached background watchers that track completion. Use when users ask to run coding work in cloud/background agents, queue multiple cloud tasks, poll task status, fetch cloud diffs, apply cloud outputs locally, or pair cloud kickoff with `$cas` orchestration.
---

# Puff

## Overview

Use this skill to launch Codex Cloud tasks without blocking the local CLI session. Use `run_puff_tool` to run the Zig `puff` CLI, submit work, detach status watchers, and retain logs/results for later diff/apply actions.

## Zig CLI Iteration Repos

When iterating on the Zig-backed `puff` helper CLI path, use these two repos:

- `skills-zig` (`/Users/tk/workspace/tk/skills-zig`): source for the `puff` Zig binary, build/test wiring, and release tags.
- `homebrew-tap` (`/Users/tk/workspace/tk/homebrew-tap`): Homebrew formula updates/checksum bumps for released `puff` binaries.

## Quick Start

```bash
run_puff_tool() {
  install_puff_direct() {
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
    if [ ! -x "$repo/zig-out/bin/puff" ]; then
      echo "direct Zig build did not produce $repo/zig-out/bin/puff." >&2
      return 1
    fi
    mkdir -p "$HOME/.local/bin"
    install -m 0755 "$repo/zig-out/bin/puff" "$HOME/.local/bin/puff"
  }

  local os="$(uname -s)"
  if command -v puff >/dev/null 2>&1 && puff --help 2>&1 | grep -q "puff.zig"; then
    puff "$@"
    return
  fi

  if [ "$os" = "Darwin" ]; then
    if ! command -v brew >/dev/null 2>&1; then
      echo "homebrew is required on macOS: https://brew.sh/" >&2
      return 1
    fi
    if ! brew install tkersey/tap/puff; then
      echo "brew install tkersey/tap/puff failed." >&2
      return 1
    fi
  elif ! (command -v puff >/dev/null 2>&1 && puff --help 2>&1 | grep -q "puff.zig"); then
    if ! install_puff_direct; then
      return 1
    fi
  fi

  if command -v puff >/dev/null 2>&1 && puff --help 2>&1 | grep -q "puff.zig"; then
    puff "$@"
    return
  fi
  echo "puff binary missing or incompatible after install attempt." >&2
  if [ "$os" = "Darwin" ]; then
    echo "expected install path: brew install tkersey/tap/puff" >&2
  else
    echo "expected direct path: SKILLS_ZIG_REPO=<skills-zig-path> zig build -Doptimize=ReleaseSafe" >&2
  fi
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
Runtime bootstrap policy for `puff` mirrors `seq`/`cas`/`lift`: use the Zig `puff` binary only, default to Homebrew install on macOS, and fallback to direct Zig install from `skills-zig` on non-macOS.

## Resources

- `puff` binary: create/submit/watch/launch/jobs/stop wrapper around `codex cloud`.
- `references/commands.md`: command map including optional `$cas` pairing.
