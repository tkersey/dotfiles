# Self-Test — trigger phrases & validation

> Use these to verify the skill triggers when expected and produces correct artifacts.

## Trigger phrases (must activate this skill)

The description's "Use when" clause should match all of these:

- "simplify this code"
- "reduce duplication in src/"
- "DRY this up"
- "remove duplicate code"
- "extract a helper from these functions"
- "reuse this component instead of duplicating"
- "create better abstractions"
- "remove lines / reduce LOC"
- "collapse these three functions into one"
- "unify these data types"
- "this file is too long, can we shorten it"
- "make these two implementations share more logic"
- "de-boilerplate this module"
- "I want fewer lines of code"

## Trigger phrases (should NOT activate)

- "this is slow / optimize this" → profiling-software-performance + extreme-software-optimization
- "find bugs in this code" → multi-pass-bug-hunting / ubs
- "review this PR" → managing-gh-issues-and-prs-with-ru / review
- "rewrite this in Rust" → porting-to-rust
- "find unused code / mocks" → mock-code-finder (then this skill if dedup follows)
- "explain this codebase" → codebase-archaeology

## Smoke test on a real project

Pick a small project with known duplication. Run:

```
Apply simplify-and-refactor-code-isomorphically to <PATH>.
```

Verify the skill:
1. Refuses to start without a clean baseline (tests + goldens + LOC).
2. Produces `refactor/artifacts/<run-id>/duplication_map.md` before scoring.
3. Scores candidates and rejects any with Score < 2.0 (does not silently accept all).
4. Produces an isomorphism card per accepted candidate **before** editing.
5. Uses Edit (never Write) for changes.
6. Asks before deleting a file (per AGENTS.md).
7. Refuses to script-edit (no sed / no codemod).
8. Verifies tests pass count equals baseline (not just "all green").
9. Refuses to re-baseline goldens silently.
10. Appends to LEDGER.md per accepted candidate.

## Validation script

```bash
~/.claude/skills/sw/scripts/validate-skill.py /data/projects/je_private_skills_repo/.claude/skills/simplify-and-refactor-code-isomorphically/
```

Expected: zero errors, possible warnings about line count (intentional — this skill teaches a methodology).

## Skill contract validation

```bash
cd /data/projects/je_private_skills_repo/.claude/skills/simplify-and-refactor-code-isomorphically
./scripts/extract_kernel.sh >/tmp/refactor-kernel.md
./scripts/validate_operators.py
./scripts/validate_corpus.py
./scripts/validate_skill_contract.py
```

Expected:
- Kernel extraction prints a block starting with `<!-- KERNEL-START -->`.
- Operator validation passes every operator card.
- Corpus validation passes every A-/S-/K- quote entry.
- Skill contract validation prints `PASS`.

## Frontmatter sanity

```bash
head -8 SKILL.md
```

Must:
- Start with `---` (no preceding blank line)
- Have `name: simplify-and-refactor-code-isomorphically`
- Have `description: >-` followed by indented continuation
- Description in third person, includes "Use when" with multiple triggers
- Description under 200 chars (front-loaded triggers)

## Reference depth check

```bash
# All references must be ONE LEVEL DEEP from SKILL.md
grep -E '\(references/.*/.*\.md\)' SKILL.md  # should be empty (no nested refs)
grep -E '\.\./.*\.md' references/*.md        # cross-skill refs are fine
```

## Script executability

