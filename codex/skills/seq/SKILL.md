---
name: seq
description: "Mine Codex sessions JSONL (`~/.codex/sessions`) and file-based memories (`~/.codex/memories`) for skill usage, section/format compliance, trigger evidence, token metrics, prompt-to-session lookup, and orchestration-concurrency analysis from `spawn_agents_on_csv` calls. Use for prompts like `$seq`, `analyze session history`, `find sessions by prompt`, `rank skill mentions`, `audit missing sections`, `report token usage`, `mine memories`, `orchestration ledger/concurrency from session artifacts`, or `use $seq to improve skill trigger descriptions/frontmatter`."
---

# seq

## Overview
Mine `~/.codex/sessions/` JSONL and `~/.codex/memories/` files quickly and consistently with a single script. Focus on skill usage, format compliance, token counts, and memory-file mining.

## Trigger Cues
- Questions that ask to verify prior session output using artifacts (`"use $seq to find it"` / `"what did that session actually say"`).
- Orchestration ledger forensics from session traces (`Orchestration Ledger`, `spawn_agents_on_csv`, wave CSVs, concurrency counts).
- Concurrency math validation (`max_concurrency`, effective fanout, occurrences of peak parallelism, planned rows vs actual parallelism).

## Zig CLI Iteration Repos

When iterating on the Zig-backed `seq` helper CLI path, use these two repos:

- `skills-zig` (`/Users/tk/workspace/tk/skills-zig`): source for the `seq` Zig binary, build/test wiring, and release tags.
- `homebrew-tap` (`/Users/tk/workspace/tk/homebrew-tap`): Homebrew formula updates/checksum bumps for released `seq` binaries.

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

Memory files by category:
```bash
seq query --spec \
  '{"dataset":"memory_files","group_by":["category"],"metrics":[{"op":"count","as":"count"}],"sort":["-count"],"format":"table"}'
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
- `--roles user,assistant`
- `--since 2026-01-01T00:00:00Z`

### 2) Trend a skill over time
```bash
seq skill-trend --root ~/.codex/sessions --skill tk --bucket week
```

### 3) Report on a specific skill
```bash
seq skill-report --root ~/.codex/sessions --skill tk \
  --sections "Contract,Invariants,Creative Frame,Why This Solution,Incision,Proof" \
  --sample-missing 3
```
Another example:
```bash
seq skill-report --root ~/.codex/sessions --skill fix \
  --sections "Contract,Findings,Changes applied,Validation,Residual risks / open questions" \
  --sample-missing 3
```

### 4) Role breakdown by skill
```bash
seq role-breakdown --root ~/.codex/sessions --format table
```

### 5) Audit section compliance
```bash
seq section-audit --root ~/.codex/sessions \
  --sections "Contract,Invariants,Creative Frame" \
  --contains "Using $tk" \
  --sample-missing 5
```

### 6) Export occurrences
```bash
seq occurrence-export --root ~/.codex/sessions --format jsonl --output occurrences.jsonl
```

### 7) Bundle a report
```bash
seq report-bundle --root ~/.codex/sessions \
  --top 20 --skills tk,fix \
  --sections "Contract,Invariants,Creative Frame,Why This Solution,Incision,Proof"
```

### 8) Token usage summary
```bash
seq token-usage --root ~/.codex/sessions --top 10
```

### 9) Reproducible perf harness
Run stable workloads with fixed warmup/sample counts and optional baseline comparison.

```bash
zig build bench -Doptimize=ReleaseFast -- --config perf/frozen/workload_config.json
```

Head-to-head Zig vs Python gate (runs parity first):
```bash
scripts/perf/head_to_head.sh --root testdata/golden/sessions --gate 20 --samples 9 --warmup 1
```

Differential parity against the Python oracle:
```bash
scripts/parity/run_diff.sh --root ~/.codex/sessions/2026/02/19
```

### 10) Find sessions by prompt text
```bash
seq find-session --root ~/.codex/sessions --prompt "adapter=auto" --limit 20
```

### 11) List prompts/messages for one session
```bash
seq session-prompts --root ~/.codex/sessions --session-id <session_id> \
  --roles user,assistant --strip-skill-blocks --limit 100
```

### 12) Cue vs invoked discovery-skill rate
```bash
seq routing-gap --root ~/.codex/sessions \
  --cue-spec @cue-spec.json \
  --discovery-skills grill-me,prove-it,complexity-mitigator,invariant-ace,tk \
  --format table
```

### 13) Orchestration concurrency summary
```bash
seq orchestration-concurrency --root ~/.codex/sessions --session-id <session_id> --format table
```
Or target one JSONL directly:
```bash
seq orchestration-concurrency --path /absolute/path/to/rollout.jsonl --format json
```

## Notes
- Default root: `~/.codex/sessions`.
- `memory_files` defaults to `~/.codex/memories` and accepts `params.memory_root` to override.
- Skill names are inferred from `${CODEX_HOME:-$HOME/.codex}/skills` by default, and from `${CLAUDE_HOME:-$HOME/.claude}/skills` when needed.
- Runtime bootstrap policy: require the Zig `seq` binary, default to Homebrew install on macOS, and fallback to direct Zig install from `skills-zig` on non-macOS.
- Add `--output <path>` to write results to a file.
- `query` auto-projects only referenced dataset fields (`where`, `group_by`, `metrics.field`, `select`, and non-grouped `sort`) to reduce scan overhead.
- `find-session` returns `session_id` and `path`; use these to target follow-on `query` or resume workflows.
- `session-prompts` defaults to `--roles user`; set `--roles user,assistant` to include both sides of a conversation.
- `session-prompts` deduplicates mirrored duplicate rows by default; pass `--no-dedupe-exact` to keep all duplicates.
- Typical flow: run `find-session`, then pass the returned `session_id` into `session-prompts --session-id <id>`.
- `orchestration-concurrency` reports both configured (`max_concurrency`) and effective fanout (`min(max_concurrency, csv_rows)`), plus how many times each maximum occurred.

## Resources
- `seq` binary: CLI for ranking skills, auditing sections, querying datasets, and summarizing token usage.
- `zig build bench -Doptimize=ReleaseFast -- --config perf/frozen/workload_config.json`: frozen-workload performance runner.
- `scripts/parity/run_diff.sh`: Zig/Python differential parity harness.
- `scripts/perf/head_to_head.sh`: parity-gated head-to-head p50 speed benchmark.
