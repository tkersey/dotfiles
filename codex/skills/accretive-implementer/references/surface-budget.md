# Surface Budget

Surface budget is the accounting discipline that prevents `accretive` from becoming merely additive.

## Principle

A change is accretive only when durable value increases after accounting for new surface area.

A smaller artifact with a stronger owner and a better witness can be more accretive than a larger artifact with more helpers.

## Additive surfaces

Treat these as budget-consuming until justified:

- helpers
- wrappers
- adapters
- fallback paths
- flags
- knobs
- branches
- state variants
- public symbols
- compatibility paths
- parser tolerance
- catch-and-continue paths
- default/coercion behavior
- abstractions

## Budget receipt

For non-trivial production changes, report:

| surface | count | notes |
|---|---:|---|
| production files touched |  |  |
| production insertions |  |  |
| production deletions |  |  |
| public symbols added |  |  |
| helpers/wrappers/adapters added |  |  |
| flags/branches/state variants added |  |  |
| duplicate/shadow paths retired |  |  |
| tests/proofs added |  |  |
| net surface call | smaller/same/larger-with-warrant/larger-without-warrant |  |

## Larger-with-warrant

A larger patch may still be right-sized when it:

- moves enforcement to the rightful owner;
- makes illegal states uninhabitable;
- retires scattered caller-side defensive logic;
- replaces implicit behavior with a single canonical representation;
- adds a proof surface that prevents future overproduction.

The warrant must name what future code or duplicate owner this addition prevents.

## Larger-without-warrant

`larger-without-warrant` is not a success state. Stop, route to fixed-point/ablation, or revise the patch.
