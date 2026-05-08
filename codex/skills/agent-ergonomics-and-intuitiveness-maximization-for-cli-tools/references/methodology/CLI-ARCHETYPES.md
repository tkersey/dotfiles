# CLI-ARCHETYPES — Per-Archetype Defaults

Different CLIs have different "shapes" — and the agent-ergonomic Polish-Bar emphasis differs by shape. A search tool's bar is different from a build tool's, even though all 11 dimensions apply to both.

This file defines **archetypes**, their canonical-task patterns, the dimensions to weight extra, and the patterns to default-apply.

Archetypes covered:

1. [Search tool](#1-search-tool)
2. [Package manager](#2-package-manager)
3. [Build tool](#3-build-tool)
4. [Test runner](#4-test-runner)
5. [Git-flavored / SCM tool](#5-git-flavored--scm-tool)
6. [Daemon / server CLI](#6-daemon--server-cli)
7. [File-format converter](#7-file-format-converter)
8. [Scaffolder / generator](#8-scaffolder--generator)
9. [Hook tool / pre-commit guard](#9-hook-tool--pre-commit-guard)
10. [Issue tracker / task graph](#10-issue-tracker--task-graph)
11. [Authentication / credential tool](#11-authentication--credential-tool)
12. [Migration tool](#12-migration-tool)
13. [Diagnostic / observability CLI](#13-diagnostic--observability-cli)
14. [MCP server with companion CLI](#14-mcp-server-with-companion-cli)
15. [Multi-binary toolkit](#15-multi-binary-toolkit)

For each archetype:

- **Canonical tasks** an agent typically wants to perform
- **Dimension weights** (what matters extra)
- **Default mega-command shape** to add (per `MEGA-COMMAND-DESIGN.md`)
- **Anti-patterns common to this archetype**
- **Worked example** from the canonical exemplars

Phase 0 should classify the target CLI into one (or sometimes two) archetypes; Phase 4 prioritization uses the archetype-specific weights.

---

## 1. Search tool

**Examples.** ripgrep, ag, fd, fzf, frankensearch, cass.

**Canonical tasks.**
- "Find all files matching pattern X."
- "Search content for query, return top N results."
- "Search across multiple sources / corpora."
- "Stream results as they're found."

**Dimension weights.**
- `output_parseability`: 1.5× (results consumed by pipelines constantly)
- `intent_inference`: 1.3× (typo'd queries are common)
- `composability`: 1.5× (pipelines are the primary use)
- `determinism`: 1.2× (same query → same results)
- `safety_with_recovery`: 0.5× (read-only by definition)

**Default mega-command.** Search itself is the mega-command; ensure `<tool> search "<query>" --json --robot-meta` returns:
- `hits` array with file:line:col + snippet
- `meta.search_mode` (lexical / semantic / hybrid)
- `meta.fallback_tier`
- `meta.data_hash`
- `commands` field with paste-ready follow-ups (e.g. `<tool> view <path> -n <line>`)

**Archetype-specific patterns.**
- Always emit `file:line:col – content` format (parseable)
- `--limit N` AND `--cursor` for pagination
- Honor `NO_COLOR` rigorously (output goes to `xargs`/`vim` constantly)
- Empty result → `{"hits": [], "total": 0, "ok": true}` (not silent_fail)

**Anti-patterns.**
- TUI-only output (forces agents to scrape ANSI)
- Implicit ordering (must be sorted or insertion-order; document which)
- No way to disable per-query telemetry / completion suggestions

**Worked example: cass.** Already a top-tier search tool. Pattern 19 (`--robot` mandatory), Pattern 20 (stdout-data/stderr-diag), Pattern 23 (`--robot-meta`). 

---

## 2. Package manager

**Examples.** cargo, npm, pnpm, bun, pip, uv, gem, brew, apt.

**Canonical tasks.**
- "Install package X."
- "List installed packages."
- "Update all packages."
- "Remove package X."
- "Show transitive dependency tree."
- "Audit for security advisories."

**Dimension weights.**
- `safety_with_recovery`: 1.5× (mutations are the norm; `--dry-run` essential)
- `idempotency`: 1.5× (repeat installs should not duplicate)
- `output_parseability`: 1.3×
- `composability`: 1.3×

**Default mega-command.** `<tool> doctor --json` (Shape 2 — STATUS) returning:
- Installed package versions
- Security advisories
- Lockfile drift status
- `recommended_action` for each issue

**Archetype-specific patterns.**
- Lockfile is the source of truth; report drift
- Every `install` accepts `--dry-run` showing the resolution plan
- Every `update` shows the diff before applying
- `<tool> tree --json` for dependency introspection
- Package coordinates are stable handles (name + version + hash)

**Anti-patterns.**
- `npm install` modifying package.json silently (use `npm install --no-save` for read-side)
- Lockfile updates that aren't atomic
- Update commands that don't show the diff

**Worked example: cargo.** Has `cargo metadata --format-version=1` (capabilities-like), `cargo tree`, `cargo audit`. Could improve with `cargo --robot-doctor` mega-command.

---

## 3. Build tool

**Examples.** make, cargo build, go build, bazel, ninja, webpack, vite, turbopack.

**Canonical tasks.**
- "Build target X."
- "Show build plan / dependency graph."
- "Show why target X is being rebuilt."
- "Clear caches."
- "Run incremental build."

**Dimension weights.**
- `output_parseability`: 1.5× (errors must be machine-parseable for IDEs)
- `determinism`: 1.5× (reproducible builds matter)
- `intent_inference`: 1.2×
- `safety_with_recovery`: 1.0× (cache deletion can be costly)

**Default mega-command.** `<tool> plan --json` (Shape 3 — PLAN) returning:
- `tracks` of parallelizable units
- `cache_status` (hit/miss/expired) per target
- `commands` to invoke individual targets

**Archetype-specific patterns.**
- Errors emit `file:line:col – message` format ALL build tools should align on
- `--why <target>` explains rebuild triggers
- `--explain` shows the dependency graph
- `SOURCE_DATE_EPOCH` honored religiously

**Anti-patterns.**
- Random ordering of parallel job output (use `--parallel-output=ordered`)
- Cache invalidation that's not surfaced in `--explain`
- `clean` command without `--dry-run`

**Worked example: cargo build.** Already strong. `cargo build --message-format=json` is the canonical agent-friendly form.

---

## 4. Test runner

**Examples.** cargo test, pytest, jest, vitest, go test, mocha, rspec.

**Canonical tasks.**
- "Run all tests."
- "Run failing tests only."
- "Run test matching pattern."
- "Show why test X failed."
- "Run with coverage."

**Dimension weights.**
- `output_parseability`: 1.5× (test output consumed by IDEs / dashboards)
- `composability`: 1.5×
- `determinism`: 1.3× (flaky tests = bad determinism)

**Default mega-command.** `<tool> --robot-summary --json` returning:
- Pass/fail counts
- Failed test list with file:line + assertion
- Slowest tests (perf hint)
- Coverage summary if enabled
- `commands` to re-run failures

**Archetype-specific patterns.**
- JUnit XML for legacy CI compat AND `--json` for modern
- TAP output as fallback
- `--rerun-failed` operates on the previous run's failures
- Test IDs are stable across runs (allow tags)

**Anti-patterns.**
- Random test order without `--seed` to reproduce
- Output that interleaves stdout from multiple tests
- No way to scope to one test file

**Worked example: cargo nextest.** Excellent agent ergonomics; `--list --json`, `--failure-output`, etc.

---

## 5. Git-flavored / SCM tool

**Examples.** git, jj, hg, fossil, sapling, br (beads).

**Canonical tasks.**
- "Show current state."
- "Show changes."
- "Commit / record."
- "Branch / push / pull."

**Dimension weights.**
- `safety_with_recovery`: 1.7× (history is sacred; reflog matters)
- `intent_inference`: 1.3× (verb confusion across SCMs is constant)
- `composability`: 1.3×

**Default mega-command.** `<tool> status --json` returning:
- Branch / current state
- Untracked / modified / staged
- Sync status with remote
- Recent ops
- `recommended_action` (e.g. "12 commits ahead; consider push")

**Archetype-specific patterns.**
- Every destructive op (`reset --hard`, `clean -fd`) requires `--yes` + names alts
- Every history-rewriting op writes to reflog before mutating
- Aliases for verbs from sibling tools (e.g. jj users typing `git` should get hint)
- Idempotent verbs (re-pushing same commits is a no-op)

**Anti-patterns.**
- Commands that bypass safety nets (`git push --force` without lease)
- Verbs that delete branches without confirmation
- Detached-HEAD / orphaned-commit scenarios without warning

**Worked example: br (beads).** Per AGENTS.md, `br` is non-invasive (never runs git commands). `br ready` is the mega-command. Could add `br --robot-doctor` showing graph health.

---

## 6. Daemon / server CLI

**Examples.** dockerd, kubectl, redis-cli, postgres CLI, traefik, caddy.

**Canonical tasks.**
- "Start / stop / restart daemon."
- "Connect to running daemon."
- "Query daemon state."
- "Send admin command."

**Dimension weights.**
- `safety_with_recovery`: 1.5×
- `composability`: 1.3×
- `error_pedagogy`: 1.5× (connection errors must teach)
- `output_parseability`: 1.3×

**Default mega-command.** `<tool> health --json` (Shape 2) returning:
- Daemon connection state
- Active sessions / connections
- Resource usage
- `recommended_action` if any component is degraded

**Archetype-specific patterns.**
- Connection errors name socket / port / config
- Daemon restart requires `--yes` AND `--graceful` option
- Active-session list before restart
- `--admin` flag gating destructive ops

**Anti-patterns.**
- Connection error: "connection refused" without naming socket / config / steps to start daemon
- `kill -9` style restart (no graceful drain)
- Mutating state without confirmation in admin mode

---

## 7. File-format converter

**Examples.** jq, yq, pandoc, ffmpeg, imagemagick, csctf.

**Canonical tasks.**
- "Convert file from X to Y."
- "Validate file conforms to schema."
- "Extract a slice."

**Dimension weights.**
- `output_parseability`: 1.5×
- `composability`: 1.7× (pipes are the primary use)
- `determinism`: 1.5× (same input → same output)

**Default mega-command.** Less applicable; converters are usually single-purpose. But `<tool> --validate --json` for schema introspection is high-value.

**Archetype-specific patterns.**
- Stdin → stdout pipe is the default; explicit input/output flags are alternatives
- Streaming mode where possible (don't buffer the whole file)
- Always emit JSON parsing errors with file:line:col
- `--strict` for fail-on-warning

**Anti-patterns.**
- Buffering huge files in memory when streaming would work
- Tool that reads stdin when stdin is a TTY (block forever)

**Worked example: jq.** Top-tier; the gold standard for JSON converters.

---

## 8. Scaffolder / generator

**Examples.** create-react-app, cargo-generate, yo, plop, copier.

**Canonical tasks.**
- "Generate a new project from template."
- "Add a new component / module to existing project."
- "List available templates."

**Dimension weights.**
- `intent_inference`: 1.3× (template-name typos common)
- `safety_with_recovery`: 1.5× (writes many files at once)
- `determinism`: 1.3× (reproducible scaffolds)

**Default mega-command.** `<tool> templates --json` listing all templates with descriptions, then `<tool> generate <template> --dry-run --json` previews the file set.

**Archetype-specific patterns.**
- `--dry-run` lists files-to-be-written WITHOUT creating them
- Templates are versioned (template@version syntax)
- `<tool> diff` shows existing-vs-template differences for upgrades
- Generated files include a marker (comment) tying them to the template version

**Anti-patterns.**
- Overwriting existing files without confirmation
- Generating to cwd implicitly (use explicit target dir)
- No way to preview without running

---

## 9. Hook tool / pre-commit guard

**Examples.** dcg, husky hooks, pre-commit framework, lefthook.

**Canonical tasks.**
- "Should this command be allowed?"
- "What rules are active?"
- "Explain why a command was blocked."

**Dimension weights.**
- `intuitiveness`: 1.5× (called every command; can't be confusing)
- `agent_ergonomics`: 1.5× (sub-millisecond required)
- `error_pedagogy`: 1.7× (block messages MUST teach)
- `safety_with_recovery`: 1.7×

**Default mega-command.** `<tool> explain <cmd> --json` showing:
- Block / allow decision
- Matched rules
- Suggested alternatives (if blocked)
- Pack / config that gave the verdict

**Archetype-specific patterns.**
- Sub-millisecond hot path (memchr-style quick reject)
- Stdin = command to check; stdout = JSON verdict; stderr = diagnostics
- Per-agent compat (Codex stderr+exit2; Claude Code stdout JSON)
- Allowlist file for explicit overrides

**Anti-patterns.**
- Block messages without naming the safe alternative (this is the canonical anti-pattern; see `[Q-300]`)
- Telemetry / network calls in hot path
- Block decisions that aren't reproducible

**Worked example: dcg.** Pattern anchor for this archetype. See WORKED-EXAMPLES.md.

---

## 10. Issue tracker / task graph

**Examples.** br (beads), bv, jira CLI, linear CLI, gh issues.

**Canonical tasks.**
- "Find next ready item."
- "Show item details + dependencies."
- "Claim an item."
- "Show project graph health."

**Dimension weights.**
- `agent_ergonomics`: 1.5× (mega-commands are huge here)
- `output_parseability`: 1.3×
- `determinism`: 1.3× (graph metrics need stable hashing)

**Default mega-command.** `<tool> --robot-triage --json` (Shape 1 — TRIAGE). The exemplar.

**Archetype-specific patterns.**
- Stable handles (`X-001` not session-IDs)
- Graph metrics (PageRank, betweenness, critical path)
- Two-phase latency (instant + async)
- `data_hash` field for change detection
- Cross-references to plan / health / next mega-commands

**Anti-patterns.**
- Hashmap-iteration order (non-deterministic)
- Recommendations without `commands` field
- "Your turn" notifications via TUI only (no `--json` form)

**Worked example: bv.** Pattern anchor for this archetype.

---

## 11. Authentication / credential tool

**Examples.** gh auth, aws configure, gcloud auth, op (1Password CLI), caam.

**Canonical tasks.**
- "Login to service X."
- "Show current identity."
- "List configured profiles / accounts."
- "Switch to profile X."

**Dimension weights.**
- `safety_with_recovery`: 1.7× (credentials are sensitive)
- `intent_inference`: 1.3×
- `error_pedagogy`: 1.5× (auth failures must explain)

**Default mega-command.** `<tool> whoami --json` returning:
- Current identity / profile
- Available accounts
- Token expiry
- Scopes / permissions
- `recommended_action` if any creds need refresh

**Archetype-specific patterns.**
- Never log credentials to stdout / files
- `--token-file` accepts piped input
- Profile names are stable handles
- Tokens have expiry; surface in capabilities
- `--no-prompt` mode for CI / automation

**Anti-patterns.**
- Browser-based OAuth without `--device-code` fallback
- Storing credentials in plain text
- Auth errors that don't say "your token expired; run X to refresh"

**Worked example: caam.** Sub-100ms account switching; non-OAuth fast path.

---

## 12. Migration tool

**Examples.** sqlx migrate, sea-orm-cli migrate, rails db:migrate, alembic, flyway.

**Canonical tasks.**
- "Apply pending migrations."
- "Rollback N migrations."
- "Show migration status."
- "Generate a new migration."

**Dimension weights.**
- `safety_with_recovery`: 1.7× (migrations are irreversible)
- `idempotency`: 1.5× (re-runs must be safe)
- `error_pedagogy`: 1.5×

**Default mega-command.** `<tool> status --json` showing:
- Applied / pending migrations
- Each migration's checksum (drift detection)
- `recommended_action` (e.g. "schema drift detected on migration 0042")

**Archetype-specific patterns.**
- Every `apply` accepts `--dry-run` showing SQL
- Every `rollback` accepts `--dry-run`
- Locks / advisory locks during apply
- Checksum every migration; refuse to apply if checksum changed since last apply

**Anti-patterns.**
- Applying migrations without dry-run option
- Rollback without confirmation
- Schema changes not gated by `--yes`

---

## 13. Diagnostic / observability CLI

**Examples.** strace, gdb, htop, lsof, rch, ntm.

**Canonical tasks.**
- "Show system / process state."
- "Watch a metric over time."
- "Inspect process X."
- "Trace syscalls."

**Dimension weights.**
- `output_parseability`: 1.5×
- `composability`: 1.7×
- `agent_ergonomics`: 1.3× (mega-commands very useful)

**Default mega-command.** `<tool> snapshot --json` showing the canonical state.

**Archetype-specific patterns.**
- Read-only by default (no mutating ops)
- Streaming output for `watch`-mode
- `--once` for snapshot vs continuous
- Stable record format (one event per JSONL line for streams)

**Anti-patterns.**
- Frame-redrawing TUI without `--once` flag for agents
- Diagnostic output that mixes log + data on stdout
- Records that aren't deterministic across runs (mod timestamps in known fields)

**Worked example: ntm.** Robot mode + json + capabilities. Strong agent ergonomics.

---

## 14. MCP server with companion CLI

**Examples.** am (mcp_agent_mail), mcp-server-* family.

**Canonical tasks.**
- "Reserve files."
- "Send / receive messages."
- "Manage identity."
- "Coordinate with other agents."

**Dimension weights.** All apply, with extra:
- `agent_ergonomics`: 1.7× (MCP IS the agent surface)
- `composability`: 1.3× (CLI for debugging / integration tests)

**Default mega-command.** Two: `<tool> capabilities --json` for MCP tool catalog AND `<tool> doctor --json` for server health.

**Archetype-specific patterns.**
- Macros vs granular tools (Pattern 11)
- Stable handles for projects, agents, threads
- Idempotent registration
- File reservations as advisory leases (not locks)
- Per-tool documentation in MCP `tools/list` response

**Anti-patterns.**
- Verbose CLI with no `--json` mode (parity gap with MCP)
- Capability differences between MCP and CLI surfaces
- Identity / registration friction not collapsed into a macro

**Worked example: am.** Pattern anchor; macros + project_key + advisory reservations.

For MCP-specific dimension scoring, see `MCP-SERVER-AUDIT.md`.

---

## 15. Multi-binary toolkit

**Examples.** cargo + cargo-audit + cargo-deny + cargo-machete; AWS CLI v2 + AWS SAM + AWS CDK; rustup + rustc + cargo + clippy.

**Canonical tasks.** Cross-binary canonical tasks where output of one binary is input to another.

**Dimension weights.**
- `composability`: 1.7×
- `output_parseability`: 1.5×
- `consistency` across binaries: 1.5× (a meta-dimension; same envelope, same exit codes)

**Default mega-command.** A wrapper / orchestrator binary OR a well-defined IPC schema:
- `<rootcli> --robot-overview --json` covering all sub-tools
- Or: each tool emits `{contract_version: "1"}` so cross-references are version-aware

**Archetype-specific patterns.**
- Shared exit-code dictionary across all binaries
- Shared envelope across `--json` outputs
- Cross-binary discoverability (`cargo` mentions `cargo audit` in `--help`)
- Single `capabilities --json` covers the whole family OR per-binary capabilities cross-reference each other

**Anti-patterns.**
- Binary A uses exit 1 for "no results" while binary B uses exit 1 for "user-input-error"
- Different envelope per binary (one wraps, one doesn't)
- Sibling binaries that don't know about each other in `--help`

**Audit approach.** Score each binary individually, then add a cross-cutting meta-dimension `consistency` that's high if envelope/exit-codes/conventions are aligned. See `MULTI-TOOL-FAMILY-AUDIT.md`.

---

## How to use archetypes in Phase 0

1. **Detect** the archetype during `discover-cli.sh` based on file patterns and binary behavior:
   - `cargo metadata`, `package.json` with `bin` → package manager
   - `Makefile`, `build.rs` → build tool
   - `tests/` directory + `*.test.{ext}` → test runner
   - `.git`, history-mutating verbs → SCM tool
   - `mcp.json` / MCP imports → MCP server
   - And so on

2. **Apply** the archetype's dimension weights to the rubric for this audit.

3. **Default-include** the archetype's mega-command shape in Phase 4 recommendations if missing.

4. **Use** the archetype's canonical-task list to seed the Phase 9 simulator (or augment user-provided tasks).

5. **Cross-check** against the archetype's anti-patterns during Phase 2 scoring.

If a tool spans two archetypes (e.g. `bv` is both a triage tool AND a daemon-flavored TUI), pick the dominant one and note the secondary in `phase0_scope_decision.md`. Apply both archetypes' weights additively (cap weight at 2.0×).

---

## Adding a new archetype

If the audit target doesn't fit any of the 15 archetypes:

1. Document the new archetype in this file (append at the bottom).
2. Define canonical tasks, dimension weights, default mega-command, anti-patterns.
3. Bump `rubric_version` in the manifest if dimension weights change anything materially.
4. The HANDOFF.md notes the new archetype for future passes.

The list is meant to grow.
