---
name: synesthesia
description: "Cross-modal diagnostic/review workflow for software systems: map technical signals into sensory models, translate them back into engineering terms, and selectively capture only explicitly endorsed or corrected durable mappings through memory-source-notes. Use for architecture, strange/flaky behavior, performance, readability, API/UX critique, onboarding, or comparisons by feel."
metadata:
  version: "2.0.0"
---

# Synesthesia

## Mission

Use reversible sensory models to surface software structure, then translate every useful observation back into precise engineering implications and action.

The sensory layer is a diagnostic instrument, not evidence and not mandatory output style. For an accepted mapping/boundary admission, load `$memory-source-notes` before invoking `run_memory_note_tool`.

## Core Contract

Always:

1. start from literal evidence: code, tests, logs, architecture, runtime behavior, user flow, or repository structure;
2. use only 2-4 modalities that illuminate the task;
3. keep mappings internally consistent;
4. mark uncertainty;
5. translate every useful metaphor into concrete technical meaning;
6. prefer directness over poetry;
7. execute code changes literally even when the lens informed the decision.

Never treat metaphor as proof, hide uncertainty in aesthetic language, overwrite exact facts with feel, force this framing onto narrow factual tasks, or infer a durable user mapping from an assistant-generated phrase alone.

## Procedure

1. Literal read: extract components, flows, hotspots, failure modes, constraints, and unknowns.
2. Sensory render: choose visual, auditory, spatial, tactile, or thermal models that expose structure.
3. Dissonances: find mismatches between intended design and observed behavior.
4. Engineering translation: state literal interpretation, why it matters, evidence, and change/investigation.
5. Action: end with concrete steps.

## Memory Capture Boundary

Most sensory output must not become memory.

A custom synesthesia source note is allowed only for:

- explicit user endorsement of a mapping;
- explicit correction of a mapping;
- explicit rejection of a mapping;
- explicit durable activation/non-activation boundary;
- repeated accepted operational use across contexts;
- stable repo/task-family vocabulary that changes future diagnosis.

Do not capture one-off poetic phrases, assistant novelty, ambient UI colors or passive Chronicle context, transient incident descriptions, mappings with no concrete engineering translation, or general technical facts better owned by learnings or negative ledger.

## Mapping Admission Gate

Require:

1. `sensory_phrase`;
2. `engineering_translation`;
3. `activation_boundary`;
4. `non_activation_boundary` when relevant;
5. narrow scope;
6. endorsement/correction/rejection authority;
7. evidence reference;
8. verification rule that keeps the mapping reversible.

## Admission Payload

```json
{
  "operation": "assert",
  "authority": "explicit-user-endorsement",
  "summary": "Endorse long corridor as serialized-wait vocabulary.",
  "scope": {
    "kind": "task-family",
    "repo": null,
    "paths": []
  },
  "source_refs": [
    {
      "kind": "user-endorsement",
      "ref": "rollout:019...",
      "summary": "User explicitly accepted and reused the mapping"
    }
  ],
  "related_ids": [],
  "supersedes_id": null,
  "payload": {
    "sensory_phrase": "long corridor",
    "engineering_translation": "serialized waits, chatty calls, or amplified dependency latency",
    "activation_boundary": "performance and dependency-chain diagnosis",
    "non_activation_boundary": "exact syntax or literal-only requests",
    "scope": "task_family_scoped",
    "scope_anchor": "performance-triage",
    "endorsement_type": "explicit-user-endorsement",
    "verification": "Every use names the concrete wait/latency mechanism and evidence"
  }
}
```

Then hand off:

```bash
run_memory_note_tool append \
  --extension synesthesia \
  --kind mapping-endorsement \
  --json -
```

For corrections/rejections use `mapping-correction`, `mapping-rejection`, `activation-boundary`, or `boundary-retraction` and reference the previous note ID when known.

## Proof Lines

```text
memory-note: id=MSN-... extension=synesthesia kind=mapping-endorsement status=created
memory-note: not-attempted: source admission gate not met
memory-note: not-attempted: cli unavailable
```

## Cross-Extension Ownership

- general workflow/operating correction -> harness-memory;
- evidence-backed technical learning -> learnings;
- failed-hypothesis exclusion/reopening -> negative-ledger;
- sensory mapping or activation boundary -> synesthesia.

## Guardrails

- Literal correctness outranks vividness.
- Metaphor never substitutes for tests, profiling, logs, or proof.
- Repo-local vocabulary remains repo-local until broader evidence exists.
- Stable mappings are preferred over novelty.
- Never directly edit compiled memory.
- Never write custom notes without passing the endorsement gate.
