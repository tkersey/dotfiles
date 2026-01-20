# Technique: Storyboarding (end-to-end flow)

## One-liner
Narrate (or sketch) the sequence from trigger to outcome, including handoffs, decision points, and failure modes; this reveals missing steps and where signal can be measured.

## Use when
- The problem involves a multi-step journey (incident response, onboarding, checkout).
- You suspect the failure is in handoffs/edges, not the core step.
- You need to decide *where* to instrument or intervene.

## Avoid when
- You need raw idea breadth (use Brainwriting / Lotus Blossom).
- You need a conceptual leap (use Synectics / Provocation).

## Inputs
- Actor(s): who experiences the flow.
- Start trigger + desired end state.

## Procedure (fast, 8–12 min)
1. Write the flow as 8–12 steps (“A → B → C”).
2. Mark 2 points:
   - decision points
   - failure points
3. Add one measurable signal per failure point.
4. Pick one step to improve; propose an experiment.

## Procedure (full, 20–30 min)
1. Establish lanes
   - User lane, system lane, human-ops lane (or analogous lanes).
2. Trace happy path
   - Include handoffs and waiting.
3. Trace key failure paths
   - Where does it degrade? how do we notice? what do we do then?
4. Identify leverage points
   - the bottleneck step, the highest uncertainty step, and the best measurement point.
5. Convert into CPS options
   - Each option targets a leverage point with a signal + escape hatch.

## Prompt bank (copy/paste)
- “What happens right before the pain?”
- “Where do we wait?”
- “Where do we hand off responsibility?”
- “Where could we detect failure earlier?”
- “What is the earliest measurable signal?”

## Outputs (feed CPS portfolio)
- A shared flow model.
- A shortlist of intervention points + instrumentation ideas.

## Aha targets
- Discovering the real problem is a handoff, a wait, or missing detection.

## Pitfalls & defusals
- Pitfall: story is too high-level → Defusal: force concrete steps and owners.
- Pitfall: no signals → Defusal: every failure point must have a detection signal.

## Examples
### Engineering
Flow: “incident → triage → mitigate → recover → follow-up.”
Leverage: detection (missing signals) and rollback (slow).
Option: add error-budget alert + rollback playbook; signal: MTTR drops; escape hatch: disable noisy alert.

### Mixed domain
Flow: “customer complaint → support intake → diagnosis → resolution → follow-up.”
Leverage: diagnosis handoff.
Option: add structured intake form + routing; signal: time-to-resolution drops; escape hatch: simplify form if completion rate falls.