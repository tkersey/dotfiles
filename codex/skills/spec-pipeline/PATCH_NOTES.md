# Patch Notes

Version: `2.2.0`

Adds a fail-closed lane-selection correction and an explicit `$plan` source
contract seam.

Key correction:

```text
explicit $spec-pipeline invocation
!= spec_only request
```

In `full` mode, default to `lane=spec_to_plan` unless the user explicitly asks
for spec-only/no-plan output or a material gate blocks planning. A successful,
plan-ready SGR-v2 must tail-call `$plan` or emit `AUTO_PLAN_HANDOFF_REQUIRED` if
same-turn loading is unavailable.

Adds:

- `references/cli-specs/01-lane-selection.md`
- `references/cli-specs/02-auto-plan-tail-call.md`
- `references/lane-selection.md`
- `references/auto-plan-tail-call.md`
- `tools/spec_lane_selection_gate.py`
- `tools/auto_plan_handoff_gate.py`
- good/bad SGR-v2 fixtures
