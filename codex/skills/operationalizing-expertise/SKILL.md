---
name: operationalizing-expertise
description: >-
  Operationalize expert methods into corpus, quote bank, triangulated kernel,
  operator library, and validators. Use when distilling a methodology or mining
  session history into executable rules.
---

# Operationalizing Expertise

Goal: turn tacit method into executable, auditable artifacts.

## Quick Start (pick a track)

### Track A: Static Distillation (corpus -> kernel)
Use when you only need a stable, parseable methodology (Lemelson-style).

Summary: corpus + quote bank + triangulated kernel + operator library + validators.
Full steps: `references/WORKFLOWS.md`.

### Track B: Orchestrated Loop (kickoff -> deltas -> artifact)
Use when you want multi-agent sessions that compile into structured artifacts (Brenner-style).

Summary: kickoff -> deltas -> deterministic merge + lint -> artifacts.
Full steps: `references/WORKFLOWS.md` and `references/ARTIFACTS.md`.

### Track C: Session Mining (your own practice)
Use when operationalizing your own repeated behaviors into a reusable skill.

1) Find repeated prompts/actions in history (cass search).
2) Extract triggers, actions, and avoided failures.
3) Generalize into rules: "When X, do Y because Z."
4) Validate against counter-examples.

If unsure, start with Track A then add Track B only if you need orchestration.

## Deliverables (non-negotiable)

- `corpus/primary_sources/` with source transcripts or papers
- `corpus/quote_bank/quote_bank.md` with stable anchors + tags
- `corpus/distillations/{gpt,opus,gemini}/...`
- `corpus/specs/triangulated_kernel.md` with START/END markers
- `corpus/specs/operator_library.md` with operator cards + prompt modules
- `corpus/specs/session_kickoff*.md` (role prompts or kickoff templates)
- `scripts/validate-corpus.py`, `scripts/validate-operators.py`, `scripts/extract-kernel.py`
- `artifacts/` for compiled outputs (if Track B)

## Core Invariants (must hold)

- Evidence-first: every rule cites anchors in the quote bank.
- Deterministic parsing: kernel/operator sections must be marker-bounded.
- Triangulation: kernel contains consensus only; disagreements go to DISPUTED/UNIQUE.
- Operator cards must include triggers, failure modes, and a prompt module.
- Validation gates are required; failing them blocks release.
- Provenance must be auditable (quote IDs, source file, page/section).
- Join-key contract: thread_id ties mail thread, tmux session, and artifact file.
- Memory feedback is opt-in and must be hygiene-gated.

## Canonical Markers and Formats
See `references/FORMATS.md` (kernel markers, quote bank entries, operator cards, delta blocks).

## Workflow A + B (full)
See `references/WORKFLOWS.md` for detailed steps.

## Validation Gates (minimum)
See `references/VALIDATION.md` (includes the minimum gate list verbatim).

## Anti-patterns
See `references/ANTI-PATTERNS.md` (includes the minimum list verbatim).

## Output Contract (what you produce)
See `references/OUTPUT.md`.

## Reference Index

- Corpus structure: `references/CORPUS.md`
- Distillation prompts: `references/DISTILLATION.md`
- Triangulation rules: `references/TRIANGULATION.md`
- Operator cards: `references/OPERATORS.md`
- Kickoff prompts: `references/KICKOFF.md`
- Artifacts and deltas: `references/ARTIFACTS.md`
- Validation gates: `references/VALIDATION.md`
- Jargon/terms: `references/JARGON.md`
- Anti-patterns: `references/ANTI-PATTERNS.md`
- End-to-end case: `references/CASE-STUDY.md`
