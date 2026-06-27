# Spec 03 — `resolve-c3 closure-gate`

Order: 3 of 4.
Depends on: Spec 01 / RAC-v1 and Spec 02 / mutation-gate.

## Purpose

Prevent delivery closure language unless the material `$resolve` campaign has a
mechanically inspectable closed authority chain.

## Native CLI surface

```bash
resolve-c3 closure-gate \
  --campaign <campaign-id> \
  --summary /tmp/seq-resolve-summary.json \
  --runs /tmp/seq-resolve-runs.jsonl \
  --format text|json
```

Reference compatibility script:

```bash
python3 codex/skills/resolve/tools/resolve_closure_gate.py \
  --summary /tmp/seq-resolve-summary.json \
  --runs /tmp/seq-resolve-runs.jsonl
```

## Exit codes

```text
0  closure allowed
2  closure blocked
3  gate could not evaluate input
```

## Closure blockers

A material run is not closed when any are true:

```text
c3_required=true and c3_closed=false
compression_state=NONE
batches_total=0 for a finding-bearing workflow
delivery_closed=true while terminal_closed=false
potential.strict_progress=0 for a material campaign
orphan_code_constructs > 0
unmapped_proof_actions > 0
wound_specific_tests > 0 unless class-mapped
semantic_surface_delta > 0 without explicit AC rebase
```

A healthy material closure row has:

```text
c3_required=true
c3_entered=true
c3_closed=true
compression_state != NONE
batches_total > 0
kernel.accepted=true
potential.strict_progress > 0
delivery_closed=true
terminal_closed=true
orphan_code_constructs=0
unmapped_proof_actions=0
semantic_surface_delta <= 0 unless AC rebased
```

## Output JSON

```json
{
  "closure_allowed": false,
  "status": "blocked",
  "violations": [
    {
      "scope": "run",
      "run_id": "019efa26-...",
      "code": "delivery_closed_without_terminal_closure",
      "detail": "delivery_closed=true while terminal_closed=false"
    }
  ],
  "legal_next_actions": [
    "enter_or_repair_c3",
    "seal_batches",
    "compile_compression",
    "accept_kernel",
    "map_or_delete_orphans",
    "map_proof_actions",
    "reduce_semantic_surface_or_rebase_ac",
    "rerun_terminal_holdout"
  ]
}
```

## Completion language rule

Do not use these words when closure blocks:

```text
closed
resolved
complete
ready
landed
shipped
all set
```

Use:

```text
blocked
not yet closed
closure gate failed
remaining authority gaps
```
