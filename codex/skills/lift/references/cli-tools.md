# Lift CLI Tools

Load only when using or changing Lift-owned `bench_stats` / `perf_report`.
Installation still requires the current task or standing environment authority.

## Zig CLI Iteration Repos

When iterating on the Zig-backed `bench_stats` / `perf_report` helper CLI path,
use these two repos:

- `skills-zig` (`$HOME/workspace/tk/skills-zig`): source for `bench_stats` and
  `perf_report`, build/test wiring, and release tags.
- `homebrew-tap` (`$HOME/workspace/tk/homebrew-tap`): Homebrew formula updates
  and checksum bumps for released `lift` binaries.

For Lift-owned CLIs, prove marker compatibility before use:

```bash
command -v bench_stats && bench_stats --help 2>&1 | grep -q bench_stats.zig
command -v perf_report && perf_report --help 2>&1 | grep -q perf_report.zig
bench_stats --input samples.txt --unit ms
perf_report --title "Perf pass" --owner "team" --system "service" --output /tmp/perf-report.md
```

## Brew-aware Launcher Pattern

```bash
run_lift_tool() {
  local subcommand="${1:-}"
  if [ -z "$subcommand" ]; then
    echo "usage: run_lift_tool <bench-stats|perf-report> [args...]" >&2
    return 2
  fi
  shift || true

  local bin="" marker=""
  case "$subcommand" in
    bench-stats) bin="bench_stats"; marker="bench_stats.zig" ;;
    perf-report) bin="perf_report"; marker="perf_report.zig" ;;
    *) echo "unknown lift subcommand: $subcommand" >&2; return 2 ;;
  esac

  install_lift_direct() {
    local repo="${SKILLS_ZIG_REPO:-$HOME/workspace/tk/skills-zig}"
    if ! command -v zig >/dev/null 2>&1; then
      echo "zig not found. Install Zig and retry." >&2
      return 1
    fi
    if [ ! -d "$repo" ]; then
      echo "skills-zig repo not found at $repo." >&2
      echo "clone it with: git clone https://github.com/tkersey/skills-zig \"$repo\"" >&2
      return 1
    fi
    (cd "$repo" && zig build -Doptimize=ReleaseSafe) || return 1
    [ -x "$repo/zig-out/bin/$bin" ] || return 1
    mkdir -p "$HOME/.local/bin"
    install -m 0755 "$repo/zig-out/bin/$bin" "$HOME/.local/bin/$bin"
  }

  if command -v "$bin" >/dev/null 2>&1 && "$bin" --help 2>&1 | grep -q "$marker"; then
    "$bin" "$@"
    return
  fi

  if [ "$(uname -s)" = "Darwin" ]; then
    command -v brew >/dev/null 2>&1 || { echo "homebrew is required on macOS" >&2; return 1; }
    brew install tkersey/tap/lift || return 1
  else
    install_lift_direct || return 1
  fi

  if command -v "$bin" >/dev/null 2>&1 && "$bin" --help 2>&1 | grep -q "$marker"; then
    "$bin" "$@"
    return
  fi

  echo "missing compatible $bin binary after install attempt" >&2
  return 1
}
```
