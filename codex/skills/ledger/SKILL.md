---
name: ledger
description: "Ensure a `ledger` command is available on PATH for consumer skills, optionally installing the native Zig CLI when it is missing, then coordinate repo-local source-memory stores, Universalist plan addresses, and pure governance-artifact validation without bypassing source-specific authority. Use before a workflow's first Ledger command, when the command is missing, or for ledger status, migration, doctor, harvest planning, memory admission handoff, Universalist plan addressing, or artifact validation."
---

# Ledger

## Mission

Own the shared Ledger bootstrap boundary, coordinate repo-local source-memory
stores under `.ledger/`, and route pure governance-artifact validation.

Use `$ledger` for source-memory migration, cross-store doctor, harvest planning, and memory admission coordination. Do not use it to bypass source-specific authority.

## Bootstrap boundary

Every procedural Ledger consumer must declare this prerequisite: before the
first native Ledger command in a workflow, load this skill and complete
`$ledger ensure` once. That readiness applies to every consumer in the workflow;
do not repeat the bootstrap per skill or per command. `$ledger` is skill syntax,
not a shell command.

Use [scripts/ensure-ledger](scripts/ensure-ledger) as the deterministic bootstrap
handler:

```bash
codex/skills/ledger/scripts/ensure-ledger
```

After the handler emits `ledger-bootstrap-ready/v1`, invoke the native CLI
directly:

```bash
ledger <native-ledger-arguments...>
```

The bootstrap handler checks only that `ledger` resolves on `PATH` and,
when installation authority exists, can install the canonical Homebrew formula.
It does not inspect the CLI version, duplicate CLI integrity checks, or proxy
native commands. A source owner that depends on a minimum version must probe
`ledger --version` after readiness and before mutation; the bootstrap receipt
does not satisfy that compatibility check. Afterward, the native CLI owns
integrity, stdout, stderr, exit status, and failure reporting.

If `ledger` does not resolve on `PATH`:

1. install only when the current user request or standing
   environment policy authorizes user-level CLI provisioning;
2. pass `--install` to the bootstrap handler when that authority exists;
3. otherwise stop with the handler's exact remediation;
4. never use `curl | sh`, an unpinned download, or a second-language Ledger
   implementation.

On supported Homebrew environments the canonical formula is
`tkersey/tap/ledger`. Bootstrap before opening an actuation generation; do not
install during an open generation.

~~~yaml
ledger_bootstrap_ready:
  schema: ledger-bootstrap-ready/v1
  status: ready
  path:
  action: none | installed
~~~

Bootstrap readiness grants no source authority. The calling skill still owns
the semantic operation and every requested write or effect.

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
missing -> legacy-only -> migrated/current
             \                 /
              +---- invalid ---+
```

`legacy-only` is an actionable preflight state. It means reads may use
compatibility fallback, but writes and commit closeout must first run the owning
source migration. For learnings, that owner is
`ledger migrate --source learnings --mode copy`; for negative evidence, that
owner is `ledger migrate --mode copy`. Synesthesia can report `notes-only`
during transition; copy import is explicit through
`ledger migrate --source synesthesia --mode copy`.

For learnings, Ledger `>= 0.5.2` validates the selected canonical or legacy
store and reports `records`, bounded repairs, and invalid physical line spans.
An `invalid` doctor result exits nonzero. Default migration rejects every
remaining invalid record. `--invalid-policy skip` is an explicit partial
projection: it is copy-only, preserves the immutable legacy source, and lists
every skipped span. The learnings skill, not `$ledger`, decides whether the
task authorizes that omission.

Compiled Codex memory is still owned by Phase 2. Memory-source notes are admission snapshots, not canonical stores.

## Trigger Cues

- `$ledger`;
- `$ledger ensure`;
- a skill's first native Ledger command;
- ensure, install, or verify the native Ledger CLI is available;
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

`$ledger` may provision and verify the native CLI, then coordinate, inspect, and
recommend. It does not proxy ordinary native commands. Writes remain delegated
to source-specific skills:

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
4. Run source doctors when available and retain their record counts, repair
   receipts, invalid line spans, and exit status.
5. If any required source is `legacy-only` or `invalid`, or Synesthesia is
   `notes-only` and import is requested, report the exact owning migration or
   blocking command before any harvest or append recommendation. Never convert
   an invalid learnings store with skip unless `$learnings` has established
   that authority.
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

- Bootstrap once before the first Ledger command in a workflow; do not repeat
  it per skill or per command.
- After readiness, invoke `ledger` directly and let the CLI own compatibility,
  integrity, and failures.
- Do not install without current installation authority.
- Do not install during an open actuation generation.
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
