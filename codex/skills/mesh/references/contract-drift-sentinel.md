# Contract Drift Sentinel

Purpose:

- Detect drift between reducer/fixer agent prompts, global orchestration policy, and mesh skill docs.
- Fail fast when dual-author defaults are missing or partially updated.

Coverage anchors:

- `codex/AGENTS.md`: pipeline + default fanout must state `coder x1 + reducer x1 -> fixer -> prover -> integrator` and include the `csv_rows_missing==0` artifact retention gate.
- `codex/skills/mesh/SKILL.md`: same pipeline/fanout language and legacy `triplet_index` compatibility note.
- `codex/skills/mesh/agents/openai.yaml`: default prompt mentions `coder x1 + reducer x1`.
- `mesh prepare_crfip_batch`: durable wave CSV preparation under the artifact root.
- `mesh doctor`: postmortem gate that checks mesh-truth + artifacts + lane completeness.
- `codex/agents/reducer.toml`: explicit `$reduce` invocation and `Reduce Record` keys.
- `codex/agents/fixer.toml`: deterministic coder/reducer candidate adjudication.
- `codex/config.toml`: reducer description explicitly references `$reduce`.
- `codex/skills/mesh/references/output-contract.md`: reducer lane + `reduce_record` schema guidance.

Run:

```bash
mesh contract_drift_lint --repo-root /Users/tk/.dotfiles
```

Expected outcome:

- Exit code `0`: all required anchors present.
- Exit code `1`: drift detected; script prints missing anchors by file.
