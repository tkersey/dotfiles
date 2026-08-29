# Specification Challenge

Run exactly one strongest project-specific challenge tied to the primary invariant
after the candidate specification is complete and before policy synthesis.

Valid outcomes:

```text
pass
changed_architecture
changed_proof
changed_scope
changed_risk
preference_only
```

When architecture is consequential, attack the governing organization rather than a
local implementation choice. Consider the strongest applicable question:

```text
Does the ordinary candidate already satisfy the law?
Could restricting the admitted domain remove the complexity?
Would a stronger representation or owner eliminate downstream validation?
Is truth duplicated across owners or encodings?
Does the design forget information that later work reconstructs?
Does every retained abstraction own a distinct live obligation?
Can observationally indistinguishable factors be quotiented?
Does migration preserve observations and retire old factors?
Does the specification square commute under the declared equivalence?
```

Record internally:

```text
primary invariant
strongest challenge
affected sections
classification
required change
whether governed specification must be regenerated
```

A material result revises only affected specification sections and every downstream
derivation. A `changed_architecture` result names the affected seam and regenerates
implementation approach, sequence, ownership, migration, rollback, proof, and done
state derived from it.

Challenge independence is valuable; broad review churn is not.
