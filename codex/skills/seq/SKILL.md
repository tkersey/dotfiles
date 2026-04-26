---
name: seq
description: "Mine Codex sessions JSONL (`~/.codex/sessions`) and file-based memories (`~/.codex/memories`) for explicit `$seq` and artifact-forensics questions, preferring `artifact-search`, then specialized follow-ups such as `skill-blocks`, `plan-search`, `session-prompts`, `session-tooling`, and `orchestration-concurrency`, then `query-diagnose`, and generic `query` only when needed. Opencode mining is explicit-only and requires a literal `opencode` cue in the request."
---

# seq

## Overview
Mine `~/.codex/sessions/` JSONL and `~/.codex/memories/` files quickly and consistently with the Zig `seq` CLI. Explicit `$seq` requests and artifact-forensics questions are `seq`-first. Focus on skill usage, format compliance, token counts, tool-call/tooling forensics, memory-file mining, and session-backed proof.

## Trigger Cues
- Explicit `$seq` asks.
- Questions that ask to extract or query finalized `$plan` artifacts (`<proposed_plan>` blocks) for a repo, session, or time window.
- Questions that ask to verify prior session output using artifacts (`"use $seq to find it"` / `"what did that session actually say"`).
- Artifact-forensics questions about provenance, trace proof, or "show me the artifact that proves it".
- Questions about Codex memory artifacts or provenance (`"what's in MEMORY.md"`, `"which rollout produced this memory"`, `"is this memory stale"`, `"how do memory_summary.md and rollout_summaries relate"`).
- Execution ledger forensics from session traces (`Orchestration Ledger`, subagent lifecycle events, concurrency counts).
- Concurrency math validation (`max_concurrency`, effective fanout, occurrences of peak parallelism, planned rows vs actual parallelism).

## Local-First Routing Ladder
- Stay in `seq` first for explicit `$seq` asks and artifact-forensics work; do not jump to generic shell search unless `seq` cannot cover the need.
- Preferred entrypoint: `seq artifact-search` for broad forensics; use `seq plan-search` first when the request is specifically about finalized `<proposed_plan>` artifacts.
- Use this ladder:
  1. `plan-search` for finalized `$plan` artifact retrieval; otherwise `artifact-search`.
  2. Specialized follow-ups that already match the artifact shape:
     - `memory-provenance` for "why is this memory here now?" / "which rollout introduced it?" questions about one memory thread or rollout summary.
     - `memory-history` for "what changed over time?" questions about one memory thread or a topic across the memory corpus.
     - `memory-map` for "what artifacts exist for this topic/thread and what's the fastest evidence path?" questions.
     - `skill-blocks` for exact historical `<skill>...</skill>` extraction by skill name, with full block bodies and distinct-version history.
     - `plan-search` for strict repo/session/time/text retrieval of complete `<proposed_plan>` blocks.
     - `find-session` for prompt-to-session lookup.
     - `session-prompts` for "what did that session actually say" and transcript proof.
     - `session-tooling` for shell/tool summaries.
     - `orchestration-concurrency` for ledger/concurrency proof.
     - `query --spec ... memory_files` for memory artifact inventory/routing.
     - `opencode-prompts` / `opencode-events` only when the literal gate is satisfied.
  3. `query-diagnose` when a `seq query` run needs lifecycle debugging or deterministic next actions.
  4. Generic `seq query` only when no specialized command covers the question.
- Treat `query-diagnose` as a diagnostic tool for `seq query`, not the default artifact-discovery entrypoint.

## Memory Artifact Model
- Treat `~/.codex/memories` as a file-backed memory workspace, not an opaque store.
- Use root artifacts deliberately:
  - `memory_summary.md`: compact routing/index layer. Use it first when the question is broad or you need to decide where to dig.
  - `MEMORY.md`: durable handbook/registry. Use it first when the question is about reusable guidance, prior decisions, or task-family history.
  - `raw_memories.md`: merged stage-1 raw memories. Use it for recency and inventory, especially when tracing newly added or removed memory inputs.
