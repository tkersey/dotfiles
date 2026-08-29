# Specification Governance

The default Plan route treats a supplied implementation specification as a candidate
to govern before architecture-policy synthesis. The purpose is to preserve the
candidate's useful decisions while refusing unsupported authority, drift, hidden
architecture, and proof-shaped omissions.

## Candidate and authority

Bind these sources before editing the candidate:

```text
user objective and explicit decisions
repository and artifact state
existing public and compatibility contracts
tests, schemas, migrations, operational evidence, and proof topology
candidate specification
prior governed plan when revising
```

The candidate does not outrank the user or repository. It may propose decisions, but
a decision becomes source authority only when accepted by the user, entailed by
inspected artifacts, or necessary inside an explicitly delegated specification-local
seam.

## Evidence Brief

For `full` or materially reconstructed work, emit:

```text
## Evidence Brief
- Current state:
- Relevant surfaces:
- Existing behavior:
- Known constraints:
- Obvious risks:
- Proof surfaces already available:
- Facts not yet verified:
- Judgment calls still needed:
```

Use `none` only after considering the field. Evidence may be concise when the
candidate and repository already make the answer obvious.

## Judgment acquisition

Ask 1-3 bounded questions per round only when a material user judgment remains.
Each question must be atomic, have a stable `snake_case` ID, place the recommended
option first when justified, and avoid discoverable facts.

When no question is needed, preserve internally:

```yaml
no_grill_justification:
  reasons: []
  material_unknowns_remaining: false
  defaulted_decisions: {}
```

A default is not a locked user decision. Record its owner, consequence, and
invalidator.

## Anti-drift check

Before compiling or repairing the specification, compare against the authoritative
objective:

```text
target
scope and non-goals
authority boundary
compatibility posture
proof bar
rollout and rollback posture
public behavior boundary
source-fixed architecture and abstraction constraints
```

Unapproved change to one of these blocks with a concrete drift statement. Do not
normalize drift into a new accepted objective.

## Candidate disposition

Choose one:

```text
adopt
  candidate is decision-complete, current, and source-consistent

repair
  one or more bounded sections or seams are invalid or incomplete

reconstruct
  governing factorization, authority, scope, or proof basis is materially unsound

block
  unavailable judgment or authority prevents an honest specification
```

`adopt` still runs the invariant challenge and fresh-eyes pass. `repair` changes only
implicated sections and all downstream derivations. `reconstruct` preserves valid
source decisions and evidence; it does not preserve the candidate's organization
merely because prose already exists.

## Decision completeness

Before implementation-spec compilation, establish:

```text
goal and target maintainer/user
scope and non-goals
locked decisions and accepted tradeoffs
primary invariant and success criteria
proof bar
compatibility posture
rollout and rollback posture
architectonic authority and seam dispositions
conceptual-compression constraints
downstream-open decisions
open, deferred, and defaulted items
```

For every material open question record:

```text
stable ID
question
owner
default or blocker
consequence
why it is non-blocking, when applicable
invalidator
```

For every downstream-open architectonic decision record:

```text
admissible candidate space
required deciding observations
forbidden outcomes
safe default or blocker
invalidators
```

An open design choice without that envelope is not decision-complete.

## Semantic readiness gate

Complete this sentence from governed facts:

```text
We are building X, for Y, by changing Z, while explicitly not doing A/B/C,
under architectonic constraints D/E, and success means P/Q/R proofs pass.
```

Planning may continue only when:

```text
authoritative objective is present and current
material user judgments are resolved or honestly blocked
scope, non-goals, compatibility, and proof bar are explicit
all consequential seams have lawful dispositions
implementation sequence derives from those dispositions
no source-fixed contradiction remains
rollback and binary done-state are testable
```

This is a semantic compiler condition, not a persisted gate or receipt.

## Implementation specification

Use these sections in order:

1. Objective
2. Context / Current State
3. Locked Decisions
4. Scope
5. Non-Goals
6. Requirements
7. Architecture and Abstraction
8. Design / Implementation Approach
9. Dependency-Ordered Implementation Sequence
10. Requirement-Owner-Enforcement-Proof Traceability
11. Proof Commands
12. Risks and Edge Cases
13. Rollback / Abort Criteria
14. Binary Done-State
15. Open / Deferred Items

`Architecture and Abstraction` carries the Architectonic Thread: seam authority,
incumbent organization, ordinary and alternative candidates, selected or conditioned
organization, canonical owners, factor dispositions, laws, falsifiers, residuals,
and invalidators.

Every downstream section derives through:

```text
requirement
-> semantic owner
-> architectural factor
-> enforcement locus
-> implementation surface
-> proof
-> invalidator
```

Each sequence item says whether it establishes, transports, migrates, retires,
proves, or removes a bypass for a factor. A sequence that realizes a quotiented,
ablated, normalized, or superseded factor is inconsistent and must be regenerated.

Keep the sequence at specification level. Do not emit EPG action rows, policy
branches, commitment horizons, or execution-wave ceremony in this phase.

## Stop conditions

Block before EPG synthesis when:

```text
material user judgment is unavailable
source authority conflicts
objective drift remains
consequential seam is obstructed
proof bar cannot be made operational
compatibility or rollback consequence is unowned
```

A blocked default route reports the exact missing authority or observation. It does
not emit a partial EPG that certifies its own readiness.
