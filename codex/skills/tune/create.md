# Create mode

## Create mode

1. Search for a skill already covering the intent.
2. Collect two or three realistic trigger prompts and at least one near miss.
3. State the problem, success criterion, and non-trigger boundary.
4. Classify the skill as `decision`, `execution`, `evidence`, `orchestration`, or
   `mixed` only when the classification affects design or observability.
5. Map activation metadata, the always-required kernel, common resources, and
   each conditional resource.
6. Scaffold when useful:
   ```bash
   uv run --with pyyaml -- python3 \
     codex/skills/.system/skill-creator/scripts/init_skill.py \
     <skill-name> --path codex/skills
   ```
7. Author the smallest operative package.
8. Evaluate decision instrumentation; do not add it by default.
9. Align `agents/openai.yaml`.
10. Remove redundant doctrine, examples, and generated ceremony.

If an existing skill already owns the intent, prefer extending it or report
`no-change`; do not create a synonym package.