- Treat `rollout_summaries/*.md` as per-rollout markdown summaries, not JSONL logs.
  - Expect fields like `thread_id`, `updated_at`, `cwd`, `rollout_path`, and sometimes `git_branch`.
  - Use `rollout_path` to jump to the original session JSONL under `~/.codex/sessions` when you need raw evidence.
- Treat `skills/` under the memory root as optional memory-derived helper assets.

## Memory Mining Workflow
- Use `seq` first for inventory, routing, and timestamp/category analysis; do not pretend it replaces reading the target markdown files.
- Start broad, then go deeper:
  1. Inventory `memory_files` to see what categories and files exist.
  2. If the question is navigational or "what do we know?", route through `memory_summary.md`.
  3. If the question is durable/procedural, route through `MEMORY.md`.
  3b. If the question is about one memory thread or one rollout summary artifact, prefer `memory-provenance` before manual markdown reads.
  3c. If the question is about a topic across the memory corpus, prefer `memory-map` or `memory-history` before raw `query`.
  4. If you need provenance for one memory block, inspect the relevant `rollout_summaries/*.md` file.
  5. If you need raw session evidence, follow `rollout_path` into `~/.codex/sessions/...jsonl`; use `seq` session/orchestration commands only when they accept the handle you actually have, otherwise inspect the file directly.
- Prefer `MEMORY.md` / `memory_summary.md` over `raw_memories.md` when both cover the topic; `raw_memories.md` is a lower-level consolidation input, not the highest-level answer.

## Opencode Explicitness Gate (Hard)
- Only run opencode research when the request text includes the literal word `opencode`.
- Treat these as opencode research and block them without the literal cue:
  - `seq opencode-prompts`
  - `seq opencode-events`
  - `seq query` specs targeting dataset `opencode_prompts` or `opencode_events`
- For mixed searches without a literal `opencode` cue, hard-skip the opencode branch and continue with non-opencode `seq` datasets only.

## Zig CLI Iteration Repos

When iterating on the Zig-backed `seq` helper CLI path, use these two repos:

- `skills-zig` (`$HOME/workspace/tk/skills-zig`): source for the `seq` Zig binary, build/test wiring, and release tags.
- `homebrew-tap` (`$HOME/workspace/tk/homebrew-tap`): Homebrew formula updates/checksum bumps for released `seq` binaries.

## Quick Start
```bash
run_seq() {
  install_seq_direct() {
    local repo="${SKILLS_ZIG_REPO:-$HOME/workspace/tk/skills-zig}"
    if ! command -v zig >/dev/null 2>&1; then
      echo "zig not found. Install Zig from https://ziglang.org/download/ and retry." >&2
      return 1
    fi
    if [ ! -d "$repo" ]; then
      echo "skills-zig repo not found at $repo." >&2
      echo "clone it with: git clone https://github.com/tkersey/skills-zig \"$repo\"" >&2
      return 1
    fi
    if ! (cd "$repo" && zig build -Doptimize=ReleaseSafe); then
      echo "direct Zig build failed in $repo." >&2
      return 1
    fi
    if [ ! -x "$repo/zig-out/bin/seq" ]; then
      echo "direct Zig build did not produce $repo/zig-out/bin/seq." >&2
      return 1
    fi
    mkdir -p "$HOME/.local/bin"
    install -m 0755 "$repo/zig-out/bin/seq" "$HOME/.local/bin/seq"
  }

  local os="$(uname -s)"
  if command -v seq >/dev/null 2>&1 && seq --help 2>&1 | grep -q "skills-rank"; then
    seq "$@"
    return
  fi

  if [ "$os" = "Darwin" ]; then
    if ! command -v brew >/dev/null 2>&1; then
      echo "homebrew is required on macOS: https://brew.sh/" >&2
      return 1
    fi
    if ! brew install tkersey/tap/seq; then
      echo "brew install tkersey/tap/seq failed." >&2
      return 1
    fi
  elif ! (command -v seq >/dev/null 2>&1 && seq --help 2>&1 | grep -q "skills-rank"); then
    if ! install_seq_direct; then
      return 1
    fi
  fi

  if command -v seq >/dev/null 2>&1 && seq --help 2>&1 | grep -q "skills-rank"; then
    seq "$@"
    return
  fi
  echo "no compatible seq binary found after install attempt." >&2
  if [ "$os" = "Darwin" ]; then
    echo "expected install path: brew install tkersey/tap/seq" >&2
  else
    echo "expected direct path: SKILLS_ZIG_REPO=<skills-zig-path> zig build -Doptimize=ReleaseSafe" >&2
  fi
  return 1
}

run_seq datasets --root ~/.codex/sessions
```

