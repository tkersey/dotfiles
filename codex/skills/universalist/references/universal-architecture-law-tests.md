# Universal Architecture Law Tests

These are practical proof signals, not full formal proofs.

| Artifact | Fastest credible proof signal |
| --- | --- |
| Product | construct and project fields consistently |
| Coproduct | exhaustive handling and invalid legacy shapes rejected |
| Refined type | valid accepted, invalid rejected, normalization idempotent |
| Pullback witness | matching inputs accepted, mismatches rejected, projections preserved |
| Exponential | strategy parity with old branch fixtures |
| Free syntax | old evaluator and new interpreter match on corpus |
| Coherent observations | overlapping observations commute |
| Transported semantics | identity/embedding path preserves behavior |
| Lifted implementation | `project(realize(case)) == required(case)` |
| Free builder behind projection | `project(free(required(case)))` satisfies `required(case)` |
| Obstruction report | required behavior fails for a named evidence/template/constraint reason |
| Residual obligations | missing obligation fails, satisfying obligations passes |
| Behavioral coalgebra | traces/unfolds satisfy observations; invalid transitions rejected |
| Effect signature / handler | test handler and production projection agree on declared observations |
| Yoneda observation | representation change preserves observations |
| Coyoneda generation | lowering equals direct interpretation |
| Defunctionalized IR | `apply(encodedCase, x) == oldFunction(x)` |

## Bypass test

A canonical artifact is not canonical if callers bypass it. Add an import, code-search, architecture, or public-API check when feasible.

## Negative witness

Every Track D artifact should have at least one negative witness:

- invalid path/payload pair;
- missing observation interpreter clause;
- realizer without required behavior;
- free builder cannot satisfy a behavior because projection loses evidence;
- obstruction report names the missing evidence/template/constraint;
- obligation omitted;
- callback case not encoded;
- invalid state transition;
- two states claimed equivalent produce different observations;
- handler omits an operation case;
- operation handled differently in test and production without an explicit observation law.
