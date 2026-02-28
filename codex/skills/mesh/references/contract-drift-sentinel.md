# Contract Drift Sentinel

Purpose:

- Detect drift between reducer/fixer agent prompts, global orchestration policy, and mesh skill docs.
- Fail fast when dual-author defaults are missing or partially updated.

Coverage anchors:

- `codex/AGENTS.md`: pipeline + default fanout must state `coder + reducer -> fixer -> integrator`.
- `codex/skills/mesh/SKILL.md`: same pipeline/fanout language and legacy `triplet_index` compatibility note.
- `codex/skills/mesh/agents/openai.yaml`: dual-author default prompt mentions `coder x2 + reducer x1`.
- `codex/agents/reducer.toml`: explicit `$reduce` invocation and `Reduce Record` keys.
- `codex/agents/fixer.toml`: deterministic coder/reducer candidate adjudication.
- `codex/config.toml`: reducer description explicitly references `$reduce`.
- `codex/skills/mesh/references/output-contract.md`: reducer lane + `reduce_record` schema guidance.

Run:

```bash
uv run /Users/tk/.dotfiles/codex/skills/mesh/references/contract_drift_lint.py
```

Expected outcome:

- Exit code `0`: all required anchors present.
- Exit code `1`: drift detected; script prints missing anchors by file.
