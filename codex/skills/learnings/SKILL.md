---
name: learnings
description: "Capture and persist evidence-backed execution learnings into `.learnings.jsonl`. Trigger cues/keywords: `$learnings`, lessons learned, takeaways, wrap up, handoff, before commit/PR, after tests pass, fail->pass, strategy pivot, footgun, retry loop."
---

# Learnings

## Overview

Capture durable lessons as soon as evidence appears, not only at explicit retrospective requests.
Write each validated learning as JSONL so future agents can reuse successful patterns and avoid footguns quickly.

## Trigger cues

- `$learnings`
- "lessons learned" / "takeaways" / "wrap up" / "handoff"
- Before commit/PR/ship; after a proof signal changes state (`fail->pass`)
- "strategy pivot" / "footgun" / "gotcha" / "retry loop"

## Operating Contract (Auto-Capture)

- Allowed to run automatically at the end of an implementation turn (success or paused) and at delivery boundaries (commit/PR/handoff).
- Best-effort and non-blocking: never require extra context; if evidence is thin, either write nothing or persist `review_later` with placeholders.
- Noise control: if no Capture Checkpoint occurred or nothing decision-shaping emerged, append 0 records; otherwise prefer 1 record (max 3).

## Capture Checkpoints

Capture at least once per coding turn when any of these checkpoints occurs:

1. Validation transition: a signal changes state (`fail->pass`, `pass->fail`, `timeout->stable`).
2. Strategy pivot: an approach is abandoned, replaced, or simplified.
3. Footgun discovery: hidden risk, brittle assumption, or recurring trap is observed.
4. Momentum discovery: a pattern repeatedly accelerates implementation or debugging.
5. Delivery boundary: immediately before commit/PR/final handoff.

Auto-trigger rule: if none of these checkpoints occurred and nothing decision-shaping emerged, do not append anything.

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
   - Append each accepted learning to `.learnings.jsonl` in repo root (0 records is valid when nothing qualifies).
   - Use `codex/skills/learnings/scripts/append_learning.py` instead of hand-building JSON.
5. Report concise highlights in chat.
   - Summarize the 1-3 highest leverage learnings (or say none).
   - Reference the write result (`.learnings.jsonl` updated, N records appended, or duplicate-skip).

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
  "tags": [
    "api",
    "testing"
  ],
  "context": {
    "repo": "owner/repo",
    "branch": "main",
    "paths": [
      "src/parser.py",
      "tests/parser_test.py"
    ]
  },
  "related_ids": [
    "lrn-20260130T120000Z-deadbeef"
  ],
  "supersedes_id": "lrn-20260101T090000Z-cafebabe",
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
- `tags`
- `related_ids`
- `supersedes_id`

## Write Procedure

Use one append call per learning:

```bash
uv run python codex/skills/learnings/scripts/append_learning.py \
  --status do_more \
  --learning "Boundary parsing eliminated downstream guard duplication." \
  --evidence "uv run pytest tests/parser_test.py::test_rejects_invalid passed after boundary parse refactor" \
  --application "Parse and refine request payloads once at API boundaries." \
  --tag api \
  --tag testing
```

The helper script:
- Normalizes `status` to snake_case.
- Defaults `status` to `review_later` when omitted.
- Backfills missing evidence/application with placeholders instead of failing.
- Captures a best-effort repo slug from `remote.origin.url` (or falls back to repo dir name).
- Captures branch and changed paths from git when available.
- Computes a fingerprint for duplicate detection.
- Appends to `.learnings.jsonl` in repo root by default.

## Mining, Recall, and Codify Loop

Use the miner script to leverage learnings at task start and to promote repeated items into durable policy.

CLI:

```bash
uv run python codex/skills/learnings/scripts/learnings.py datasets
uv run python codex/skills/learnings/scripts/learnings.py query --spec @codex/skills/learnings/specs/status-rank.json
uv run python codex/skills/learnings/scripts/learnings.py recall --query "fix flaky pre-commit hook" --limit 5
uv run python codex/skills/learnings/scripts/learnings.py codify-candidates --min-count 3 --limit 20
```

Promotion rule of thumb:
- If a learning is repeated (theme appears >= 3 times) or status is `codify_now`, promote it into durable docs (for example `codex/AGENTS.md` or a relevant skill doc).
- After codifying, append a follow-up learning referencing the durable anchor (use `--related-id`/`--supersedes-id` and a `codified` tag).

## Guardrails

- Ground every learning in observed evidence; do not infer hidden causes as facts.
- Do not write pure changelog bullets; write decision-shaping rules.
- Keep `status` action-oriented and semantically meaningful for the situation.
- Avoid duplicate entries; the helper script skips exact duplicates by fingerprint.
  - If you have materially new evidence for an existing learning, append a follow-up record (adjust `status` and/or make the `learning` statement more specific) or re-run with `--allow-duplicate` intentionally.
  - Do not hand-edit existing JSONL lines in place.
- If evidence is weak, persist with `review_later` and placeholders, then enrich later.
