# CANONICAL-EXEMPLARS — What 750+ looks like

Five hand-built CLIs that demonstrate distinct patterns of agent-ergonomic design. Use these as the rubric anchor for "what 750+ looks like." When scoring or recommending, ask: "which of these would handle this surface, and how?"

The skill scores other CLIs against these. They are not the only good designs, but they are the most concentrated examples in the user's own toolchain.

---

## 1. dcg — Destructive Command Guard

**Repo.** `/dp/destructive_command_guard` (binary: `dcg`).

**What it does.** A pre-execution shell hook for AI coding agents that intercepts destructive commands and either blocks or allows them. Sub-millisecond hot path.

**The agent-ergonomic patterns it exemplifies.**

### Pattern 1 — Default-allow with whitelist + blacklist architecture

```
JSON Input → Parse → Quick Reject (memchr) → Normalize → Safe Patterns → Destructive Patterns → Default Allow
```

The architecture itself teaches the design philosophy: errors are never invented. If a command isn't on either list, it's allowed (default-allow). Safety isn't paranoia.

**Score evidence.** `agent_intuitiveness: 950`. The agent's first instinct (run a command) succeeds for 99%+ of inputs without any intervention.

### Pattern 2 — Error messages that teach the safe alternative

When `dcg` blocks `git reset --hard`, the message says (paraphrased): "this destroys uncommitted changes; use `git stash`, `git revert <commit>`, or back up first." The error names the EXACT alternatives, not "see docs."

**Score evidence.** `error_pedagogy: 1000`. Anchor for the rubric. Recommendations that improve error messages are scored against this bar.

### Pattern 3 — Sub-millisecond hot path with quick-reject filter

99%+ of commands skip the regex engine entirely via a memchr-based quick-reject filter. The hot path is sub-millisecond. The agent never waits.

**Score evidence.** `agent_ergonomics: 950`. Performance is part of ergonomics — slow hooks make agents wait.

### Pattern 4 — Multiple agent compatibility

Codex CLI uses stderr + exit 2 for denials; Claude Code uses stdout JSON. `dcg` adapts to both. The same binary works for every agent without configuration drift.

**Score evidence.** `composability: 900`. Cross-agent works.

### Pattern 5 — `dcg explain` introspection

The `explain` subcommand interprets the agent's intent on a blocked command and explains *why* it would be blocked. Agents can use `dcg explain '<cmd>'` to learn the rules without trial-and-error.

**Score evidence.** `self_documentation: 850`. Approaches the bar; would be 1000 if `dcg capabilities --json` existed.

---

## 2. bv — Beads Viewer (robot mode)

**Repo.** `/dp/beads_viewer` (binary: `bv`).

**What it does.** Graph-aware triage engine for beads-tracked projects. Has an interactive TUI (the default) and a parallel `--robot-*` family of flags for agent use.

**The agent-ergonomic patterns it exemplifies.**

### Pattern 6 — Mandatory `--robot-*` flags for agents

Bare `bv` launches a TUI that *blocks an automated agent*. The CLI explicitly requires `--robot-*` flags for any agent invocation. The agent-handbook says: "**CRITICAL: Use ONLY `--robot-*` flags. Bare `bv` launches an interactive TUI that blocks your session.**"

This is the canonical pattern for tools that have BOTH a human TUI and an agent surface: make the agent surface mandatory and obvious.

**Score evidence.** `composability: 900`. The TUI is gated behind explicit user invocation; agents are never trapped.

### Pattern 7 — The mega-command (`--robot-triage`)

`bv --robot-triage` is "your single entry point." It returns:
- `quick_ref`: at-a-glance counts + top 3 picks
- `recommendations`: ranked actionable items with scores, reasons, unblock info
- `quick_wins`: low-effort high-impact items
- `blockers_to_clear`: items that unblock the most downstream work
- `project_health`: status/type/priority distributions, graph metrics
- `commands`: copy-paste-ready shell commands for next steps

A single call returns *all the slices* an agent needs. No round-trip required for the canonical "what should I work on next?" question.

**Score evidence.** `agent_ergonomics: 1000`. **Anchor for the mega-command pattern.** This is the highest-leverage agent ergonomic move possible.

### Pattern 8 — Copy-paste-ready follow-up commands embedded in JSON

`bv --robot-triage`'s `commands` field is a list of *paste-ready shell strings*. The agent doesn't construct the next step; it copies and runs.

```json
"commands": [
  "br update bd-1234 --status=in_progress",
  "br show bd-1234",
  "git checkout -b bd-1234-feature"
]
```

