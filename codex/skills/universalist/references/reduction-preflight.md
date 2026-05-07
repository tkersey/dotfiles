# Reduction preflight for Universalist

Run this before choosing a higher construction. The goal is not to avoid abstraction; the goal is to make only abstractions that delete more obligation than they add.

## Required questions

1. **What tax does the proposed construction add?**
   - new files
   - new names
   - new wrappers
   - new conversions
   - new lifecycle rules
   - new test setup
   - new type or runtime indirection

2. **What obligation does it delete?**
   - repeated predicate checks
   - repeated normalization
   - scattered mismatch assertions
   - flag/null guard matrices
   - duplicated branch policy
   - mixed syntax/interpreter behavior
   - invalid transitions currently representable

3. **Could a lower primitive solve it?**
   - direct function
   - record or object literal
   - local assertion
   - table/map
   - plain reducer
   - native form/URL state
   - explicit SQL/query

4. **Does it improve agent-editability?**
   - fewer edit hops
   - fewer lookup hops
   - fewer generated/configured layers
   - faster proof signal
   - smaller semantic diff

5. **What would `reduce` score?**
   - `T`: tax added or retained
   - `V`: proven value from deleted obligations
   - `D = T - V`
   - confidence
   - external obligation risk

## Veto rules

Do not climb when:

- the construction has no stable seam;
- the invariant is not stable enough to encode;
- the lift adds more files than checks it deletes;
- the only proof is taste or conceptual elegance;
- a lower-level primitive preserves the same truth more directly;
- public boundary compatibility is unknown and breaking change is not approved;
- the proof signal cannot detect behavior loss.

## Split recommendation

Recommend `split` when the code has both:

- an incidental high-tax wrapper, such as a framework, generator, DI container, ORM, gateway, or build tool; and
- an essential invariant, protocol, state machine, or boundary contract that should not be flattened.

Template:

```md
Move: split
Reduce: <wrapper/layer> -> <lower primitive>
Preserve or climb: <invariant/protocol/construction>
First seam:
Compatibility boundary:
Proof signal:
Rollback:
```

## Example

A small React app has two static pages and a four-step checkout flow.

Bad: "Remove React and use loose DOM event handlers for everything."

Better: "Descend from React/Vite to HTML/CSS/native ES modules for static pages and forms; preserve the checkout lifecycle as an explicit reducer with a transition table and invalid-transition tests."
