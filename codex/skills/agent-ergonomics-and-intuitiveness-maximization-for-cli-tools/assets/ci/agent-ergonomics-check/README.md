# Agent Ergonomics CI Action

Reusable GitHub Action that runs lightweight scored-surface continuity checks on every PR.

## What it does

Two checks, fast (no LLM API calls required):

1. **Surface deletion guard** — diffs the current `inventory_surfaces.sh` output against a committed `audit/baseline.jsonl`. Any surface in the baseline that no longer exists in the inventory is treated as a HARD failure (PR removed a flag/verb without a deprecation path). The skill's One Rule says "never punish a reasonable misstep" — removing a working surface punishes existing agents.

2. **New-surface flagging** — surfaces present in the inventory but absent from the baseline are reported in the step summary as "needs scoring at next full pass." Doesn't fail the PR; informs the maintainer.

For full LLM-driven re-scoring, run a `mini` or `full` mode pass locally and commit the updated `audit/baseline.jsonl`. This action is the cheap regression check; it complements but doesn't replace a full audit.

## Usage

In your repo's `.github/workflows/ergonomics-check.yml`:

```yaml
name: Agent Ergonomics Check

on:
  pull_request:
    paths:
      # Trigger on any PR touching CLI-relevant code
      - 'src/**/cli.rs'
      - 'cmd/**/*.go'
      - 'src/**/cli.py'
      - 'README.md'

jobs:
  ergonomics:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build CLI
        run: cargo build --release

      - name: Agent ergonomics check
        uses: ./assets/ci/agent-ergonomics-check
        with:
          target-binary: target/release/mytool
          baseline: audit/baseline.jsonl
          skill-path: .claude/skills/agent-ergonomics-and-intuitiveness-maximization-for-cli-tools

      - name: Upload scorecard
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: scorecard
          path: .audit_ci/audit/scorecard.html
```

## Inputs

| Input | Description | Default | Required |
|-------|-------------|---------|----------|
| `target-binary` | Path to the post-build CLI binary | — | yes |
| `baseline` | Path to the committed baseline scorecard JSONL | — | yes |
| `skill-path` | Path to the skill on the runner | — | yes |

## Outputs

| Output | Description |
|--------|-------------|
| `scorecard-html` | Rendered HTML scorecard for the run |
| `surface-delta` | Comma-separated counts: `removed=<N>,added=<N>` |

## Generating the baseline

```bash
# Run a full audit on main first (one-time setup).
bash <skill>/scripts/scaffold-workspace.sh /tmp/audit_baseline /path/to/repo
# ... run full audit ...
cp /tmp/audit_baseline/audit/agent_surfaces.jsonl audit/baseline.jsonl
git add audit/baseline.jsonl && git commit -m "Pin agent ergonomics baseline"
```

## Limits

This action does NOT call the LLM scorer — it only diffs surface sets. Full re-scoring requires the parent agent + API spend; do that locally or in a separate workflow with secrets. The action's value: prevents accidental surface deletion (the most common regression class) without per-PR token spend.
