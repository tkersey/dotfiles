# CANONICAL-EXEMPLARS-DEEP — Code-level analysis of dcg / bv / am / ubs / cass

CANONICAL-EXEMPLARS.md catalogues 25 numbered patterns. This file gives the deeper code-level analysis: real `--help` excerpts, capabilities JSON snippets, internal file:line references where applicable.

Use this when you need the precise idioms — not just "what dcg does" but "how dcg does it."

---

## DCG — Destructive Command Guard

**Repo.** `/dp/destructive_command_guard`. Rust + clap.

### Top-level `--help`

```
  🛡  dcg 0.5.0
     Destructive Command Guard - multi-agent safety hook

  USAGE
  ──────────────────────────────────────────────────
    Runs as a pre-execution shell hook for Claude Code, Codex CLI,
    Gemini CLI, GitHub Copilot CLI, and Cursor IDE.
    Compatible agents receive stdout JSON; Codex denials use stderr + exit 2.

  CONFIGURATION
  ──────────────────────────────────────────────────
    Installers configure supported agent hooks automatically.
    Common Claude Code config in ~/.claude/settings.json:

    ╭──────────────────────────────────────────────────────────────╮
    │ {"hooks": {"PreToolUse": [{"matcher": "Bash",                │
    │   "hooks": [{"type": "command", "command": "dcg"}]}]}}       │
    ╰──────────────────────────────────────────────────────────────╯

  OPTIONS
  ──────────────────────────────────────────────────
    --version, -V     Print version information
    --help, -h        Print this help message

  COMMANDS
  ──────────────────────────────────────────────────
    test         Test a command against enabled packs
    explain      Explain why a command would be blocked/allowed
    doctor       Check installation and hook registration
    packs        List all available packs and their status
    pack         Pack management commands (info, validate)
    allowlist    Manage allowlist entries (add, list, remove)
    allow        Add a rule to the allowlist
    unallow      Remove a rule from the allowlist
    allow-once   Allow a blocked command once via short code
    scan         Scan files for destructive commands
    simulate     Simulate policy evaluation on command logs
    config       Show current configuration
    init         Generate a sample configuration file
```

**What's good.**
- Top of help describes the safety model in 2 sentences
- Cross-agent compatibility note explicit ("stdout JSON" vs "stderr + exit 2")
- Configuration paste-ready
- Verb list short and clearly grouped

**What an audit would flag.**
- No AGENT/AUTOMATION footer pointing to capabilities/robot-docs
- No `dcg capabilities --json`
- No exit-code dictionary in `--help`

### Block message pattern (Operator 🩹 anchor)

For `git reset --hard`:

```
[Hypothetical block output, paraphrased from dcg behavior]
🛡  dcg blocked: git reset --hard
  reason: destroys uncommitted changes irreversibly
  alternatives:
    git stash               # save changes for later
    git revert <commit>     # create new commit reversing changes
    git diff > backup.patch # backup as patch
  to override (NOT RECOMMENDED): dcg allow-once <code>
exit 2 (Codex-compat denial)
```

The structure:
1. What was blocked
2. Why
3. Named alternatives (3+)
4. Override path (gated)
5. Exit code with semantic

### Quick-reject hot path

```rust
// src/main.rs (paraphrased)
use memchr::memmem;

const DANGER_TOKENS: &[&[u8]] = &[
    b"reset --hard", b"clean -fd", b"rm -rf", b"DROP TABLE",
];

fn might_be_destructive(cmd: &[u8]) -> bool {
    DANGER_TOKENS.iter().any(|t| memmem::find(cmd, t).is_some())
}

fn check(cmd: &str) -> Verdict {
    if !might_be_destructive(cmd.as_bytes()) {
        return Verdict::Allow;  // 99%+ of commands skip regex
    }
    // Full regex against fancy-regex pack list
    ...
}
```

The memchr quick-reject is the canonical sub-millisecond pattern. See Operator ⏱.

### Exit-code contract

```
exit 0  → allowed (Claude Code: normal pass-through)
exit 1  → user-input-error (bad invocation)
exit 2  → blocked (Codex CLI denial; stderr message)
exit 3  → tool-environment-error
```

