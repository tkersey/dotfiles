# Verification Gap Report Template

```markdown
## Verification Gap Report

### Intended change
- [Specific behavior changed]

### Scope boundaries
- In scope: [files/components]
- Out of scope: [files/components/behaviors intentionally untouched]

### Preserved invariants
- [Behavior or contract expected to remain unchanged]

### Blast-radius review
- Direct callers checked: [yes/no + details]
- Data/API contracts checked: [yes/no + details]
- Operational surfaces checked: [queues/cache/cron/logs/etc.]

### Tacit-context gaps
- [Unknowns, missing owner knowledge, docs not found, external constraints]

### Verification performed
- [Commands run and results]
- [Tests added/updated]
- [Manual inspections]

### Remaining risk
- [Concrete residual risks]

### Rollout / rollback notes
- [Feature flags, deployment ordering, monitoring, rollback plan if relevant]
```
