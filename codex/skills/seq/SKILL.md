---
name: seq
description: Mine Codex sessions JSONL (sessions/) for skill usage, section compliance, and token counts. Use when analyzing session history or building reports from sessions/ logs.
---

# Seq

## Overview
Mine `sessions/` JSONL quickly and consistently with a single script. Focus on skill usage, format compliance, and token counts.

## Quick Start
```bash
uv run -- python3 scripts/seq.py skills-rank --root sessions
```

## Tasks

### 1) Rank skill usage
```bash
uv run -- python3 scripts/seq.py skills-rank --root sessions
```
Common options:
- `--format json|csv`
- `--max 20`
- `--roles user,assistant`
- `--since 2026-01-01T00:00:00Z`

### 2) Trend a skill over time
```bash
uv run -- python3 scripts/seq.py skill-trend --root sessions --skill tk --bucket week
```

### 3) Report on a specific skill
```bash
uv run -- python3 scripts/seq.py skill-report --root sessions --skill tk \
  --sections "Contract,Invariants,Creative Frame,Why This Solution,Incision,Proof" \
  --sample-missing 3
```
Another example:
```bash
uv run -- python3 scripts/seq.py skill-report --root sessions --skill fix \
  --sections "Contract,Findings,Changes applied,Validation,Residual risks / open questions" \
  --sample-missing 3
```

### 4) Role breakdown by skill
```bash
uv run -- python3 scripts/seq.py role-breakdown --root sessions --format table
```

### 5) Audit section compliance
```bash
uv run -- python3 scripts/seq.py section-audit --root sessions \
  --sections "Contract,Invariants,Creative Frame" \
  --contains "Using $tk" \
  --sample-missing 5
```

### 6) Export occurrences
```bash
uv run -- python3 scripts/seq.py occurrence-export --root sessions --format jsonl --output occurrences.jsonl
```

### 7) Bundle a report
```bash
uv run -- python3 scripts/seq.py report-bundle --root sessions \
  --top 20 --skills tk,fix \
  --sections "Contract,Invariants,Creative Frame,Why This Solution,Incision,Proof"
```

### 8) Token usage summary
```bash
uv run -- python3 scripts/seq.py token-usage --root sessions --top 10
```

## Notes
- Default root: `./sessions`, then `~/.codex/sessions`, then `~/.dotfiles/codex/sessions`.
- Skill names are inferred from `~/.dotfiles/codex/skills` and `~/.codex/skills` by default.
- Add `--output <path>` to write results to a file.

## Resources
### scripts/
- `scripts/seq.py`: CLI for ranking skills, auditing sections, and summarizing token counts.
