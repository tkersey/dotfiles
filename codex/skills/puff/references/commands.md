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

- Doctor check (auth + env resolution):
  `run_puff_tool doctor --env <env>`
- Create instructions only (manual environment creation; no API call):
  `run_puff_tool create`
- Submit only:
  `run_puff_tool submit --env <env> --prompt "..."`
- Watch in foreground:
  `run_puff_tool watch --task <task-id-or-url>`
- Launch detached watcher:
  `run_puff_tool launch --env <env> --prompt "..."`
- Launch cloud Join operator prompt (`seq -> join`):
  `run_puff_tool join-operator --env <env> --repo <owner/repo> --patch-inbox <locator>`
- Launch single-cycle canary:
  `run_puff_tool join-operator --env <env> --repo <owner/repo> --patch-inbox <locator> --canary`
- List jobs:
  `run_puff_tool jobs`
- Stop job:
  `run_puff_tool stop --job <job-id>`

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
- `run_puff_tool cas-start --cwd <workspace>`
- `run_puff_tool cas-stop`

Start proxy directly (advanced):
- `node "$CAS_PROXY_SCRIPT"`

Then drive methods like:
- `thread/start`
- `turn/start`
- `thread/resume`
- `turn/steer`
