# Validation Gates

These checks convert methodology into a contract. If any fail, do not ship.

## Corpus Validation

- Required directories exist: `primary_sources`, `quote_bank`.
- Primary sources are non-empty and above a minimum size.
- Anchor scheme is consistent and references actual segments.

## Quote Bank Validation

- Anchors are sequential with no gaps (e.g., §1..§N).
- Each entry has: header, quote line, source line, tags line.
- Quote length bounds are enforced (avoid noise or truncation).
- Tags are from a fixed taxonomy.

## Kernel Validation

- START/END markers present and versioned.
- Minimum count of axioms and operators.
- All anchors referenced exist in the quote bank.

## Operator Library Validation

- Each operator has required fields:
  - Definition
  - When-to-Use Triggers
  - Failure Modes
  - Prompt Module
  - Canonical tag
  - Quote-bank anchors

## Kickoff Validation

- Kernel markers embedded.
- Version marker matches kernel version.
- All role prompts include operator references.

## Artifact Lint (Track B)

- Required sections present.
- Third alternative is included.
- Evidence anchors required for claims.
- Invalid deltas are reported, not ignored.

## Minimal Scripts (examples)

- `scripts/validate-corpus.py`
- `scripts/validate-operators.py`
- `scripts/extract-kernel.py`

Add CI to run these on every change to corpus/specs/artifacts.