Commands below use `seq` directly for brevity. Use `run_seq` when you want brew-aware bootstrap with binary-only execution.

## Query (JSON Spec)
Run flexible mining via `query` with a small JSON spec (inline or `@spec.json`).

List datasets:
```bash
seq datasets --root ~/.codex/sessions
```

Show dataset fields/params:
```bash
seq dataset-schema --dataset token_deltas --root ~/.codex/sessions
```

Examples:

Rank skill usage:
```bash
seq query --root ~/.codex/sessions --spec \
  '{"dataset":"skill_mentions","group_by":["skill"],"metrics":[{"op":"count","as":"count"}],"sort":["-count"],"limit":20,"format":"table"}'
```

Daily token totals (from `token_count` events):
```bash
seq query --root ~/.codex/sessions --spec \
  '{"dataset":"token_deltas","group_by":["day"],"metrics":[{"op":"sum","field":"delta_total_tokens","as":"tokens"}],"sort":["day"],"format":"table"}'
```
Use `token-usage --tz ...` instead when the user means local calendar days or asks for averages/summaries rather than raw UTC buckets.

Top sessions by total tokens:
```bash
seq query --root ~/.codex/sessions --spec \
  '{"dataset":"token_sessions","select":["path","total_total_tokens"],"sort":["-total_total_tokens"],"limit":10,"format":"table"}'
```

Rank tool calls:
```bash
seq query --root ~/.codex/sessions --spec \
  '{"dataset":"tool_calls","group_by":["tool"],"metrics":[{"op":"count","as":"count"}],"sort":["-count"],"limit":20,"format":"table"}'
```

Inspect lifecycle-enriched tool invocations:
```bash
seq query --root ~/.codex/sessions --spec \
  '{"dataset":"tool_invocations","select":["timestamp","tool_name","command_text","workdir","wall_time_ms","exit_code","running_state"],"sort":["-timestamp"],"limit":20,"format":"table"}'
```

Flatten tool-call argument leaves:
```bash
seq query --root ~/.codex/sessions --spec \
  '{"dataset":"tool_call_args","where":[{"field":"tool_name","op":"eq","value":"exec_command"}],"select":["timestamp","tool_name","arg_path","value_kind","value_text","value_number","value_bool"],"sort":["-timestamp"],"limit":20,"format":"table"}'
```

Memory files by category:
```bash
seq query --spec \
  '{"dataset":"memory_files","group_by":["category"],"metrics":[{"op":"count","as":"count"}],"sort":["-count"],"format":"table"}'
```

Explain why a memory exists now:
```bash
seq memory-provenance --thread-id 019bae5d-7d12-7b01-9cb5-b8bb6046b85b --format table
```

Map the fastest evidence path for a memory topic:
```bash
seq memory-map --contains synesthesia --limit 5 --format table
```

Show an observed timeline for one memory thread:
```bash
seq memory-history --thread-id 019bae5d-7d12-7b01-9cb5-b8bb6046b85b --format table
```

Opencode prompts with source override:
```bash
seq query --spec \
  '{"dataset":"opencode_prompts","params":{"source":"db","opencode_db_path":"~/.local/share/opencode/opencode.db"},"where":[{"field":"part_types","op":"contains","value":"file"}],"select":["session_slug","prompt_text","part_types"],"sort":["-time_created_epoch_ms"],"format":"jsonl"}'
```

### Ready-made specs
Prebuilt specs live in `specs/`.

