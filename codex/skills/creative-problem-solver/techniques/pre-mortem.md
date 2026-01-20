# Technique: Pre-mortem (assume failure → mine causes)

## One-liner
Time-travel: assume the plan has failed, then list reasons why; convert top causes into mitigations and discriminating experiments.

## Use when
- You have a plan and want to de-risk before committing.
- You need to surface failure modes beyond the obvious.
- Stakes are high (migration, launch, org change).

## Avoid when
- You’re still deciding what to do (use Brainstorming / Morphological Analysis).
- The group is already risk-paralyzed.

## Inputs
- The plan (or leading candidate option).
- A time horizon (“3 months later…”).

## Procedure (fast, 8–12 min)
1. Write: “It’s <time> later. We failed. Why?”
2. Generate 10–15 failure causes.
3. Rank top 3 by likelihood × impact.
4. For each top cause: mitigation + signal + escape hatch.

## Procedure (full, 20–30 min)
1. Setup
   - Name the plan and the success criteria.
2. Silent generation
   - Each participant lists failure causes privately (reduces anchoring).
3. Aggregate + cluster
   - Group causes into themes (tech, process, people, market).
4. Convert to actions
   - For each top theme:
     - prevention (guardrail), detection (signal), response (escape hatch).
5. Converge
   - Pick 1–2 high-signal experiments that de-risk multiple causes.

## Prompt bank (copy/paste)
- “What surprised us?”
- “What did we underestimate?”
- “Where did we lack ownership?”
- “What dependency failed us?”
- “What was the silent failure mode?”

## Outputs (feed CPS portfolio)
- A ranked failure-mode list.
- A mitigation plan expressed as experiments + guardrails.

## Aha targets
- Discovering that the real risk is organizational/ownership, not technical.
- Turning ‘risk’ into ‘instrumentation + rollback plan’.

## Pitfalls & defusals
- Pitfall: doom spirals → Defusal: timebox; end by converting causes into mitigations.
- Pitfall: generic causes (“communication”) → Defusal: force a concrete mechanism (artifact, meeting, owner).

## Examples
### Engineering
Plan: migrate to a new service mesh.
- Fail causes: unclear ownership, traffic regressions, observability gaps, rollback too slow.
Mitigations: canary rollout, metric dashboard, rollback playbook.
Signal: error rate + latency; escape hatch: feature flag / revert to old mesh per service.

### Mixed domain
Plan: run a community event.
- Fail causes: low turnout, unclear agenda, volunteer burnout.
Mitigations: pre-registration, agenda draft, role rotation.
Signal: registrations by date; escape hatch: scale down scope if uptake is low.