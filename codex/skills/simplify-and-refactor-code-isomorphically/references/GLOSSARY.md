# Glossary — terms used across this skill

> The skill is a big surface area. Terms drift. This file is the single
> authoritative definition for every jargon term you'll see. When a reference
> file uses a term, it means what's here.

## Contents

1. [Core concepts](#core-concepts)
2. [Clone taxonomy](#clone-taxonomy)
3. [Abstraction ladder](#abstraction-ladder)
4. [Process vocabulary](#process-vocabulary)
5. [Artifacts](#artifacts)
6. [Levers](#levers)
7. [Scoring and risk](#scoring-and-risk)
8. [Sibling-skill names and acronyms](#sibling-skill-names-and-acronyms)
9. [Rule / pattern / pathology IDs](#rule--pattern--pathology-ids)
10. [Model and session terms](#model-and-session-terms)

---

## Core concepts

**Isomorphism.** Behavior preservation under transformation. Two pieces of
code are isomorphic if, for every input the caller might supply, they
produce the same observable output, side effects, error modes, and timing
guarantees. Structural differences are allowed; contract differences are not.
See [ISOMORPHISM.md](ISOMORPHISM.md).

**Observable contract.** The set of things a caller of a function/module can
observe: return value, exceptions thrown, side effects (I/O, mutations,
messages), ordering, timing, observability hooks (logs, metrics, traces).
Everything that is NOT in the contract is free to change in a refactor.

**The One Rule.** *Preserve observable behavior. Prove it. One lever per
commit.* If you can't articulate what's observable, don't edit. If you can't
prove it's preserved, don't commit. If you combine levers, split the PR.
See [SKILL.md](../SKILL.md).

**Candidate.** A cluster of sites proposed for collapse or a single target
for a type-shrink / dead-code removal. Identified by `ISO-<nnn>`.

**Site.** One call site / usage / definition of the thing a candidate wants
to collapse. Named as `path:line`.

**Collapse.** The act of reducing N sites to 1 (or 0) without changing the
observable contract.

**Pass.** A single refactor session that runs the full loop (phases 0-8).
Identified by a run-id like `2026-04-23-pass-1`.

## Clone taxonomy

See [DUPLICATION-TAXONOMY.md](DUPLICATION-TAXONOMY.md) for the full decision
tree. Short form:

- **Type I — Exact.** Byte-identical. Usually Rule-of-3 triggers a collapse.
- **Type II — Parametric.** Identical structure, differ only by literal
  values or names. Collapse with extract-fn + parameters.
- **Type III — Gapped.** Near-identical; differ by added/removed statements.
  Sometimes intentional — audit each gap before collapsing.
- **Type IV — Semantic.** Different code, same observable behavior. Collapse
  with a dispatch table or strategy pattern; only if 3+ sites.
- **Type V — Accidental rhyme.** Sites look alike but their contracts diverge
  (or will diverge). **Do not collapse.** Log in rejection_log.md.

## Abstraction ladder

From [ABSTRACTION-LADDER.md](ABSTRACTION-LADDER.md). Each "rung" is a level
of indirection you can climb to. Higher ≠ better; the right answer is
usually the lowest rung that accommodates the variation.

- **Rung 0** — copy-paste (≤ 2 sites, cheap to keep).
- **Rung 1** — literal duplication (3+ sites, Rule of 3 fires).
- **Rung 2** — extract function (DRY with parameters).
- **Rung 3** — strategy / dispatch table (enum or tag-driven).
- **Rung 4** — policy object (inject behavior per caller).
- **Rung 5** — generic framework (type-class / trait / generic fn).
- **Rung 6** — DSL / macro / codegen (rarely the right answer).

## Process vocabulary

**Pre-flight.** The non-negotiable checklist before any edit. See
[SKILL.md § Pre-Flight](../SKILL.md).

**Phase.** One of the 8 loop steps (0 bootstrap, A baseline, B map, C score,
D prove, E collapse, F verify, G ledger) plus phase 8 "repeat". See
[METHODOLOGY.md](METHODOLOGY.md).

**Baseline.** A recorded snapshot of test-pass count, golden outputs, LOC,
warning count at the start of a pass. Everything is measured against this.

**Map.** A duplication map — the list of candidate clusters. The artifact
is [`duplication_map.md`](ARTIFACTS.md).

**Prove.** The phase where you fill an [isomorphism card](ISOMORPHISM.md)
**before** editing. No card, no edit.

**Verify.** Running [`verify_isomorphism.sh`](../scripts/verify_isomorphism.sh)
after the edit; tests+goldens+warnings must not have regressed.

**Ledger.** Append-only record of accepted, reverted, and rejected
candidates. See [assets/ledger_header.md](../assets/ledger_header.md).

**Gauntlet.** The 12-step dead-code safety check. See
[DEAD-CODE-SAFETY.md](DEAD-CODE-SAFETY.md). Never delete without running it.

**Rescue mission.** A dedicated pre-pass when the project is in crisis
(red tests, drowned warnings, orphan sprawl). Precedes the main loop. See
[RESCUE-MISSIONS.md](RESCUE-MISSIONS.md).

**Continuous refactor.** Integrating the skill into the daily dev rhythm
via hooks + CI gates rather than one-off passes. See
[CONTINUOUS-REFACTOR.md](CONTINUOUS-REFACTOR.md).

## Artifacts

**Isomorphism card.** Per-candidate document that states identity, sites,
observable contract, hidden differences, proof strategy, risk, and commit
plan. Template: [assets/isomorphism_card.md](../assets/isomorphism_card.md).

**Duplication map.** Scored list of candidates. Template in
[ARTIFACTS.md](ARTIFACTS.md).

**Rejection log.** Forever-kept list of candidates deliberately NOT
collapsed, with reasons. Template:
[assets/rejection_log.md](../assets/rejection_log.md).

**Warning ceiling.** A single-line file (`warning_ceiling.txt`) tracking
the maximum allowed warning count. Enforced by
[`lint_ceiling.sh`](../scripts/lint_ceiling.sh). Per rule R-013, count may
only decrease, never increase.

**Callsite census.** For each candidate, the count and location of every
reference to the symbol(s) being collapsed. Built by
[`callsite_census.sh`](../scripts/callsite_census.sh).

**Goldens.** Byte-captured outputs from representative inputs. After a
collapse, goldens must diff clean. See [TESTING.md](TESTING.md).

**Run-id.** Session identifier, typically `YYYY-MM-DD-pass-N`. Artifacts
live at `refactor/artifacts/<run-id>/`.

## Levers

A **lever** is a single type of refactor action. One lever per commit.

- **L-EXTRACT** — pull duplicated body into a helper
- **L-PARAMETERIZE** — fold a diff axis into a parameter
- **L-DISPATCH** — replace if/switch-on-type with a table
- **L-ELIMINATE** — remove a wrapper that adds no observable value
- **L-TYPE-SHRINK** — replace broader type with narrowest that fits; see
  [TYPE-SHRINKS.md](TYPE-SHRINKS.md)
- **L-DELETE-DEAD** — remove provably-unreachable code (gauntlet required)
- **L-MERGE-FILES** — combine `_v2`/`_new` orphans back to canonical
- **L-PIN-DEP** — pin an unpinned dependency (pathology P37)

## Scoring and risk

**Score.** `(LOC_saved × Confidence) / Risk`. Accept if Score ≥ 2.0. Built
by [`score_candidates.py`](../scripts/score_candidates.py).

**Confidence.** `∈ (0, 1]`. How sure you are the sites are truly isomorphic.
Drop when sites live in different security zones, perf tiers, or have
diverging error modes.

**Risk.** `∈ [1, 10]`. Blast radius × reversibility cost. High risk: touches
`pub` API, crosses a network boundary, changes an error type.

**Blast radius.** The number of downstream consumers affected by a change.
A private function has blast radius 0; a `pub` trait method can have
radius 1000+.

**Reversibility.** Can `git revert HEAD` restore the system? If downstream
has cached generated types or schemas, reversibility is impaired.

**Rule of 3.** Don't collapse until a thing appears in 3+ sites. Two are
"coincidence"; three are "signal." Applies at rung 1 → rung 2.

## Sibling-skill names and acronyms

- **AGENTS.md** — project-level agent-contract file (deletion rules,
  workflow). Rule #1 of this skill's referenced AGENTS.md: *no file deletion
  without explicit user approval*.
- **cass** — Cross-Agent Session Search. Mine past sessions.
- **UBS** — Ultimate Bug Scanner. Run on every diff before commit.
- **jsm** — Jeffrey's Skills Manager. `jsm install <skill>` adds siblings.
- **NTM** — Node TMUX — multi-agent tmux orchestration.
- **br** — beads_rust. Local-first issue tracker.
- **bv** — beads view / graph-aware triage.
- **cc-hooks** — Claude Code hooks (PreToolUse / PostToolUse / Stop).
  Different from git hooks. See [HOOKS.md](HOOKS.md) and
  [GIT-HOOKS.md](GIT-HOOKS.md).
- **Agent Mail** — MCP server for multi-agent coordination and file locks.
- **dcg** — Destructive-Command Guard. Blocks `rm -rf`, `git reset --hard`,
  etc. pre-execution.

## Rule / pattern / pathology IDs

Scheme used throughout this skill:

- **R-###** — triangulated-kernel operational rule. 30 total. See
  [TRIANGULATED-KERNEL.md](TRIANGULATED-KERNEL.md).
- **M-###** — micropattern. 80 total across language guides. See
  [MICROPATTERNS.md](MICROPATTERNS.md) (M1–M40) and
  [ADVANCED-MICROPATTERNS.md](ADVANCED-MICROPATTERNS.md) (M41–M80).
- **P##** — vibe-coded pathology. 40 total. See
  [VIBE-CODED-PATHOLOGIES.md](VIBE-CODED-PATHOLOGIES.md).
- **HS#** — horror story from real session evidence. 5 total. See
  [REAL-SESSION-EVIDENCE.md](REAL-SESSION-EVIDENCE.md).
- **ISO-<nnn>** — per-pass candidate ID. Zero-padded within the pass.
- **RHY-<nnn>** — per-pass type-V rhyme rejection ID.

## Model and session terms

**50-line reality rule.** Weak-model agents (Haiku-class) often decide
skill relevance from the first ~50 lines of SKILL.md. The skill must
communicate triggers, the One Rule, and the loop in that window.

**Progressive disclosure.** SKILL.md links to references one level deep.
The agent loads detail only on demand.

**Fallback.** Every sibling-skill reference has an inline degradation path
so the skill works even when siblings aren't installed. See
[JSM-BOOTSTRAP.md](JSM-BOOTSTRAP.md).

**Pass closeout.** The end-of-pass artifact (`CLOSEOUT.md`) with shipped
count, revert count, rejection count, LOC delta, and surprises. Template
in [FORMULAS.md](FORMULAS.md).
