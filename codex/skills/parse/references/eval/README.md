# Parse Eval Suite

This directory holds the fixture-based regression suite for the `$parse` collector and its slice-aware evidence model.

## Intent
- Cover each dominant architecture label with at least one positive fixture.
- Keep repo kind coverage broad without rewarding false confidence.
- Check focus-path observations so hybrid repos can expose slice-local exceptions.
- Catch common near-miss errors such as `services/` folders being mistaken for microservices.

## Files
- `suite.yaml`: fixture cases and expected collector outcomes.
- `fixtures/`: synthetic repositories used as stable local evidence.

## Run
```bash
uv run --with pyyaml python codex/skills/parse/scripts/eval_parse_collector.py \
  --suite codex/skills/parse/references/eval/suite.yaml
```
