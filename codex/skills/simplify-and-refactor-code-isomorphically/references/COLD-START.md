# Cold start — applying this skill to a project with no baseline

> Most projects that need this skill most are the ones least ready for it:
> no tests, no goldens, no warning ceiling, maybe no AGENTS.md. You cannot
> collapse on an empty baseline. This file is the pre-pass that *creates*
> the baseline without shipping any refactor.

## Contents

1. [The cold-start paradox](#the-cold-start-paradox)
2. [Order of operations](#order-of-operations)
3. [Step 1 — add a smoke test](#step-1--add-a-smoke-test)
4. [Step 2 — capture first goldens](#step-2--capture-first-goldens)
5. [Step 3 — snapshot the warning ceiling](#step-3--snapshot-the-warning-ceiling)
6. [Step 4 — create AGENTS.md](#step-4--create-agentsmd)
7. [Step 5 — initial duplication map (read-only)](#step-5--initial-duplication-map-read-only)
8. [What NOT to do during cold start](#what-not-to-do-during-cold-start)
9. [Exit criterion: when is cold-start done?](#exit-criterion-when-is-cold-start-done)

---

## The cold-start paradox

The One Rule says: *Prove behavior identical, then remove lines.* To prove
identity you need a baseline. If there's no baseline, you can't prove
anything — so you can't collapse.

A common failure mode: agents try to skip cold-start and "just do the
refactor." Without a baseline, every post-refactor test is either green
because the code works or because the test doesn't cover the change — you
can't tell which. The refactor becomes a hope rather than a proof.

Cold-start solves this: **spend one pass building the baseline. Ship no
refactor that pass.** The deliverable is the baseline itself.

## Order of operations

```
1. Smoke test   — at least one test that exercises the main path
2. Goldens      — capture observable outputs for a small input set
3. Ceiling      — snapshot warning/error count (even if huge)
4. AGENTS.md    — write the no-deletion rule explicitly
5. Map          — duplication_map.md, but read-only; don't score this pass
```

Only after all 5 steps is the project ready for a normal Phase A / Phase B
pass.

## Step 1 — add a smoke test

You do not need full coverage; you need enough that a refactor that
silently breaks the program will fail the test.

**For a CLI:** smoke-test runs the binary with one representative input
and asserts a non-zero exit or an expected stdout substring.

**For a library:** smoke-test imports the top-level function and calls
it with one realistic input.

**For an API service:** smoke-test starts the server, hits `/healthz` and
one endpoint, asserts 200.

**For a data pipeline:** smoke-test runs a known input through and
asserts the output file exists and has the right row count.

This takes ~15-30 min. Commit:
`test(smoke): add cold-start smoke test`. No skill artifacts yet.

## Step 2 — capture first goldens

Pick 3-5 representative inputs; do not try to be exhaustive. Capture their
outputs. Sanitize (remove timestamps, random IDs, wall-clock durations).
Commit:
`test(goldens): capture initial golden outputs`.

This takes ~20-30 min. If the outputs aren't deterministic, see
[TESTING.md § Layer 3](TESTING.md) — drop to property tests for that
surface.

## Step 3 — snapshot the warning ceiling

```bash
./scripts/lint_ceiling.sh snapshot refactor/artifacts/warning_ceiling.txt
```

The ceiling starts wherever the project currently is. Don't try to
reduce it in cold-start; ceilings only decrease, never increase. This
is the *high-water mark* baseline. Commit the `warning_ceiling.txt`.

## Step 4 — create AGENTS.md

If the project has no AGENTS.md, create a minimal one:

```markdown
# AGENTS.md

## Rule #1
No file deletion without explicit user approval in the PR description.
Stage deletions to `_to_delete/<date>/` first; request approval to
proceed to hard-delete in a follow-up PR.

## Rule #2
Refactors must follow the protocol in
[.claude/skills/simplify-and-refactor-code-isomorphically/SKILL.md](.claude/skills/simplify-and-refactor-code-isomorphically/SKILL.md).
One lever per commit. Isomorphism card for every non-trivial collapse.

## Rule #3
No silent re-baselining of goldens. A golden change is a behavioral
change and requires explicit justification.

## Rule #4
No `sed -i`/codemod/regex-rewriting-at-scale. Edits go through the Edit
tool or parallel subagents with narrow scope.
```

Commit: `docs(agents): add AGENTS.md with deletion/refactor policies`.

## Step 5 — initial duplication map (read-only)

Run the scanner, capture the output, but do NOT score or act on it:

```bash
./scripts/session_setup.sh cold-start-$(date +%Y-%m-%d) src
```

Review `duplication_map.md` and annotate candidates you plan to address in
the first real pass. Commit the artifacts.

## What NOT to do during cold start

- **Do NOT collapse anything.** Not even an "obvious" duplicate. You have
  no proof your smoke test covers it.
- **Do NOT delete anything.** Not even obvious dead code. Run the gauntlet
  in a later pass.
- **Do NOT "just clean up while you're in there."** That's a drive-by and
  blocks your ability to audit the cold-start output cleanly.
- **Do NOT try to get the warning count to zero.** The ceiling is a
  snapshot, not a goal, this pass.
- **Do NOT add comprehensive tests.** One smoke test is enough. Full
  coverage is a different project.
- **Do NOT rewrite any file.** Any file rewrite in cold-start makes the
  goldens meaningless.

## Exit criterion: when is cold-start done?

- [ ] `test(smoke)` commit exists and CI green
- [ ] `test(goldens)` commit exists with ≥ 3 golden inputs
- [ ] `refactor/artifacts/warning_ceiling.txt` exists in the repo
- [ ] `AGENTS.md` exists in the repo root
- [ ] `refactor/artifacts/cold-start-<date>/duplication_map.md` exists
- [ ] No code change has shipped beyond tests + baseline artifacts

If all ticked: cold-start is complete. Start the first real refactor
pass per [METHODOLOGY.md](METHODOLOGY.md). That pass should produce
small, confident collapses precisely because the baseline is thin —
aim for 3-5 candidates max in the first real pass, not 15.

See [RESCUE-MISSIONS.md](RESCUE-MISSIONS.md) if the project is not just
cold-starting but actively broken (red tests, drowned warnings). Rescue
is a superset of cold-start; if tests are red, do rescue first.

Cross-references: [EXIT-CRITERIA.md](EXIT-CRITERIA.md) for phase time-boxes,
[TEAM-ADOPTION.md](TEAM-ADOPTION.md) for introducing this discipline to a
team that's never done it.
