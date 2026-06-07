# Example: Compact Local Refactor

## Input cue

> This function works, but it is hard to follow. Can you simplify it?

Code symptoms:
- nested guard/else blocks;
- three booleans controlling behavior;
- parsing, validation, decision, and side effects mixed together.

## Expected `$complexity-mitigator` response shape

**0) Slice**
- Entrypoint: `submitOrder`
- Inputs/outputs/state: request payload -> order result; mutates order store; emits notification.

**1) Heat Read**
- `submitOrder` - [nesting=4, branches=9, booleans=3, state=2 mutations] - happy path is hidden behind failure branches - `incidental`
- `submitOrder` - [mixed parse/validate/decide/effect] - reader cannot see which branch is policy vs mechanics - `mixed`

**2) Risk Vector**
- Primary: `complexity`
- Secondary: `invisibility`
- Confidence: `medium`
- Refactor-first allowed: `only tiny/local`

**3) Essential vs Incidental**
- Essential: order eligibility, inventory reservation, notification semantics.
- Spec/conformity/change risk: low unless retry/duplicate submission policy is undocumented.
- Incidental: nested validation, negative boolean names, side effects interleaved with decision logic.

**4) Preferred Cut**
- Recommendation: flatten validation into guard clauses, rename flags positively, split `decideOrderAction` from `applyOrderAction`.
- Why this before alternatives: it makes the behavior visible before deciding whether extraction or a state model is justified.

**5) TRACE Delta**
- T: consider local enum `OrderAction` only after branches are flattened.
- R: positive names replace reader simulation of double negatives.
- A: decision separated from effects.
- C: nesting and state simulation decrease.
- E: order policy remains explicit.
