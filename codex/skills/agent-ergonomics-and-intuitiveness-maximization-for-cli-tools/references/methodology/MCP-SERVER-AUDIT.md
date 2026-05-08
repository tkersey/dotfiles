# MCP-SERVER-AUDIT — Auditing MCP servers (the agent-native surface)

Many tools today are built **MCP-first** (Model Context Protocol): the agent surface IS the MCP server, and the CLI is a thin wrapper for humans / debugging. This file extends the methodology for MCP server audits.

The 11 dimensions still apply, but with adapted anchors:

- A "verb" is an **MCP tool**.
- A "flag" is an **MCP tool argument**.
- A "verb's `--help`" is the **MCP tool's `description` + `inputSchema`**.
- An "exit code" doesn't apply to MCP (use error codes in the response instead).

---

## Pre-audit: identify MCP surface

In `phase0_scope_decision.md`:

```yaml
target_kind: mcp_server
target_path: /dp/mcp_agent_mail_rust
mcp_transport: stdio | sse | http
companion_cli_path: /dp/mcp_agent_mail_rust   # (same repo; CLI binary is `am`)
canonical_tasks:
  - "Reserve a file glob with TTL"
  - "Send a threaded message"
  - "Start a session via macro"
```

For tools with both an MCP server AND a CLI, audit both surfaces (see WORKED-EXAMPLES.md § am).

---

## Phase 1 — MCP surface inventory

For an MCP server, the surfaces are:

1. **MCP tools** — each tool has a name, description, and input schema. Inventory each.
2. **MCP resources** — read-side endpoints (`resource://`).
3. **MCP prompts** — server-provided prompt templates.
4. **Server metadata** — server name, version, capabilities (which methods supported).
5. **Auth surfaces** — if the server uses auth (JWT, OAuth, API key).

Inventory record schema:

```jsonc
{
  "surface_id":     "mcp_tool__macro_start_session",
  "kind":           "mcp_tool" | "mcp_resource" | "mcp_prompt" | "auth",
  "name":           "macro_start_session",
  "description":    "...",                       // from tools/list response
  "input_schema":   { /* JSON schema */ },
  "output_shape":   { /* observed output shape */ },
  "mutates":        false,
  "side_effects":   ["registers_agent", "ensures_project"],
  "rate_limited":   false,
  "auth_required":  true
}
```

---

## Phase 2 — MCP-adapted scoring

The 11 dimensions translate to MCP context:

### 1. agent_intuitiveness (MCP)

> "Would the first tool an agent guesses succeed?"

Rubric anchors:

- 0: tool name is obscure (`__internal_v2_handler`)
- 500: tool name follows verb-ish naming (`registerAgent`)
- 750: tool name is a verb and matches the canonical task name (`register_agent`)
- 1000: macro covers the canonical task (`macro_start_session`)

### 2. agent_ergonomics (MCP)

> "Min calls to complete the canonical task."

- 0: 5+ calls
- 750: 1-2 calls (with macros + sensible defaults)
- 1000: 1 call (macro collapses identity friction; **am pattern anchor**)

### 3. agent_ease_of_use (MCP)

> "Can the agent introspect tools without external docs?"

- MCP `tools/list` returns description + input schema → 750+ baseline
- Plus tool `description` includes examples → 1000

### 4. output_parseability (MCP)

> "Is the tool's response a stable, schema'd JSON?"

- MCP tools always return JSON (no parseability concern at transport layer)
- Score on schema stability: pinned schema → 1000; per-call drift → 200

### 5. error_pedagogy (MCP)

> "Does the error response teach?"

- MCP error format: `{ "error": { "code": -32602, "message": "...", "data": {} } }`
- Score 1000 if `data.suggestion` field names the corrected tool/arg
- Score 0 if just `"message": "Invalid request"`

### 6. intent_inference (MCP)

> "Does the server tolerate near-miss tool names / arg names?"

- 0: typo in tool name → silent_fail
- 500: typo → useful_hint suggesting correct name (via `tools/list`)
- 1000: typo → server proceeds + warns (rare; usually tool names must match exactly)

