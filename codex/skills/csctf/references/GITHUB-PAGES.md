# GitHub Pages Publishing

## Table of Contents
- [Quick Start](#quick-start)
- [Requirements](#requirements)
- [Configuration Options](#configuration-options)
- [Publish Flow](#publish-flow)
- [Remembered Settings](#remembered-settings)

---

## Quick Start

```bash
# Publish with defaults (creates repo if needed)
csctf <url> --publish-to-gh-pages --yes

# Creates: <gh-username>/my_shared_conversations repo
# Branch: gh-pages
# Directory: csctf/
```

---

## Requirements

- GitHub CLI (`gh`) installed and authenticated
- Verify with: `gh auth status`

### Install GitHub CLI

```bash
# If not installed, csctf can install it
csctf <url> --publish-to-gh-pages --gh-install --yes

# Or install manually
# macOS
brew install gh

# Ubuntu/Debian
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update && sudo apt install gh

# Then authenticate
gh auth login
```

---

## Configuration Options

| Flag | Default | Description |
|------|---------|-------------|
| `--publish-to-gh-pages` | off | Enable publishing |
| `--gh-pages-repo <owner/name>` | `my_shared_conversations` | Target repo |
| `--gh-pages-branch <branch>` | `gh-pages` | Target branch |
| `--gh-pages-dir <dir>` | `csctf` | Subdirectory in repo |
| `--remember` | off | Save settings for future use |
| `--forget-gh-pages` | off | Clear saved settings |
| `--dry-run` | off | Simulate (build index, no push) |
| `--yes` / `--no-confirm` | off | Skip confirmation prompt |

---

## Publish Flow

1. **Resolve settings** — Use remembered, CLI flags, or defaults
2. **Clone/create repo** — Via `gh repo clone` or `gh repo create`
3. **Copy files** — MD + HTML to target directory
4. **Regenerate index** — `manifest.json` and `index.html`
5. **Commit + push** — Automatic commit with conversation title
6. **Print URL** — Viewer URL for the published page

---

## Remembered Settings

Save your preferences once, use them forever:

```bash
# First time: save settings
csctf <url> --publish-to-gh-pages --remember --yes

# Subsequent: just use --yes
csctf <url> --yes
```

### Clear Remembered Settings

```bash
csctf --forget-gh-pages
```

### Settings Location

`~/.config/csctf/config.json`

---

## Custom Configuration

### Different Repo

```bash
csctf <url> --publish-to-gh-pages \
  --gh-pages-repo myuser/my-chats \
  --yes
```

### Different Branch

```bash
csctf <url> --publish-to-gh-pages \
  --gh-pages-branch main \
  --yes
```

### Different Directory

```bash
csctf <url> --publish-to-gh-pages \
  --gh-pages-dir exports \
  --yes
```

### All Custom

```bash
csctf <url> --publish-to-gh-pages \
  --gh-pages-repo myuser/my-chats \
  --gh-pages-branch main \
  --gh-pages-dir exports \
  --remember \
  --yes
```

---

## Dry Run

Preview what would happen without actually pushing:

```bash
csctf <url> --publish-to-gh-pages --dry-run
```

Builds the index and shows the operations, but doesn't commit or push.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Publish fails (auth) | Run `gh auth status`, re-authenticate if needed |
| Repo doesn't exist | csctf creates it automatically with `--yes` |
| Branch doesn't exist | csctf creates it automatically |
| Permission denied | Check repo permissions in GitHub settings |

---

## Output Structure

After publishing, your repo will have:

```
csctf/
├── index.html           # Auto-generated index page
├── manifest.json        # List of all conversations
├── conversation_1.md    # Markdown version
├── conversation_1.html  # HTML version
├── conversation_2.md
├── conversation_2.html
└── ...
```

The index.html provides a browsable list of all published conversations.
