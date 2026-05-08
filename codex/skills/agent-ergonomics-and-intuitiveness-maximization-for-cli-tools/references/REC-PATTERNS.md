# REC-PATTERNS.md — Pre-built recommendation patterns library

When the recommender subagent is drafting a fix, it doesn't need to derive each common pattern from scratch. This file is the catalog: for the most-frequent rec types across past audits, here's the trigger condition, code template per language, expected uplift, regression-test template, and common pitfalls.

**How to use this from `subagents/recommender.md`**: before drafting a novel diff_sketch, scan this file for a matching pattern. If one matches, copy its template, adapt to the target's source style, and reference the pattern by name in `operators_applied`. Patterns are battle-tested; novel diff_sketches should be rare.

---

## Pattern-1: Levenshtein-1 typo correction for unknown flags

**Trigger.** `intent_inference < 600` AND the `intent_inference_corpus.jsonl` shows multiple `category=A` typos classified as `useless_error` against this surface (the tool errored "unknown option" without suggesting the right one).

**Expected uplift.**
- `intent_inference`: +200 to +400 (this is the headline gain)
- `error_pedagogy`: +100 to +200
- `agent_intuitiveness`: +50 to +100

**Code template — Rust + clap (with kebab-case flag names):**
```rust
fn handle_unknown_flag(flag: &str, known: &[&str]) -> Error {
    if let Some(close) = known.iter().min_by_key(|k| levenshtein(flag, k))
        .filter(|k| levenshtein(flag, k) == 1) {
        eprintln!("error: unknown flag '--{}'; did you mean '--{}'?", flag, close);
        return Error::UnknownFlagDidYouMean { typed: flag.into(), suggested: close.to_string() };
    }
    eprintln!("error: unknown flag '--{}'", flag);
    Error::UnknownFlag(flag.into())
}
```

**Code template — Go + cobra:**
```go
// In root command's PersistentPreRunE or the global error hook:
cmd.SetFlagErrorFunc(func(cmd *cobra.Command, err error) error {
    var unknownFlagErr *pflag.UnknownFlagError
    if errors.As(err, &unknownFlagErr) {
        if suggestion := closestKnownFlag(unknownFlagErr.Flag, knownFlagsFor(cmd), 1); suggestion != "" {
            return fmt.Errorf("unknown flag '--%s'; did you mean '--%s'?", unknownFlagErr.Flag, suggestion)
        }
    }
    return err
})
```

**Code template — Python + click:**
```python
class TypoCorrectingGroup(click.Group):
    def parse_args(self, ctx, args):
        try:
            return super().parse_args(ctx, args)
        except click.NoSuchOption as e:
            close = closest_known(e.option_name, self.params_known, max_dist=1)
            if close:
                ctx.fail(f"unknown flag {e.option_name!r}; did you mean {close!r}?")
            raise
```

**Regression test template (`audit/regression_tests/R-NNN__typo_correction.test.sh`):**
```bash
#!/bin/bash
set -euo pipefail
out=$("$TOOL" --jsno 2>&1 || true)
echo "$out" | grep -q "did you mean '--json'" || { echo "FAIL: no typo hint"; exit 1; }
echo "PASS: typo correction works"
```

**Common pitfalls.**
- Don't suggest at distance > 1; rate of false-positives explodes (the agent already typed clearly-wrong things and gets bad suggestions).
- Build the known-flag list AT BUILD TIME from clap/cobra metadata — don't hardcode. `scripts/extract-known-flags.sh` produces the same list for testing.
- Keep the original error path (still exit non-zero, still write to stderr). The hint is ADDITIVE, not a replacement.

---

## Pattern-2: Add `--json` mode preserving human default

**Trigger.** `output_parseability < 500` AND the surface produces structured-ish output (lists, tables, key/value pairs) that an agent would want to consume programmatically.

**Expected uplift.**
- `output_parseability`: +200 to +400
- `composability`: +100 to +200
- `determinism_and_reproducibility`: +50 to +150

