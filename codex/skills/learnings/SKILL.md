---
name: learnings
description: "Capture, browse, query, supersede, migrate, and selectively admit evidence-backed execution learnings from repo-local `.ledger/learnings/learnings.jsonl`. Trigger for `$learnings`, browse/recent/search learnings, lessons learned, takeaways, wrap up, handoff, validation transitions, strategy pivots, footguns, retry loops, or memory admission of a durable learning."
metadata:
  version: "6.0.0"
---

# Learnings

## Mission

Maintain a repo-local, evidence-backed execution-learning store and selectively admit only high-value learning snapshots to the global Codex memory compiler.

Authority split:

```text
<repo>/.ledger/learnings/learnings.jsonl
  canonical detailed learning record

~/.codex/memories/extensions/learnings/notes/*.md
  immutable admission snapshots for Phase 2

memory_summary.md / MEMORY.md / skills/*
  compiled memory written only by Phase 2
```

Do not duplicate every learning into memory notes. For an accepted admission, load `$memory-source-notes` before invoking `run_memory_note_tool`.

## Trigger Cues

- `$learnings`;
- browse, recent, search, rank, or summarize learnings;
- "what do we already know about X";
- lessons learned, takeaways, wrap up, or handoff;
- fail-to-pass, pass-to-fail, timeout-to-stable;
- strategy pivot, footgun, gotcha, retry loop, or acceleration pattern;
- before a Codex-made commit/PR/handoff after material implementation;
- explicit request to promote/admit a learning to memory.

## Canonical Store

```text
.ledger/learnings/learnings.jsonl
```

Use `learnings append` for writes. Do not hand-edit rows in normal operation.
Legacy `.learnings.jsonl` is read only during migration. Use
`learnings migrate --mode copy` to copy old rows into the canonical store.

Rows should preserve `id`, `captured_at`, `status`, `learning`, `evidence`, `application`, `source`, `fingerprint`, `context`, `tags`, `related_ids`, and `supersedes_id`.

## Capture Gate

Capture only when at least one decision-shaping checkpoint occurred:

1. validation transition;
2. strategy pivot;
3. hidden footgun or brittle assumption;
4. repeated acceleration pattern;
5. useful or failed recalled learning;
6. delivery boundary after real implementation work.

Require decision delta, transferability, and counterfactual cost. Prefer one essential learning; append at most three per turn.

## Write Workflow

1. Verify the git root:

   ```bash
   git rev-parse --show-toplevel
   ```

2. Gather exact evidence and changed paths.
3. Distill objective, inflection, proof, and transferable rule.
4. Append from the verified repo root:

   ```bash
   learnings append \
     --status do_more \
     --learning "When X, prefer Y because Z." \
     --evidence "exact command/result/path" \
     --application "Do Y first on the next similar task." \
     --tag example
   ```

5. Verify the reported target path is exactly `<repo>/.ledger/learnings/learnings.jsonl`.
6. Before any Codex-made commit, inspect `.ledger/learnings/learnings.jsonl` explicitly.
7. Emit exactly one canonical learning proof line.

Proof lines:

```text
appended: id=lrn-...
duplicate-skip: <reason>
0 records appended: <reason>
```

## Recall Workflow

```bash
learnings recall \
  --query "<focused component failure objective terms>" \
  --limit 5 \
  --drop-superseded
```

Do not use `recall` as a substitute for current artifact inspection.

## Memory Admission Gate

A learning becomes a custom memory-source note only when all four checks pass:

1. the canonical row exists and its ID is known;
2. evidence is inspectable and embedded in a bounded snapshot;
3. scope and future behavior are clear;
4. Phase 2 consideration would plausibly reduce future steering, retries, or search.

At least one must also hold:

- status is `codify_now`;
- the same theme appears at least three times;
- the user explicitly asks to remember/promote it;
- it captures a stable cross-task preference or operating default;
- it is an unusually high-impact failure shield, repo map, verification path, or stop rule;
- it proves a repeatable procedure suitable for a memory-root skill.

Do not admit every `do_more` row, raw chronology, weak `review_later` candidates, failed-hypothesis exclusions better owned by `negative-ledger`, harness corrections, or synesthetic mappings.

## Learning Admission Payload

After the canonical append succeeds, construct:

```json
{
  "operation": "assert",
  "authority": "learnings-cli",
  "summary": "Admit lrn-... for Phase 2 consideration.",
  "scope": {
    "kind": "repo",
    "repo": "owner/repo",
    "paths": ["src/parser"]
  },
  "source_refs": [
    {
      "kind": "learning",
      "ref": ".ledger/learnings/learnings.jsonl#lrn-...",
      "summary": "Canonical learning row"
    }
  ],
  "related_ids": [],
  "supersedes_id": null,
  "payload": {
    "learning_id": "lrn-...",
    "learning_status": "codify_now",
    "repo": "owner/repo",
    "source_path": ".ledger/learnings/learnings.jsonl",
    "decision_delta": "Future Codex should do Y before Z.",
    "evidence_snapshot": ["exact command/test/result"],
    "future_behavior": "Operational default or route",
    "verification": "Proof or stop condition",
    "tags": ["memory-admission"]
  }
}
```

Then hand off:

```bash
run_memory_note_tool append \
  --extension learnings \
  --kind learning-admission \
  --json -
```

## Admission Proof

Report canonical and admission outcomes separately:

```text
appended: id=lrn-...
memory-note: id=MSN-... extension=learnings kind=learning-admission status=created
```

If the CLI is unavailable:

```text
appended: id=lrn-...
memory-note: not-attempted: cli unavailable
```

A failed memory admission must never roll back or invalidate the canonical learning append.

## Supersession and Withdrawal

When a canonical learning is superseded or withdrawn from memory relevance, append the new canonical row, create a `learning-supersession` or `learning-withdrawal` note, reference the previous memory-source note ID when known, and let Phase 2 update compiled memory surgically.

Never edit or delete prior admission notes.

## Memory Digest Compatibility

`learnings memory-digest` remains useful for disposable batch imports, but it is not the primary durable admission path. Prefer timestamped resources under:

```text
~/.codex/memories/extensions/learnings/resources/YYYY-MM-DDTHH-MM-SS-learnings-digest.md
```

## Relationship to Negative Ledger

A learning can seed negative evidence, but `.ledger/learnings/learnings.jsonl` is not the operational route-exclusion store. Promote witnessed failed hypotheses through `ledger capture`, then use `ledger export` plus `memory-note` for memory admission.

## Guardrails

- Ground every row in observed evidence.
- Write rules, not changelog bullets.
- Do not append from an unverified non-repo cwd.
- Do not write legacy `.learnings.jsonl` after migration.
- Do not force-add local-only source stores.
- Do not manually edit JSONL rows.
- Do not admit every learning to memory.
- Do not write compiled memory directly.
- Do not use source notes to bypass the canonical store.
