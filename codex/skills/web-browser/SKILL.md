---
name: web-browser
description: "Automate Chrome/Chromium via CDP: navigate, click, fill forms, evaluate JS, screenshot, scrape."
---

# Web Browser

## When to use
- Navigate or interact with live websites.
- Click buttons, fill forms, or extract page content.
- Evaluate JavaScript in a real browser context.
- Capture screenshots for debugging or review.

## Quick start
```bash
# Start Chrome with remote debugging on :9222
./tools/start.js

# Navigate (optionally open a new tab)
./tools/nav.js https://example.com
./tools/nav.js https://example.com --new
```

Loop: take small steps → inspect state (`eval.js` / `screenshot.js`) → repeat.

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

Tip: use `pick.js` to confirm selectors, then drive actions via `eval.js`.

## Pitfalls
- Chrome must be running with remote debugging enabled on `:9222`.
- `--profile` copies your profile; use only when you need existing cookies/logins.
- Use single quotes around JS to avoid shell-escaping issues.
- `./tools/start.js` kills running Chrome processes and uses a macOS Chrome path; close Chrome first or adapt for your OS.

## References
- `codex/skills/web-browser/tools/start.js`
- `codex/skills/web-browser/tools/nav.js`
- `codex/skills/web-browser/tools/eval.js`
- `codex/skills/web-browser/tools/screenshot.js`
- `codex/skills/web-browser/tools/pick.js`
