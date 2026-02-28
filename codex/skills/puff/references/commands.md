# Puff Command Map

## Primary Path (Codex Cloud)

Use this path for cloud background task execution from CLI.

```bash
CODEX_SKILLS_HOME="${CODEX_HOME:-$HOME/.codex}"
CLAUDE_SKILLS_HOME="${CLAUDE_HOME:-$HOME/.claude}"
CAS_PROXY_SCRIPT="$CODEX_SKILLS_HOME/skills/cas/scripts/cas_proxy.mjs"
[ -f "$CAS_PROXY_SCRIPT" ] || CAS_PROXY_SCRIPT="$CLAUDE_SKILLS_HOME/skills/cas/scripts/cas_proxy.mjs"

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

Proxy lifecycle is managed by `$cas` (not `$puff`):
- `node "$CAS_PROXY_SCRIPT"`

Then drive methods like:
- `thread/start`
- `turn/start`
- `thread/resume`
- `turn/steer`
