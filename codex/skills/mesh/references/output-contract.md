# Mesh Output Contract v2 (Streaming)

Mesh streaming runs fail closed when worker results are ambiguous.

For `spawn_agents_on_csv`, the canonical output channel is the worker-only
`report_agent_job_result` call. Narrative text is non-authoritative.

## Required Reporting Mechanism

Every worker MUST call `report_agent_job_result` exactly once with:

- `job_id`: worker job id
- `item_id`: worker item id
- `result`: JSON object following this contract

Missing report calls are hard failures.

## Required `result` Keys

Required keys for strict parsing:

- `id`: unit id
- `candidate_id`: candidate id unique within unit
- `triplet_index`: lane index (legacy key retained)
- `lane`: `coder|reducer|locksmith|applier|prover|fixer|integrator`
- `decision`: lane outcome token
- `proof_status`: `pass|fail|skipped|not_applicable`
- `write_scope`: list of lock roots or file globs
- `risk_tier`: `low|med|high`
- `base_sha`: commit used for apply/proof context
- `proof_attempts`: integer (`0` for non-proof lanes)
- `proof_evidence`: object with `command`, `key_line`, `exit_code`

Mesh classifies rows as `invalid_output_schema` when any required key is missing,
wrongly typed, or semantically invalid.

## Lane-Specific Expectations

- `coder` and `reducer`:
  - usually `decision=accept`
  - `proof_status=skipped`
  - include `patch` when proposing changes
  - include `challenge_findings`
- `locksmith`:
  - `decision=lease_granted|lease_denied|lease_reclaimed`
  - include `lease_id` and `ttl_ms`
- `applier`:
  - `decision=applied|apply_failed`
  - `proof_status=not_applicable`
  - include `apply_evidence`
- `prover`:
  - `decision=proof_complete|proof_failed`
  - `proof_status=pass|fail`
  - `proof_attempts` must be `1` or `2`
- `fixer`:
  - `decision=accepted|rework_required|blocked_safety`
  - include `selected_candidate`, `quorum_target`, `quorum_observed`
- `integrator`:
  - `decision=integrated_patch|integrated_commit|blocked_delivery`
  - include `artifact_ref` and `scope_assertion`

## Recommended Optional Keys

- `failure_code`
- `notes`
- `patch` (apply_patch-format patch text)
- `patch_sha256`
- `challenge_findings`
- `reduce_record`
- `lease_id`, `ttl_ms`
- `worktree_path`
- `apply_evidence`
- `selected_candidate`, `quorum_target`, `quorum_observed`
- `artifact_ref`, `scope_assertion`

## Example Result (Prover)

```json
{
  "id": "u-104",
  "candidate_id": "u-104-coder-1",
  "triplet_index": 1,
  "lane": "prover",
  "decision": "proof_complete",
  "proof_status": "pass",
  "write_scope": ["codex/skills/mesh", "codex/agents"],
  "risk_tier": "med",
  "base_sha": "9c6458d",
  "proof_attempts": 1,
  "proof_evidence": {
    "command": "uv run pytest tests/test_streaming.py",
    "key_line": "1 passed",
    "exit_code": 0
  },
  "worktree_path": "/tmp/mesh-u-104"
}
```

## Recommended `output_schema`

`spawn_agents_on_csv` does not enforce schema at runtime, so mesh must enforce this schema during parse:

```json
{
  "type": "object",
  "required": [
    "id",
    "candidate_id",
    "triplet_index",
    "lane",
    "decision",
    "proof_status",
    "write_scope",
    "risk_tier",
    "base_sha",
    "proof_attempts",
    "proof_evidence"
  ],
  "properties": {
    "id": {"type": "string"},
    "candidate_id": {"type": "string"},
    "triplet_index": {"type": "integer", "minimum": 1},
    "lane": {
      "type": "string",
      "enum": ["coder", "reducer", "locksmith", "applier", "prover", "fixer", "integrator"]
    },
    "decision": {"type": "string"},
    "proof_status": {
      "type": "string",
      "enum": ["pass", "fail", "skipped", "not_applicable"]
    },
    "write_scope": {
      "type": "array",
      "items": {"type": "string"},
      "minItems": 1
    },
    "risk_tier": {"type": "string", "enum": ["low", "med", "high"]},
    "base_sha": {"type": "string"},
    "proof_attempts": {"type": "integer", "minimum": 0, "maximum": 2},
    "proof_evidence": {
      "type": "object",
      "required": ["command", "key_line", "exit_code"],
      "properties": {
        "command": {"type": "string"},
        "key_line": {"type": "string"},
        "exit_code": {"type": "integer"}
      }
    }
  }
}
```
