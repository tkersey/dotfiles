# Structure — folder layout reference

> Map of every file this skill owns and every artifact a pass produces.

## Contents

1. [Skill folder](#skill-folder)
2. [Project artifacts (what this skill writes)](#project-artifacts-what-this-skill-writes)
3. [Progressive-disclosure discipline](#progressive-disclosure-discipline)
4. [When to add a new reference file](#when-to-add-a-new-reference-file)

---

## Skill folder

```
simplify-and-refactor-code-isomorphically/
├── SKILL.md                       # entry point; progressive disclosure starts here
├── SELF-TEST.md                   # trigger-phrase and behavior tests
├── CHANGELOG.md                   # semver log of skill revisions
│
├── references/                    # all deeper docs — loaded on demand
│   ├── QUICK-REFERENCE.md         # one-screen dense card (tape above monitor)
│   ├── GLOSSARY.md                # every term defined once
│   ├── FAQ.md                     # 20+ agent-friction Q&As
│   ├── DECISION-TREES.md          # ASCII flowcharts for ambiguous calls
│   ├── VISUAL-DIAGRAMS.md         # ASCII loop, quadrants, defense-in-depth
│   ├── METHODOLOGY.md             # the loop, phase-by-phase playbook
│   ├── EXIT-CRITERIA.md           # precise "done" gates + time-boxes per phase
│   ├── BENCHMARKS.md              # what a good pass looks like (typical numbers)
│   ├── TECHNIQUES.md              # specific refactor techniques
│   ├── COOKBOOK.md                # complete worked examples per lever
│   ├── FORMULAS.md                # copy-paste templates for artifacts/prompts
│   ├── SELECTION.md               # when to use this skill vs. siblings
│   ├── TESTING.md                 # how to prove a refactor is isomorphic
│   ├── VALIDATION.md              # read-only self-validation gates
│   ├── REVIEWER-QUICKSTART.md     # 10-min audit of a skill-produced PR
│   ├── ROLLBACK-PLAYBOOK.md       # when a shipped collapse breaks prod
│   ├── COLD-START.md              # applying to a project with no baseline
│   ├── TEAM-ADOPTION.md           # L0 → L3 maturity ladder
│   ├── HOOKS.md                   # cc-hooks integration
│   ├── GIT-HOOKS.md               # native git pre-commit/pre-push
│   ├── CI-CD-INTEGRATION.md       # GitHub Actions / GitLab / CircleCI
│   ├── STRUCTURE.md               # this file
│   │
│   ├── DUPLICATION-TAXONOMY.md    # clone types I–V
│   ├── ABSTRACTION-LADDER.md      # rungs 0–6; when to climb
│   ├── ISOMORPHISM.md             # proof rubric
│   ├── ANTI-PATTERNS.md           # what NOT to do (core)
│   ├── ANTI-PATTERNS-2.md         # extended catalog
│   ├── OPERATOR-CARDS.md          # per-lever operator cards
│   ├── PROMPTS.md                 # prompt library
│   ├── KICKOFF-PROMPTS.md         # session-starter prompts
│   ├── ARTIFACTS.md               # artifact formats (pairs with FORMULAS.md)
│   ├── CASE-STUDIES.md            # long-form narratives
│   ├── CROSS-SKILL.md             # how this skill composes with others
│   │
│   ├── VIBE-CODED-PATHOLOGIES.md  # P1–P40 — AI-generated-code smells
│   ├── DEAD-CODE-SAFETY.md        # the 12-step gauntlet
│   ├── RESCUE-MISSIONS.md         # when the project is in crisis
│   ├── CONTINUOUS-REFACTOR.md     # keep-it-green playbook
│   ├── PROPERTY-TESTS.md          # property-test design guidance
│   ├── REAL-SESSION-EVIDENCE.md   # citation appendix from cass mining
│   ├── CORPUS.md                  # methodology source corpus
│   ├── TRIANGULATED-KERNEL.md     # R-001 … R-030 rule base
│   ├── PROMPT-ENGINEERING.md      # how to ask an agent to do this work
│   ├── FLYWHEEL-INTEGRATION.md    # multi-agent flywheel hookup
│   │
│   ├── REACT-DEEP.md              # React-specific duplication patterns
│   ├── DB-SCHEMAS.md              # schema-deduplication
│   ├── TYPE-SHRINKS.md            # narrow-type levers
│   │
│   ├── JSM-BOOTSTRAP.md           # sibling-skill install on demand
│   ├── AGENT-COORDINATION.md      # Agent Mail, NTM, beads
│   ├── METRICS-DASHBOARD.md       # per-pass dashboard spec
│   │
│   ├── RUST-DEEP.md               # Rust idioms
│   ├── PYTHON-DEEP.md             # Python idioms
│   ├── GO-DEEP.md                 # Go idioms
│   ├── CPP-DEEP.md                # C++ idioms
│   ├── LANGUAGE-GUIDES.md         # cross-language overview
│   ├── MICROPATTERNS.md           # M1–M40
│   ├── ADVANCED-MICROPATTERNS.md  # M41–M80
│   │
│   ├── MONOREPO.md                # monorepo-specific concerns
│   ├── SECURITY-AWARE-REFACTOR.md # when sites cross security boundaries
│   └── PERF-AWARE-REFACTOR.md     # when sites cross perf tiers
│
├── assets/                        # ready-to-copy templates
│   ├── isomorphism_card.md        # per-candidate card
│   ├── ledger_header.md           # refactor ledger template
│   ├── rejection_log.md           # rejection-log template
│   ├── dashboard_skeleton.md      # per-pass dashboard template
│   ├── pr_description.md          # PR body template
│   └── bead_commands.md           # br workflow cheat-commands
│
├── scripts/                       # executable helpers
│   ├── session_setup.sh           # phase 0: one-shot kickoff
│   ├── check_skills.sh            # sibling-skill inventory
│   ├── install_jsm.sh             # jsm installer bootstrap
│   ├── install_missing_skills.sh  # install missing siblings
│   ├── baseline.sh                # phase A: tests + goldens + LOC + lint
│   ├── dup_scan.sh                # phase B: duplication scanners
│   ├── ai_slop_detector.sh        # phase B: P1–P40 pathology scan
│   ├── unpinned_deps.sh           # phase B: dep-pin audit
│   ├── loc_delta.sh               # source-line diff helper
│   ├── callsite_census.sh         # count every call site per candidate
│   ├── score_candidates.py        # phase C: scoring (threshold ≥ 2.0)
│   ├── isomorphism_card.sh        # phase D: card scaffold
│   ├── dead_code_safety_check.sh  # dead-code gauntlet
│   ├── boundary_validator_scaffold.sh
│   ├── property_test_scaffold.sh
│   ├── verify_isomorphism.sh      # phase F: verify
│   ├── lint_ceiling.sh            # warning-ceiling enforcer (R-013)
│   ├── rescue_phase_check.sh      # rescue-mission exit gate
│   ├── ledger_row.sh              # phase G: append ledger row
│   ├── metrics_snapshot.sh        # dashboard baseline
│   ├── multi_agent_swarm.sh       # fan-out across candidates
│   ├── extract_kernel.sh          # print marker-delimited kernel
│   ├── validate_operators.py      # operator-card contract validator
│   ├── validate_corpus.py         # quote-bank contract validator
│   └── validate_skill_contract.py # top-level package validator
│
└── subagents/                     # role-specialized defs (per .claude subagent format)
    ├── refactor-extractor.md
    ├── refactor-reviewer.md
    ├── duplication-scanner.md
    ├── isomorphism-auditor.md
    └── dead-code-checker.md
```

## Project artifacts (what this skill writes)

Any project consuming this skill will have, per pass:

```
<project-root>/
└── refactor/
    └── artifacts/
        └── <run-id>/                            # yyyy-mm-dd-pass-N
            ├── skill_inventory.json             # sibling-skill state
            ├── baseline.md                      # test + LOC + lint snapshot
            ├── tests_before.txt                 # raw test runner output
            ├── duplication_map.md               # candidate list (edit manually)
            ├── slop_scan.md                     # AI-slop pathology findings
            ├── unpinned_deps.md                 # dep-pin audit
            ├── goldens/                         # golden inputs + outputs
            ├── cards/
            │   └── ISO-<nnn>.md                 # one per accepted candidate
            ├── callsites/
            │   └── ISO-<nnn>.txt                # callsite census
            ├── metrics.json                     # baseline metrics
            ├── ledger.md                        # shipped/reverted/rejected rows
            ├── rejection_log.md                 # explicit rejections (forever)
            ├── dashboard.md                     # per-pass dashboard
            ├── CLOSEOUT.md                      # end-of-pass summary
            └── rescue_gate.md                   # only for rescue passes
```

Plus one persistent file per project:

```
refactor/artifacts/warning_ceiling.txt           # R-013 ceiling, keep across passes
```

The `refactor/` directory is gitignored EXCEPT for `warning_ceiling.txt`,
ledger, rejection log, and CLOSEOUT files — those belong in git so the next
pass can read them.

## Progressive-disclosure discipline

- SKILL.md links to references one level deep.
- Reference files may cross-link (e.g., COOKBOOK.md → DEAD-CODE-SAFETY.md) but
  do not create a tangled web. Each reference should read coherently on its
  own without pre-loading siblings.
- `assets/` are pure templates — no prose, no cross-links, just placeholders.
- `scripts/` are self-contained. Each reads the run-id + artifacts dir it
  needs; they don't source each other's shell state.
- `subagents/` are role briefings — each one is small, focused, and callable
  via the Agent tool.

## When to add a new reference file

Only add a new file when:

1. An existing file is getting long enough that its TOC hides content (roughly
   >1000 lines), OR
2. A new domain emerges that's orthogonal to existing files (e.g., if we add
   first-class support for "frontend framework X", it gets its own deep
   reference), OR
3. A sibling skill wants to link to a specific subset of guidance — linking to
   a focused file is better than linking deep into a large one.

When adding, update SKILL.md's Reference Index AND the tree above.
