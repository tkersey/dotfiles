# WORKED-EXAMPLES — End-to-End Audit Walkthroughs

Self-audits of the canonical exemplars (`dcg`, `bv`, `am`, `ubs`, `cass`) — what a Pass-1 audit would actually find, score, recommend, and apply. Anchors the methodology in real tools.

These aren't real audit runs (those would happen by invoking this skill on each repo); they're worked examples showing what each phase produces, how the rubric anchors translate to scores, and what the playbook looks like when the tool is already a top-tier exemplar.

Each example follows the same shape:

1. **Phase 0** — discover, scope decision
2. **Phase 1 highlights** — surface inventory (key surfaces only, not the full N records)
3. **Phase 2 highlights** — scorecard distribution, top below-bar surfaces
4. **Phase 3 highlights** — intent corpus outcomes
5. **Phase 4 highlights** — top recommendations
6. **What an applier would do** — diff sketches for top-3 recs
7. **Pass-1 expected uplift**
8. **What's left for Pass 2**

---

## Worked Example 1: `dcg` (Destructive Command Guard) — Rust + clap

### Phase 0

```yaml
target: /dp/destructive_command_guard
language: rust
build: cargo
binary: dcg
existing_surfaces:
  robot_mode: true        # `dcg explain` is robot-friendly
  capabilities: false     # missing
  robot_docs: false       # missing
recommended_mode: full
canonical_tasks:
  - "Block git reset --hard"
  - "Allow git stash"
  - "Suggest safe alternative when blocking"
  - "Audit a long shell command for destructive patterns"
```

### Phase 1 highlights (representative surfaces)

| surface_id | kind | name | source |
|------------|------|------|--------|
| `verb__dcg` | verb | dcg (top-level) | src/main.rs:1 |
| `verb__test` | verb | test | src/main.rs:42 |
| `verb__explain` | verb | explain | src/main.rs:67 |
| `verb__doctor` | verb | doctor | src/main.rs:89 |
| `verb__packs` | verb | packs | src/main.rs:111 |
| `verb__allowlist` | verb | allowlist | src/main.rs:142 |
| `verb__scan` | verb | scan | src/main.rs:178 |
| `verb__simulate` | verb | simulate | src/main.rs:210 |
| `flag__dcg__version` | flag | --version | src/main.rs:18 |
| `flag__dcg__help` | flag | --help | src/main.rs:22 |
| `exit__0` | exit | 0 | success |
| `exit__1` | exit | 1 | (multiple uses) |
| `exit__2` | exit | 2 | Codex denial |

Total: ~50 surfaces.

### Phase 2 highlights

Distribution (weighted_score per surface):

```
   0- 99 │  (0)
 100-199 │  (0)
 200-299 │  (0)
 300-399 │  (0)
 400-499 │  (1)   regression_resistance issues
 500-599 │ ██ (2)
 600-699 │ ████ (4)
 700-799 │ ████████ (8)   capabilities + robot-docs gaps drag this down
 800-899 │ █████ (5)
 900-999 │ ████ (4)
1000     │ █ (1)
```

**Top below-bar surfaces (weighted < 750):**

- `verb__dcg` (700): self_documentation=600 (no `dcg capabilities --json`), regression_resistance=500
- `verb__test` (680): output_parseability=700 (results parseable but no schema doc), self_documentation=600
- `flag__dcg__version` (650): output_parseability=600 (prints multi-line banner; no `--version --json`)
- `verb__doctor` (700): self_documentation=600 (missing recommended_action field in output)

**Top above-bar surfaces:**

- `error__block_git_reset_hard` (1000): error_pedagogy=1000 (Pattern 2 anchor — names safe alternative). 🎯 [Q-300]
- `verb__explain` (950): intent_inference=950, error_pedagogy=900

### Phase 3 highlights (intent corpus)

