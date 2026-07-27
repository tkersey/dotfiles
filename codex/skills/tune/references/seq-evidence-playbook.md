# Seq Evidence for Tune

Use Seq only to reconstruct session evidence. Tune owns classification,
attribution, gap diagnosis, and refinement choice.

## Canonical observation

Historical or multi-session:

```bash
seq observe \
  --definition <tune-skill-root>/definitions/seq/skill-decision-audit.json \
  --projection evidence \
  --root <sessions-root> \
  --last <duration> \
  --param skill=<skill> \
  --format json
```

One watched session:

```bash
seq observe \
  --definition <tune-skill-root>/definitions/seq/skill-decision-audit.json \
  --projection evidence \
  --root <sessions-root> \
  --session-id <session> \
  --param skill=<skill> \
  --format json
```

Use `--repo`, `--since`, or `--until` only when the question requires that
scope. Record the exact selector set. The result envelope supplies definition
identity, corpus identity, selected-session denominator, contamination posture,
limitations, and execution statistics.

## Interpretation

Treat every returned row as candidate evidence:

- distinguish a user activation, assistant declaration, injected skill block,
  skill-file read, decision receipt, route statement, outcome, and raw mention;
- exclude current-audit prompts and quoted contracts from causal counts;
- keep activation, decision influence, and outcome evidence separate;
- use stable `source_event_id`, `session_id`, `path`, `line_number`, and
  `turn_index` as provenance;
- mark causality unknown unless the episode explicitly binds the skill to the
  decision.

Tune authors STE-v1 from the classified evidence. Seq does not author or
validate Tune artifacts.

## Narrow physical follow-ups

Use a native physical command only when the canonical observation identifies a
specific unresolved question:

| Question | Surface |
|---|---|
| Full context for one selected session | `seq session-detail` |
| Exact turn boundaries or state | `seq turns` |
| Tool start/result pairing | `seq tool-lifecycle` |
| Root/worker provenance | `seq session-graph` |
| Physical relation or field discovery | `seq datasets`, `seq dataset-schema` |
| A bounded source-structural relation not yet projected | `seq query` |

Do not recreate retired skill, workflow, message, tool, cohort, or report
commands through ad hoc command chains. When a recurring evidence shape is
missing, change the owning passive observation definition. Request a new Seq
operator only when the capability is domain-independent, bounded, and cannot
be expressed at equivalent performance.

## Artifact boundary

Validate Tune-authored packets through their canonical Ledger definitions:

```bash
ledger validate \
  --definition <tune-skill-root>/definitions/ledger/skill-tuning-evidence.json \
  --input evidence=<ste.json> \
  --format json
```

Structural validity never establishes attribution, usefulness, approval,
publication authority, or completion.
