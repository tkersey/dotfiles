---
name: saddle-up
description: Continuously evaluate and improve AGENTS.md-style harness instructions through explicit-trigger OpenCode loops with an explicit model. Use when you want recurring harness reliability runs, especially for Gemini 2.5 Pro/OpenCode harness tuning, clean-repo eval cycles, curated exact-output probes, automatic eval-branch commits and PR updates for passing harness/doc changes, and external-blocker detection or regression auto-revert without scheduler/cron automation.
---

# Saddle Up

## Overview
Run an explicit-trigger continuous loop that updates a target harness, evaluates it against a fixed suite, and promotes passing changes through a dedicated branch + PR flow. Recent session-mining updates bias the loop toward Gemini 2.5 Pro failure modes: exact-output envelopes, proof honesty, failure-recovery wording, workdir discipline, and immediate external-blocker reporting.

## Quick Start
Use an explicit model on every run, and prefer a clean target repo or a docs-only worktree.

```bash
uv run --with pyyaml codex/skills/saddle-up/scripts/saddle_up.py run \
  --repo /path/to/target-repo \
  --harness-path AGENTS.md \
  --model google/gemini-2.5-pro
```

For a bounded debugging pass that cannot hang forever:

```bash
uv run --with pyyaml codex/skills/saddle-up/scripts/saddle_up.py run \
  --repo /path/to/target-repo \
  --harness-path AGENTS.md \
  --model google/gemini-2.5-pro \
  --no-commit \
  --max-cycles 1 \
  --opencode-timeout-seconds 180
```

If the improver path is the problem and you want to evaluate the current harness as-is:

```bash
uv run --with pyyaml codex/skills/saddle-up/scripts/saddle_up.py run \
  --repo /path/to/target-repo \
  --harness-path AGENTS.md \
  --model google/gemini-2.5-pro \
  --skip-improve \
  --no-commit \
  --max-cycles 1 \
  --opencode-timeout-seconds 180
```

Refresh a Gemini-tuned suite before the next run:

```bash
uv run --with pyyaml codex/skills/saddle-up/scripts/saddle_up.py replay-refresh \
  --repo /path/to/target-repo \
  --harness-path AGENTS.md \
  --model google/gemini-2.5-pro \
  --refresh-curated
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
  --repo /path/to/target-repo \
  --model google/gemini-2.5-pro
```

## Workflow
1. Validate preflight: git repo, harness path, explicit model, `opencode` availability, and no pre-existing non-doc changes that would poison the docs-only gate.
2. Bootstrap `.saddle-up/` files if missing, using model-aware defaults when the target is Gemini 2.5 Pro.
3. Start explicit-trigger continuous improve+eval cycles.
4. Use Gemini-oriented curated probes for exact-output blocks, local-evidence-first behavior, `not run` honesty, retry-path wording, workdir discipline, anti-drift, and external hard stops.
5. Filter replay prompts toward harness-like OpenCode history instead of short/noisy chat fragments.
6. Enforce pass gate (`>=80%` by default) and docs-scope write policy.
7. Auto-commit passing changes to `saddle-up/eval` and open/update PR.
8. Auto-revert harness on regression below gate using the last passing commit, but do not revert for external provider/quota/auth/network blockers.
9. Stop automatically when reliability reaches 3 consecutive passing cycles, an external blocker is detected, or a manual stop/cycle cap is reached.

## Defaults and Gates
- `threshold`: `0.80`
- `stability_window`: `3` consecutive passes
- `opencode_timeout_seconds`: `180`
- Gemini 2.5 Pro bootstrap mix: `80% curated / 20% replay`
- generic bootstrap mix: `60% curated / 40% replay`
- stop file: `.saddle-up/STOP` (override with `--stop-file`)
- `max_cycles`: unbounded unless set
- branch: `saddle-up/eval`
- `replay-refresh --refresh-curated` reseeds the curated suite from the current model profile

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
- Fail fast when the repo already contains non-doc changes before the loop starts.
- Fail run-level success when non-doc file edits appear.
- Do not auto-merge PRs.
- Require explicit model selection per invocation.
- Stop and surface external quota/auth/provider/network blockers instead of treating them as harness regressions.
- No scheduler/cron path in this version; start runs explicitly with `run`.

## Troubleshooting
- If `yaml` import fails, run with `uv run --with pyyaml ...`.
- If a run appears stuck inside `opencode run`, lower or set `--opencode-timeout-seconds` and retry.
- If the improver child is the part that hangs and you already trust the current harness edits, rerun with `--skip-improve` to evaluate the current harness without another rewrite attempt.
- If `openrouter/google/gemini-2.5-pro` hits credit or `max_tokens` failures, switch to direct `google/gemini-2.5-pro` before spending more harness cycles.
- For one-cycle diagnosis without commits or PR side effects, use `--no-commit --max-cycles 1`.
- If the loop stops with `external_blocker`, clear the provider/auth/network issue first; do not keep cycling a blocked harness.
- If replay prompts feel noisy, rerun `replay-refresh --model google/gemini-2.5-pro --refresh-curated` to restore the Gemini-focused suite.
- If you need to stop a running loop gracefully, create the stop file path (default `.saddle-up/STOP`) or interrupt with `Ctrl+C`.
- If `gh` auth fails, run `gh auth login` before enabling PR automation.
