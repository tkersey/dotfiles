# Ledger: specification-driven storage lifecycles

**Specification ID:** `ledger-storage-lifecycle-v1`
**Status:** implementation specification; not an implemented or released feature
**Target:** `tkersey/skills-zig`, principally `apps/ledger` and reusable storage libraries
**Companion:** the Ledger guidance changes in `tkersey/dotfiles`
**Design date:** October 28, 2026, America/Los_Angeles

This document is the single implementation contract for the native work. It
supersedes the earlier suggestion to create a skill-aware `ledger-custody`
product. Implement generic Ledger capabilities, not domain cleanup branches.
The command names and schemas below are proposed native interfaces. They must
not be used against the currently installed baseline merely because this spec
exists. MUST, MUST NOT, and SHOULD express requirements in this document.

## 1. Outcome and scope

Ledger follows passive owner specifications to validate, materialize, write,
retain, replay, and project artifacts. Extend that contract so it can also
account for storage, enforce declared lifetimes, safely reclaim eligible
representations, prevent retry amplification, and report emerging resource
problems before avoidable growth disrupts work.

A new owner protocol expressible in the supported vocabulary MUST require only
new definitions, explicit inputs, and fixtures: no native source edit, owner-name
registry, or Ledger release. The native engine MUST NOT know what a review,
learning, task, worktree, or particular model session means.

Deliver:

1. A bounded passive lifecycle extension, with explicit retaining references,
   release transitions, holds, and conservative defaults.
2. Generic native accounting, admission reservations, bounded maintenance,
   exact dependency enumeration, and safe reclamation.
3. Selected-definition preparation that excludes unrelated payload, preserves
   provenance, and reuses evidence across failed retries. Preserve broad
   historical transport as a distinct explicit scope.
4. Structured health and failure results; maintenance failure never disguises
   a committed semantic transaction as an uncommitted write.
5. Legacy classification, format fencing, compatibility and crash tests,
   release qualification, and a documented host/adapter cutover contract.

This is NOT a general backup service, a remote tiering product, a new workflow
engine, a semantic log-compaction feature, or an excuse to move Git discovery
into Ledger. No new executable is required. Use the existing Ledger executable
and shared native modules. Refactor the current machinery rather than creating
an independent second storage implementation.

## 2. Evidence and verified baseline

The source snapshots examined for this specification are:

- `dotfiles`: `52f0cc9be529be647b80ccef21fc60b28ad502a2`; its Ledger helper is
  unchanged from the incident's `9b2864f529dacbb044ef033edc0db96b128306a0`.
- `skills-zig`: `d92e5e3cf10c203c4515af534aa489195ff7c5db`;
  `apps/ledger/VERSION` reports `1.5.5`.

Refresh main before implementation, preserve intervening work, and adapt
internal module placement to the actual current tree. These pins identify the
analysis baseline, not permission to overwrite newer changes.

The supplied incident report establishes a sufficient inventory-limit mechanism,
not an exact replay of the original failed invocation. Its selected history was
261,736 bytes. The removed archive contained 1,801,170,721 regular-file bytes;
98.42% was unrelated CAS payload. Reconstructed eligible archived payload alone
was 2,937,301,833 bytes, above the 2 GiB limit. Cleanup reclaimed logical file
bytes, not measured filesystem blocks, and did not establish restored migration.

The inspected helper adds enclosing archived worktree roots to selected-owner
inventory, inventories whole `.ledger` trees, fingerprints source paths, and
publishes an archive before completing preparation. An unchanged failed retry
can therefore rediscover its own transport copies as new sources. Healthy
ordinary access already has a path that avoids archive enumeration; preserve it.

The earlier isolated Python component probes are test ideas, not native runtime
qualification: they demonstrated retry amplification, a written manifest with
129 sources rejected by a 128-source reader limit, and inconsistent size/digest
accounting when a file grew between stat and hashing. Recreate those conditions
against the new native implementation. Do not claim those probes proved the
health of any live user store.

### Source anchors

