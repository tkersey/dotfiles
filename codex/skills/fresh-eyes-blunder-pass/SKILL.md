---
name: fresh-eyes-blunder-pass
description: "Run a targeted fresh-eyes blunder pass over code, specs, plans, adjudications, closure gates, skill edits, or negative-evidence ledgers. Trigger when asked to reread with fresh eyes, find obvious bugs, catch mistakes/oversights/omissions, check for embarrassing misses, or perform a second independent blunder pass before closure. Do not use as a substitute for implementation, adjudication, or verification; use it as the final falsification/check pass for those workflows."
---

# Fresh-Eyes Blunder Pass

Use this as a reusable second-pass falsifier. The pass objective is to reread the current artifact set as if another agent produced it, treating prior confidence as untrusted.

## Modes

- `implementation`: new code, modified code, neighboring unchanged code, tests, imports, callsites, and invariants.
- `closure`: handoff packet, closure gates, verification evidence, negative-evidence gate, readiness claim, and reopen trigger.
- `adjudication`: `act`, `address`, `validate-only`, severity, direction, mutation approval, authority clearances, and handoff agenda rows.
- `spec`: authoritative brief, Evidence Brief, Gate Result, decision packet, proof bar, rollback, non-goals, requirement-to-test traceability, and execution handoff.
- `plan`: convergence claim, owners, dates, rollback, requirements, proof, scope, and execution order.
- `skill-edit`: trigger description, companion boundaries, validation requirements, stale paths, duplicate sections, false activation, and missed activation.
- `negative-evidence`: active exclusions, stale/reopened candidates, evidence anchors, applicability, overbroad bans, and reopening criteria.

## Universal prompt

> Carefully reread the artifact set with fresh eyes, looking for blunders, mistakes, errors, oversights, omissions, misconceptions, bugs, confusion, stale assumptions, scope creep, missing proof, and anything that would be embarrassing if it reached the user unchanged.

## Required result

Return:

```yaml
fresh_eyes_pass:
  mode: implementation | closure | adjudication | spec | plan | skill-edit | negative-evidence
  artifact_state_id: "..."
  checked_surfaces: []
  material_delta: yes | no
  findings: []
  fixes_or_required_updates: []
  verification_to_rerun: []
  fresh_eyes_delta: "none | summary"
```

If the pass changes the artifact, rerun the narrowest credible verification owned by the parent workflow. If it finds no material issue, report `fresh_eyes_delta: none` rather than inventing low-value findings.
