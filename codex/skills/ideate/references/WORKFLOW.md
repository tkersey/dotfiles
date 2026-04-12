# Workflow

This skill combines exhaustive clarification with a disciplined ideation funnel.

## Phase 1 — Ground in reality

Before asking the user, inspect available artifacts and build a factual baseline.

Read:
- `AGENTS.md`
- `README*`
- docs and design notes
- roadmap, backlog, changelog, ADRs, TODOs
- tests, benchmarks, package manifests, config files
- user-provided files, links, tickets, or issue exports

Capture:
- the apparent problem
- affected users
- constraints
- current workarounds
- possible existing plans or overlap

## Phase 2 — Interrogate until you can ideate responsibly

Do not settle for surface-level framing.

You should be able to answer, explicitly or by assumption:
- what problem or opportunity this is about
- who benefits
- what “better” means
- what constraints matter
- what is out of scope
- what evidence exists
- what success would look like

If you cannot answer those, keep asking.

## Phase 3 — Generate 30 candidates

Generate a wide field before selecting a direction.

Candidate types to include:
- direct user-facing improvements
- enabling capabilities with clear downstream user value
- workflow reductions
- reliability/robustness improvements
- insight or visibility improvements
- adjacent opportunities that may complement the strongest idea

Avoid:
- duplicate variants
- pure implementation details with no strategic meaning
- ideas whose only appeal is novelty

## Phase 4 — Winnow 30 → 5 → 15

Use the rubric to score and cut aggressively.

Suggested sequence:
1. remove anything with a fatal flaw
2. remove low-average ideas
3. rank the rest
4. keep the strongest 5
5. add the next 10 or the strongest complements
6. choose the leading direction

The value of the 15-set is not merely “more ideas.” It reveals complements, enabling bets, and trade-offs around the top candidate.

## Phase 5 — Overlap scan without `br`

Search the repo and provided artifacts for:
- similar roadmap items
- TODOs or backlog notes
- past attempts
- recently completed adjacent work
- naming collisions and scope collisions

For each shortlisted idea, classify:
- duplicate
- adjacent / merge mentally
- conflict
- net-new

If certainty is impossible because the repo is thin, say so explicitly.

## Phase 6 — Plan-space refinement

Refine the chosen direction before turning it into a plan seed.

Use at least three passes:

### Pass 1 — Is this the right bet?
- sharp user benefit
- clear thesis
- sensible boundaries

### Pass 2 — What could derail it?
- dependencies
- rollout burdens
- maintenance cost
- awkward edge cases

### Pass 3 — What would justify full planning?
- validation path
- measurable success signals
- planning questions that remain open

Optional:
### Pass 4 — Can the seed be sharper?
- better title
- tighter framing
- cleaner workstream grouping

## Final output

The final artifact is a **plan seed**, not a roadmap, ticket set, or implementation plan.

A good plan seed is:
- specific enough to guide a later planning pass
- bounded enough not to sprawl
- honest about risks and assumptions
- explicit about why it won
- grounded in existing context

See `PLAN_SEED_TEMPLATE.md`.
