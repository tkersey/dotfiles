# `$retrace` Decision Capsules

`$seq` owns the deterministic source packet for historical inquiry.

Preferred future command:

```bash
seq decision-capsule \
  --session-id <id> \
  --decision-id <decision> \
  --anchor all \
  --format json
```

Output:

```text
decision_context_packet / DCP-v1
```

The capsule must include:

- source session/thread/rollout identity;
- artifact state;
- visible decision episode;
- explicit rationale and assumptions;
- selected/rejected routes actually present;
- skills/instructions/tools present;
- total turn count and decision/outcome indexes;
- exact turns-to-drop for pre-decision and post-decision/pre-outcome horizons;
- contamination and limitations.

`$seq` must not infer hidden rationale or alternatives.

When exact anchoring is unavailable, report that fact rather than creating a prompt-only pseudo-replay.

Implementation requirements are in:

```text
SEQ_DECISION_CAPSULE_CLI_SPEC.md
```
