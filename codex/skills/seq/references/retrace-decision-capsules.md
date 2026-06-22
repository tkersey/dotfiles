# `$retrace` Source and Decision Capsules

`$seq` owns deterministic source selection.

For a workflow-specific replay:

```text
1. run the native workflow audit;
2. select the exact included-session row;
3. classify governance and closure provenance;
4. produce SGG-v1;
5. locate the visible route decision;
6. produce DCP-v2.
```

Do not use aggregate counts or transcript similarity to select the source.

When automatic decisions are absent:

```bash
seq turns --session-id <id> --format table
seq session-detail --session-id <id> --format markdown
seq decision-capsule \
  --session-id <id> \
  --turn-index <n> \
  --anchor all \
  --outcome-policy conservative \
  --format json
```

DCP must include source thread or rollout identity, turn digest, artifact reconstructability, and exact temporal anchors.

`$seq` does not ask a model to infer hidden rationale.
