# OPERATIONALIZING-EXPERTISE-TRACK-A — How this skill IS a Track A artifact

The `/operationalizing-expertise` skill defines a methodology — "Track A" — for converting tacit expertise into executable rules. It produces five canonical artifacts: **corpus**, **quote bank**, **triangulated kernel**, **operator library**, **validators**.

This skill IS a Track A artifact for the domain "agent ergonomics for CLI tools." This file makes the mapping explicit so:
- Readers understand the methodological foundation
- Future contributors know how to extend each artifact correctly
- Cross-skill comparisons are tractable (e.g. against `wills-and-estate-planning-skill`'s Track A treatment)

---

## The five artifacts in this skill

### 1. Corpus

> *Source material: real-world tools, sessions, and incidents that the methodology is distilled from.*

| Source | Where it lives | Used by |
|--------|-----------------|---------|
| **Canonical CLIs the user built** | `references/exemplars/CANONICAL-EXEMPLARS.md` (dcg / bv / am / ubs / cass) | Phase 2 scoring (anchor for 750+) |
| **Counter-examples in the wild** | `references/exemplars/COUNTER-EXAMPLES.md` (CE-1 to CE-20) | Phase 2 scoring (anchor for < 250) |
| **Worked end-to-end audits** | `references/exemplars/WORKED-EXAMPLES.md` (15 case studies including dcg, bv, am, ubs, cass, jq, ripgrep, gh, kubectl, npm, cargo, ffmpeg, terraform, aws-cli, docker) | Phase 0 calibration; Phase 4 priority weighting |
| **CASS findings — observed agent failure modes** | `references/exemplars/CASS-FINDINGS.md` | Phase 0 frequency signal; Phase 4 priority weighting |
| **AGENTS.md compliance corpus** | Cited in `references/exemplars/QUOTE-BANK.md` § 900-series | Phase 5 application discipline |

**How to extend.** When you find a new exemplar (a CLI doing something better than any current one), add a numbered Pattern to CANONICAL-EXEMPLARS.md AND cite it in QUOTE-BANK.md with a `[Q-NNN]` ID. When you find a new counter-example, add `CE-NN` to COUNTER-EXAMPLES.md.

---

### 2. Quote Bank

> *Anchored, citable phrases from the corpus that pin the methodology to specific source material.*

Lives in `references/exemplars/QUOTE-BANK.md`, organized into ID ranges:

| Range | Theme |
|-------|-------|
| `[Q-001]–[Q-003]` | The One Rule (north-star) |
| `[Q-100]–[Q-102]` | Robot mode discipline |
| `[Q-200]–[Q-201]` | Mega-commands |
| `[Q-300]–[Q-302]` | Error pedagogy |
| `[Q-400]–[Q-402]` | Determinism + provenance |
| `[Q-500]–[Q-501]` | Self-documentation |
| `[Q-600]–[Q-601]` | Exit codes |
| `[Q-700]–[Q-701]` | Safety with recovery |
| `[Q-800]–[Q-801]` | File reservations + multi-agent coordination |
| `[Q-900]–[Q-903]` | AGENTS.md compliance |
| `[Q-1000]–[Q-1004]` | Audit methodology meta-rules |

**How to use.** Cite `[Q-NNN]` in:
- Recommendation playbooks (anchors the rationale)
- HANDOFF.md narratives
- Conversation with the user
- New operator cards (every operator should cite ≥ 1 quote)

**How to extend.** When a powerful new insight appears in the corpus, add it as the next-available `Q-NNN`. Don't paraphrase — quotes are calibration anchors. New quotes should cite their source (file:line, session URL, or attributable speaker).

---

### 3. Triangulated Kernel

> *The minimal set of axioms that the entire methodology can be derived from. Stable across passes; rarely changed.*

The kernel of this skill is **the 11 dimensions + the One Rule + the Polish Bar**:

```
The One Rule:  Design every surface so the FIRST thing an agent instinctively
               tries "just works." Never silent-fail. Never punish a reasonable
               misstep. Always provide a safe alternative for any dangerous
               request. Output is parseable, deterministic, and self-describing.

11 Dimensions:
  1. agent_intuitiveness         — first-try success
  2. agent_ergonomics            — round-trip count
  3. agent_ease_of_use           — discoverability without external docs
  4. output_parseability         — JSON, exit codes, stdout/stderr
  5. error_pedagogy              — does the error teach?
  6. intent_inference            — does it tolerate legible-but-wrong?
  7. safety_with_recovery        — irreversible ops gated; safe alts named
  8. determinism_and_reproducibility
  9. self_documentation          — capabilities, robot-docs
 10. composability                — pipes, NO_COLOR, CI mode
 11. regression_resistance        — golden tests pin contracts

Polish Bar:    12 non-negotiable rows that every shipped CLI must satisfy on
               its primary surfaces. (See POLISH-BAR.md.)
```

These are the kernel axioms. Most of the rest of the skill is derivable from them.

**How to extend.** Don't lightly. Adding a 12th dimension or amending the One Rule is rare and requires:
- Evidence from 3+ unrelated tools / sessions / incidents
- A `Q-NNN` quote anchor
- A bumped `rubric_version` and re-score across all passes
- Documentation in HANDOFF.md explaining the kernel change

The kernel is meant to be stable. If you find yourself proposing kernel changes frequently, the issue is probably elsewhere (the rubric anchors or operator library, not the kernel).

---

### 4. Operator Library

> *Composable cognitive moves. Each operator is a question that, if it fails, names a section to fix.*

Lives in `references/methodology/OPERATORS.md`. **33 operators**, organized by glyph:

| Glyph | Name | Lifts which dim |
|-------|------|------------------|
| ① | First-Try-Inevitability | intuitiveness |
| Σ | Mega-Command | ergonomics |
| ⟁ | Intent-Infer-Then-Act | intent_inference |
| 🛡 | Safe-Alternative-Always | safety |
| 📜 | Self-Describing | self_documentation |
| 📖 | In-Tool-Docs | self_documentation |
| 🚦 | Exit-Code-Contract | parseability |
| 🪧 | Stdout-Data-Stderr-Diag | parseability + composability |
| 🧪 | Pin-The-Contract-Test | regression_resistance |
| 🔀 | Macros-vs-Granular | ergonomics |
| 🆔 | Stable-Handle | determinism |
| 🩹 | Error-Teaches | error_pedagogy |
| 🚫 | Never-Silent-Fail | error_pedagogy + composability |
| ⏱ | Sub-Second-Hot-Path | ergonomics |
| 🌐 | Honors-Env-Conventions | composability |
| 🔢 | Deterministic-Output | determinism |
| 🧭 | Discoverable-From-Help | self_documentation |
| 🪄 | Recommended-Action | error_pedagogy |
| 🪟 | Provenance-Field | parseability + determinism |
| 📐 | Schema-Pin | regression_resistance |
| 🩻 | Doctor-Mode | self_documentation |
| 🔇 | Telemetry-Disable | composability |
| 🎯 | Discovery-Footer | self_documentation |
| 🪜 | Two-Phase-Latency | ergonomics |
| 🔗 | Cross-Verb-Reference | self_documentation |
| 🛂 | Identity-Friction-Collapse | ergonomics |
| 📦 | Stable-Envelope | parseability |
| 🔬 | Single-Step-Atomicity | safety |
| 🧷 | Idempotency-Pin | safety |
| 🧶 | Composable-Verbs | composability |
| 🧮 | Bulk-Friendly | composability |
| 🧾 | Drift-Guard | regression_resistance |
| 🎓 | Onboarding-Curve | intuitiveness |

Each operator is a card with: trigger, failure modes, fix-pointer (rubric §, exemplar), prompt module.

**Composition cheat-sheet.** OPERATORS.md § Composition lists which operators apply per failing dimension. Phase 5 appliers default to applying the operator pipeline for whichever dim is failing.

**How to extend.** When you observe a recurring fix that doesn't map cleanly to an existing operator, propose a new card:
- Pick a free glyph (avoid emoji collisions)
- Define: question, trigger, failure modes, fix-pointer, prompt module
- Cite ≥ 1 `[Q-NNN]` and ≥ 1 exemplar Pattern
- Add to the composition cheat-sheet
- Bump `rubric_version` if the new operator changes the dimension landscape

---

### 5. Validators

> *Executable checks that enforce the methodology mechanically. The shift from "best practice" to "invariant."*

Lives in `tools/` and `audit/regression_tests/`. The skill ships:

| Validator | What it enforces |
|-----------|-------------------|
| `tools/validate_scorecard.sh` | Scores > 700 require evidence; no integer-parse failures; no duplicate (surface_id, pass) |
| `tools/compute_surface_id.sh` | Surface IDs are deterministic given (kind, subtree, name) |
| `scripts/validate_pass.sh` | applied:true ↔ applied_changes.jsonl row + regression test exists |
| `audit/regression_tests/*.test.{sh,rs,py,ts}` | Every applied recommendation pins its contract |
| `scripts/aerg-hooks/check-capabilities-pin.sh` | capabilities --json schema doesn't drift without contract_version bump |
| `scripts/aerg-hooks/check-help-footer.sh` | Every subcommand's --help has the AGENT/AUTOMATION footer |
| `scripts/aerg-hooks/check-mutating-verb-gates.sh` | Every mutating verb has --yes AND --dry-run |
| `scripts/aerg-hooks/check-stdout-stderr-split.sh` | Best-effort scan for error-paths printing to stdout |
| `scripts/diff_scorecards.sh` | Hard-stop on regression > 50 pts overall |

The validator philosophy: **enforce mechanically what's documented in the kernel + operators + Polish Bar.** Documentation rots; validators don't.

**How to extend.** When a recommendation lands, write its regression test using `references/rubric/REGRESSION-TEST-PATTERNS.md`. When a methodology rule emerges, add a CI/hook validator. When a hand-applied rule keeps drifting, add a hook.

---

## Track A maturity: where this skill stands

The Track A maturity ladder (per `/operationalizing-expertise`):

| Level | Description | This skill's status |
|-------|-------------|---------------------|
| 0. **Tacit** | The expertise lives only in the practitioner's head | ✗ (we're past this) |
| 1. **Anecdote** | Stories told but not codified | ✗ |
| 2. **Heuristic** | "Here's what I usually do" rules-of-thumb | ✗ |
| 3. **Rubric** | Anchored scoring scale | ✓ (11 dims × 5 anchors in SCORING-RUBRIC.md) |
| 4. **Operator library** | Composable cognitive moves | ✓ (33 operators in OPERATORS.md) |
| 5. **Validators** | Mechanical enforcement | ✓ (CI hooks + regression tests + scorecard validator) |
| 6. **Self-applying** | The methodology improves itself | ◐ partial — see SELF-APPLICATION.md |

