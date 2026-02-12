# Puff Command Map

## Primary Path (Codex Cloud)

Use this path for cloud background task execution from CLI.

- Doctor check (auth + env resolution):
  `~/.dotfiles/codex/skills/puff/scripts/puff.sh doctor --env <env>`
- Submit only:
  `~/.dotfiles/codex/skills/puff/scripts/puff.sh submit --env <env> --prompt "..."`
- Watch in foreground:
  `~/.dotfiles/codex/skills/puff/scripts/puff.sh watch --task <task-id-or-url>`
- Launch detached watcher:
  `~/.dotfiles/codex/skills/puff/scripts/puff.sh launch --env <env> --prompt "..."`
- List jobs:
  `~/.dotfiles/codex/skills/puff/scripts/puff.sh jobs`
- Stop job:
  `~/.dotfiles/codex/skills/puff/scripts/puff.sh stop --job <job-id>`

Direct Codex Cloud commands:
- `codex cloud list --json`
- `codex cloud status <task-id>`
- `codex cloud diff <task-id>`
- `codex cloud apply <task-id>`

## Optional Advanced Path ($casp)

Use `$casp` when you need programmatic multi-thread orchestration, turn steering, or server-request routing beyond simple cloud task polling.

Typical pairing:
1. Use `$puff` to submit independent cloud tasks quickly.
2. Use `$casp` to orchestrate complex app-server thread/turn flows or integrate custom automation.

Start/stop proxy via puff:
- `~/.dotfiles/codex/skills/puff/scripts/puff.sh casp-start --cwd <workspace>`
- `~/.dotfiles/codex/skills/puff/scripts/puff.sh casp-stop`

Start proxy directly (advanced):
- `node ~/.dotfiles/codex/skills/casp/scripts/casp_proxy.mjs`

Then drive methods like:
- `thread/start`
- `turn/start`
- `thread/resume`
- `turn/steer`
