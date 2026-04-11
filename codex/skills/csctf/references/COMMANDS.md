# CSCTF Command Reference

## Table of Contents
- [Basic Usage](#basic-usage)
- [Output Options](#output-options)
- [GitHub Pages Publishing](#github-pages-publishing)
- [Environment Variables](#environment-variables)
- [File Locations](#file-locations)

---

## Basic Usage

```bash
csctf <share-url> [options]
```

### Supported URLs

```bash
# ChatGPT
csctf https://chatgpt.com/share/69343092-91ac-800b-996c-7552461b9b70

# Gemini
csctf https://gemini.google.com/share/66d944b0e6b9

# Grok
csctf https://grok.com/share/bGVnYWN5_d5329c61-f497-40b7-9472-c555fa71af9c

# Claude
csctf https://claude.ai/share/549c846d-f6c8-411c-9039-a9a14db376cf
```

---

## Output Options

| Flag | Default | Description |
|------|---------|-------------|
| `--outfile <path>` | auto | Override output path |
| `--no-html` / `--md-only` | off | Skip HTML output |
| `--html-only` | off | Skip Markdown output |
| `--quiet` | off | Minimal logging |
| `--timeout-ms <ms>` | `60000` | Navigation + selector timeout |
| `--check-updates` | — | Print latest release tag |
| `--version` | — | Print version and exit |

---

## GitHub Pages Publishing

| Flag | Default | Description |
|------|---------|-------------|
| `--publish-to-gh-pages` | off | Publish to GitHub Pages |
| `--gh-pages-repo <owner/name>` | `my_shared_conversations` | Target repo |
| `--gh-pages-branch <branch>` | `gh-pages` | Target branch |
| `--gh-pages-dir <dir>` | `csctf` | Subdirectory in repo |
| `--remember` | off | Save GH settings |
| `--forget-gh-pages` | off | Clear saved settings |
| `--dry-run` | off | Simulate publish (build index, no push) |
| `--yes` / `--no-confirm` | off | Skip `PROCEED` confirmation prompt |
| `--gh-install` | off | Auto-install `gh` CLI |

### Publish Flow

1. Resolve repo/branch/dir (use remembered or defaults)
2. Clone (or create via `gh`)
3. Copy MD + HTML files
4. Regenerate `manifest.json` and `index.html`
5. Commit + push
6. Print viewer URL

---

## Environment Variables

### Runtime

| Variable | Description |
|----------|-------------|
| `PLAYWRIGHT_BROWSERS_PATH` | Reuse cached Chromium bundle |

### Installer

| Variable | Description | Default |
|----------|-------------|---------|
| `VERSION` | Pin release tag | latest |
| `DEST` | Install directory | `~/.local/bin` |
| `CHECKSUM_URL` | Override checksum location | — |

---

## File Locations

| Path | Purpose |
|------|---------|
| `~/.local/bin/csctf` | Binary |
| `~/.config/csctf/config.json` | GitHub Pages settings |
| `~/.cache/ms-playwright/` | Playwright Chromium cache |

---

## Recipes

### Quiet CI Scrape (MD only)

```bash
csctf <url> --md-only --quiet --outfile /tmp/chat.md
```

### HTML-only for Embedding

```bash
csctf <url> --html-only --outfile site/chat.html
```

### Slow/Large Conversations

```bash
csctf <url> --timeout-ms 90000
```

### Custom Browser Cache

```bash
PLAYWRIGHT_BROWSERS_PATH=/opt/ms-playwright csctf <url>
```

### Batch Archive

```bash
for url in $URLS; do
  csctf "$url" --outfile ~/archive/ --quiet
done
```

### Quick Recipe (GitHub Pages)

```bash
# Publish with defaults
csctf <url> --publish-to-gh-pages --yes

# Creates: <gh-username>/my_shared_conversations repo
# Branch: gh-pages
# Directory: csctf/
```

### Remembered Settings

```bash
# First time: save settings
csctf <url> --publish-to-gh-pages --remember --yes

# Subsequent: just use --yes
csctf <url> --yes

# Clear remembered settings
csctf --forget-gh-pages
```

### Custom Configuration

```bash
csctf <url> --publish-to-gh-pages \
  --gh-pages-repo myuser/my-chats \
  --gh-pages-branch main \
  --gh-pages-dir exports \
  --yes
```
