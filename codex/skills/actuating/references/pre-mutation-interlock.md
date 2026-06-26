# Actuating Pre-Mutation Interlock

## Purpose

`$actuating` is a transaction controller. It does not merely advise implementation.

The interlock prevents this failure shape:

```text
plan pressure
-> local decomposition
-> patch attempts
-> update_plan projection
-> proof attempts
-> retrospective control language
```

and enforces this shape:

```text
plan pressure
-> st session binding
-> claim/fencing
-> GCR-v2 execution_allowed=yes
-> APMA-v1 mutation-authorized
-> bounded slice
-> isolated realization
-> proof receipt
-> sealed changeset
-> serialized integration
```

## APMA-v1

APMA-v1 is the local pre-mutation authority receipt.

```yaml
actuation_pre_mutation_authority:
  version: APMA-v1
  verdict: mutation-authorized
  issued_at:
  run_id:
  workspace:
    workspace_id:
    target_branch:
    head:
    workspace_sequence:
    branch_epoch:
    working_tree_fingerprint:
  plan:
    plan_id:
    plan_sequence:
    selected_task_ids: []
  coordination:
    claim_id:
    session_id:
    executor:
    fencing_token:
    lease_current:
    fencing_current:
    resources: []
  gcr:
    gcr_id:
    execution_allowed: yes
    projection_view_id:
    projection_digest:
  intended_resources: []
  resource_coverage: []
```

APMA-v1 is derived from a current GCR-v2 plus the exact intended edit resource.
It is not hand-authored.

## Generate

```bash
uv run python codex/skills/actuating/tools/actuation_authority_gate.py \
  authorize \
  --gcr .ledger/actuating/<run-id>/gcr-v2.json \
  --run-id <run-id> \
  --path src/example.zig \
  --out .ledger/actuating/<run-id>/apma-v1.json
```

Use repeated `--path` or `--resource` flags for multi-path edits.

```bash
--resource write:path:src
--resource write:schema:events
--resource exclusive:git:index
```

## Check immediately before mutation

```bash
uv run python codex/skills/actuating/tools/actuation_authority_gate.py \
  check \
  --apma .ledger/actuating/<run-id>/apma-v1.json \
  --path src/example.zig
```

A failed check means no patch.

## What it validates

The gate requires:

```text
GCR-v2 receipt_version
GCR-v2 execution_allowed=yes
no denial reasons
claim id
session id
executor
fencing token
lease_current=true
fencing_current=true
workspace sequence equality
plan sequence equality
branch epoch equality
projection selected IDs equals plan selected IDs
projection session equals coordination session
nonempty selected task IDs
nonempty claim resources
no conflicting claims
graph gate passed
no graph debt
intended write/exclusive resource covered by claim resource
```

## Self-invalidating GCR

Run:

```bash
uv run python codex/skills/actuating/tools/actuation_authority_gate.py \
  diagnose-gcr \
  --gcr .ledger/actuating/<run-id>/gcr-v2.json
```

If the result is:

```text
blocked-self-invalidating-gcr-candidate
```

then the workflow reached the known failure mode where the receipt path invalidated its own session/view/sequence precondition.

Required action:

1. stop actuation;
2. do not mutate product files under `$actuating`;
3. release any held claim when safe;
4. record the run as blocked on `$st` authority tooling;
5. repair `$st` so compile is non-self-invalidating, or explicitly leave `$actuating` before any direct implementation.

## Direct implementation fallback

Direct implementation can be valid when no concurrent workspace coordination is needed, but it must not be presented as `$actuating`.

Use an explicit transition:

```text
$actuating blocked: GCR path self-invalidating.
Leaving $actuating before direct implementation.
No actuation authority is claimed for subsequent edits.
```

## Falsifier

The interlock is working when future `seq actuation-audit` true/control rows show:

```text
mutations_without_gcr = 0
apply_patch_calls are covered by APMA-v1
no graph_bypass verdicts
no projection_inversion verdicts
```
