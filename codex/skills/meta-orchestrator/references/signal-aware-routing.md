# Signal-aware routing reference

Use these signals together, not in isolation.

## Invariants
- critical + broken -> material; remediation required
- critical + unknown -> material validation gap unless bounded by direct evidence
- critical + strained -> material unless the strain is explicitly temporary, bounded, and verified
- major + broken -> material
- supporting + broken -> material when blast radius is module-wide, cross-cutting, user-facing, persistence-affecting, or safety-affecting

## Foot-guns
Escalate to material when:
- impact is meaningful and misuse is easy
- detectability is subtle or silent
- the hazard sits on a public API, default path, retry path, rollback path, migration path, or operational path
- the hazard could create a false sense of safety because happy-path tests still pass

## Complexity
Escalate to material when:
- the delta increases incidental complexity rather than essential complexity
- the increase is cross-cutting
- the increase creates fragility, coupling, operational burden, or hides future hazards
- the increase weakens reviewability or testability

## Verification
Escalate to material when:
- the changed behavior was not directly checked
- the claimed failure mechanism was not exercised
- a plausible regression surface remains untested
- a critical invariant lacks direct supporting evidence
