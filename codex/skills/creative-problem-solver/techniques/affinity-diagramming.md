# Technique: Affinity Diagramming (cluster → name themes)

## One-liner
After divergence, silently cluster raw ideas by similarity, then label clusters by underlying intent; a fast path from chaos to a few directions.

## Use when
- You already have 20+ ideas and need convergence.
- The list feels noisy and repetitive.
- You want to find the “themes” that deserve one experiment each.

## Avoid when
- You still need breadth (use Brainstorming / Brainwriting).
- You need a conceptual leap (use Synectics / Provocation).

## Inputs
- A pile of raw ideas (notes, bullets).

## Procedure (fast, 6–10 min)
1. Write ideas as atomic notes (one per line).
2. Cluster silently by similarity (no debate).
3. Name each cluster with an intent label (verb + object).
4. Pick 1 representative idea per cluster; harden into experiments.

## Procedure (full, 15–25 min)
1. Atomicize
   - Split compound ideas into smaller notes.
2. Silent clustering
   - Move notes until clusters stabilize.
3. Naming
   - Name the cluster by *why*, not *what* (e.g., “reduce handoffs”, not “Slack”).
4. Converge
   - Score clusters for signal + reversibility.
   - Select 3–5 clusters; choose one experiment per CPS tier.

## Prompt bank (copy/paste)
- “What is the shared intent behind these notes?”
- “If this cluster had to be one verb, what is it?”
- “What cluster is missing (a blank theme)?”

## Outputs (feed CPS portfolio)
- 3–7 themes.
- 1 hardened candidate per theme.

## Aha targets
- Realizing many ideas are the same intent with different implementations.
- Discovering a missing theme (“we have no observability ideas”).

## Pitfalls & defusals
- Pitfall: debating during clustering → Defusal: enforce silence; debate only after naming.
- Pitfall: naming too early → Defusal: cluster first, name second.

## Examples
### Engineering
Input: 40 ideas to cut CI time.
Clusters: parallelize, cache, reduce scope, stabilize flakes, improve feedback.
Pick one per cluster; convert to experiments (signal: median CI time; escape hatch: revert caching if inconsistent).

### Mixed domain
Input: 30 ideas to improve a community.
Clusters: onboarding, rituals, moderation, recognition, feedback loops.
Pick one per cluster; signal: retention and participation quality; escape hatch: drop rituals if they feel forced.