**Code template — Rust + clap:**
```rust
#[derive(Args)]
struct OutputArgs {
    /// Emit JSON-Lines instead of human-readable text. Stable schema: see `<tool> --json --schema`.
    #[arg(long, global = true)]
    json: bool,
}

fn render(items: &[Item], out: &OutputArgs, w: &mut impl Write) {
    if out.json {
        for item in items {
            writeln!(w, "{}", serde_json::to_string(item).unwrap()).unwrap();
        }
    } else {
        // Existing human renderer, unchanged.
        render_table(items, w);
    }
}
```

**Code template — Go + cobra:**
```go
var jsonOutput bool

func init() {
    rootCmd.PersistentFlags().BoolVar(&jsonOutput, "json", false, "Emit JSON-Lines instead of human text")
}

func renderItems(items []Item, w io.Writer) error {
    if jsonOutput {
        enc := json.NewEncoder(w)
        for _, item := range items { enc.Encode(item) }
        return nil
    }
    return renderTable(items, w)
}
```

**Code template — Python + click:**
```python
@click.option('--json', 'as_json', is_flag=True, help='Emit JSON-Lines.')
def list_items(as_json: bool):
    items = fetch_items()
    if as_json:
        for item in items:
            click.echo(json.dumps(asdict(item)))
    else:
        render_table(items)
```

**Regression test template:**
```bash
#!/bin/bash
set -euo pipefail
"$TOOL" list --json | head -1 | jq -e . >/dev/null  # parses as JSON
"$TOOL" list | grep -qE '\b[A-Z]+\b' || true        # human still works (non-JSON tokens)
```

**Common pitfalls.**
- Don't break stdin/stdout discipline. `--json` should write to stdout; logs/errors stay on stderr.
- Schema must be STABLE. Document with `--json --schema` returning the JSON Schema. Bumping the shape is a breaking change; add `--json-schema-version=1` opt-in for v2.
- For commands that print multiple records, use JSON-Lines (one record per line), not a single JSON array. Streaming-friendly.
- Honor `--json` in error paths too: errors should be JSON `{"error": "...", "code": <N>}` when the flag is set, not human text.

---

## Pattern-3: Honor NO_COLOR / TERM=dumb / CI=true

**Trigger.** `non_tty_discipline` low (heatmap shows red on `output_parseability` for any colorized surface) AND `verify-non-tty-discipline.sh` reports ANSI escape codes leaking when stdin is closed.

**Expected uplift.**
- `agent_ergonomics`: +100 to +200
- `output_parseability`: +50 to +150
- `composability`: +50 to +100

**Code template — Rust:**
```rust
fn use_color() -> bool {
    if std::env::var("NO_COLOR").is_ok() { return false; }
    if std::env::var("TERM").as_deref() == Ok("dumb") { return false; }
    if std::env::var("CI").is_ok() { return false; }
    atty::is(atty::Stream::Stdout)
}
```

**Code template — Go:**
```go
import "github.com/mattn/go-isatty"

func useColor() bool {
    if os.Getenv("NO_COLOR") != "" { return false }
    if os.Getenv("TERM") == "dumb" { return false }
    if os.Getenv("CI") != "" { return false }
    return isatty.IsTerminal(os.Stdout.Fd())
}
```

**Common pitfalls.**
- `NO_COLOR=` (empty value) — per the standard, ANY value (including empty) of NO_COLOR means "no color." Test `is_set`, not the value.
- Don't forget stderr — error messages with ANSI codes break `2>&1 | jq`.
- The `--color=auto|always|never` flag (where `auto` uses these env checks) is the ergonomic addition; users expect it.

---

## Pattern-4: Add `--robot-mode` capability surface

**Trigger.** `agent_intuitiveness` low across many surfaces; agent has no programmatic way to discover available verbs/flags from the binary itself; user wants the tool to be self-describing for future audit passes (or for other agents).

**Expected uplift.**
- `self_documentation`: +200 to +400
- `agent_intuitiveness`: +100 to +200
- `agent_ergonomics`: +100 to +150