**Score evidence.** `agent_ergonomics: 1000`. Removes the construction-step round-trip.

### Pattern 9 — `data_hash` provenance field

Every robot-mode output includes `data_hash` — a fingerprint of the source `.beads/beads.jsonl`. Downstream consumers know if the input changed.

**Score evidence.** `determinism_and_reproducibility: 950`. Stable handle pattern.

### Pattern 10 — Two-phase analysis with timing

Phase 1 (instant): degree, topo sort, density. Phase 2 (async, 500ms timeout): PageRank, betweenness, HITS. Per-metric `status` field: `computed | approx | timeout | skipped`.

The agent gets the fast results immediately and can decide whether to wait for slower ones.

**Score evidence.** `agent_ergonomics: 950`. Latency budget is explicit and per-metric.

---

## 3. am — MCP Agent Mail (Rust)

**Repo.** `/dp/mcp_agent_mail_rust` (binary: `am`).

**What it does.** MCP-based file-reservation, messaging, and identity layer for multi-agent coordination.

**The agent-ergonomic patterns it exemplifies.**

### Pattern 11 — Macros vs. granular tools as a deliberate ergonomic axis

`am` exposes:
- **Macros for speed**: `macro_start_session`, `macro_prepare_thread`, `macro_file_reservation_cycle`, `macro_contact_handshake`. One call collapses a multi-step ritual.
- **Granular tools for control**: `register_agent`, `file_reservation_paths`, `send_message`, `fetch_inbox`, `acknowledge_message`. Use when the macro doesn't fit.

This is the **macro-vs-granular** axis. Both must exist; macros must be the default.

**Score evidence.** `agent_ergonomics: 1000`. **Anchor for the macros-vs-granular pattern.**

### Pattern 12 — `project_key` as a stable handle

Every API call takes a `project_key` (the absolute path to the project). The same project at the same path always has the same key. No drift across sessions, agents, or migrations.

**Score evidence.** `determinism: 1000`. Stable handle = content-addressed identity.

### Pattern 13 — Identity friction collapsed into one call

`macro_start_session` registers the agent, ensures the project, sets up identity, and returns the session — all in one call. The friction of "do I need to register first?" is eliminated.

**Score evidence.** `agent_ergonomics: 1000`. The identity-as-friction problem is canonically solved.

### Pattern 14 — Advisory file reservations (not locks)

`file_reservation_paths` creates *advisory* leases with TTLs. Agents respect them but the leases don't prevent disk writes. This is the right model for cooperative multi-agent — failures don't deadlock.

**Score evidence.** `safety_with_recovery: 1000`. Reservations are reversible; locks aren't.

---

## 4. ubs — Ultimate Bug Scanner

**Repo.** `/dp/ultimate_bug_scanner` (binary: `ubs`).

**What it does.** Multi-language bug scanner with a strict exit-code contract.

**The agent-ergonomic patterns it exemplifies.**

### Pattern 15 — Exit-code contract: 0 = safe, ≥1 = fix

```
ubs file.rs file2.rs                    # Specific files (< 1s) — USE THIS
Exit 0 = safe; Exit ≥1 = fix and re-run.
```

The exit code IS the signal. Agents can pipeline `ubs <files> && commit` without parsing output.

**Score evidence.** `output_parseability: 1000`. **Anchor for the exit-code-contract pattern.**

### Pattern 16 — Parseable output format

```
⚠️  Category (N errors)
    file.rs:42:5 – Issue description
    💡 Suggested fix
```

Standard `file:line:col` location format. `💡` prefix on the suggested fix. Agents parse with `awk` or simple grep.

**Score evidence.** `output_parseability: 950`. Schema is informal but stable; would be 1000 with a `--json` flag pinning the same structure.

### Pattern 17 — Language filters cut runtime 3-5x

`ubs --only=rust src/` skips Python/Go/JS analyzers. Lets agents tune for hot-path performance.

**Score evidence.** `agent_ergonomics: 850`. Tuning knob is explicit + documented.

### Pattern 18 — Explicit Fix Workflow in --help

`--help` includes a numbered "Fix Workflow":

> 1. Read finding → category + fix suggestion
> 2. Navigate `file:line:col` → view context
> 3. Verify real issue (not false positive)
> 4. Fix root cause (not symptom)
> 5. Re-run `ubs <file>` → exit 0
> 6. Commit

The agent gets a step-by-step recipe in-tool. No external docs.

**Score evidence.** `self_documentation: 900`.

---

## 5. cass — Coding Agent Session Search (robot mode)

