# OpenCode Runner Contract

## Invocation
Saddle-up uses OpenCode CLI in headless mode:

```bash
opencode run --model <provider/model> --dir <repo> --format json "<message>"
```

Individual calls may be capped by the runner's `--opencode-timeout-seconds` option.

## Expectations
- `--model` is mandatory.
- `--format json` output is parsed line-by-line as JSON events.
- Non-JSON lines are tolerated and ignored.
- Return code `0` is required for a case to pass.
- Timed-out OpenCode calls return a non-zero status and count as failures.
- The repo must start clean from a docs-scope perspective; pre-existing non-doc changes fail preflight.
- The loop is explicit-trigger continuous (`run` command); no scheduler/cron path.

## Text Extraction
The runner recursively extracts strings from JSON event objects. Strings from fields such as `text`, `content`, `message`, and nested arrays/maps are concatenated into `output_text`.

## Case Scoring
For each case:
1. Evaluate declared checks (`contains`, `not_contains`, `regex`, `min_chars`).
2. Enforce `policy_forbidden_patterns` from scoring config.
3. Enforce `critical_error_classes` absence.
4. Require OpenCode return code `0`.

A case passes only when all checks above pass.

## Improvement Loop Prompt
Before eval in each cycle, the runner sends an improvement prompt requesting harness/doc updates with strict write-scope boundaries. For Gemini 2.5 Pro, that prompt explicitly targets exact-output envelopes, `not run` honesty, local-evidence-first behavior, retry-path wording, workdir discipline, anti-drift, and external hard-stop reporting.

## Replay Refresh
`replay-refresh` ranks recent OpenCode prompts and prefers harness-shaped prompts over short/noisy chat fragments. With `--refresh-curated --model google/gemini-2.5-pro`, it also reseeds the curated suite with Gemini-specific exact-output probes.

## Failure Signals
The runner marks run failure on:
- OpenCode invocation errors
- timed-out OpenCode improve/eval calls
- detected external blockers such as quota, credits, auth, provider, or network failures
- pass rate below threshold
- non-doc file mutations in git status
- policy/critical error matches

## Continuous Stop Conditions
The runner exits when one of these occurs:
- reliability gate reached (`pass_rate >= threshold` and required consecutive pass streak met)
- external blocker detected (reported and persisted instead of auto-reverting the harness)
- stop file detected (default `.saddle-up/STOP`, configurable via `--stop-file`)
- optional cycle cap reached (`--max-cycles`)
- operator interruption (`Ctrl+C`)
- fatal command error

## Promotion Signals
The runner can auto-promote only when:
- pass rate meets threshold
- scope checks pass
- git commit succeeds on eval branch
- PR create/update succeeds (if `gh` is available)

Auto-revert is reserved for harness regressions after a prior passing cycle; it does not fire for external provider/quota/auth/network blockers.
