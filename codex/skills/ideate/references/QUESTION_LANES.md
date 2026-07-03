# Question Lanes

Ask only after inspecting artifacts. Close each material gap by artifact evidence, user input, explicit assumption, or deferral.

## Problem validity

Ask only if unclear:

- What user-visible or maintainer-visible problem proves this matters?
- What breaks if ignored?
- Is this the real problem or a symptom?

## Stakeholders

- Who benefits?
- Who pays the cost?
- Who owns adoption?
- Is the audience users, contributors, maintainers, operators, or future implementers?

## Outcome shape

- What would feel obviously better?
- What burden should disappear?
- What must not get worse?
- What would count as meaningful improvement?

## Scope and behavior boundary

- Prefer behavior-preserving refactors or user-visible changes?
- Which surface is off-limits?
- What compatibility promise should the seed assume?

## Constraints

- Optimize for speed, confidence, reversibility, reach, or risk reduction?
- What systems are off-limits?
- How much migration pain is acceptable?

## Existing work and overlap

- Is there already a partial solution?
- Was this tried before?
- Should this merge into an adjacent plan or stay distinct?

## Evidence and confidence

- Which assumption is most dangerous?
- What is the cheapest credible validation step?
- What evidence would change the ranking?

## Non-goals

- What should this explicitly exclude?
- Which adjacent asks belong later?
- What complexity are we refusing now?

## Rollout and maintenance

- Who owns it after launch?
- What support/migration burden appears?
- What is the rollback or containment story?

## Breakthrough quality

Clarify only when evidence cannot resolve appetite for boldness:

- Should the winner be allowed to change user-visible behavior?
- Which is more valuable: capability surface, invariant, diagnostic/proof surface, or strategic sequence?
- What proof signal would make a bold idea worth planning?
- How much risk is acceptable for a genuinely non-obvious direction?

## Follow-up rules

- If scope expands, ask whether it belongs in this seed or a later branch.
- If an answer introduces a dependency, ask whether the seed assumes it or addresses it.
- If vague, force a threshold, example, metric, or comparison.
- If impressive but not useful, ask which pain or burden it removes.
- If priorities compete, force a choice.
- If artifacts can answer, inspect instead of asking.
- If Glaze is rhetoric only, ask what concrete artifact or mechanism makes it real.
- If ASI has vision but no proof artifact, ask for the smallest testable artifact.
