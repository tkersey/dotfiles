# CANONICAL-TASK-LIBRARY — Pre-built tasks per archetype

Phase 9 simulators need a list of canonical tasks the CLI is documented to support. This file ships pre-built lists per archetype (per `CLI-ARCHETYPES.md`). Phase 0 picks the archetype; Phase 9 spawns simulators with the relevant task list.

A **canonical task** is something the agent should be able to complete using only `<tool> --help`, `<tool> capabilities --json`, `<tool> robot-docs guide`, and the documented surfaces. No README required.

---

## Format

Each task follows `assets/canonical-task-template.md`:

```markdown
## Task NN: <slug>

**Statement.** <user-facing description>
**Tags.** <read-only|mutating|pipe-friendly|multi-step|requires-config|...>
**Expected outcome.** <exit code, stdout shape, side effects>
**Documented in.** <where the tool surfaces this>
**Pre-pass round-trips estimate.** <K>
**Post-pass target.** <K-1 or K>
```

When customizing per-tool: copy the archetype's tasks, swap `<tool>` for the actual binary name, adjust task wording for the tool's domain (e.g. for an issue tracker, "items" → "issues"), and add tool-specific tasks.

---

## Search tool tasks (e.g. ripgrep, fd, fzf, cass, frankensearch)

### Task 01: search-content-basic
**Statement.** Search a project for files matching pattern "TODO". Print results as `file:line:content`.
**Tags.** read-only, pipe-friendly
**Expected outcome.** exit 0 if matches, exit 1 if no matches (consistent with grep convention); stdout has one line per match.
**Round-trips estimate (pre-pass).** 1.

### Task 02: search-content-jsonish
**Statement.** Same as Task 01 but produce JSON output suitable for downstream pipelines.
**Tags.** read-only, pipe-friendly, JSON
**Expected outcome.** exit 0/1 same; stdout is `{"hits": [...], "total": N, "meta": {...}}`.
**Round-trips estimate.** 1.

### Task 03: search-with-fallback-detection
**Statement.** Search using semantic mode if available, fall back to lexical. Detect which mode actually ran.
**Tags.** read-only, JSON, provenance
**Expected outcome.** stdout JSON with `meta.search_mode` field set to `"hybrid" | "lexical" | "semantic"`.
**Round-trips estimate.** 1.

### Task 04: paginate-large-result
**Statement.** Search returning > 1000 results; fetch the first page then the next page using cursor.
**Tags.** read-only, multi-step
**Expected outcome.** Two calls; first returns `meta.cursor.next`; second uses `--cursor=<next>`.
**Round-trips estimate.** 2.

### Task 05: filter-by-extension
**Statement.** Search only `.rs` files for "panic!" calls.
**Tags.** read-only, pipe-friendly
**Expected outcome.** exit 0/1; results limited to `.rs`.
**Round-trips estimate.** 1.

---

## Package manager tasks (e.g. cargo, npm, pnpm, bun, pip, uv)

