# Quick Reference — one-screen dense card

> Print this. Tape it above your monitor. When a pass stalls, read top-to-bottom.
> Full depth lives in [METHODOLOGY.md](METHODOLOGY.md) and siblings.

## Contents

1. [The One Rule](#the-one-rule)
2. [Loop](#loop)
3. [Score formula](#score-formula)
4. [Clone taxonomy](#clone-taxonomy-i-ii-iii-iv-v)
5. [Abstraction Ladder](#abstraction-ladder)
6. [Collapse levers](#collapse-levers)
7. [Pre-commit gates](#pre-commit-gates)
8. [Anti-pattern tripwires](#anti-pattern-tripwires)
9. [Command crib-sheet](#command-crib-sheet)

---

## The One Rule

**Preserve observable behavior. Prove it. One lever per commit.**

If you can't articulate what's observable, do not edit.
If you can't prove it's preserved, do not commit.
If you combine levers, split the PR.

## Loop

```
Phase 0  bootstrap (session_setup.sh)
Phase A  baseline   — tests + goldens + LOC + warnings
Phase B  map        — dup_scan, slop_detector, callsite census
Phase C  score      — score_candidates.py (threshold ≥ 2.0)
Phase D  prove      — isomorphism card per candidate
Phase E  collapse   — Edit only, one lever per commit
Phase F  verify     — verify_isomorphism.sh
Phase G  ledger     — ledger_row.sh, update dashboard
→ back to B (next candidate) or exit
```

## Score formula

```
Score = (LOC_saved × Confidence) / Risk
         where  Confidence ∈ (0, 1]        (how sure sites are truly iso)
                Risk      ∈ [1, 10]        (blast radius × reversibility cost)

Accept if Score ≥ 2.0.  Below that, log in rejection_log.md.
```

## Clone taxonomy (I, II, III, IV, V)

| Type | Name              | Collapse | Collapse method |
|:----:|-------------------|:--------:|-----------------|
|  I   | Exact copy        | ✅ yes   | extract fn / move to shared module |
|  II  | Parametric        | ✅ yes   | extract fn w/ params |
|  III | Gapped (minor logic drift) | maybe | normalize to longest body, diff, collapse only if drift was unintentional |
|  IV  | Semantic (different code, same behavior) | maybe | dispatch table / strategy — if 3+ sites |
|  V   | Accidental rhyme  | ❌ NO   | LEAVE SEPARATE — collapsing breaks contracts |

## Abstraction Ladder

```
0  copy-paste            (≤ 2 sites, cheap to keep)
1  literal duplication   (3+ sites, Rule of 3 — time to collapse)
2  extract function      (DRY with parameters)
3  strategy table        (enum/discriminator-driven dispatch)
4  policy object         (injected behavior per caller)
5  generic framework     (type-class / trait / generic fn)
6  DSL / macro / codegen (yield only if ≥ 3 frameworks)
```

Never climb higher than needed. The right answer is usually **rung 2 or 3**.

## Collapse levers

Pick one per commit:

- **L-EXTRACT** — pull duplicated body into a helper
- **L-PARAMETERIZE** — fold a diff axis into a parameter
- **L-DISPATCH** — replace if/switch-on-type with a table
- **L-ELIMINATE** — remove a wrapper that adds no observable value
- **L-TYPE-SHRINK** — replace broader type with narrowest that fits (see [TYPE-SHRINKS.md](TYPE-SHRINKS.md))
- **L-DELETE-DEAD** — remove provably-unreachable code (gauntlet — [DEAD-CODE-SAFETY.md](DEAD-CODE-SAFETY.md))
- **L-MERGE-FILES** — combine `_v2` / `_new` orphans back to canonical
- **L-PIN-DEP** — pin an unpinned dependency (P37)

## Pre-commit gates

Every commit in this skill must pass all of these:

- [ ] `baseline → after` test suite equal (pass count & exact failures)
- [ ] Goldens byte-identical OR change is proven intentional
- [ ] Warning / error count ≤ ceiling (see `lint_ceiling.sh`)
- [ ] No new `any`, `unwrap`, `ignore`, bare `except:` in the diff
- [ ] No `_v2` / `_new` / `tmp_` in added filenames
- [ ] No deleted files (unless explicit user approval — AGENTS.md Rule #1)
- [ ] One lever (i.e. one conceptual change)
- [ ] UBS (Ultimate Bug Scanner) clean on the diff

## Anti-pattern tripwires

If you catch yourself doing any of these — **stop**, back out, and reconsider:

- Adding a feature flag to "safely migrate" a refactor → you're building two-pathway debt
- Renaming something "just because" → not a refactor, not a lever
- Bundling "small drive-by fixes" into the commit → split them
- Deleting tests that "don't apply anymore" → the contract changed; document why
- Using `sed`, `jq -i`, or any codemod — all edits go through `Edit` or a subagent
- Collapsing two sites before you've read BOTH fully → almost always creates clone-type-V

## Command crib-sheet

```bash
# Session kickoff
./scripts/session_setup.sh <run-id> src

# Score a candidate list (reads duplication_map.md)
./scripts/score_candidates.py refactor/artifacts/<run-id>/duplication_map.md

# Per-candidate card
./scripts/isomorphism_card.sh ISO-014 <run-id>

# Prove dead code is really dead (the 12-step gauntlet)
./scripts/dead_code_safety_check.sh <path/to/function>

# Verify a commit preserves behavior
./scripts/verify_isomorphism.sh <run-id>

# Snapshot / enforce warning ceiling
./scripts/lint_ceiling.sh snapshot
./scripts/lint_ceiling.sh check

# Rescue-mission gate (when project is in crisis)
./scripts/rescue_phase_check.sh <run-id>

# Multi-agent swarm (when candidate list is deep)
./scripts/multi_agent_swarm.sh <run-id>
```

## When to refuse

Refuse to collapse if any of these are true:

- Tests are red or flaky on baseline (fix first)
- No golden outputs for code with observable I/O
- Sites are in different security zones (auth-bearing vs non-)
- Sites are in different perf tiers (hot-path vs cold-path — see [PERF-AWARE-REFACTOR.md](PERF-AWARE-REFACTOR.md))
- You cannot name the exact observable contract

See [SELECTION.md](SELECTION.md) for "is this skill even the right tool?"
