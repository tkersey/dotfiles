# Workflow Trace

Every final answer must include this section:

```text
## Workflow Trace
| Phase | Skill | Status | Reason | Output artifact | Handoff |
|---|---|---|---|---|---|
| 1 | $latent-diver | invoked | ... | Latent Frame Set | to $creative-problem-solver |
| 2 | $creative-problem-solver | invoked | ... | Five-Tier Portfolio | to $accretive |
| 3 | $accretive | invoked | ... | Candidate Compression + Nominee | to $dominance |
| 4 | $dominance | invoked | ... | Dominance Verdict | to Dominant Move Brief |
```

Allowed `Status` values:

- `invoked`
- `emulated`
- `skipped`
- `unavailable`
- `failed`

If `emulated`, say why explicit nested skill invocation was unavailable.
If `skipped`, say which prior artifact allowed the skip.
If `unavailable` or `failed`, say whether the phase could be contract-emulated.
