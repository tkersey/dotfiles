---
name: learnings
description: "Capture, browse, query, supersede, migrate, and selectively admit evidence-backed execution learnings through the repo-local `ledger --source learnings` API. Trigger for `$learnings`, browse/recent/search learnings, lessons learned, takeaways, wrap up, handoff, validation transitions, strategy pivots, footguns, retry loops, or memory admission of a durable learning."
metadata:
  version: "7.0.0"
---

# Learnings

## Mission

Maintain a repo-local, evidence-backed execution-learning store and selectively admit only high-value learning snapshots to the global Codex memory compiler.

Authority split:

```text
ledger --source learnings
  canonical learning event API; learning records live under event.record

<repo>/.ledger/learnings/events.jsonl
  current persistent-adapter location; compatibility and migration surface only

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
complete `$ledger ensure`. Learnings doctor/migration recovery requires Ledger
`>= 0.5.2`; after readiness, run `ledger --version` and block or perform an
authorized Homebrew upgrade when the version is older. Only then invoke the
learnings commands directly.

Use `ledger capture --source learnings` for writes and native query, recall,
recent, doctor, and path commands for reads and diagnostics. Treat the source
API and returned learning ID as canonical identity. Do not open or hand-edit
the current persistent adapter during normal operation. Legacy
`.ledger/learnings/learnings.jsonl` and
`.learnings.jsonl` are read only during migration. Use
`ledger migrate --source learnings --mode copy` to copy old rows into the
canonical event store.
Treat `legacy-only` as a required migration state, not a normal operating
state. If `ledger doctor --source learnings` reports `legacy-only`, run
`ledger migrate --source learnings --mode copy` before any append, commit
closeout, or handoff that depends on learning capture.
Treat `invalid` as a blocking state. Inspect the reported physical line spans.
Migration recovers logical multiline objects and reports bounded repairs. It
rejects irreparable records by default. Use `--invalid-policy skip` only when
the task explicitly authorizes retaining valid records despite the reported
invalid spans; it must remain `--mode copy`, preserve the legacy source, and
report every skipped span with a `*_with_skips` status. Never combine skip with `--mode move` or
`--remove-legacy`.

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

If a canonical row passes the admission gate, use the native export below and
return `created`, `duplicate-skip`, or `blocked` with the note proof. If it does
not pass, return `not-eligible`; if no canonical row exists, return
`not-applicable`. An admission failure after a successful append never changes
the canonical disposition.

## Write Workflow

1. Verify the git root:

   ```bash
   git rev-parse --show-toplevel
   ```

2. Run the migration preflight:

   ```bash
   ledger doctor --source learnings
   ```

   If status is `legacy-only`, run:

   ```bash
   ledger migrate --source learnings --dry-run --mode copy
   ledger migrate --source learnings --mode copy
   ledger doctor --source learnings
   ```

   If status is `invalid`, inspect the receipt and stop by default. When the
   task explicitly authorizes source-preserving omission of irreparable rows,
   run:

   ```bash
   ledger migrate --source learnings --dry-run --mode copy --invalid-policy skip
   ledger migrate --source learnings --mode copy --invalid-policy skip
   ledger doctor --source learnings
   ```

   Append only after the doctor status is `migrated`, `current`, or `missing`.
   `missing` is valid only when neither legacy learning path exists.
3. Gather exact evidence and changed paths.
4. Distill objective, inflection, proof, and transferable rule.
5. Append from the verified repo root:

   ```bash
   ledger capture --source learnings \
     --status do_more \
     --learning "When X, prefer Y because Z." \
     --evidence "exact command/result/path" \
     --application "Do Y first on the next similar task." \
     --tag example
   ```

6. Retain the appended learning ID from the capture receipt, then run
   `ledger doctor --source learnings` and a focused native recall or query to
   verify the source remains readable through its API.
7. Before any Codex-made commit, inspect the current learning through native
   Ledger commands. Do not read the persistent adapter directly.
8. Retain exactly one canonical learning proof line in working evidence. Include
   source-memory proof in the final user-facing reply only when it changed
   repo-visible state, needs user action, explains a blocker/error, or the user
   explicitly asks.

Use the disposition invariant above as the internal proof line.

## Recall Workflow

```bash
ledger recall --source learnings \
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

Do not admit every `do_more` row, raw chronology, weak `review_later` candidates, failed-hypothesis exclusions better owned by `negative-ledger`, operating-correction events better handled as standing policy, or synesthetic mappings.

## Native projection and admission

Ledger 0.10.0 or newer is required for authoritative Learnings export. After
the source owner accepts admission, load `$memory-source-notes` and pass the
native deterministic projection to the general writer:

```bash
ledger export --source learnings --id lrn-... --format memory-note |
  run_memory_note_tool append \
    --extension learnings \
    --kind learning-admission \
    --json -
```

Do not reconstruct the payload from prose, `recent`, or query output. Native
export validates the canonical store and fails closed for a missing or
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

## Memory Digest Compatibility

`ledger memory-digest --source learnings` remains useful for disposable batch imports, but it is not the primary durable admission path. Prefer timestamped resources under:

```text
~/.codex/memories/extensions/learnings/resources/YYYY-MM-DDTHH-MM-SS-learnings-digest.md
```

## Relationship to Negative Ledger

A learning can seed negative evidence, but the learning source is not the operational route-exclusion store. Promote witnessed failed hypotheses through `ledger capture --source negative-ledger`, then use native export plus `memory-note` for memory admission.

## Guardrails

- Ground every row in observed evidence.
- Write rules, not changelog bullets.
- Do not append from an unverified non-repo cwd.
- Do not write legacy `.learnings.jsonl` after migration.
- Do not force-add local-only source stores.
- Do not bypass the Ledger API or edit persistent-adapter records directly.
- Do not admit every learning to memory.
- Do not write compiled memory directly.
- Do not use source notes to bypass the canonical store.
- In checkpoint context, do not invoke the coordinator or a sibling participant.
