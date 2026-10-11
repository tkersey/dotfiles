# Learnings Memory Source Adapter

Use this file only during Codex Phase 2 memory consolidation.

## Role and Authority

Interpret selectively admitted execution learnings. `$learnings` owns their
semantics; `$ledger` selects their canonical personal store independently of a
Git checkout. Managed scope uses `ledger-repository:<store_id>`. Retain the
scope and source references actually present in each historical snapshot.

The extension intake is:

```text
extensions/learnings/notes/*.md
```

A note is an immutable admission snapshot for Phase 2 consideration. Its
presence proves neither promotion nor later behavioral value. It does not
replace the canonical row or grant runtime authority. The payload's
`.ledger/learnings/events.jsonl` locator is relative to its selected native
store, not an instruction to read a working directory with a matching name.
Do not discover or migrate legacy source stores during consolidation.

Copy this instruction file as a regular file to the `instructions_path`
reported by native `memory-note path --extension learnings --format json`.
Interpret only notes in that selected memory root; do not read another version
as an implicit fallback.

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

Never mutate or delete source notes or canonical learning records.

## Promotion Gate

Require future decision delta, concrete evidence anchor, clear scope, and actionable default, trigger, failure shield, route, verification rule, or procedure.

Prefer promotion when status is `codify_now`, the theme repeats, it expresses a stable user operating preference, it is a high-value failure shield/repo map/command/verification path, or it would save future steering/retries/search.

## Artifact Targeting

Follow the active Phase 2 output contract. V2 produces only a compact
`memory_summary.md` under its context budget. Promote a high-value default or
retrieval route with the scope and verification needed to use it safely. Keep
full evidence, canonical fields, and chronology in immutable source notes. An
exact `MSN-*` reference can provide a retrieval route when useful; do not add
every source field merely as a receipt.

V1 may additionally permit task-group entries in `MEMORY.md` or proven reusable
procedures in `skills/*`. Their availability in v1 does not require or permit
creating them in v2. Select `none` for weak, duplicate, task-local, superseded,
retracted, already-codified, or insufficiently valuable material.

## Negative-Ledger Boundary

A learning may seed a negative-ledger capture. It does not itself create an active route exclusion. Let the negative-ledger extension own compiled route constraints after a canonical `NEG-*` projection is admitted.

## Security and Hygiene

- no secrets or unbounded evidence blobs;
- no arbitrary repo scans;
- no source-log mutation;
- preserve exact IDs, commands, errors, paths, and test names when retrieval-relevant;
- no direct edits to compiled memory outside Phase 2.