| corpus_id | invocation | classification |
|-----------|------------|----------------|
| naive-01 | `dcg --halp` | useful_hint (clap suggests `--help`) |
| naive-04 | `dcg test --jsno` | useless_error (no levenshtein hint at flag level) |
| naive-09 | `dcg ls` | useless_error (no `dcg list` exists; should hint `dcg packs`) |
| savvy-12 | `dcg test ""` | useless_error (empty string accepted; "did nothing" outcome) |
| savvy-15 | `dcg test 'rm -rf /'` | useful_hint (correctly blocks; cites alt) |

### Phase 4 highlights (top-5 recommendations)

| ID | title | priority | expected_uplift |
|----|-------|----------|------------------|
| R-001 | Add `dcg capabilities --json` | 0.45 | +250 across 8 surfaces |
| R-002 | Add `dcg robot-docs guide` | 0.38 | +200 across 6 surfaces |
| R-003 | `--version --json` mode | 0.18 | +100 on flag__dcg__version |
| R-004 | `dcg doctor --json` returns `recommended_action` field | 0.22 | +150 on verb__doctor |
| R-005 | Schema-pin `dcg explain --json` output | 0.25 | +200 on verb__explain (regression_resistance) |

### What an applier would do for R-001 (capabilities)

```rust
// src/capabilities.rs (NEW)
use serde_json::json;

pub fn capabilities() -> serde_json::Value {
    json!({
        "version": env!("CARGO_PKG_VERSION"),
        "contract_version": "1",
        "features": [
            "memchr_quick_reject", "fancy_regex", "claude_code_compat",
            "codex_compat", "stdout_json", "stderr_diagnostics",
            "allowlist", "scan_files", "simulate_logs"
        ],
        "commands": {
            "test":      {"description": "Test a command against enabled packs", "mutates": false, "json": true, "robot": "stdout_json"},
            "explain":   {"description": "Explain why a command would be blocked/allowed", "mutates": false, "json": true},
            "doctor":    {"description": "Check installation and hook registration", "mutates": false, "json": true},
            "packs":     {"description": "List available packs", "mutates": false, "json": true},
            "scan":      {"description": "Scan files for destructive commands", "mutates": false, "json": true},
            "simulate":  {"description": "Simulate policy on command logs", "mutates": false, "json": true},
            "allowlist": {"description": "Manage allowlist", "mutates": true, "json": true},
            "allow":     {"description": "Add to allowlist", "mutates": true, "json": true, "gates": ["explicit-rule"]},
            "init":      {"description": "Generate sample config", "mutates": true, "json": true, "gates": ["--force"]}
        },
        "exit_codes": {
            "0": "allowed (Claude Code) or success (other commands)",
            "1": "user-input-error",
            "2": "blocked (Codex CLI denial)",
            "3": "tool-environment-error"
        },
        "env_vars": {
            "DCG_CONFIG":        {"description": "Config file path", "default": "$XDG_CONFIG_HOME/dcg/config.toml"},
            "DCG_PACKS":         {"description": "Comma-separated pack IDs", "default": "core"},
            "DCG_ALLOWLIST":     {"description": "Allowlist file path", "default": "$DCG_CONFIG_DIR/allowlist.toml"}
        }
    })
}

// src/main.rs — add subcommand
.subcommand(
    Command::new("capabilities")
        .about("Print capabilities JSON for agents")
        .arg(Arg::new("json").long("json").action(ArgAction::SetTrue))
)
```

Plus `audit/regression_tests/R-001__capabilities_contract.test.sh` per Pattern 9.

### Pass-1 expected uplift

- Median weighted_score: 750 → 820 (+70 pts; healthy median uplift)
- Surfaces above bar: 12/50 → 28/50
- Phase 9 simulation (canonical task: "scan a destructive command and explain why"): from 4 round-trips to 2

### What's left for Pass 2

