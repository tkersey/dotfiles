# Universalist Overview

## Goal and stance

Treat universal constructions as practical design tools for everyday code, not
as a theory showcase. Start from the smell in the repo, choose the smallest
construction that explains it, encode it idiomatically, and prove the win with a
small executable signal.

A good `universalist` run leaves the repo with:

- a stronger internal truth shape
- a narrow reviewed seam
- a compatibility story at the boundary
- one clear proof signal
- an explicit stop point

## What this skill is for

Use `universalist` when the real leverage is structural:

- impossible states are leaking through flag or nullable matrices
- the same predicate is checked at several boundaries
- shared-key agreement is asserted over and over
- branchy behavior wants to be supplied, not hard-coded
- syntax and interpretation are tangled together

## What this skill is not for

Do not use it as a general implementation shell. Once the structural decision is
made, switch to the repo's ordinary implementation loop or to
`accretive-implementer`.

## Default operator loop

1. Inspect repo reality: language, framework, boundary layers, and tests.
2. Start from the code smell, not the category name.
3. Pick one seam with a stable blast radius.
4. Choose the smallest honest construction.
5. Keep external shapes stable behind an adapter when possible.
6. Encode with the strongest honest language feature the repo can support.
7. Verify with the cheapest meaningful proof signal.
8. Record what remains runtime-only and stop after the first seam.

## Core constructions

### Product plus terminal object
Use for independent fields carried together.

### Coproduct plus initial object
Use for exclusive states, workflows, or typed errors.

### Equalizer or refined type
Use when one stable predicate is enforced repeatedly.

### Pullback
Use when two views must agree on a shared projection.

### Exponential
Use when behavior should be passed as a function or strategy.

### Free construction or initial algebra
Use when syntax should be modeled separately from execution.

Use Algebra-Driven Design only after the outer shape is chosen.

## Honest encoding ladder

Choose the strongest encoding the repo can actually support:

1. Native ADTs, exhaustive matching, value objects, and generics
2. Sealed hierarchies, records, enums with payload, and closed interfaces
3. Interface + tag, checked constructor, witness struct, strategy object
4. Runtime validator + wrapper + differential tests in dynamic code

Be explicit about what remains runtime-only.

## Companion-skill routing

- Use `invariant-ace` when invariants are still implicit or disputed.
- Use `accretive-implementer` once the structural move is settled.
- Use `repeatedly-apply-skill` to sweep multiple seams serially.
