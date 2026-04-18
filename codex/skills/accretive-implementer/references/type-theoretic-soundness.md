# Type-theoretic soundness notes

Use these questions when a code change feels "unsound" in more than the everyday sense.

## Witness
What concrete artifact witnesses the claim?
Examples:
- direct test
- boundary refinement or parsing
- exhaustive match
- constructor discipline
- explicit guard plus bounded error path

## Preservation
After each step, retry, rollback, serialization hop, or normalization pass, what must still be true?
If the guarantee holds only at entry, preservation is incomplete.

## Progress
Can execution always move to a legal next state?
Look for stuck states:
- partial initialization
- ambiguous defaults
- swallowed errors
- sentinel states
- impossible-but-representable values

## Totality
Where a case split matters, are all cases visible and forced?
If partiality is unavoidable, make it explicit.

## Refinement
Push raw-to-validated narrowing toward the boundary.
Illegal states should be uninhabitable when practical and explicit when not.