```bash
ls -la scripts/
# Each script must be `chmod +x` and start with `#!/usr/bin/env bash` or `#!/usr/bin/env python3`
for s in scripts/*; do head -1 "$s"; done
```

Every shell script must pass `bash -n`; every Python script must pass
`python3 -m py_compile`.

## Anti-pattern check on SKILL.md itself

```bash
# Must not contain emojis (other than operator symbols which are part of the operator algebra)
# Must not say "I can help"
grep -E "I can help|I'll help|Let me" SKILL.md  # should be empty
```

## Model-specific validation scenarios

These exercise the skill under different model capabilities. Run each as a
fresh session on a representative project.

### Haiku test (weakest model, 50-line reality)

Haiku-class models often read only the first ~50 lines before deciding what
to do. The skill must pass this constraint:

1. Give Haiku the prompt: *"Apply the simplify-and-refactor-code-isomorphically
   skill to this project."*
2. Expect Haiku to, based ONLY on SKILL.md's first 50 lines, correctly:
   - State The One Rule.
   - State the 8-phase loop.
   - Name at least 3 pre-flight checklist items.
   - Point at `references/QUICK-REFERENCE.md` as the dense card.
3. Failure mode: Haiku proposes an edit before reading baseline. That means
   the first 50 lines of SKILL.md don't impose the loop strongly enough.

### Opus test (full-depth)

1. Prompt: *"Run a full refactor pass on `<path>`. Produce every artifact."*
2. Expect Opus to produce, in order:
   - baseline.md, tests_before.txt, duplication_map.md, slop_scan.md
   - One isomorphism card per accepted candidate under `cards/`
   - One commit per lever
   - ledger.md with one row per shipped candidate
   - rejection_log.md with reasons for each rejected candidate
   - CLOSEOUT.md at the end
3. Failure mode: Opus collapses candidates without a card, or mixes levers
   in one commit. Either is a SKILL.md authority failure.

### Trigger phrase test

For each trigger phrase in the list above, simulate a fresh session and
verify the skill activates. For each negative-trigger phrase, verify the
skill does NOT activate and a sibling is preferred.

### Sibling-missing fallback test

Set up a disposable harness with zero siblings installed. Do not alter or
delete the user's real `~/.claude/skills` directory.

```bash
export CLAUDE_CONFIG_DIR="$(mktemp -d)/claude"
mkdir -p "$CLAUDE_CONFIG_DIR/skills"
```

1. Trigger this skill.
2. Expect: skill detects missing siblings in Phase 0, offers `jsm install`
   or falls back gracefully. Never errors out.
3. Expect: skill produces all its required artifacts even with siblings
   missing (inline fallbacks work).
4. Failure mode: skill blocks entirely or silently omits an artifact.

### Rescue-mission test

Set up a project with:
- Failing tests on main (simulate with `exit 1` in one test).
- No golden outputs captured.
- No warning ceiling recorded.

1. Trigger the skill with: *"rescue this codebase — it's a mess."*
2. Expect: skill enters RESCUE mode via `rescue_phase_check.sh`, NOT the
   main loop. All rescue checkboxes must pass before the refactor loop
   is allowed to start.
3. Expect: skill refuses to collapse anything until tests are green or
   quarantined.
4. Failure mode: skill tries to collapse duplication on top of a red
   baseline. That produces an undebuggable PR.

### Vibe-coded-artifact test

Stage a project with `_v2` files, orphan duplicates, and unpinned deps.

1. Trigger the skill.
2. Expect: `ai_slop_detector.sh` flags P3 (orphans), `unpinned_deps.sh`
   flags P37. Both appear in the pathology scan before any collapse is
   proposed.
3. Expect: skill does NOT delete the `_v2` files — it stages them to
   `_to_delete/` per AGENTS.md Rule #1.

### UBS-before-commit test

1. Trigger the skill on a project where an AI has sprinkled `.unwrap()`
   through the code.
2. Collapse a candidate that happens to remove one or two `.unwrap()` calls.
3. Expect: UBS is invoked on the diff BEFORE commit; the unwrap removal
   is documented explicitly or a new bead is filed if it's out of scope.
4. Failure mode: the skill silently "cleans up" unwraps during an unrelated
   collapse. That's a drive-by fix and violates one-lever-per-commit.

## Expected failure reports

When the skill reports a failure, it MUST produce:

- A one-line verdict (`pass` / `fail` / `block`).
- A cited line (file:line) showing what triggered the failure.
- A pointer to the reference section with the relevant policy.
- No emoji, no hedging, no "I'll try to …".

Use [ubs](../ubs/SKILL.md) to inspect any test report that looks too clean.
