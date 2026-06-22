# Command Routing

```text
skill influence             skill-decision-audit
skill presence              skill-evidence
activation counts           skill-audit
successful ranking          skill-success-rank
workflow cohort             workflow-audit
historical decision         decision-capsule / historical_decisions
review compiler             review-compiler-audit
resolve churn               resolve-churn-audit
raw artifact search         artifact-search
plan artifact               plan-search
session narrative           turns / session-prompts / session-detail
tools                       tool-lifecycle / tool-audit / tool-search
workers                     session-graph / orchestration-concurrency
memory inventory            memory-inventory
memory provenance           memory-provenance
generic relation            query
query failure               query-diagnose
```

For `$retrace` workflow sources:

```text
review-compiler-audit included row
-> provenance classification
-> SGG-v1
-> decision-capsule
```
