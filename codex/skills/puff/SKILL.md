---
name: puff
description: Launch and manage Codex Cloud tasks from the CLI, including detached background watchers that track completion. Use when users ask to run coding work in cloud/background agents, queue multiple cloud tasks, poll task status, fetch cloud diffs, apply cloud outputs locally, or pair cloud kickoff with `$cas` orchestration.
---

# Puff

## Overview

Use this skill to launch Codex Cloud tasks without blocking the local CLI session. Use the bundled wrapper to submit work, detach status watchers, and retain logs/results for later diff/apply actions.

## Workflow

1. Ensure ChatGPT auth is present.
`codex login`
2. Resolve skill paths (`.codex` primary, `.claude` fallback).
```bash
CODEX_SKILLS_HOME="${CODEX_HOME:-$HOME/.codex}"
CLAUDE_SKILLS_HOME="${CLAUDE_HOME:-$HOME/.claude}"
PUFF_SCRIPT="$CODEX_SKILLS_HOME/skills/puff/scripts/puff.sh"
[ -f "$PUFF_SCRIPT" ] || PUFF_SCRIPT="$CLAUDE_SKILLS_HOME/skills/puff/scripts/puff.sh"
```
3. Run readiness checks.
`"$PUFF_SCRIPT" doctor --env <env-id-or-label>`
Optional: print manual environment-creation instructions.
`"$PUFF_SCRIPT" create`
4. Launch cloud work with a detached watcher.
`"$PUFF_SCRIPT" launch --env <env-id-or-label> --prompt "Implement X"`
Optional: launch the cloud Join operator prompt (`seq -> join`) for PR patch routing.
`"$PUFF_SCRIPT" join-operator --env <env-id-or-label> --repo <owner/repo> --patch-inbox <locator>`
Canary mode (single bounded cycle):
`"$PUFF_SCRIPT" join-operator --env <env-id-or-label> --repo <owner/repo> --patch-inbox <locator> --canary`
5. Inspect running and completed watcher jobs.
`"$PUFF_SCRIPT" jobs`
6. Tail watcher logs when needed.
`tail -f <watch_log_path>`
7. Inspect or apply result when ready.
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
Use `$puff` `cas-start` / `cas-stop` to manage the `$cas` proxy lifecycle from the same wrapper.
Use `$cas` for app-server thread/turn orchestration, steering, forwarding server requests, or complex multi-thread routing.

## Notes

Pass either environment id or unique environment label to `--env`.
Treat `READY` and `APPLIED` as successful terminal states in watch loops.
Treat `ERROR` as terminal failure and inspect with `codex cloud status <task-id>` and `codex cloud diff <task-id>`.

## Resources

- `scripts/puff.sh`: create/submit/watch/launch/jobs/stop wrapper around `codex cloud`.
- `scripts/puff.sh join-operator`: launch helper for cloud join operator prompts.
- `references/commands.md`: command map including optional `$cas` pairing.
