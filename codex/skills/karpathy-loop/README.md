# karpathy-loop

A Claude Skill for improving prompts, agent instructions, Claude Skills, and workflows through a measured Karpathy-style optimization loop.

## What it does

This skill turns prompt improvement into a controlled experiment:

1. Score the current prompt.
2. Find the biggest recurring failure.
3. Make one focused change.
4. Retest on the same cases.
5. Keep the change only if it improves the score.
6. Repeat until the prompt is good enough or the experiment budget is reached.

## Install

Upload `karpathy-loop.zip` as a custom skill. The zip contains the required folder structure:

```text
karpathy-loop.zip
└── karpathy-loop/
    ├── SKILL.md
    ├── README.md
    ├── examples/
    ├── templates/
    └── scripts/
```

The skill name is lowercase and hyphenated: `karpathy-loop`.

## Fastest way to use it

Paste this into Claude after enabling the skill:

```text
Run a Karpathy loop on the prompt below. Create 5 synthetic test cases and 4 success checks. Run 3 experiments. Give me the final optimized prompt.

[paste prompt]
```

## More controlled usage

```text
Run a Karpathy loop on this prompt.

Target prompt:
[paste prompt]

Goal:
[what the prompt should reliably do]

Test cases:
1. Input: ...
   Good output should: ...
2. Input: ...
   Good output should: ...
3. Input: ...
   Good output should: ...

Success checks:
1. Does the output follow the requested format?
2. Does the output answer the actual request?
3. Does the output avoid unsupported claims?
4. Does the output include a concrete next step?

Budget:
Run 5 experiments.
```

## Files included

- `SKILL.md` — the actual skill instructions.
- `examples/simple-invocation.md` — the simplest usage template.
- `examples/sales-email-example.md` — concrete business prompt example.
- `examples/skill-optimization-example.md` — example for optimizing another skill or long instruction.
- `templates/cases.yaml` — test case template.
- `templates/evals.yaml` — binary eval checklist template.
- `templates/experiment-log.md` — experiment log template.
- `templates/final-report.md` — final report template.
- `templates/results.tsv` — score tracking template.
- `scripts/summarize_results.py` — optional helper for summarizing a results TSV file.

## Recommended default settings

```yaml
experiments: 3
test_cases: 5
success_checks: 4
holdout_cases: 1-2 if enough cases exist
minimum_improvement_to_keep: +10 percentage points or +2 passed checks
```

## Important rule

Never optimize by vibes. Every kept change should be tied to a test case, an observed failure, a targeted mutation, and a measured improvement.
