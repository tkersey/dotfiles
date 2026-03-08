# TK Replay Eval Suite

This directory holds the leakage-audited replay benchmark for `$tk`.

## Intent
- Distill real session patterns into replayable, synthetic prompts.
- Judge seam choice and code shape before prose polish.
- Catch regressions in strict-output worker mode, advice mode, and non-diff implementation reporting.
- Exercise internal `$parse` preflight cases without allowing output-contract leakage.

## Files
- `replay-suite.yaml`: replay-distilled cases and machine checks.
- `shadow-mode.md`: how to use the suite against fresh sessions after the static pass is green.
- `shadow-suite-YYYY-MM-DD.yaml`: fresh-session shadow cases for one pass.
- `shadow-pass-YYYY-MM-DD.md`: scored shadow-pass report with verdicts and drift notes.

## Leakage policy
- Prompts are synthetic reconstructions, not transcript copies.
- `source_session` metadata records provenance for maintainers.
- Real transcript excerpts stay out of public exemplars/docs.

## Run
```bash
uv run --with pyyaml python codex/skills/tk/scripts/tk_replay_benchmark.py \
  --suite codex/skills/tk/references/eval/replay-suite.yaml \
  --timeout-seconds 240
```

Use `--dry-run` to lint and preview the suite without executing Codex.
Add `--model ...` only when the local Codex account/provider supports explicit model selection.
