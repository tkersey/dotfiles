# Eval Suite Schema

## Files
- `.saddle-up/suite.yaml`
- `.saddle-up/scoring.yaml`
- `.saddle-up/state.yaml`
- `.saddle-up/runs.jsonl`

## `suite.yaml`

```yaml
version: 1
profile: gemini-2.5-pro
mix:
  curated: 0.8
  replay: 0.2
cases:
  - id: curated-gemini-proof-honesty
    source: curated
    prompt: |
      Read `AGENTS.md`. Return exactly:
      BEGIN_FINAL
      If a command, test, or proof step was not executed in this turn, say `not run`; do not imply success.
      END_FINAL
    checks:
      - type: regex
        value: '(?is)^\s*BEGIN_FINAL\nIf a command, test, or proof step was not executed in this turn, say `not run`; do not imply success\.\nEND_FINAL\s*$'
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

Optional top-level fields:
- `profile` (for example `generic` or `gemini-2.5-pro`)
- `mix` (`curated` / `replay` ratios used when selecting the run subset)

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
last_external_blocker: null
last_result:
  gate_passed: false
  regression_reverted: false
  post_improver_curated_gate_ran: false
  post_improver_curated_gate_passed: false
  post_improver_curated_pass_rate: null
  post_improver_failed_case_ids: []
  post_improver_external_blocker: null
  post_improver_reverted: false
  post_improver_reverted_rule_ids: []
  post_improver_reverted_paths: []
  post_improver_fallback_full_file_revert_used: false
  external_blocker: null
  stop_reason: none
```

## `runs.jsonl`
One record per continuous cycle.

```json
{"run_id":"20260304T041522Z-c00001","continuous_session_id":"20260304T041522Z","cycle":1,"pass_rate":0.8,"gate_passed":true,"external_blocker":null,"post_improver_curated_gate_ran":true,"post_improver_curated_gate_passed":true,"post_improver_reverted":false}
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
- `external_blocker`
- `elapsed_seconds`

Additional Gemini post-improver gate fields:
- `post_improver_curated_gate_ran`
- `post_improver_curated_gate_passed`
- `post_improver_curated_pass_rate`
- `post_improver_failed_case_ids`
- `post_improver_external_blocker`
- `post_improver_reverted`
- `post_improver_reverted_rule_ids`
- `post_improver_reverted_paths`
- `post_improver_fallback_full_file_revert_used`
