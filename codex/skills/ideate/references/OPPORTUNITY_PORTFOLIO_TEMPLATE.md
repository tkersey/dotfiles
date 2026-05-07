# Opportunity Portfolio Template

Use this output shape for the final artifact before the plan seed.

```md
# Codebase Opportunity Portfolio

## 1. Compressed repo snapshot

- Scope:
- Repo shape:
- Primary user-facing surfaces:
- Primary maintainer surfaces:
- Important constraints:
- Signal sources inspected:
- Assumptions / blind spots:

## 2. Opportunity map

Group the strongest evidence signals by theme.

### Theme: <name>

- Evidence:
- Observation:
- Opportunity implied:
- Confidence:

## 3. Top 5 ideas

### 1. <idea title>

- Category:
- Evidence:
- Originality source:
- User / maintainer benefit:
- Why this beats alternatives:
- Why this is not generic:
- Validation path:
- Risks / behavior-change concerns:
- Overlap status:

### 2. <idea title>

...

## 4. Next 10 ideas

Use shorter cards, but keep evidence.

1. **<idea title>** — Category; evidence; originality source; benefit; validation path; overlap status.
2. ...

## 5. Ideas cut

Briefly list the most tempting rejected ideas and why they lost.

- **<cut idea>** — Cut because ...

## 6. Overlap findings

- Direct duplicates:
- Adjacent / merge mentally:
- Conflicts:
- Net-new:
- Unknown due to thin evidence:

## 7. Chosen direction

Name the leading direction and explain why it won.

## 8. Plan seed

Use `PLAN_SEED_TEMPLATE.md`.
```

## Notes

- Keep the portfolio useful, not exhaustive.
- Do not expose all 30 raw candidates unless the user explicitly asks.
- Cite file paths, symbols, tests, commands, or docs for evidence.
- Be clear when an idea is promising but evidence is thin.
- The plan seed should focus on the chosen direction, not the full portfolio.
