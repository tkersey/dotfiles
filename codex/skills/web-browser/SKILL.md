---
name: web-browser
description: Use when you need to browse the web or automate Chrome/Chromium via CDP (navigate/open/go to, click/press, fill/type forms, evaluate JS, take screenshots, or scrape/extract page content).
---

# Web Browser Skill

## When to use
- Navigate or interact with live websites
- Click buttons, fill forms, or extract page content
- Evaluate JS in a real browser context
- Capture screenshots for review or debugging

## Quick start
```bash
# Start Chrome with remote debugging on :9222
./tools/start.js

# Navigate or open a new tab
./tools/nav.js https://example.com
./tools/nav.js https://example.com --new
```
Workflow loop: take small steps → inspect state with `eval.js` or `screenshot.js` → repeat. Favor quick state checks over long, brittle scripts.

## Common commands
```bash
# Start with your existing profile (cookies, logins)
./tools/start.js --profile

# Evaluate JS in the active tab
./tools/eval.js 'document.title'
./tools/eval.js 'document.querySelectorAll("a").length'

# Screenshot current viewport
./tools/screenshot.js

# Pick elements interactively
./tools/pick.js "Click the submit button"
```
Discovery tip: use `pick.js` to identify elements and confirm selectors; then run `eval.js` to click/type with those selectors.

## Pitfalls / gotchas
- Chrome must be running with remote debugging enabled on `:9222`.
- `--profile` copies your profile; use only when you need existing cookies/logins.
- Use single quotes around JS to avoid shell-escaping issues.
- `./tools/start.js` kills all running Chrome processes and uses a macOS Chrome path; close Chrome first or edit the script for your OS.

## References
- `codex/skills/web-browser/tools/start.js`
- `codex/skills/web-browser/tools/nav.js`
- `codex/skills/web-browser/tools/eval.js`
- `codex/skills/web-browser/tools/screenshot.js`
- `codex/skills/web-browser/tools/pick.js`
