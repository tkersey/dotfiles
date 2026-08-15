# Universalist Subagent Packet Contract

Every Universalist custom subagent returns one compact packet and no
user-facing essay.

```text
artifact_state_id: "branch=<name> head=<sha-or-id> diff=<digest-or-path-set> phase=<phase>"
role: "<custom-agent-name>"
scope:
  boundary: "<owned seam>"
  axis: "<one architectural axis>"
  typed_hole: "<one compatible hole>"
observations:
  - claim: "<verified observation>"
    evidence_ref: "<file:line, command, trace, or not-inspected>"
candidate:
  summary: "<role-specific candidate or none>"
  repository_native_artifact: "<artifact or none>"
  current_encoding_relation: "<relation or not-material>"
  nearest_false_friend: "<candidate or not-material>"
  discriminating_law: "<law/counterexample or not-material>"
  generalization_dividend: "<material delta or none>"
  transition_witness: "<bounded transition or not-material>"
card_dispositions:
  - card: "<card id>"
    disposition: "selected | rejected | contradicted | unresolved"
    evidence_ref: "<evidence>"
countercase:
  summary: "<strongest ordinary or neighboring challenge>"
  disposition: "defeats | narrows | survives | unresolved"
proof_obligations:
  - "<required check>"
residual_obligations:
  - "<requirement + owner + check time; or none>"
invalidators:
  - "<proof-lease invalidator; or none>"
resource_bound: "<effective bound or unresolved>"
obstructions:
  - "<missing effectivity, evidence, primitive, law, or resource constraint; or none>"
agreement_pressure: "confirms | challenges | narrows | conflicts | none"
stale: false
final_call: "<one-line recommendation>"
```

Rules:

- observations are evidence-backed; proposals are not observations;
- one packet covers one axis and one typed hole;
- a category name never substitutes for encoding relation or discriminator;
- no raw logs, transcript dumps, or long essays;
- no root-only Echo or user-facing preamble;
- no child delegation;
- read-only roles never mutate;
- child agents never select a route, grant mutation, or emit a root receipt;
- implementer and verifier report exact files, commands, and artifact state.