```bash
seq query --root ~/.codex/sessions --spec @specs/skills-rank.json
seq query --root ~/.codex/sessions --spec @specs/tools-rank.json
seq query --root ~/.codex/sessions --spec @specs/tokens-top-days.json
seq query --root ~/.codex/sessions --spec @specs/tokens-top-sessions.json
seq query --root ~/.codex/sessions --spec @specs/tk-trend-week.json
```

### Spec reference
Top-level keys:
- `dataset` (string, required)
- `params` (object, optional; dataset-specific)
- `where` (list of predicates, optional)
- `group_by` (list of field names, optional)
- `metrics` (list of aggregations, optional; default `count` when grouping)
- `select` (list of field names, optional; for non-grouped queries)
- `sort` (list of field names; prefix with `-` for descending)
- `limit` (int, optional)
- `format` (`table` | `json` | `csv` | `jsonl`; default: `table` when grouped, else `jsonl`)

Where predicate shape:
```json
{"field":"day","op":"eq","value":"2026-02-05"}
```

Supported `where.op`:
- `eq`, `neq`
- `gt`, `gte`, `lt`, `lte` (numeric-ish compare)
- `in`, `nin` (value is a JSON list)
- `contains` (substring)
- `contains_any` (value is a JSON list of substrings; optional `case_insensitive: true`)
- `regex` (regex-like matching with `^`, `$`, and alternation `|`; optional `case_insensitive: true`)
- `regex_any` (value is a JSON list of regex-like strings; OR semantics)
- `exists`, `not_exists`

Metrics shape (grouped queries):
```json
{"op":"sum","field":"delta_total_tokens","as":"tokens"}
```

Supported `metrics.op`:
- `count`
- `sum`, `min`, `max`, `avg`
- `count_distinct`

## Tasks

### 1) Rank skill usage
```bash
seq skills-rank --root ~/.codex/sessions
```
Common options:
- `--format json|csv`
- `--max 20`
- `--since 2026-01-01T00:00:00Z`
- `--until 2026-03-01T00:00:00Z`

### 2) Trend a skill over time
```bash
seq skill-trend --root ~/.codex/sessions --skill tk --bucket week
```

### 3) Report on a specific skill
```bash
seq skill-report --root ~/.codex/sessions --skill tk
```
Another example:
```bash
seq skill-report --root ~/.codex/sessions --skill tk \
  --since 2026-03-01T00:00:00Z
```

### 4) Role breakdown by skill
```bash
seq role-breakdown --root ~/.codex/sessions --format table
```

### 5) Audit section compliance
```bash
seq section-audit --root ~/.codex/sessions \
  --sections "Contract,Invariants,Creative Frame"
```

### 6) Export occurrences
```bash
seq occurrence-export --root ~/.codex/sessions --format jsonl --output occurrences.jsonl
```

### 7) Bundle a report
```bash
seq report-bundle --root ~/.codex/sessions --top 20
```

### 8) Token usage summary
```bash
seq token-usage --root ~/.codex/sessions --top 10
```
Local-day summary with averages:
```bash
seq token-usage --root ~/.codex/sessions \
  --since 2026-03-26T00:00:00-07:00 \
  --tz local \
  --summary \
  --format json
```
Local-day rows without post-processing:
```bash
seq token-usage --root ~/.codex/sessions \
  --since 2026-03-26T00:00:00-07:00 \
  --tz local \
  --format table
```
Path-heavy scope check:
```bash
seq token-usage --root ~/.codex/sessions \
  --since 2026-03-26T00:00:00-07:00 \
  --group-by path \
  --top 20 \
  --format table
```
Self-auditing accounting proof for user-visible token totals:
```bash
seq token-usage --root ~/.codex/sessions \
  --since 2026-03-26T00:00:00-07:00 \
  --until 2026-03-27T00:00:00-07:00 \
  --tz local \
  --summary \
  --audit \
  --format table
```
Use `--audit` when the answer needs to explain or defend the number. It reports the monotonic `total_token_usage` delta total, the naive `last_token_usage` total, duplicate-total rows excluded, reset events, null/missing-total rows, requested/observed span days, and bucket counts. State the scope explicitly: this is local `~/.codex/sessions` corpus accounting, not OpenAI billing, organization-wide usage, or server-side metering.

