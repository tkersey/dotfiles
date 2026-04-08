# Logophile Doctrine Patch Notes

## What changed
- Added doctrine synthesis as a first-class `logophile` submode.
- Kept rewrite and naming behavior intact.
- Kept trigger boundary hard: wording, naming, or doctrine output must be explicitly requested.
- Made `doctrine` the canonical mode name.
- Preserved backward-compatible aliases: `rigor`, `rigor-fast`, `rigor-annotated`.

## Why this shape
- One lexical skill now covers rewrite, naming, and doctrine-word synthesis.
- The skill still does not claim operational work such as implementation, review, or orchestration.
- Doctrine mode produces word stacks plus an unpacked doctrine block, not naked lists.