### 7. safety_with_recovery (MCP)

> "Mutating tools have explicit confirmation pattern?"

- MCP tools that mutate should have an `acknowledge` pattern OR require an explicit `confirm: true` arg
- am pattern: file reservations are advisory leases (recoverable) → 1000
- A tool that deletes records on first call → 0

### 8. determinism_and_reproducibility (MCP)

> "Same input → same output?"

- Idempotent tools score 1000
- Tools that include wall-clock timestamps in primary output (not just metadata) → 500

### 9. self_documentation (MCP)

> "Server provides capability introspection?"

- 0: no `capabilities/list` or equivalent
- 750: MCP server advertises its capabilities + tool list
- 1000: + per-tool examples in description, plus a server-info resource

### 10. composability (MCP)

> "Can tool results be passed to another tool without parsing?"

- MCP tools natively return JSON; composability is high by default
- Score on shared schema across tool families (e.g. all "fetch_*" tools return `{items: [...]}`)

### 11. regression_resistance (MCP)

> "Schema-pin tests for tool responses?"

- Pattern 9 from REGRESSION-TEST-PATTERNS.md applies here too

---

## Phase 3 — MCP intent corpus

The "naive agent" for MCP is an agent calling `tools/list` and trying to use the discovered tools. The "savvy agent" knows the server's source.

Generate corpus:

```jsonc
{
  "corpus_id": "mcp-naive-01",
  "generator": "naive",
  "category": "tool_name_typo",
  "invocation": {
    "tool": "register_agent_v2",   // typo of register_agent
    "args": {...}
  },
  "predicted_outcome": "useful_hint"
}
```

Run via the MCP transport (stdio JSON-RPC or HTTP):

```bash
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"register_agent_v2","arguments":{}}}' | mcp-server
# server response → classify outcome
```

---

## MCP-specific recommendations (often P1)

When auditing an MCP server, these recs are usually high priority:

### MR-1: Add macro tools

If the server only has granular tools (`register_agent`, `ensure_project`, `start_session`) and no macros, add `macro_*` tools that collapse common rituals. (am Pattern 11; [Q-201].)

### MR-2: Add `capabilities` MCP resource

Even though MCP has `tools/list`, add a `resource://capabilities` returning the same capabilities JSON the CLI exposes. Cross-platform consistency.

### MR-3: Schema-pin tool input/output

Each tool's `inputSchema` should be tested for stability. Add regression tests that verify the schema across versions.

### MR-4: Document in `description` what each error code means

```jsonc
{
  "name": "send_message",
  "description": "Send a threaded message to another agent.\nErrors: -32602 (invalid args), -32000 (recipient not found), -32001 (rate limited)."
}
```

Agents reading the description know what to expect.

### MR-5: Add idempotency keys for mutating tools

```jsonc
{
  "name": "send_message",
  "inputSchema": {
    "properties": {
      "idempotency_key": {"type": "string", "description": "Optional; SHA256 of payload. Tool deduplicates if same key seen."}
    }
  }
}
```

Agents can retry safely.

---

## MCP server's `capabilities` schema

Beyond MCP's standard `tools/list`, ship a richer `capabilities` resource:

```jsonc
{
  "server_name":     "mcp-agent-mail",
  "server_version":  "0.4.1",
  "mcp_version":     "1.0",
  "contract_version": "1",
  "tools": {
    "macro_start_session": {
      "description": "Collapse identity friction.",
      "deprecated":  false,
      "stable":      true,
      "rate_limited": false
    },
    /* per-tool */
  },
  "resources": {
    "resource://inbox/{agent}":    {"description": "...", "stable": true},
    "resource://thread/{id}":      {"description": "...", "stable": true}
  },
  "errors": {
    "-32602": {"meaning": "invalid args", "retryable": false},
    "-32000": {"meaning": "recipient not found", "retryable": false},
    "-32001": {"meaning": "rate limited", "retryable": true}
  },
  "limits": {
    "max_concurrent_agents": 64,
    "max_message_size_bytes": 65536
  }
}
```

