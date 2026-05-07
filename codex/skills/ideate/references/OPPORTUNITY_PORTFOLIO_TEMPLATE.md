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

## 3. Escalation ledger

Show how the mandatory Glaze and ASI gates changed the portfolio. Keep this compact but specific.

### Chosen direction escalation chain

- Baseline idea:
- Why the obvious version loses:
- Glaze material delta:
- Stronger move:
- ASI 10x frame:
- Systemic leverage point:
- Smallest proof-bearing artifact:
- Cash-out type: Mechanism | Interface | Proof surface | Strategy
- First proof signal:
- Evidence anchor:

### Other high-signal escalations

1. **<idea title>** — baseline → Glaze delta → ASI artifact → result: promoted | kept | demoted | cut.
2. ...

## 4. Top 5 breakthrough ideas

### 1. <idea title>

- Category:
- Evidence:
- Originality source:
- User / maintainer benefit:
- Why this beats alternatives:
- Why this is not generic:
- Glaze material delta:
- ASI 10x frame:
- Smallest proof-bearing artifact:
- Cash-out type:
- First proof signal:
- Validation path:
- Risks / behavior-change concerns:
- Overlap status:

### 2. <idea title>

...

## 5. Next 10 ideas

Use shorter cards, but keep evidence and escalation status.

1. **<idea title>** — Category; evidence; originality source; benefit; escalation status; validation path; overlap status.
2. ...

## 6. Ideas cut

Briefly list the most tempting rejected ideas and why they lost. Include escalation failures.

- **<cut idea>** — Cut because ...
- **<cut idea>** — Glaze failed: no material delta.
- **<cut idea>** — ASI failed: no proof-bearing artifact.

## 7. Overlap findings

- Direct duplicates:
- Adjacent / merge mentally:
- Conflicts:
- Net-new:
- Unknown due to thin evidence:

## 8. Chosen direction

Name the leading direction and explain why it won after ordinary scoring, Glaze, ASI, and overlap checks.

## 9. Plan seed

Use `PLAN_SEED_TEMPLATE.md`.
```

## Notes

- Keep the portfolio useful, not exhaustive.
- Do not expose all 30 raw candidates unless the user explicitly asks.
- Cite file paths, symbols, tests, commands, or docs for evidence.
- Be clear when an idea is promising but evidence is thin.
- Be clear when an idea is strong but not actually breakthrough.
- The escalation ledger should prove the gates were used without turning the answer into process theater.
- The plan seed should focus on the chosen direction, not the full portfolio.
