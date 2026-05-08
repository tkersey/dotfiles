# TUI-MODE-AUDIT — Auditing TUI-flavored CLIs (charmbracelet, frankentui, ratatui)

Many modern CLIs ship a TUI interface. TUIs are great for humans but **must be gated behind explicit invocation** so they don't trap automated agents.

This file extends the methodology for tools that have BOTH a TUI mode AND an agent-targeted CLI surface.

---

## The TUI-trap problem

When an agent invokes:

```bash
$ mytool
```

If `mytool` launches a full-screen TUI:
- The agent's Bash tool blocks waiting for output
- After timeout, the agent retries (still gets stuck)
- The agent loses cycles unable to tell "did the tool work" from "is it still running"

This is the **agent-hostility-by-default** anti-pattern. Tools like `bv` and `cass` get this right by **mandating** `--robot-*` flags for non-TTY use. Tools that get it wrong silently waste agent time.

---

## Architecture: gated TUI

The agent-ergonomic TUI architecture:

```
┌───────────────────────────────────────────────┐
│  Tool entry point (main)                      │
│  ─> detect TTY context                        │
│  ─> if non-TTY OR --robot OR --json:          │
│       skip TUI; route to agent surface        │
│     else:                                     │
│       launch TUI                              │
└───────────────────────────────────────────────┘
```

Concretely:

```rust
fn main() -> Result<()> {
    let cli = Cli::parse();

    // If user explicitly requested non-TUI surface → skip TUI
    if cli.robot || cli.json || cli.command.is_some() {
        return run_cli_surface(cli);
    }

    // If non-TTY context → skip TUI; emit guidance instead
    if !std::io::stdout().is_terminal() {
        eprintln!("error: refusing to launch TUI in non-TTY context");
        eprintln!("hint: use 'mytool --robot' for automation, or 'mytool <verb>' for a specific action");
        eprintln!("see also: 'mytool capabilities --json' or 'mytool robot-docs guide'");
        std::process::exit(1);
    }

    // Otherwise: launch TUI
    run_tui()
}
```

---

## Auditing TUI-flavored tools

### Phase 1: surface inventory adjustments

For TUI-flavored tools, inventory adds:

- **TUI keys/shortcuts** — e.g. `bv`'s TUI key bindings (j/k/G/gg/q/etc.)
- **TUI views** — actionable, board, graph, history, insights panels
- **TUI filters** — open/closed/ready/label/search modes
- **TUI actions** — time-travel, export, copy

Each is a surface BUT with a `non_agent_target: true` flag because they're for humans.

```jsonc
{
  "surface_id": "tui_action__bv__copy_id",
  "kind": "tui_action",
  "name": "y",
  "description": "Copy issue ID (TUI shortcut)",
  "non_agent_target": true,
  "scoring_skip_reasons": ["tui_only"]
}
```

These surfaces don't get scored on most dims (n/a:true) but DO get scored on:
- `composability` — does the TUI degrade to agent-mode in non-TTY?
- `intuitiveness` — does pressing 'q' actually quit (not 'q for QUERY')?

### Phase 2: TUI-specific scoring

Add a meta-dimension `tui_gate` that scores how well the tool gates its TUI:

```
0:    TUI launches in any non-TTY context; blocks agents
250:  TUI launches in non-TTY but exits cleanly after timeout
500:  TUI gated behind `--tui` flag; non-TTY default is help text
750:  All of 500 PLUS: `--robot-*` family is mandatory documentation; bare invocation in non-TTY
      emits useful error
1000: All of 750 PLUS: --robot-help in-tool guide; capabilities lists `tui_available: true` and
      gating behavior
```

Anchor: `bv` and `cass` score 1000.

### Phase 4: TUI-specific recommendations

Common recs:

| Rec | Description |
|-----|-------------|
| TR-1 | Detect non-TTY at startup; emit guidance |
| TR-2 | Mandate `--robot-*` for automation; document in --help |
| TR-3 | Provide capabilities-equivalent for TUI (e.g. `<tool> tui --capabilities --json`) |
| TR-4 | Include `tui_available: true` in `capabilities --json` |
| TR-5 | Document keys/shortcuts in `<tool> robot-docs guide § TUI` (for human reference) |

---

## Charmbracelet-specific patterns (Bubble Tea, Lip Gloss, Gum)

If the target uses Bubble Tea (Go TUI framework):

- `tea.NewProgram(model)` is the entry point
- `tea.WithAltScreen()` enables full-screen TUI
- Detect non-TTY via `isatty.IsTerminal(os.Stdout.Fd())`

Recommended pattern:

```go
func main() {
    if shouldRunCLI(os.Args, os.Stdout.Fd()) {
        runCLI()
        return
    }
    p := tea.NewProgram(model{}, tea.WithAltScreen())
    p.Run()
}

func shouldRunCLI(args []string, fd uintptr) bool {
    // Has explicit subcommand
    for _, a := range args[1:] {
        if !strings.HasPrefix(a, "-") {
            return true
        }
    }
    // Has --robot or --json
    for _, a := range args {
        if a == "--robot" || a == "--json" {
            return true
        }
    }
    // Non-TTY context
    return !isatty.IsTerminal(fd)
}
```

---

## Ratatui-specific patterns (Rust)