---

## MCP-CLI parity audit

For tools with both MCP + CLI surfaces (am, mcp-server-* family):

For every CLI verb, there should be an MCP tool with similar capability — and vice versa. The audit checks parity.

```jsonc
{
  "kind": "parity_check",
  "cli_verb":  "send",
  "mcp_tool":  "send_message",
  "parity_status": "aligned" | "cli_only" | "mcp_only" | "divergent_args"
}
```

Recommendations close parity gaps:

```jsonc
{
  "recommendation_id": "P-001",
  "title": "CLI's `am send` needs `--thread-id` flag (MCP send_message has it)",
  "scope": "parity",
  "diff_sketch": "..."
}
```

---

## Auditing MCP transport

Transports differ:

| Transport | Notes |
|-----------|-------|
| stdio | Easy to audit (pipe JSON-RPC). Default for many MCP clients (Claude Desktop, etc.). |
| sse | Server-sent events; audit reconnection behavior, line-buffering. |
| http | Audit auth, CORS, rate limiting, request-id propagation. |

Phase 1 should inventory transport-specific concerns:

- Does the server emit a heartbeat? (Cross-ref OBSERVABILITY-AND-TELEMETRY-SURFACES.md.)
- Does stdio handle backpressure?
- Does HTTP set proper status codes (400 for bad-input, 500 for server-error)?

---

## Auth surfaces

If the MCP server has auth:

- Auth method documented in capabilities
- Auth errors return `data.suggestion` field naming the canonical login flow
- Tokens have expiry; surfaced in capabilities

```jsonc
{
  "auth": {
    "method": "jwt",
    "issuer_url": "https://example.com/auth",
    "expiry_seconds": 3600,
    "refresh_supported": true,
    "loop_friendly": true
  }
}
```

---

## MCP-aware regression tests

Test the MCP tool calls via stdio:

```bash
# audit/regression_tests/MCP-001__macro_start_session_idempotent.test.sh
set -euo pipefail
SERVER="${MCP_SERVER:-./target/release/mcp-agent-mail}"

call() {
  echo "$1" | "$SERVER" 2>/dev/null
}

req='{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"macro_start_session","arguments":{"project_key":"/tmp/test"}}}'

resp1=$(call "$req")
resp2=$(call "$req")

# Idempotent: both responses should be identical (or differ only in request_id / timestamp)
norm() { jq 'del(.id, .result.meta.request_id, .result.meta.ts_iso)' <<< "$1"; }
[ "$(norm "$resp1")" = "$(norm "$resp2")" ] || {
  echo "FAIL: macro_start_session not idempotent" >&2; exit 1; }

echo OK
```

---

## Worked example: am (MCP Agent Mail)

Already covered in WORKED-EXAMPLES.md § Worked Example 3. Key points:
- Macros are the rubric anchor for `agent_ergonomics: 1000` (`macro_start_session`)
- Granular tools provide control escape hatch
- Stable handles via `project_key` (absolute path)
- Advisory file reservations (Pattern 14)

---

## Anti-patterns specific to MCP

- **Tool names that aren't verbs.** `entity_handler_v2` instead of `add_entity`.
- **Hidden side effects.** A "read" tool that registers the caller behind the scenes.
- **Long-running tools without progress.** Block forever; agents time out.
- **Per-call schema drift.** Tool returns different shapes based on undocumented args.
- **MCP-CLI capability divergence.** CLI has `am send --priority=high` but MCP `send_message` lacks priority.
- **Unbounded results.** Tool returns 100,000 records in one call without pagination.
- **Tool descriptions in marketing-speak.** "Powerful, intuitive..." vs "Sends a threaded message."

---

## Related

- `references/exemplars/CANONICAL-EXEMPLARS.md` § am (MCP exemplar)
- `methodology/JSON-SCHEMA-PATTERNS.md` (MCP responses are JSON)
- `methodology/MEGA-COMMAND-DESIGN.md` (macro tools = MCP mega-commands)
- `/mcp-server-design` skill for MCP-specific design patterns
