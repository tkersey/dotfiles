---
name: st
description: "Repository-level durable graph workspace under `.ledger/st/`. Use for `$st`, one or many plans, dependency graphs, proof-carrying completion, execution-policy horizons, multi-agent allocation, same-repo/same-target-branch coordination, session-local Codex/OpenCode projections, or resuming durable work. Every material mutation requires a current plan-scoped GCR-v2 plus a workspace claim with an unexpired fencing token."
metadata:
  version: "2.0.0"
  activation_cost: medium
  default_depth: standard
---

# st

## Mission

`$st` is the repository execution workspace.

```text
many independent plan graphs
+ one cross-plan resource authority
+ session-specific projections
+ branch-epoch proof binding
+ serialized target-branch integration
```

Canonical root:

```text
.ledger/st/
```

Never create new durable planning artifacts under `.step/`.

## Governing model

```text
plan
  owns intent, work graph, dependencies, proof obligations, waivers,
  graph debt, polish history, fingerprints, and lifecycle

workspace
  owns plan registry, cross-plan dependencies, resource claims, leases,
  fencing, agent/session views, branch epochs, proof invalidation,
  change-set integration, and global execution permission
```

Core law:

```text
Plans own work.
The workspace owns interference.
```

## Canonical layout

```text
.ledger/st/
  workspace.jsonl
  plans/<plan-id>/plan.jsonl
  plans/<plan-id>/intake/
  plans/<plan-id>/policy/
  proof/<plan-id>/
  runtime/claims.jsonl
  runtime/sessions/<session-id>.json
  runtime/views/<session-id>.json
  runtime/branch-state.json
  worktrees/<claim-id>.json
  changesets/<changeset-id>.json
  integration/queue.jsonl
  integration/receipts/
  transactions/
  locks/
  migration/
```

Actual detached Git worktrees should live outside the primary checkout. Their metadata belongs under `.ledger/st/worktrees/`.

See [storage-layout.md](references/storage-layout.md).

## Plan identity

Every plan has an immutable `plan_id`.

Local task IDs may remain concise:

```text
st-001
st-002
```

Global references are qualified:

```text
plan://auth-hardening/st-001
plan://cache-redesign/st-002
```

When exactly one active plan exists, the CLI may infer it.

When two or more plans are active:

```text
missing --plan => hard error
```

Never infer from current directory, selected projection, or most recently touched plan.

## Capability preflight

Use one capability probe only when the installed CLI is uncertain:

```bash
st capabilities --format json
```

Required multi-plan capabilities:

```text
workspace_v1
plan_namespace_v1
qualified_refs_v1
workspace_claim_v1
fencing_token_v1
session_view_v1
branch_epoch_v1
changeset_v1
serialized_integration_v1
gcr_v2
graph_intelligence_receipt_v1
graph_repair_receipt_v1
st_artifact_maintenance_receipt_v1
ledger_artifact_root_v1
```

See [capability-and-legacy-mode.md](references/capability-and-legacy-mode.md).

If unavailable:

```text
analysis and migration planning allowed
material concurrent mutation forbidden
```

Do not emulate multi-plan coordination with separate unmanaged files.

## Initialize the workspace

```bash
st workspace init \
  --workspace .ledger/st \
  --repo . \
  --branch <target-branch>
```

Create a plan:

```bash
st plan create \
  --workspace .ledger/st \
  --plan <plan-id> \
  --source <plan-or-spec>
```

List and inspect:

```bash
st plan list --workspace .ledger/st --format table
st plan show --workspace .ledger/st --plan <plan-id> --format json
st workspace status --workspace .ledger/st --format json
```

## Material plan intake

Each plan retains the full current graph compiler.

```bash
st intake scaffold \
  --workspace .ledger/st \
  --plan <plan-id> \
  --source <source> \
  --out .ledger/st/plans/<plan-id>/intake/intake.md

# Author or correct semantic intake.

st intake check \
  --input .ledger/st/plans/<plan-id>/intake/intake.md \
  --gate implementation-ready \
  --format json

st intake normalize \
  --input .ledger/st/plans/<plan-id>/intake/intake.md \
  --out .ledger/st/plans/<plan-id>/intake/normalized.md

st intake apply \
  --workspace .ledger/st \
  --plan <plan-id> \
  --input .ledger/st/plans/<plan-id>/intake/normalized.md \
  --gate implementation-ready
```