**Code template — Rust + clap:**
```rust
#[derive(Subcommand)]
enum Cmd {
    /// Print machine-readable capabilities — verbs, flags, env vars, exit codes — as JSON.
    #[command(name = "capabilities")]
    Capabilities {
        /// Output format
        #[arg(long, default_value = "json")] format: String,
    },
    // ... other commands
}

fn capabilities() -> serde_json::Value {
    serde_json::json!({
        "schema_version": "1.0",
        "verbs": collect_verbs(),
        "flags": collect_flags(),
        "env_vars": collect_env_vars(),
        "exit_codes": collect_exit_codes(),
    })
}
```

**Code template — Python + click:** add `mytool capabilities --format=json` that introspects the click command tree and emits the same shape.

**Regression test template:**
```bash
"$TOOL" capabilities --format=json | jq -e '.schema_version, .verbs, .flags, .env_vars, .exit_codes' >/dev/null
```

**Common pitfalls.**
- Don't hand-curate the capabilities output; introspect from the actual command tree. Otherwise it drifts.
- Emit JSON-Lines or a single object — pick one and stick with it; don't switch shapes between releases.
- Include exit codes' SEMANTIC meaning, not just the integer ("0=success, 1=user error, 2=system error, 3=auth required").

---

## Pattern-5: Two-pass deprecation (alias-only flag)

**Trigger.** Audit recommends renaming a flag (e.g. `--colour` → `--color` for US-English consistency) but breaking the old name would punish existing users.

**Expected uplift.**
- `regression_resistance`: +100 (preserves backward-compat)
- `agent_ergonomics`: +50 (consistency)

**Process (one rec per pass):**

**Pass-N.s1 (Stage 1 — Both names work, old aliases new):**
- Define both flags; old delegates to new.
- Print a deprecation note ON STDERR (not stdout — non-breaking) when old is used:
  `warning: '--colour' is deprecated; use '--color' instead. The old form will be removed in 2.0.`

**Pass-N.s2 (Stage 2 — old still works but emits stronger warning, after one release cycle):**
- Same code; warning escalates to "DEPRECATED: removal scheduled for 2.0 (next release)."

**Pass-N.s3 (Stage 3 — old removed, after a major version bump):**
- Delete old name.
- Update README + changelog.

**Code template — Rust + clap:**
```rust
#[arg(long = "color", alias = "colour")]
color: ColorMode,

// Detect if the alias was used (clap doesn't expose this directly):
fn detect_aliased(args: &[String]) -> Option<&str> {
    for arg in args {
        if arg.starts_with("--colour") {
            return Some("--colour → --color");
        }
    }
    None
}
```

Use `subagents/migration-planner.md` to sequence the stages across passes; per-stage rec gets its own R-NNN.s<N> id.

---

## Pattern-6: Stable structured error output

**Trigger.** `error_pedagogy < 500` — errors are unstructured prose, hard for agents to parse and react.

**Expected uplift.**
- `error_pedagogy`: +200 to +400
- `output_parseability`: +100

**Code template — JSON-Lines errors when `--json` is set:**
```rust
fn emit_error(err: &Error, json_mode: bool) {
    if json_mode {
        let payload = serde_json::json!({
            "error": err.message(),
            "code": err.numeric_code(),
            "kind": err.kind(),  // "user_input" | "auth" | "network" | "system"
            "remediation": err.suggested_fix(),
            "docs_url": err.docs_url(),
        });
        eprintln!("{}", serde_json::to_string(&payload).unwrap());
    } else {
        eprintln!("error: {}", err.message());
        if let Some(fix) = err.suggested_fix() {
            eprintln!("  → {}", fix);
        }
    }
}
```

**Common pitfalls.**
- The error code is part of the API; once shipped, don't change its meaning.
- Include `docs_url` even for errors that are "obviously self-explanatory" — agents triage by URL pattern, not message text.

---

## How to add a new pattern

When a recommender produces a rec that doesn't match any existing pattern AND it's a shape that's likely to recur (3+ similar surfaces in the same audit, or known to recur across CLIs):

1. After Phase 4 completes, distill the rec into the format above (trigger / uplift / templates / pitfalls).
2. Append to this file under a new Pattern-N heading.
3. Future Phase-4 recommenders will find it and reuse it.

This is how the library gets richer audit-by-audit without manual curation.
