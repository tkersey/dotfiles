# Specification-driven storage lifecycle

Use for lifecycle design, storage-cost diagnosis, or qualification of native
maintenance support. This is not an always-on agent checklist or permission to
scan unrelated stores.

## Capability status

The currently integrated baseline has no generic lifecycle/reclamation contract.
The existing bootstrap, owner preparation, exact recovery, and segmented-migration
instructions remain authoritative for available operations. This guidance does
not implement retention, repair the existing archive-amplification path, enable
new commands, install a scheduler, or establish live-store health.

The single native implementation specification is
[skills-zig-storage-lifecycle.md](../specs/skills-zig-storage-lifecycle.md).
Its proposed schemas and command spellings are not runtime instructions. Activate
them only after capability checks, native qualification, a tagged release, tap
qualification, installed-version verification, and an owner-specific cutover.
Do not raise every consumer's minimum version or remove a working helper early.

## Ownership

| Concern | Owner |
| --- | --- |
| Artifact meaning, retention obligations, retaining references, and release transitions | The semantic owner's passive definition |
| Bounded planning, identities, native custody dependencies, atomic publication, accounting, and safe reclamation | Generic Ledger runtime and shared storage primitives |
| Root selection, personal catalog, Git/workspace discovery, budgets, scheduling, and notification destination | This skill's integration and explicit host policy |

Ledger follows a specification to write and store. It must not acquire a registry
of named skills, cleanup branches for a review verdict, or knowledge of one
installation's layout. New protocols expressible in the vocabulary require new
definitions and fixtures, not native code changes. Definitions remain passive:
no cleanup scripts, subprocess hooks, network calls, or hidden source discovery.

Move reusable storage machinery into `skills-zig`; do not port Git discovery or
personal-home defaults into the generic engine. A remaining adapter may resolve
explicit context or invoke owner-owned retired-format interpretation. It must
not duplicate the native locking, copying, byte accounting, or reclamation
implementation after cutover. Do not create a bespoke custody product merely
to relocate Python.

## Lifetimes follow obligations

Every newly managed artifact needs an accountable owner and a retention rule.
A rule may retain it indefinitely. Runtime-generated overhead needs native
lifetime rules; owners do not describe Ledger's temporary filenames.

| Class | Safe release condition |
| --- | --- |
| Canonical records and event history | Owner-authorized semantic retirement, not age; no semantic truncation is introduced by routine maintenance |
| Definitions, bindings, historical revisions | No retained replay, idempotency, integrity, compatibility, or recovery dependency requires them |
| Transaction staging and journals | Native recovery protocol proves terminal disposition and no required retry or reader still depends on them |
| Preservation bundles | A verified surviving representation covers the required bytes, original provenance, and recovery/redundancy obligations |
| Reconstructible runtime caches | Required reconstruction inputs remain retained and no active operation pins the cache |
| Diagnostic payloads | A released owner-declared obligation, elapsed declared grace period, and absence of retaining references/holds |
| Foreign or unknown files | Preserve and account as unclassified until their actual owner provides a supported lifecycle contract |

A clean verdict, absent PID, expired lease, old timestamp, supersession, or directory
name alone is not a reclamation witness. A checkpoint does not replace full-history
obligations. Native safety dependencies override a request to expire something
still needed for replay or recovery.

Keep content identity, original source provenance, transport location, and required
independent redundancy distinct. Equal bytes may share a representation without
merging source observations. A new transport copy must not create a new original
observation or another preservation generation. A digest match alone does not
prove that a required independent recovery copy is redundant.

## Bounded maintenance contract

The native target must prevent avoidable growth before reporting it: bounded
selected-definition preservation, stable failed retries, eligible cache eviction,
and resolved-staging cleanup. Full historical preservation remains a separate
explicit scope; do not globally narrow its preservation promise.

Admit writes against explicit budgets including concurrent reservations and peak
staging cost. Enforce byte limits during streaming, deriving size and digest from
the same accepted snapshot. Keep source-read cost, logical retained bytes, observed
allocated bytes, staging, and reclaimable bytes distinct. Unknown allocation or
incomplete inventory is not zero usage or proof of safe deletion.

Reclamation must coordinate with actual native writers, readers, references, and
recovery. Changing a definition, failing to discover a workspace, or losing an
index cannot turn retained data into garbage. No empty-store fallback, binding
rewrite to bless damage, or mass deletion by age. Overbudget stores retain safe
read/recovery access; missing capacity is not permission to weaken history.

Routine maintenance under a qualified spec and standing host policy needs no
per-run approval. That authority does not authorize new semantic capture,
publication, weaker retention, new provisioning, or deletion of foreign evidence.
Explicit no-maintenance execution remains nonmutating. Pure validation and
materialization must not resolve stores or perform housekeeping.

## Automatic execution and reporting

Once the native release is activated, use bounded maintenance on supported write
paths and the host's periodic invocation of the same engine. The host owns the
schedule and delivery channel; a CLI that is not invoked cannot inspect idle
stores. Verify scheduler execution and alert delivery at integration rollout.
Do not substitute an unbounded agent scan or a second cleanup script.

Routine success should be quiet. New actionable pressure, stalled maintenance,
unclassified growth, or corruption should surface the selected store/owner,
measurements and freshness, retained/reclaimable costs, actual action taken, and
specific remaining obligation. Deduplicate unchanged alerts; expose a stale
maintenance heartbeat. Keep the maintenance history and diagnostics bounded too.

Preserve integrity, resource health, and maintenance status separately. A healthy
`doctor` verdict is not a capacity assessment. A committed write remains committed
when later maintenance degrades; do not trigger semantic retries from housekeeping
failure. Cleanup or a preservation receipt does not establish restoration of the
original owner operation.

On the current implementation, report observed blockers and unknowns without
inventing lifecycle metrics, claiming automatic maintenance, or deleting files.
Do not repeat the same unchanged bound-exceeding preparation as a recovery tactic.

## Owner qualification and cutover

Before adding lifecycle fields to an active owner definition:

1. Verify the installed native capability and the exact definition closure.
2. Declare the owner's obligations using generic vocabulary; unspecified legacy
   data remains retained. Inventory real consumers and explicit external holds;
   a best-effort path scan cannot prove that no consumer needs an artifact.
3. Qualify unchanged history, the original owner operation, legacy roots/IDs,
   failure/retry stability, concurrent publication/reclamation, and bounded cost.
4. Cut over writers before enabling destructive maintenance. Old binaries must
   refuse an enabled new store format before reading or mutating it; unsupported
   downgrade cannot be hidden by falling back to an unmanaged selector.
5. Verify ongoing maintenance and notification delivery. Do not claim the native
   feature released, installed, enabled, or effective from a documentation merge.

Keep canonical capture, memory admission, workflow decisions, and external
publication outside lifecycle authority. Foreign evidence can be reclaimed only
through its declared owner contract, not because it resides beneath `.ledger`.
