# Workflow

`$ideate` is a mode-aware opportunity compiler. It combines repository signal harvesting, candidate generation, ruthless winnowing, Glaze/ASI prompt passes, overlap checking, and a planning handoff seed when evidence is sufficient.

## Phase 0 — Select mode

Choose one:

```text
fast | standard | deep | audit-only
```

Default: `standard`.

Mode budgets:

| mode | candidates | gates | output |
|---|---:|---|---|
| fast | 8-12 | Glaze top 2, ASI top 1-2 | top 3 + seed if supported |
| standard | 18-20 | Glaze top 5, ASI top 3 | top 5 + next 8-10 + seed |
| deep | 30+ | Glaze top 5-7, ASI top 3-5 | full portfolio + seed |
| audit-only | optional | optional | signals, hypotheses, gaps, no seed by default |

Downgrade when evidence cannot support the requested mode. Do not fake depth.

## Phase 1 — Scope and ground

Infer scope from the prompt. Default to the current repository or supplied artifacts.

Read relevant:

- `AGENTS.md`, `README*`, docs, ADRs, design notes;
- roadmap, backlog, TODOs, changelog;
- tests, benchmarks, fixtures, examples;
- package manifests, build scripts, config, CI workflows;
- public surfaces: commands, APIs, routes, exports, UI flows;
- user-provided files, reports, links, or issue exports;
- git history when relevant.

Capture:

```text
scope, repo shape, users/maintainers, constraints, opportunity signals,
overlap, assumptions, unknowns requiring user input.
```

## Phase 2 — Harvest signals

Use `CODEBASE_SIGNAL_LANES.md`. Sample strategically; do not audit every file.

Signal classes:

```text
public surface, maintainer friction, architecture seam, test intent,
reliability, performance, observability, negative space, history/churn,
refactor-enabler
```

Evidence should cite the smallest useful path, symbol, command, test, or artifact. Prefer `path:line` when practical.

## Phase 3 — Interrogate only material gaps

Before ideating, know or assume:

- what problem/opportunity this concerns;
- who benefits;
- what better means;
- constraints and non-goals;
- what behavior must remain stable;
- what evidence exists;
- what success would look like;
- overlap with existing work;
- behavior-change appetite.

Ask only if the missing answer would materially change ranking and cannot be inferred.

## Phase 4 — Generate candidate field

Generate the mode-appropriate number of concrete candidates. Each should include evidence, originality source, benefit, risk, validation path, and overlap status.

Candidate buckets to sample when relevant:

- user-facing additions or features;
- DX / CLI / API / workflow improvements;
- refactor or simplification opportunities;
- reliability / correctness / recovery;
- observability / diagnostics;
- performance / scalability;
- documentation/onboarding with structural value;
- hidden primitive or negative-space wildcards.

Avoid duplicate variants, generic cleanup, unsupported features, refactors without behavior-preservation strategy, and pure implementation details with no strategic meaning.

## Phase 5 — First winnow

Use `RUBRIC.md`.

1. Remove fatal flaws.
2. Remove weak or generic evidence.
3. Score remaining candidates.
4. Rank by evidence, value, originality, validation, and fit.
5. Keep the mode-appropriate shortlist.
6. Pick a preliminary leader.

The preliminary leader is not final. It is input to Glaze and ASI.

## Phase 6 — Glaze prompt pass

Use `ESCALATION_GATES.md`.

For each shortlisted candidate under the mode budget, produce:

- why the obvious version loses;
- default basin;
- material delta;
- stronger move;
- why it wins;
- next evaluation step.

Cut or demote candidates with no material delta.

## Phase 7 — ASI prompt pass

Use `ESCALATION_GATES.md`.

For the strongest Glaze survivors, produce:

- why the current answer still underperforms;
- 10x horizon;
- systemic frame;
- leverage point;
- smallest proof-bearing artifact;
- cash-out type;
- why it preserves the 10x insight;
- first proof signal.

Cut or demote candidates with no small proof-bearing artifact.

## Phase 8 — Breakthrough synthesis and second winnow

Re-score escalated candidates against ordinary value and breakthrough quality.

Ask:

- Did Glaze add a material delta?
- Did ASI expose and compress a 10x frame?
- Is the artifact still grounded in evidence?
- Is the result better than the baseline?
- Can the proof signal be observed before a full implementation bet?

Rank the final portfolio.

## Phase 9 — Overlap scan

Search after escalation for matching or conflicting existing work:

```text
roadmap, TODOs, backlog, issue exports, past attempts, recent changes,
hidden features, naming collisions, adjacent plans
```

Classify each shortlisted idea:

```text
direct duplicate | adjacent / merge mentally | conflict | net-new | unknown due to thin evidence
```

Do not use `br`.

## Phase 10 — Refine the chosen direction

Use critique passes appropriate to mode:

- fast: at least 2 passes — value/fit, proof/cash-out;
- standard/deep: at least 5 passes — value, architecture risk, evidence/originality, Glaze delta, ASI cash-out;
- audit-only: no seed refinement unless explicitly requested.

Do not overspecify implementation.

## Phase 11 — Emit portfolio and planning handoff seed

Use `OPPORTUNITY_PORTFOLIO_TEMPLATE.md` and `PLAN_SEED_TEMPLATE.md`.

The seed is not a plan. It is a handoff object for a later `$spec-pipeline` or `$plan` run.

## Thin-evidence terminal

Use `IDEATE_EVIDENCE_TOO_THIN` when evidence cannot support a credible portfolio.

Output:

- compressed snapshot;
- evidence gaps;
- 3-5 signal hypotheses;
- exact artifacts needed next;
- no breakthrough claim;
- no planning seed unless one hypothesis is sufficiently grounded and the user requested it.

## IDR-v1 terminal receipt

Every terminal output includes IDR-v1. See `IDEATE_RESULT.md`.