**Audit recommendation.** Add `dcg capabilities --json` exposing this dictionary so agents can branch on `exit_code_kind`.

---

## BV — Beads Viewer (robot mode)

**Repo.** `/dp/beads_viewer`. Go + cobra. Wraps the beads_rust core.

### `bv --robot-help`

```
bv (Beads Viewer) AI Agent Interface
====================================
Use --robot-* flags for deterministic automation output.
Bare bv launches the interactive TUI.

Core commands:
  --robot-triage    Unified triage output (recommended entry point)
  --robot-next      Single top recommendation
  --robot-plan      Dependency-respecting execution tracks
  --robot-insights  Graph metrics and structural analysis
```

**What's good.**
- Mandatory `--robot-*` discipline stated up front
- "Bare bv launches TUI" warning explicit
- Single entry point recommended (`--robot-triage`)

### `bv --robot-triage` JSON shape

```jsonc
{
  "data_hash":     "abc123...",
  "as_of":         "2026-05-06T12:00:00Z",
  "quick_ref": {
    "summary":  "12 ready / 4 blocked / 23 total",
    "top_3": [
      {"id": "br-001", "score": 0.92, "reason": "..."},
      ...
    ]
  },
  "recommendations": [...],
  "quick_wins":      [...],
  "blockers_to_clear": [...],
  "project_health":  {
    "ready_count": 12, "blocked_count": 4,
    "graph_metrics": {"...": "..."}
  },
  "commands": [
    "br update br-001 --status=in_progress",
    "br show br-001",
    "git checkout -b br-001-feature"
  ],
  "warnings": []
}
```

### Two-phase analysis pattern (Operator 🪜)

```jsonc
{
  "data_hash": "...",
  "phase_1_metrics": {
    "ready_count":   {"value": 12, "status": "computed_ms_3"},
    "blocked_count": {"value":  4, "status": "computed_ms_2"}
  },
  "phase_2_metrics": {
    "pagerank":     {"value": {...}, "status": "computed_ms_240"},
    "betweenness":  {"value": null,  "status": "timeout_ms_500", "reason": "exceeded budget"},
    "centrality":   {"value": null,  "status": "skipped",        "reason": "user opted out via --skip-expensive"}
  }
}
```

Per-metric `status: computed | approx | timeout | skipped` is the Operator 🪜 anchor. See [Q-400].

### `data_hash` provenance (Operator 🆔)

Every robot-mode output includes a SHA-256 fingerprint of the input `.beads/beads.jsonl`. Downstream consumers cache by data_hash:

```python
# Agent-side caching
result = run("bv --robot-triage")
if cache.get(result["data_hash"]) == result:
    return cache.hit
cache.put(result["data_hash"], result)
```

---

## AM — MCP Agent Mail (Rust)

**Repo.** `/dp/mcp_agent_mail_rust`. Both an MCP server and a thin CLI.

### MCP tool catalog (key ones)

```
macro_start_session         — collapse identity + project + session into 1 call
macro_prepare_thread        — start a thread with reservations + initial msg
macro_file_reservation_cycle — reserve → message → release in 1 call
macro_contact_handshake     — 2-agent rendezvous

register_agent              — granular: just register
ensure_project              — granular: just ensure project exists
file_reservation_paths      — granular: reserve files
release_file_reservations   — granular: release
send_message                — granular: send threaded message
fetch_inbox                 — granular: read inbox
acknowledge_message         — granular: ack
search_messages             — search across threads
```

**The macro vs granular axis** is `am`'s signature pattern. See Operator 🔀.

### macro_start_session shape

```jsonc
{
  "tool": "macro_start_session",
  "params": {
    "project_key": "/data/projects/some-project",  // absolute path = stable handle
    "program":     "claude_code",
    "model":       "opus-4.7"
  }
}
```

Returns:

```jsonc
{
  "ok":          true,
  "agent_name":  "claude-opus-47-abc123",
  "project_key": "/data/projects/some-project",
  "registered_at": "...",
  "inbox_uri":   "resource://inbox/claude-opus-47-abc123?project=...",
  "thread_count_unread": 0,
  "next_actions": [
    {"command": "fetch_inbox(project_key, agent_name)"},
    {"command": "send_message(...)"}
  ]
}
```

