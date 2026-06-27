# Spec 02 — `resolve-c3 mutation-gate`

Order: 2 of 4.
Depends on: Spec 01 / RAC-v1.

## Purpose

Prevent review-originated patches unless review prose has been compiled into an
inspectable authority chain.

## Native CLI surface

```bash
resolve-c3 mutation-gate \
  --chain rac.yaml \
  --format text|json
```

Optional controller-integrated shape:

```bash
resolve-c3 mutation-gate \
  --campaign <campaign-id> \
  --review-claim-id <claim-id> \
  --artifact-state <artifact-state.json> \
  --format json
```

Reference compatibility script:

```bash
python3 codex/skills/resolve/tools/resolve_mutation_gate.py --chain rac.yaml
```

## Exit codes

```text
0  mutation allowed
2  mutation blocked
3  gate could not evaluate input
```

## Required checks

Mutation is allowed only when all are true:

```text
RAC-v1 validates
RAC artifact state is current
review claim is present
AC law/horizon relation is in-horizon
CEX is confirmed
RB-v1 is sealed
CEB class is present
MBK/RC transition is present
proof obligation is present
realization.allowed = true
gate.mutation_allowed = yes
```

## Blocked output

```json
{
  "mutation_allowed": false,
  "reason": "uncompiled_review_text",
  "missing": ["sealed_batch", "ceb_class", "mbk_transition"],
  "legal_next_actions": [
    "adjudicate_claim",
    "seal_or_repair_batch",
    "compile_or_repair_ceb_mbk_rc",
    "rebase_ac",
    "create_followup",
    "reject_finding",
    "block"
  ]
}
```

## Legal blocked actions

When blocked, the workflow may only:

```text
adjudicate the claim
seal or repair the batch
compile or repair CEB/MBK/RC
rebase AC
create a follow-up
reject the finding
block
```

It must not:

```text
patch
commit
push
close PR threads
emit completion language
```
