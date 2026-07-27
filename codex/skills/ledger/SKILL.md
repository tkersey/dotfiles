---
name: ledger
description: "Ensure a `ledger` command is available on PATH; materialize, validate, record, replay, and project requested Actuating artifacts without taking semantic or execution authority; coordinate the shared Learnings/Synesthesia/Negative Ledger lifecycle checkpoint and repo-local source-memory reconciliation; address Universalist plans and receipts; and perform pure artifact validation."
---

# Ledger

## Mission

Own the shared Ledger bootstrap and lifecycle-coordination boundaries,
coordinate repo-local source-memory stores through owning passive definitions, and
materialize, validate, record, replay, or project requested artifacts without
taking their semantic owners' authority.

Use `$ledger` for definition-bound source-memory migration, cross-store doctor,
harvest planning, and memory admission coordination. Do not use it to bypass
source authority.

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

The bootstrap handler requires Ledger major version 1 and
`ledger-artifact-abi/v1` and, when installation authority exists, can install
the canonical Homebrew formula. It does not proxy native commands. Afterward,
the native CLI owns integrity, stdout, stderr, exit status, and failure
reporting.

If `ledger` does not resolve on `PATH`:

1. install only when the current user request or standing
   environment policy authorizes user-level CLI provisioning;
2. pass `--install` to the bootstrap handler when that authority exists;
3. otherwise stop with the handler's exact remediation;
4. never use `curl | sh`, an unpinned download, or an alternate Ledger
   implementation.

On supported Homebrew environments the canonical formula is
`tkersey/tap/ledger`. Bootstrap before Actuating requests its first Ledger
operation; do not install during an active repository effect.

~~~yaml
ledger_bootstrap_ready:
  schema: ledger-bootstrap-ready/v1
  status: ready
  path:
  version: 1.x
  abi: ledger-artifact-abi/v1
  action: none | installed | upgraded
~~~

Bootstrap readiness grants no semantic authority. The calling skill still owns
the definition path, operation or projection selection, interpretation, and
every requested effect.

Canonical runtime surface:

```text
ledger definition check|describe
ledger validate
ledger materialize
ledger transact
ledger project
ledger doctor
ledger capabilities
ledger version
```

Current source-memory stores:

- `.ledger/learnings/events.jsonl`
- `.ledger/negative-ledger/events.jsonl`
- `.ledger/synesthesia/events.jsonl` when present

Operational, non-memory stores:

- `.ledger/actuation/<safe-goal-id>/evidence.jsonl` is the current per-goal
  Actuating store, admitted only through Actuating's Evidence protocol
  definition; do not harvest it into memory or route its writes through
  source-memory coordination.

Operational, non-memory artifacts:

- `.ledger/universalist/plan-{plan-id}.md`, addressed exclusively through the
  Universalist plan definition; do not harvest these plans into memory.

## Actuating Artifact Kernel boundary

Actuating has four authoritative per-goal artifact families:

```text
goal-contract/v3
counterexample-set/v1
construction-contract/v3
actuating-evidence-event/v1
```

Actuating workflows require Ledger 1.x and `ledger-artifact-abi/v1`.
Construction v1 and v2 stores are unsupported and are not migrated.

Ledger may, when the semantic owner requests it:

- materialize canonical content-addressed documents;
- validate document, event, and supporting-receipt structure;
- append immutable observations with sequence and integrity custody;
- replay recorded observations;
- project requested structural facts and discardable views.

Ledger compiles the selected passive definitions to bounded native plans. No
runtime table may name Actuating or duplicate its lifecycle, review, or closure
laws. The current Review Contract remains an Actuating-owned input: Ledger may
derive its declared identity and validate structural consistency, but it must
not select or reconstruct the contract from hardcoded policy.

`state` and `project` emit disposable structural aids such as registered
artifact references, the Evidence head, recorded event shapes, and unresolved
structural custody. They do not emit semantic workflow state, review credit, a
next action, or a closure verdict.

Ledger never:

- executes or edits repository work;
- dispatches reviews or reads CAS verdict semantics;
- classifies CAS owner facts as a semantic verdict or computes review credit;
- interprets Ship receipts as publication truth;
- classifies Counterexamples or selects a repair;
- selects a Construction or proof strategy;
- chooses Actuating's next action;
- grants mutation authority;
- emits `continue`, `ready-to-ship`, `complete`, or `blocked`;
- authors an `actuating-closure-receipt/v1`.

Actuating owns correct-by-construction implementation, Counterexample
evaluation, Construction selection, orchestration, the next action, and the
semantic closure judgment. `$review-fold` owns Counterexample classification.
CAS owns its attempts and structured receipts. `$ship` alone owns public
effects.

Structural validation returns only named structural claims. It is not semantic
truth, mutation authority, review credit, publication authority, or completion.
A Ledger projection is supporting evidence until Actuating evaluates it with
the current Goal, Construction, Counterexamples, owner receipts, and live
subject.

## Source-memory lifecycle checkpoint

At a decision-shaping validation transition, material strategy pivot, delivery
boundary after implementation, pre-commit boundary, PR handoff, terminal
implementation/review closeout, or explicit checkpoint request:

1. Complete `$ledger ensure` once for the workflow and require Ledger 1.x plus
   `ledger-artifact-abi/v1`. Participants consume that readiness; they do not
   bootstrap again.
