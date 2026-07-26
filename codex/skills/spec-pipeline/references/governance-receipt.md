# SGR-v2

`spec_governance_receipt` is the canonical JSON artifact for current-spec work.

It contains:

- mode/profile/lane/status;
- authoritative-brief state;
- phase presence;
- gate impact;
- challenge impact;
- fresh-eyes impact;
- subagent accounting;
- plan/mutation authority;
- retro trigger.

The exact final object must be structurally valid under
`spec-pipeline/spec-governance-receipt@<definition-digest>`. Ledger owns the
structural decision only. Spec Pipeline owns every semantic value and any planning
or mutation authority encoded by the receipt.

A full implementation handoff without one exact, structurally valid SGR-v2 is
invalid. Do not emit a companion receipt that duplicates it.
