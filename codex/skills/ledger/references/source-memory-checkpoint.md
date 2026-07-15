# Source-Memory Checkpoint Contract

## Ownership

Ledger owns checkpoint completeness, freshness, aggregation, and reporting.
Learnings, Synesthesia, and Negative Ledger each own their semantic disposition
and admission gate. `memory-note` owns immutable transport. Phase 2 alone owns
compiled memory.

## Input

Build one bounded `source-memory-checkpoint-input/v1` packet:

```json
{
  "schema": "source-memory-checkpoint-input/v1",
  "checkpoint_id": "SMC-...",
  "trigger": "validation-transition",
  "subject": {
    "repository_id": "owner/repo",
    "head_oid": "<git-oid-or-null>",
    "workspace_fingerprint": "<sha256>"
  },
  "evidence": {
    "decision_delta": "Literal route or conclusion change",
    "validation_transitions": [],
    "attempted_routes": [],
    "user_authority_events": [],
    "changed_paths": [],
    "final_handoff": "Current outcome and next owner"
  }
}
```

Do not embed full logs, transcripts, secrets, or unrelated chronology. Preserve
exact source references and explicit missing values. Fingerprint canonical JSON
for the material subject and evidence objects. The workspace fingerprint must
cover the HEAD-relative index, worktree, and in-scope untracked artifacts in a
staging-stable canonical representation; staging alone must not change it.

## Fixed participant registry

Invoke each participant once with
`checkpoint_context=source-memory-checkpoint/v1`:

| Source | Canonical dispositions |
|---|---|
| Learnings | `appended`, `duplicate-skip`, `no-op`, `blocked` |
| Synesthesia | `appended`, `candidate`, `no-op`, `blocked` |
| Negative Ledger | `mapped`, `captured`, `transitioned`, `no-op`, `blocked` |

Every participant also returns one admission disposition:
`created`, `duplicate-skip`, `not-eligible`, `not-applicable`, or `blocked`.
Canonical IDs and note IDs are present only when compatible with those results.
Canonical writes require proof references; no-write outcomes require a reason.

A participant in checkpoint context must not bootstrap Ledger, invoke the
coordinator, call a sibling participant, or use another participant's result as
authority. Continue the fan-out after a participant failure so the receipt
retains all independent outcomes.

## Receipt

Assemble one stateless `source-memory-checkpoint/v1` receipt with:

- `checkpoint_id`, `trigger`, current subject and evidence fingerprints;
- exactly one object under each of `learnings`, `synesthesia`, and
  `negative-ledger`;
- separate canonical and admission outcomes;
- aggregate `complete`, `degraded`, or `blocked` status.

Validate with:

```bash
ledger validate source-memory-checkpoint --input checkpoint.json
```

Validation is structural and non-authorizing. It never reads or writes a source
store and never decides eligibility.

## Freshness and idempotence

Before reusing a receipt, recompute the subject and evidence fingerprints from
the current packet. Any mismatch makes the receipt stale and blocks only the
claim of clean source-memory closeout until all participants are rerun.

Rerunning an unchanged packet must yield source duplicate/no-op outcomes and
memory-note duplicate skips, never duplicate canonical events. An admission or
digest failure after canonical success is `degraded`; it never converts that
canonical success into failure or triggers rollback.

## Trigger and exclusion boundary

Trigger for material validation transitions, strategy pivots, completed
implementation/review delivery boundaries, pre-commit and PR handoff, terminal
closeout, or an explicit user request. Do not trigger merely for read-only
questions, trivial formatting, an early incomplete red test, or every command.

Negative Ledger pre-route mapping remains an independent online gate. The
lifecycle checkpoint records closeout evidence and does not replace or weaken
that map.

## Checkpoint, reconcile, compile

- `checkpoint`: current-turn evidence to three source dispositions;
- `reconcile`: explicit read-only diagnosis of historical canonical/admission
  gaps, followed by source-authorized selective admission;
- `compile`: Phase 2 consumption of valid new or changed source notes.

Never scan historical stores during every checkpoint, infer source eligibility
inside reconciliation, or edit `memory_summary.md`, `MEMORY.md`, or memory-root
skills.
