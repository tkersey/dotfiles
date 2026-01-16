---
name: cx
description: Spawn Codex CLI sub-agents non-interactively with fixed model/effort and required flags (web search, skills, yolo). Use when dispatching a single agent per bead via codex exec with a positional prompt string and locked defaults.
---

# cx

## Workflow
1. Accept a positional prompt string (required).
2. Run `$HOME/.codex/skills/cx/scripts/cx-exec.sh "$PROMPT"`.
3. Do not override defaults; update the script if defaults change.

## Defaults
- Model: gpt-5.2-codex
- Reasoning effort: high (via `-c model_reasoning_effort="high"`)
- Flags: `--search`, `--enable web_search_request`, `--enable skills`, `--yolo`
- Sandbox/approvals: bypassed (via `--dangerously-bypass-approvals-and-sandbox`)
- Mode: `codex exec` (non-interactive)

## Script
- `$HOME/.codex/skills/cx/scripts/cx-exec.sh`

## Example
```bash
$HOME/.codex/skills/cx/scripts/cx-exec.sh "Work bead 123. Use skill resolve. Source the next task per that skill's workflow."
```