All existing plan features remain plan-local:

```text
intent atoms
contracted task capsules
hierarchy and links
hard dependencies
acceptance and validation
proof obligations and receipts
waivers
graph debt
polish/fixed-point history
graph fingerprints
execution-policy bindings
aperture scoring
import/export
```

## Session binding

Bind each coding-agent session explicitly:

```bash
st session bind \
  --workspace .ledger/st \
  --session <session-id> \
  --executor <executor-id> \
  --plan <plan-id>
```

A session view is projection state, not task state.

```text
runtime/views/<session-id>.json
```

Two coding agents receive independent projections.

No session may reconcile, assert, or overwrite another session’s view.

## Resource declarations

Executable items declare structured resources:

```text
path:<file-or-directory>
symbol:<file>#<symbol>
generated:<artifact>
schema:<name>
service:<name>
git:index
git:branch:<branch>
repo:all
```

Modes:

```text
read
write
exclusive
```

Conflict laws:

```text
read + read                    compatible
read + write                   conflict
write + write                  conflict
exclusive + anything           conflict
directory path + descendant    overlap
file path + symbol in file     overlap
repo:all                       conflicts with every mutation
```

Unknown mutation scope becomes:

```text
repo:all / exclusive
```

Never infer safety from different plan IDs.

See [resource-claims.md](references/resource-claims.md).

## Workspace aperture

Compile plan-local candidates, then allocate a conflict-free workspace aperture.

```bash
st workspace aperture \
  --workspace .ledger/st \
  --executors <agent-a>,<agent-b> \
  --format json
```

The workspace scheduler may use:

```text
plan aperture score
priority
critical path
downstream unlocks
proof readiness
uncertainty
fairness/age
resource conflict graph
cross-plan dependencies
```

Only CLI-emitted allocation facts count.

## Claims and fencing

Claim work before mutation:

```bash
st claim \
  --workspace .ledger/st \
  --plan <plan-id> \
  --session <session-id> \
  --ids st-001,st-002 \
  --lease-seconds 900
```

The claim emits:

```text
claim ID
workspace and plan sequence
branch epoch
resource set
lease expiry
monotonic fencing token
```

Every mutation, proof write, change-set seal, and integration operation must present the current claim/fencing token.

After reclaim:

```text
old fencing token => permanently invalid
```

Refresh:

```bash
st heartbeat \
  --workspace .ledger/st \
  --claim <claim-id> \
  --fencing-token <token>
```

Reclaim:

```bash
st claim reclaim-stale --workspace .ledger/st
```

## GCR-v2

Compile executable authority:

```bash
st compile aperture \
  --workspace .ledger/st \
  --plan <plan-id> \
  --session <session-id> \
  --claim <claim-id> \
  --limit 7
```

GCR-v2 binds:

```text
workspace ID and sequence
plan ID and sequence
target branch and branch epoch
HEAD and working-tree fingerprint
selected task IDs
claim ID and fencing token
resource set and conflict result
graph fingerprints and debt
proof cut
session projection
execution_allowed
```

For material mutation:

```text
current plan graph
+ current workspace state
+ current branch epoch
+ current held claim
+ current fencing token
+ conflict-free resources
= execution_allowed: yes
```

A plan-local preview without a claim must emit:

```text
execution_allowed: no
reason: workspace_claim_required
```

Validate receipts with:

```bash
python3 codex/skills/st/tools/gcr_v2_gate.py gcr.json
```

## Projection

Prime one session:

```bash
st prime \
  --workspace .ledger/st \
  --plan <plan-id> \
  --session <session-id> \
  --claim <claim-id> \
  --mode aperture \
  --limit 7
```

Project only:

```text
plan_sync.codex.plan
or
plan_sync.opencode.todos
```

Visible IDs are qualified:

```text
[auth-hardening/st-001] ...
```

Assert:

```bash
st assert-projection \
  --workspace .ledger/st \
  --plan <plan-id> \
  --session <session-id>
```

## Same target branch, two agents

Recommended execution mode:

```text
one target branch
two detached ephemeral worktrees
one global integration queue
```

Each claim receives a worktree based on the current branch epoch.

Agents do not directly commit or push the target branch.

They seal change sets:

```bash
st changeset seal \
  --workspace .ledger/st \
  --claim <claim-id> \
  --fencing-token <token>
```

Then enqueue:

```bash
st integrate enqueue \
  --workspace .ledger/st \
  --changeset <changeset-id>
```

A single integrator:

1. acquires `git:index` and `git:branch:<target>`;
2. compares expected target HEAD;
3. verifies changed paths are within claimed resources;
4. applies/rebases the change set;
5. runs required integration proof;
6. advances target branch by compare-and-swap;
7. increments branch epoch;
8. invalidates affected proof;
9. emits an integration receipt.

See [worktree-integration.md](references/worktree-integration.md).

## Proof

Record proof with workspace lineage:

```bash
st proof record \
  --workspace .ledger/st \
  --plan <plan-id> \
  --claim <claim-id> \
  --id st-001 \
  --obligation proof-001 \
  --action proof-action-001 \
  --command "<command>" \
  --evidence-ref .ledger/st/proof/<plan-id>/proof-001.log \
  --artifact-ref "tree:<digest>"
```

A proof receipt binds:

```text
plan ID/item
workspace sequence
plan sequence
branch epoch
base HEAD
tree digest
dependency cut
foreign change sets
focused/wave/final scope
```

Branch-epoch changes invalidate:

```text
final proof always
wave proof when covered resources changed
focused proof when dependency cut intersects foreign changes
```

See [proof-epochs.md](references/proof-epochs.md).

## Cross-plan dependencies

Use qualified refs:

```bash
st plan link \
  --workspace .ledger/st \
  --from plan://cache/st-004 \
  --to plan://auth/st-002 \
  --type blocks
```

Cross-plan edges are workspace-owned and audited globally.

A plan cannot mutate another plan’s graph to create or remove one.

## Storage policy

All new artifacts live below `.ledger/`.

Shared mode may track:

```text
.ledger/st/workspace.jsonl
.ledger/st/plans/*/plan.jsonl
declared cross-plan links
selected durable proof receipts when desired
```

Always local-exclude:

```text
.ledger/st/locks/
.ledger/st/runtime/
.ledger/st/transactions/
.ledger/st/worktrees/
integration scratch
```

Local mode may exclude all of `.ledger/st/`.

See [storage-policy.md](references/storage-policy.md).

## Legacy migration

Migrate the canonical legacy file:

```bash
st workspace migrate \
  --from .step/st-plan.jsonl \
  --to .ledger/st \
  --plan-id default
```

Preserve:

```text
IDs and task state
event/checkpoint history
graph envelope and policy
intent, waivers, debt
proof actions and receipts
polish passes
fingerprints
claims as historical records
projection membership as an initial session view
```

After successful migration:

```text
no new writes to .step/
```

See [migration.md](references/migration.md).

## Failure rules

Hard block when:

```text
multiple active plans and --plan omitted
session not bound to plan
claim absent, expired, or owned by another session
fencing token stale
workspace/plan sequence stale
branch epoch or expected HEAD stale
resource conflict exists
changed path outside claim
cross-plan dependency blocks work
open transaction recovery required
proof context stale
integration queue authority absent
```

Never “continue carefully” after one of these.

## Final report

```text
st Workspace:
- workspace / target branch / branch epoch:
- plan / plan sequence:
- session / executor:
- GCR-v2:
- claim / fencing token / lease:
- resource set / conflicts:
- ready / blocked / selected frontier:
- cross-plan dependencies:
- proof basis / stale proof:
- change set / integration state:
- projection assertion:
```

## Hard rules

- `.ledger/st/` is the only new canonical artifact root.
- No unmanaged alternate plan files.
- Plan graphs are isolated; coordination is global.
- No material mutation without current GCR-v2 and claim fencing.
- No session may overwrite another session’s projection.
- No two conflicting resource claims may coexist.
- No direct target-branch commit/push by worker agents.
- Integration is serialized and compare-and-swap bound.
- Proof is branch-epoch and dependency-cut bound.
- Unknown scope reduces concurrency; it never grants it.
