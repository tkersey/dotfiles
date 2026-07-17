---
name: ledger
description: "Ensure a `ledger` command is available on PATH, coordinate the shared Learnings/Synesthesia/Negative Ledger lifecycle checkpoint and repo-local source-memory reconciliation, address Universalist plans and receipts, and route pure artifact validation without bypassing source authority. Use before a workflow's first Ledger command, at material validation or delivery checkpoints, when the command is missing, or for ledger status, migration, doctor, harvest planning, memory-admission handoff, reconciliation, Universalist plan addressing or receipt emission, or artifact validation."
---

# Ledger

## Mission

Own the shared Ledger bootstrap and lifecycle-coordination boundaries,
coordinate repo-local source-memory stores through native source APIs, and
route pure validation of governance and review artifacts.

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
4. never use `curl | sh`, an unpinned download, or an alternate Ledger
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

Canonical source APIs:

- `ledger --source learnings`
- `ledger --source negative-ledger` for negative evidence; source-less commands
  remain a compatibility surface
- `ledger --source synesthesia` when present
- `ledger --source actuation`
- `ledger --source hylo`

Current source-memory persistent-adapter locations, retained for path
compatibility and explicit migration:

- `.ledger/learnings/events.jsonl`
- `.ledger/negative-ledger/events.jsonl`
- `.ledger/synesthesia/events.jsonl` when present

Operational, non-memory stores:

- `.ledger/actuation/events.jsonl` is the current actuation persistent adapter,
  owned exclusively by `ledger --source actuation`; do not harvest it into
  memory or route its writes through source-memory coordination.
- `.ledger/hylo/events.jsonl` is the current Hylo persistent adapter, owned
  exclusively by `ledger --source hylo`; do not harvest it into memory or
  route its writes through source-memory coordination.

Operational, non-memory artifacts:

- `.ledger/universalist/plan-{plan-id}.md`, addressed exclusively by
  `ledger --source universalist`; do not harvest these plans into memory.

Stateless, non-authorizing observations:

- `ledger validate plan-source-contract --input FILE`
- `ledger validate policy-synthesis-receipt --input FILE`
- `ledger validate review-fold --input FILE`
- `ledger validate actuation-review-policy --phase PHASE --input FILE`
- `ledger validate review-resolution --phase PHASE --input FILE`
- `ledger validate source-memory-checkpoint --input FILE`

These commands accept canonical JSON and never read or write `.ledger`. General
governance contracts emit `ledger-validate-decision/v1`; Actuating contracts
emit their domain validation-decision schemas. Ledger 0.7.0 and newer preserve
v1 same-tuple review-policy validation and enforce the v2 certified
cross-tuple standard-clean chain. Source-memory checkpoint coordination requires
Ledger 0.10.0 or newer; probe `ledger --version` before opening that checkpoint.

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
owner is `ledger migrate --source negative-ledger --mode copy`. Synesthesia can report `notes-only`
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

## Source-memory lifecycle checkpoint

At a decision-shaping validation transition, material strategy pivot, delivery
boundary after implementation, pre-commit boundary, PR handoff, terminal
implementation/review closeout, or explicit checkpoint request:

1. Complete `$ledger ensure` once for the workflow and require Ledger 0.10.0 or
   newer. Participants consume that readiness; they do not bootstrap again.
2. Construct one bounded immutable `source-memory-checkpoint-input/v1` packet
   containing current subject identity, literal decision and validation
   evidence, attempted routes, user-authority events, changed paths, and the
   final handoff. Compute subject and evidence SHA-256 fingerprints.
3. Invoke exactly `$learnings`, `$synesthesia`, and `$negative-ledger` with
   `checkpoint_context=source-memory-checkpoint/v1`. Each participant evaluates
   only its source contract, returns exactly one canonical disposition plus one
   admission disposition, and does not invoke Ledger as coordinator or call a
   sibling source.
4. Continue collecting all three results when one participant fails. Canonical
   source writes are independent and append-only; never roll one back because a
   sibling or derived admission stage failed.
5. Assemble `source-memory-checkpoint/v1`, validate it with
   `ledger validate source-memory-checkpoint --input FILE|-`, and retain one
   current receipt. Recompute both fingerprints before reuse; changed code,
   evidence, route, or authority makes the prior receipt stale and requires a
   fresh fan-out.

Aggregate `complete` when every participant evaluated and neither a canonical
nor derived operation is blocked; use `degraded` when semantic evaluation and
canonical writes completed but a note or digest stage failed; use `blocked` for
a missing participant, stale/invalid evidence, or a required canonical failure.
This status proves source-memory closeout only. It does not grant delivery
authority, and the separate exact current Negative Ledger pre-route map remains
the only source-memory route gate.

Evaluation is mandatory; writes and admissions are conditional. Keep ordinary
all-no-op receipts internal. Report source writes, actionable Synesthesia
candidates, derived-stage degradation, and exact blockers. See
[source-memory-checkpoint.md](references/source-memory-checkpoint.md) for the
packet, participant, receipt, freshness, idempotence, and reporting contracts.

## Reconciliation boundary

Lifecycle checkpointing prevents new gaps; it does not scan or admit historical
rows. Run the read-only reconciliation workflow explicitly to compare canonical
records, immutable notes, derived digests, and compiled-memory mentions. The
report may identify `admitted`, `eligible-unadmitted`, `not-eligible`,
`needs-source-review`, `incomplete-projection`, `stale-note`, and
`phase2-lag`; it must not synthesize source eligibility or write notes.

