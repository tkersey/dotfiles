# OBSERVABILITY-AND-TELEMETRY-SURFACES

Logs, traces, telemetry, progress bars, spinners — the surfaces that report what the tool is doing while running. These cross-cut the agent-ergonomic dimensions, especially `composability` and `determinism`.

---

## The agent's expectations

Agents differ from humans in what they need from observability:

| Concern | Human user | AI agent |
|---------|------------|----------|
| Visual progress | Helpful | Noise |
| Verbose logs | Sometimes wanted | Stderr only, never stdout |
| ANSI / colors | Nice-to-have | Strip in non-TTY |
| Phone-home telemetry | Often tolerated | Often blocked (offline / sandboxed) |
| Diagnostic depth | "Why is it slow?" | Same; via `--trace-file` |
| Crash dumps | Annoying | Critical for triage |

Agent-ergonomic CLIs make every observability surface **opt-in for humans, machine-readable when accessed**.

---

## Log levels and where they go

Standard pattern:

| Level | Default in interactive | Default in non-TTY | --quiet | --verbose | --trace |
|-------|------------------------|---------------------|---------|-----------|---------|
| `error` | stderr | stderr | stderr | stderr | stderr |
| `warning` | stderr | stderr | suppressed | stderr | stderr |
| `info` | stderr | suppressed | suppressed | stderr | stderr |
| `debug` | suppressed | suppressed | suppressed | stderr | stderr |
| `trace` | suppressed | suppressed | suppressed | suppressed | trace-file |

