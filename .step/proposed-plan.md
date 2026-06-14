# Plan: seq activation audit and current-session exclusion

## Summary

Implement the focused seq query-lift improvement for skill activation audits. The governing invariant is that a skill activation audit has one canonical command surface that classifies real activation evidence separately from pasted skill text and other references, while common forensic commands can exclude the current session without dropping to a raw `seq query`.

## Implementation

- step=freeze current seq surfaces; owner=implementer; success_criteria=record current skills-zig and dotfiles state, Zig version, target files, and existing command support before mutation.
- step=wire shared CLI option support; owner=skills-zig implementer; success_criteria=`skill-audit`, `skill-success-rank`, `workflow-audit`, and `message-search` accept/document `--exclude-current`; `skill-audit` accepts/documents `--last`; unsupported commands still reject unsupported flags.
- step=implement activation mode; owner=skills-zig implementer; success_criteria=`seq skill-audit --skill <name> --mode activation --last 36h --exclude-current` emits evidence buckets for `explicit_user_call`, `implicit_assistant_call`, `injected_skill_block`, and `other_reference` with activation verdicts.
- step=add regressions; owner=skills-zig implementer; success_criteria=tests cover explicit user call, implicit assistant call, pasted skill block non-activation, zero-result rows, `--last`, and current-session exclusion across target commands.
- step=update docs and version; owner=implementer; success_criteria=seq README and dotfiles `$seq` skill prefer the activation audit command for this query family while preserving `seq query` as valid when it is the most efficient route; `apps/seq/VERSION` is bumped.
- step=run fixed-point review; owner=implementer; success_criteria=root-equivalent fixed-point review clears duplicate-owner, additive-scaffold, ablation, and one-change gates.
- step=run proof bundle; owner=implementer; success_criteria=`zig build test-seq --summary all`, `zig build build-seq -Doptimize=ReleaseFast --summary all`, help output, smoke activation command, doc validation, projection checks, and diff checks pass or have exact blockers.
- step=close durable state; owner=implementer; success_criteria=`st complete` records proof for every task, `st assert-projection` passes, and final response reports graph debt, proof, fixed-point state, and residual risk.

## Locked Decisions

- Add `skill-audit --mode activation`; do not create a new top-level command.
- Add `--exclude-current` to `skill-audit`, `skill-success-rank`, `workflow-audit`, and `message-search`.
- Add `--last <Nm|Nh|Nd>` to `skill-audit`.
- Preserve raw `seq query` as a valid efficient route; the command improvements are for recurring query shapes, not a prohibition.
- Treat pasted `<skill>...</skill>` blocks as `injected_skill_block`, not activation.
- Keep mutation single-writer; use root-equivalent fixed-point/adversarial review.

## Validation

- `zig version`
- `zig build test-seq --summary all`
- `zig build build-seq -Doptimize=ReleaseFast --summary all`
- `./zig-out/bin/seq skill-audit --help`
- `./zig-out/bin/seq message-search --help`
- `./zig-out/bin/seq workflow-audit --help`
- `./zig-out/bin/seq skill-success-rank --help`
- `./zig-out/bin/seq skill-audit --skill universalist --mode activation --last 36h --exclude-current --format table`
- `uv run --with pyyaml -- python3 codex/skills/.system/skill-creator/scripts/quick_validate.py codex/skills/seq`
- `st doctor --file .step/st-plan.jsonl`
- `st assert-projection --file .step/st-plan.jsonl`
- `git diff --check`
