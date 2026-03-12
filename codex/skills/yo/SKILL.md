---
name: yo
description: Publish provided content to a secret GitHub gist bucket and surface it to a human via a local macOS notification that opens the gist when tapped. Use when Codex needs to show or notify a human with raw text or file content, wants a gist-backed human handoff, or is explicitly invoked as `$yo`. YO accepts inline text or file paths, creates or reuses a repo-scoped secret gist, and notifies through macOS Notification Center.
---

# YO

## Workflow

1. Decide whether the request clearly asks to show or notify a human. If it does not, do not use YO implicitly.
2. Gather the payload as either:
   - inline text
   - a file path whose contents should be published
3. Run the helper:
   - `uv run python codex/skills/yo/scripts/publish_notify.py --text "..."` for inline content
   - `uv run python codex/skills/yo/scripts/publish_notify.py --file path/to/content.md` for file-backed content
   - Add `--title "..."` only when the caller already knows the exact notification title
   - Add `--dry-run` when you need proof without side effects
4. Treat the helper's JSON as the source of truth:
   - `status=delivered`: gist publish + notification succeeded
   - `status=partial`: gist publish succeeded, notification failed after one retry
   - `status=dry_run`: no side effects; inspect `repo_label`, `file_name`, `preview`, and `bucket_action`
   - `status=dropped`: GitHub gist capability was unavailable; do not fall back to notification-only delivery
   - `status=failed`: invalid input, non-macOS execution, gist mutation failure, or another visible error

## Output Contract

- Publish into a secret gist only. Never use public gist mode.
- Reuse a stable gist bucket per repo label:
  - `origin` remote first
  - first remote second
  - `no-repo` when no parseable remote exists
- Keep one markdown file per delivery inside that bucket.
- Preserve the original body verbatim below the helper's minimal metadata header.
- Include the literal gist URL in the notification body.
- Open the gist when the human taps the notification.
- Stay silent by default. Do not add sound.
- Fail closed on non-macOS platforms.
- If GitHub auth or `gist` scope is unavailable, accept the helper's `dropped` result and stop quietly instead of inventing a fallback.
- If `terminal-notifier` is unavailable, fail visibly instead of falling back to a non-clickable notifier.

## Constraints

- Use only `gh` plus `terminal-notifier` for live behavior.
- Do not rewrite, summarize, or polish the payload.
- Do not trigger from generic escalation or handoff language alone; the request must clearly aim to show or notify a human.

## Examples

- `Use $yo to send this handoff note to the human.`
- `Show this markdown to a human with a local macOS notification.`
- `Notify the human locally and include a gist link for this release summary.`
