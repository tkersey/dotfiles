---
name: cass
description: >-
  Mine past agent sessions for working prompts, decisions, and patterns. Use when
  "what did I ask?", "find that prompt", session archaeology, or agent history.
---

<!-- TOC: Goldmine | THE EXACT PROMPT | Quick Reference | When to Use | Critical Rules | Search Modes | Heuristics | jq Essentials | References -->

# cass Session Search

> **Core Insight:** Your repeated prompts are your best prompts. If you typed it 10+ times, it works. Mine your history.

## The Goldmine Principle

Your conversation history contains:
- **Refined prompts** — Every rephrase that worked better was captured
- **Working rituals** — Prompts repeated 10+ times ARE your methodology
- **Scope decisions** — "When did we decide NOT to do X?"
- **Recovery moments** — What you searched for after context loss = what mattered

**The insight:** Mining your past beats inventing new approaches.

---

## THE EXACT PROMPT — Discovery Workflow

```
1. Bootstrap: Check health, refresh index, get project overview
   cass status --json && cass index --json
   cass search "*" --workspace /data/projects/PROJECT --aggregate agent,date --limit 1 --json

2. Find prompts: Search for keywords, filter to user prompts (lines 1-3)
   cass search "KEYWORD" --workspace /data/projects/PROJECT --json --fields minimal --limit 50 \
     | jq '[.hits[] | select(.line_number <= 3)]'

3. Follow hits: View the actual content
   cass view /path/from/source_path.jsonl -n LINE -C 20

4. Expand context: See the full conversation flow
   cass expand /path/from/source_path.jsonl --line LINE --context 3

5. Discover related: Find the whole work cluster
   cass context /path/from/source_path.jsonl --json
```

### Why This Workflow Works

- **Aggregations first** — Know the terrain before diving in
- **`--fields minimal`** — 5x smaller output, preserves context window
- **`line_number <= 3`** — User prompts live at the top of sessions
- **Context clustering** — Work happens in clusters; one good hit → many related sessions

---

## Quick Reference

```bash
# Health + refresh (ALWAYS first)
cass status --json && cass index --json

# Project overview: who did what, when?
cass search "*" --workspace /path --aggregate agent,date --limit 1 --json

# Find keyword, minimal output
cass search "KEYWORD" --workspace /path --json --fields minimal --limit 50

# Follow a hit
cass view /path.jsonl -n LINE -C 20        # Line-oriented
cass expand /path.jsonl --line LINE --context 3  # Message-oriented

# Find related sessions
cass context /path.jsonl --json

# Export for parsing
cass export /path.jsonl --format json --include-tools -o /tmp/out.json
```

---

## When to Use What

| You Want | Use | Why |
|----------|-----|-----|
| Project overview | `--aggregate agent,date --limit 1` | Counts only, no content |
| Find prompts | `--fields minimal` + `jq select(.line_number <= 3)` | User prompts are lines 1-3 |
| Ritual detection | Count matches: >10 = ritual | Repeated = working |
| Full conversation | `cass expand --context 3` | Message boundaries preserved |
| Raw JSON parsing | `cass export --include-tools -o file.json` | Never pipe exports |
| Content not found | `rg "string" /path.jsonl` | cass skips tool outputs |

---

## Critical Rules

| Rule | Why | Consequence |
|------|-----|-------------|
| **`--limit 1` minimum** | `--limit 0` panics | Use 1 for aggregations |
| **`--fields minimal`** | Token efficiency | 5x smaller output |
| **Export to file** | Piping causes broken pipe panic | `-o /tmp/out.json` always |
| **Exact workspace paths** | Case-sensitive matching | Use `--aggregate workspace` to discover |
| **`--include-tools`** | Tool calls hidden by default | Required for full export |

---

## Search Modes

| Mode | When | Example |
|------|------|---------|
| `lexical` (default) | Exact strings, filenames | `"AGENTS.md"`, `"--workspace"` |
| `semantic` | Conceptual, unknown wording | `"scope reduction discussions"` |
| `hybrid` | Broad exploration | `"architecture decisions"` |

**Default to lexical.** Only use semantic when you don't know exact wording.

---

## The Heuristics

| Signal | Meaning | Action |
|--------|---------|--------|
| `line_number` 1-3 | User prompts | Filter: `select(.line_number <= 3)` |
| `/subagents/` line 2 | THE extraction prompt | Copy-paste ready |
| `total_matches` > 10 | Ritual pattern | Document it, reuse it |
| 0 results + content exists | Workspace path mismatch | Use `--aggregate workspace` |

---

## jq Essentials

```bash
# User prompts only
| jq '[.hits[] | select(.line_number <= 3)]'

# Source paths for follow-up
| jq '.hits[].source_path' -r

# Aggregation buckets
| jq '.aggregations.agent.buckets'

# Count matches
| jq '.total_matches'

# Find repeated prompts (ritual detection)
| jq '[.hits[] | select(.line_number <= 3) | .title[0:80]] | group_by(.) | map({prompt: .[0], count: length}) | sort_by(-.count) | .[0:20]'
```

---

## References

| Need | Reference |
|------|-----------|
| Full command reference | [COMMANDS.md](references/COMMANDS.md) |
| Workflow recipes | [RECIPES.md](references/RECIPES.md) |
| jq patterns | [PATTERNS.md](references/PATTERNS.md) |
| Pitfalls & fixes | [PITFALLS.md](references/PITFALLS.md) |
| Session file formats | [SESSION_FORMATS.md](references/SESSION_FORMATS.md) |

---

## Scripts

| Script | Usage |
|--------|-------|
| `./scripts/quick_analysis.sh /path` | One-command project overview |
| `./scripts/prompt_miner.py --workspace /path` | Find repeated prompts |
| `./scripts/validate.sh` | Validate cass is working |

---

## Validation

```bash
# Quick health check
cass status --json | jq '.index.fresh'

# Should return: true
```

If `false`, run: `cass index --json`