**Repo.** `/dp/coding_agent_session_search` (binary: `cass`).

**What it does.** Indexes prior agent sessions (Claude Code, Codex, Cursor, Gemini, ChatGPT, etc.) so agents can reuse solved problems.

**The agent-ergonomic patterns it exemplifies.**

### Pattern 19 — `--robot` / `--json` mandatory for non-TTY

"Never run bare `cass` (TUI). Always use `--robot` or `--json`." Same TUI-gating pattern as `bv`.

**Score evidence.** `composability: 950`.

### Pattern 20 — Stdout-data / stderr-diagnostics separation

`cass robot-docs guide` says: "stdout is data-only, stderr is diagnostics; exit code 0 means success." Strict.

**Score evidence.** `output_parseability: 1000`. **Anchor for the stdout/stderr split.**

### Pattern 21 — `cass capabilities --json` self-describing endpoint

```json
{
  "crate_version": "0.4.1",
  "api_version": 1,
  "contract_version": "1",
  "features": ["json_output", "jsonl_output", "robot_meta", ...],
  "connectors": ["codex", "claude_code", "gemini", "chatgpt", ...],
  "limits": {"max_limit": 0, "max_content_length": 0, ...}
}
```

Agents can introspect version, features, connectors, limits in one call. **Anchor for the capabilities pattern.**

**Score evidence.** `self_documentation: 1000`.

### Pattern 22 — `cass robot-docs guide` in-tool documentation

```
guide:
  Robot-mode handbook: docs/ROBOT_MODE.md (automation quickstart)
  Output: --robot/--json; formats via --robot-format json|jsonl|compact|toon
  Logging: INFO auto-suppressed in robot mode; add -v to re-enable
  Search contract: SQLite is source of truth; lexical is the required self-healing fast path; semantic is opportunistic enrichment.
  Default search: hybrid-preferred. With --robot-meta, inspect requested_search_mode, search_mode, semantic_refinement, fallback_tier, and fallback_reason.
  ...
```

Paste-ready handbook for agents. No external doc lookup. **Anchor for the in-tool-docs pattern.**

**Score evidence.** `self_documentation: 1000`.

### Pattern 23 — `--robot-meta` field as a contract pin

When called with `--robot-meta`, `cass` includes provenance fields (`requested_search_mode`, `search_mode`, `semantic_refinement`, `fallback_tier`, `fallback_reason`). Agents can interpret partial results and detect fallbacks.

**Score evidence.** `output_parseability: 1000`. Schema-pinned, drift-detectable.

### Pattern 24 — `recommended_action` field in `health`/`status` is authoritative

> "cass health/status JSON `recommended_action` is authoritative; lexical-only fallback can be normal while semantic assets catch up."

The tool tells the agent what to do next, not what the state is. Agents follow the recommendation, not interpret raw state.

**Score evidence.** `error_pedagogy: 1000` for the health command surface.

### Pattern 25 — `doctor.operation_outcome.kind` (kebab-case) for branching

> "Doctor outcomes: branch on `doctor.operation_outcome.kind` (kebab-case) before prose; `exit_code_kind` says whether the outcome is success, health-failure, usage-error, lock-busy, or repair-failure."

Machine-friendly enum first; prose second. Agents branch on the enum without parsing prose.

**Score evidence.** `output_parseability: 1000`.

---

## Cross-cutting takeaways

What these five exemplars share:

1. **Bare invocation is gated**: TUIs require explicit invocation; agent surfaces are mandatory or default-on.
2. **One mega-command per tool**: `--robot-triage`, `macro_start_session`, `<tool> capabilities --json`. The canonical agent task is one call.
3. **Exit codes carry signal**: Parseable; documented; never ad-hoc.
4. **Errors teach**: Every error names the safe alternative or the corrected form.
5. **Self-describing**: `capabilities`, `robot-docs`, `--robot-meta`. No external docs needed.
6. **Stdout/stderr split**: Stdout = data; stderr = diagnostics. Always.
7. **Stable handles**: `project_key`, `surface_id`, `data_hash`, `request_id`. Re-runnable, re-comparable.
8. **Macros and granular both exposed**: Defaults to macro for speed; granular for control.
9. **Sub-second hot paths**: Quick-reject filters, two-phase analysis, lexical-fast / semantic-opportunistic patterns.
10. **Provenance and fallback fields**: `--robot-meta` reports what mode the tool actually ran in. Agents detect graceful degradation.

These are the rubric anchors for 750–1000 scores. When in doubt, ask: "what would [exemplar X] do here?"
