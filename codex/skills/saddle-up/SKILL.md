---
name: saddle-up
description: Continuously evaluate and improve AGENTS.md-style harness instructions through explicit-trigger OpenCode loops with an explicit model. Use when you want recurring harness reliability runs, automatic eval-branch commits and PR updates for passing harness/doc changes, and regression auto-revert without scheduler/cron automation.
---

# Saddle Up

## Overview
Run an explicit-trigger continuous loop that updates a target harness, evaluates it against a fixed suite, and promotes passing changes through a dedicated branch + PR flow.

## Quick Start
Use an explicit model on every run.

```bash
uv run --with pyyaml codex/skills/saddle-up/scripts/saddle_up.py run \
  --repo /path/to/target-repo \
  --harness-path AGENTS.md \
  --model openrouter/google/gemini-2.5-pro
```

Stop gracefully from another shell:

```bash
touch /path/to/target-repo/.saddle-up/STOP
```

Inspect state:

```bash
uv run --with pyyaml codex/skills/saddle-up/scripts/saddle_up.py status \
  --repo /path/to/target-repo
```

Refresh replay cases from OpenCode prompt history (`seq opencode-prompts`):

```bash
uv run --with pyyaml codex/skills/saddle-up/scripts/saddle_up.py replay-refresh \
  --repo /path/to/target-repo
```

## Workflow
1. Validate preflight: git repo, harness path, explicit model, `opencode` availability.
2. Bootstrap `.saddle-up/` files if missing.
3. Start explicit-trigger continuous improve+eval cycles.
4. Enforce pass gate (`>=80%` by default) and docs-scope write policy.
5. Auto-commit passing changes to `saddle-up/eval` and open/update PR.
6. Auto-revert harness on regression below gate using the last passing commit.
7. Stop automatically when reliability reaches 3 consecutive passing cycles.
8. Stop gracefully on manual interrupt or when stop file exists (`.saddle-up/STOP` by default).

## Defaults and Gates
- `threshold`: `0.80`
- `stability_window`: `3` consecutive passes
- suite mix target: `60% curated / 40% replay`
- stop file: `.saddle-up/STOP` (override with `--stop-file`)
- branch: `saddle-up/eval`

## Repo Contract
`run` and `status` read/write these files under the target repo:
- `.saddle-up/suite.yaml`
- `.saddle-up/scoring.yaml`
- `.saddle-up/state.yaml`
- `.saddle-up/runs.jsonl`

Schema details:
- [references/eval_suite_schema.md](references/eval_suite_schema.md)
- [references/opencode_runner_contract.md](references/opencode_runner_contract.md)

## Guardrails
- Keep mutation scope to harness/docs plus `.saddle-up/*` state files.
- Fail run-level success when non-doc file edits appear.
- Do not auto-merge PRs.
- Require explicit model selection per invocation.
- No scheduler/cron path in this version; start runs explicitly with `run`.

## Troubleshooting
- If `yaml` import fails, run with `uv run --with pyyaml ...`.
- If you need to stop a running loop gracefully, create the stop file path (default `.saddle-up/STOP`) or interrupt with `Ctrl+C`.
- If `gh` auth fails, run `gh auth login` before enabling PR automation.
