# Puff Command Map

## Primary Path (Codex Cloud)

Use this path for cloud background task execution from CLI.

```bash
CODEX_SKILLS_HOME="${CODEX_HOME:-$HOME/.codex}"
CLAUDE_SKILLS_HOME="${CLAUDE_HOME:-$HOME/.claude}"
PUFF_SCRIPT="$CODEX_SKILLS_HOME/skills/puff/scripts/puff.sh"
[ -f "$PUFF_SCRIPT" ] || PUFF_SCRIPT="$CLAUDE_SKILLS_HOME/skills/puff/scripts/puff.sh"
CAS_PROXY_SCRIPT="$CODEX_SKILLS_HOME/skills/cas/scripts/cas_proxy.mjs"
[ -f "$CAS_PROXY_SCRIPT" ] || CAS_PROXY_SCRIPT="$CLAUDE_SKILLS_HOME/skills/cas/scripts/cas_proxy.mjs"
```

- Doctor check (auth + env resolution):
  `"$PUFF_SCRIPT" doctor --env <env>`
- Create instructions only (manual environment creation; no API call):
  `"$PUFF_SCRIPT" create`
- Submit only:
  `"$PUFF_SCRIPT" submit --env <env> --prompt "..."`
- Watch in foreground:
  `"$PUFF_SCRIPT" watch --task <task-id-or-url>`
- Launch detached watcher:
  `"$PUFF_SCRIPT" launch --env <env> --prompt "..."`
- List jobs:
  `"$PUFF_SCRIPT" jobs`
- Stop job:
  `"$PUFF_SCRIPT" stop --job <job-id>`

Direct Codex Cloud commands:
- `codex cloud list --json`
- `codex cloud status <task-id>`
- `codex cloud diff <task-id>`
- `codex cloud apply <task-id>`

## Optional Advanced Path ($cas)

Use `$cas` when you need programmatic multi-thread orchestration, turn steering, or server-request routing beyond simple cloud task polling.

Typical pairing:
1. Use `$puff` to submit independent cloud tasks quickly.
2. Use `$cas` to orchestrate complex app-server thread/turn flows or integrate custom automation.

Start/stop proxy via puff:
- `"$PUFF_SCRIPT" cas-start --cwd <workspace>`
- `"$PUFF_SCRIPT" cas-stop`

Start proxy directly (advanced):
- `node "$CAS_PROXY_SCRIPT"`

Then drive methods like:
- `thread/start`
- `turn/start`
- `thread/resume`
- `turn/steer`
