# Universalist Subagent Packet Contract

Every Universalist custom subagent returns one compact packet and no user-facing essay.

```text
artifact_state_id: "branch=<name> head=<sha-or-id> diff=<digest-or-path-set> phase=<phase>"
role: "<custom-agent-name>"
scope: "<assigned system, files, seam, or question>"
observations:
  - claim: "<verified observation>"
    evidence_ref: "<file:line, command, trace, or not-inspected>"
candidate:
  summary: "<role-specific candidate or none>"
  artifact: "<certificate/map/model/plan>"
countercase:
  summary: "<strongest challenge>"
  disposition: "defeats | narrows | survives | unresolved"
proof_obligations:
  - "<required check>"
obstructions:
  - "<missing effectivity, evidence, primitive, law, or resource constraint; or none>"
agreement_pressure: "confirms | challenges | narrows | conflicts | none"
stale: false
final_call: "<one-line recommendation>"
```

Rules:

- observations must be evidence-backed;
- proposals are not observations;
- no raw logs or long essays;
- no root-only Echo or user-facing preamble;
- no child delegation;
- read-only roles never mutate;
- implementer and verifier report exact files and commands.