```bash
uv run python \
  codex/skills/ledger/scripts/source-memory-reconcile.py \
  --repo "$(git rev-parse --show-toplevel)" \
  --format text
```

When source owners have reviewed specific historical rows, pass an explicit
`source-memory-eligibility/v1` JSON file via `--eligibility`. Each decision must
name one canonical ID, `eligible|not-eligible`, and a non-empty source-owned
reason. The reconciler uses that input only to distinguish a real admission gap
from an ineligible or unreviewed record; it remains read-only and non-authorizing.

After an owning source explicitly accepts a candidate, use its documented
adapter or native export plus `memory-note`. Keep backfill bounded and auditable;
never bulk-admit every learning or incomplete Negative Ledger projection.

## Trigger Cues

- `$ledger`;
- `$ledger ensure`;
- a skill's first native Ledger command;
- ensure, install, or verify the native Ledger CLI is available;
- ledger status;
- source memory stores;
- migrate learnings;
- memory harvesting;
- source-memory lifecycle checkpoint;
- reconcile canonical source records with memory notes;
- harvest stores for memories;
- why memories are not being captured;
- doctor `.ledger`;
- cross-store memory digest.
- validate PSC-v1, PSR-v1, or RF-v2;
- `ledger validate`.
- create or resolve a Universalist plan;
- find the newest Universalist plan without overwriting an earlier run.
- emit or atomically append a Universalist SDR-v1 decision receipt.

## Authority

`$ledger` may provision and verify the native CLI, then coordinate, inspect, and
recommend. It does not proxy ordinary native commands. Writes remain delegated
to source-specific skills and native source APIs:

- `$learnings` / `ledger --source learnings`; the current compatibility adapter is `.ledger/learnings/events.jsonl`;
- `$negative-ledger` / `ledger --source negative-ledger`; source-less commands
  remain compatible, and the current persistent adapter is
  `.ledger/negative-ledger/events.jsonl`;
- `$synesthesia` / `ledger --source synesthesia`; the current compatibility adapter is `.ledger/synesthesia/events.jsonl`, and current Synesthesia notes remain transition evidence;
- `$memory-source-notes` / `memory-note` for immutable admission snapshots.
- `$actuating` / `ledger --source actuation` for the operational actuation
  event chain; this is not a memory-admission source.
- `$hylo` / `ledger --source hylo` for operational replay-campaign evidence;
  the current compatibility adapter is `.ledger/hylo/events.jsonl`, and this is
  not a memory-admission source.
- `$universalist` owns decision policy, its SKDC-v1 contract, plan templates,
  and ordinary Markdown field updates; `ledger --source universalist` owns plan
  identity, atomic creation, address resolution, SDR-v1 receipt construction,
  Seq validation, and single-receipt atomic append.

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

New plans use `.ledger/universalist/plan-{plan-id}.md`. Exact-id and `latest`
lookup preserve read access to legacy `.ledger/universalist-plan-{plan-id}.md`
files without rewriting them; the namespaced path is canonical when both
layouts contain the same id.

Ledger 0.10.4 or newer, paired with Skills Seq 0.3.51 or newer, emits the
consequential root receipt selected by Universalist:

```bash
ledger emit --source universalist \
  --plan .ledger/universalist/plan-PLAN_ID.md \
  --contract /path/to/universalist/references/decision-contract.yaml \
  --question "Which construction owns this seam?" \
  --selected-route UNI-ORDINARY \
  --rejected-route UNI-CANONICAL \
  --expected-outcome "One owner enforces the observable law." \
  --disposition changed \
  --construction "checked owner-boundary adapter" \
  --law "required observations are preserved" \
  --falsifier "a mismatched source is accepted" \
  --advanced-mechanics none \
  --evidence-ref "code:path" \
  --write-plan
```

The native command preserves the Universalist contract as policy authority,
accepts YAML and JSON SKDC-v1, and consumes Seq's fingerprint, decision-capable
skill kind, parsed identities, and clause-route bindings from one validation of
one immutable contract snapshot. It validates the generated SDR-v1 with that
capability-compatible Skills Seq companion and fails before plan mutation on an
unknown reference, noncanonical write target, invalid receipt, concurrent
writer, or duplicate JSON or YAML receipt. Ledger checks a sibling `seq` before
searching `PATH` and skips same-name binaries that do not advertise the required
receipt-binding projection and receipt-validation capabilities. Without
`--write-plan`, receipt projection leaves the plan unchanged.

## Read-Only Workflow

1. Resolve the git root.
2. Run each native source doctor and path command. Inspect only explicit legacy
   import locations and current Synesthesia notes when migration evidence is
   needed; do not open a current persistent adapter for ordinary reads.
3. Classify each source as `migrated`, `legacy-only`, `current`, `legacy-path`, `notes-only`, `missing`, or `invalid`.
4. Retain source-doctor record counts, repair
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
- Do not persist checkpoint receipts or turn Ledger into a semantic source
  decision engine without evidence that the stateless protocol is insufficient.
- Do not reuse a checkpoint receipt after its subject or evidence fingerprint
  changes.
- Do not admit every source-store event to memory.
- Do not block a route from Negative Ledger memory without current ledger verification.
- Do not turn Synesthesia decorative language into memory.
- Do not migrate, compact, hand-edit, or harvest actuation events as source
  memory; use the actuation source's `doctor`, `state`, and transition commands.
- Do not invent Universalist plan ids, write a replacement latest pointer, or
  reuse an existing plan path; use the Universalist source commands.
- Do not route stateless validation through `--source`; sources own state, while
  `validate` is a pure observation.