### Task 01: install-package
**Statement.** Add a new dependency `serde@1.0` to the project. Save to manifest. Print resolution plan first (don't actually install if --dry-run).
**Tags.** mutating, requires-config
**Expected outcome.** With --dry-run: stdout shows resolution plan; no manifest changes. Without: manifest updated.
**Round-trips estimate.** 1.

### Task 02: list-installed-with-versions
**Statement.** List all installed dependencies with versions in JSON.
**Tags.** read-only, pipe-friendly, JSON
**Expected outcome.** exit 0; stdout is `{"dependencies": [{"name": "...", "version": "..."}]}`.
**Round-trips estimate.** 1.

### Task 03: audit-for-vulnerabilities
**Statement.** Run security audit. Print findings as JSON. Exit non-zero if any vulnerabilities found.
**Tags.** read-only, security
**Expected outcome.** exit 0 if clean, exit 3 (findings-present) if vulnerabilities found; stdout JSON.
**Round-trips estimate.** 1.

### Task 04: update-with-diff
**Statement.** Update all packages and show what changed.
**Tags.** mutating, pipe-friendly
**Expected outcome.** With --dry-run: shows update plan; without: applies updates and prints diff.
**Round-trips estimate.** 1 + 1 (for --dry-run preview).

### Task 05: lockfile-drift-check
**Statement.** Detect lockfile drift from manifest.
**Tags.** read-only, JSON
**Expected outcome.** exit 0 = aligned; exit 1 = drift; stdout details.
**Round-trips estimate.** 1.

---

## Build tool tasks (e.g. cargo build, go build, bazel, ninja)

### Task 01: incremental-build
**Statement.** Build the project; rebuild only what changed since last build.
**Tags.** mutating (writes build artifacts), JSON-output via --message-format=json
**Expected outcome.** exit 0 on success; stdout is build messages; build artifacts updated.
**Round-trips estimate.** 1.

### Task 02: explain-rebuild
**Statement.** Show why target X is being rebuilt.
**Tags.** read-only
**Expected outcome.** exit 0; stdout explains dependency edges that triggered rebuild.
**Round-trips estimate.** 1.

### Task 03: parse-build-errors
**Statement.** Build fails; agent parses errors as `file:line:col – message` to surface to the user.
**Tags.** read-only on output, mutating on side effects
**Expected outcome.** exit non-zero; stdout has machine-parseable errors (or `--message-format=json`).
**Round-trips estimate.** 1.

### Task 04: clean-cache
**Statement.** Clean build cache. Show plan first.
**Tags.** mutating (deletes), requires-confirmation
**Expected outcome.** With --dry-run: lists what would be deleted; with --yes: deletes.
**Round-trips estimate.** 1.

---

## Test runner tasks (e.g. cargo test, pytest, vitest, go test)

### Task 01: run-all-tests
**Statement.** Run all tests; exit non-zero if any fail.
**Tags.** mutating (writes results), JSON
**Expected outcome.** exit 0 if pass, exit 1 if fail; stdout includes summary.
**Round-trips estimate.** 1.

### Task 02: run-failing-tests-only
**Statement.** Re-run only the tests that failed in the previous run.
**Tags.** mutating, multi-step
**Expected outcome.** exit 0/1; if no previous run, error with "no previous run; run all first".
**Round-trips estimate.** 1.

### Task 03: filter-by-pattern
**Statement.** Run only tests whose name matches "auth*".
**Tags.** mutating
**Expected outcome.** exit 0/1; runs only matching tests.
**Round-trips estimate.** 1.

### Task 04: get-junit-xml
**Statement.** Run all tests and emit JUnit XML for CI ingestion.
**Tags.** mutating, structured output
**Expected outcome.** exit 0/1; XML file at known path or stdout.
**Round-trips estimate.** 1.

### Task 05: parse-failure-details
**Statement.** Test fails; parse the failure to find file:line + assertion.
**Tags.** read-only on output
**Expected outcome.** stderr or JSON has `file:line:col – assertion`.
**Round-trips estimate.** 1.

---

## SCM / git-flavored tool tasks (e.g. git, jj, hg, br beads)

### Task 01: show-current-state
**Statement.** Show current branch, dirty files, sync status with remote.
**Tags.** read-only, JSON
**Expected outcome.** exit 0; stdout JSON with `{branch, ahead_count, dirty_files: [...]}`.
**Round-trips estimate.** 1.

### Task 02: show-diff
**Statement.** Show changes since last commit.
**Tags.** read-only, pipe-friendly
**Expected outcome.** exit 0; stdout is unified-diff format (or `--json` patches).
**Round-trips estimate.** 1.

### Task 03: commit-with-message
**Statement.** Commit staged changes with message "feat: add X".
**Tags.** mutating
**Expected outcome.** exit 0; stdout shows commit SHA.
**Round-trips estimate.** 1.

### Task 04: list-stale-branches
**Statement.** List branches not merged into main and older than 30 days.
**Tags.** read-only, JSON
**Expected outcome.** stdout JSON list of branches.
**Round-trips estimate.** 1.

### Task 05: safe-rebase-prep
**Statement.** Before rebasing, show what would happen with --dry-run.
**Tags.** mutating-preview
**Expected outcome.** stdout shows rebase plan; no mutations.
**Round-trips estimate.** 1.

---

## Daemon / server CLI tasks (e.g. dockerd, kubectl, redis-cli)

### Task 01: connect-to-daemon
**Statement.** Connect to running daemon; fail with useful message if not running.
**Tags.** read-only, error_pedagogy
**Expected outcome.** exit 0 if connected; exit 4 (transient) with "is the daemon running? start with `<command>`".
**Round-trips estimate.** 1.

### Task 02: query-state
**Statement.** Get the current state of all resources of type X.
**Tags.** read-only, JSON, pagination
**Expected outcome.** stdout JSON with paginated results.
**Round-trips estimate.** 1 (or N for paginated).

### Task 03: send-admin-command
**Statement.** Send a privileged admin command (e.g. flush cache).
**Tags.** mutating, admin-gated
**Expected outcome.** Requires `--admin` flag; exit non-zero if unauthorized.
**Round-trips estimate.** 1.

### Task 04: tail-logs
**Statement.** Follow logs in real-time, last N lines first.
**Tags.** streaming, NDJSON
**Expected outcome.** Continuous NDJSON output until interrupted.
**Round-trips estimate.** 1 (long-running).

### Task 05: graceful-restart
**Statement.** Restart daemon without dropping active connections.
**Tags.** mutating, requires --yes
**Expected outcome.** exit 0; active connections drained gracefully.
**Round-trips estimate.** 1.

---

## File-format converter tasks (e.g. jq, pandoc, ffmpeg, csctf)

### Task 01: convert-stdin-stdout
**Statement.** Convert from format A on stdin to format B on stdout.
**Tags.** read-only, streaming
**Expected outcome.** stdin = input; stdout = output; exit 0 on success.
**Round-trips estimate.** 1.

### Task 02: validate-input
**Statement.** Validate input conforms to schema; report errors with file:line.
**Tags.** read-only, error_pedagogy
**Expected outcome.** exit 0 = valid; exit 1 = invalid + stderr lists errors.
**Round-trips estimate.** 1.

### Task 03: extract-slice
**Statement.** Extract a specific slice (page, section, range) from input.
**Tags.** read-only, pipe-friendly
**Expected outcome.** stdout = extracted slice.
**Round-trips estimate.** 1.

### Task 04: convert-with-options
**Statement.** Convert applying transformations (e.g. resize, downsample).
**Tags.** read-only, configurable
**Expected outcome.** stdout = transformed output.
**Round-trips estimate.** 1.

---

## Scaffolder / generator tasks (e.g. cargo-generate, create-react-app)

### Task 01: list-templates
**Statement.** List all available templates with descriptions.
**Tags.** read-only, JSON
**Expected outcome.** stdout JSON list of templates.
**Round-trips estimate.** 1.

### Task 02: dry-run-generate
**Statement.** Generate a project from template "rust-cli" but only show what files would be created.
**Tags.** mutating-preview
**Expected outcome.** stdout lists files; nothing written to disk.
**Round-trips estimate.** 1.

### Task 03: generate-with-overrides
**Statement.** Generate project, overriding template var `author=Alice`.
**Tags.** mutating, requires --yes
**Expected outcome.** exit 0; project created at target dir.
**Round-trips estimate.** 1.

### Task 04: refresh-existing
**Statement.** Apply template updates to an existing project (re-scaffold without losing user changes).
**Tags.** mutating, conflict-aware
**Expected outcome.** exit 0; report conflicts; require user resolution.
**Round-trips estimate.** 1+.

---

## Hook tool tasks (e.g. dcg, husky, pre-commit)

### Task 01: should-allow-command
**Statement.** Check whether shell command "X" should be allowed; return JSON verdict.
**Tags.** read-only, JSON, sub-second
**Expected outcome.** exit 0 = allowed; exit 2 = blocked; stdout = `{verdict, rules_matched, alternatives}`.
**Round-trips estimate.** 1.

### Task 02: explain-verdict
**Statement.** Explain why command "X" was blocked, with safe alternatives.
**Tags.** read-only, JSON, error_pedagogy
**Expected outcome.** stdout includes `safe_alternatives: ["...", "..."]`.
**Round-trips estimate.** 1.

### Task 03: list-active-rules
**Statement.** List all active blocking rules from active packs.
**Tags.** read-only, JSON
**Expected outcome.** stdout JSON list.
**Round-trips estimate.** 1.

### Task 04: allowlist-add
**Statement.** Add command pattern "X" to allowlist.
**Tags.** mutating, requires --yes (since it weakens safety)
**Expected outcome.** Allowlist updated.
**Round-trips estimate.** 1.

---

## Issue tracker / task graph tasks (e.g. br beads, bv, gh issues, linear-cli)

### Task 01: find-next-ready-item
**Statement.** Find the highest-priority item that's ready to work on (no blockers).
**Tags.** read-only, JSON, mega-command
**Expected outcome.** Single mega-call returns top item + claim command + alternatives. (Operator Σ)
**Round-trips estimate.** 1.

### Task 02: claim-and-start
**Statement.** Claim item X-001 and mark in-progress.
**Tags.** mutating
**Expected outcome.** exit 0; item state updated.
**Round-trips estimate.** 1.

### Task 03: show-graph-health
**Statement.** Show project graph metrics (cycles, blocked count, critical path).
**Tags.** read-only, JSON, two-phase-latency
**Expected outcome.** stdout JSON with metrics + per-metric `status: computed | timeout`.
**Round-trips estimate.** 1.

### Task 04: plan-parallel-tracks
**Statement.** Show how to parallelize remaining work across N agents.
**Tags.** read-only, JSON
**Expected outcome.** stdout JSON with `tracks: [...]`.
**Round-trips estimate.** 1.

### Task 05: close-with-reason
**Statement.** Close item X-001 with reason "fixed in commit abc123".
**Tags.** mutating
**Expected outcome.** exit 0; close logged.
**Round-trips estimate.** 1.

---

## Authentication / credential tool tasks (e.g. gh auth, gcloud auth, op)

### Task 01: check-current-identity
**Statement.** Show current logged-in user, profile, scopes.
**Tags.** read-only, JSON, never-leak-credentials
**Expected outcome.** stdout JSON; no token/secret in output.
**Round-trips estimate.** 1.

### Task 02: switch-profile
**Statement.** Switch to profile "prod".
**Tags.** mutating
**Expected outcome.** exit 0; subsequent commands use "prod".
**Round-trips estimate.** 1.

### Task 03: refresh-token
**Statement.** Refresh expired token without browser flow.
**Tags.** mutating, network-required
**Expected outcome.** exit 0 if successful; exit 4 (transient) on network failure.
**Round-trips estimate.** 1.

### Task 04: list-profiles
**Statement.** List configured profiles with token expiry.
**Tags.** read-only, JSON
**Expected outcome.** stdout JSON.
**Round-trips estimate.** 1.

---

## Migration tool tasks (e.g. sqlx migrate, alembic, flyway)

### Task 01: show-migration-status
**Statement.** Show applied vs pending migrations.
**Tags.** read-only, JSON
**Expected outcome.** stdout JSON list.
**Round-trips estimate.** 1.

### Task 02: dry-run-apply-pending
**Statement.** Show SQL that would run for pending migrations.
**Tags.** mutating-preview
**Expected outcome.** stdout = SQL statements; nothing applied.
**Round-trips estimate.** 1.

### Task 03: apply-with-yes
**Statement.** Apply pending migrations.
**Tags.** mutating, requires --yes
**Expected outcome.** exit 0; migrations applied.
**Round-trips estimate.** 1.

### Task 04: rollback-one
**Statement.** Rollback the last applied migration.
**Tags.** mutating, requires --yes, requires --dry-run
**Expected outcome.** Rollback applied with confirmation.
**Round-trips estimate.** 1.

---

## Diagnostic / observability CLI tasks (e.g. strace, lsof, htop, pt)

### Task 01: snapshot-state
**Statement.** Take a one-time snapshot of system state.
**Tags.** read-only, JSON, --once
**Expected outcome.** stdout JSON; tool exits.
**Round-trips estimate.** 1.

### Task 02: watch-metric
**Statement.** Watch a metric over time, NDJSON one-per-second.
**Tags.** streaming, NDJSON
**Expected outcome.** Continuous NDJSON until interrupted.
**Round-trips estimate.** 1.

### Task 03: inspect-process
**Statement.** Show details about process PID 12345.
**Tags.** read-only, JSON
**Expected outcome.** stdout JSON.
**Round-trips estimate.** 1.

### Task 04: list-resources
**Statement.** List all resources of type X (e.g. open files, sockets, processes).
**Tags.** read-only, JSON, pagination
**Expected outcome.** stdout JSON list.
**Round-trips estimate.** 1.

---

## MCP server with companion CLI tasks (e.g. am)

### Task 01: start-session-via-macro
**Statement.** Start a session using the macro that collapses identity friction.
**Tags.** mutating, mega-command
**Expected outcome.** Single call returns session_id + initial state.
**Round-trips estimate.** 1.

### Task 02: reserve-files
**Statement.** Reserve glob "src/**" for editing with TTL 1800s.
**Tags.** mutating, advisory-lease
**Expected outcome.** exit 0; reservation logged.
**Round-trips estimate.** 1.

### Task 03: send-threaded-message
**Statement.** Send a message to another agent in thread "feat-123".
**Tags.** mutating, communication
**Expected outcome.** exit 0; message persisted.
**Round-trips estimate.** 1.

### Task 04: fetch-inbox
**Statement.** Fetch unread messages for current agent.
**Tags.** read-only, JSON
**Expected outcome.** stdout JSON list.
**Round-trips estimate.** 1.

### Task 05: cli-mcp-parity-check
**Statement.** Verify CLI invocation produces same result as MCP tool call.
**Tags.** read-only, parity-check
**Expected outcome.** Both produce identical output (modulo metadata).
**Round-trips estimate.** 2.

---

## Multi-binary toolkit tasks

### Task 01: discover-family
**Statement.** Discover all binaries in the family + their relationships.
**Tags.** read-only, JSON
**Expected outcome.** stdout JSON of binary catalog.
**Round-trips estimate.** 1.

### Task 02: cross-binary-pipeline
**Statement.** Pipeline output of binary A through binary B.
**Tags.** read-only, composability
**Expected outcome.** Works without jq surgery (envelopes align).
**Round-trips estimate.** 1.

### Task 03: family-doctor
**Statement.** Run health check across the whole family.
**Tags.** read-only, JSON
**Expected outcome.** stdout reports per-binary health.
**Round-trips estimate.** 1.

---

## Universal tasks (apply to every CLI)

These should be in every Phase 9 simulation regardless of archetype:

### U-Task 01: read-help
**Statement.** Read top-level `--help`. Confirm AGENT/AUTOMATION footer present.
**Tags.** discoverability
**Round-trips estimate.** 1.

### U-Task 02: read-capabilities
**Statement.** Read `<tool> capabilities --json`. Confirm 6 required keys present.
**Tags.** introspection
**Round-trips estimate.** 1.

### U-Task 03: read-robot-docs
**Statement.** Read `<tool> robot-docs guide`. Should be < 80 lines and cover basics.
**Tags.** in-tool docs
**Round-trips estimate.** 1.

### U-Task 04: try-typo
**Statement.** Run with a typo'd flag (e.g. `--jsno`). Verify "did you mean --json?" hint appears.
**Tags.** intent_inference
**Round-trips estimate.** 1.

### U-Task 05: pipe-output
**Statement.** Pipe `<tool> X --json | jq .` and verify it works without ANSI noise.
**Tags.** composability
**Round-trips estimate.** 1.

### U-Task 06: respect-no-color
**Statement.** Run with `NO_COLOR=1` and verify no ANSI in output.
**Tags.** composability
**Round-trips estimate.** 1.

### U-Task 07: respect-non-tty
**Statement.** Pipe stdout to `cat`. Verify no TUI launches; no progress bars; no spinners.
**Tags.** composability
**Round-trips estimate.** 1.

### U-Task 08: deterministic-rerun
**Statement.** Run twice with same input. Verify output is byte-identical (modulo documented volatile fields).
**Tags.** determinism
**Round-trips estimate.** 2.

---

## How to use this library

1. Phase 0 picks the archetype.
2. Phase 9 simulator gets the relevant archetype's tasks PLUS the 8 universal tasks.
3. Customize task wording for the specific tool (s/`<tool>`/`mytool`/g).
4. Phase 9 captures transcripts; classifies success/round-trips per task.
5. Compare pre-pass vs post-pass round-trip counts as the ground-truth methodology check.

If the user has additional tool-specific canonical tasks, add them to `audit/canonical_tasks.md` (per `assets/canonical-task-template.md`). The simulator reads from there.