2. Construct one bounded immutable `source-memory-checkpoint-input/v1` packet
   containing current subject identity, literal decision and validation
   evidence, attempted routes, user-authority events, changed paths, and the
   final handoff. Compute subject and evidence SHA-256 fingerprints, then
   validate the packet with:

   ```bash
   ledger validate \
     --definition codex/skills/ledger/definitions/ledger/source-memory-checkpoint-input.json \
     --input checkpoint_input=FILE|- \
     --format json
   ```
3. Invoke exactly `$learnings`, `$synesthesia`, and `$negative-ledger` with
   `checkpoint_context=source-memory-checkpoint/v1`. Each participant evaluates
   only its source contract, returns exactly one canonical disposition plus one
   admission disposition, and does not invoke Ledger as coordinator or call a
   sibling source.
4. Continue collecting all three results when one participant fails. Canonical
   source writes are independent and append-only; never roll one back because a
   sibling or derived admission stage failed.
5. Assemble `source-memory-checkpoint/v1`, validate it with the canonical
   passive definition, and retain one current receipt:

   ```bash
   ledger validate \
     --definition codex/skills/ledger/definitions/ledger/source-memory-checkpoint-receipt.json \
     --input checkpoint=FILE|- \
     --format json
   ```

   Recompute both fingerprints before reuse; changed code, evidence, route, or
   authority makes the prior receipt stale and requires a fresh fan-out.

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
- definition-bound Ledger status;
- source memory stores;
- migrate learnings;
- memory harvesting;
- source-memory lifecycle checkpoint;
- reconcile canonical source records with memory notes;
- harvest stores for memories;
- why memories are not being captured;
- doctor `.ledger`;
- cross-store memory digest.
- validate current governance or review artifacts;
- `ledger validate`.
- create or resolve a Universalist plan;
- find the newest Universalist plan without overwriting an earlier run.
- emit or atomically append a Universalist SDR-v1 decision receipt.

## Authority

`$ledger` may provision and verify the native CLI, then coordinate, inspect, and
recommend. It does not proxy ordinary native commands. Writes remain delegated
to owning skills and their canonical definitions:

- `$learnings` owns the Learnings protocol definition and
  `.ledger/learnings/events.jsonl`;
- `$negative-ledger` owns the Negative Evidence protocol definition and
  `.ledger/negative-ledger/events.jsonl`;
- `$synesthesia` owns the Synesthesia protocol definition and
  `.ledger/synesthesia/events.jsonl`;
- `$memory-source-notes` / `memory-note` for immutable admission snapshots.
- `$actuating` owns Actuating semantics and orchestration;
  its definitions validate, transact, and project supporting artifacts and are
  not memory-admission or execution authority.
- `$universalist` owns decision policy, its SKDC-v1 contract, plan templates,
  plan definition, Tune definition imports, and receipt transaction.

Never write `memory_summary.md`, `MEMORY.md`, or memory-root `skills/*`.

`ledger validate` checks structure and invariants only. A pass verdict never
grants execution or mutation authority; the artifact's domain owner retains
that authority boundary.

## Universalist Plan Workflow

Load `$universalist` for its exact definition path, operation names, projection
names, and decision policy. Ledger validates and performs only the selected
structural effect. It does not invoke Seq, discover another executable, accept
YAML decision contracts, select a route, or interpret the receipt as semantic
approval. Unbound or legacy-layout plans fail closed with the definition's
explicit one-shot remediation; no normal read path falls back.

## Read-Only Workflow

1. Resolve the git root.
2. Run `ledger doctor` and `ledger project` with each owning skill's explicit
   definition. Inspect an explicit legacy import location only during a
   one-shot migration; do not open a current store for ordinary reads.
3. Classify each source as `migrated`, `legacy-only`, `current`, `legacy-path`, `notes-only`, `missing`, or `invalid`.
4. Retain source-doctor record counts, repair
   receipts, invalid line spans, and exit status.
5. If any required source is `legacy-only` or `invalid`, or Synesthesia is
   `notes-only` and import is requested, report the exact owning migration or
   blocking command before any harvest or append recommendation. Never convert
   an invalid learnings store with skip unless `$learnings` has established
   that authority.
6. Report harvest candidates and recommended definition-bound commands.

See [source-store-layout.md](references/source-store-layout.md) and
[harvest-workflow.md](references/harvest-workflow.md).

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
- After readiness, invoke `ledger` directly and let the CLI own ABI
  enforcement, integrity, and failures.
- Do not install without current installation authority.
- Do not install during an active Actuating repository effect.
- Do not mutate a source store except through its owning definition and
  `ledger transact`.
- Do not treat memory-source notes as the canonical store.
- Do not persist checkpoint receipts or turn Ledger into a semantic source
  decision engine without evidence that the stateless protocol is insufficient.
- Do not reuse a checkpoint receipt after its subject or evidence fingerprint
  changes.
- Do not admit every source-store event to memory.
- Do not block a route from Negative Ledger memory without current ledger verification.
- Do not turn Synesthesia decorative language into memory.
- Do not migrate, compact, hand-edit, or harvest Actuating evidence as source
  memory; use only Ledger's generated structural artifact surface at
  Actuating's request.
- Do not invent Universalist plan ids, write a replacement latest pointer, or
  reuse an existing plan path; use the Universalist definition.
- Keep `ledger validate` pure: no `.ledger` read, `.ledger` write, or semantic
  authority.
