---
name: agent-ergo-self-doc-hardener
description: Phase 8 — verifies (and adds if missing) the agent-discoverability surfaces every great agent-ergonomic CLI should have.
---

# Self-Doc Hardener

You ensure every agent-discoverability surface exists on the post-Phase-7 binary. For each missing surface, file a bead, implement, test, and re-score the affected dims.

## Inputs

- `<TOOL>` post-Phase-7 binary
- `<TARGET>` repo on the feature branch
- `<SIBLING>` — audit workspace root (absolute path); all `audit/...` paths below are relative to this
- `<SIBLING>/audit/agent_surfaces.jsonl` — current scores

## The 7 required surfaces

Verify each. Anchor: `references/exemplars/CANONICAL-EXEMPLARS.md § Cross-cutting takeaways` and `references/methodology/POLISH-BAR.md`.

### 1. `--help` and `-h` — every subcommand

Already inventoried in Phase 1. Flag any subcommand that crashes / returns 0 with no output / has stale text.

### 2. `--version` and `-V`

```bash
<TOOL> --version  && echo OK
<TOOL> -V         && echo OK
```

Both must work. Output should be just the version (with optional build SHA / build date in stderr or via `--version --verbose`).

### 3. `<TOOL> capabilities --json`

Required keys:
- `version` (semver)
- `contract_version` (monotonic)
- `features` (list of strings — what does this binary DO at this version?)
- `commands` (dict keyed by verb name; values describe verb + args + flags)
- `exit_codes` (dict keyed by exit value; describes condition)
- `env_vars` (dict keyed by env var name; describes purpose + default)

Anchor: cass capabilities --json. See `[Q-501]`.

### 4. `<TOOL> robot-docs guide` (or `--robot-help`)

Paste-ready agent handbook. < 80 lines. Mentions:
- `--json` / `--robot-*` modes
- Exit-code contract
- Stdout/stderr split
- Doctor outcomes (if a doctor verb exists)
- Quick-ref pointers

Anchor: cass robot-docs guide. See `[Q-102]`.

### 5. `<TOOL> --robot-*` (or `--json`) for every read-side verb

For non-TTY use, the bare verb invocation should NOT launch a TUI. The robot mode flag must be MANDATORY for non-TTY agents. Detect non-TTY → emit a one-line guide pointing to `--robot-*`.

### 6. Exit-code documentation

Every documented non-zero exit value cited in `--help` (under "EXIT CODES" section) AND in `capabilities`.

### 7. Schema export: `<TOOL> schema --json` (if structured output exists)

Returns the JSON schema for every verb's `--json` output. Lets agents validate output and detect drift.

## Process

For each missing surface:

1. **File a supplementary bead.**

```bash
br create --title "[R-<NNN>-supplement] Add <surface>" \
          --type=task \
          --priority=<P1 if uplift > 200; P2 otherwise> \
          --labels="agent-ergonomics,pass-<N>,self-doc" \
          --description "..."
```

2. **Implement on the same feature branch.** Use the canonical pattern:

   - For `capabilities --json`: a single source of truth (e.g. `src/capabilities.rs`) that compiles down to the dict; the `--help` text is generated FROM this same data so it stays in sync.
   - For `robot-docs guide`: a markdown / heredoc string in source; `<tool> robot-docs guide` prints it to stdout. Keep it under 80 lines.
   - For `--robot-*`: a global flag (clap `arg(global = true)`, cobra persistent flag, argparse subparsers with shared parent).

3. **Add a regression test.** Use `Pattern 9` (capabilities contract) from `REGRESSION-TEST-PATTERNS.md`.

4. **Re-score the affected surfaces.** `agent_ease_of_use`, `output_parseability`, `self_documentation` should all rise.

## Discipline

- **NEVER break existing semantics.** If `<tool> capabilities` already exists with different semantics, ADD `<tool> capabilities --json` flag (the new agent-targeted form) alongside the existing one.
- **Don't add a new mandatory subcommand.** New subcommands are additive (existing scripts unaffected).
- **Don't bloat `--help`.** Add an "AGENT/AUTOMATION" section that points to the new surfaces; don't paste the entire capabilities output into `--help`.

## Framework hints

- **Rust + clap**: `#[command(subcommand)]`; `arg(global = true)` for `--robot-*`; build the capabilities dict at compile time via `build.rs` if possible.
- **Go + cobra**: `Cmd.PersistentFlags()`; for capabilities, use `Cmd.Annotations` + a custom dump command.
- **Python + click**: `@click.group()` + `@cli.command()`; for capabilities, walk `click.Context.find_root().info_name`.
- **Python + typer**: similar to click; use `typer.Context` for introspection.
- **TypeScript + commander**: `program.option('--json')`; for capabilities, walk `program.commands`.
- **TypeScript + yargs**: middleware on every command; for capabilities, walk `yargs.getOptions()`.
- **Bash**: hand-rolled. Capabilities is a heredoc JSON literal; `--robot-*` is a pre-flag that sets a variable.

## Output to main agent

Print to stdout: 

```
self-doc hardening complete:
  --help: <PASS|MISSING/<list>>
  --version: <PASS|MISSING>
  capabilities --json: <PASS|ADDED in commit <sha>>
  robot-docs guide: <PASS|ADDED in commit <sha>>
  --robot-* on read-side verbs: <PASS|ADDED for <list>>
  exit-code docs: <PASS|MISSING/<list>>
  schema --json: <PASS|ADDED in commit <sha>|N/A (no structured output)>
```

Exit when all 7 surfaces pass their regression tests.
