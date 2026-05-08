# MEGA-COMMAND-DESIGN — A Library of Agent-Friendly Mega-Calls

> "When three round-trips can collapse into one, build the mega-command. When the mega-command can name the next three round-trips inside its output, ship it." — design rule extracted from `bv --robot-triage` and `cass capabilities --json`.

A **mega-command** is a single invocation that returns multiple useful slices in one call: data + recommendations + follow-up commands + provenance. It is the highest-leverage agent-ergonomic move available — see Operator `Σ` in OPERATORS.md.

This file catalogues the canonical mega-command shapes, when to use each, and the JSON schema templates to copy.

---

## Why mega-commands matter (in concrete agent terms)

A typical canonical task with non-mega-command CLI:

```
agent: tool status
agent: tool list --json
agent: tool list --filter ready --json
agent: tool show 1234 --json
agent: tool plan 1234 --json
[agent does the work]
agent: tool update 1234 --status in_progress
agent: tool close 1234
```

7 round-trips. With a `--robot-triage` mega-command and follow-up `commands` field:

```
agent: tool --robot-triage
[ output includes recommendations, top 3 picks, copy-paste commands ]
agent: <copy first command from output>
[ work ]
agent: <copy close command from output>
```

3 round-trips. ~60% reduction in round-trips for the canonical task.

---

## The four canonical mega-command shapes

### Shape 1 — TRIAGE (recommendation engine)

Returns "what should I work on next, why, and how do I claim it?"

**Anchor.** `bv --robot-triage` (see [Q-200] in QUOTE-BANK.md).

**Schema template:**

```jsonc
{
  "tool_version": "0.4.1",
  "contract_version": "1",
  "data_hash": "abc123",                    // fingerprint of inputs
  "as_of": "2026-05-06T12:00:00Z",          // honor SOURCE_DATE_EPOCH
  "quick_ref": {
    "summary": "12 ready / 4 blocked / 23 total",
    "top_3": [
      {"id": "X-001", "score": 0.92, "reason": "highest impact + ready"},
      {"id": "X-007", "score": 0.81, "reason": "unblocks 3 downstream"},
      {"id": "X-013", "score": 0.74, "reason": "quick win"}
    ]
  },
  "recommendations": [
    {
      "id": "X-001",
      "title": "...",
      "score": 0.92,
      "reason_components": {"impact": 0.7, "ready": 1.0, "effort": 0.3},
      "unblocks": ["X-005", "X-009"]
    }
  ],
  "quick_wins": [...],                      // low-effort high-impact
  "blockers_to_clear": [...],               // most-downstream unblocking
  "project_health": {
    "ready_count": 12,
    "blocked_count": 4,
    "stale_count": 2,
    "graph_metrics": {"...": "..."}
  },
  "commands": [                             // copy-paste-ready follow-ups
    "tool claim X-001",
    "tool show X-001",
    "tool plan X-001"
  ],
  "warnings": []                            // anomalies the agent should know about
}
```

**When to use.** Any tool that recommends work ranked by graph properties or scoring (issue trackers, task graphs, build queues, dependency systems).

**When NOT to use.** Pure data-fetch tools where there's no "what's next" choice (a `cat` clone). The shape misleads agents into asking for recommendations that don't exist.

### Shape 2 — STATUS / DIAGNOSE (the doctor)

Returns "what state is everything in, what's wrong, what should I do?"

**Anchor.** `cass health` and `cass doctor` ([Q-302], [Q-402]).

**Schema template:**

```jsonc
{
  "tool_version": "0.4.1",
  "contract_version": "1",
  "data_hash": "abc123",
  "operation_outcome": {
    "kind": "success" | "health-failure" | "usage-error" | "lock-busy" | "repair-failure",
    "exit_code_kind": "success" | "health-failure" | "usage-error" | "lock-busy" | "repair-failure"
  },
  "components": {
    "<component_a>": {"state": "healthy", "version": "...", "details": null},
    "<component_b>": {"state": "degraded", "details": "lexical-only fallback active"},
    "<component_c>": {"state": "unhealthy", "error": "...", "since": "..."}
  },
  "recommended_action": {                  // CRITICAL: the tool tells the agent what to do
    "command": "tool repair --component=<component_c>",
    "rationale": "component_c has been unhealthy for >5 min",
    "is_destructive": false,
    "alternatives": [
      {"command": "tool diagnose --component=<component_c> --verbose", "purpose": "investigate first"}
    ]
  },
  "fallbacks_active": [                    // PROVENANCE: where degraded modes are running
    {"component": "search", "active_mode": "lexical", "preferred_mode": "hybrid", "reason": "semantic-index-rebuild-in-progress"}
  ],
  "warnings": [],
  "next_check_after_seconds": 60
}
```

