# Changelog — simplify-and-refactor-code-isomorphically

> All notable changes to this skill are documented here. This file is a
> semver-style changelog so downstream users can pin a version and
> understand breaking changes.

**Versioning policy:**

- **Patch (x.y.Z)** — typo fixes, wording tweaks, new examples, FAQ
  additions. No behavior change for agents following the skill.
- **Minor (x.Y.0)** — new reference files, new scripts, new subagents,
  new hook templates. Existing artifact schemas unchanged; agents on
  previous versions continue to work.
- **Major (X.0.0)** — changes to The Loop phases, isomorphism-card
  schema, score formula, or any artifact shape that downstream tooling
  depends on.

Pin a version by recording it in your project's `AGENTS.md` or in a
`.refactor-skill-version` file at the repo root.

## [Unreleased]

### Added
- `references/VALIDATION.md` documenting read-only package validation gates.
- `scripts/extract_kernel.sh` for marker-delimited extraction of
  `TRIANGULATED-KERNEL.md`.
- `scripts/validate_operators.py` to enforce the operator-card contract.
- `scripts/validate_corpus.py` to enforce quote-bank entry shape.
- `scripts/validate_skill_contract.py` as the top-level self-validator.

### Changed
- Extended `scripts/ai_slop_detector.sh` from P1-P21 coverage to P1-P40
  coverage, matching the expanded pathology catalog.
- Completed operator cards with missing third triggers and prompt modules so
  the operator library is executable by agents and machine-checkable.
- Hardened `scripts/ai_slop_detector.sh` source-path handling, made the `rg`
  dependency explicit, and fixed P18 hook counting to count hook occurrences
  instead of matching lines.
- Tightened `scripts/validate_skill_contract.py` so P1-P40 consistency is
  checked in the specific files that must expose those markers.
- Corrected stale P1-P21 wording in `references/VIBE-CODED-PATHOLOGIES.md`
  and fixed malformed links in `references/SECURITY-AWARE-REFACTOR.md`.
- Extended local-link validation beyond `SKILL.md` and fixed additional stale
  links in rescue, pathology, and PR-template references.
- Extended local-link validation to check Markdown section anchors and preserve
  inline-code link labels, then fixed stale anchors in the entry point,
  property-test TOC, Rust/type-shrink references, and pathology catalog.
- Tightened anchor extraction so headings inside fenced examples cannot satisfy
  section links.
- Corrected GitHub-style heading slugging for code spans containing generic
  syntax such as `Box<dyn Trait>` and `parse<T: FromStr>`.
- Corrected heading slugging for headings that contain Markdown links so the
  rendered link text, not the target URL, determines the anchor.
- Added anchor-slug regression samples to `validate_skill_contract.py`.
- Aligned Markdown anchor and fenced-block extraction with CommonMark's
  0-3 leading-space rule so valid indented headings are checked and 4-space
  indented code headings stay inert.
- Hardened generated scripts and prompts against unsafe mechanics: removed
  `sed -i`/backup deletion from card scaffolding, removed `eval` from
  callsite census, replaced temp `rm -rf` cleanup in metrics/LOC helpers,
  added `loc_delta.sh --net-only` for CI, and rewrote stash/destructive-cleanup
  examples into non-destructive flows.
- Fixed helper-script correctness issues found by ShellCheck: repaired
  `ledger_row.sh` command-substitution syntax, made ledger appends quote-safe,
  quoted dynamic scanner commands, removed unsafe simian filename splitting,
  and made rescue/dead-code file discovery handle missing paths and spaces.
- Moved long-reference contents lists directly under their titles so `/sw`
  and weak-model first-screen scans see navigation immediately.

## [1.0.0] — 2026-04-23

**First stable release.**

Major pieces — the skill is usable end-to-end at this version:

### Core
- The Loop (Phases 0-8) as the mandatory flow
- The One Rule: *preserve behavior, prove it, one lever per commit*
- Opportunity Matrix scoring: `Score = (LOC_saved × Conf) / Risk ≥ 2.0`
- Clone taxonomy (Types I-V including Type V "accidental rhyme")
- Abstraction ladder (rungs 0-6)
- 8 canonical levers (L-EXTRACT, L-PARAMETERIZE, L-DISPATCH, L-ELIMINATE,
  L-TYPE-SHRINK, L-DELETE-DEAD, L-MERGE-FILES, L-PIN-DEP)
