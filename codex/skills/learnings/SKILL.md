---
name: learnings
description: "Capture, browse, query, supersede, and selectively admit evidence-backed execution learnings through the passive Learnings protocol definition. Trigger for `$learnings`, browse/recent/search learnings, lessons learned, takeaways, wrap up, handoff, validation transitions, strategy pivots, footguns, retry loops, or memory admission of a durable learning."
metadata:
  version: "8.0.0"
---

# Learnings

## Mission

Maintain a repo-local, evidence-backed execution-learning store and selectively admit only high-value learning snapshots to the global Codex memory compiler.

Authority split:

```text
definitions/ledger/learnings-protocol.json
  canonical passive protocol; learning records live under event.record

<repo>/.ledger/learnings/events.jsonl
  canonical repo-local store

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

Before the first native Ledger command in this workflow, load `$ledger` and
complete `$ledger ensure`. Require Ledger 1.x and `ledger-artifact-abi/v1`.
Set:

```bash
learnings_definition="${CODEX_HOME:-$HOME/.codex}/skills/learnings/definitions/ledger/learnings-protocol.json"
```

Use `ledger transact --operation capture` for writes; use definition-bound
`record`, `recent`, `recall`, `search`, `reconciliation-index`, and
`memory-note` projections for reads. Treat the returned `lrn-*` identity as
canonical. Do not open or hand-edit the store. An unbound current-format store
requires the explicit one-shot `bind-existing` transaction and otherwise fails
closed; there is no alternate-path reader.

Rows should preserve `id`, `captured_at`, `status`, `learning`, `evidence`, `application`, `source`, `fingerprint`, `context`, `tags`, `related_ids`, and `supersedes_id`.

Standalone recall, browse, and explicit source-local capture remain Learnings
operations. They do not invoke Synesthesia or open a Ledger lifecycle
checkpoint. When the surrounding work reaches a material lifecycle boundary,
the root `$ledger` coordinator invokes all three participants independently.

## Capture Gate

Capture only when at least one decision-shaping checkpoint occurred:

1. validation transition;
2. strategy pivot;
3. hidden footgun or brittle assumption;
4. repeated acceleration pattern;
5. useful or failed recalled learning;
6. delivery boundary after real implementation work.

Require decision delta, transferability, and counterfactual cost. Prefer one essential learning; append at most three per turn.

## Disposition Invariant

At each triggered execution checkpoint, retain exactly one internal outcome:

```text
learning-disposition: appended id=lrn-...
learning-disposition: duplicate-skip reason=<reason>
learning-disposition: no-op reason=<capture gate not met>
learning-disposition: blocked reason=<doctor, migration, or capture failure>
```

The checkpoint is mandatory; the append is conditional. Do not claim learning
closeout without a disposition. Keep `no-op` and `duplicate-skip` internal
unless the user asks, while `blocked` is user-visible when it affects delivery.

## Ledger checkpoint participant

When invoked with `checkpoint_context=source-memory-checkpoint/v1`, consume the
coordinator's existing Ledger readiness and evidence packet. Do not rerun
`$ledger ensure`, invoke `$ledger` as a lifecycle coordinator, or call
Synesthesia or Negative Ledger.

Project only the packet's decision delta, validation transitions, changed
paths, and final handoff through the existing capture gate. Return exactly one
Learnings disposition plus one admission disposition. Preserve
`appended|duplicate-skip|no-op|blocked`; do not append merely because the
checkpoint is mandatory. A duplicate skip may identify the existing `lrn-*`
row. A no-op or block must state its source-local reason.

If a canonical row passes the admission gate, use the definition projection
below and return `created`, `duplicate-skip`, or `blocked` with the note proof. If it does
not pass, return `not-eligible`; if no canonical row exists, return
`not-applicable`. An admission failure after a successful append never changes
the canonical disposition.

## Write Workflow

1. Verify the git root:

   ```bash
   git rev-parse --show-toplevel
   ```

2. Run the definition-bound doctor:

   ```bash
   ledger doctor \
     --definition "$learnings_definition" \
     --repo "<repo-root>" \
     --format json
   ```

   Append only when the store is `current` or absent. For an unbound
   current-format store, run the explicit `bind-existing` operation once after
   full validation. Stop on every invalid row; do not skip or reinterpret it.
3. Gather exact evidence and changed paths.
4. Distill objective, inflection, proof, and transferable rule.
5. Author `learning.json` as one `submission.record` packet, then append from
   the verified repo root:

   ```bash
   ledger transact \
     --definition "$learnings_definition" \
     --operation capture \
     --repo "<repo-root>" \
     --input submission=learning.json \
     --format json
   ```

6. Retain the appended learning ID, rerun definition-bound doctor, and use a
   focused `record` or `recall` projection to verify readability.
7. Before any Codex-made commit, inspect the current learning through the
   `record` projection. Do not read the store directly.
8. Retain exactly one canonical learning proof line in working evidence. Include
   source-memory proof in the final user-facing reply only when it changed
   repo-visible state, needs user action, explains a blocker/error, or the user
   explicitly asks.

Use the disposition invariant above as the internal proof line.

## Recall Workflow

```bash
ledger project \
  --definition "$learnings_definition" \
  --projection recall \
  --repo "<repo-root>" \
  --param "query=<focused component failure objective terms>" \
  --param limit=5 \
  --format json
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

Do not admit every `do_more` row, raw chronology, weak `review_later` candidates, failed-hypothesis exclusions better owned by `negative-ledger`, operating-correction events better handled as standing policy, or synesthetic mappings.

## Definition projection and admission

After the source owner accepts admission, load `$memory-source-notes` and pass
the deterministic definition projection to the general writer:

```bash
ledger project \
  --definition "$learnings_definition" \
  --projection memory-note \
  --repo "<repo-root>" \
  --param id=lrn-... \
  --payload-only \
  --format json |
  run_memory_note_tool append \
    --extension learnings \
    --kind learning-admission \
    --json -
```

Do not reconstruct the payload from prose, `recent`, or query output. The
projection validates the canonical store and fails closed for a missing or
incomplete row; it does not decide admission eligibility.

## Admission Proof

When admission is user-visible or actionable, report canonical and admission
outcomes separately:

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

## Memory Digest

`$memory-source-notes` owns generated Learnings digests and their timestamped
resources. Ledger supplies only the deterministic source projection.

## Relationship to Negative Ledger

A learning can seed negative evidence, but the learning source is not the
operational route-exclusion store. Promote witnessed failed hypotheses through
the Negative Evidence definition's `capture` transaction, then use its
`memory-note` projection for admission.

## Guardrails

- Ground every row in observed evidence.
- Write rules, not changelog bullets.
- Do not append from an unverified non-repo cwd.
- Do not force-add local-only source stores.
- Do not bypass the Ledger API or edit persistent-adapter records directly.
- Do not admit every learning to memory.
- Do not write compiled memory directly.
- Do not use source notes to bypass the canonical store.
- In checkpoint context, do not invoke the coordinator or a sibling participant.
