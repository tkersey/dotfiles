---
name: logophile
description: "Precision rewrites + naming + doctrine synthesis: replace vague phrasing with sharper wording, choose names, and derive task-specific doctrine stacks when wording, naming, or doctrine output is explicitly requested. Triggers: `$logophile`, rewrite/reword/rephrase, tighten/sharpen/compress wording, choose final wording/phrasing, rename titles/labels/headings/skill names, derive doctrine words or mode words for a task. In operational turns, use only when wording, naming, or doctrine output is explicitly requested."
---

# Logophile

## Intent
Replace generic phrasing with sharper wording, choose better names, and synthesize task-fit doctrine stacks without semantic drift.

## Contract
- Preserve meaning, obligations, uncertainty, agency, sequence, numbers, quotes, code, and identifiers.
- Prefer substitution before deletion or reordering.
- Precision beats brevity when it is more exact for the audience and local context.
- In doctrine mode, each chosen word must add a distinct procedural gain.
- Prefer compact stacks over exhaustive dumps.
- A doctrine stack is incomplete without an unpacked doctrine block.
- Do not turn doctrine mode into hidden policy for unrelated operational turns.

## Modes
- `fast`: revised text only.
- `annotated`: edits + revised text.
- `delta`: minimal diff.
- `naming`: 3-7 candidates unless the user asks for one.
- `doctrine-fast`: stack + doctrine block only.
- `doctrine`: full doctrine analysis.
- `doctrine-annotated`: doctrine analysis + per-word rationale.

## CLI-tail-weighted output
- In multi-part outputs, end with the selected wording, best name, or final doctrine block.
- In multi-candidate outputs, end with `Best Pick:` or `Use This:`.
- In `fast` mode, keep the revised-text-only contract.

## Doctrine mode
Use doctrine mode when the task is to find semantically dense words that compress a useful operating doctrine for a task.

Rubric:
- choose 3-6 non-overlapping words
- prefer words that imply checks, constraints, or execution discipline
- avoid praise-only words that only change tone
- keep task-fit above novelty

## Doctrine output
### doctrine
- Task Reading
- Dominant Failure Pressures
- Stricter Variant
- Lighter Variant
- Words to Avoid
- Recommended Stack
- Prompt-Ready Doctrine Block
- Use This

### doctrine-annotated
Same as `doctrine`, plus a short per-word rationale before the final doctrine block.

## Naming mode
- Goal: shorter, more specific, and more distinctive.
- Output: 3-7 candidates, best first.

## Resources
- [precision_lexicon.md](references/precision_lexicon.md)
- [doctrine_word_bank.md](references/doctrine_word_bank.md)
- [task_pressure_map.md](references/task_pressure_map.md)
- [probe_cases.md](references/probe_cases.md)
- [doctrine_probe_cases.md](references/doctrine_probe_cases.md)
- [composition.md](references/composition.md)