**Rules:**
- Stdout is ALWAYS reserved for data.
- Logs ALWAYS go to stderr.
- Default in non-TTY (piped, CI) is `warning+` only — agents see less noise.
- `--trace` writes to a file, not stderr (don't pollute stderr with trace data).

---

## Robot mode + log discipline

When `--robot` is active OR `--json` is passed, suppress info/debug by default:

```rust
fn log_level_default() -> LogLevel {
    if env::var_os("MYTOOL_ROBOT").is_some() || cli.json || !std::io::stdout().is_terminal() {
        LogLevel::Warning
    } else {
        LogLevel::Info
    }
}
```

Agents can opt back in with `--verbose`:

```bash
$ mytool list --json --verbose
[2026-05-06T12:00:00Z INFO  mytool::list] loading items from cache
[2026-05-06T12:00:00Z INFO  mytool::list] cache hit (12 items)
{"ok":true,"data":{"items":[...]}}                    # stdout (data)
```

stdout is still pure JSON; logs go to stderr.

---

## Progress bars

Progress bars are TUI-flavored output. Default rules:

```rust
fn show_progress() -> bool {
    if env::var_os("CI").is_some()    { return false; }
    if env::var_os("NO_COLOR").is_some() { return false; }
    if !std::io::stderr().is_terminal()  { return false; }
    true
}
```

Plus an explicit `--no-progress` flag for CI / agents who want to suppress.

For long-running operations, emit periodic stderr lines instead of redrawing:

```bash
# Without progress bar (non-TTY)
$ mytool import big.json
[2026-05-06T12:00:00Z INFO] importing 10000 items
[2026-05-06T12:00:05Z INFO] 25% complete (2500/10000)
[2026-05-06T12:00:10Z INFO] 50% complete (5000/10000)
[2026-05-06T12:00:20Z INFO] complete (10000/10000)
{"ok":true,"data":{"imported":10000}}
```

These periodic lines parse cleanly; agents can scrape progress from stderr if they want.

---

## Spinners

Same rules as progress bars. Default off in non-TTY.

For agents that genuinely want to know "is it still running?", emit a heartbeat to stderr every N seconds:

```bash
[heartbeat] mytool sync — running 30s — phase: indexing
[heartbeat] mytool sync — running 60s — phase: indexing
[heartbeat] mytool sync — running 90s — phase: writing
```

Heartbeat format is fixed and grep-friendly. Agents check stderr periodically; if no heartbeat in expected interval, escalate.

---

## Telemetry

Many tools phone home for analytics. Two key rules:

1. **Honor opt-out env vars.** Standard list:
   - `DO_NOT_TRACK=1` (community standard, see https://consoledonottrack.com/)
   - `<TOOL>_TELEMETRY=0` (per-tool)
   - `<TOOL>_NO_ANALYTICS=1` (alternative form)

2. **Document in `capabilities --json`:**

```jsonc
"telemetry": {
  "enabled_by_default": true,
  "opt_out_env":         ["DO_NOT_TRACK", "MYTOOL_TELEMETRY"],
  "data_collected":      ["tool_version", "command_name", "exit_code", "duration_ms"],
  "endpoint":            "https://telemetry.example.com",
  "policy_url":          "https://example.com/privacy"
}
```

Agents can read this and decide whether to opt out per the user's policy.

3. **Never block on telemetry.** Telemetry must be fire-and-forget (background thread) AND have a timeout. Tools that block the main thread on telemetry POSTs are unacceptable.

4. **Never include user data in telemetry.** Tool version, command name, exit code, duration — fine. File paths, query strings, auth tokens — not fine.

---

## Trace files

For deep debugging, agents (and humans) want a structured trace:

```bash
$ mytool sync --trace-file=/tmp/mytool-trace.jsonl
{"ok":true,"data":{"synced":42}}                   # normal output

$ cat /tmp/mytool-trace.jsonl | head -3
{"ts_ns":12345,"span":"sync","event":"start"}
{"ts_ns":12500,"span":"sync.fetch_remote","event":"start","args":{"url":"..."}}
{"ts_ns":13200,"span":"sync.fetch_remote","event":"end","duration_ms":700}
```

Trace files use JSONL (one record per line). Each record has:

- `ts_ns` — relative timestamp from start (always honor SOURCE_DATE_EPOCH)
- `span` — current operation name
- `event` — `start | end | log`
- `args` / `result` / `message` per event type

Agents can post-process trace files to find slow spans or errors.

---

## Quiet mode

`--quiet` (or `-q`) is the agent-friendly default for batch operations:

```bash
$ mytool sync --quiet --json
{"ok":true,"data":{"synced":42}}
# nothing on stderr unless an error
```

Suppresses info/warning; only errors emit. Useful for CI pipelines or daemons.

---

## Standard observability flags

All CLIs should support:

| Flag | Effect |
|------|--------|
| `--quiet` / `-q` | Suppress info/warning logs |
| `--verbose` / `-v` | Add info logs (or `-vv` for debug) |
| `--trace-file=<path>` | Write trace JSONL to path |
| `--no-progress` | Suppress progress bars / spinners |
| `--no-color` | Suppress ANSI color codes |
| `--no-emoji` | Suppress emoji in output (some terminals don't render) |

Document in capabilities:

```jsonc
"flags": {
  "global": {
    "--quiet":       {"effect": "suppress info/warning"},
    "--verbose":     {"effect": "add info; -vv adds debug"},
    "--trace-file":  {"effect": "write trace JSONL", "type": "path"},
    "--no-progress": {"effect": "suppress progress UI"}
  }
}
```

---

## NO_COLOR / TERM=dumb / CI honored

Already covered in `LANGUAGE-RECIPES.md § NO_COLOR / non-TTY discipline`. Repeating because it's that important:

```rust
pub fn colors_enabled() -> bool {
    if env::var_os("NO_COLOR").is_some() { return false; }
    if let Ok(v) = env::var("TERM") {
        if v == "dumb" || v.is_empty() { return false; }
    }
    if env::var_os("CI").is_some() { return false; }
    std::io::stdout().is_terminal()
}
```

The same logic should apply to:
- ANSI color codes
- Unicode box-drawing characters (some terminals lack)
- Emoji
- Progress bars
- Spinners

Test it:

```bash
# Pipe must strip ANSI
mytool list | xxd | grep -qE 'esc\[' && echo "FAIL: ANSI in pipe" || echo "OK"

# NO_COLOR must strip
NO_COLOR=1 mytool list | xxd | grep -qE 'esc\[' && echo "FAIL" || echo "OK"

# CI must suppress prompts
CI=true mytool destructive-op --json   # must error or proceed; must not prompt
```

---

## Logging libraries — agent-ergonomic config

Per language:

**Rust + tracing:**

```rust
use tracing_subscriber::{fmt, EnvFilter};

let log_level = if env::var_os("MYTOOL_ROBOT").is_some() || !std::io::stdout().is_terminal() {
    "warn"
} else {
    "info"
};

fmt()
    .with_env_filter(EnvFilter::try_from_env("MYTOOL_LOG").unwrap_or_else(|_| EnvFilter::new(log_level)))
    .with_writer(std::io::stderr)   // logs to stderr ALWAYS
    .with_ansi(colors_enabled())
    .init();
```

**Go + slog:**

```go
import "log/slog"
import "os"

handler := slog.NewJSONHandler(os.Stderr, &slog.HandlerOptions{
    Level: defaultLevel(),
})
slog.SetDefault(slog.New(handler))
```

**Python + logging:**

```python
import logging, sys, os

level = logging.WARNING if os.environ.get('MYTOOL_ROBOT') else logging.INFO
logging.basicConfig(stream=sys.stderr, level=level)
```

**TypeScript + pino / winston:**

```typescript
import pino from 'pino';
const logger = pino({
    level: process.env.MYTOOL_ROBOT ? 'warn' : 'info',
}, pino.destination(2));   // stderr (fd 2)
```

---

## Crash dumps

Tools that can crash (panics, segfaults, uncaught exceptions) should emit a structured crash dump:

```bash
$ mytool sync
PANIC: assertion failed at src/sync.rs:42
  message: "expected non-empty input"
  thread:  main
  trace:   /tmp/mytool-crash-12345.jsonl

  please report:
    crash file: /tmp/mytool-crash-12345.jsonl
    file an issue: https://github.com/.../issues/new?template=crash
    full version info: mytool --version --verbose
```

Crash dump file:

```jsonl
{"event":"panic","ts_iso":"...","message":"...","file":"src/sync.rs","line":42}
{"event":"thread_main_backtrace","frames":[...]}
{"event":"env","tool_version":"0.4.1","rust_version":"1.74"}
```

Agents reading the panic message AND crash file can file precise bug reports.

---

## Per-archetype observability defaults

| Archetype | Progress UI | Trace file | Telemetry |
|-----------|-------------|------------|-----------|
| Search tool | Off | On (`--trace-file`) | Off |
| Package manager | On in TTY | On | Common (opt-in) |
| Build tool | On in TTY | On | Common (opt-in) |
| Test runner | On in TTY | On | Off |
| Daemon | N/A (uses syslog) | On | Off (agent-driven) |
| Scaffolder | On in TTY | Off | Off |
| Hook tool | Off | On | Off (must be sub-ms) |

---

## Anti-patterns

- **Logs on stdout.** Always stderr. Always.
- **No `--quiet` / `--verbose`.** Provide both.
- **ANSI in pipes.** Always strip in non-TTY.
- **Telemetry that blocks main thread.** Background-thread-only.
- **Telemetry without opt-out.** Honor `DO_NOT_TRACK=1` at minimum.
- **Telemetry that includes user data.** Never.
- **Progress bars that overwrite previous lines in non-TTY.** Causes garbled CI logs.
- **Crash messages without backtrace.** Useless for triage.
- **Verbose logs that interleave with stdout JSON.** Breaks parsing.

---

## Pinning observability surfaces

Add regression tests:

```bash
# audit/regression_tests/OBS-001__stdout_pure.test.sh
# Stdout in --json mode is pure JSON, even with --verbose
out=$("$TOOL" list --json --verbose 2>/dev/null)
echo "$out" | jq . > /dev/null || { echo "FAIL: --verbose contaminated stdout JSON" >&2; exit 1; }
```

```bash
# audit/regression_tests/OBS-002__telemetry_optout.test.sh
# DO_NOT_TRACK=1 disables telemetry
DO_NOT_TRACK=1 "$TOOL" list > /dev/null
# Check that no telemetry endpoint was hit (e.g. via tcpdump in test env)
```

---

## Document in robot-docs guide

```
guide:
  Logging: stdout = data, stderr = diagnostics
  Default log level: --robot or non-TTY → warn+; otherwise info+
  Verbose: -v (info), -vv (debug), --trace-file=<path> (trace)
  Quiet: --quiet (errors only)
  Progress: auto-disabled in non-TTY; --no-progress to force off
  Telemetry: opt-out via DO_NOT_TRACK=1 or MYTOOL_TELEMETRY=0
  Crash dumps: written to /tmp/mytool-crash-<pid>.jsonl
```

This block in `robot-docs guide` tells agents everything they need to know about observability surfaces in 80 chars per line.
