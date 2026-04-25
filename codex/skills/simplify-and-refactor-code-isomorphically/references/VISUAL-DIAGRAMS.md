# Visual diagrams — ASCII flowcharts of the skill's core shapes

> Sometimes a picture beats 500 words. These diagrams are ASCII so they
> render in any terminal, grep cleanly, and survive copy-paste.

## Contents

1. [The Loop — phases 0 through 8](#the-loop--phases-0-through-8)
2. [Score matrix quadrants](#score-matrix-quadrants)
3. [Clone-type decision tree](#clone-type-decision-tree)
4. [Isomorphism-card lifecycle](#isomorphism-card-lifecycle)
5. [Rescue → main-loop switch](#rescue--main-loop-switch)
6. [Artifact relationships](#artifact-relationships)
7. [Defense-in-depth layers](#defense-in-depth-layers)

---

## The Loop — phases 0 through 8

```
   ┌───────────────────────────────────────────────────────┐
   │                    PHASE 0                            │
   │  BOOTSTRAP: check siblings, jsm install, inventory    │
   └────────────────────────┬──────────────────────────────┘
                            │
                            ▼
   ┌───────────────────────────────────────────────────────┐
   │                    PHASE A                            │
   │  BASELINE: tests + goldens + LOC + warnings           │
   └────────────────────────┬──────────────────────────────┘
                            │
                            ▼
   ┌───────────────────────────────────────────────────────┐
   │                    PHASE B                            │
   │  MAP: dup_scan + slop_detector + callsite census      │
   └────────────────────────┬──────────────────────────────┘
                            │
                            ▼
   ┌───────────────────────────────────────────────────────┐
   │                    PHASE C                            │
   │  SCORE: opportunity matrix, threshold ≥ 2.0           │
   └────────────────────────┬──────────────────────────────┘
                            │
                            ▼
   ┌───────────────────────────────────────────────────────┐
   │                    PHASE D                            │
   │  PROVE: isomorphism card per candidate BEFORE edit    │
   └────────────────────────┬──────────────────────────────┘
                            │
                            ▼
   ┌───────────────────────────────────────────────────────┐
   │                    PHASE E                            │
   │  COLLAPSE: Edit tool only, one lever per commit       │
   └────────────────────────┬──────────────────────────────┘
                            │
                            ▼
   ┌───────────────────────────────────────────────────────┐
   │                    PHASE F                            │
   │  VERIFY: tests + goldens + ceiling + LOC delta        │
   └───────────┬───────────────────────────────┬───────────┘
               │                               │
           fail│                           pass│
               ▼                               ▼
   ┌────────────────────┐   ┌───────────────────────────────┐
   │  REVERT.           │   │              PHASE G          │
   │  Re-audit card.    │   │  LEDGER: append row; close    │
   │  Update rejection_ │   │  bead; update dashboard       │
   │  log if pattern    │   └───────────────┬───────────────┘
   │  is permanent.     │                   │
   └────────────────────┘                   ▼
                              ┌───────────────────────────┐
                              │         PHASE 8           │
                              │  REPEAT or CLOSE pass     │
                              │  (new candidates surface  │
                              │  once noise clears)       │
                              └───────────────────────────┘
```

## Score matrix quadrants

```
                       LOC saved × Confidence →
                       low                     high
                 ┌────────────────┬─────────────────┐
                 │                │                 │
          low    │   SKIP (low    │   ACCEPT        │
          risk   │   payoff)      │   (high yield,  │
            ▲    │                │    low risk)    │
            │    ├────────────────┼─────────────────┤
          Risk   │                │                 │
            │    │   REJECT       │   ESCALATE      │
          high   │   (not worth   │   (big yield    │
                 │    the risk)   │    but high     │
                 │                │    risk — ask   │
                 │                │    user)        │
                 └────────────────┴─────────────────┘

  Threshold: score = (LOC_saved × Confidence) / Risk ≥ 2.0 to ACCEPT.
  The quadrants are heuristic; the threshold is the gate.
```

## Clone-type decision tree

```
                       [ two+ pieces of similar code ]
                                      │
                                      ▼
                        ┌──────────────────────────┐
                        │ byte-identical?          │
                        └──────────────────────────┘
                              │              │
                             yes             no
                              │              │
                              ▼              ▼
                         ╔════════╗  ┌──────────────────────────┐
                         ║ TYPE I ║  │ same structure, differ   │
                         ║ exact  ║  │ only in literals/names?  │
                         ║        ║  └──────────────────────────┘
                         ║Collapse║        │              │
                         ║  YES   ║       yes             no
                         ╚════════╝        │              │
                                           ▼              ▼
                                      ╔═════════╗  ┌───────────────────────┐
                                      ║ TYPE II ║  │ identical structure   │
                                      ║parametric║  │ but some sites have   │
                                      ║         ║  │ added/removed stmts?  │
                                      ║ Collapse║  └───────────────────────┘
                                      ║   YES   ║        │          │
                                      ╚═════════╝       yes         no
                                                         │          │
                                                         ▼          ▼
                                                ╔═════════════╗ ┌───────────────────────┐
                                                ║ TYPE III    ║ │ different code, same  │
                                                ║ gapped      ║ │ observable behavior?  │
                                                ║             ║ └───────────────────────┘
                                                ║ Collapse IF ║       │          │
                                                ║ gaps are    ║      yes         no
                                                ║ unintentnl. ║       │          │
                                                ║ Else: leave ║       ▼          ▼
                                                ║ side effects║  ╔════════════╗  ╔═══════════╗
                                                ║ OUTSIDE.    ║  ║ TYPE IV    ║  ║ TYPE V    ║
                                                ╚═════════════╝  ║ semantic   ║  ║accidental ║
                                                                 ║            ║  ║ rhyme     ║
                                                                 ║ Collapse   ║  ║           ║
                                                                 ║ IF 3+ sites║  ║ DO NOT    ║
                                                                 ║ via table. ║  ║ COLLAPSE. ║
                                                                 ╚════════════╝  ╚═══════════╝
```

## Isomorphism-card lifecycle

```
 [ scanner flags ]
        │
        ▼
 [ candidate in duplication_map.md ]
        │
        ▼
 [ score ≥ 2.0 ? ] ── no ── > [ rejection_log.md (forever) ]
        │
       yes
        │
        ▼
 [ stub card via isomorphism_card.sh ]
        │
        ▼
 [ fill card: sites, contract, hidden diffs, proof, risk ]
        │
        ▼
 [ audit via isomorphism-auditor subagent ]
        │
        ▼
 [ audit verdict ]
    │        │         │
 READY   NEEDS     REJECT
    │    REVISION     │
    │       │         ▼
    │       ▼    [ rejection_log ]
    │    [ revise ]
    │       │
    │       ▼
    │  [ re-audit ]
    │       │
    ▼       │
 [ edit + commit (Phase E) ]
    │
    ▼
 [ verify (Phase F) ]
    │      │
   pass   fail
    │      │
    │      ▼
    │   [ revert ]
    │   [ add REVERT ADDENDUM to card ]
    │   [ rejection_log (permanent) ]
    │
    ▼
 [ ledger row (Phase G) ]
    │
    ▼
 [ card archived as evidence in CASE-STUDIES.md ]
```

## Rescue → main-loop switch

```
 ┌──────────────────────────────────────────────────┐
 │ ./scripts/rescue_phase_check.sh                  │
 │                                                  │
 │ Gates (all must be green):                       │
 │   ◻ Tests pass on main                           │
 │   ◻ Build passes clean                           │
 │   ◻ Golden-path test exists                      │
 │   ◻ Warning ceiling captured                     │
 │   ◻ any/unwrap counts snapshotted                │
 │   ◻ Recent clean CI run                          │
 └──────────────────┬───────────────────────────────┘
                    │
            any ❌ │
                    │                ┌────────────────┐
                    ▼                │                │
          ┌──────────────┐           │   all ✅ →     │
          │ RESCUE MODE  │           │   ENTER MAIN   │
          │              │           │   LOOP         │
          │ triage per   │           │                │
          │ RESCUE-      │◄──────────┤ session_setup  │
          │ MISSIONS.md  │           │ runs, Phase A  │
          │              │           │ starts         │
          │ loop until   │           │                │
          │ all gates    │           └────────────────┘
          │ green        │
          └──────────────┘
```

## Artifact relationships

```
 refactor/artifacts/<run-id>/
 │
 ├── baseline.md ───────────┐
 ├── tests_before.txt ──────┤
 ├── goldens/ ──────────────┤
 ├── warning_ceiling.txt ◄──┘ (these define "what we'll measure against")
 │
 ├── duplication_map.md ──┐
 ├── slop_scan.md ────────┤
 ├── unpinned_deps.md ────┘ (phase B — read-only inputs to scoring)
 │
 ├── cards/ISO-*.md ◄─── (phase D — one per accepted candidate)
 │         │
 │         └──► referenced by commit messages
 │
 ├── ledger.md ◄──── (phase G — append-only, one row per candidate)
 ├── rejection_log.md ◄─ (forever-kept reasons for NOT collapsing)
 ├── dashboard.md ◄─── (summary for team view)
 └── CLOSEOUT.md ◄──── (end of pass summary + lessons)
```

## Defense-in-depth layers

```
 ┌──────────────────────────────────────────────────────┐
 │ Layer 1: AGENTS.md (policy)                          │
 │   Text-level discipline. Agents read and obey.       │
 ├──────────────────────────────────────────────────────┤
 │ Layer 2: cc-hooks (PreToolUse / PostToolUse / Stop)  │
 │   Runtime block before a tool executes.              │
 │   See HOOKS.md.                                      │
 ├──────────────────────────────────────────────────────┤
 │ Layer 3: git hooks (pre-commit / commit-msg / pre-   │
 │          push)                                       │
 │   Repo-boundary block. Catches humans and agents     │
 │   equally. See GIT-HOOKS.md.                         │
 ├──────────────────────────────────────────────────────┤
 │ Layer 4: CI/CD (GitHub Actions / GitLab / CircleCI)  │
 │   Clean-VM enforcer. Cannot be subverted. See        │
 │   CI-CD-INTEGRATION.md.                              │
 ├──────────────────────────────────────────────────────┤
 │ Layer 5: Reviewer (human)                            │
 │   The final contract-level audit. Catches what       │
 │   automation can't. See REVIEWER-QUICKSTART.md.      │
 ├──────────────────────────────────────────────────────┤
 │ Layer 6: Prod telemetry / rollback playbook          │
 │   If all else fails, limit blast radius + learn.     │
 │   See ROLLBACK-PLAYBOOK.md.                          │
 └──────────────────────────────────────────────────────┘
```

Each layer catches things the others miss. Don't rely on one.
