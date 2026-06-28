# Learnings Memory Source Adapter

Use this file only during Codex Phase 2 memory consolidation.

## Role and Authority

This extension interprets selectively admitted snapshots of repo-local execution learnings.

Canonical detailed records remain:

```text
<repo>/.ledger/learnings/learnings.jsonl
```

The extension intake is:

```text
extensions/learnings/notes/*.md
```

A note is an immutable admission snapshot proving that a specific canonical row should be considered by Phase 2. It is not a replacement for the row and not a runtime instruction. Legacy `.learnings.jsonl` may be consulted only as migration evidence.

## Primary Source

Process valid new/changed `memory-source-note/v1` events in `notes/`, especially those shown by `phase2_workspace_diff.md`.

Supported kinds:

```text
learning-admission
learning-confirmation
learning-supersession
learning-withdrawal
```

## Required Admission Payload

```text
learning_id
learning_status
repo
source_path
decision_delta
evidence_snapshot
future_behavior
verification
tags
```

The envelope must also include authority, scope, source refs, fingerprint, and note ID.

Do not promote merely because a learning exists or has status `do_more`.

## Operation Semantics

- `assert`/`learning-admission`: consider current row for promotion;
- `confirm`: strengthen an existing compiled rule without duplicating it;
- `supersede`: update the compiled rule using the new canonical learning and remove stale guidance supported only by the old event;
- `retract`/`learning-withdrawal`: remove support unless independent evidence remains;
- `reject`: do not promote;
- `reopen`: renewed evidence gathering, not automatic restoration.

Never mutate or delete source notes or `.ledger/learnings/learnings.jsonl`.

## Promotion Gate

Require future decision delta, concrete evidence anchor, clear scope, and actionable default, trigger, failure shield, route, verification rule, or procedure.

Prefer promotion when status is `codify_now`, the theme repeats, it expresses a stable user operating preference, it is a high-value failure shield/repo map/command/verification path, or it would save future steering/retries/search.

## Artifact Targeting

- `memory_summary.md`: compact cross-task defaults and routing only.
- `MEMORY.md`: use task-group structure with learning id, status, scope, evidence anchor, future behavior, verification, and `source_note_ids`.
- `skills/*`: only when multiple learnings prove a repeatable procedure.
- `none`: weak, duplicate, task-local, superseded, retracted, or already-codified material.

## Negative-Ledger Boundary

A learning may seed a negative-ledger capture. It does not itself create an active route exclusion. Let the negative-ledger extension own compiled route constraints after a canonical `NEG-*` projection is admitted.

## Security and Hygiene

- no secrets or unbounded evidence blobs;
- no arbitrary repo scans;
- no source-log mutation;
- preserve exact IDs, commands, errors, paths, and test names when retrieval-relevant;
- no direct edits to compiled memory outside Phase 2.