Aspirationally, Level 6 is full self-application: the skill is auditable by itself for its own ergonomics, the rubric is refined automatically based on uplift signal, the operator library grows from CASS findings without human intervention. The skill doesn't fully reach Level 6 today (operator additions still need human review), but the scaffolding is in place.

---

## Cross-pollination with other Track A skills

This skill borrows patterns from other Track A skills in this repo:

| Source skill | Pattern borrowed |
|--------------|-------------------|
| `wills-and-estate-planning-skill` | Multi-phase rigor; "the plan is not complete when X looks good" framing |
| `saas-billing-patterns-for-stripe-and-paypal` | Operating modes (audit-only / full / re-score-only); audit workspace as sibling dir; bead-per-recommendation; CASS mining recipes; verification-first discipline |
| `documentation-website-for-software-project` | Phase loop with idempotent re-entry; Polish Bar as a numbered checklist; orchestration tiers (Solo/Pair/Squad/Swarm) |
| `multi-pass-bug-hunting` | Three calibrated fresh-eyes prompts (verbatim) |
| `multi-model-triangulation` | Phase 4 + 7 multi-model reconciliation matrix |
| `idea-wizard` | Phase 10 second-order improvement generation |
| `codebase-archaeology` + `codebase-report` | Phase 1 surface inventory methodology |