- 40 vibe-coded pathologies (P1-P40)
- 80 named micropatterns (M1-M80)
- 30 triangulated-kernel rules (R-001 to R-030)
- 5 horror stories (HS#1-HS#5) anchored to real session evidence

### References (44 total)
- Core methodology: METHODOLOGY, TECHNIQUES, LANGUAGE-GUIDES,
  DUPLICATION-TAXONOMY, ABSTRACTION-LADDER, ISOMORPHISM, ANTI-PATTERNS,
  OPERATOR-CARDS, PROMPTS, ARTIFACTS, CASE-STUDIES, CROSS-SKILL
- Vibe-coded: VIBE-CODED-PATHOLOGIES, DEAD-CODE-SAFETY, RESCUE-MISSIONS,
  CONTINUOUS-REFACTOR, PROPERTY-TESTS, REAL-SESSION-EVIDENCE, CORPUS,
  TRIANGULATED-KERNEL, PROMPT-ENGINEERING, ANTI-PATTERNS-2,
  FLYWHEEL-INTEGRATION
- Domain: REACT-DEEP, DB-SCHEMAS, TYPE-SHRINKS
- Orchestration: JSM-BOOTSTRAP, AGENT-COORDINATION, METRICS-DASHBOARD,
  KICKOFF-PROMPTS
- Language deep-dives: RUST-DEEP, PYTHON-DEEP, GO-DEEP, CPP-DEEP,
  MICROPATTERNS, ADVANCED-MICROPATTERNS
- Cross-cutting: MONOREPO, SECURITY-AWARE-REFACTOR, PERF-AWARE-REFACTOR
- Quick-access layer: QUICK-REFERENCE, COOKBOOK, FORMULAS, SELECTION,
  TESTING, HOOKS, STRUCTURE
- Friction-reducing layer: GLOSSARY, FAQ, DECISION-TREES, EXIT-CRITERIA,
  REVIEWER-QUICKSTART, ROLLBACK-PLAYBOOK, COLD-START, GIT-HOOKS,
  CI-CD-INTEGRATION, TEAM-ADOPTION, VISUAL-DIAGRAMS, BENCHMARKS

### Scripts (21)
- Bootstrap: check_skills, install_jsm, install_missing_skills
- Pipeline: baseline, dup_scan, ai_slop_detector, unpinned_deps, loc_delta
- Per-candidate: isomorphism_card, score_candidates, callsite_census,
  dead_code_safety_check, boundary_validator_scaffold,
  property_test_scaffold
- Verify: verify_isomorphism, lint_ceiling
- Rescue: rescue_phase_check
- Ledger/dashboard: ledger_row, metrics_snapshot
- Multi-agent: multi_agent_swarm
- One-shot: session_setup

### Assets (6 copy-ready templates)
- isomorphism_card.md
- ledger_header.md
- rejection_log.md
- dashboard_skeleton.md
- pr_description.md
- bead_commands.md

### Subagents (5 role-specialized)
- refactor-extractor
- refactor-reviewer
- duplication-scanner
- isomorphism-auditor
- dead-code-checker

### Artifact schema
- Per-pass directory layout: `refactor/artifacts/<run-id>/{baseline,
  duplication_map, cards/, goldens/, ledger, rejection_log, dashboard,
  CLOSEOUT}.md`
- Project-persistent files: `refactor/artifacts/warning_ceiling.txt`,
  `ledger.md`, `rejection_log.md`, `CLOSEOUT.md`
- Candidate ID format: `ISO-<nnn>`; rhyme ID format: `RHY-<nnn>`
- Run ID format: `YYYY-MM-DD-pass-<N>`

### Known limitations in v1.0.0
- `loc_delta.sh` reports source-line diff from `git diff --numstat`; use
  baseline artifacts for total-code-LOC accounting when needed
- `verify_isomorphism.sh` treats golden-dir absence as pass (for
  projects without goldens yet); cold-start sets up the directory
- Score threshold `2.0` is a default; see METHODOLOGY.md for tuning
- Warning ceiling is per-project; for monorepos, run one ceiling per
  package (see MONOREPO.md)

## Future (unreleased)

### [1.1.x] — planned
- `score_candidates.py` to emit a second-opinion score using an LLM
  call to the [multi-model-triangulation](../multi-model-triangulation/SKILL.md)
  skill
- Additional pathologies P41-P50 as they're observed in real sessions
- Monorepo-aware `lint_ceiling.sh` with per-package state

### [2.0.0] — candidate
- Isomorphism card schema change: structured YAML front-matter replacing
  free-form markdown sections. Tooling would break.
- Score formula tuning: weight blast radius more heavily for PUB-API
  changes. Would re-classify some previously-accepted candidates.

Any 2.0.0-class change will ship with a migration guide and a runnable
migration script (`scripts/migrate_v1_to_v2_cards.py`).

---

## How to contribute a change

1. Open a PR updating the relevant reference file(s).
2. Update this CHANGELOG under a `[Unreleased]` section above [1.0.0].
3. Follow conventional-commit style in your commit messages:
   `docs(refactor-skill): add X`, `feat(refactor-skill): ship Y`,
   etc.
4. After merge, a maintainer tags the release and renames `[Unreleased]`
   to the new version.