For Rust TUIs using ratatui:

```rust
use std::io::IsTerminal;

fn main() -> Result<()> {
    let cli = Cli::parse();
    
    // Skip TUI for explicit subcommand or non-TTY
    if cli.command.is_some() || cli.robot || !std::io::stdout().is_terminal() {
        return run_cli_surface(cli);
    }
    
    // Setup TUI
    enable_raw_mode()?;
    let mut stdout = io::stdout();
    execute!(stdout, EnterAlternateScreen)?;
    let backend = CrosstermBackend::new(stdout);
    let mut terminal = Terminal::new(backend)?;
    
    let result = run_tui_loop(&mut terminal);
    
    disable_raw_mode()?;
    execute!(terminal.backend_mut(), LeaveAlternateScreen)?;
    
    result
}
```

---

## frankentui-specific patterns

For tools using the frankentui framework:

```rust
use frankentui::{Doctor, Showcase};

fn main() {
    if /* should run TUI */ {
        Showcase::default().run();
    } else {
        // Route to CLI surface
    }
}
```

Plus `doctor_frankentui` for self-diagnosis.

---

## Capabilities for TUI-flavored tools

`<tool> capabilities --json` should include:

```jsonc
{
  "tui": {
    "available": true,
    "framework": "ratatui" | "bubble-tea" | "frankentui" | "ncurses" | "blessed-contrib",
    "auto_launch_in_tty": true,
    "gate_method": "detect_non_tty + explicit_subcommand",
    "robot_docs_section": "robot-docs guide § TUI"
  }
}
```

---

## TUI keybinding documentation

For human-facing reference, document keybindings in robot-docs guide:

```
TUI mode (run `<tool>` without args in TTY):
  j / k          — move down / up
  gg / G         — jump to top / bottom
  enter          — open selected
  /              — search
  q              — quit
  ?              — help overlay
  shift+arrows   — extended navigation

To bypass TUI for automation:
  <tool> --robot-<verb>     — robot-mode invocation
  <tool> capabilities --json — introspect
  <tool> robot-docs guide   — agent handbook (this output)
```

Agents can still find this if they encounter `bv` or similar tools mid-task.

---

## Common TUI anti-patterns

### TA-1: Bare invocation launches TUI without checking TTY

Tools just call `tea.NewProgram(...).Run()` at top of main without TTY detection. Trap.

**Fix.** Detect non-TTY → emit error + exit non-zero.

### TA-2: --help launches TUI

Tools that have `--help` open a TUI for help instead of printing text. Agents read text; agents cannot read TUI.

**Fix.** `--help` always emits text to stdout.

### TA-3: TUI is the only way to perform certain actions

Some actions only available via TUI keypress (e.g. "press shift+R to refresh"). Agents can't drive these.

**Fix.** Every TUI action has a CLI verb equivalent.

### TA-4: TUI consumes stdin

TUI uses raw mode and reads stdin. Agent piping data into the tool unintentionally invokes TUI input.

**Fix.** Detect piped stdin; route to non-interactive mode.

### TA-5: TUI doesn't exit cleanly on Ctrl+C

Tool ignores SIGINT or hangs in event loop after Ctrl+C. Agent's Bash tool can't kill cleanly.

**Fix.** Robust signal handling; clean shutdown on any interrupt.

### TA-6: TUI requires terminal of specific size

Tool errors with "terminal too small (need 120x40)" when run in narrow CI terminal.

**Fix.** Adapt layout to size; gracefully fall back; don't error.

---

## Hybrid TUI + CLI architecture

Some tools want a UNIFIED experience: TUI when interactive, CLI when not. Example tool architectures:

### Architecture A: Single binary, dual mode (bv, k9s)

One binary; detects context; routes to TUI or CLI surface.

```
bv               # TUI (default in TTY)
bv --robot-triage  # CLI mode (mandatory in non-TTY)
```

### Architecture B: Two binaries (kubectl + k9s)

Separate binaries for separate purposes. kubectl is CLI-first; k9s is TUI-first.

```
kubectl get pods   # CLI
k9s                # TUI (always)
```

### Architecture C: TUI as a verb (mytool tui)

CLI is default; TUI launched via explicit verb.

```
mytool list       # CLI
mytool tui        # TUI (only if TTY)
```

For agent-ergonomic audits:
- Architecture A scores best when gating is robust
- Architecture B scores well; just audit each separately
- Architecture C is fine for tools where CLI is primary

---

## Phase 9 simulation for TUI-flavored tools

The fresh-context simulator should attempt:

```
Task X: Run `<tool>` (bare). What happens? Should not be a TUI in non-TTY context.
```

If the simulator gets stuck waiting for output, that's a finding.

Plus the TR-1 through TR-5 recs above directly translate to canonical tasks.

---

## Cross-references

- `methodology/CLI-ARCHETYPES.md` — many archetypes overlap with TUI-flavored
- `methodology/OBSERVABILITY-AND-TELEMETRY-SURFACES.md` — non-TTY discipline (overlap)
- `references/exemplars/CANONICAL-EXEMPLARS-DEEP.md` — bv and cass anchor TUI gating
- `/tui-glamorous` skill — companion skill for designing the TUI itself
- `/frankentui` skill — for FrankenTUI-specific tools
