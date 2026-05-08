# AGENT-API-DESIGN-PRINCIPLES — First-principles for designing any agent-facing API

The 11 dimensions are *measurable* properties of an existing API. This file gives the *generative* first-principles you'd use to design one from scratch (or refactor one mid-pass).

If the rubric tells you what to score, this file tells you why those things matter.

Pulled from `/mcp-server-design`, dcg/bv/am/ubs/cass design choices, and the LLM agent literature on tool use.

---

## The agent's working memory model

Agents operate on bounded context windows. A canonical agent has:

- **Short-term working memory** — what's in the current message thread; the last 50–100 tool calls; constantly compacted
- **Long-term memory** — persistent across sessions (CLAUDE.md, AGENTS.md, /cm Claude memory, /cass session search)
- **Tool catalog** — what tools/CLIs/MCP servers it has access to

API design implications:

1. **Every tool call is expensive** — round-trips, tokens, cognitive overhead. Mega-commands collapse round-trips (Operator Σ).
2. **Outputs eat working memory** — return less, more structured. Sparse fields, pagination, `--limit`. Agents usually need IDs + 2–3 fields, not the full payload.
3. **Agents forget tool conventions across sessions** — the API must teach itself every time. `capabilities --json` is the canonical "remind me what this tool does" surface.
4. **Agents read top-down** — `--help`'s first 10 lines matter most. The AGENT/AUTOMATION footer is read AFTER usage examples — bury it and it gets missed.

---

## The "first-try inevitability" principle (operationalized)

> Design every surface so the FIRST thing an agent instinctively tries "just works."

Inevitability has three components:

### 1. Naming inevitability

Verb / flag names match the agent's prior expectation. Sources of expectation:

- **POSIX conventions** (`--help`, `-h`, `--version`, `-V`, `--quiet`, `-q`)
- **Modern tool conventions** (`--json`, `--no-color`, `--dry-run`, `--yes`)
- **Family conventions** (e.g. `cargo X` family: `cargo audit`, `cargo deny`, all expose `--json`)
- **Dictionary expectations** (`list` not `enumerate`; `delete` not `purge`; `add` not `insert`)
- **Symmetry** (if `add` exists, `remove` is more expected than `delete`)

When you choose a name, ask: "what would the agent guess first?" That's the canonical name. Aliases for popular alternatives.

### 2. Behavior inevitability

The default behavior matches the agent's prior expectation:

- Bare invocation does something useful (or guides toward `--help`).
- Read-side verbs are read-side (no hidden side effects).
- `--json` produces valid JSON on stdout (not pretty-printed terminal art).
- Empty input → empty array (not error, not silent_fail).
- Repeat invocation = idempotent (Operator 🧷).

When defaults diverge from agent expectation, document the divergence at top of `--help` AND in `capabilities`.

### 3. Output inevitability

The output shape matches the agent's prior expectation:

- JSON is in the **Universal Envelope**: `{ok, data, meta, warnings, commands}` — see JSON-SCHEMA-PATTERNS.md
- Errors include `did you mean` for common typos
- Doctor / status verbs include `recommended_action`
- Mega-commands include `commands` field with paste-ready follow-ups
- Provenance fields (`data_hash`, `search_mode`, `fallback_tier`) are present when degradation possible

---

## The "no telepathy required" principle

Agents shouldn't need to know undocumented behavior to use the tool correctly. Concretely:

- Every flag mentioned in the source is documented in `capabilities`
- Every exit code site has a documented meaning
- Every error message names the safe alternative
- Every undocumented behavior IS a finding (Phase 2 will score it low on `self_documentation`)

The complement: **telepathy is optional but rewarded**. Agents that DO know the tool deeply benefit from advanced features (`--robot-meta` for provenance, `--from-stdin` for bulk, etc.). But the canonical task should require zero prior knowledge.

---

## The "least-surprise-on-failure" principle

Agents handle failure differently from humans. When something goes wrong:

- Humans iterate visually; agents iterate via parsed signals
- Humans accept ambiguity; agents need explicit branches
- Humans tolerate latency; agents have timeout budgets
- Humans backtrack on intuition; agents backtrack on exit codes

Design for the agent failure model:

| Concern | Agent expectation |
|---------|-------------------|
| Exit code | Documented; consistent across versions; branch-on-able (e.g. `[ $? -eq 4 ] && retry`) |
| Stderr | Has machine-readable error code + `did you mean` + `safe alternative` |
| Stdout | Empty on failure (so jq doesn't get confused) OR contains an `ok: false` envelope |
| Timeout | Documented; tool emits heartbeats so agent knows it's alive |
| State | If mid-state on failure, the agent can introspect via `<tool> doctor --json` |

The least-surprise failure model is more important than the least-surprise happy path, because failures are when agents lose the most time.

---

## The "graceful degradation" principle

Modern tools have multi-tier capabilities (lexical + semantic search; cache + remote fetch; sync + async metrics). When a tier is unavailable:

- **Don't fail entirely** — emit best-effort with provenance
- **Tell the agent what mode actually ran** — Operator 🪟 (Provenance-Field)
- **Tell the agent what would unlock the better tier** — `recommended_action: "rebuild semantic index via mytool reindex"`
- **Don't pretend nothing changed** — agents may build downstream logic on the result

This is why `cass --robot-meta` returns `requested_search_mode`, `search_mode`, `fallback_tier`, `fallback_reason`. Agents see the degradation AND know what to do about it.

---

## The "minimum viable surface" principle

Each tool should expose the smallest agent-facing surface that covers its canonical tasks. Don't:

- Add a verb because "someone might want it" — wait until 3+ canonical tasks need it
- Add a flag because "it's symmetric with another tool" — symmetry is good but proliferation is worse
- Document undocumented commands — if it's not documented, it shouldn't exist (delete or document)
- Ship multiple ways to do the same thing — pick one canonical form, alias the others

Smaller surface = faster mastery = lower onboarding curve (Operator 🎓).

---

## The "explicit > implicit" principle

Agents struggle with implicit conventions. Where humans tolerate ambiguity ("this is probably what you mean"), agents need explicit signals:

| Implicit (bad) | Explicit (good) |
|----------------|------------------|
| Color enabled by default | `--color=auto\|never\|always` (auto = explicit detection rules) |
| Pager invoked on long output | `--pager=auto\|never` |
| Prompt for confirmation | `--yes` required for destructive |
| Assume current dir | `--target=.` documented as default |
| Implicit timestamps | Honor `SOURCE_DATE_EPOCH`; document |
| Implicit ordering | Document or sort |

The explicit form is harder for humans (more typing) but agent-friendlier. For human ergonomics, keep the implicit defaults but make the explicit override available + documented.

---

## The "deterministic by default" principle

Agents trust outputs to be reproducible. Sources of non-determinism that agents trip on:

- Hashmap iteration order (Go `map` ranges, Rust `HashMap` non-default)
- Wall-clock timestamps in non-JSON output
- Random IDs (UUIDs, request IDs not seeded)
- Async metric computation that runs to "best effort" then reports varying results
- Per-locale formatting (number separators, dates)

Deterministic-by-default means:

- Sort iteration before serialization (or document insertion-order)
- Timestamps go in `meta.ts_iso` JSON field; never in prose
- IDs are content-addressed where possible; otherwise documented as volatile
- Async metrics report `status: computed | timeout | skipped` so agents can branch
- Honor `LC_ALL=C` for output formatting

When the user wants non-determinism (`--random` flag, network-dependent results), make it explicit with `--seed` and provenance fields.

---

## The "machine-first, human-second" principle

For modern CLIs that will be used by both humans and agents, design the machine-readable surface FIRST, then layer the human-readable surface on top:

```
1. Define capabilities --json schema
2. Define per-verb output schemas
3. Define error code taxonomy
4. Implement the verbs to produce the JSON
5. Render JSON → human-readable for terminal use (when not --json)
```

Tools designed human-first then retrofit for agents always have parity gaps. Tools designed machine-first then rendered for humans don't.

This is the inverse of the historical pattern (most pre-2020 CLIs are human-first). It's a recent best practice.

---

## The "discoverable-from-stdin" principle

Many agents want pipelines:

```
mytool list --json | jq '.items[]' | mytool annotate --from-stdin --json
```

Tools that support `--from-stdin` (or the equivalent `-` argument convention) become composable. Tools that don't force agents into shell loops:

```
for id in $(mytool list --json | jq -r '.items[].id'); do
  mytool annotate "$id"
done
```

The shell-loop pattern is per-call overhead × N. The `--from-stdin` pattern is one call. Operator 🧶.

---

## The "reservation-instead-of-lock" principle

For multi-agent coordination:

- **Locks** prevent disk writes; failure deadlocks
- **Reservations** are advisory leases with TTLs; agents respect them but failure recovers naturally

The MCP Agent Mail (`am`) pattern is reservations, not locks. Apply this to any tool where multiple agents might compete:

- File reservations (per `agent-mail` or `slb`)
- Lock-busy errors return `exit 4 (transient-failure)` with a `recommended_action: "wait <N>s and retry"`
- TTL is documented; agents can respect it
- Force-unlock requires explicit `--force-unlock` with safety warnings

Operator 🧷 (Idempotency-Pin) makes retries safe.

---

## The "sub-second hot path" principle

Every CLI has a hot path — the most common invocation pattern. Examples:

- For a search tool: `mytool search "query"`
- For a hook tool (dcg-style): every shell command
- For a build tool: `mytool build` (incremental rebuild)
- For a daemon CLI: `mytool status`

The hot path should:

- Return in < 1 second on warm cache
- Use a quick-reject filter (memchr-style) where applicable
- Cache aggressively
- Defer expensive computation to a slow path (`--full`, `--deep`)

Operator ⏱.

---

## The "agent-driven workflow" principle

Tools are increasingly used as components of agent-driven workflows. Key implications:

- An agent invocation may pause (rate limit, timeout, manual approval) and resume hours/days later
- An agent may delegate work to other agents who run with different account scopes
- An agent may be running in a sandboxed environment without network or with a constrained filesystem

Tools should be:

- **Resumable** — long ops checkpoint state; `--resume` or `--continue` is supported
- **Sandbox-tolerant** — work without network where possible; document network requirements
- **Multi-tenant aware** — accept identity/auth via env or flag; don't assume single user

See `CRASH-RECOVERY-AND-RESUMABILITY.md` for resumability patterns.

---

## The "self-as-tool" principle

The skill itself is a tool that agents use. So this skill applies to itself. See `SELF-APPLICATION.md`.

---

## The "verification-first" principle

Don't claim a tool has a property without verifying. Every score > 700 in this skill requires evidence. Every recommendation cites a canonical pattern OR counter-example. Every applied change has a regression test.

This is the discipline that keeps Track A grounded in reality rather than vibes.

See `VERIFICATION-FIRST.md` for the full discipline.

---

## Designing from these principles

When you sit down to design (or refactor) an agent-facing API:

1. **Start with capabilities.json**
   - Sketch the JSON schema first
   - List every verb, flag, exit code, env var
   - Define the contract version

2. **Define the canonical task**
   - What's the ONE thing an agent will most often do with this tool?
   - Build the mega-command for it
   - Make sure the mega-command's output includes paste-ready follow-up `commands`

3. **Design the error-pedagogy surface**
   - For every "this could go wrong" path, what does the error message say?
   - Does it name the safe alternative?
   - Does it include `did you mean` for common typos?

4. **Design the output schema**
   - Universal envelope?
   - Pagination strategy?
   - Sparse field selection?
   - Provenance fields?

5. **Design the safety gates**
   - Every mutating verb has `--yes` AND `--dry-run`?
   - Reservations for distributed mutations?
   - Recovery paths for partial failures?

6. **Design the self-documentation surface**
   - `capabilities --json` returns the contract
   - `robot-docs guide` returns paste-ready handbook
   - `--help` ends with AGENT/AUTOMATION footer

7. **Design the regression tests**
   - capabilities-pin
   - per-verb output-shape pin
   - error-message hint pin
   - typo-correction pin

8. **Design the deprecation path**
   - How does v2 supersede v1 without breaking?
   - What's the migration script?

If you do all eight before writing the first line of business logic, the result will score 750+ on every dimension out of the gate.

---

## Cross-referenced principles

| Principle | Operators | Polish-Bar rows |
|-----------|-----------|------------------|
| First-try inevitability | ① ⟁ 🩹 🎓 | Row 1 |
| No telepathy required | 📜 📖 🎯 | Rows 3, 4, 7 |
| Least-surprise-on-failure | 🩹 🚦 🚫 🪄 | Rows 6, 7 |
| Graceful degradation | 🪟 🪜 | Row 4 |
| Minimum viable surface | (negative space; not an operator) | — |
| Explicit > implicit | 🌐 🔢 | Rows 10, 11 |
| Deterministic by default | 🔢 🆔 🪟 | Row 10 |
| Machine-first | All output dims | All output rows |
| Discoverable-from-stdin | 🧶 🧮 | Row 11 |
| Reservation-instead-of-lock | 🧷 🛡 | Row 9 |
| Sub-second hot path | ⏱ | (in dim §2) |
| Resumable / agent-driven | 🔬 🧷 | Row 9 |
| Self-as-tool | (meta) | (meta) |
| Verification-first | 📐 🧾 🧪 | Row 12 |

---

## When to break a principle

Principles aren't laws. Break one when:

- Documentation, tests, AND deprecation path say so
- The break is documented in CHANGELOG with migration instructions
- A `[Q-NNN]` quote is added explaining why
- The break is reversible

If you break a principle without these, you've shipped a future bug. Track A is the discipline that keeps tools coherent across versions.