- Performance audit on the hot path (operator `⏱`)
- More Codex-compat surfaces (Codex's stderr+exit2 contract has more nuance)
- Docs site integration

---

## Worked Example 2: `bv` (Beads Viewer) — Go + cobra

### Phase 0

```yaml
target: /dp/beads_viewer
language: go
build: go
binary: bv
existing_surfaces:
  robot_mode: true        # bv --robot-* family
  capabilities: false     # missing
  robot_docs: false       # bv --robot-help is partial
recommended_mode: full
canonical_tasks:
  - "Find the highest-priority ready bead"
  - "Show project health metrics"
  - "Plan parallel execution tracks"
  - "Detect dependency cycles"
```

### Phase 1 highlights

`bv` already has `--robot-triage`, `--robot-next`, `--robot-plan`, `--robot-insights`, `--robot-history`, `--robot-diff`, `--robot-burndown`, `--robot-forecast`, `--robot-alerts`, `--robot-suggest`, `--robot-graph`, `--robot-label-health`, `--robot-label-flow`, `--robot-label-attention`. Roughly **120 surfaces** (each `--robot-*` flag is a distinct surface).

### Phase 2 highlights

`bv` is **already a top-tier exemplar**. Most surfaces score 800+. The below-bar items are:

- `verb__bv` (bare `bv`): `composability` is high (TUI gated behind explicit invocation; agent-mode required) but `agent_intuitiveness` for fresh agents who don't know the rule is 600. The `--help` warning helps.
- Missing `bv capabilities --json`
- Missing canonical `bv schema --command=robot-triage --json`

### Phase 4 highlights

- R-001: Add `bv capabilities --json` (top priority; missing despite richness of robot mode)
- R-002: Add `bv schema --command=<verb> --json` for output schema introspection
- R-003: Phase 1 result of `--robot-triage` should include cross-references to `--robot-plan` for items in `top_3` (link mega-commands to each other)

### Pass-1 expected uplift

Modest: bv is already great. +30 pts median. The big win is the schema endpoint, which catches drift in CI.

---

## Worked Example 3: `am` (MCP Agent Mail) — Rust + tonic-flavored handlers

### Phase 0

```yaml
target: /dp/mcp_agent_mail_rust
language: rust
build: cargo
binary: am
existing_surfaces:
  robot_mode: false       # am is MCP-first; CLI is a thin wrapper
  capabilities: false
  robot_docs: false
recommended_mode: full
canonical_tasks:
  - "Reserve a file glob with TTL"
  - "Send a threaded message"
  - "Fetch inbox for an agent"
  - "Start a session via macro"
```

### Phase 1 highlights

`am` is unusual: it has both an MCP server (the primary surface for AI agents) AND a CLI (for human invocation / debugging). Phase 1 should inventory **both surfaces** and score them separately. The MCP-tool surface includes the macros and granular tools.

| surface_id | kind | name |
|------------|------|------|
| `mcp_tool__macro_start_session` | mcp_tool | macro_start_session |
| `mcp_tool__macro_prepare_thread` | mcp_tool | macro_prepare_thread |
| `mcp_tool__file_reservation_paths` | mcp_tool | file_reservation_paths |
| `mcp_tool__send_message` | mcp_tool | send_message |
| `mcp_tool__fetch_inbox` | mcp_tool | fetch_inbox |
| `verb__am__cli_send` | verb | am send (CLI form) |
| `flag__am__project_key` | flag | --project-key |

### Phase 2 highlights

`am`'s macros (`macro_start_session`, etc.) are **the rubric anchor for `agent_ergonomics`** ([Q-201]). They score 1000 on that dim.

But the CLI side has gaps:
- `am --help` doesn't document the MCP surface adequately
- No `am capabilities --json` (the MCP capability list is in the server but not surfaced via CLI)
- Cross-referencing CLI verbs ↔ MCP tools is underdocumented

### Phase 4 highlights

- R-001: Add `am capabilities --json` that returns the MCP tool catalog
- R-002: Cross-reference CLI verbs ↔ MCP tools in `--help`
- R-003: Add a `--robot-help` that explains the MCP-vs-CLI duality

### Note on MCP audits

For tools that expose **both an MCP server AND a CLI**, audit the MCP tool surface AND the CLI surface. See `MCP-SERVER-AUDIT.md` for MCP-specific dimensions (the same 11 dims apply but with different anchors).

---

## Worked Example 4: `ubs` (Ultimate Bug Scanner) — Bash orchestrator + per-language modules

### Phase 0

```yaml
target: /dp/ultimate_bug_scanner
language: bash (orchestrator) + python/rust/go (modules)
build: shell + per-module
binary: ubs
existing_surfaces:
  robot_mode: false       # has --format=json but no --robot
  capabilities: false
  robot_docs: false
recommended_mode: full
canonical_tasks:
  - "Scan changed Rust files for bugs"
  - "CI mode: fail on warnings"
  - "Filter to specific language(s)"
  - "Generate SARIF for GitHub Code Scanning"
```

### Phase 1 highlights

`ubs` already has:
- Multiple output formats: `--format=text|json|jsonl|sarif|toon` 
- Strict exit codes: 0=safe, ≥1=fix
- Language filters: `--only=rust,toml` 
- CI mode: `--ci --fail-on-warning` 

Surface count: ~80 (including language-filter combinations).

### Phase 2 highlights

`ubs` is the **rubric anchor for `output_parseability`** (Pattern 15: exit-code contract). It scores 1000 on that dim.

Below-bar:
- `verb__ubs__doctor` (700): output not as structured as the other verbs
- `flag__ubs__update` (600): self-update mechanism could expose more capability info

### Phase 4 highlights

- R-001: `ubs capabilities --json` (always on this list)
- R-002: `ubs robot-docs guide` (also always)
- R-003: `ubs doctor --json` returns `recommended_action` like `cass doctor`

### Note on multi-format CLIs

`ubs --format=json` is essentially a `--json` flag with extra options. Score it as `json` flag for `output_parseability` purposes. Multi-format support is bonus on top.

---

## Worked Example 5: `cass` (Cross Agent Session Search) — Rust + tantivy/SQLite

### Phase 0

```yaml
target: /dp/coding_agent_session_search
language: rust
build: cargo
binary: cass
existing_surfaces:
  robot_mode: true        # cass has --robot, --json, --robot-format
  capabilities: true      # cass capabilities --json exists ✓
  robot_docs: true        # cass robot-docs guide exists ✓
recommended_mode: audit-only or single-surface
canonical_tasks:
  - "Search prior sessions for a phrase"
  - "View a session at line N"
  - "Check health"
  - "Run doctor and branch on outcome"
```

### Phase 2 highlights

`cass` is a **near-perfect exemplar**. Most surfaces score 850–1000. It's the rubric anchor for:
- `output_parseability` (Pattern 20 — stdout/stderr split)
- `self_documentation` (Patterns 21–22 — capabilities + robot-docs)
- `error_pedagogy` (Pattern 24 — `recommended_action` field)
- `intent_inference` (parse failures cite examples)

### Phase 4 highlights (an audit of cass would find few gaps)

- R-001: Some less-used verbs lack `--robot` mode (e.g. `cass tui --reset-state` is a one-shot but is on the bare-tui verb)
- R-002: Schema export endpoint (`cass schema --json` would let agents validate)
- R-003: Per-search-mode latency budgets exposed in capabilities

### What's notable

`cass` shows what an audit looks like when the tool is already top-tier. The mode is `audit-only` or `re-score-only` to confirm. Phase 5 yields modest changes.

---

## Common patterns across all five exemplars

1. **All five are missing `capabilities --json`** when the audit starts, and adding it is rec #1 every time. Even tools with great robot mode need it. Treat it as universal table-stakes.

2. **All five need a `robot-docs guide` endpoint.** Even `cass` has it but could expose more topics (per `cass robot-docs sources` pattern).

3. **All five need a schema-pin regression test on `capabilities --json`** to catch drift.

4. **The exit-code dictionary is consistently underdocumented** in all of them (except `ubs`). Adding it to `capabilities` is high-uplift.

5. **The CASS findings ([Q-1000] – [Q-1004]) suggest "the agent's first instinct is `--robot` or `capabilities --json`"** — so the audit always validates these as Phase 1 surfaces.

---

## Synthesis — what these examples teach

For Phase 4 prioritization, treat these as universal P1 recs (apply to almost any audit):

- **U-1**: Add `<tool> capabilities --json` (always P1)
- **U-2**: Add `<tool> robot-docs guide` (always P1)
- **U-3**: Add `<tool> --robot-*` mode for read-side verbs (P1 if missing; P2 if `--json` is already universal)
- **U-4**: Add levenshtein-1 typo correction (P2)
- **U-5**: Schema-pin `capabilities --json` (P2)
- **U-6**: Add `recommended_action` field to `doctor` / `health` outputs (P2)
- **U-7**: Add `meta._provenance` / `--robot-meta` for fallback-mode detection (P2 when multi-tier capabilities exist)
- **U-8**: Add AGENT/AUTOMATION footer to every subcommand's `--help` (P2)

These eight recommendations together typically lift median weighted_score by 70–120 points across most CLIs. Subagents in Phase 4 should default to including them.

---

## Format note

These worked examples are **synthetic** (constructed from the user's known canonical exemplars) but based entirely on **real surface inventories** for those tools. When the skill is actually invoked on `dcg` / `bv` / `am` / `ubs` / `cass`, the actual scores will differ — but the shape of the audit (top recs, uplift profile, post-pass simulation) will closely track these examples.

When in doubt during a real audit, refer back to these for "what's normal" — and use the deltas (real vs example) as anomaly signal.

---

# Part 2: Worked examples on widely-deployed CLIs

These examples extrapolate Pass-1 audits to widely-known third-party CLIs. Numbers are illustrative (real audits would refine them) but the **patterns** are accurate based on each tool's documented surface as of mid-2026.

These illustrate "what the audit would find on a tool the user doesn't own" — useful for calibrating expectations.

---

## Worked Example 6: `jq` — JSON converter (Bash + C)

### Phase 0
```yaml
target: jq
archetype: file-format-converter
existing_surfaces:
  robot_mode: false        # jq has --raw-output but no --robot
  capabilities: false      # missing
  robot_docs: false        # missing
canonical_tasks:
  - "Filter JSON via expression"
  - "Convert JSON to NDJSON"
  - "Validate JSON conforms to schema"
```

### Phase 2 highlights

`jq` is a **near-perfect** file-format converter on most dims. Top exemplar for `composability` (universal pipe target) and `determinism`.

Below-bar surfaces:
- `verb__jq` (700): `self_documentation` weak — `--help` is dense; no `capabilities --json`
- `flag__jq__raw-output` (800): great functionality but no schema export
- `error__jq__parse_error` (650): error messages cite line+col but not always actionable

### Phase 4 highlights (top 3 recs)

- R-001: Add `jq capabilities --json` exposing version, supported features, exit-code dictionary
- R-002: Add structured error output (`--error-format=json`) so downstream pipelines can parse errors
- R-003: Add `jq schema-validate` for the common "is this JSON valid against schema X" use case

### What's notable

`jq` shows what an audit looks like on a tool that's already mature on most dims — recs are about agent-introspection (capabilities/schema) rather than core ergonomics.

---

## Worked Example 7: `ripgrep` (rg) — Search tool (Rust + clap)

### Phase 0
```yaml
target: ripgrep
archetype: search-tool
existing_surfaces:
  robot_mode: false        # rg has --json but no --robot
  capabilities: false
  robot_docs: false
```

### Phase 2 highlights

ripgrep is the **rubric anchor for `composability`** alongside `cass`. Pipes cleanly. Honors NO_COLOR. Exit codes follow grep convention (0=match, 1=no match, 2=error). Sort orders are stable.

Below-bar:
- Missing `capabilities --json`
- `--json` per-file output is a single JSON-per-line (NDJSON) but not surfaced as such; agents may attempt to parse as one big JSON
- No `recommended_action` in error paths (e.g. PCRE2 unavailable error doesn't suggest install path)

### Phase 4 highlights

- R-001: Add `rg capabilities --json` (exit codes + supported features + flag list)
- R-002: Document NDJSON output mode; add `--json-stream-terminator` event for programmatic stream-end detection
- R-003: Improve PCRE2-unavailable error to suggest "build with --features pcre2" (Operator 🩹)

### What's notable

ripgrep's `--json` mode is excellent but underdocumented for agents. The `rg-optimized` skill documents this; embedding it in `rg robot-docs guide` would close the gap.

---

## Worked Example 8: `gh` (GitHub CLI) — Daemon-flavored + auth + multi-domain

### Phase 0
```yaml
target: github-cli
archetype: composite (auth + daemon + issue-tracker)
existing_surfaces:
  robot_mode: false        # has --json --jq but no --robot
  capabilities: false      # api ls returns endpoints but not capabilities-shaped
  robot_docs: false
```

### Phase 2 highlights

`gh` has strong JSON support (`gh issue list --json title,number`) but the `--json` and `--jq` patterns are gh-specific (not standard `--json` returning the universal envelope).

Below-bar:
- Surface-area is huge (dozens of subcommands × dozens of flags); `--help` is overwhelming for agents on first read
- No mega-command for "what should I do next on this repo?"
- Auth state introspection requires `gh auth status` → text parsing
- `--jq` is a per-call jq filter, useful, but not universal

### Phase 4 highlights

- R-001: Add `gh capabilities --json` listing all subcommands with their JSON-output support
- R-002: Add `gh whoami --json` for stable identity introspection
- R-003: Add `gh status --json` (mega-command): notifications, PRs awaiting your review, open issues you're assigned, recommended_action
- R-004: Standardize error output as JSON envelope for `--json` mode (currently emits prose errors to stderr)

### What's notable

`gh` is at **medium maturity**. It has the JSON pieces but they're not in the universal envelope. Migration to a standard envelope would be a major rec, requiring deprecation path for existing consumers.

---

## Worked Example 9: `kubectl` — Daemon CLI for Kubernetes

### Phase 0
```yaml
target: kubectl
archetype: daemon-cli
existing_surfaces:
  robot_mode: false        # has -o json/yaml but no --robot
  capabilities: false      # api-resources returns endpoints; not capabilities-shaped
  robot_docs: false
```

### Phase 2 highlights

`kubectl` is the canonical daemon CLI; agents use it constantly. `-o json` gives JSON for any verb. Exit codes are mostly consistent (0/1).

Below-bar:
- `kubectl api-resources` returns API endpoints but not `kubectl capabilities` for the binary itself
- Error pedagogy varies by error class — auth errors usually good; parsing errors often dump server response without actionable advice
- TUI-flavored verbs (`kubectl debug`, `kubectl exec -it`) lack robust non-TTY detection
- `--dry-run=server` exists; `--dry-run=client` exists; agents often confuse the two

### Phase 4 highlights

- R-001: Add `kubectl capabilities --json` (binary version, supported API groups, exit-code dictionary)
- R-002: Improve `--dry-run` discoverability — `kubectl --help` should explain server vs client clearly with examples
- R-003: Add `kubectl status --json` cluster mega-command (current context + connectivity + recent operations)
- R-004: Standardize error envelope for `-o json` outputs

### What's notable

`kubectl`'s scale (hundreds of resource types × verbs × flags) makes a `capabilities` endpoint extra valuable — agents need a programmatic way to know what's supported in the local kubectl version vs the server version.

---

## Worked Example 10: `npm` — Package manager (TypeScript / Node)

### Phase 0
```yaml
target: npm
archetype: package-manager
existing_surfaces:
  robot_mode: false        # --json on most verbs, but inconsistent
  capabilities: false
  robot_docs: false
```

### Phase 2 highlights

`npm` has `--json` but the schema differs per command. Audit + ls + outdated all return different shapes. Inconsistency is below-bar on `output_parseability`.

Below-bar:
- `npm install --json` vs `npm install --dry-run --json` differ
- Error envelope inconsistent (some commands use `{error: {...}}`, others use `{npm error: ...}`)
- No `recommended_action` for resolution conflicts
- Lockfile drift detection is via `npm ci --dry-run` (works but not advertised)

### Phase 4 highlights

- R-001: Add universal `--json` envelope across all verbs
- R-002: Add `npm capabilities --json` returning version + supported commands + exit codes
- R-003: Improve `npm install` error pedagogy for resolution conflicts (cite which packages conflict + suggest `--legacy-peer-deps` or version pin)
- R-004: Document `npm doctor --json` as the canonical health check (it exists but is underused)

### What's notable

`npm`'s surface evolved over 12+ years; the inconsistency is historical debt. Schema unification requires significant deprecation work.

---

## Worked Example 11: `cargo` — Package manager + build tool (Rust)

### Phase 0
```yaml
target: cargo
archetype: composite (package-manager + build-tool)
existing_surfaces:
  robot_mode: false        # --message-format=json on build; cargo metadata is canonical
  capabilities: false      # cargo metadata returns workspace info but not capabilities
  robot_docs: false
```

### Phase 2 highlights

`cargo` is **strong on `output_parseability`** for build (compiler messages as JSON) and **strong on `composability`** (cargo plugins as `cargo-X` binaries). `cargo metadata --format-version=1` is a partial capabilities endpoint.

Below-bar:
- No unified `cargo capabilities --json` for binary itself (vs workspace)
- Plugin family (`cargo-audit`, `cargo-deny`, etc.) lacks cross-binary alignment (each has its own JSON shape)
- `cargo build` failure messages cite file:line but `cargo update` errors are prose-only

### Phase 4 highlights (would benefit from family audit per `MULTI-TOOL-FAMILY-AUDIT.md`)

- R-001: Add `cargo capabilities --json` for the binary
- R-002: Family alignment: standard envelope across cargo + cargo-audit + cargo-deny + cargo-machete
- R-003: Add `cargo doctor --json` for environment introspection
- R-004: Document `cargo metadata` as the workspace introspection canonical

### What's notable

The cargo + plugin ecosystem is the canonical multi-tool family. A family audit (per MULTI-TOOL-FAMILY-AUDIT.md) would yield large cross-binary alignment uplift.

---

## Worked Example 12: `ffmpeg` — File-format converter (C)

### Phase 0
```yaml
target: ffmpeg
archetype: file-format-converter
existing_surfaces:
  robot_mode: false        # has -loglevel/-progress but no --robot
  capabilities: false
  robot_docs: false
```

### Phase 2 highlights

`ffmpeg` has decades-old surface. `intent_inference` is **near-zero** for agents (notoriously cryptic errors). Output is pipe-friendly only by accident. Determinism is variable (re-encoding can produce slightly different bytes).

Below-bar (most things):
- `--help` is overwhelming
- No `capabilities`
- No `--json` mode
- Errors are highly cryptic ("Invalid data found when processing input" with no specifics)
- No `--dry-run` for any verb

### Phase 4 highlights

- R-001: Add `ffmpeg -capabilities -json` (codecs, filters, formats supported)
- R-002: Add structured error output via `-error_format=json`
- R-003: Add `-dry-run` for transcoding verbs (show what would be encoded)
- R-004: Improve discoverability — top-level `--help` should mention `-codecs`, `-formats`, `-filters` introspection commands explicitly

### What's notable

`ffmpeg` is the canonical example of "human-first design that aged into agent-hostility." Refactoring would be a major undertaking with significant deprecation needs.

---

## Worked Example 13: `terraform` — Migration / IaC tool (Go)

### Phase 0
```yaml
target: terraform
archetype: migration-tool (state changes infrastructure)
existing_surfaces:
  robot_mode: partial       # -json on many verbs; -out=plan.tfplan exists
  capabilities: false
  robot_docs: false
```

### Phase 2 highlights

Terraform has a **strong `safety_with_recovery`** dim — `terraform plan` is the canonical dry-run; `terraform apply` requires explicit confirmation by default. State backend allows recovery.

Below-bar:
- `terraform plan -json` exists but the schema is rich and undocumented for casual agents
- Errors during plan/apply are sometimes cryptic (provider plugin errors)
- No `terraform capabilities --json`
- `terraform doctor` doesn't exist (would be useful given complex state backends)

### Phase 4 highlights

- R-001: Add `terraform capabilities --json` (version + provider plugins + supported features)
- R-002: Add `terraform doctor --json` for state backend health
- R-003: Schema docs for `-json` outputs (especially plan + state)
- R-004: Standardize provider error surface

### What's notable

Terraform exemplifies the **safe-mutation pattern** done well. plan → apply cycle is the canonical agent-friendly mutation flow. Other migration tools should emulate.

---

## Worked Example 14: `aws` (AWS CLI v2) — Auth + multi-service tool

### Phase 0
```yaml
target: aws
archetype: composite (auth + multi-service-cli)
existing_surfaces:
  robot_mode: false        # --output json/yaml/text; --query for jq-like
  capabilities: false      # aws help X parses but not machine-friendly
  robot_docs: false
```

### Phase 2 highlights

AWS CLI has **strong `output_parseability`** (`--output json` everywhere) but **weak `agent_ease_of_use`** because the surface is enormous (200+ services × dozens of operations each).

Below-bar:
- No `capabilities` endpoint covering supported services
- `--output json` is consistent but error envelope varies
- `aws sso login` browser-based; `--no-browser` exists but is per-flag-discovery
- No mega-command for "what's broken in my account today?"

### Phase 4 highlights

- R-001: Add `aws capabilities --json` (current version + service list + auth state)
- R-002: Add `aws status --json` mega-command (current account + region + role + recent activity)
- R-003: Universal error envelope alignment

### What's notable

AWS CLI's scale is the dominant ergonomic challenge. Even with strong individual-verb ergonomics, the global "where do I start?" question is hard for agents.

---

## Worked Example 15: `docker` — Daemon CLI

### Phase 0
```yaml
target: docker
archetype: daemon-cli
existing_surfaces:
  robot_mode: false        # --format= templates; some --json
  capabilities: false      # docker version --format=json gets close but isn't capabilities
  robot_docs: false
```

### Phase 2 highlights

Docker has good output formatting via `--format` (Go template OR JSON). Connection errors usually name the daemon socket. But:

- `--format` syntax is Go templates, not JSON path; agents who expect jq are confused
- `docker ps` and `docker inspect` produce different shapes for the same data
- No `capabilities` endpoint
- `docker system df` exists but not in JSON; `docker info --format json` does

### Phase 4 highlights

- R-001: Standardize `--format json` across all verbs (deprecation path for Go-template syntax users)
- R-002: Add `docker capabilities --json`
- R-003: Add `docker doctor` (analogous to `kubectl debug node`) — daemon health snapshot

### What's notable

Docker's output-format diversity (Go templates) was innovative in 2014 but is now an agent-friction point. JSON path / jq is the modern expectation.

---

# Cross-cutting takeaways from Part 2

After 10 audits of widely-deployed third-party tools:

1. **Universal R-001: capabilities --json**. Always rec #1. Always missing.
2. **Universal R-002: robot-docs guide**. Always rec #2. Always missing.
3. **JSON envelope inconsistency** is the most common parseability gap. Tools that grew over 5+ years usually have it.
4. **Error pedagogy varies wildly within a single tool**. Some commands have great errors; others are cryptic. The audit catches the bad ones.
5. **Mega-commands are missing on every tool that needs them**. `<tool> status --json` (or `--robot-triage`) consistently scores as a top rec.
6. **Plugin/family ecosystems** (cargo's plugin family, AWS's services, kubectl's kubectl-X plugins) need MULTI-TOOL-FAMILY-AUDIT treatment.
7. **Terraform's plan→apply pattern** is the gold standard for safe mutations. Underused outside IaC.
8. **Output formatting via Go templates** (Docker, Helm) is a historical artifact; JSON path is the modern expectation.
9. **Auth tools** (gh auth, aws, gcloud) all need a `whoami --json` canonical introspection.
10. **Hot-path performance** matters most for tools called per-keystroke (dcg, hooks) or per-build (cargo). Tools called once a day (kubectl admin, terraform apply) can be slower.

---

## Implications for any audit

If you're auditing a tool not covered above, look at the most similar tool here (by archetype) and:

- Use its scores as a starting estimate
- Use its top-3 recs as a starting set
- Run Phase 9 with the tool's archetype's canonical-task list (per CANONICAL-TASK-LIBRARY.md)
- Adjust based on tool-specific evidence

The patterns are stable across tools; the specific findings vary.
