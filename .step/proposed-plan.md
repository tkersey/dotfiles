# Plan: Build `auto` Skill for Evidence-Backed Skill Optimization

## Summary

Build `codex/skills/auto` as a real shell-backed Codex skill for closed-loop skill ecosystem improvement. First implement the tracked skill folder and helper scripts, then validate the full skill corpus through `codex/skills/auto/scripts/auto-validate-corpus codex/skills`, and consider the work done only when `auto scan/status` work read-only, bootstrap can generate advisory policies, optimize-one enforces one strong evidence-backed target, and protected skills remain untouched.

## Implementation Brief

- step=initialize durable plan; owner=implementer; success_criteria=`st import-proposed-plan`, `st prime`, and `update_plan` projection succeed with `[st-id]` prefixes.
- step=scaffold `codex/skills/auto`; owner=implementer; success_criteria=required files exist and command scripts are executable.
- step=implement helpers and commands; owner=implementer; success_criteria=read-only commands are side-effect free and mutating commands enforce protected-skill and evidence gates.
- step=run fixed-point review/repair; owner=implementer; success_criteria=no material findings remain after review pass.
- step=validate; owner=implementer; success_criteria=`auto-validate-corpus codex/skills`, smoke tests, and `git diff --check` pass.
- step=ship; owner=implementer; success_criteria=`$ship` opens/updates PR with proof, or reports exact blocker.

## Locked Decisions

- Preserve `.system/*` as protected; do not modify `quick_validate.py`.
- Use `codex/skills/auto/scripts/auto-validate-corpus` as the auto-owned corpus validation wrapper.
- Implement `auto-optimize-one` as command-assisted `prepare` and `finalize` phases, with the agent owning `$seq`, `$refine`, `$ship`, and `$fin` judgment.
- Bootstrap policy rollout is the only many-skill exception; later optimization remains one ordinary skill, one evidence-backed change set, one PR.
- Do not create cron entries, durable local report directories, GitHub issues, `.autoupdate`, scheduler state, or protected-skill patches.

## Validation

- `codex/skills/auto/scripts/auto-validate-corpus codex/skills`
- `test -f` for all required files.
- `test -x` for command scripts.
- `auto-scan` and `auto-status` run without creating files.
- `auto-optimize-one prepare` rejects protected skill `seq`.
- `auto-optimize-one prepare` rejects weak-only evidence class.
- `git diff --check`