- [Incident helper](https://github.com/tkersey/dotfiles/blob/9b2864f529dacbb044ef033edc0db96b128306a0/agents/skills/ledger/scripts/ensure_custody.py)
- [Context and identity selection](https://github.com/tkersey/dotfiles/blob/52f0cc9be529be647b80ccef21fc60b28ad502a2/agents/skills/ledger/scripts/ledger_context.py)
- [Existing owner-preparation tests](https://github.com/tkersey/dotfiles/blob/52f0cc9be529be647b80ccef21fc60b28ad502a2/agents/skills/ledger/tests/test_owner_upgrade.py)
- [Native managed-root contract](https://github.com/tkersey/skills-zig/blob/d92e5e3cf10c203c4515af534aa489195ff7c5db/apps/ledger/STORAGE.md)
- [Native runtime and release surfaces](https://github.com/tkersey/skills-zig/blob/d92e5e3cf10c203c4515af534aa489195ff7c5db/apps/ledger/README.md)
- [Revision archives](https://github.com/tkersey/skills-zig/blob/d92e5e3cf10c203c4515af534aa489195ff7c5db/apps/ledger/src/v1/revision_archive.zig)
- [Transactions](https://github.com/tkersey/skills-zig/blob/d92e5e3cf10c203c4515af534aa489195ff7c5db/apps/ledger/src/v1/transaction.zig)
- [Monorepo libraries and release rules](https://github.com/tkersey/skills-zig/blob/d92e5e3cf10c203c4515af534aa489195ff7c5db/README.md)

The incident report is the user-supplied
`Pasted markdown(20261029-031056).md`, titled *Ledger migration incident: cause,
cleanup, and a bounded recovery design*. Its observations motivate this design;
all new schemas, algorithms, and acceptance criteria below are proposed work.

## 3. Ownership and authority

| Layer | Owns | Must not own |
| --- | --- | --- |
| Passive owner definition | Artifact structure, protocol transitions, retention obligations, retaining/provenance reference meaning | Executable hooks, absolute output roots, budgets for other owners, hidden discovery |
| Native Ledger | Compilation, custody dependencies, identities, accounting, transaction safety, bounded preservation and reclamation | Owner-specific verdicts, choice among divergent histories, Git or personal-home discovery |
| Generic shared storage libraries | Safe filesystem access, atomic publication, reservation/recovery mechanics where reusable | Skill names, workflow states, application cleanup policy |
| Host integration | Explicit root/catalog selection, trusted owner selection, budgets, periodic invocation and alert delivery | A second implementation of native locking/copying/reclamation or inferred semantic deletion authority |

`authority_granted: false` remains meaningful: enforcement reports what a
selected law and operation established; it grants no new capture, publication,
review-credit, or closure authority. An explicitly activated lifecycle definition
plus the installed host's standing maintenance policy permits routine eligible
maintenance without asking the user for each run. It does not permit weakening
retention, deleting foreign data, installing software, or selecting a new root.

Pure validation/materialization MUST remain store-independent and nonmutating.
Read-only commands and explicit no-maintenance contexts MUST not create lock
files, caches, indexes, catalog entries, or maintenance state. Necessary OS-held
read coordination may use already-existing resources without persistent writes.
Failure to coordinate read-only inspection is an explicit incomplete/busy result,
not an invitation to create control files.

## 4. Hard invariants

**L1 — Preserve meaning.** Required canonical records, identities, order,
provenance, projections, replay, and idempotency outcomes remain unchanged.
Maintenance cannot weaken bindings or declare missing history empty.

**L2 — Complete obligations before deletion.** An artifact is eligible only
when its declared retention, native dependencies, holds, recovery/reader pins,
and required redundancy all permit release. Unknown obligations retain it.

**L3 — Scope independence.** With selected evidence and shared native control
state fixed, changes to unrelated opaque payload do not change selected-owner
preservation results or cause it to read/copy that payload. Broad historical
preservation is a separate scope.

**L4 — Stable failed retries.** With identical original observations, definition
closure, and target state, retrying any interrupted stage does not create another
bulk preservation generation or count transport copies as new observations.
Bounded diagnostic counters may change; preserved payload and provenance do not
grow merely with the number of retries.

**L5 — One snapshot.** Accepted byte count, digest, and copied content describe
the same bounded captured stream. A pre-read stat is not the accepted size.

**L6 — Publication and accounting agree.** Committed artifacts are discoverable
by the native lifecycle inventory, and committed accounting cannot certify
unpublished bytes. Recovery resolves every interrupted publication state.

**L7 — Concurrency safety.** No writer, reader, reference addition, or recovery
can race reclamation into a dangling required reference or lost required bytes.
Do not infer quiescence from an old timestamp, absent PID, or lease age.

**L8 — Bounded work and overhead.** Scanning, hashing, staging, planning,
diagnostics, reservations, indexes, and maintenance history have explicit limits.
Maintenance must not generate its own unbounded archive or event stream.

**L9 — Honest outcomes.** Integrity, capacity, maintenance status, and semantic
commit outcome remain distinct. A committed operation cannot become retryable
merely because later housekeeping or notification failed.

**L10 — Compatibility is explicit.** Legacy data is retained conservatively.
Newly enabled stores reject incompatible old readers/writers before a successful
operation; no unmanaged-root fallback bypasses the fence.

## 5. Artifact model and retaining graph

### 5.1 Identity is not a path

Use a native artifact handle with these logical fields:

```json
{
  "schema": "ledger-artifact-reference/v1",
  "store_id": "opaque-existing-store-id",
  "slot_id": "example/protocol::attachments",
  "instance_id": "opaque-native-instance-id",
  "content_id": "sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
}
```

`slot_id` is the immutable definition ID plus logical slot name, qualified and
validated by the compiler; it is not a user-supplied filesystem path. An instance
identifies a publication/lifetime, while `content_id` identifies exact bytes.
Creating the same bytes in a genuinely new operation may create a new instance.
Retrying the same idempotent create MUST return the original instance, including
its released/reclaimed status, and MUST NOT resurrect expired payload.

The implementation may reuse an existing native identity representation when it
has these semantics. It must publish the canonical encoding and bounds in the
native ABI fixtures. Handles cannot silently retarget when a pathname is reused.
Retained copies share content only where immutability and custody scope permit;
content equality does not merge logical instances or original observations.

### 5.2 Required roots

The retaining graph roots include unexpired owner obligations, retaining
references from retained sources, explicit owner holds, active transaction and
reader pins, required recovery objects, native replay/idempotency dependencies,
and explicitly required independent recovery copies.

Every retained artifact's transitive native dependency closure is retained.
Cycles are handled as strongly connected sets: a cycle with no root may be
reclaimed only when all members' rules permit it and reference coverage is
complete. Reference counting alone MUST NOT be the source of deletion authority.
A bounded mark/reconcile implementation is sufficient; no graph service is needed.

Native dependencies are mandatory even if an owner marks an object releasable.
In particular, definition closures, event bindings, revision archives needed for
replay, and historical ordering data are not disposable caches. Sorted folds or
full-history doctor behavior cannot be weakened by reclamation.

### 5.3 Closed reference scope

Version 1 supports authoritative retaining references within one selected store.
Cross-store retaining references are rejected with a structured unsupported
composition error; cross-store provenance locators are allowed but confer no
retention guarantee and are not dereferenced during collection. Do not implement
an unsafe cross-store collector as an incidental convenience.

External readers that require future availability must participate through an
explicit hold, or their artifacts remain under conservative retention during
adoption. A search for filenames in arbitrary files is not proof of complete
reference coverage. The integration must identify and cut over legacy writers
and retaining consumers before enabling destructive maintenance.

Selected-owner lookup does not require validating every unrelated owner. A
collection operation involving shared objects, however, must establish complete
reference coverage for those objects across the admitted store. An unreadable
owner or unknown writer blocks that deletion, not healthy unrelated access.

## 6. Passive lifecycle extension

### 6.1 Capability and defaults

Keep existing definitions and their archived closure bytes unchanged. Add an
optional top-level `lifecycle` section to `ledger-artifact-definition/v1`, gated
by a new required native operator `artifact-lifecycle` version 1. Register it
through the existing operator requirement mechanism; advertise the exact version
in capabilities. Do not invent an alternative loader or silently ignore unknown
lifecycle fields on old runtimes.

Definitions without lifecycle declarations retain their current semantics and
receive conservative owner-data retention. No default TTL applies to old data.
Internal overhead is reclaimable only where native protocol knowledge proves it
unneeded; missing lifecycle metadata never makes semantic data garbage.

The lifecycle section is part of the canonical definition closure/digest. Compile
it through the same bounded, passive plan path and shared JSON rules as the rest
of the definition. Reject duplicate keys, unknown fields, inconsistent slot
names, unsupported compositions, and non-finite/unbounded numeric values.

### 6.2 Normative grammar

The following fragment defines the new section; it is not a standalone complete
owner definition. Existing shape, storage, transition, and identity declarations
are still required.

```json
{
  "lifecycle": {
    "schema": "ledger-artifact-lifecycle/v1",
    "slots": {
      "events": {"retention": {"kind": "retain"}},
      "attachments": {
        "retention": {"kind": "until-release", "grace_seconds": 604800}
      }
    },
    "references": [
      {
        "source_slot": "events",
        "pointer": "/attachment",
        "cardinality": "optional-one",
        "strength": "provenance"
      }
    ],
    "operations": {
      "finish": [
        {
          "op": "release",
          "artifact": {"input": "submission", "pointer": "/attachment"}
        }
      ],
      "pin": [
        {
          "op": "hold",
          "artifact": {"input": "submission", "pointer": "/attachment"},
          "hold_id": {"input": "submission", "pointer": "/hold_id"}
        }
      ],
      "unpin": [
        {
          "op": "release-hold",
          "artifact": {"input": "submission", "pointer": "/attachment"},
          "hold_id": {"input": "submission", "pointer": "/hold_id"}
        }
      ]
    },
    "bounds": {
      "max_references_per_record": 64,
      "max_effects_per_operation": 16,
      "max_holds_per_artifact": 64
    }
  }
}
```

Closed grammar and semantics:

- `slots` maps declared logical storage slot names to exactly one `retention`
  object. Unmentioned slots retain by default. `retain` has no additional fields.
  `until-release` requires a nonnegative integer `grace_seconds`, bounded by the
  compiler's advertised maximum. It is valid only for independently reclaimable
  attachment slots in version 1, not canonical event logs or addressed documents
  with mandatory historical replay dependencies.
- `references` is a bounded array. `source_slot` names a declared canonical JSON
  document/event slot. `pointer` is a standard JSON Pointer into the canonical
  document or the canonical event record (not its storage envelope). No recursive
  path expressions, executable predicates, or wildcard globbing is added.
- `cardinality` is exactly `one`, `optional-one`, or `many`; `many` selects a
  bounded array at that pointer. Values must be native artifact-reference/v1
  objects. Missing optional-one means no edge; malformed values never mean no
  edge. Required missing pointers reject admission/replay.
- `strength` is `retain` or `provenance`. Retain creates a retaining edge for
  every retained source record/revision, not merely its current folded state.
  Provenance records the handle but explicitly does not promise payload
  availability. A later definition cannot retroactively weaken archived edges.
- `operations` maps existing operation names to bounded arrays of lifecycle
  effects. The owner's ordinary validation/transition law must succeed before
  any effect commits. Native code does not infer completion from an operation
  name, status string, review result, or timestamp.
- A selector is exactly `{input, pointer}` and refers to a declared, validated
  JSON input. Resolve it before effects; the result must be the required handle
  or bounded hold-ID string. Arbitrary source paths and ambient lookups are
  forbidden. Parameter-based selectors can be added only through the same
  explicitly versioned generic operator extension, not undocumented shortcuts.
- `release` releases the selected instance's initial retention obligation once.
  Only the definition authority owning the target slot may release its initial
  obligation. Duplicate release is an idempotent no-op and cannot restart or
  shorten its clock. A `retain` slot rejects release. Release is not physical deletion.
- `hold` adds an idempotent hold scoped to the artifact and declaring definition
  authority. `release-hold` removes only that exact authority's matching hold;
  it cannot remove another owner's hold by guessing an ID. Ordinary operation
  preconditions and expected-revision controls still apply. Unknown holds return
  a declared no-op/not-found result, never bulk release.
- All effects commit atomically with the semantic operation and use its existing
  idempotency/revision semantics. There is no script invocation, second loosely
  coupled write, or user-authored timestamp that can backdate release.
- Bounds cannot exceed native maxima advertised by capabilities. Proposed initial
  maxima: 256 lifecycle slot declarations, 256 reference declarations, 4,096
  references per record, 128 lifecycle effects per operation, 1,024 holds per
  artifact, and grace intervals up to 315,576,000 seconds. These are parser and
  per-operation bounds, not lifetime limits on the number of retained artifacts.
  Exercise exact boundaries and overflow handling; final constants are ABI data.

The example's numbers are fixture values, not retention defaults for real owners.
No active owner is automatically assigned a seven-day retention policy.

### 6.3 Independently reclaimable attachments

To avoid pretending that historical document revisions are disposable, add a
small generic attachment facility. An attachment is immutable explicitly supplied
payload with a native descriptor; it is not a new application log subsystem.

Add input codec `bytes` with a declared maximum and streaming digest validation.
Add logical slot kind `attachment`, codec `bytes`, and a bounded publish effect
that consumes one explicitly named byte input. The descriptor consists of its
native handle, exact byte length, and publication identity; output descriptor
selection must reuse the runtime's generated-output mechanism where possible.
The publish effect is exactly
`{"op":"publish-attachment","slot":"attachments","input":"payload"}`;
`slot` names the attachment slot and `input` its declared bounded bytes input.
An attachment slot is exactly
`{"kind":"attachment","codec":"bytes","max_bytes":1048576}` in the existing
logical slot map; the example limit is not a global default. Unlike owner-path
slots, its physical immutable instance/object paths are runtime-managed beneath
the admitted control root. Publish this canonical schema and complete owner
fixtures alongside the lifecycle schema. The effect returns one descriptor and
uses the enclosing transaction's idempotency key plus compiled effect identity.
Any operation that publishes an attachment must use native idempotency; missing
keys reject before payload publication. Multiple effects have distinct instance
identities while retaining one atomic transaction outcome. Definitions cannot set physical
paths outside their selected control root or supply an arbitrary instance ID.

Attachment payload MUST NOT be required to replay canonical control history.
The compiler rejects laws, identity derivations, or projections that claim to
reconstruct expired payload from a descriptor. Content validation occurs while
payload is present; retained descriptor history proves the committed identity
and lifecycle disposition, not a new validation of absent bytes.

Canonical JSON/event records may retain a descriptor, declare a retaining edge,
or keep a nonretaining provenance locator. A retained reference pins the payload
even after release. A record that merely observes the prior existence of an
attachment uses provenance strength explicitly. This choice belongs to the owner.

An expired attachment read returns `ArtifactReclaimed` with its descriptor and
witnessed disposition; never empty content, fabricated content, or `FileNotFound`
masquerading as initial absence. Unexpected missing retained payload is corruption.
Digest/length descriptors and terminal dispositions needed for replay/idempotency
remain retained under their own obligations. Their cost is measured, not hidden.

Do not migrate existing canonical documents or CAS logs into attachments merely
to make them deletable. Each owner needs a separate explicit, tested adoption.
Generic fixtures must cover at least a generated-report protocol, a build-output
protocol, and a measurement-diagnostics protocol using identical native code.

## 7. Runtime lifetimes and reclamation eligibility

Owner data and native overhead are distinct. Native overhead has protocol-defined
lifetimes without owner declarations for internal filenames.

| Artifact | Retention/release rule |
| --- | --- |
| Canonical event segments and bound document revisions | Retain every byte needed by the existing replay/idempotency/integrity contract; no semantic history truncation in this feature |
| Archived definition closure and binding history | Retain while any admitted historical/current law, binding, or recovery depends on it |
| Active transaction journal/staging | Pin until native recovery proves terminal disposition and publication/accounting consistency |
| Historical transaction evidence | Retain the minimum evidence required by supported idempotency and recovery; do not trim merely because the transaction committed |
| Compiled-plan caches | Evict only if exact reconstruction inputs remain admitted and active users are coordinated |
| Segmented checkpoints | Replace/reclaim only if the storage format proves replay/recovery remains complete; an active head reference pins its checkpoint |
| Preservation bundle payload | Retain while it supplies required history, original evidence, or explicitly required redundancy; reuse identical verified representations |
| Advisory/fencing resources | Keep according to the native locking protocol; never delete a persistent advisory inode as age-based cleanup |
| Maintenance inventory/index | Rebuildable cache except publication-critical obligations recorded in the native journal; corrupted/lost cache disables deletion until reconciliation |
| Operational health history | Bounded current record and bounded recent changes; unresolved recovery evidence remains pinned |
| Unknown/foreign objects | Account and retain; no native name-based cleanup |

For an artifact `a` and a validated store generation `g`, eligibility requires:

```text
rule_allows_release(a, witnessed_time)
AND not_reachable_from_required_roots(a, g)
AND no_live_operation_pin(a, g)
AND required_redundancy_survives(a, g)
AND reference_coverage_complete(a, g)
AND native_recovery_allows_removal(a, g)
```

Age is a necessary grace-period condition where declared, never sufficient
proof. A rebuildable cache may be evicted earlier than other representations,
but not if reconstruction inputs have themselves been removed.

### Clock semantics

Release time is recorded by the native transaction clock, not supplied in an
owner record. Production maintenance samples host wall time and monotonic/boot
context; store the last accepted wall-time observation. Backward movement freezes
time-based eligibility and reports `ClockUncertain`. Suspicious forward jumps
beyond host policy's maximum trusted elapsed interval also defer expiry until
corroborated by elapsed monotonic time or an explicitly trusted host clock reset.
A restart alone does not prove elapsed monotonic time. Conservative retention is
acceptable; premature expiration is not. Provide an injectable clock only to
native test/embedding interfaces. A command-line `--as-of` may simulate inspection
but MUST NOT backdate a destructive production apply.

Policy changes cannot silently shorten an already-admitted artifact's lifetime.
Bind the governing lifecycle closure to publication/release. Extensions may add
holds or longer protection; weakening existing obligations requires an explicit
owner-authorized migration with evidence and must not be inferred from installing
a new definition. Version 1 may reject such weakening rather than invent it.

## 8. Resource policy and accounting

Use an explicit host configuration, separate from passive owner definitions.
Proposed schema `ledger-storage-policy/v1`:

```json
{
  "schema": "ledger-storage-policy/v1",
  "budget_id": "explicit-host-budget",
  "limits": {
    "logical_bytes": 10737418240,
    "staging_bytes": 536870912,
    "metadata_bytes": 134217728,
    "minimum_free_bytes": 1073741824,
    "recovery_reserve_bytes": 67108864
  },
  "maintenance": {
    "max_entries": 10000,
    "max_read_bytes": 67108864,
    "max_write_bytes": 16777216,
    "max_elapsed_ms": 1000,
    "max_manifest_bytes": 8388608,
    "max_provenance_edges": 10000,
    "max_clock_jump_seconds": 86400,
    "health_history_entries": 64
  },
  "thresholds": {
    "high_water_basis_points": 8000,
    "low_water_basis_points": 7000,
    "warning_horizon_seconds": 604800
  },
  "automatic_maintenance": true
}
```

Numbers above are examples for parser/behavior fixtures, not recommended budgets
for the user's machine. No lifecycle policy file is installed by the dotfiles
preparatory PR. The integration selects real budgets explicitly during rollout.

Closed fields, unsigned checked arithmetic, positive work limits, consistent
watermarks, and recovery reserve within the total limit are mandatory. Policy
limits may be lowered, but an already-overbudget store is not garbage: permit
safe reads, diagnosis, recovery, and eligible reducing maintenance; refuse new
unaffordable growth before semantic publication. Supplying a policy does not
change an owner's semantic retention or grant provisioning authority.

### 8.1 Measures

Report separately: canonical logical bytes, retained payload bytes, runtime
overhead, metadata, staging/reserved bytes, eligible reclaimable bytes, pinned
bytes by reason, unclassified bytes, observed allocated bytes when the filesystem
can supply them, and bytes read/written by this maintenance invocation. Include
measurement scope, generation, coverage, and freshness. A partial inventory or
unsupported allocation measure is `unknown`/`partial`, never zero.

Reclaimable logical bytes are not promised free disk blocks. Open handles,
filesystem snapshots, clones, and compression may change actual physical
recovery. Report observed post-action allocation/free-space changes only when
measured, with attribution limitations. Do not double-count shared immutable
payload physically, and do not erase distinct logical/provenance obligations.

### 8.2 Reservations

Before an operation publishes new storage, atomically reserve its conservative
peak additional cost, including staging, journals, descriptors, and accounting.
Admission must satisfy both the configured budget and an observed free-space
reserve. Enforce streaming maxima even when an estimate was lower than actual
input; extend the reservation atomically before more output or fail without
semantic publication.

Concurrent reservations MUST be coordinated at the budget domain. A host may
explicitly share a budget across stores using a supplied native budget-control
root; this is explicit host context, not a directory discovered from definitions.
No hard aggregate-budget claim is allowed for separately coordinated stores.
Per-store and per-class quotas are additionally enforced. Budget lock sections
must be short; do not hold them while hashing, copying, or waiting for store
writers. Use a documented total lock order and validate reservations again at
publication. Reservations are reconciled using transaction state, not expired
PIDs or TTL alone; a crash cannot refund capacity still occupied by staging.

External processes can still consume disk space. Out-of-space handling must keep
recovery possible and report uncertainty; logical reservations are not a guarantee
against other applications. Keep a bounded emergency recovery/reporting reserve.
Deletion-only maintenance must not require another full-store copy to make space.

### 8.3 Incremental accounting

Account created/released representations in the same native publication protocol
as their effects. Maintain a rebuildable index with generation/digest witnesses;
its loss or corruption disables deletion until a bounded reconciliation completes.
Reconcile on explicit maintenance or bounded scheduled slices, not a full scan
before every normal operation. Unknown external changes invalidate affected
coverage and surface a condition. Do not make index trust depend only on mtime.

Per-invocation entry/read/time bounds are progress limits, not lifetime store-size
limits. Return a resumable cursor bound to the store generation and predicate;
revalidate on resume and restart invalidated work safely. A bounded cursor or
index can be recomputed; it must not multiply into a new snapshot per run.

## 9. Generic selected-definition preparation

This replaces reusable preservation/transport logic currently in Python, not
personal-catalog or Git discovery. The host supplies explicit source descriptors
and the selected target. Ledger derives semantic custody dependencies itself.

### 9.1 Explicit sources

Use `ledger-storage-sources/v1` with a bounded `sources` array. Each entry has
`source_id` (stable observation identity), `kind` (`unmanaged-root`, `managed-root`,
or `preservation-bundle`), an explicit absolute locator, optional expected managed
store ID required for managed-root, and a bounded list of original provenance
observations. Initial parser maxima are 1,024 source descriptors, 10,000 original
observations per preparation slice, and 8 MiB per source manifest, further limited
by host policy. Oversized requests require explicit bounded partitioning with
coverage preserved, not silently dropped entries. Bundle sources also provide expected manifest identity/digest.
Reject unknown keys, duplicate conflicting IDs, unsafe paths, symlinks in custody
components, nonregular inputs, and inconsistent managed identities.

Absolute source locators are host inputs, never passive definition output paths.
Resolve/open handles during admission and retain handle-relative access against
path replacement. Locators describe where to read; they do not select authority
among histories. The native engine MUST NOT enumerate Git worktrees, inspect
personal catalogs, load arbitrary `migration.json` files, or execute importers.

A host observation identity must be backed by verifiable root/registration or
source evidence. For legacy manifests with ambiguous origin, retain distinct
provenance instead of inventing ancestry from equal contents. Native inspection
may recognize the legacy archive schema as a generic transport format; it must
not treat its enclosing directory as a newly authoritative source.

### 9.2 Two scopes

`declared` scope includes the selected definition's event/document slots and the
exact sufficient set of bindings, archived closures/revisions, recovery evidence,
and provenance needed to certify them. Derive this closure using native custody
code. Do not guess metadata names in the adapter, include all `.revisions` by
habit, or inventory opaque siblings. Unrelated owner defects do not block healthy
selected-owner lookup; shared native corruption may legitimately block custody.

`historical` scope preserves the explicitly selected broader source tree and
unselected material according to the existing broad transport contract. Preserve
link spellings without following external targets and unowned FIFO topology
without opening/recreating a live channel. Unsupported protected special files
fail closed. Historical transport is not semantic import, not a merge, and not
permission to execute an owner importer. Its size may legitimately exceed a
chosen budget; report that instead of silently narrowing scope.

A prepared native plan carries the scope as a discriminated value. A declared
plan cannot expand to arbitrary root traversal through an optional flag or a
shared function's accidental default. The scope distinction must appear in
results and fixtures.

### 9.3 History selection and validation

For supported monolithic selected histories, equal or complete-record-prefix
sources may establish one covering history; ties are byte-equivalent, not a
latest-path/time election. Divergence, extra local history beyond established
managed custody, malformed bindings, or unknown damage require reconciliation.
Do not concatenate logs, choose a timestamp winner, or replace established
custody with an empty store.

Version 1 MUST support the actual existing static monolithic owner-preparation
path and exact missing-bound-slot restoration. It MUST also enumerate native
segmented storage dependencies for accounting/maintenance without imposing a
lifetime-size ceiling. Transporting segmented/dynamic owner layouts can initially
return `UnsupportedPreparationLayout` with no mutation if their full publication
protocol is not implemented; it must not misclassify them as empty history.

Bind source selection and validation to the locked snapshot used for transfer.
Detect sources that appear after discovery, including a previously empty explicit
source root gaining the selected slot. A host list of Git sources can change;
the host must revalidate its association/coverage immediately before catalog
publication. Native locking covers supplied roots, not an invented promise that
no undisclosed workspace exists.

### 9.4 Immutable preparation identity and provenance

A bundle identity is a digest of its format version, selected definition closure,
scope, target identity, normalized original observations, selected content
identities/lengths, and required dependency witnesses. Generated transport/staging
paths and retry timestamps MUST NOT create a new observation or bundle identity.
Different actual target generations may require different preparation, but old
unchanged evidence must be reused rather than blindly recopied.

Original observations and transport instances are separate records. Deduplicate
payload where safe while preserving all distinct required observations. Repeated
transport edges collapse to already-known origins only when their manifests
verify that lineage. An unverified copy is not trusted merely because its path
looks like an archive. Manifest provenance must itself have bounded cardinality
and reader/writer-compatible encoding.

Use self-contained bounded bundles or explicit verified artifact references with
retention pins. A tiny retained artifact MUST NOT accidentally pin an entire
opaque multi-gigabyte tree solely because that is its transport container. If
necessary, create one bounded independently retained representation and validate
it before retiring a larger redundant copy. No general global archive/object
service is required; scope deduplication to the selected custody/bundles.

### 9.5 Capture and publication

Reserve peak cost, open protected sources, and capture each selected file with
bounded streaming. Count actual bytes consumed; compute digest and length from
that same stream. Preflight remaining budget before reading an obviously-too-large
file, but do not trust stat against growth/truncation/replacement. A read crossing
the remaining budget stops with a diagnostic; no overbudget payload is accepted.
Check source consistency under the actual writer protocol before publication.

Validate the entire proposed manifest against reader limits before publication.
A writer may not emit an archive with more sources/edges/bytes than its own
reader admits. Reuse a verified existing bundle by identity. Interrupted staging
is tied to the same operation identity and recovered or reclaimed through its
native terminal-state protocol, not rediscovered as a source.

Validate the staged owner's complete history and native dependency closure before
publishing active custody. Exact restoration satisfies the unchanged existing
binding; never rebuild a binding to bless arbitrary archive bytes. Use atomic
no-replace or generation-checked replacement as appropriate. Final native
validation and the original expected owner projection are completion criteria.
Catalog publication remains a short, host-owned compare-and-publish step after
validation. Never hold a global personal-catalog lock through native writer waits.

## 10. Reclamation algorithm and crash consistency

A reference implementation may use these phases; equivalent constructions must
satisfy the same observations:

1. Admit the selected root, explicit policy, format/capabilities, and bounded work
   slice. Read current generation and authoritative native obligations.
2. Mark required artifacts from all relevant roots. Validate coverage and retain
   unknowns. Build a bounded candidate batch; do not materialize a full unbounded
   graph or whole history in memory.
3. Acquire native publication/reference coordination, revalidate the generation
   and candidates, and create a recoverable reclamation intent. Coordinate active
   readers/writers through real pins/locks, not scanning process IDs.
4. For replacement/deduplication, verify and sync the surviving representation
   first. Atomically publish reference/accounting changes under the store's
   transaction protocol. Preserve required independent copies.
5. Unlink only exact witnessed eligible instances, using admitted handles and
   identity checks against path replacement. Record bounded terminal disposition
   needed for idempotency/recovery. Sync required directories.
6. Reconcile committed accounting, release reservations, and report actual work.
   Resume an interrupted intent before collecting overlapping candidates.

An intent never makes an otherwise-required artifact collectible. Lock order
must cover reference creation and deletion publication. New references either
win before eligibility is committed or receive an explicit reclaimed/not-found
result; a dangling committed retaining reference is forbidden.

Do not use mutable hard links for deduplication. Immutable shared bytes require
native ownership and retention accounting. Native mandatory-copy policies include
failure-domain meaning; two paths on one disk are not automatically independent
backups. Version 1 does not create or verify remote backup claims.

Admission/refcounts/indexes can accelerate collection, but validate against the
same journal/generation protocol. Recovery must distinguish reserved, staged,
published, obsolete, reclaiming, and terminal states. Fault-inject every persistent
write/rename/fsync boundary. A failure must leave a valid retained representation
or an exact recoverable operation, not ambiguous loss.

## 11. Native CLI surface and result contract

Add a generic `storage` group. Existing baseline commands retain their meanings.
The following are future signatures, not commands available in Ledger 1.5.5:

```text
ledger storage inspect --store-root ROOT --store-id ID --policy POLICY --format json
ledger storage activate --store-root ROOT --store-id ID --policy POLICY [--apply --confirm-writer-cutover] --format json
ledger storage maintain --store-root ROOT --store-id ID --policy POLICY [--apply] --format json
ledger storage prepare --definition DEF --sources SOURCES --scope declared|historical --store-root ROOT --store-id ID --policy POLICY [--apply] --format json
```

`inspect` is read-only, returns a bounded resource/lifecycle view and coverage.
`activate` plans format/policy adoption without mutation by default. Applying
initial activation requires `--confirm-writer-cutover` and actual host-established
writer quiescence, then native locks, legacy classification, and the tested format
fence; the flag alone is not proof that writers have stopped. It preserves root
identity and treats existing owner payload conservatively. Repeating the same
activation is a no-op. On an enabled root, the same command may update compatible
host resource policy only with `--expected-policy-digest OLD`; changed generations
or mismatched policy fail. A resource-policy update never weakens artifact
retention. It does not require another writer-cutover assertion if the format
remains unchanged, but still uses native publication coordination.
`maintain` without `--apply` is read-only planning; `--apply` performs a bounded
eligible maintenance slice under existing standing policy. `prepare` without
`--apply` plans only; apply preserves/prepares the explicitly selected scope and
returns the resulting native context/proof. None discovers a root or creates a
new store identity. Fresh root/catalog creation stays host-selected.

A separate serialized approval token is not required for routine maintenance.
Apply recomputes/revalidates current eligibility; a stale printed plan is not
authority. An optional resumed cursor is progress, not permission. Use a bounded
`--resume` argument on inspect, maintain, or prepare tied to the exact work scope;
reject changed/incompatible cursors rather than silently widening the operation.

Support `--storage-policy POLICY` on mutating native operations for budget admission
and optional bounded maintenance. No policy means unchanged legacy behavior plus
existing native safety limits, not unlimited permission or silent new deletion.
For an enabled lifecycle store, its policy identity is already bound: omitting
or changing the supplied policy must not bypass its quota or reclamation rules.
Policy changes use the generation-checked `storage activate` update described above.

For an existing semantic operation, a successful commit remains exit 0 even when
post-commit maintenance degrades. Include a distinct maintenance warning/result;
never return the operation's precommit failure code after a known successful
commit. Precommit resource failure has no semantic write and reports its actual
side effects, including any safe maintenance already performed. Inconclusive
commit recovery remains `unknown`, not automatically retryable.

### 11.1 Structured output

New storage commands emit exactly one bounded JSON envelope on stdout on both
success and operational failure. stderr may carry human diagnostics, never the
only structured result. Preserve established output contracts for legacy invocations. An explicitly
policy-enabled mutating command retains its existing semantic envelope and adds
`storage_health`, containing the common usage/condition/maintenance fields below;
the schema and existing semantic fields are unchanged. Supplying
`--storage-policy` negotiates this additive result, and new adapters must qualify
it. An enabled root requires its bound policy on writes rather than silently
falling back to an old output/authorization mode. Pure and read-only baseline
operations retain their output schema and do not add this field by surprise.
Do not drop normal definition/store envelopes via payload-only output.

Proposed common fields, with command-specific payloads:

```json
{
  "schema": "ledger-storage-result/v1",
  "operation": "maintain",
  "status": "partial",
  "store_id": "opaque-existing-store-id",
  "definition": null,
  "policy_digest": "sha256:...",
  "generation_before": "opaque-generation",
  "generation_after": "opaque-generation",
  "integrity": "not-checked",
  "capacity": "pressure",
  "maintenance": "progress",
  "coverage": "partial",
  "semantic_commit": "not-applicable",
  "storage_mutated": true,
  "authority_granted": false,
  "usage": {},
  "work": {},
  "retained_reasons": [],
  "conditions": [],
  "resume": "bounded-native-cursor",
  "error": null
}
```

Status is `ok`, `planned`, `partial`, `blocked`, or `failed`; integrity is
`healthy`, `unhealthy`, `unknown`, or `not-checked`; capacity is `normal`,
`pressure`, `exhausted`, or `unknown`; maintenance is `idle`, `progress`,
`complete`, `blocked`, or `failed`. Do not claim integrity was checked merely
because accounting succeeded. Definition metadata, when present, includes the
exact closure digest and ABI/operator requirements.

`usage` includes named integer-byte measurements with scope/freshness and nullable
physical allocation. `work` includes entries examined, bytes read/written,
logical bytes reclaimed, observed allocation change if available, and elapsed
work. `retained_reasons` is bounded with counts/totals and truncation indication.
`error`, when present, has code, phase, limit kind/value, observed count, admitted
source/slot locator, and retry advice. Redact sensitive payloads and credentials;
never include full transcripts. Unknown mutation state is null, not false.

Use exit 0 for successful inspection/planning and a bounded partial-progress slice;
exit 2 for invalid input/unsupported capability; exit 3 for blocked safety/resource
conditions; exit 1 for unexpected execution failure. Dedicated maintenance failure
is independent of already-returned semantic command success. Publish these codes
in CLI tests and do not change unrelated baseline error contracts.

## 12. Automatic maintenance and operational visibility

The engine provides bounded on-write/preparation maintenance and one maintenance
entry point for host scheduling. It does not install daemons, know a notification
provider, make network calls, or read Git/Codex defaults. Host scheduling must
invoke that same engine, not a second cleanup script.

On admitted writes: reserve, perform a bounded safe reducing slice if needed,
recheck capacity, and either proceed or return an exact blocker. After commit:
finalize accounting and eligible internal lifetimes within a bounded slice.
Do not scan every legacy archive or run full-history doctor around each operation.
Healthy owner access keeps its existing no-archive-scan behavior.

Persist bounded current health/last-progress state for mutating maintenance runs.
Read-only inspect does not update a heartbeat. Expose last started/successful/progress
observations and measurement coverage, so the host can detect stale maintenance.
A missed scheduler run is a host-delivery condition; Ledger cannot detect it
while no process invokes it. The integration must verify scheduling and delivery
before claiming proactive service.

Condition identities are stable across unchanged failures and scoped to store,
owner/class, and cause. Hysteresis uses high/low watermarks; repeated identical
conditions are not repeated notifications or new full diagnostic snapshots.
Report resolved transitions. Growth-rate forecasts require enough observations
and disclose uncertainty; no invented time-to-full for unknown or volatile usage.
Prioritize conditions that automation cannot resolve under current obligations.

Maintenance history is a bounded current record plus bounded changes, not an
append-only receipt per no-op sweep. Required unresolved recovery evidence remains
pinned and accounted; if that irreducible metadata grows, report it as such rather
than deleting recovery evidence or silently exceeding limits.

## 13. Legacy adoption and compatibility

### 13.1 No live-data experiment

Do not qualify by running migration/cleanup on the user's actual stores. Use
synthetic or explicitly authorized disposable copies with exact source digests.
No task implementation may change live catalogs, permissions, installed binaries,
semantic records, or global memory merely to exercise the feature.

### 13.2 Inventory before activation

Recognize old native formats and enumerate their dependency closures. Preserve
original root/store IDs, owner slots, record IDs, order, fingerprints, bindings,
archived closures, memory-admission snapshots, and provenance. Account unknown
files as retained/unclassified. Existing archive manifests need reader-compatible
bounded streaming; a tiny selected history may require metadata work but not
reading unrelated payload. Do not globally weaken full historical preservation.

Legacy duplicate archives may be consolidated only after verifying actual listed
bytes and detecting unlisted contents in the exact candidate deletion scope.
Equal totals or digest matches at other paths alone do not prove every deleted
byte is covered. Preserve extra or unclassified material until explicitly covered.
No cleanup policy may rely on incomplete reference scans of arbitrary files.

The host must preserve these classification distinctions during cutover:
`VerifiedGitFamily`, `PlainDirectory`, and `UnverifiableGitEvidence`. Failed Git
discovery cannot justify fresh empty custody. Likewise, an owner's declared
ability to import retired formats is not evidence that the selected source
requires such an import. Keep actual fresh/current-format paths available.
These are adapter obligations, not new native Git/owner-specific branches.

### 13.3 Store format fence

Lifecycle-enabled destructive maintenance requires a new explicit store-format
capability and an activation transaction after writer cutover. Old native binaries
must fail closed for both managed and existing unmanaged selectors before a
successful read/write could ignore lifecycle state. A managed marker extension
alone is insufficient if old `--repo` bypasses it. Select a physical/control-format
fence that the pinned old binaries demonstrably reject; test it rather than
assuming unknown fields are checked everywhere.

An enabled store cannot downgrade by removing a marker or falling back to an old
selector. Preferred rollback disables automatic maintenance and retains the new
reader/runtime and current identities. A full downgrade requires a separately
qualified export to an old compatible representation with no unsupported lifetime
assumptions; it may be rejected when no safe representation exists.

Existing non-enabled stores remain readable/writable with their prior definitions
and supported old runtimes. Installing the new binary does not enable destructive
maintenance or change all consumers' minimum versions.

### 13.4 Definition evolution

Retain archived lifecycle laws for historical obligations. New definitions may
extend protection but cannot turn old retaining edges into provenance or backdate
release. Definition imports remain passive and bounded. Updating a lifecycle law
requires motivating invalid and required-valid neighboring cases, old-data replay,
and all affected consumer tests. Missing operators block only the selected new
feature, never unrelated legacy validation/materialization.

## 14. Implementation map

Use the existing loader/compiler and `libs/definition_core` for parsing,
canonicalization, closure identity, and capability requirements. Add native plan
structures for lifecycle rules and references; extend `definition describe` to
expose their compiled surface and bounds without granting semantic approval.

Extend `apps/ledger` storage, transaction, replay, doctor, and envelope modules to
participate in lifecycle publication and reporting. Factor dependency enumeration
out of the actual custody/revision/definition/segmented readers rather than
replicating their knowledge in a new filename walker.

Place generic filesystem, reservation, and crash-consistency primitives in
`libs/durable_store` where genuinely shared. Keep lifecycle plan interpretation
in Ledger. `storage_root` admission must protect new state with handle-relative
access and the explicit format fence. `definition_core` must not learn owner
workflow semantics. Repository-local module names are implementation choices;
avoid mandatory class hierarchies or a new framework.

Remove storage-critical Python duplication at adapter cutover. Thin host code
may continue resolving catalog/workspace context and choosing explicit inputs;
owner-specific retired-format conversion remains separately selected owner code.
No dynamic loading of those importers occurs inside native Ledger. Do not port
the `retired_sources` declaration shortcut that blocks unrelated current-format
preparation, or hold the personal-catalog lock through native work.

Document supported bounds and rejected layouts in capabilities. A rejected
unsupported composition must be distinguishable from corruption or absence.
All changed native behavior belongs to the Ledger release stream; shared-library
changes follow the monorepo's existing affected-release classification rules.

## 15. Required test matrix

All tests use real native operations where custody semantics matter. Mocked
protocol results or documentation phrase tests are not native qualification.
Failure injection and property/model tests should share fixtures with normal
CLI tests, not duplicate the implementation as their oracle.

| ID | Counterexample or valid case | Required observation |
| --- | --- | --- |
| T01 | Three unrelated owner protocols | Same executable/vocabulary; no owner-name branches |
| T02 | No lifecycle section, old stores/definitions | Exact prior outputs/identities and conservative retention |
| T03 | Unsupported operator/unknown field/duplicate key | Structured rejection, no storage mutation |
| T04 | Release before the owner's transition is valid | Transaction rejects; no lifecycle effects |
| T05 | Release then hold / hold then release | Correct lifetime and hold semantics; no premature reclamation |
| T06 | Retaining historical reference after source supersession | Target remains retained; current fold is not the complete graph |
| T07 | Provenance locator to expired attachment | History remains valid; payload read reports witnessed reclamation |
| T08 | Reclaimable cycles and rooted cycles | Only entirely eligible rootless components reclaim |
| T09 | Foreign/cross-store reference | Retain edge rejected; provenance allowed without false guarantee |
| T10 | Lost/corrupt lifecycle index or unclassified legacy files | No guessed deletion; bounded reconciliation/explicit blocker |
| T11 | Clock rollback, jump, restart, caller-supplied old timestamp | Conservative expiry; no backdated release |
| T12 | Definition update weakens old retention | Reject implicit weakening; old obligations remain |
| T13 | Selected history fixed; unrelated payload exceeds legacy 2 GiB | Same selected result; unrelated bytes not read/copied |
| T14 | Many transport copies of identical evidence | Provenance preserved; no new bulk preservation generation |
| T15 | Failure after every archive/publication boundary, repeated 100 times | Bounded staging; stable evidence identity and payload usage |
| T16 | Source/manifests at writer and reader bounds, including 129-source legacy example | No self-unreadable new manifest; bounded diagnostic for unsupported legacy scope |
| T17 | File grows/truncates/replaces during capture | Bounded read; size/digest/stored bytes agree or fail safely |
| T18 | Divergent logs or local extension beyond managed history | Reconciliation error; no concatenation, latest-wins, or empty fallback |
| T19 | Missing bound slot with correct/tampered archived copy | Exact restoration succeeds or rejects without rebind |
| T20 | Healthy repeated preparation | No archive scan, identity change, or storage mutation |
| T21 | Unrelated owner malformed, selected healthy lookup | Selected lookup stays isolated; shared-object deletion blocks when coverage is incomplete |
| T22 | Empty supplied source gains owner history after discovery | Detect or coordinate new source before publication |
| T23 | Concurrent writer/reference/reader and collection | No dangling retaining edges or disappearing pinned bytes |
| T24 | Concurrent reservation under shared budget | Peak aggregate admission never oversubscribes managed limits |
| T25 | Slow migration in store A, unrelated catalog operation B | No global-catalog lock held through native waits |
| T26 | ENOSPC at every persistent write boundary | Recoverable state; preserved semantic commit truth |
| T27 | Committed semantic write, later maintenance failure | Exit/receipt retain committed outcome; no induced semantic retry |
| T28 | Same idempotency key after attachment reclamation | Original instance/disposition; no resurrection |
| T29 | Full historical transport with unselected data, links, FIFO topology | Existing broad preservation contract retained |
| T30 | Physical sharing/open handles/snapshots | Logical reclamation not misreported as measured physical free space |
| T31 | Old prefeature binaries against enabled managed/unmanaged store | Fail closed, never success with empty/partial history |
| T32 | Canonical events/checkpoints/revision archives needed for replay | Not reclaimed by age or owner attachment release |
| T33 | Explicit read-only inspect/plan and pure operations | No persistent metadata, cache, catalog, or housekeeping effect |
| T34 | Failed retry/idle maintenance reporting repeated many times | Bounded metadata/history; stable alert identity |
| T35 | Stale heartbeat and notification delivery failure | Exposed separately from integrity and semantic commit |
| T36 | Required data alone exceeds quota | Safe read/recovery retained; new growth blocked with exact pinned reasons |
| T37 | Artifact representation redundancy requirement | Deduplication does not destroy required independent copy |
| T38 | Exact legacy root/catalog and owner adoption on disposable data | IDs, records, provenance and expected projection unchanged |

Property laws include generation-validated no-dangling-reference safety,
idempotent preparation/maintenance after quiescence, invariance to unrelated
payload in declared scope, bounded failed-retry overhead, and conservation of
required information across representation replacement. Use an independent
small reference model of obligations, not the runtime's own classifier as oracle.

## 16. Performance and boundedness qualification

Measure cold/warm ordinary projection, transaction, healthy prepare, pressure
maintenance, and interrupted-retry recovery. Include many small artifacts,
large selected streams, large unrelated payload, deep/broad dependency sets,
shared immutable content, segmented history, and limits at exact boundaries.

Report measured bytes read/written, peak RSS, elapsed time, staged peak storage,
retained bytes, and metadata growth. Demonstrate that increasing only unrelated
opaque payload does not increase selected preparation payload I/O. Legacy manifest
metadata work must be disclosed separately rather than hidden in the claim.

Do not impose invented universal latency targets. Compare against a pinned
baseline with the repository's existing local performance tooling, report
regressions, and fix material avoidable overhead. Preserve the existing large
history support; maintenance slice bounds must not become a store lifetime cap.
A complete full-history integrity check may legitimately scale with retained
history and must not be confused with incremental resource inspection.

## 17. Delivery sequence and release gates

Implement this as one coherent feature with internally reviewable commits. Do
not ship two independently authoritative maintenance engines or permanently stack
Python fallbacks around native errors.

**Stage A: native fundamentals.** Inventory native writer families, specify their
release conditions, implement dependency enumeration, same-stream accounting,
reservations, and declared-scope preservation with stable retries. No destructive
owner lifecycle activation yet. Keep broad transport compatible.

**Stage B: lifecycle execution.** Add passive compiler support, independently
managed attachments, references/holds/releases, transactional accounting and
reclamation, format fences, and structured CLI/health results. Complete generic
fixtures, reader/old-binary matrices, and all failure/concurrency tests.

**Stage C: release qualification.** Run the current documented Ledger Debug and
release-safe/unit/CLI/segmented suites on Linux and macOS, plus the new matrix and
shared-library affected suites. At this baseline the documented targets include
`zig build build-ledger`, `zig build test-ledger`, and
`zig build test-ledger-segmented`; confirm current target/optimization spelling
from the checked-out build graph. Use the repository-supported Zig toolchain
(current baseline 0.17.0), format/style checks, and existing CI policy. Do not
claim a test run with skipped native cases qualifies storage semantics.

Bump Ledger to the next unused compatible minor release (nominally 1.6.0 above
the examined 1.5.5 baseline), applying current repository release rules instead
of overwriting a version already used. Publish the required independent Ledger
tag/assets, update the Homebrew tap, pass audit/test, and verify the installed
binary's version and exact capabilities. ABI extension and store-format version
are separate; never claim a version string alone proves either compatibility.

Preserve the user's required five consecutive clean standard reviews and
auxiliary review policy for the implementation workflow. An interrupted or
inconclusive review earns no credit. Do not represent self-inspection or a
written test plan as executed independent review.

**Stage D: host/owner cutover.** After release/install, update dotfiles adapters to
select explicit contexts, invoke native preparation/maintenance, and stop
reimplementing its storage mechanics. Cut over old writers, classify/adopt
legacy storage on disposable copies first, activate definitions only for tested
owners, and preserve all existing IDs and memory associations. Follow owner
minimums, not a blanket upgrade requirement for unrelated pure operations.

The host configures and verifies periodic maintenance and notification delivery.
Installation/provisioning requires its existing authority. No native daemon or
network notification dependency is added. If this host work is not delivered,
report native capability readiness separately and do not claim proactive idle
maintenance is operational. The preparatory dotfiles PR does not perform Stage D.

## 18. Definition of done and honest limitations

Native implementation is complete only when:

- Existing required history and original owner operations pass expected-content
  verification, not just exit-code checks.
- Scope independence, stable failed retries, bounded snapshots, complete reference
  coverage, and crash/concurrency laws have native evidence.
- Generic lifecycle definitions exercise three unrelated protocols without native
  specialization; unsupported compositions fail explicitly.
- Eligible overhead is reclaimed without per-run user intervention under activated
  policy; irreducible required growth is measured and reported honestly.
- Legacy compatibility and old-writer fences are qualified; rollout preserves root
  identities and never repairs availability with a new empty store.
- Release/tap/installation evidence is available, and remaining host activation is
  explicitly identified rather than implied by successful native tests.

Finite disk cannot retain infinitely growing required history forever. This
feature prevents waste, reclaims ended obligations, and exposes unavoidable
pressure; it does not silently sacrifice required evidence. Compression,
remote archival tiers, semantic event compaction, and cross-store distributed
collection are out of scope until separately specified by demonstrated need.

The user should intervene only when a genuine preservation/resource-policy choice
remains. Routine housekeeping, source-copy amplification, and hidden storage
pressure are the system's responsibilities.
