# LANGUAGE-RECIPES — Per-Language Framework Cookbook

Concrete, copy-pasteable code for adding the agent-ergonomic surfaces (`--json`, `--robot-*`, `capabilities --json`, `robot-docs guide`, exit-code dictionary, error-pedagogy hints, intent inference) to every supported language and CLI framework.

When an applier subagent needs to apply a recommendation, they pull from this file. Phase 8 self-doc-hardening agents use it as the canonical implementation anchor.

Sections:

1. [Rust + clap](#rust--clap)
2. [Rust + argh / lexopt / pico-args / hand-rolled](#rust--alternatives)
3. [Go + cobra](#go--cobra)
4. [Go + standard flag](#go--standard-flag)
5. [Python + argparse](#python--argparse)
6. [Python + click / typer](#python--click--typer)
7. [TypeScript + commander](#typescript--commander)
8. [TypeScript + yargs](#typescript--yargs)
9. [TypeScript + oclif](#typescript--oclif)
10. [Bash + getopts / hand-rolled](#bash--getopts--hand-rolled)
11. [Ruby + thor](#ruby--thor)
12. [Cross-cutting helpers](#cross-cutting-helpers)

Each section follows the same shape:

- **Inventory hints** — where surfaces live in the source (file:line patterns)
- **Add `--json`** — flag + plumbing
- **Add `--robot-*`** — global mode flag detection
- **Add `capabilities --json`** — paste-ready endpoint
- **Add `robot-docs guide`** — paste-ready endpoint
- **Exit-code dictionary** — enum + match + documentation
- **Error pedagogy** — wrap framework errors with project-specific guidance
- **Intent inference** — levenshtein-1 typo correction
- **NO_COLOR / non-TTY discipline** — paste-ready helpers
- **Determinism helpers** — sorted output, SOURCE_DATE_EPOCH, deterministic IDs

Treat the snippets as starting points. Adapt naming to project idioms.

---

## Rust + clap

### Inventory hints

- Subcommand defs: `Command::new(...).subcommand(...)` or `#[derive(Subcommand)]` enum variants
- Flag defs: `.arg(Arg::new(...).long(...))` or `#[arg(long, short, env)]`
- Env-var bindings: `#[arg(env = "MYTOOL_HOME")]`
- Exit codes: `std::process::exit(N)` or `Result<(), eyre::Report>` returns from main
- Error literals: `bail!()`, `Err(...)`, `panic!()`, `eprintln!()` followed by `exit`

### Add `--json` to a verb (clap derive)

```rust
// src/cmd/list.rs
use clap::Args;

#[derive(Args)]
pub struct ListArgs {
    /// Output JSON instead of human-readable.
    #[arg(long, short = 'j', help = "Emit JSON to stdout (data only). Logs go to stderr.")]
    pub json: bool,

    /// Show extra parseability metadata (search_mode, fallback_tier, etc.)
    #[arg(long, requires = "json")]
    pub robot_meta: bool,
}

pub fn run(args: ListArgs) -> Result<(), Error> {
    let items = load_items()?;
    if args.json {
        let payload = serde_json::json!({
            "ok": true,
            "items": items,
            "meta": if args.robot_meta {
                Some(serde_json::json!({
                    "data_hash": compute_data_hash(&items),
                    "search_mode": "lexical",
                    "fallback_tier": null
                }))
            } else { None }
        });
        println!("{}", serde_json::to_string(&payload)?);
    } else {
        for item in items { println!("{}", item.display()); }
    }
    Ok(())
}
```

### Add a global `--robot-*` family

```rust
// src/cli.rs
use clap::Parser;

#[derive(Parser)]
#[command(name = "mytool", version, about = "...")]
pub struct Cli {
    #[command(subcommand)]
    pub command: Command,

    /// Force machine-readable output for any verb. Implies --json where applicable.
    /// Detects non-TTY and emits stderr guidance otherwise.
    #[arg(long, global = true, env = "MYTOOL_ROBOT")]
    pub robot: bool,

    /// Emit a paste-ready agent handbook.
    #[arg(long = "robot-help", global = true)]
    pub robot_help: bool,
}

pub fn main() -> Result<(), Error> {
    let cli = Cli::parse();

    if cli.robot_help {
        print!("{}", include_str!("../docs/robot-docs.txt"));
        return Ok(());
    }

    if cli.robot && std::io::stdout().is_terminal() {
        eprintln!("note: --robot active; output will be machine-readable on stdout");
    }

    cli.command.run(cli.robot)
}
```

### Add `capabilities --json` (single source of truth)

```rust
// src/capabilities.rs
use serde_json::json;

pub fn capabilities() -> serde_json::Value {
    json!({
        "version": env!("CARGO_PKG_VERSION"),
        "contract_version": "1",
        "features": [
            "json_output",
            "robot_meta",
            "levenshtein_typo_hint",
            "deterministic_output",
            "no_color_honored"
        ],
        "commands": {
            "list":    {"description": "List all items.",      "mutates": false, "json": true,  "robot": "--json"},
            "add":     {"description": "Add an item.",         "mutates": true,  "json": true,  "robot": "--json", "gates": ["--yes"]},
            "delete":  {"description": "Remove an item.",      "mutates": true,  "json": true,  "robot": "--json", "gates": ["--yes", "--dry-run"]},
            "doctor":  {"description": "Self-diagnose.",       "mutates": false, "json": true,  "robot": "--json"}
        },
        "exit_codes": {
            "0": "success",
            "1": "user-input-error",
            "2": "safety-block",
            "3": "tool-environment-error",
            "4": "transient-failure"
        },
        "env_vars": {
            "MYTOOL_HOME":  {"description": "Root config dir", "default": "$XDG_CONFIG_HOME/mytool"},
            "MYTOOL_ROBOT": {"description": "Force --robot mode", "default": "unset"},
            "NO_COLOR":     {"description": "Honored if set",  "default": "unset"},
            "CI":           {"description": "Honored if true (suppresses prompts)", "default": "unset"}
        },
        "limits": {
            "max_items_per_list": 10000,
            "default_timeout_seconds": 30
        }
    })
}

// src/cmd/capabilities.rs
pub fn run() -> Result<(), Error> {
    println!("{}", serde_json::to_string_pretty(&capabilities())?);
    Ok(())
}
```

### Add `robot-docs guide`

Embed a markdown handbook in-tool via `include_str!`:

```rust
// src/cmd/robot_docs.rs
const GUIDE: &str = include_str!("../../docs/robot-docs.md");

pub fn run(topic: &str) -> Result<(), Error> {
    match topic {
        "guide" => print!("{}", GUIDE),
        "commands" => print!("{}", include_str!("../../docs/robot-docs-commands.md")),
        "examples" => print!("{}", include_str!("../../docs/robot-docs-examples.md")),
        other => {
            eprintln!("error: unknown robot-docs topic '{}'", other);
            eprintln!("hint: try one of: guide | commands | examples");
            std::process::exit(1);
        }
    }
    Ok(())
}
```

`docs/robot-docs.md` should be paste-ready, < 80 lines:

```markdown
guide:
  Robot-mode handbook for mytool v{{VERSION}}
  Output: --json (data) on stdout; --verbose adds stderr logs
  Modes: --robot forces --json on every read-side verb
  Stdout/stderr: stdout = data only, stderr = diagnostics
  Exit codes: 0=success, 1=user-input, 2=safety-block, 3=env, 4=transient
  Mega-call: `mytool doctor --json` returns health + status + recommended_action
  Quick refs: `mytool capabilities --json`, `mytool robot-docs commands`
```

### Exit-code dictionary as a Rust enum

```rust
// src/exit_code.rs
#[derive(Debug, Clone, Copy)]
#[repr(u8)]
pub enum ExitCode {
    Success = 0,
    UserInputError = 1,
    SafetyBlock = 2,
    EnvironmentError = 3,
    TransientFailure = 4,
}

impl ExitCode {
    pub fn description(self) -> &'static str {
        match self {
            Self::Success => "success",
            Self::UserInputError => "user-input-error: bad arg, missing required, typo",
            Self::SafetyBlock => "safety-block: refused destructive op without --yes",
            Self::EnvironmentError => "tool-environment-error: missing config, bad permissions",
            Self::TransientFailure => "transient-failure: retry safe (network, lock-busy)",
        }
    }
    pub fn exit(self) -> ! { std::process::exit(self as i32) }
}
```

In your error handling:

```rust
fn handle_error(e: &Error) -> ExitCode {
    match e {
        Error::ArgParse(_) => ExitCode::UserInputError,
        Error::DangerousWithoutYes(_) => ExitCode::SafetyBlock,
        Error::ConfigNotFound(_) => ExitCode::EnvironmentError,
        Error::Network(_) | Error::LockBusy => ExitCode::TransientFailure,
        _ => ExitCode::EnvironmentError,
    }
}
```

### Levenshtein-1 typo hint (intent_inference)

```rust
// src/cli/typo_hint.rs
const KNOWN_FLAGS: &[&str] = &[
    "json", "verbose", "quiet", "color", "no-color", "config", "yes", "dry-run",
    "robot", "robot-help", "version", "help",
];

fn levenshtein_1(a: &str, b: &str) -> bool {
    let (la, lb) = (a.len(), b.len());
    if (la as i32 - lb as i32).abs() > 1 { return false; }
    let mut diffs = 0usize;
    let (mut ai, mut bi) = (a.bytes(), b.bytes());
    let (mut ac, mut bc) = (ai.next(), bi.next());
    while ac.is_some() || bc.is_some() {
        match (ac, bc) {
            (Some(x), Some(y)) if x == y => { ac = ai.next(); bc = bi.next(); }
            (Some(_), Some(_)) if la == lb => { diffs += 1; ac = ai.next(); bc = bi.next(); }
            (Some(_), Some(_)) if la > lb  => { diffs += 1; ac = ai.next(); }
            (Some(_), Some(_)) /* la < lb */ => { diffs += 1; bc = bi.next(); }
            (Some(_), None) => { diffs += 1; ac = ai.next(); }
            (None, Some(_)) => { diffs += 1; bc = bi.next(); }
            (None, None) => break,
        }
        if diffs > 1 { return false; }
    }
    diffs == 1
}

pub fn closest_known_flag(unknown: &str) -> Option<&'static str> {
    let stripped = unknown.trim_start_matches('-');
    KNOWN_FLAGS.iter().copied().find(|k| levenshtein_1(stripped, k))
}
```

In your error handler (replace the framework's default "unknown flag" error):

```rust
fn map_clap_error(e: clap::Error) -> Error {
    if let clap::error::ErrorKind::UnknownArgument = e.kind() {
        if let Some(token) = e.context().find_map(|(k, v)| {
            (k == clap::error::ContextKind::InvalidArg).then_some(v)
        }) {
            let s = token.to_string();
            if let Some(suggestion) = closest_known_flag(&s) {
                return Error::UnknownFlagDidYouMean(s, format!("--{}", suggestion));
            }
        }
    }
    Error::ClapPassthrough(e.to_string())
}
```

### NO_COLOR / non-TTY discipline

```rust
// src/styling.rs
use std::io::{self, IsTerminal};

pub fn colors_enabled() -> bool {
    if std::env::var_os("NO_COLOR").is_some() { return false; }
    if let Ok(v) = std::env::var("TERM") {
        if v == "dumb" || v.is_empty() { return false; }
    }
    if std::env::var_os("CI").is_some() { return false; }
    io::stdout().is_terminal()
}

pub fn detect_non_tty_for_robot() -> bool {
    !io::stdout().is_terminal() || std::env::var_os("CI").is_some()
}
```

Then early in main:

```rust
if launches_tui_by_default() && detect_non_tty_for_robot() {
    eprintln!("error: refusing to launch TUI in non-TTY context");
    eprintln!("hint: use 'mytool --robot <verb> --json' for automation");
    eprintln!("see also: 'mytool capabilities --json' or 'mytool robot-docs guide'");
    return Ok(ExitCode::UserInputError.exit());
}
```

### Determinism helpers

```rust
// src/determinism.rs
pub fn source_date_epoch() -> Option<u64> {
    std::env::var("SOURCE_DATE_EPOCH").ok().and_then(|s| s.parse().ok())
}

pub fn now_ms() -> u64 {
    if let Some(epoch) = source_date_epoch() { return epoch * 1000; }
    use std::time::{SystemTime, UNIX_EPOCH};
    SystemTime::now().duration_since(UNIX_EPOCH).map(|d| d.as_millis() as u64).unwrap_or(0)
}

pub fn data_hash<T: serde::Serialize>(t: &T) -> String {
    use sha2::{Digest, Sha256};
    let bytes = serde_json::to_vec(t).unwrap_or_default();
    let mut hasher = Sha256::new();
    hasher.update(&bytes);
    let hex = hex::encode(hasher.finalize());
    hex[..16].to_string() // truncate; full hash via --robot-meta
}
```

Sort iteration order before serialization:

```rust
let mut items: Vec<_> = collection.iter().collect();
items.sort_by_key(|item| item.id.clone()); // or content-hash
```

---

## Rust — Alternatives

For tools using `argh`, `lexopt`, `pico-args`, or hand-rolled parsing:

- The shape is identical to clap; only the binding syntax differs.
- For `argh`: `#[derive(FromArgs)]` and `#[argh(option, short = 'j')]`.
- For `lexopt`: pattern-match on `Arg::Long(name)` and emit your own typo hint when the catch-all fires.
- For hand-rolled: implement levenshtein-1 hint as a single function called when unrecognized argv tokens are encountered.

The `capabilities`, `robot-docs`, exit-code, and determinism helpers are all framework-agnostic — they live in their own modules.

---

## Go + cobra

### Inventory hints

- Subcommand defs: `&cobra.Command{Use: "list", ...}` typically in `cmd/<name>/main.go` or `internal/cmd/`
- Flag defs: `cmd.Flags().StringP(...)`, `cmd.PersistentFlags().Bool(...)`
- Env-var bindings: `viper.BindEnv(...)` or `os.Getenv(...)`
- Exit codes: `os.Exit(N)`, often via `cobra`'s SilenceErrors + a top-level switch

### Add `--json` to a verb

```go
// internal/cmd/list.go
package cmd

import (
    "encoding/json"
    "fmt"
    "github.com/spf13/cobra"
)

var listJSON bool
var listRobotMeta bool

func newListCmd() *cobra.Command {
    cmd := &cobra.Command{
        Use:   "list",
        Short: "List all items.",
        RunE: func(cmd *cobra.Command, args []string) error {
            items, err := loadItems()
            if err != nil { return err }
            if listJSON {
                payload := map[string]any{
                    "ok":    true,
                    "items": items,
                }
                if listRobotMeta {
                    payload["meta"] = map[string]any{
                        "data_hash":     dataHash(items),
                        "search_mode":   "lexical",
                        "fallback_tier": nil,
                    }
                }
                enc := json.NewEncoder(cmd.OutOrStdout())
                enc.SetIndent("", "")
                return enc.Encode(payload)
            }
            for _, item := range items {
                fmt.Fprintln(cmd.OutOrStdout(), item.Display())
            }
            return nil
        },
    }
    cmd.Flags().BoolVarP(&listJSON, "json", "j", false, "Emit JSON to stdout. Logs go to stderr.")
    cmd.Flags().BoolVar(&listRobotMeta, "robot-meta", false, "Include parseability metadata (data_hash, search_mode).")
    return cmd
}
```

### Global `--robot` flag

```go
// internal/cmd/root.go
var robotMode bool
var robotHelp bool

func newRootCmd() *cobra.Command {
    cmd := &cobra.Command{
        Use:   "mytool",
        Short: "...",
        PersistentPreRunE: func(cmd *cobra.Command, args []string) error {
            if robotHelp {
                fmt.Print(RobotDocsGuide)
                os.Exit(0)
            }
            if robotMode && isatty.IsTerminal(os.Stdout.Fd()) {
                fmt.Fprintln(os.Stderr, "note: --robot active; output will be machine-readable on stdout")
            }
            return nil
        },
    }
    cmd.PersistentFlags().BoolVar(&robotMode, "robot", false, "Force machine-readable output for any verb.")
    cmd.PersistentFlags().BoolVar(&robotHelp, "robot-help", false, "Print agent handbook to stdout.")
    return cmd
}
```

### `capabilities --json`

```go
// internal/capabilities/capabilities.go
package capabilities

import "encoding/json"

const ContractVersion = "1"

func Build(version string) map[string]any {
    return map[string]any{
        "version":          version,
        "contract_version": ContractVersion,
        "features":         []string{"json_output", "robot_meta", "levenshtein_typo_hint", "deterministic_output"},
        "commands": map[string]any{
            "list":   map[string]any{"description": "List items.",   "mutates": false, "json": true, "robot": "--json"},
            "add":    map[string]any{"description": "Add an item.",  "mutates": true,  "json": true, "gates": []string{"--yes"}},
            "delete": map[string]any{"description": "Remove item.",  "mutates": true,  "json": true, "gates": []string{"--yes", "--dry-run"}},
        },
        "exit_codes": map[string]string{
            "0": "success",
            "1": "user-input-error",
            "2": "safety-block",
            "3": "tool-environment-error",
            "4": "transient-failure",
        },
        "env_vars": map[string]map[string]string{
            "MYTOOL_HOME": {"description": "Config dir", "default": "$XDG_CONFIG_HOME/mytool"},
            "NO_COLOR":    {"description": "Honored",     "default": "unset"},
            "CI":          {"description": "Honored",     "default": "unset"},
        },
    }
}

func MustJSON(version string) string {
    b, _ := json.MarshalIndent(Build(version), "", "  ")
    return string(b)
}
```

### Cobra error wrapping for typo hints

```go
// internal/cmd/typo_hint.go
package cmd

var KnownFlags = []string{
    "json", "verbose", "quiet", "color", "no-color", "config", "yes", "dry-run",
    "robot", "robot-help", "version", "help",
}

func ClosestKnownFlag(s string) string {
    s = strings.TrimLeft(s, "-")
    for _, k := range KnownFlags {
        if levenshtein1(s, k) { return k }
    }
    return ""
}

// In root.go:
rootCmd.SetFlagErrorFunc(func(cmd *cobra.Command, err error) error {
    msg := err.Error()
    // Extract the bad token; cobra format: "unknown flag: --foo"
    if i := strings.Index(msg, "--"); i != -1 {
        token := strings.Fields(msg[i:])[0]
        if suggestion := ClosestKnownFlag(token); suggestion != "" {
            return fmt.Errorf("error: unknown flag '%s'\n  did you mean '--%s'?\n  see: %s --help", token, suggestion, cmd.Use)
        }
    }
    return err
})
```

### Exit-code constants

```go
// internal/exitcode/exitcode.go
package exitcode

const (
    Success            = 0
    UserInputError     = 1
    SafetyBlock        = 2
    EnvironmentError   = 3
    TransientFailure   = 4
)

// In main:
if err != nil {
    fmt.Fprintln(os.Stderr, "error:", err)
    os.Exit(classifyError(err))
}
```

---

## Go + standard flag

For tools using only `flag` (no cobra):

```go
// main.go
fs := flag.NewFlagSet("mytool", flag.ContinueOnError)
jsonOutput := fs.Bool("json", false, "Emit JSON to stdout.")
robotMode := fs.Bool("robot", false, "Force machine-readable output.")
showCapabilities := fs.Bool("capabilities", false, "Print capabilities --json and exit.")
robotDocs := fs.Bool("robot-help", false, "Print agent handbook.")

fs.SetOutput(os.Stderr)

err := fs.Parse(os.Args[1:])
if err != nil {
    if errors.Is(err, flag.ErrHelp) { os.Exit(0) }
    // Standard flag's error message includes "flag provided but not defined: -X".
    if i := strings.Index(err.Error(), "flag provided but not defined: "); i != -1 {
        bad := strings.TrimPrefix(err.Error()[i:], "flag provided but not defined: ")
        if suggestion := ClosestKnownFlag(bad); suggestion != "" {
            fmt.Fprintf(os.Stderr, "error: unknown flag '%s'; did you mean '-%s'?\n", bad, suggestion)
        }
    }
    os.Exit(exitcode.UserInputError)
}

if *showCapabilities {
    fmt.Println(capabilities.MustJSON(version))
    os.Exit(0)
}
```

---

## Python + argparse

### Inventory hints

- Subcommand defs: `subparsers = parser.add_subparsers(...)`; `subparsers.add_parser(...)`
- Flag defs: `parser.add_argument('--json', ...)`
- Env-var bindings: `os.environ.get(...)` or via `default=os.environ.get(...)`
- Exit codes: `sys.exit(N)`; or `parser.exit(N, "msg")`
- Error literals: `parser.error("...")`

### Add `--json` to a verb

```python
# src/mytool/cmd/list.py
import json, sys
from .. import capabilities

def add_args(p):
    p.add_argument('-j', '--json', action='store_true',
                   help='Emit JSON to stdout. Logs go to stderr.')
    p.add_argument('--robot-meta', action='store_true',
                   help='Include parseability metadata (data_hash, search_mode).')

def run(args):
    items = load_items()
    if args.json:
        payload = {"ok": True, "items": [i.to_dict() for i in items]}
        if args.robot_meta:
            payload["meta"] = {
                "data_hash": data_hash(items),
                "search_mode": "lexical",
                "fallback_tier": None,
            }
        json.dump(payload, sys.stdout)
        sys.stdout.write("\n")
    else:
        for item in items:
            print(item.display())
```

### Global `--robot` and `--robot-help`

```python
# src/mytool/cli.py
import argparse, sys, os

def make_parser():
    p = argparse.ArgumentParser(prog='mytool', allow_abbrev=False)
    p.add_argument('--version', action='version', version=__version__)
    p.add_argument('--robot', action='store_true',
                   default=os.environ.get('MYTOOL_ROBOT') in ('1', 'true'),
                   help='Force machine-readable output for any verb.')
    p.add_argument('--robot-help', action='store_true',
                   help='Print agent handbook to stdout.')
    sub = p.add_subparsers(dest='cmd')
    list_cmd = sub.add_parser('list')
    cmd.list.add_args(list_cmd)
    # ...
    cap_cmd = sub.add_parser('capabilities')
    cap_cmd.add_argument('--json', action='store_true', default=True)
    return p

def main():
    parser = make_parser()
    args = parser.parse_args()
    if args.robot_help:
        sys.stdout.write(ROBOT_DOCS_GUIDE)
        return 0
    if args.robot and sys.stdout.isatty():
        print("note: --robot active; output will be machine-readable on stdout", file=sys.stderr)
    return dispatch(args)
```

### `capabilities --json`

```python
# src/mytool/capabilities.py
import json
from . import __version__

CONTRACT_VERSION = "1"

def build():
    return {
        "version": __version__,
        "contract_version": CONTRACT_VERSION,
        "features": ["json_output", "robot_meta", "levenshtein_typo_hint", "deterministic_output"],
        "commands": {
            "list":   {"description": "List items.",   "mutates": False, "json": True, "robot": "--json"},
            "add":    {"description": "Add an item.",  "mutates": True,  "json": True, "gates": ["--yes"]},
            "delete": {"description": "Remove item.",  "mutates": True,  "json": True, "gates": ["--yes", "--dry-run"]},
        },
        "exit_codes": {
            "0": "success",
            "1": "user-input-error",
            "2": "safety-block",
            "3": "tool-environment-error",
            "4": "transient-failure",
        },
        "env_vars": {
            "MYTOOL_HOME": {"description": "Config dir", "default": "$XDG_CONFIG_HOME/mytool"},
            "NO_COLOR":    {"description": "Honored", "default": "unset"},
            "CI":          {"description": "Honored", "default": "unset"},
        },
    }

def to_json():
    return json.dumps(build(), indent=2, sort_keys=False)
```

### argparse typo hint hook

```python
# src/mytool/typo_hint.py
import sys

KNOWN_FLAGS = [
    "json", "verbose", "quiet", "color", "no-color", "config", "yes", "dry-run",
    "robot", "robot-help", "version", "help",
]

def levenshtein_1(a, b):
    if abs(len(a) - len(b)) > 1: return False
    diffs = 0
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            i += 1; j += 1
        else:
            diffs += 1
            if diffs > 1: return False
            if   len(a) > len(b): i += 1
            elif len(a) < len(b): j += 1
            else: i += 1; j += 1
    return diffs + (len(a) - i) + (len(b) - j) == 1

def closest_known(s):
    s = s.lstrip('-')
    for k in KNOWN_FLAGS:
        if levenshtein_1(s, k): return k
    return None

class HintingArgParser(argparse.ArgumentParser):
    def error(self, message):
        # argparse format: "unrecognized arguments: --foo"
        if "unrecognized arguments:" in message:
            bad = message.split("unrecognized arguments:")[1].split()[0]
            if (s := closest_known(bad)):
                self.exit(1, f"error: unknown flag '{bad}'; did you mean '--{s}'?\nsee: {self.prog} --help\n")
        super().error(message)
```

---

## Python + click / typer

```python
# src/mytool/cli.py
import click, json, sys

@click.group()
@click.option('--robot', is_flag=True, envvar='MYTOOL_ROBOT')
@click.option('--robot-help', is_flag=True)
@click.version_option()
@click.pass_context
def cli(ctx, robot, robot_help):
    ctx.ensure_object(dict)
    ctx.obj['robot'] = robot
    if robot_help:
        click.echo(ROBOT_DOCS_GUIDE, nl=False)
        ctx.exit(0)

@cli.command()
@click.option('--json', 'json_output', is_flag=True)
@click.option('--robot-meta', is_flag=True)
@click.pass_context
def list(ctx, json_output, robot_meta):
    items = load_items()
    if json_output or ctx.obj.get('robot'):
        payload = {"ok": True, "items": [i.to_dict() for i in items]}
        if robot_meta:
            payload["meta"] = {"data_hash": data_hash(items), "search_mode": "lexical"}
        click.echo(json.dumps(payload))
    else:
        for item in items:
            click.echo(item.display())

@cli.command()
@click.option('--json', 'json_output', is_flag=True, default=True)
def capabilities(json_output):
    """Print capabilities JSON for agents."""
    from . import capabilities as cap
    click.echo(cap.to_json())
```

For typer, the equivalent is `app.callback()` for global flags and `@app.command()` per verb; the click pattern translates 1:1.

### Typer typo-hint via `result_callback`

Click/Typer don't expose unknown-flag errors as easily as argparse; the cleanest workaround is wrapping `cli()` invocation:

```python
def main():
    try:
        cli(standalone_mode=False)
    except click.exceptions.NoSuchOption as e:
        bad = e.option_name
        if (s := closest_known(bad)):
            click.echo(f"error: unknown flag '{bad}'; did you mean '--{s}'?", err=True)
            sys.exit(1)
        raise
    except click.exceptions.UsageError as e:
        click.echo(f"error: {e.message}", err=True)
        sys.exit(1)
```

---

## TypeScript + commander

```typescript
// src/cli.ts
import { Command, InvalidArgumentError } from 'commander';
import { capabilitiesJson, ROBOT_DOCS_GUIDE } from './capabilities';
import { closestKnownFlag } from './typoHint';

const program = new Command();

program
  .name('mytool')
  .version(VERSION)
  .option('--robot', 'Force machine-readable output for any verb.', !!process.env.MYTOOL_ROBOT)
  .option('--robot-help', 'Print agent handbook.')
  .hook('preAction', (thisCommand) => {
    if (thisCommand.opts().robotHelp) {
      process.stdout.write(ROBOT_DOCS_GUIDE);
      process.exit(0);
    }
    if (thisCommand.opts().robot && process.stdout.isTTY) {
      process.stderr.write("note: --robot active; output will be machine-readable on stdout\n");
    }
  });

program
  .command('list')
  .option('-j, --json', 'Emit JSON to stdout.')
  .option('--robot-meta', 'Include parseability metadata.')
  .action((opts) => {
    const items = loadItems();
    if (opts.json) {
      const payload: any = { ok: true, items };
      if (opts.robotMeta) {
        payload.meta = { data_hash: dataHash(items), search_mode: "lexical" };
      }
      process.stdout.write(JSON.stringify(payload) + "\n");
    } else {
      for (const item of items) console.log(item.display);
    }
  });

program
  .command('capabilities')
  .option('--json', '', true)
  .action(() => {
    process.stdout.write(capabilitiesJson() + "\n");
  });

// Override commander's default unknown-option handler
program.exitOverride();
try {
  program.parse(process.argv);
} catch (err: any) {
  if (err.code === 'commander.unknownOption') {
    const bad = err.message.match(/'([^']+)'/)?.[1];
    if (bad) {
      const s = closestKnownFlag(bad);
      if (s) {
        process.stderr.write(`error: unknown flag '${bad}'; did you mean '--${s}'?\n`);
        process.exit(1);
      }
    }
  }
  process.stderr.write(`error: ${err.message}\n`);
  process.exit(1);
}
```

---

## TypeScript + yargs

```typescript
import yargs from 'yargs';
import { hideBin } from 'yargs/helpers';

const argv = yargs(hideBin(process.argv))
  .scriptName('mytool')
  .option('robot',      { type: 'boolean', global: true })
  .option('robot-help', { type: 'boolean', global: true })
  .middleware((args) => {
    if (args['robot-help']) { process.stdout.write(ROBOT_DOCS_GUIDE); process.exit(0); }
  })
  .command('list', 'List items', (y) => y
    .option('json',        { type: 'boolean', alias: 'j' })
    .option('robot-meta',  { type: 'boolean' }),
    (a) => { /* ... */ })
  .command('capabilities', 'Print capabilities JSON', () => {}, () => {
    process.stdout.write(capabilitiesJson() + "\n");
  })
  .strict()
  .fail((msg, err, y) => {
    if (msg && msg.includes('Unknown argument')) {
      const bad = msg.match(/Unknown argument:\s*(\S+)/)?.[1];
      if (bad && (s = closestKnownFlag(bad))) {
        process.stderr.write(`error: unknown flag '${bad}'; did you mean '--${s}'?\n`);
        process.exit(1);
      }
    }
    process.stderr.write(`${msg || err.message}\n`);
    process.exit(1);
  })
  .parse();
```

---

## TypeScript + oclif

oclif has built-in JSON support via `--json` flag, which many tools enable per-command:

```typescript
// src/commands/list.ts
import { Command, Flags } from '@oclif/core';

export default class List extends Command {
  static description = 'List items';

  static enableJsonFlag = true;

  static flags = {
    'robot-meta': Flags.boolean({
      description: 'Include parseability metadata.',
      dependsOn: ['json'],
    }),
  };

  async run() {
    const { flags } = await this.parse(List);
    const items = await loadItems();
    if (flags['robot-meta']) {
      return { ok: true, items, meta: { data_hash: dataHash(items), search_mode: 'lexical' } };
    }
    return { ok: true, items };
  }
}
```

For `capabilities` as an oclif command, set `static enableJsonFlag = true` so `mytool capabilities --json` works idiomatically.

---

## Bash + getopts / hand-rolled

Bash CLIs often have the worst agent-ergonomic surface but are easy to fix because there's no framework abstraction:

```bash
#!/usr/bin/env bash
set -euo pipefail

VERSION="0.5.0"
JSON_OUTPUT=false
ROBOT_MODE=false
NO_COLOR_REQ=false

CAPABILITIES_JSON='{
  "version": "'"$VERSION"'",
  "contract_version": "1",
  "features": ["json_output", "deterministic_output"],
  "commands": {
    "list":   {"description": "List items.",   "mutates": false, "json": true},
    "add":    {"description": "Add an item.",  "mutates": true,  "json": true, "gates": ["--yes"]},
    "delete": {"description": "Remove item.",  "mutates": true,  "json": true, "gates": ["--yes", "--dry-run"]}
  },
  "exit_codes": {
    "0": "success",
    "1": "user-input-error",
    "2": "safety-block",
    "3": "tool-environment-error",
    "4": "transient-failure"
  },
  "env_vars": {
    "MYTOOL_HOME": {"description": "Config dir", "default": "$XDG_CONFIG_HOME/mytool"},
    "NO_COLOR":    {"description": "Honored",     "default": "unset"},
    "CI":          {"description": "Honored",     "default": "unset"}
  }
}'

ROBOT_DOCS_GUIDE='guide:
  Robot-mode handbook for mytool v'"$VERSION"'
  Output: --json (data on stdout); logs on stderr
  Exit codes: 0=success 1=user-input 2=safety-block 3=env 4=transient
  Mega-call: mytool doctor --json
  Quick refs: mytool capabilities --json | mytool --robot-help
'

KNOWN_FLAGS=(json verbose quiet color no-color config yes dry-run robot robot-help version help)

# Returns 0 if edit-distance between $1 and $2 is exactly 1 (substitution / insert / delete).
# Returns non-zero otherwise. Pure-bash; no external deps.
levenshtein_1() {
  local a="$1" b="$2"
  local la=${#a} lb=${#b}
  local diff=$(( la - lb ))
  # |la - lb| > 1 → distance > 1
  [ "${diff#-}" -gt 1 ] && return 1

  if [ "$la" -eq "$lb" ]; then
    # Same length: substitution. Count differing positions; bail on > 1.
    local d=0 i
    for (( i=0; i<la; i++ )); do
      if [ "${a:$i:1}" != "${b:$i:1}" ]; then
        d=$((d+1))
        [ "$d" -gt 1 ] && return 1
      fi
    done
    [ "$d" -eq 1 ]
  else
    # Different length by 1: one insertion (or deletion). Walk both, allowing one skip.
    local long short
    if [ "$la" -gt "$lb" ]; then long="$a"; short="$b"; else long="$b"; short="$a"; fi
    local i=0 j=0 skipped=0
    while [ "$i" -lt "${#long}" ] && [ "$j" -lt "${#short}" ]; do
      if [ "${long:$i:1}" = "${short:$j:1}" ]; then
        i=$((i+1)); j=$((j+1))
      else
        skipped=$((skipped+1))
        [ "$skipped" -gt 1 ] && return 1
        i=$((i+1))
      fi
    done
    return 0
  fi
}

closest_known_flag() {
  local s="${1#--}"; s="${s#-}"
  local k
  for k in "${KNOWN_FLAGS[@]}"; do
    if levenshtein_1 "$s" "$k"; then
      echo "$k"
      return
    fi
  done
}

usage() {
  cat <<EOF
Usage: mytool <verb> [args]
Verbs: list, add, delete, capabilities, robot-docs, doctor
Flags (global): --json, --robot, --robot-help, --version, --no-color
EXIT CODES: 0=success 1=user-input 2=safety-block 3=env 4=transient
AGENT/AUTOMATION: mytool capabilities --json | mytool --robot-help
EOF
}

# Honor NO_COLOR / CI / non-TTY
if [ -n "${NO_COLOR:-}" ] || [ "${TERM:-}" = "dumb" ] || [ -n "${CI:-}" ] || [ ! -t 1 ]; then
  NO_COLOR_REQ=true
fi

# Parse global flags first
while [ $# -gt 0 ]; do
  case "$1" in
    --json|-j)  JSON_OUTPUT=true; shift ;;
    --robot)    ROBOT_MODE=true; JSON_OUTPUT=true; shift ;;
    --robot-help) printf '%s' "$ROBOT_DOCS_GUIDE"; exit 0 ;;
    --version|-V) echo "$VERSION"; exit 0 ;;
    --help|-h|help) usage; exit 0 ;;
    --no-color) NO_COLOR_REQ=true; shift ;;
    --*|-*)
      sugg=$(closest_known_flag "$1" || true)
      if [ -n "$sugg" ]; then
        echo "error: unknown flag '$1'; did you mean '--$sugg'?" >&2
      else
        echo "error: unknown flag '$1'; see 'mytool --help'" >&2
      fi
      exit 1
      ;;
    *) break ;;
  esac
done

verb="${1:-}"
shift || true

case "$verb" in
  list)         cmd_list "$@" ;;
  add)          cmd_add "$@" ;;
  delete)       cmd_delete "$@" ;;
  capabilities) printf '%s\n' "$CAPABILITIES_JSON" ;;
  robot-docs)   printf '%s' "$ROBOT_DOCS_GUIDE" ;;
  doctor)       cmd_doctor "$@" ;;
  "")           usage ;;
  *)
    echo "error: unknown verb '$verb'; see 'mytool --help'" >&2
    exit 1
    ;;
esac
```

Tips for Bash CLIs:
- Always `set -euo pipefail`
- Use `printf '%s\n'` instead of `echo` (more predictable)
- Source the `KNOWN_FLAGS` array from a generated file shared with capabilities to keep them in sync
- For complex tools, consider a Python or Rust rewrite — Bash is harder to make agent-ergonomic at scale

---

## Ruby + thor

```ruby
# lib/mytool/cli.rb
require 'thor'
require 'json'

module Mytool
  class CLI < Thor
    class_option :json, type: :boolean, aliases: '-j'
    class_option :robot, type: :boolean
    class_option 'robot-help', type: :boolean
    class_option 'no-color', type: :boolean

    desc "list", "List all items"
    def list
      items = load_items
      if options[:json] || options[:robot]
        STDOUT.puts JSON.generate({ ok: true, items: items.map(&:to_h) })
      else
        items.each { |i| puts i.display }
      end
    end

    desc "capabilities", "Print capabilities JSON"
    def capabilities
      STDOUT.puts JSON.pretty_generate(Mytool::Capabilities.build)
    end

    no_commands do
      def invoke_command(command, *args)
        if options['robot-help']
          STDOUT.write Mytool::ROBOT_DOCS_GUIDE
          exit 0
        end
        super
      end
    end

    # Thor doesn't natively expose unknown-flag hints; subclass error:
    def self.handle_unknown_options?; true; end
  end
end
```

---

## Cross-cutting helpers

### Shared `KNOWN_FLAGS` list (generated to keep capabilities + typo-hint in sync)

Best practice: **generate** the `KNOWN_FLAGS` list and the `commands.<verb>.flags` field of capabilities from a single source of truth. Otherwise drift creeps in.

For Rust:
```rust
// build.rs (generates src/known_flags.rs from clap definitions at build time)
fn main() {
    use clap::CommandFactory;
    let cmd = MyApp::command();
    let mut flags = vec![];
    walk(&cmd, &mut flags);
    std::fs::write(
        format!("{}/known_flags.rs", std::env::var("OUT_DIR").unwrap()),
        format!("pub const KNOWN_FLAGS: &[&str] = &[{}];", flags.iter().map(|f| format!("\"{}\"", f)).collect::<Vec<_>>().join(",")),
    ).unwrap();
}
```

For Python: introspect argparse parser at startup.
For TypeScript: introspect yargs/commander config at startup.
For Go: cobra's `cmd.Flags().VisitAll(...)` walks all flags.
For Bash: hand-maintained, but with a comment cross-referencing capabilities JSON.

### Schema-pinning capabilities

Add a regression test that fails on any unintentional change:

```bash
# audit/regression_tests/capabilities-schema-pin.test.sh
got=$("$TOOL_BIN" capabilities --json | jq -S .)
want=$(cat audit/regression_tests/capabilities-golden.json | jq -S .)
diff <(echo "$got") <(echo "$want") && echo OK || {
  echo "REGRESSION: capabilities --json changed; if intentional, bump contract_version and regenerate golden." >&2
  exit 1
}
```

### Stable IDs (content-addressed)

```rust
fn surface_id(kind: &str, subtree: Option<&str>, name: &str) -> String {
    use sha2::{Digest, Sha256};
    let key = format!("{}|{}|{}", kind, subtree.unwrap_or(""), name);
    let mut h = Sha256::new(); h.update(key); 
    format!("{}__{}__{}", kind, subtree.unwrap_or("global"), &hex::encode(h.finalize())[..8])
}
```

### Reading `SOURCE_DATE_EPOCH` for reproducible timestamps

Already shown for Rust; equivalent Go:

```go
func now() time.Time {
    if s := os.Getenv("SOURCE_DATE_EPOCH"); s != "" {
        if t, err := strconv.ParseInt(s, 10, 64); err == nil {
            return time.Unix(t, 0)
        }
    }
    return time.Now()
}
```

Python:
```python
import os, time
def now():
    if (s := os.environ.get("SOURCE_DATE_EPOCH")):
        return float(s)
    return time.time()
```

### Quick-reject filter for hot-path safety hooks (dcg-style)

For tools like dcg that intercept every command and must be sub-millisecond:

```rust
// memchr-based pre-filter: 99%+ of inputs skip regex
use memchr::memmem;

const DANGER_TOKENS: &[&[u8]] = &[
    b"reset --hard", b"clean -fd", b"rm -rf", b"DROP", b"force-with-lease",
];

fn might_be_destructive(cmd: &[u8]) -> bool {
    DANGER_TOKENS.iter().any(|t| memmem::find(cmd, t).is_some())
}

fn is_destructive_full(cmd: &str) -> Option<&'static str> {
    if !might_be_destructive(cmd.as_bytes()) { return None; } // fast path
    // Slow path: full regex matching only on candidates
    REGEXES.iter().find_map(|r| r.captures(cmd).map(|_| r.name))
}
```

This pattern (cheap pre-filter + expensive full-check) is the canonical sub-millisecond hot-path shape. See `[Q-103]` in QUOTE-BANK.md.

---

## Pattern checklist (use during Phase 5 application)

- [ ] `--json` is on every read-side verb (verify with `capabilities --json | jq '.commands | to_entries | .[] | select(.value.mutates == false) | .value.json'`)
- [ ] Global `--robot` exists and switches to JSON
- [ ] `<tool> capabilities --json` returns the 6 required keys (version, contract_version, features, commands, exit_codes, env_vars)
- [ ] `<tool> robot-docs guide` returns < 80 lines of paste-ready handbook
- [ ] `--robot-help` works as alias to `robot-docs guide`
- [ ] `KNOWN_FLAGS` and capabilities `.commands.*.flags` are generated from one source
- [ ] Levenshtein-1 typo hint hooked into the framework's unknown-arg error
- [ ] NO_COLOR / CI / TERM=dumb / non-TTY honored
- [ ] Exit-code dictionary documented in `--help` AND in `capabilities`
- [ ] Mutating verbs require `--yes` AND offer `--dry-run`
- [ ] Errors name the safe alternative (don't just block)
- [ ] Output is sorted before serialization
- [ ] `SOURCE_DATE_EPOCH` honored
- [ ] `data_hash` field in `--robot-meta` mode for change detection
- [ ] At least one mega-command bundling 2+ slices with copy-paste-ready follow-ups