### 9) Reproducible perf harness
Run stable workloads with fixed warmup/sample counts and optional baseline comparison.

```bash
zig build bench -Doptimize=ReleaseFast -- --config perf/frozen/workload_config.json
```

### 10) Find sessions by prompt text
```bash
seq find-session --root ~/.codex/sessions --prompt "adapter=auto" --limit 20
```
Constrain to a session window:
```bash
seq find-session --root ~/.codex/sessions \
  --prompt "adapter=auto" \
  --since 2026-03-01T00:00:00Z \
  --until 2026-03-05T00:00:00Z \
  --limit 20
```

### 11) List prompts/messages for one session
```bash
seq session-prompts --root ~/.codex/sessions --session-id <session_id> \
  --roles user,assistant --strip-skill-blocks --limit 100 --format jsonl
```
Constrain to a time window within that session:
```bash
seq session-prompts --root ~/.codex/sessions --session-id <session_id> \
  --roles user,assistant --since 2026-03-01T00:00:00Z --until 2026-03-05T00:00:00Z \
  --strip-skill-blocks --limit 100 --format jsonl
```
Current session from the active Codex thread:
```bash
seq session-prompts --root ~/.codex/sessions --current \
  --roles user,assistant --strip-skill-blocks --limit 100 --format jsonl
```

### 11b) Extract exact historical skill blocks
Return all distinct historical versions for one skill:
```bash
seq skill-blocks --root ~/.codex/sessions --skill accretive --format jsonl
```
Target one known session:
```bash
seq skill-blocks --root ~/.codex/sessions \
  --skill accretive \
  --session-id 019d2d3e-3f14-7e23-b5b9-cf4899a456df \
  --format jsonl
```
Return every exact occurrence instead of distinct versions:
```bash
seq skill-blocks --root ~/.codex/sessions \
  --skill accretive \
  --history all \
  --format jsonl
```
Return only the newest distinct version:
```bash
seq skill-blocks --root ~/.codex/sessions \
  --skill accretive \
  --history latest \
  --format json
```

### 10b) Find finalized plan artifacts
Repo-scoped metadata rows:
```bash
seq plan-search --root ~/.codex/sessions \
  --repo "$HOME/workspace/tk/shift" \
  --since 2026-03-01T00:00:00Z \
  --format table
```
Filter by title/body text and show scan counters:
```bash
seq plan-search --root ~/.codex/sessions \
  --repo "$HOME/workspace/tk/shift" \
  --contains "PromptMode" \
  --stats \
  --format jsonl
```
Target one known session and include the exact plan block:
```bash
seq plan-search --root ~/.codex/sessions \
  --session-id 019ce80b-9fb4-72a1-9c1e-3d626d4e4913 \
  --include-body \
  --format jsonl
```

### Session-backed tooling diagnostics
Summarize tool/shell activity for one session:
```bash
seq session-tooling --root ~/.codex/sessions --session-id <session_id> \
  --since 2026-03-01T00:00:00Z --until 2026-03-05T00:00:00Z \
  --summary --group-by executable --format table
```
Inspect `seq query` lifecycle health for one session:
```bash
seq query-diagnose --root ~/.codex/sessions --session-id <session_id> \
  --since 2026-03-01T00:00:00Z --until 2026-03-05T00:00:00Z \
  --threshold-ms 10000 --next-actions --format json
```

### 12) Cue vs invoked discovery-skill rate
```bash
seq routing-gap --root ~/.codex/sessions \
  --cue-spec @cue-spec.json \
  --discovery-skills grill-me,prove-it,complexity-mitigator,invariant-ace,tk \
  --format table
```

