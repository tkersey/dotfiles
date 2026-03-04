# Eval Suite Schema

## Files
- `.saddle-up/suite.yaml`
- `.saddle-up/scoring.yaml`
- `.saddle-up/state.yaml`
- `.saddle-up/runs.jsonl`

## `suite.yaml`

```yaml
version: 1
mix:
  curated: 0.6
  replay: 0.4
cases:
  - id: curated-clarity
    source: curated
    prompt: "Review AGENTS.md and provide the top 3 ambiguity risks and fixes."
    checks:
      - type: min_chars
        value: 120
  - id: replay-0001
    source: replay
    prompt: "<prompt from seq opencode-prompts>"
    checks:
      - type: min_chars
        value: 80
```

Case fields:
- `id` (string, unique)
- `source` (`curated` or `replay`)
- `prompt` (string)
- `checks` (optional array)

Check types:
- `contains`: require substring
- `not_contains`: forbid substring
- `regex`: require regex match
- `min_chars`: require minimum output length

## `scoring.yaml`

```yaml
version: 1
threshold: 0.8
pass_definition: task_outcome_policy_no_critical_errors
suite_size: 10
critical_error_classes:
  - contract violation
  - unhandled exception
  - traceback
  - meshtruthfailed
policy_forbidden_patterns:
  - "cannot comply"
  - "ignored instructions"
```

## `state.yaml`

```yaml
version: 1
consecutive_passes: 0
reliable: false
cycle_count: 0
continuous_session_id: null
stop_reason: none
last_passing_commit: null
last_run_at: null
last_pass_rate: 0.0
last_result:
  gate_passed: false
  regression_reverted: false
  stop_reason: none
```

## `runs.jsonl`
One record per continuous cycle.

```json
{"run_id":"20260304T041522Z-c00001","continuous_session_id":"20260304T041522Z","cycle":1,"pass_rate":0.8,"gate_passed":true}
```

Required fields:
- `run_id`
- `continuous_session_id`
- `cycle`
- `pass_rate`
- `gate_passed`
- `threshold`
- `reliable`
- `consecutive_passes`
- `model`
- `branch`
- `stop_reason`
- `elapsed_seconds`
