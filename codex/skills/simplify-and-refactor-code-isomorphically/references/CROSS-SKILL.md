# Cross-Skill Map — composing with other skills

> When this skill hands off (or hands back) work to another skill in this repo.

## Contents

1. [Composition diagram](#composition-diagram)
2. [Per-skill protocol](#per-skill-protocol)
3. [Coordination via beads + agent-mail](#coordination-via-beads--agent-mail)
4. [Handoff messages (copy-paste)](#handoff-messages-copy-paste)

---

## Composition diagram

```
                   ┌─────────────────────────────────────────────────────┐
                   │  WHAT YOU WANT TO ACCOMPLISH                        │
                   └─────────────────────────────────────────────────────┘

  "this is slow"            ──→  profiling-software-performance
                                       │
                                       ▼
                                 ranked hotspots
                                       │
                                       ▼
                                 extreme-software-optimization
                                       │ (preserves behavior at perf cost)
                                       ▼
                                 simplification still applies on top
                                       │
                                       ▼
                                 simplify-and-refactor-code-isomorphically  ← THIS SKILL

  "remove duplication"      ──→  simplify-and-refactor-code-isomorphically  ← THIS SKILL
                                       │
                                       ▼
                                 (after a pass) re-run multi-pass-bug-hunting
                                                or ubs to confirm no quiet bugs

  "merge two services"      ──→  Tier-3 architectural — write a plan doc first
                                       │
                                       ▼
                                 planning-workflow → multi-agent-swarm-workflow → THIS SKILL

  "find unused code"        ──→  mock-code-finder → THIS SKILL (if it surfaces dead code)

  "review the refactor"     ──→  code-review-gemini-swarm-with-ntm
                                       OR
                                 multi-model-triangulation
                                       OR
                                 ubs (per-file static analysis)

  "port to Rust"            ──→  porting-to-rust (spec-first; preserves invariants)
                                       │
                                       ▼
                                 THIS SKILL on the Rust target after port stabilizes
```

---

## Per-skill protocol

### profiling-software-performance / extreme-software-optimization

**Direction:** profiling → optimization → (this skill).

**Why:** all three skills demand isomorphism artifacts (golden outputs, baseline, ledger). Re-use them. The hotspot table from profiling tells the optimizer where to apply changes; once optimization is done and behavior is verified preserved, this skill runs on the surrounding scaffolding.

**Don't:** mix optimization and simplification in the same commit. They fight: optimization sometimes accepts more code (loop unroll, prefetch, manual vectorization) for speed; simplification gives up nothing for fewer lines.

**Shared artifacts:**
- `goldens/` (this skill, optimization, profiling all read it)
- `BUDGETS.md` (profiling) tells you which hot paths must stay fast post-refactor

### multi-pass-bug-hunting

**Direction:** (this skill) → multi-pass-bug-hunting; sometimes the reverse.

**Why:** a refactor that "passed verify" can still hide latent bugs that didn't have test coverage (the verify gates only check what was already tested). Run a bug-hunt pass after a major shrink to catch them.

Conversely, when a bug-hunt pass surfaces patterns of duplicated buggy code (the same `unwrap()` at 12 sites), reach for this skill to consolidate the fix.

### ubs (Ultimate Bug Scanner)

**Direction:** Always run `ubs <changed-files>` before commit (per AGENTS.md). Treat exit > 0 as a hard gate.

**This skill's verifier already includes** running ubs on changed files. If ubs flags a real issue, the simplification was actually a behavior change — roll back.

### codebase-archaeology

**Direction:** codebase-archaeology → (this skill).

**Why:** when entering an unfamiliar codebase, archaeology builds the mental model. Then this skill applies it.

**Don't:** start refactoring before archaeology. You'll merge things that look the same but encode different invariants you didn't see.

### mock-code-finder

**Direction:** mock-code-finder → (this skill).

**Why:** mocks, stubs, and TODO-marked code are often duplicated and partially-implemented. Mock-code-finder surfaces them; this skill consolidates and removes the dead branches (with permission).

### multi-model-triangulation

**Direction:** (this skill) → triangulation for review.

**Why:** the simplification PR's verifier passed your local checks. Before merging, get a second opinion from Codex/Gemini/Grok on whether the isomorphism cards are convincing. Often a different model spots a missed axis.

### code-review-gemini-swarm-with-ntm

**Direction:** (this skill) → swarm review.

**Why:** for Tier 2/3 changes, run multiple Gemini reviewers in parallel. Their per-file findings catch things a single reviewer misses (especially type-narrowing and React-reconciler subtleties).

### porting-to-rust

**Direction:** porting → (this skill).

**Why:** a fresh port often introduces accidental duplication (because the porter writes each file independently). Don't simplify mid-port — that conflates two unfreezable cycles. Wait until the port is stable, then run a simplification pass.

### planning-workflow

**Direction:** plan ↔ (this skill).

**Why:** for Tier 3 simplifications (collapse two services, replace ORM, monorepo consolidation), this skill says **stop and write a plan**. The plan doc is what planning-workflow produces; this skill consumes its scoped tasks back.

### beads-workflow / br

**Direction:** every accepted candidate ↔ a bead.

**Why:** each candidate is one or more atomic tasks. File a bead per candidate so progress is auditable and dependencies (`br dep add`) capture "D2 must finish before D4" relationships.

### agent-mail

**Direction:** for multi-agent passes (swarm of agents each handling a subdir), use agent-mail file reservations to prevent collision.

```
file_reservation_paths(project_key, agent_name, ["crates/mail/src/**"], ttl_seconds=3600, exclusive=true, reason="beads-D1")
```

---

## Coordination via beads + agent-mail

When running a multi-agent simplification swarm:

```bash
# 1. Score candidates and create one bead per accepted ID
br create --title "[refactor] collapse 3x send_* in messaging.rs" --type task --priority 2 --label refactor
br create --title "[refactor] unify <Button> variants" --type task --priority 2 --label refactor
# ... etc

# 2. Set dependencies (rule of thumb: low-risk first, dependencies block high-risk)
br dep add D4 D1   # D4 (csv/tsv parsers) waits for D1 (messaging refactor)

# 3. For each agent in the swarm:
br ready                       # claim a ready bead
br update <id> --status=in_progress
# reserve files via agent-mail
# do the work (run the loop)
br close <id> --reason "Completed; ledger entry: <ref>"
# release files
```

The beads database becomes the audit log; agent-mail provides the file-locking layer; the LEDGER.md aggregates everyone's work.

---

## Handoff messages (copy-paste)

### Hand off to extreme-software-optimization

```
[handoff: simplify → extreme-software-optimization]

Refactor pass <run-id> complete. Goldens at refactor/artifacts/<run>/goldens/checksums.txt;
LEDGER.md shows -X LOC across N candidates. Surface should now be cleaner for performance work.

If you re-baseline performance on the post-refactor commit, expect:
- p95 unchanged (refactor was isomorphic)
- bundle size <smaller / unchanged> (frontend only)
- compile time <smaller / unchanged> (smaller surface usually means faster compile)

Pick up with profiling-software-performance to identify hotspots, then ESO with the
existing golden artifacts.
```

### Hand off to multi-pass-bug-hunting

```
[handoff: simplify → multi-pass-bug-hunting]

Refactor pass <run-id> complete. The five gates passed locally, but verify only catches
what tests already cover. Latent bugs may exist in:
  - newly-exposed branches in unified types
  - error-handling paths after `?` collapses
  - React rerender behavior after component identity changes

Suggest a multi-pass-bug-hunt scoped to:
  refactor/artifacts/<run>/LEDGER.md  (the file list of changed surfaces)
```

### Hand off to user (end-of-pass)

```
Simplification pass <run-id> complete.

  Net Δ LOC:        -X (Y%)
  Candidates:       N accepted, M rejected (REJECTIONS.md cites why)
  Goldens:          all bit-identical
  Tests:            <pass/fail/skip> = baseline
  Type/lint:        no new warnings
  Time:             ~Zh

Reviewable artifacts under refactor/artifacts/<run-id>/:
  - LEDGER.md         per-candidate before/after with commits
  - REJECTIONS.md     candidates not pursued and why
  - cards/*.md        isomorphism cards per candidate

Recommended next step:
  - run code-review-gemini-swarm-with-ntm or multi-model-triangulation on the changed files
  - schedule a multi-pass-bug-hunting pass to catch latent issues
  - re-run after the next feature work to catch newly-surfaced clones
```