**When to use.** Any tool with state across runs: stateful daemons, indexes, caches, distributed components. Tools that have a `doctor`, `status`, `health`, or `info` subcommand.

**When NOT to use.** Stateless filters and converters (jq, sort). They have nothing to "diagnose."

### Shape 3 — PLAN (dependency-aware execution proposal)

Returns "given these N items, here is the parallelizable execution plan."

**Anchor.** `bv --robot-plan`.

**Schema template:**

```jsonc
{
  "tool_version": "0.4.1",
  "data_hash": "...",
  "plan": {
    "tracks": [                              // each track is independent (parallel-safe)
      {
        "id": "track-1",
        "items": [
          {"id": "X-001", "estimated_effort": "S"},
          {"id": "X-005", "estimated_effort": "M", "depends_on_in_track": ["X-001"]}
        ]
      },
      {
        "id": "track-2",
        "items": [...]
      }
    ],
    "summary": {
      "total_items": 12,
      "parallel_tracks": 3,
      "highest_impact": "X-001",
      "longest_chain": ["X-007", "X-013", "X-021"],
      "estimated_total_effort": "L"
    },
    "blocked_by_external": [
      {"id": "X-099", "external_dep": "design-review-pending"}
    ]
  },
  "commands": [
    "tool claim X-001 X-007 X-013",
    "tool start track-1"
  ]
}
```

**When to use.** Tools that track work-with-dependencies (build systems, test runners, dependency graphs, task graphs).

**When NOT to use.** Tools where ordering is implicit (most filters and converters).

### Shape 4 — CAPABILITIES (the contract)

Returns "what does this tool do, what version, what surfaces, what limits?"

**Anchor.** `cass capabilities --json` ([Q-501]).

**Schema template:**

```jsonc
{
  "tool_name": "mytool",
  "version": "0.4.1",
  "api_version": 1,
  "contract_version": "1",
  "features": ["json_output", "robot_meta", "levenshtein_typo_hint", "deterministic_output"],
  "commands": {
    "<verb>": {
      "description": "...",
      "mutates": false,
      "json": true,
      "robot": "--json",
      "args": [{"name": "<arg>", "required": true, "type": "string"}],
      "flags": [{"name": "--limit", "type": "int", "default": 100}],
      "exit_codes": [0, 1, 3]
    }
  },
  "exit_codes": {
    "0": {"meaning": "success", "retryable": false},
    "1": {"meaning": "user-input-error", "retryable": false},
    "2": {"meaning": "safety-block", "retryable": false},
    "3": {"meaning": "tool-environment-error", "retryable": true},
    "4": {"meaning": "transient-failure", "retryable": true}
  },
  "env_vars": {
    "MYTOOL_HOME":  {"description": "Config dir", "default": "$XDG_CONFIG_HOME/mytool"},
    "MYTOOL_ROBOT": {"description": "Force --robot mode", "default": "unset"}
  },
  "limits": {
    "max_items_per_list": 10000,
    "max_concurrent_writers": 4,
    "default_timeout_seconds": 30
  },
  "schemas_uri": "tool schema --json",   // pointer to schema export
  "robot_docs_uri": "tool robot-docs guide"
}
```

**When to use.** Always. Every CLI should ship a capabilities endpoint. This is table stakes.

---

## Decision tree: which mega-command to add

```
Is the tool stateful (has state across runs)?
├── YES → add STATUS/DIAGNOSE (Shape 2)
└── NO  → skip Shape 2

Does the tool produce ranked recommendations / "what next" choices?
├── YES → add TRIAGE (Shape 1)
└── NO  → skip Shape 1

Does the tool track dependencies between work items?
├── YES → add PLAN (Shape 3)
└── NO  → skip Shape 3

Always add CAPABILITIES (Shape 4) — no exceptions.
```

