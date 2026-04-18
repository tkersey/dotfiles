---
name: karpathy-loop
description: Use when the user wants to improve, optimize, debug, test, or iterate on a prompt, agent instruction, Claude Skill, or workflow through a measured eval loop. Runs baseline tests, creates binary success checks, changes one thing at a time, retests, keeps/reverts changes, and returns an optimized final prompt or skill.
---

# Karpathy Loop

Use this skill to improve a target prompt, agent instruction, skill, or workflow by running controlled experiments.

The loop is:

```text
Baseline → Diagnose → Change one thing → Retest → Keep or reject → Repeat → Validate
```

The purpose is to improve measured behavior, not to rewrite by vibes.

---

## Fast Path

When the user asks to “run a Karpathy loop,” “optimize this prompt,” “improve this skill,” or similar, proceed with this default workflow unless the user gives different constraints.

1. Identify the target prompt, instruction, skill, or workflow.
2. Define what success means in one paragraph.
3. Create or use 3–6 binary success checks.
4. Create or use 5–10 test cases.
5. Reserve 1–3 holdout cases if there are enough cases.
6. Score the original target as the baseline.
7. Run the requested number of experiments, defaulting to 3.
8. In each experiment, change exactly one meaningful thing.
9. Keep the change only if it improves the score without meaningful regressions.
10. Return the final optimized target and a concise experiment report.

If the user provides too little information, make reasonable synthetic test cases and label them synthetic. Do not block on clarification unless the task, target, or success condition is genuinely ambiguous.

---

## Inputs

Prefer this structure, but adapt to whatever the user provides.

```text
Target:
[prompt, skill, agent instruction, or workflow to improve]

Goal:
[what the target should reliably accomplish]

Test cases:
[example inputs and what good outputs should satisfy]

Success checks:
[3–6 yes/no checks]

Budget:
[number of experiments]
```

If `Test cases` are missing, create 5 synthetic cases.

If `Success checks` are missing, create 4 checks based on the goal.

If `Budget` is missing, run 3 experiments.

---

## Output Contract

For normal user-facing runs, produce this final structure:

```md
# Karpathy Loop Result

## Setup
- Target:
- Goal:
- Test cases:
- Success checks:
- Budget:

## Baseline Score
...

## Experiments
### Experiment 1
- Hypothesis:
- Change made:
- Before:
- After:
- Decision: KEEP / REJECT
- Reason:

## Final Score
...

## Changes Kept
1.

## Changes Rejected
1.

## Remaining Weaknesses
...

## Final Optimized Target
[paste full final prompt, skill, or instruction]
```

When the user asks for a downloadable package, create files using the companion templates in `templates/` and examples in `examples/`.

---

## Success Checks

Success checks must be binary, observable, and specific.

Good checks:

```text
Does the output follow the requested format?
Does the output answer the actual user request?
Does the output avoid unsupported claims?
Does the output include exactly one concrete next step?
Does the output stay under the word limit?
```

Bad checks:

```text
Is it good?
Is it high quality?
Is it compelling?
```

Score each check as:

```text
PASS = 1
FAIL = 0
UNCERTAIN = 0
```

Treat uncertainty as failure unless the user explicitly asks for a softer scoring method.

---

## Baseline Procedure

Before editing the target:

1. Run the original target against every optimization test case.
2. Score each output against every success check.
3. Calculate the baseline score.
4. Identify the largest recurring failure.

Use this table:

```text
Case | Check 1 | Check 2 | Check 3 | Check 4 | Score | Notes
```

Calculate:

```text
score = passed_checks / total_checks
```

Example:

```text
Baseline: 14 / 25 = 56%
```

Do not change the target until the baseline is scored.

---

## Failure Analysis

Before each mutation, write:

```text
Main failure:
Evidence:
Likely cause:
Proposed one-change fix:
Risk of the fix:
```

Prioritize failures by:

1. Safety, factuality, or compliance failures.
2. Format failures that break usability.
3. Missing required content.
4. Generic or low-specificity content.
5. Tone, polish, or concision issues.

---

## Mutation Rules

Each experiment may make one meaningful change.

Allowed changes:

- Add one missing constraint.
- Clarify one ambiguous instruction.
- Add or tighten an output format.
- Add one high-signal example.
- Remove one conflicting instruction.
- Move an important rule earlier.
- Add one “do not” rule for a repeated failure.
- Add one self-check before final output.
- Simplify a confusing section.

Avoid:

- Rewriting the whole target at once.
- Adding many rules in one experiment.
- Changing test cases after seeing failures.
- Changing success checks to make the score look better.
- Copying test cases into the prompt as examples.
- Making the target much longer without a measurable benefit.
- Removing safety, accuracy, or compliance constraints.

---

## Retest Procedure

After a mutation:

1. Run the candidate against the same optimization cases.
2. Score with the same success checks.
3. Compare against the current best version.
4. Note improvements and regressions.

Use this decision rule:

```text
KEEP if the candidate improves the score and introduces no serious regression.
REJECT if the score is flat, worse, noisy, overfit, bloated, or less safe.
```

Default keep threshold:

```text
At least +10 percentage points for small test sets, or at least +2 passed checks.
```

If scores tie, keep the simpler version.

---

## Holdout Validation

If there are at least 7 total cases, reserve 20–30% as holdout.

Rules:

1. Do not use holdout failures to design early mutations.
2. Run holdout after the final kept change or after every 3 kept changes.
3. If holdout score is much worse than optimization score, warn that the target may be overfit.
4. Do not silently tune to the holdout set.

Default acceptable gap:

```text
holdout_score is within 10 percentage points of optimization_score
```

---

## Experiment Log Format

For each experiment, use:

```md
## Experiment N

### Hypothesis
[what this change should improve]

### Change Made
[the one change]

### Score
Before: X / Y = Z%
After: X / Y = Z%

### Improvements
...

### Regressions
...

### Decision
KEEP or REJECT

### Lesson
...
```

---

## Final Report Rules

The final answer must include:

1. Baseline score.
2. Final score.
3. Number of experiments run.
4. Kept changes.
5. Rejected changes.
6. Remaining weaknesses.
7. The full final optimized target.

Be concise enough that the user can immediately copy and use the final target.

---

## Practical Invocation Examples

Read `examples/simple-invocation.md` when the user wants the easiest way to use the skill.

Read `examples/sales-email-example.md` when the user wants a concrete business prompt optimization example.

Read `examples/skill-optimization-example.md` when the target itself is a Claude Skill or long agent instruction.

---

## Template Files

Use these when the user wants artifacts, repeatable process files, or a downloadable skill package:

- `templates/cases.yaml`
- `templates/evals.yaml`
- `templates/experiment-log.md`
- `templates/final-report.md`
- `templates/results.tsv`

---

## Core Principle

Every improvement must connect to this chain:

```text
test case → observed failure → one prompt change → retest → measured improvement
```

If that chain is missing, do not claim the prompt improved.
