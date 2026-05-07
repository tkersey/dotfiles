# Question Lanes for Ideation

Use these lanes to decide what to ask next after inspecting artifacts. Do not ask every question literally. Close every material gap by artifact evidence, user input, explicit assumption, or deferral.

## 1. Problem validity

Clarify:

- What is the actual pain, missed opportunity, risk, or decision?
- Why does it matter now?
- What happens if we do nothing?
- Is this the real problem, or a symptom?

Good forcing questions:

- What user-visible or maintainer-visible problem proves this matters?
- What is the current workaround?
- What breaks if we ignore this for three months?
- Is this the first problem we should solve, or a downstream one?

## 2. User and stakeholder reality

Clarify:

- Who benefits?
- Who pays the cost?
- Who decides?
- Who might resist the change?

Good forcing questions:

- Which user or maintainer is the primary beneficiary?
- Who owns adoption after launch?
- Whose workflow would this disrupt?
- Is the target audience end users, contributors, maintainers, operators, or future implementers?

## 3. Outcome shape

Clarify:

- What better state are we trying to reach?
- What would users or maintainers notice?
- What should remain unchanged?

Good forcing questions:

- What would feel obviously better to a user?
- What maintenance burden should disappear?
- What must not get worse?
- What would count as a meaningful improvement?

## 4. Codebase scope and behavior boundary

Clarify:

- Which subsystem is in scope?
- Are behavior changes acceptable?
- Is this primarily a feature, refactor, simplification, reliability fix, performance improvement, or DX improvement?
- What public APIs, commands, outputs, config formats, or data formats must remain stable?

Good forcing questions:

- Should this prefer behavior-preserving refactors or user-visible changes?
- Which surface is off-limits?
- What compatibility promise should the plan seed assume?

## 5. Constraints

Clarify:

- time
- staffing
- technical boundaries
- platform limits
- policy, legal, or security limits
- appetite for risk
- migration tolerance

Good forcing questions:

- What timeline assumption should we design around?
- What systems are off-limits?
- Are we optimizing for speed, confidence, reversibility, or reach?
- How much migration pain is acceptable?

## 6. Existing work and overlap

Clarify:

- what already exists
- what was attempted before
- what is already planned
- what adjacent work could absorb this
- what recent changes may make this easier or obsolete

Good forcing questions:

- Is there already a partial solution?
- Was this tried before? What happened?
- Which existing roadmap item is closest to this?
- Should this merge into an adjacent plan, or stay distinct?

## 7. Evidence and confidence

Clarify:

- what evidence exists
- what is guessed
- what can be cheaply validated
- what repo signals support the opportunity

Good forcing questions:

- What evidence supports this opportunity?
- Which assumption is most dangerous?
- What is the cheapest credible validation step?
- What repo signal would change our ranking if it turned out to be false?

## 8. Non-goals and boundaries

Clarify:

- what this idea is not
- what should be deferred
- what should stay stable
- what complexity is intentionally excluded

Good forcing questions:

- What should this plan seed explicitly exclude?
- Which adjacent asks belong in a later branch?
- What complexity are we refusing to take on yet?
- What would make this idea too large to remain useful?

## 9. Rollout, support, and maintenance

Clarify:

- launch shape
- migration burden
- ownership
- observability
- long-term care
- documentation and support implications

Good forcing questions:

- Who owns this after launch?
- Does this require migration or support overhead?
- What new maintenance burden are we buying?
- What is the rollback or containment story?

## 10. Success and failure

Clarify:

- success signals
- failure modes
- reversibility
- disconfirming evidence

Good forcing questions:

- What metric, behavior, or feedback would prove success?
- How might this fail even if we build it correctly?
- Can we reverse or contain the change if it underperforms?
- What evidence would convince us not to pursue this?

## Follow-up rules

Use these decision rules aggressively:

- If the answer expands scope, ask whether it belongs in this seed or a later branch.
- If the answer introduces a dependency, ask whether the seed assumes it or must address it.
- If the answer is vague, force a measurable or example-based answer.
- If the answer sounds impressive but not useful, ask which user pain or maintainer burden it removes.
- If the answer suggests competing priorities, force a choice.
- If artifacts can answer the question, inspect instead of asking.
