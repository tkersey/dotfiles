# CSCTF Processing Algorithms

## Table of Contents
- [End-to-End Flow](#end-to-end-flow)
- [Selector Strategy](#selector-strategy)
- [Turndown Customization](#turndown-customization)
- [Normalization](#normalization)
- [Slugging Algorithm](#slugging-algorithm)
- [HTML Rendering](#html-rendering)

---

## End-to-End Flow

### ChatGPT, Gemini, Grok

```
1. Launch headless Playwright Chromium with stealth config
   (spoofed navigator properties, realistic headers)
2. Navigate twice (domcontentloaded → networkidle) for late-loading assets
3. Detect provider from URL hostname
4. Wait for provider-specific selectors with retry/fallback
5. Extract each role's inner HTML (assistant/user), traverse Shadow DOM
6. Clean pills/metadata, run Turndown with fenced-code rule
7. Normalize whitespace and newlines
8. Write Markdown to temp file, rename atomically
9. Render HTML twin with inline CSS/TOC/HLJS
```

### Claude.ai

```
1. Copy Chrome session cookies to temporary profile
2. Launch Chrome with remote debugging
3. Connect via Chrome DevTools Protocol
4. Extract conversation HTML
5. Process through same Turndown/normalization pipeline
6. Clean up temporary profile
```

---

## Selector Strategy

Provider-specific selectors with fallback chains:

| Provider | Primary Selector |
|----------|-----------------|
| **ChatGPT** | `article [data-message-author-role]` |
| **Gemini** | Custom web components (`share-turn-viewer`, `response-container`) |
| **Grok** | Flexible `data-testid` patterns |
| **Claude** | `[data-testid="user-message"]` and streaming indicators |

Each has multiple fallbacks tried with short timeouts.

---

## Turndown Customization

- Injects fenced code blocks
- Detects language via `class="language-*"`
- Strips citation pills and `data-start`/`data-end` attributes

---

## Normalization

- Converts newlines to `\n`
- Removes Unicode LS/PS characters
- Collapses excessive blank lines

---

## Slugging Algorithm

```
Title → lowercase → non-alphanumerics → "_" → trim → max 120 chars
      → Windows reserved-name suffix → collision suffix (_2, _3, ...)
```

### Examples

```
"How to Build a REST API"  → how_to_build_a_rest_api.md
"Python Tips & Tricks!"    → python_tips_tricks.md
"File exists already"      → file_exists_already_2.md
```

### Rules

- Lowercase
- Non-alphanumerics → `_`
- Trimmed leading/trailing `_`
- Max 120 characters
- Windows reserved names suffixed
- Collisions: `_2`, `_3`, ...

---

## HTML Rendering

- Markdown-it + highlight.js
- Heading slug de-dupe for TOC
- Inline CSS for light/dark/print
- Zero JavaScript

### Features

| Feature | Implementation |
|---------|----------------|
| **Standalone** | No external dependencies |
| **Zero JavaScript** | Safe for any hosting |
| **Inline CSS** | Light/dark mode via `prefers-color-scheme` |
| **Syntax highlighting** | highlight.js themes inline |
| **Table of contents** | Auto-generated from headings |
| **Language badges** | Code block language indicators |
| **Print-friendly** | Optimized print styles |

---

## Design Principles

| Principle | Implementation |
|-----------|----------------|
| **Determinism** | Explicit slugging and collision handling |
| **Minimal network** | Only share URL fetched (update checks/publish opt-in) |
| **Safety** | Static HTML (inline CSS/HLJS), no scripts emitted |
| **Clarity** | Colorized step-based logging, confirmation gates |
| **Atomicity** | Temp+rename writes prevent partial files |

---

## Security & Privacy

### Network Behavior

- **Only fetches:** The share URL itself
- **Opt-in:** Update checks, GitHub publish flows
- **Auth:** GitHub CLI (`gh`) for publishing—no tokens stored

### HTML Safety

- Zero JavaScript in output
- Inline styles only
- Citation pills and data attributes stripped
- highlight.js used statically

### Filesystem

- Temp+rename write pattern (atomic)
- Collision-proof naming
- Config: `~/.config/csctf/config.json`

### Claude.ai Cookies

- Copied to temporary directory only
- Used for single scraping session
- Original Chrome profile never modified
