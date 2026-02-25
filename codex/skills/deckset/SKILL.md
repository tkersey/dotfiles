---
name: deckset
description: Generate Deckset markdown presentations from conversation context with high semantic fidelity. Use when requests mention decks, slides, presentations, speaker notes, or Deckset markdown output, especially when converting an existing conversation into a narrative slide flow. This skill refreshes upstream Deckset markdown docs and the configured gist examples on every run before drafting.
---

# Deckset

## Workflow

1. Refresh upstream references first, on every invocation (run from this skill directory):
   - `uv run scripts/refresh_sources.py`
   - Optional: set `GH_TOKEN`/`GITHUB_TOKEN` to avoid GitHub API rate limits
   - Optional: `--max-age-sec 3600` to reduce network refreshes
2. Read refresh metadata:
   - `references/refresh-metadata.json` -> capture `refreshed_at`, `docs_source`, `gist_source`, `used_cache_fallback`
3. Read the conversation and extract:
   - audience
   - objective
   - timebox (talk length) + format (demo, deep dive, status update, pitch)
   - key claims and evidence
   - constraints (must-include points, required sections, theme/footer if specified)
4. Build a narrative spine and a slide outline (titles + 1-line intent) before writing slides.
5. Draft a single Deckset markdown deck.
6. Add a provenance stamp as a presenter note on slide 1:
   - `^ deckset-skill refresh: refreshed_at=<...> docs=<...> gist=<...> cache_fallback=<...>`
7. Run quality gates before returning output.

## Output Contract

- Output exactly one complete Deckset markdown deck by default.
- Include presenter notes using `^` when they improve delivery.
- Defaults:
  - if audience is not specified, assume a mixed technical audience
  - if duration is not specified, target ~10 minutes / ~10 slides (do not force a hard slide count)
- If missing duration/audience would materially change the deck, ask exactly one clarifying question; otherwise apply the defaults.
- Keep styling prompt-driven:
  - do not force a theme/footer/slidenumbers/autoscale unless requested
  - do not force a fixed slide count; size to content
- Prefer `references/deckset-cheatsheet.md` over the HTML docs cache.

## Deckset Rules

- Separate slides with `---`.
- Prefer `#` and `##` headings for slide structure.
- Use `[fit]` only when needed to preserve readability.
- Keep one major idea per slide unless the content is inherently coupled.
- Keep code blocks concise and language-labeled.
- Use incremental build commands only when the user asks for staged reveals.
- Global commands (e.g. `theme:`, `footer:`, `slidenumbers:`) must be at the top of the file with no blank lines between them.
- If you open columns (`[.column]`), always close with `[.end-columns]`.

## Quality Gates

- Fidelity: preserve the conversation's claims and hierarchy.
- Coherence: each slide should have a clear purpose in the narrative.
- Syntax: deck parses as valid markdown with Deckset commands placed correctly.
- Delivery: presenter notes clarify talking points, not duplicate slide text.
- Structure: every slide has a title; one major idea per slide.
- Density: keep slides scannable (<= 6 bullets per slide; move detail into presenter notes).
- Provenance: slide 1 includes the refresh stamp and it matches `references/refresh-metadata.json`.

## References

- Cheatsheet (preferred):
  - `references/deckset-cheatsheet.md`
- Full docs cache (fallback):
  - `references/deckset-markdownDocumentation.html`
- Gist example cache:
  - `references/examples/*.md`
- Refresh metadata:
  - `references/refresh-metadata.json`

If `used_cache_fallback` is true, disclose that in the response summary.
