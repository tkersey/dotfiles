---
name: csctf
description: >-
  Convert ChatGPT, Gemini, Grok, and Claude share links to clean Markdown + HTML.
  Use when archiving AI conversations, preserving code fences, or publishing
  transcripts to GitHub Pages.
---

<!-- TOC: Quick Start | THE EXACT PROMPT | Providers | Commands | References -->

# CSCTF — Chat Shared Conversation To File

> **Core Capability:** Convert AI share links into clean Markdown + HTML with preserved code fences, stable filenames, and optional GitHub Pages publishing.

## Quick Start

```bash
# Install
curl -fsSL https://raw.githubusercontent.com/Dicklesworthstone/chat_shared_conversation_to_file/main/install.sh | bash

# Convert any share link
csctf https://chatgpt.com/share/69343092-91ac-800b-996c-7552461b9b70
```

Output:
- `<conversation_title>.md` — Clean Markdown with preserved code fences
- `<conversation_title>.html` — Styled static HTML (zero JavaScript)

---

## THE EXACT PROMPT — Convert Share Link

```
Convert this conversation to Markdown:

csctf <share-url>

# Example providers:
csctf https://chatgpt.com/share/69343092-91ac-800b-996c-7552461b9b70
csctf https://gemini.google.com/share/66d944b0e6b9
csctf https://grok.com/share/bGVnYWN5_d5329c61-f497-40b7-9472-c555fa71af9c
csctf https://claude.ai/share/549c846d-f6c8-411c-9039-a9a14db376cf
```

---

## THE EXACT PROMPT — Publish to GitHub Pages

```
# Publish with defaults (creates repo if needed)
csctf <url> --publish-to-gh-pages --yes

# Save settings for future use
csctf <url> --publish-to-gh-pages --remember --yes

# Subsequent: just use --yes
csctf <url> --yes

# Custom repo
csctf <url> --publish-to-gh-pages \
  --gh-pages-repo myuser/my-chats \
  --gh-pages-branch main \
  --yes
```

---

## THE EXACT PROMPT — Batch Archive

```
# Archive multiple conversations
for url in $URLS; do
  csctf "$url" --outfile ~/archive/ --quiet
done

# Markdown only (faster, smaller)
csctf <url> --md-only --quiet

# HTML only for embedding
csctf <url> --html-only --outfile site/chat.html
```

---

## Supported Providers

| Provider | URL Pattern | Method |
|----------|-------------|--------|
| **ChatGPT** | `chatgpt.com/share/*` | Headless Chromium |
| **Gemini** | `gemini.google.com/share/*` | Headless Chromium |
| **Grok** | `grok.com/share/*` | Headless Chromium |
| **Claude** | `claude.ai/share/*` | Your Chrome session |

### Claude.ai Special Handling

Claude.ai uses Cloudflare protection. CSCTF handles this automatically:
1. Copies your Chrome session cookies to a temporary profile
2. Launches Chrome with remote debugging
3. Extracts conversation via Chrome DevTools Protocol

**Requirement:** Chrome installed + logged into claude.ai

---

## Essential Commands

| Flag | Description |
|------|-------------|
| `--outfile <path>` | Override output path |
| `--md-only` | Skip HTML output |
| `--html-only` | Skip Markdown output |
| `--quiet` | Minimal logging |
| `--timeout-ms <ms>` | Navigation timeout (default: 60000) |
| `--publish-to-gh-pages` | Publish to GitHub Pages |
| `--yes` | Skip confirmation prompts |

---

## Output Format

### Markdown

```markdown
# Conversation: <Title>

**Source:** https://chatgpt.com/share/...
**Retrieved:** 2026-01-08T15:30:00Z

## User

How do I sort an array in Python?

## Assistant

Here's how to sort:

```python
my_list.sort()
```
```

### HTML Features

- **Zero JavaScript** — Safe for any hosting
- **Inline CSS** — Light/dark mode via `prefers-color-scheme`
- **Syntax highlighting** — highlight.js themes inline
- **Table of contents** — Auto-generated from headings

---

## Filename Generation

```
"How to Build a REST API"  → how_to_build_a_rest_api.md
"Python Tips & Tricks!"    → python_tips_tricks.md
"File exists already"      → file_exists_already_2.md
```

Rules: lowercase, non-alphanumerics → `_`, max 120 chars, collision suffix

---

## Performance

| Phase | Time |
|-------|------|
| First run (Chromium download) | 30-60s |
| Subsequent runs | 5-15s |
| Claude.ai (uses local Chrome) | 5-10s |

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| "No messages found" | Link is private; verify public share |
| Bot detection | Retry; verify link in browser |
| Timeout | Raise `--timeout-ms 90000` |
| Publish fails (auth) | Ensure `gh auth status` passes |
| Claude.ai Cloudflare | Complete verification in Chrome window |

---

## Installation

```bash
# One-liner
curl -fsSL https://raw.githubusercontent.com/Dicklesworthstone/chat_shared_conversation_to_file/main/install.sh | bash

# Pin version
VERSION=v1.0.0 curl -fsSL .../install.sh | bash

# Verify checksum
curl -fsSL .../install.sh | bash -s -- --verify
```

---

## References

| Topic | Reference |
|-------|-----------|
| Full command reference | [COMMANDS.md](references/COMMANDS.md) |
| Processing algorithms | [ALGORITHMS.md](references/ALGORITHMS.md) |
| GitHub Pages setup | [GITHUB-PAGES.md](references/GITHUB-PAGES.md) |
