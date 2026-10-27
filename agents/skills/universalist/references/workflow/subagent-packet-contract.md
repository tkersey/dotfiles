# Universalist Subagent Packet Contract

Every Universalist custom subagent returns one compact packet and no
user-facing essay.

```text
artifact_state_id: "branch=<name> head=<sha-or-id> diff=<digest-or-path-set> phase=<phase>"
role: "<custom-agent-name>"
scope:
  boundary: "<owned seam or bounded task-grounded question>"
  axis: "<evidenced axis, provisional hypothesis, or not-yet-identified>"
  typed_hole: "<compatible hole, provisional hypothesis, not-yet-identified, or not-applicable>"
observations:
  - claim: "<verified observation>"
    evidence_ref: "<inspected file:line, executed command, or observed trace>"
candidate:
  summary: "<role-specific candidate or none>"
  repository_native_artifact: "<artifact or none>"
  current_encoding_relation: "<material correspondence, scope, law strength, and placement; or not-material>"
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
  - "<required check, unresolved evidence, and next discriminator>"
residual_obligations:
  - "<requirement + owner + check time; or none>"
invalidators:
  - "<proof-lease invalidator; or none>"
resource_bound: "<effective bound or unresolved>"
obstructions:
  - "<claim-scoped impossibility argument with witness and reopening condition; or none>"
agreement_pressure: "confirms | challenges | narrows | conflicts | none"
stale: false
final_call: "<one-line recommendation>"
```

Rules:

- observations are evidence-backed; proposals and uninspected claims are not observations;
- `candidate` describes the actual construction, including composite or unregistered
  constructions. Use `card_dispositions: []` when no card is used; never invent a
  card to fill the packet. Catalogue membership changes neither acceptance nor proof;
- missing evidence or authority belongs in `proof_obligations` or owned
  `residual_obligations` and the unresolved recommendation, not `obstructions`.
  The entrypoint owns evidence states and claim-scoped obstruction requirements;
- one packet covers one bounded question; axis and typed hole may be derived or
  revised during inquiry rather than supplied as admission prerequisites;
- distinguish provisional scope from evidenced conclusions; do not invent an
  incumbent, axis, or hole to fill the packet;
- split independently governed axes once identified and preserve their interactions;
- a category name never substitutes for encoding relation or discriminator;
- no raw logs, transcript dumps, or long essays;
- no root-only Echo or user-facing preamble;
- no child delegation;
- read-only roles never mutate;
- child agents never select a route, grant mutation, or emit a root receipt;
- implementer and verifier report exact files, commands, and artifact state.
