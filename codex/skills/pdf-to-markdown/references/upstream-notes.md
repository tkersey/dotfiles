# Upstream notes

This skill is designed to preserve the behavior profile of `jzillmann/pdf-to-markdown` without depending on that repository or any external package manager at runtime.

## Why the skill is not a thin wrapper

The upstream repository is still organized as a browser-first application. Its README and package manifest describe a webpack app with build/start scripts rather than a stable CLI entrypoint, so using it directly inside a Codex skill would still require packaging the app runtime around it.

## Heuristics intentionally transplanted from the upstream design

The bundled Python converter follows the same broad transformation shape as the original JavaScript pipeline:

- global document statistics: dominant body font, dominant line spacing, and max heading size
- line compaction from positioned text fragments
- repeated header/footer suppression by hashing edge lines while ignoring spaces and digits
- table-of-contents detection from early pages with trailing page numbers
- TOC-driven heading recovery by matching heading text back into body pages
- heading fallback from size tiers, font changes, and title-page cues
- bullet and numbered list normalization
- list nesting derived from indentation levels
- block gathering by vertical spacing and block type transitions
- indented code/quote block detection
- Markdown rendering with block-type semantics similar to the upstream `BlockType` / `WordType` model

## Main implementation differences

- Parser backend: this skill uses vendored `pypdf` code inside `scripts/vendor/python/pypdf` rather than PDF.js.
- Runtime: this skill runs as a local Python script with no npm, webpack, browser UI, or runtime downloads.
- Scope: OCR, images, and high-fidelity layout reproduction are still out of scope.
- Tables: support is heuristic and opportunistic; the original upstream project also treats tables as an open problem.

## Practical implications

This bundle is meant to be deterministic, repo-local, and easy for Codex to run directly. It trades browser interactivity for a self-contained conversion workflow that can live entirely inside `.agents/skills/pdf-to-markdown`.
