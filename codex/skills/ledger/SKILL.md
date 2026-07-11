---
name: ledger
description: "Coordinate repo-local source-memory stores, Universalist plan addresses, and pure Zig governance-artifact validation under `.ledger/` without bypassing source-specific authority. Use for ledger status, migration, doctor, harvest planning, memory admission handoff, Universalist plan create/latest/path lookup, or `ledger validate`."
---

# Ledger

## Mission

Coordinate repo-local source-memory stores under `.ledger/` and route pure
governance-artifact validation.

Use `$ledger` for source-memory migration, cross-store doctor, harvest planning, and memory admission coordination. Do not use it to bypass source-specific authority.

Canonical stores:

- `.ledger/learnings/events.jsonl`
- `.ledger/negative-ledger/events.jsonl`
- `.ledger/synesthesia/events.jsonl` when present

Operational, non-memory store:

- `.ledger/actuation/events.jsonl`, owned exclusively by
  `ledger --source actuation`; do not harvest it into memory or route its writes
  through source-memory coordination.

Operational, non-memory artifacts:

- `.ledger/universalist-plan-{plan-id}.md`, addressed exclusively by
  `ledger --source universalist`; do not harvest these plans into memory.

Stateless, non-authorizing observations:

- `ledger validate plan-source-contract --input FILE`
- `ledger validate policy-synthesis-receipt --input FILE`
- `ledger validate review-fold --input FILE`

These commands accept canonical JSON, emit `ledger-validate-decision/v1`, and
never read or write `.ledger`.

Source-store state model:

```text
missing -> legacy-only -> migrated/current -> invalid
```

`legacy-only` is an actionable preflight state. It means reads may use
compatibility fallback, but writes and commit closeout must first run the owning
source migration. For learnings, that owner is
`ledger migrate --source learnings --mode copy`; for negative evidence, that
owner is `ledger migrate --mode copy`. Synesthesia can report `notes-only`
during transition; copy import is explicit through
`ledger migrate --source synesthesia --mode copy`.

Compiled Codex memory is still owned by Phase 2. Memory-source notes are admission snapshots, not canonical stores.

## Trigger Cues

- `$ledger`;
- ledger status;
- source memory stores;
- migrate learnings;
- memory harvesting;
- harvest stores for memories;
- why memories are not being captured;
- doctor `.ledger`;
- cross-store memory digest.
- validate PSC-v1, PSR-v1, or RF-v2;
- `ledger validate`.
- create or resolve a Universalist plan;
- find the newest Universalist plan without overwriting an earlier run.

## Authority

`$ledger` may coordinate, inspect, and recommend. Writes are delegated to source-specific tools:

- `$learnings` / `ledger --source learnings` for `.ledger/learnings/events.jsonl`;
- `$negative-ledger` / `ledger` for `.ledger/negative-ledger/events.jsonl`;
- `$synesthesia` / `ledger --source synesthesia` for `.ledger/synesthesia/events.jsonl`; current Synesthesia notes remain transition evidence;
- `$memory-source-notes` / `memory-note` for immutable admission snapshots.
- `$actuating` / `ledger --source actuation` for the operational actuation
  event chain; this is not a memory-admission source.
- `$universalist` owns plan contents and updates;
  `ledger --source universalist` owns plan identity, atomic creation, and
  address resolution.

Never write `memory_summary.md`, `MEMORY.md`, or memory-root `skills/*`.

`ledger validate` checks structure and invariants only. A pass verdict never
grants execution or mutation authority; the artifact's domain owner retains
that authority boundary.

## Universalist Plan Workflow

Create a fresh plan from the Universalist-owned template:

```bash
ledger create --source universalist \
  --repo PROJECT_ROOT \
  --template /path/to/universalist/templates/universalist-plan.md
```

Retain the returned `plan_id`; resolve the exact run address with:

```bash
ledger path --source universalist --repo PROJECT_ROOT --id PLAN_ID
```

Recover the newest valid address only when the run id was lost:

```bash
ledger latest --source universalist --repo PROJECT_ROOT
```

Plan ids use `YYYYMMDDTHHMMSSnnnnnnnnnZ-NNNN`. Timestamp order makes the
newest address visible, while atomic ordinal retries prevent overwrite. Treat
`latest` as recovery, not identity: verify the plan's task fields before
resuming because another run may be newer.

## Read-Only Workflow

1. Resolve the git root.
2. Inspect `.ledger/`, previous `.ledger/learnings/learnings.jsonl`, legacy `.learnings.jsonl`, and current Synesthesia notes when present.
3. Classify each store as `migrated`, `legacy-only`, `current`, `legacy-path`, `notes-only`, `missing`, or `invalid`.
4. Run source doctors when available.
5. If any required source is `legacy-only` or Synesthesia is `notes-only` and import is requested, report the exact owning migration
   command before any harvest or append recommendation.
6. Report harvest candidates and recommended source-specific commands.

See [source-store-layout.md](references/source-store-layout.md), [migration-workflow.md](references/migration-workflow.md), and [harvest-workflow.md](references/harvest-workflow.md).

## Output Shape

```md
## Ledger status

- learnings: migrated | legacy-only | missing | invalid
- negative-ledger: current | legacy-path | missing | invalid
- synesthesia: notes-only | ledger-present | missing | invalid

## Harvest candidates

- learnings:
- negative-ledger:
- synesthesia:

## Recommended actions

1. ...

## Proof

- commands run:
- source stores read:
- writes attempted:
- memory-note admissions:
```

## Guardrails

- Do not mutate a source store except through its owning CLI.
- Do not treat memory-source notes as the canonical store.
- Do not admit every source-store event to memory.
- Do not block a route from Negative Ledger memory without current ledger verification.
- Do not turn Synesthesia decorative language into memory.
- Do not migrate, compact, hand-edit, or harvest actuation events as source
  memory; use the actuation source's `doctor`, `state`, and transition commands.
- Do not invent Universalist plan ids, write a replacement latest pointer, or
  reuse an existing plan path; use the Universalist source commands.
- Do not route stateless validation through `--source`; sources own state, while
  `validate` is a pure observation.