One call collapses what would otherwise be `register_agent` + `ensure_project` + `set_active_session`. Operator 🛂 anchor.

### File reservations (Operator 🛡 anchor for advisory leases)

```jsonc
{
  "tool": "file_reservation_paths",
  "params": {
    "project_key": "/data/projects/some-project",
    "agent_name":  "claude-opus-47-abc123",
    "paths":       ["src/cmd/list.rs", "src/cli.rs"],
    "ttl_seconds": 1800,
    "exclusive":   true,
    "reason":      "br-1234 implementing list verb"
  }
}
```

**Why advisory, not enforced:**
- Failure recovers naturally (TTL expires; agent crashes don't deadlock)
- Other agents respect the reservation but can override with `force_release`
- All reservations are committed to git as `mail_archive/projects/<key>/reservations/*.json`

This is the canonical pattern for multi-agent coordination. See [Q-700], [Q-800].

---

## UBS — Ultimate Bug Scanner

**Repo.** `/dp/ultimate_bug_scanner`. Bash orchestrator + per-language analyzer modules.

### `ubs --help` (excerpt)

```
Usage: ubs [options] [PROJECT_DIR]
       ubs [options] FILE1 FILE2 ...
       ubs --files FILE1,FILE2,... [options] [PROJECT_DIR]

Options:
  --format=FMT            text|json|jsonl|sarif|toon (default: text)
  --version               Print version and exit
  --ci                    CI mode (stable timestamps)
  --fail-on-warning       Exit non-zero if warnings or critical exist
  --only=CSV              Restrict to languages: js,python,c,cpp,rust,golang,...
  --comparison=FILE       Baseline JSON to diff combined results against
  --report-json=FILE      Write combined summary JSON to FILE
  ...

Golden Rule: ubs <changed-files> before every commit. Exit 0 = safe. Exit >0 = fix & re-run.
```

**What's good.**
- Multiple usage forms (top-level)
- Output formats explicit (`--format=text|json|jsonl|sarif|toon`)
- CI mode dedicated flag
- Golden Rule at the bottom (anchor for users + agents)

### Output format (text mode, parseable)

```
⚠️  Memory Safety (3 errors)
    src/parser.c:42:5 – use-after-free on `buf` after free at line 38
    💡 Move free() to after last use, or use a smart pointer pattern
    src/parser.c:67:12 – buffer overflow: write past end of stack array
    💡 Use bounds-checked write (e.g. snprintf instead of strcpy)
    ...

⚠️  SQL Injection (1 error)
    src/db.py:99:18 – string-concat in SQL query
    💡 Use parameterized query: cur.execute("...", (user_id,))

Total: 4 errors across 2 categories
Exit code: 1
```

The format is parseable but not JSON. Adds `--format=json` for the JSON form. Both pass `output_parseability` because the text form has stable `file:line:col – issue` + `💡 fix` structure.

### Exit-code contract

```
exit 0  → safe (no findings or only style-level findings under threshold)
exit 1  → findings present (fix and re-run)
exit 2  → user-input-error
exit 3  → tool-environment-error (missing language tool, no source files)
```

**Audit recommendation.** Add `ubs capabilities --json` AND a `<file:line:col> --json` SARIF-flavored format that's easier to parse than the text form. (`--format=sarif` partially does this.)

---

## CASS — Coding Agent Session Search

**Repo.** `/dp/coding_agent_session_search`. Rust + tantivy + SQLite.

### `cass robot-docs guide` (excerpt — in-tool handbook)

```
guide:
  Robot-mode handbook: docs/ROBOT_MODE.md (automation quickstart)
  Output: --robot/--json; formats via --robot-format json|jsonl|compact|toon
  Logging: INFO auto-suppressed in robot mode; add -v to re-enable
  Search contract: SQLite is source of truth; lexical is the required
                   self-healing fast path; semantic is opportunistic enrichment.
  Default search: hybrid-preferred. With --robot-meta, inspect
                   requested_search_mode, search_mode, semantic_refinement,
                   fallback_tier, and fallback_reason.
  Readiness: cass health/status JSON recommended_action is authoritative;
             lexical-only fallback can be normal while semantic assets catch up.
  Doctor outcomes: branch on doctor.operation_outcome.kind (kebab-case)
                   before prose; exit_code_kind says whether the outcome is
                   success, health-failure, usage-error, lock-busy, or
                   repair-failure.
  Args: accepts --robot-docs=topic and misplaced globals; detailed errors
        with examples on parse failure
  Source control: use `cass robot-docs sources` for remote sync/setup
                  plus persistent agent-harness exclusions
  TUI drill-in contract: Enter on selected hit opens detail modal (Messages tab);
                          Enter with no selected hit falls back to query submit
  Detail modal shortcuts: / opens find, n/N cycles matches, Esc exits find
                          then closes modal, F8 opens selected hit in $EDITOR
  Safety: prefer --color=never in non-TTY; use --trace-file for spans;
          reset TUI via `cass tui --reset-state`
  Quick refs: cass --robot-help | cass robot-docs commands |
              cass robot-docs examples | cass robot-docs sources
```

This is the **rubric anchor for `📖 In-Tool-Docs`**. ~30 lines covers:
- Output formats
- Logging discipline
- Search contract
- Readiness signals
- Doctor branching
- Arg-parsing tolerance
- Safety hints
- Quick references

### `cass capabilities --json`

```jsonc
{
  "crate_version":   "0.4.1",
  "api_version":      1,
  "contract_version": "1",
  "features": [
    "json_output", "jsonl_output", "robot_meta", "time_filters",
    "field_selection", "content_truncation", "aggregations",
    "wildcard_fallback", "timeout", "cursor_pagination",
    "request_id", "dry_run", "query_explain", "view_command",
    "status_command", "state_command", "api_version_command",
    "introspect_command", "export_command", "expand_command",
    "timeline_command", "highlight_matches"
  ],
  "connectors": [
    "codex", "claude_code", "gemini", "clawdbot", "vibe",
    "opencode", "amp", "cline", "aider", "cursor", "chatgpt",
    "pi_agent", "factory", "openclaw", "kimi", "copilot",
    "copilot_cli", "qwen", "crush"
  ],
  "limits": {
    "max_limit":           0,    // 0 = no hard limit
    "max_content_length":  0,
    "max_fields":          50,
    "max_agg_buckets":     10
  }
}
```

Connectors-list is unique to cass (it indexes session formats from many agents). The `features` list is comprehensive — agents can read and adapt:

```python
caps = json.loads(subprocess.check_output(["cass", "capabilities", "--json"]))
if "robot_meta" in caps["features"]:
    use_robot_meta = True
```

### `cass --robot-meta` provenance fields

When `--robot-meta` is passed:

```jsonc
{
  "hits": [...],
  "meta": {
    "requested_search_mode": "hybrid",        // what user asked for
    "search_mode":           "hybrid",        // what actually ran
    "semantic_refinement":   true,
    "fallback_tier":         null,
    "fallback_reason":       null,
    "data_hash":             "...",
    "elapsed_ms":            42
  }
}
```

When semantic search isn't available:

```jsonc
{
  "hits": [...],
  "meta": {
    "requested_search_mode": "hybrid",
    "search_mode":           "lexical",       // degraded mode
    "semantic_refinement":   false,
    "fallback_tier":         "semantic-unavailable",
    "fallback_reason":       "semantic index rebuild in progress; eta 5min",
    "data_hash":             "...",
    "elapsed_ms":            18
  }
}
```

Agents detect degradation. **This is the rubric anchor for Operator 🪟 (Provenance-Field).** See [Q-401].

### Doctor structured outcome

```jsonc
{
  "operation_outcome": {
    "kind":           "health-failure",
    "exit_code_kind": "health-failure"
  },
  "components": {
    "sqlite":          {"state": "healthy",  "version": "..."},
    "lexical_index":   {"state": "healthy",  "size": 12345},
    "semantic_index":  {"state": "degraded", "details": "rebuild in progress", "eta_seconds": 300}
  },
  "recommended_action": {
    "command":      "cass reindex --semantic --wait",
    "rationale":    "semantic index degraded; rebuild needed for full quality",
    "is_destructive": false,
    "alternatives": [
      {"command": "cass reindex --semantic --background", "purpose": "background rebuild"},
      {"command": "cass health --watch",                  "purpose": "wait for natural recovery"}
    ]
  }
}
```

Per [Q-302] and [Q-402]. The structured `operation_outcome.kind` (kebab-case) is the agent-friendly branching point.

---

## Cross-cutting code-level patterns

These five exemplars converge on a small set of code-level idioms:

### 1. Quick-reject for hot path (dcg → Operator ⏱)

```rust
// memchr-based: 99%+ of inputs skip the slow path
fn might_be_destructive(cmd: &[u8]) -> bool {
    DANGER_TOKENS.iter().any(|t| memmem::find(cmd, t).is_some())
}
```

### 2. Two-phase analysis (bv → Operator 🪜)

```rust
fn compute_metrics(graph: &Graph) -> Metrics {
    let phase_1 = compute_cheap_metrics(graph);  // sync, < 10ms
    let phase_2 = tokio::time::timeout(
        Duration::from_millis(500),
        compute_expensive_metrics(graph)
    ).await;
    Metrics { phase_1, phase_2: phase_2.unwrap_or(Status::Timeout) }
}
```

### 3. Stable handles (am → Operator 🆔)

```rust
fn project_key(path: &Path) -> String {
    // Absolute path, canonicalized. Stable across processes.
    path.canonicalize().unwrap().to_string_lossy().into_owned()
}
```

### 4. Provenance fields (cass → Operator 🪟)

```rust
struct SearchMeta {
    requested_search_mode: SearchMode,
    actual_search_mode:    SearchMode,
    fallback_tier:         Option<&'static str>,
    fallback_reason:       Option<String>,
    data_hash:             String,
}

fn search(query: &str, requested: SearchMode) -> (Hits, SearchMeta) {
    let actual = pick_actual_mode(requested);
    let hits = run_search(query, actual);
    let meta = SearchMeta {
        requested_search_mode: requested,
        actual_search_mode:    actual,
        fallback_tier:         if actual != requested { Some("...") } else { None },
        ...
    };
    (hits, meta)
}
```

### 5. Recommended-action structured field (cass doctor → Operator 🪄)

```rust
#[derive(Serialize)]
struct DoctorReport {
    operation_outcome:  OperationOutcome,
    components:         HashMap<&'static str, ComponentHealth>,
    recommended_action: Option<RecommendedAction>,
}

#[derive(Serialize)]
struct RecommendedAction {
    command:        String,
    rationale:      String,
    is_destructive: bool,
    alternatives:   Vec<Alternative>,
}
```

These five idioms compose into 80% of what makes a CLI agent-ergonomic.

---

## Importing these patterns to a new tool

When auditing a new tool, look for the absence of these idioms:

| Pattern | Look for | If missing |
|---------|----------|------------|
| Quick-reject | memchr / fast-path filter on the hot path | Add (if hot path exists) |
| Two-phase analysis | Per-metric status fields | Add when async metrics are slow |
| Stable handles | Absolute paths or content-addressed IDs | Replace ephemeral IDs |
| Provenance fields | `meta.fallback_tier` or equivalent | Add for any tool with multi-tier capabilities |
| Recommended-action | `recommended_action` in doctor output | Add when state is reportable |

These five fixes alone often raise a tool from 600 → 800 median weighted score.

---

## Cross-references

- `methodology/LANGUAGE-RECIPES.md` — language-specific implementations of these patterns
- `methodology/MEGA-COMMAND-DESIGN.md` — mega-command shape using these idioms
- `methodology/AGENT-API-DESIGN-PRINCIPLES.md` — first-principles derivation
- `methodology/WORKED-OPERATOR-COMPOSITIONS.md` — applying multiple operators per surface
- `exemplars/CANONICAL-EXEMPLARS.md` — the 25 numbered patterns (this file's source)
