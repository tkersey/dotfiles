---
name: seq
description: Mine Codex sessions JSONL (sessions/) for skill usage, section compliance, and token counts. Use when analyzing session history or building reports from sessions/ logs.
---

# seq

## Overview
Mine `sessions/` JSONL quickly and consistently with a single script. Focus on skill usage, format compliance, and token counts.

## Quick Start
```bash
uv run scripts/seq.py datasets --root sessions
```

## Query (JSON Spec)
Run flexible mining via `query` with a small JSON spec (inline or `@spec.json`).

List datasets:
```bash
uv run scripts/seq.py datasets --root sessions
```

Show dataset fields/params:
```bash
uv run scripts/seq.py dataset-schema --dataset token_deltas --root sessions
```

Examples:

Rank skill usage:
```bash
uv run scripts/seq.py query --root sessions --spec \
  '{"dataset":"skill_mentions","group_by":["skill"],"metrics":[{"op":"count","as":"count"}],"sort":["-count"],"limit":20,"format":"table"}'
```

Daily token totals (from `token_count` events):
```bash
uv run scripts/seq.py query --root sessions --spec \
  '{"dataset":"token_deltas","group_by":["day"],"metrics":[{"op":"sum","field":"delta_total_tokens","as":"tokens"}],"sort":["day"],"format":"table"}'
```

Top sessions by total tokens:
```bash
uv run scripts/seq.py query --root sessions --spec \
  '{"dataset":"token_sessions","select":["path","total_total_tokens"],"sort":["-total_total_tokens"],"limit":10,"format":"table"}'
```

Rank tool calls:
```bash
uv run scripts/seq.py query --root sessions --spec \
  '{"dataset":"tool_calls","group_by":["tool"],"metrics":[{"op":"count","as":"count"}],"sort":["-count"],"limit":20,"format":"table"}'
```

### Ready-made specs
Prebuilt specs live in `specs/`.

```bash
uv run scripts/seq.py query --root sessions --spec @specs/skills-rank.json
uv run scripts/seq.py query --root sessions --spec @specs/tools-rank.json
uv run scripts/seq.py query --root sessions --spec @specs/tokens-top-days.json
uv run scripts/seq.py query --root sessions --spec @specs/tokens-top-sessions.json
uv run scripts/seq.py query --root sessions --spec @specs/tk-trend-week.json
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
- `regex` (value is a regex string; optional `case_insensitive: true`)
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
uv run scripts/seq.py skills-rank --root sessions
```
Common options:
- `--format json|csv`
- `--max 20`
- `--roles user,assistant`
- `--since 2026-01-01T00:00:00Z`

### 2) Trend a skill over time
```bash
uv run scripts/seq.py skill-trend --root sessions --skill tk --bucket week
```

### 3) Report on a specific skill
```bash
uv run scripts/seq.py skill-report --root sessions --skill tk \
  --sections "Contract,Invariants,Creative Frame,Why This Solution,Incision,Proof" \
  --sample-missing 3
```
Another example:
```bash
uv run scripts/seq.py skill-report --root sessions --skill fix \
  --sections "Contract,Findings,Changes applied,Validation,Residual risks / open questions" \
  --sample-missing 3
```

### 4) Role breakdown by skill
```bash
uv run scripts/seq.py role-breakdown --root sessions --format table
```

### 5) Audit section compliance
```bash
uv run scripts/seq.py section-audit --root sessions \
  --sections "Contract,Invariants,Creative Frame" \
  --contains "Using $tk" \
  --sample-missing 5
```

### 6) Export occurrences
```bash
uv run scripts/seq.py occurrence-export --root sessions --format jsonl --output occurrences.jsonl
```

### 7) Bundle a report
```bash
uv run scripts/seq.py report-bundle --root sessions \
  --top 20 --skills tk,fix \
  --sections "Contract,Invariants,Creative Frame,Why This Solution,Incision,Proof"
```

### 8) Token usage summary
```bash
uv run scripts/seq.py token-usage --root sessions --top 10
```

## Notes
- Default root: `./sessions`, then `~/.codex/sessions`, then `~/.dotfiles/codex/sessions`.
- Skill names are inferred from `~/.dotfiles/codex/skills` and `~/.codex/skills` by default.
- Add `--output <path>` to write results to a file.

## Resources
### scripts/
- `scripts/seq.py`: CLI for ranking skills, auditing sections, and summarizing token counts.
