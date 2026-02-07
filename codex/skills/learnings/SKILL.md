---
name: learnings
description: Capture and persist evidence-backed execution learnings discovered during coding work. Use when a coding slice is completed or paused and there is new evidence from diffs, validations, pivots, retries, reversals, or fixes; also trigger implicitly after validation state transitions from failing to passing, repeated failure loops, strategy changes, and before commit or PR finalization. Extract actionable nuggets about fruitful paths and footguns, then append structured records to `.learnings.jsonl` at repo root.
---

# Learnings

## Overview

Capture durable lessons as soon as evidence appears, not only at explicit retrospective requests.
Write each validated learning as JSONL so future agents can reuse successful patterns and avoid footguns quickly.

## Capture Checkpoints

Capture at least once per coding turn when any of these checkpoints occurs:

1. Validation transition: a signal changes state (`fail->pass`, `pass->fail`, `timeout->stable`).
2. Strategy pivot: an approach is abandoned, replaced, or simplified.
3. Footgun discovery: hidden risk, brittle assumption, or recurring trap is observed.
4. Momentum discovery: a pattern repeatedly accelerates implementation or debugging.
5. Delivery boundary: immediately before commit/PR/final handoff.

## Workflow

1. Gather evidence.
   - Inspect changed surface (`git status -sb`, `git diff --stat`, targeted `git diff`).
   - Collect executed validation signals and outcomes.
   - Collect failed attempts only when evidenced by commands, logs, diffs, or test output.
2. Distill candidate learnings.
   - Keep only lessons that alter future decisions.
   - Convert narrative into rule form (`When X, prefer Y because Z`).
3. Assign semantic status.
   - Use a concise action status in snake_case.
   - Prefer `do_more` or `do_less` when they fit.
   - Choose a more precise status when needed (for example `investigate_more`, `codify_now`, `avoid_for_now`).
4. Persist immediately.
   - Append each accepted learning to `.learnings.jsonl` in repo root.
   - Use `codex/skills/learnings/scripts/append_learning.py` instead of hand-building JSON.
5. Report concise highlights in chat.
   - Summarize the 1-3 highest leverage learnings.
   - Reference the write result (`.learnings.jsonl` updated, N records appended).

## JSONL Contract

Write one JSON object per line:

```json
{
  "id": "lrn-20260207T173422Z-a91f4e2c",
  "captured_at": "2026-02-07T17:34:22Z",
  "status": "do_more",
  "learning": "Boundary parsing eliminated downstream guard duplication.",
  "evidence": [
    "uv run pytest tests/parser_test.py::test_rejects_invalid passed after boundary parse refactor"
  ],
  "application": "Parse and refine request payloads once at API boundaries.",
  "context": {
    "branch": "main",
    "paths": [
      "src/parser.py",
      "tests/parser_test.py"
    ]
  },
  "source": "skill:learnings",
  "fingerprint": "a91f4e2c6b5d3f10"
}
```

Required keys:
- `id`
- `captured_at`
- `status`
- `learning`
- `evidence`
- `application`
- `source`
- `fingerprint`

Optional keys:
- `context`

## Write Procedure

Use one append call per learning:

```bash
uv run python codex/skills/learnings/scripts/append_learning.py \
  --status do_more \
  --learning "Boundary parsing eliminated downstream guard duplication." \
  --evidence "uv run pytest tests/parser_test.py::test_rejects_invalid passed after boundary parse refactor" \
  --application "Parse and refine request payloads once at API boundaries."
```

The helper script:
- Normalizes `status` to snake_case.
- Defaults `status` to `review_later` when omitted.
- Backfills missing evidence/application with placeholders instead of failing.
- Captures branch and changed paths from git when available.
- Computes a fingerprint for duplicate detection.
- Appends to `.learnings.jsonl` in repo root by default.

## Guardrails

- Ground every learning in observed evidence; do not infer hidden causes as facts.
- Do not write pure changelog bullets; write decision-shaping rules.
- Keep `status` action-oriented and semantically meaningful for the situation.
- Avoid duplicate entries; if a learning already exists, update its evidence context only when materially new.
- If evidence is weak, persist with `review_later` and placeholders, then enrich later.