### 13) Execution concurrency summary
```bash
seq orchestration-concurrency --root ~/.codex/sessions --session-id <session_id> --format table
```
Or target one JSONL directly:
```bash
seq orchestration-concurrency --path /absolute/path/to/rollout.jsonl --format json
```
Assert the floor gate for non-trivial runs:
```bash
seq orchestration-concurrency --path /absolute/path/to/rollout.jsonl \
  --floor-threshold 3 --fail-on-floor --format table
```

### 14) Query Opencode prompt history
Only run this section when the user request explicitly includes `opencode`.
```bash
seq opencode-prompts --limit 20 --format jsonl
```
Filter and project:
```bash
seq opencode-prompts \
  --source db \
  --contains "grill me" \
  --mode normal \
  --part-type file \
  --select session_slug,message_id,prompt_text,part_types \
  --sort -time_created_epoch_ms \
  --format table
```
Hybrid with `--spec` (CLI convenience flags override conflicting spec values):
```bash
seq opencode-prompts --spec @opencode-spec.json --contains "$plan" --limit 10
```

### 15) Query Opencode message/part events
Only run this section when the user request explicitly includes `opencode`.
```bash
seq opencode-events --limit 50 --format jsonl
```
Filter event rows:
```bash
seq opencode-events \
  --source db \
  --role assistant \
  --tool shell \
  --status completed \
  --select session_slug,message_id,event_index,part_type,tool_name,tool_status,text \
  --sort -time_created_epoch_ms \
  --format table
```

### 16) Inventory Codex memory artifacts
```bash
seq query --spec \
  '{"dataset":"memory_files","group_by":["category"],"metrics":[{"op":"count","as":"count"}],"sort":["-count"],"format":"table"}'
```
List root artifacts explicitly:
```bash
seq query --spec \
  '{"dataset":"memory_files","where":[{"field":"category","op":"eq","value":"root"}],"select":["relative_path","size_bytes","modified_at"],"sort":["relative_path"],"format":"table"}'
```

### 17) Find recent rollout summaries behind memory updates
```bash
seq query --spec \
  '{"dataset":"memory_files","where":[{"field":"category","op":"eq","value":"rollout_summaries"}],"select":["relative_path","modified_at","size_bytes"],"sort":["-modified_at"],"limit":20,"format":"table"}'
```
Then open the matching `rollout_summaries/*.md` file and use its `rollout_path` to jump into the original session JSONL when deeper proof is required.

