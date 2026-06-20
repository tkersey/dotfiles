---
name: harness-memory
description: "Capture durable, evidence-backed corrections and steering about how Codex should operate, then hand accepted rules to memory-source-notes for append-only harness admission. Use for explicit durable operating corrections, repeated harness rules, verification gates, stop rules, or escalation rules."
metadata:
  version: "1.0.0"
---

# Harness Memory

## Mission

Turn durable operating corrections into precise future behavior rules without preserving scolding, tone, or one-off task chronology.

This skill owns the admission decision for:

```text
~/.codex/memories/extensions/harness/notes/*.md
```

It delegates the actual append to `$memory-source-notes`. Load that companion skill before running `run_memory_note_tool`; it owns CLI discovery, validation, and proof-line behavior.

## Trigger Cues

- explicit `$harness-memory`;
- "remember this operating rule";
- "from now on, when X, do Y";
- direct correction about search, planning, editing, verification, delegation, approvals, scope, or output behavior;
- repeated steering that reliably prevented retries or user interruption;
- a stable stop rule, escalation rule, source-of-truth rule, or verification gate.

Do not trigger for frustration without a reusable rule, artifact-local content corrections, transient branch/task/session state, or assistant-authored advice the user did not adopt.

## Admission Gate

Require all of:

1. `harness_rule`: one concise operating rule.
2. `trigger`: a recognizable future situation.
3. `preferred_behavior`: what Codex should do.
4. `failure_avoided`: predictable cost or correction prevented.
5. `verification_cue`: observable proof or stop condition.
6. `scope`: global, repo, path-family, task-family, workflow, or tool.
7. `authority`: explicit correction, repeated steering, or verified outcome.
8. `decision_delta`: a future agent would behave differently.

At least one must also hold:

- the user explicitly says the rule should persist;
- the same correction recurs;
- one high-impact correction exposes a clearly reusable default;
- the rule would save substantial user steering or prevent a recurrent failure.

If the gate fails, do not create a note.

## Normalization

Prefer:

```text
When <trigger>, do <preferred behavior> before/without <bad route>; verify with <cue>.
```

Avoid generic instructions such as "be careful", "research more", or "listen to the user" unless they are transformed into a concrete trigger, behavior, and verification cue.

## Capture Workflow

1. Quote or identify the concrete correction/evidence.
2. Separate the operational rule from emotion and task-local details.
3. Decide the narrowest reusable scope.
4. Search recent harness notes when needed:

   ```bash
   run_memory_note_tool list --extension harness
   ```

5. Build a bounded input object with `operation`, `authority`, `summary`, `scope`, `source_refs`, and a harness payload.
6. Hand off:

   ```bash
   run_memory_note_tool append \
     --extension harness \
     --kind harness-rule \
     --json -
   ```

7. Emit the memory-note proof line.

## Confirm, Supersede, Retract

- `confirm`: the rule remains the same and new evidence raises confidence.
- `supersede`: a newer rule is more precise or changes scope.
- `retract`: the user rejects the rule or evidence shows it should not persist.

Never edit an old note. Reference it from the new event.

## Relationship to AGENTS.md

`AGENTS.md` remains the high-authority standing policy. Harness notes are evidence for Phase 2 to compile user-specific defaults and routing cues. Do not let compiled memory duplicate long policy text.

## Proof Lines

```text
memory-note: id=MSN-... extension=harness kind=harness-rule status=created
memory-note: duplicate-skip: extension=harness fingerprint=...
memory-note: not-attempted: source admission gate not met
memory-note: not-attempted: cli unavailable
```

## Guardrails

- One correction is not automatically a global preference.
- Do not store scolding or frustration.
- Do not infer a rule from passive Chronicle context alone.
- Do not use a harness rule to bypass user approval or side-effect boundaries.
- Do not directly edit compiled memory.
- Do not write into `ad_hoc` or Chronicle.
