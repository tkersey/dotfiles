# Logophile Precision Lexicon

Use this lexicon to replace generic phrases with more exact phrasing before doing ordinary tightening.

## Rules
- This is a single lexicon, not a general-vs-repo split.
- Context wins over the default replacement.
- A replacement must improve precision, not just sound fancier.
- A mapping may be added on one compelling case and should be pruned quickly if it starts causing drift.

## Entry Fields
- `source_phrase`: the weak phrase to detect.
- `candidate_replacements`: stronger options; pick the one that fits the local text.
- `precision_gain`: what became more exact.
- `fits_when`: when the replacement is a good default.
- `avoid_when`: when the replacement would overreach or misread the text.
- `example`: a concrete rewrite.
- `status`: `active` or `prune`.

## Entries

### iterate on improvements
- `source_phrase`: `iterate on improvements`
- `candidate_replacements`: `find accretive changes`; `tighten the contract`; `refine the workflow`
- `precision_gain`: replaces a generic progress phrase with a concrete direction
- `fits_when`: the surrounding text is about skill, workflow, plan, or contract refinement
- `avoid_when`: the text is user-facing plain-language copy or the target of the change is unknown
- `example`: `We should iterate on improvements to this skill.` -> `Find accretive changes to this skill.`
- `status`: `active`

### make it better
- `source_phrase`: `make it better`
- `candidate_replacements`: `simplify it`; `clarify it`; `stabilize it`; `harden it`
- `precision_gain`: forces the writer to name what kind of improvement is intended
- `fits_when`: the target object is known from nearby context
- `avoid_when`: no axis of improvement is recoverable from context
- `example`: `Make the error path better.` -> `Harden the error path.`
- `status`: `active`

### improve
- `source_phrase`: `improve`
- `candidate_replacements`: `simplify`; `clarify`; `stabilize`; `accelerate`; `harden`; `refine`
- `precision_gain`: turns a vague quality claim into a concrete change axis
- `fits_when`: one axis is clearly implied by nearby wording
- `avoid_when`: the surrounding text does not reveal the intended axis
- `example`: `Improve the onboarding flow.` -> `Clarify the onboarding flow.`
- `status`: `active`

### handle
- `source_phrase`: `handle`
- `candidate_replacements`: `parse`; `validate`; `normalize`; `route`; `retry`; `throttle`; `reject`
- `precision_gain`: replaces a catch-all verb with the actual action
- `fits_when`: the operation is inferable from the object or nearby sentence
- `avoid_when`: the sentence genuinely covers multiple different actions
- `example`: `Handle malformed inputs.` -> `Reject malformed inputs.`
- `status`: `active`

### better
- `source_phrase`: `better`
- `candidate_replacements`: `clearer`; `safer`; `faster`; `tighter`; `more exact`
- `precision_gain`: names the improvement axis instead of gesturing at it
- `fits_when`: the sentence can support one specific axis
- `avoid_when`: the axis is not recoverable
- `example`: `Choose a better phrase.` -> `Choose a tighter phrase.`
- `status`: `active`

### robust
- `source_phrase`: `robust`
- `candidate_replacements`: `bounded`; `idempotent`; `deterministic`; `fail-closed`; `resilient`
- `precision_gain`: states the concrete reliability property
- `fits_when`: the text implies a specific failure or reliability contract
- `avoid_when`: the writer is naming general durability without a precise property
- `example`: `Use a robust parser.` -> `Use a fail-closed parser.`
- `status`: `active`

### check it works
- `source_phrase`: `check it works`
- `candidate_replacements`: `validate the behavior`; `prove the path`; `confirm the invariant`
- `precision_gain`: replaces a weak verification phrase with explicit proof intent
- `fits_when`: the text is about verification, proofs, or acceptance
- `avoid_when`: only a casual smoke-check is intended and stronger proof wording would mislead
- `example`: `Check it works before shipping.` -> `Validate the behavior before shipping.`
- `status`: `active`

### at this point in time
- `source_phrase`: `at this point in time`
- `candidate_replacements`: `now`
- `precision_gain`: removes bureaucratic scaffolding
- `fits_when`: always, unless the longer phrase is quoted text
- `avoid_when`: the wording must remain verbatim
- `example`: `At this point in time, we can proceed.` -> `Now we can proceed.`
- `status`: `active`

### in order to
- `source_phrase`: `in order to`
- `candidate_replacements`: `to`
- `precision_gain`: removes empty setup phrasing
- `fits_when`: always, unless the phrase is quoted text
- `avoid_when`: verbatim preservation is required
- `example`: `In order to proceed, verify access.` -> `To proceed, verify access.`
- `status`: `active`

### due to the fact that
- `source_phrase`: `due to the fact that`
- `candidate_replacements`: `because`
- `precision_gain`: removes scaffolding without reducing causality
- `fits_when`: always, unless the phrase is quoted text
- `avoid_when`: verbatim preservation is required
- `example`: `The build failed due to the fact that the cache was stale.` -> `The build failed because the cache was stale.`
- `status`: `active`

### thing / stuff / area / part
- `source_phrase`: `thing`; `stuff`; `area`; `part`
- `candidate_replacements`: name the object directly
- `precision_gain`: removes placeholder nouns
- `fits_when`: the specific referent is present nearby
- `avoid_when`: the referent is genuinely unknown
- `example`: `Tighten that part.` -> `Tighten the rollback section.`
- `status`: `active`
