# Classification Rules

## Purpose

Map unreleased commits into two buckets only:
- `feature`
- `notable_improvement`

Anything else is excluded.

## Source Priority

1. Pull request title (when commit message includes `(#NNNNN)` and PR lookup succeeds).
2. Commit subject line.

Use combined text from both for keyword matching.

## Include as `feature`

Include when text has clear feature intent, for example:
- `feat`
- `feature`
- `add` / `added`
- `support`
- `enable`
- `introduce`
- `new`
- `allow`
- `expand`
- `promote` (when behavior expands capability)

## Include as `notable_improvement`

Include when text signals meaningful user-impacting improvements, for example:
- reliability/stability
- performance/latency/startup speed
- crash/hang prevention
- accessibility
- major UX quality upgrades
- hardening/security/sandbox correctness

## Exclude by default

Exclude when text is clearly maintenance-only and lacks user-impact signals, for example:
- `chore`
- `docs`
- `test`
- `ci`
- `build`
- `style`
- `refactor`
- `nit`

## Tie-breakers

- Prefer conventional-commit prefixes (`feat:`, `fix:`) over generic noun mentions.
- Use whole-word matching for keywords; do not classify from substring hits like `features` in unrelated maintenance titles.
- If both `feature` and `notable_improvement` match, classify as `feature`.
- If only weak tokens match and user impact is unclear, exclude.
- Keep behavior deterministic: prefer explicit keywords over subjective interpretation.
