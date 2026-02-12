---
name: puff
description: Launch and manage Codex Cloud tasks from the CLI, including detached background watchers that track completion. Use when users ask to run coding work in cloud/background agents, queue multiple cloud tasks, poll task status, fetch cloud diffs, apply cloud outputs locally, or pair cloud kickoff with `$casp` orchestration.
---

# Puff

## Overview

Use this skill to launch Codex Cloud tasks without blocking the local CLI session. Use the bundled wrapper to submit work, detach status watchers, and retain logs/results for later diff/apply actions.

## Workflow

1. Ensure ChatGPT auth is present.
`codex login`
2. Run readiness checks.
`~/.dotfiles/codex/skills/puff/scripts/puff.sh doctor --env <env-id-or-label>`
3. Launch cloud work with a detached watcher.
`~/.dotfiles/codex/skills/puff/scripts/puff.sh launch --env <env-id-or-label> --prompt "Implement X"`
4. Inspect running and completed watcher jobs.
`~/.dotfiles/codex/skills/puff/scripts/puff.sh jobs`
5. Tail watcher logs when needed.
`tail -f <watch_log_path>`
6. Inspect or apply result when ready.
`codex cloud diff <task-id>`
`codex cloud apply <task-id>`

## Command Selection

Use `launch` for async/background execution.
`launch` runs `doctor` by default; pass `--skip-doctor` to bypass pre-checks.
Use `submit` when only task id/url is needed.
Use `doctor` for explicit auth/environment readiness checks.
Use `watch` for blocking foreground polling.
Use `jobs` and `stop` to manage detached watchers.

## Interop With `$casp`

Use `$casp` when orchestration requirements exceed simple cloud task lifecycle control.
Use `$puff` for fast cloud kickoff and lifecycle polling.
Use `$puff` `casp-start` / `casp-stop` to manage the `$casp` proxy lifecycle from the same wrapper.
Use `$casp` for app-server thread/turn orchestration, steering, forwarding server requests, or complex multi-thread routing.

## Notes

Pass either environment id or unique environment label to `--env`.
Treat `READY` and `APPLIED` as successful terminal states in watch loops.
Treat `ERROR` as terminal failure and inspect with `codex cloud status <task-id>` and `codex cloud diff <task-id>`.

## Resources

- `scripts/puff.sh`: submit/watch/launch/jobs/stop wrapper around `codex cloud`.
- `references/commands.md`: command map including optional `$casp` pairing.