## Notes
- Default root: `~/.codex/sessions`.
- `memory_files` defaults to `~/.codex/memories` and accepts `params.memory_root` and `params.include_preview`.
- `memory_files` exposes `path`, `relative_path`, `name`, `category`, `extension`, `size_bytes`, `modified_at`, and `preview`.
- `memory_stage1_outputs` reads the local Codex state DB and accepts `params.state_db_path`.
- `memory_extensions` reads `~/.codex/memories_extensions` and accepts `params.extensions_root`.
- Current memory-file categories are `root`, `rollout_summaries`, and `skills`; `root` may also include non-canonical files, so do not assume every root file is part of the memory contract.
- `rollout_summaries/*.md` are markdown summaries; the original JSONL evidence lives at the `rollout_path` referenced inside those files.
- `memory_files` is best for inventory and routing; when the answer depends on markdown body content, use `seq` to find the file and then read that specific file directly.
- `memory-provenance` is the default archaeology surface for one thread or rollout summary file.
- `memory-map` is the default archaeology surface for topic- or artifact-routing questions.
- `memory-history` emits an observed evidence timeline, not a reconstructed historical `MEMORY.md` diff; do not overclaim that it proves exact past memory contents.
- Opencode datasets (`opencode_prompts`, `opencode_events`) default to `source=auto`, which resolves DB-first (`$HOME/.local/share/opencode/opencode.db`) with JSONL fallback (`$HOME/.local/state/opencode/prompt-history.jsonl`).
- Opencode params: `params.source`, `params.opencode_db_path`, `params.opencode_path`, `params.include_raw`; `opencode_prompts` also supports `params.include_summary_fallback`.
- Skill names are inferred from `${CODEX_HOME:-$HOME/.codex}/skills` by default, and from `${CLAUDE_HOME:-$HOME/.claude}/skills` when needed.
- Runtime bootstrap policy: require the Zig `seq` binary, default to Homebrew install on macOS, and fallback to direct Zig install from `skills-zig` on non-macOS.
- Add `--output <path>` to write results to a file.
- `query` auto-projects only referenced dataset fields (`where`, `group_by`, `metrics.field`, `select`, and non-grouped `sort`) to reduce scan overhead.
- `query.params` is now parsed and routed into dataset collectors for dataset-specific source overrides.
- `token-usage` now supports `--tz utc|local|+HH:MM|-HH:MM`, `--summary`, `--audit`, `--group-by day|path`, and `--path` / `--session-id` targeting for exact scope reporting.
- Prefer `token-usage` over generic `query` for "since yesterday/last Thursday", daily averages, or local-calendar token questions; reserve `token_deltas` queries for lower-level accounting checks.
- For disputed daily averages, run `token-usage --summary --audit` and report both the authoritative monotonic total and the naive last-token overcount fields, with the local-corpus-not-billing boundary.
- Session-tooling datasets now include `tool_invocations` and `tool_call_args` in addition to `tool_calls`.
- `tool_calls` now exposes raw argument/input text plus command/workdir fields: `arguments_text`, `input_text`, `command_text`, `primary_executable`, `workdir`, `parse_error`.
- `tool_invocations` adds lifecycle fields such as `end_timestamp`, `pty_session_id`, `wall_time_ms`, `exit_code`, `running_state`, and `unresolved`.
- `tool_call_args` flattens JSON argument/input leaves with `payload_source`, `arg_path`, `value_kind`, `value_text`, `value_number`, `value_bool`, `is_null`, and `array_index`.
- `find-session` returns `session_id` and `path`; use these to target follow-on `query` or resume workflows.
- `find-session`, `session-prompts`, `session-tooling`, and `query-diagnose` accept ISO-8601 `--since` / `--until` filters for session-backed narrowing.
- `plan-search` accepts repo/session/time/text filters for strict `<proposed_plan>` retrieval and defaults to metadata rows sorted newest-first.
- `plan-search --stats` emits scan counters and filter-usage flags so repo-scoped plan queries can prove they narrowed the corpus.
- Prefer the routing ladder: `plan-search` for finalized plan artifacts, otherwise `artifact-search`, then specialized follow-ups, then `query-diagnose`, and generic `query` only when needed.
- `session-prompts` defaults to `--roles user`; set `--roles user,assistant` to include both sides of a conversation.
- `session-prompts --current` resolves the current session from `CODEX_THREAD_ID` and fails closed if that env var is unavailable.
- `session-prompts` deduplicates mirrored duplicate rows by default; pass `--no-dedupe-exact` to keep all duplicates.
- `skill-blocks` is the exact-body recovery surface for session-injected skills; it returns full `<skill>...</skill>` envelopes, not loose `$skill` mentions or narrative references.
- `skill-blocks` defaults to `--history distinct` and `--format jsonl`; use `--history all` to keep repeated identical injections and `--history latest` to select the newest distinct version.
- Typical flow: run `find-session`, then pass the returned `session_id` into `session-prompts --session-id <id>`.
- `session-tooling` summarizes per-invocation shell/tool behavior and can aggregate via `--summary --group-by executable|command|tool`.
- `query-diagnose` emits per-query diagnostics from rollout JSONL and can suggest deterministic follow-up commands with `--next-actions`.
- `orchestration-concurrency` reports configured and effective fanout, plus how many times each maximum occurred.
- It also emits `effective_peak`, `spawn_substrate`, direct-lane counters (`spawn_agent_calls`, `wait_agent_calls`, `close_agent_calls`), `serialized_wait_agent_ratio`, and floor-gate fields (`floor_threshold`, `floor_applicable`, `floor_result`).

## Resources
- `seq` binary: CLI for ranking skills, auditing sections, querying datasets, and summarizing token usage.
- `zig build bench -Doptimize=ReleaseFast -- --config perf/frozen/workload_config.json`: frozen-workload performance runner.
