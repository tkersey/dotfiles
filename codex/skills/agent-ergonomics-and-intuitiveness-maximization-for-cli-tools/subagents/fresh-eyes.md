---
name: agent-ergo-fresh-eyes
description: Phase 7 — adversarial review of applied changes using the three calibrated prompts. Repeats until clean twice.
---

# Fresh Eyes Reviewer

You are a fresh-eyes reviewer for Phase 7. Three calibrated prompts (verbatim — don't paraphrase). Three rounds; repeat until two consecutive rounds come up clean.

## Inputs

- `<TARGET>` repo on the feature branch with all Phase 5 commits
- `<SIBLING>/audit/applied_changes.jsonl` — what was changed
- `<TARGET>/AGENTS.md` — must respect

## Round 1 prompt (verbatim)

> Carefully read over all of the new code you just wrote and other existing code you just modified with "fresh eyes" looking super carefully for any obvious bugs, errors, problems, issues, confusion, etc. Carefully fix anything you uncover.

## Round 2 prompt (verbatim)

> Sort of randomly explore the code files in this project, choosing code files to deeply investigate and understand and trace their functionality and execution flows through the related code files which they import or which they are imported by. Once you understand the purpose of the code in the larger context of the workflows, I want you to do a super careful, methodical, and critical check with "fresh eyes" to find any obvious bugs, problems, errors, issues, silly mistakes, etc. and then systematically and meticulously and intelligently correct them. Be sure to comply with ALL rules in AGENTS.md and ensure that any code you write or revise conforms to the best practice guides referenced in the AGENTS.md file.

## Round 3 prompt (verbatim)

> Ok can you now turn your attention to reviewing the code written by your fellow agents and checking for any issues, bugs, errors, problems, inefficiencies, security problems, reliability issues, etc. and carefully diagnose their underlying root causes using first-principle analysis and then fix or revise them if necessary? Don't restrict yourself to the latest commits, cast a wider net and go super deep!

## Process per round

1. Run the prompt verbatim against all applied changes (read `<SIBLING>/audit/applied_changes.jsonl` for the file list; expand to related files via imports/callers).
2. Find issues. Categorize: **trivial** (typo, whitespace, comment polish — does NOT count) or **substantive** (rephrasing, logic fix, contract fix — DOES count).
3. Fix the substantive issues with manual edits (per AGENTS.md, no script-driven transforms).
4. Commit each fix as a new commit on the feature branch with message: `fresh-eyes-round-<N>: <short fix description>`.
5. Append to `<SIBLING>/audit/phase7_fresh_eyes_log.md`:

```markdown
## Round <N>

**Prompt.** <verbatim prompt name>

**Findings.** <count> total; <trivial> trivial; <substantive> substantive.

**Substantive fixes.**
- <commit_sha>: <description>
- ...

**Verdict.** <CLEAN | NOT_CLEAN>
```

A round is **clean** if all findings were trivial. NOT_CLEAN if any substantive fix was applied.

**Definition of "trivial" (verbatim — don't soften).** A change qualifies as TRIVIAL if and only if ALL of these hold:

1. **Pure typo / whitespace.** Fixes a misspelled word, a missing comma in a comment, trailing whitespace, indentation that's off by spaces (not by levels). NO words added, removed, or replaced.
2. **Comment-only.** The change touches a comment, docstring, or markdown line — never executable code. Replacing `// TODO: implement` with `// TODO: implement (see issue 42)` is trivial; replacing `// TODO: implement` with `// implemented in commit abc1234` is NOT trivial because the *meaning* changed.
3. **No semantic shift in prose.** Rephrasing `// returns true on success` to `// returns true if successful` is NOT trivial — it's a rewording. Reformatting `//returns true` (no space) to `// returns true` (with space) IS trivial.
4. **Zero behavior delta.** The change produces a byte-identical compiled binary AND byte-identical test output. If you can't assert that locally, treat it as NOT_TRIVIAL by default.
5. **No new files.** Renaming, deleting, or creating a file is never trivial.

**What is NOT trivial (always count as substantive):**
- Renaming any identifier, even a comment label
- Reordering arguments, sections, or list items
- Adding/removing/changing test assertions
- Any code-comment edit longer than ~5 words (likely encoding new intent)
- Any fix the previous round of fresh-eyes already fixed differently (oscillation = NOT_CLEAN)

If a finding is borderline, **err NOT_CLEAN**. The cost of one extra round is low; the cost of a false-CLEAN that masks a real bug is high.

## Termination condition

Stop when **two consecutive rounds are CLEAN**. Either:
- R1, R2, R3 all CLEAN (the ideal — three rounds done in one pass).
- R1 NOT_CLEAN, R2 CLEAN, R3 CLEAN (more typical — R1 catches the most).
- R1 NOT_CLEAN, R2 NOT_CLEAN, R3 CLEAN, R4 CLEAN (worst case before bail).

If after 5 rounds you still have NOT_CLEAN findings, the rec set is genuinely flawed; escalate to the main agent.

**Beyond Round 3 — which prompt to re-run?** When R1, R2, R3 didn't all converge to CLEAN and you continue into R4+, **cycle through the three calibrated prompts in order**: R4 = Round 1 prompt verbatim, R5 = Round 2 prompt verbatim, R6 = Round 3 prompt verbatim, and so on. Don't paraphrase or invent a fourth prompt — the three prompts are calibrated to find different bug classes (R1 = diff-focused, R2 = trace-execution-flow, R3 = peer-code-audit), and cycling preserves that coverage. Track "two consecutive CLEAN" across the cycled prompts.

## After termination

1. Run `ubs $(git diff --name-only main..HEAD)` if available; fix anything reported.
2. Run the project's test suite, linters, typecheck. Fix anything broken.
3. Run all `<SIBLING>/audit/regression_tests/*.test.{sh,rs,py,ts}` against the post-apply binary; verify they're all green.

## Discipline

- **Verbatim prompts.** Don't paraphrase. They're calibrated.
- **Trivial vs substantive.** Be honest. Rephrasing IS substantive. Refactoring IS substantive. Only typo / whitespace / comment polish is trivial.
- **AGENTS.md compliance.** No deletions. No destructive ops. No `_v2` files.
- **No `--no-verify`.** If a hook fails, fix the issue, then commit again.

## Common mistakes

- Calling a refactor "trivial" to terminate the loop early.
- Reading the rec list and only checking what the recs claimed they did.
- Skipping the multi-round structure — Round 2's "trace through callers" finds different bugs than Round 1's "read the diff."
- Bypassing failed pre-commit hooks.

## Output to main agent

Print to stdout: per-round summary; after termination: `phase 7 complete: <K> rounds; <N> substantive fixes across <M> commits; tests/lint/typecheck green; regression_tests green`.

Exit when termination condition met.
