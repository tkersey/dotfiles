---
name: deckset
description: Generate Deckset markdown presentations from conversation context with high semantic fidelity. Use when requests mention decks, slides, presentations, speaker notes, or Deckset markdown output, especially when converting an existing conversation into a narrative slide flow. This skill refreshes upstream Deckset markdown docs and the configured gist examples on every run before drafting.
---

# Deckset

## Workflow

1. Refresh upstream references first, on every invocation:
   - `uv run /Users/tk/.dotfiles/codex/skills/deckset/scripts/refresh_sources.py`
2. Read the conversation and extract:
   - audience
   - objective
   - key claims and evidence
   - constraints or required talking points
3. Build a narrative spine before writing slides:
   - opening context
   - core argument sequence
   - implementation/evidence details
   - decision summary or call to action
4. Draft a single Deckset markdown deck.
5. Run quality gates before returning output.

## Output Contract

- Produce one complete Deckset markdown artifact by default.
- Include presenter notes using `^` when they improve delivery.
- Keep styling app/prompt-driven:
  - do not force a fixed theme/footer unless requested
  - do not force a fixed slide count; size to content
- Use Deckset syntax and commands only where they add clear value.

## Deckset Rules

- Separate slides with `---`.
- Prefer `#` and `##` headings for slide structure.
- Use `[fit]` only when needed to preserve readability.
- Keep one major idea per slide unless the content is inherently coupled.
- Keep code blocks concise and language-labeled.
- Use incremental build commands only when the user asks for staged reveals.

## Quality Gates

- Fidelity: preserve the conversation's claims and hierarchy.
- Coherence: each slide should have a clear purpose in the narrative.
- Syntax: deck parses as valid markdown with Deckset commands placed correctly.
- Delivery: presenter notes clarify talking points, not duplicate slide text.

## References

- Deckset markdown docs cache:
  - `references/deckset-markdownDocumentation.html`
- Gist example cache:
  - `references/examples/*.md`
- Refresh metadata:
  - `references/refresh-metadata.json`

If refresh falls back to cache, disclose that in the response summary.