If a tool has more than one applicable shape, the **best** answer is to:
1. Pick the most-canonical-task shape and make it the default mega-command (e.g. `<tool> --robot-triage`).
2. Expose the others as named subcommands (e.g. `<tool> doctor --json`, `<tool> plan --json`).
3. Cross-reference them in capabilities and robot-docs guide.

---

## The `commands` field — copy-paste-ready follow-ups

The single highest-leverage feature inside a mega-command output is the `commands` field. It's the difference between "agent has data" and "agent has the next move."

**Bad (forces construction):**

```json
{ "recommendations": [{"id": "X-001"}] }
```
Agent must know that the next move is `<tool> claim X-001` and the syntax for it.

**Good (paste-ready):**

```json
{
  "recommendations": [{"id": "X-001"}],
  "commands": [
    "tool claim X-001",
    "tool show X-001 --json"
  ]
}
```
Agent copies the first string and runs.

**Even better (annotated):**

```json
{
  "commands": [
    {"action": "claim", "command": "tool claim X-001", "destructive": false},
    {"action": "show",  "command": "tool show X-001 --json", "destructive": false},
    {"action": "skip",  "command": "tool skip X-001 --reason '<reason>'", "destructive": false, "requires_input": ["reason"]}
  ]
}
```
Agent can branch on `action`, knows which require input filling.

---

## Latency budget

Mega-commands should be **fast on the canonical path** even if they expose slow analyses:

- Two-phase pattern (see `bv` Pattern 10): emit the cheap slices first (sync), then expensive ones (async with timeout) with per-metric `status: computed | approx | timeout | skipped`.
- Use a quick-reject pre-filter (memchr-style) for hot-path tools.
- Cache expensive computations behind `data_hash` — return cached result if hash unchanged.

Target: < 1 second for the canonical mega-call on cold cache; < 100 ms on warm cache.

```jsonc
{
  "data_hash": "abc123",
  "phase_1": { "ready_count": 12, "status": "computed_ms_3" },
  "phase_2": {
    "pagerank":     { "values": {...}, "status": "computed_ms_240" },
    "betweenness":  { "values": null, "status": "timeout_ms_500", "reason": "exceeded budget" },
    "centrality":   { "values": null, "status": "skipped",        "reason": "user opted out" }
  }
}
```

Agents can read partial results and decide whether to wait for more.

---

## The "warnings" field

Every mega-command should have a `warnings` array (often empty). Use it to surface non-fatal issues the agent should know about:

```jsonc
{
  "warnings": [
    {"code": "stale_index", "message": "search index is 4 hours stale; rebuild via 'tool reindex'"},
    {"code": "config_deprecation", "message": "config key 'old_name' deprecated; rename to 'new_name'"}
  ]
}
```

Distinguish from errors: warnings don't change the exit code; errors do.

---

## Anti-patterns

### Anti-1: Returning data without recommendations

```jsonc
{ "items": [...] }   // ❌ — agent must figure out what to do
```

vs.

```jsonc
{
  "items": [...],
  "recommendations": [...],
  "commands": [...]
}
```

### Anti-2: Returning recommendations without commands

```jsonc
{ "recommendations": [{"id": "X-001"}] }   // ❌ — agent must construct command
```

### Anti-3: Mega-command with no data_hash

```jsonc
{ "items": [...] }   // ❌ — agent can't detect drift
```

vs.

```jsonc
{ "items": [...], "data_hash": "abc123" }
```

### Anti-4: Mixing data and prose

```jsonc
{
  "items": [...],
  "explanation": "I see you have 12 items. Here are the top 3..."   // ❌
}
```

Prose belongs in `robot-docs guide`, not in mega-command output. The mega-command is data-only.

### Anti-5: Inconsistent envelope across mega-commands

If `triage` returns `{ "recommendations": [...] }` but `plan` returns `{ "data": { "tracks": [...] } }`, agents need separate parsers per call. Use a consistent top-level envelope:

```jsonc
{
  "ok": true,
  "tool_version": "...",
  "data_hash": "...",
  "data": {
    /* the slice — whether triage, plan, status, capabilities */
  },
  "warnings": [],
  "commands": []
}
```

### Anti-6: Mega-command that requires authentication / network

If `tool --robot-triage` makes a network call, an offline agent gets stuck. Mega-commands should work offline OR clearly document network requirements in `capabilities`.