Conversely, this skill contributes back:

| Pattern | Other Track A skills that could adopt |
|---------|----------------------------------------|
| `--robot-*` mandatory + `bare invocation gated` | Any skill that ships a TUI |
| `capabilities --json` as table-stakes | Every CLI-flavored skill |
| Universal Envelope for JSON output | Every skill emitting JSON |
| Levenshtein-1 typo correction | Every skill exposing an arg parser |
| Schema-pin regression tests | Every skill with a stable contract |

---

## How to read the skill through this lens

When you read this skill, group the content as:

1. **Kernel** — SKILL.md § The One Rule + 11 Dimensions + Polish Bar
2. **Corpus** — references/exemplars/*
3. **Quote bank** — references/exemplars/QUOTE-BANK.md
4. **Operators** — references/methodology/OPERATORS.md
5. **Validators** — tools/* + scripts/aerg-hooks/* + audit/regression_tests/*
6. **Phase loop + IO contracts + applier scaffolding** — references/methodology/PHASES.md + IO-CONTRACTS.md + AGENT-PROMPTS.md (the *operational* layer that turns Track A into a runnable pipeline)
7. **Per-language / per-archetype extensions** — references/methodology/LANGUAGE-RECIPES.md + CLI-ARCHETYPES.md + MEGA-COMMAND-DESIGN.md + ERROR-REWRITING-COOKBOOK.md (the *applied* layer)

Each layer can be extended independently. The kernel is sticky. The operational and applied layers grow with use.

---

## Why this matters for the user

When the user invokes this skill, the methodology runs predictably because each piece is anchored:

- A scorer cites a quote → reproducible scoring
- A recommender cites an operator → reproducible recommendations
- An applier follows a regression-test pattern → reproducible application
- A re-scorer uses the same rubric_version → reproducible uplift measurement

Track A is the discipline that prevents "vibes-based" auditing. Without it, two scorers reach different scores; with it, they converge.

---

## Related

- `references/methodology/OPERATORS.md` — full operator library
- `references/exemplars/QUOTE-BANK.md` — full quote bank
- `references/rubric/SCORING-RUBRIC.md` — full kernel rubric
- `/operationalizing-expertise` skill — methodological source
- `references/methodology/SELF-APPLICATION.md` — Level 6 aspirations
