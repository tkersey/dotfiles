# Latent Move Workflow

## Full algorithm

1. Establish entry state.
2. Create an artifact state label:
   - repo and branch if known
   - task label
   - relevant artifact surfaces
   - evidence freshness
3. Build the initial Evidence Ledger from user input and direct inspection.
4. Decide whether a read-only subagent swarm is useful.
5. If using subagents:
   - brief only the needed roles
   - require exactly one `LATENT_MOVE_PACKET` per role
   - wait for relevant results
   - normalize packets into the Specialist Briefing Ledger
   - mark malformed packets `transport-invalid`
6. Run `latent-diver` or directly perform the latent pass:
   - surface hidden assumptions
   - identify latent frames
   - record non-obvious opportunity and risk surfaces
   - update the Latent Frame Ledger
7. Run `creative-problem-solver` or directly produce its portfolio:
   - identify Double Diamond stage
   - state working definition and success criteria if weak
   - define the Artifact Spine
   - generate the five-tier portfolio
   - update the Portfolio Ledger
8. Run `accretive` or directly perform candidate compression:
   - choose the target lane
   - compress the portfolio into two to four candidates
   - nominate one move only if it clearly dominates
   - otherwise abstain
   - update the Candidate Ledger
9. If no nominee exists:
   - set state to `no-dominant-move` or `needs-evidence`
   - name the fastest discriminating check
   - skip dominance unless a candidate set still needs adjudication
10. Run `dominance` on the candidate set and nominee:
    - validate or reject the winner
    - update the Dominance Ledger
11. If `dominance` returns `Winner`:
    - require a concrete first proof signal
    - produce a Dominant Move Brief
    - set final state to `dominant-move`
12. If `dominance` returns `No dominant move`:
    - state why no candidate dominates
    - identify closest contender
    - name what would break the tie
    - set final state to `no-dominant-move`
13. If `dominance` returns `Insufficient evidence`:
    - state missing evidence
    - name the fastest discriminating check
    - state what decision the check would unlock
    - set final state to `needs-evidence`
14. If the blocker is a product, architecture, compatibility, or scope decision:
    - set final state to `needs-decision`
15. If access or tooling prevents meaningful analysis:
    - set final state to `blocked`
16. Stop. Do not execute.

## Routing rules

### Latent frames

If a latent frame changes the apparent problem statement, rerun the portfolio from that frame.

If multiple latent frames are plausible, keep at most three and feed them into the portfolio.

If a latent frame is interesting but not evidence-backed, record it as speculative and do not let it dominate selection.

### Portfolio

The five-tier portfolio must include: Quick Win, Strategic Play, Advantage Play, Transformative Move, and Moonshot.

Each tier must include move, accretive artifact, expected signal, and escape hatch.

If a tier cannot be produced honestly, mark it `not-found` and explain why.

Do not invent a Moonshot just to satisfy symmetry if it would be theater.

### Candidate compression

Compress to two to four plausible candidates before dominance.

Prefer candidates with concrete proof surface, narrow minimum viable diff, compounding leverage, clear artifact spine, low reversibility cost, and good time to first signal.

Reject broad cleanup, cosmetic churn, prestige architecture, novelty without leverage, moves whose proof would be unavailable, and moves that require unmade product decisions.

### Dominance

Do not name a winner unless it clearly dominates.

If the candidate set is too heterogeneous, normalize it to comparable move granularity.

If there is only one candidate and the user did not mandate it, generate or recover at least one plausible alternative before judging.

If no winner exists, name the fastest check that could change the ranking.

If the fastest check would require implementation, say so and recommend an executor.