### Anti-7: Mega-command name that doesn't include "robot" or "json"

If the canonical agent invocation is just `<tool> triage` (no `--robot-*` / `--json` mandatory), agents will guess wrong. Make the agent-targeted shape explicit:

- ✅ `<tool> --robot-triage`
- ✅ `<tool> triage --json`
- ❌ `<tool> triage` (returns TUI / human-only output)

Per [Q-100]: "Use ONLY `--robot-*` flags. Bare `<tool>` launches an interactive TUI that blocks your session."

---

## Implementing a mega-command

### Step 1 — define the shape

Pick from the four canonical shapes. Sketch the JSON output before writing code.

### Step 2 — implement the data layer

Build the data the mega-command needs. Cache aggressively; many of these slices are derivable from the same underlying data.

### Step 3 — wire the verb

```bash
# Rust: a clap subcommand returning the JSON
mytool --robot-triage          # global flag form (preferred for top-level)
mytool triage --json           # subcommand form (alternative)
```

### Step 4 — populate the `commands` field

For every recommendation in the output, derive the canonical follow-up command(s). This is the highest-impact part of the implementation. Don't return recs without commands.

### Step 5 — pin the schema

Add a regression test: `audit/regression_tests/mega-command-schema-pin.test.sh` validates `--robot-triage --json` output has all required keys.

### Step 6 — document in capabilities

`capabilities.commands` is keyed by **verb name**, not flag. So if your mega-command is exposed BOTH as `tool triage --json` (subcommand form) AND `tool --robot-triage` (global-flag shortcut), document the subcommand under `commands` and the flag under a global `flags` section:

```jsonc
{
  "commands": {
    "triage": {
      "description":     "Mega-command: ranked recommendations + commands + project_health.",
      "mutates":         false,
      "json":            true,
      "robot":           "--json",
      "is_mega_command": true,
      "schema_uri":      "tool schema --command=triage --json"
    }
  },
  "flags": {
    "global": {
      "--robot-triage": {
        "description": "Shortcut for `tool triage --json`",
        "alias_for":   "triage --json"
      }
    }
  }
}
```

If you only ship one form (subcommand only OR global-flag only), document only that one.

### Step 7 — link from `robot-docs guide`

```
Mega-call: `mytool --robot-triage` returns recommendations + commands + health in one call.
Quick refs: `mytool capabilities --json`
```

---

## Worked example: adding `--robot-triage` to a typical task tracker

**Before (no mega-command).** Agent's canonical task: "find next item to work on, claim it, start work."

```
$ tool status
Open: 12 / Closed: 30
$ tool list --json | jq '.[] | select(.ready==true) | .id'
"X-001" "X-007" ...
$ tool show X-001 --json
{ ... full record ... }
$ tool plan X-001 --json
{ ... }
$ tool claim X-001 --status in_progress
```

5 round-trips before any work happens.

**After.**

```
$ tool --robot-triage
{
  "data_hash": "abc",
  "quick_ref": {"top_3": [{"id":"X-001","score":0.92,"reason":"unblocks 3"}]},
  "recommendations": [{"id":"X-001",...}],
  "commands": [
    "tool show X-001 --json",
    "tool claim X-001"
  ]
}
$ tool show X-001 --json     # paste from output
$ tool claim X-001           # paste from output
```

3 round-trips, no constructed commands.

---

## Recipes per language

See **LANGUAGE-RECIPES.md** for framework-specific scaffolding. The key shapes:

- **Rust + clap**: a top-level `--robot-triage` global flag detected in `main()` before subcommand dispatch
- **Go + cobra**: a custom `cobra.Command` named `--robot-triage` registered on root
- **Python + argparse / click / typer**: a top-level subcommand or a flag with a callback
- **TypeScript + commander / yargs**: middleware on the root command
- **Bash**: a `case "$1"` branch that emits the JSON heredoc

---

## Pin to your project

Once a mega-command exists:

1. Document it in `capabilities --json` AND `robot-docs guide`.
2. Add it to `--help` under an "AGENT/AUTOMATION" section.
3. Pin it in `audit/regression_tests/` with a schema-pin test.
4. Reference it in your project's README under "For agents:" — drives adoption.
5. Update the canonical-task list (`audit/canonical_tasks.md`) to reflect the new round-trip count.

The mega-command is the single best uplift Phase 5 can deliver.
