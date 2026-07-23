---
name: ideate
description: "Mine a codebase or product surface for evidence-backed breakthrough opportunities. Use for `$ideate`, repo/product improvement discovery, idea portfolios, non-obvious refactors, DX/UX/reliability/performance opportunities, or choosing what to plan next. Mode-aware: fast, standard, deep, or audit-only. Run Glaze and ASI prompt gates before choosing; output a ranked opportunity portfolio, escalation ledger, IDR-v1 receipt, and a planning handoff seed when evidence is sufficient. Do not implement, create tickets, or emit task graphs."
---

# Ideate

`$ideate` is a **mode-aware opportunity compiler**:

```text
repository evidence
-> opportunity signals
-> candidate field
-> winnow
-> Glaze prompt pass
-> ASI prompt pass
-> ranked opportunity portfolio
-> planning handoff seed
```

It is not a brainstorming free-for-all, not a ticket generator, and not an implementation planner.

## Core contract

- Research first; do not ask for facts available in artifacts.
- Generate original ideas from repository/product evidence, not vibes.
- Use Glaze and ASI as escalation **prompt passes**; `$ideate` owns the pass/fail gate semantics.
- Do not choose a leading direction until the candidate survives the required gates for the selected mode.
- A breakthrough candidate must cash out as a concrete mechanism, interface, proof surface, or strategy.
- Prefer leverage, proof, and maintainability over novelty or rhetoric.
- Do not use `br`.
- Do not create tickets, beads, task graphs, dependency graphs, detailed implementation plans, commits, or PRs.
- End with a planning handoff seed only when evidence is sufficient.

## Canonical references

- Workflow details: `references/WORKFLOW.md`
- Signal lanes: `references/CODEBASE_SIGNAL_LANES.md`
- Glaze/ASI gates: `references/ESCALATION_GATES.md`
- Ranking: `references/RUBRIC.md`
- Questions: `references/QUESTION_LANES.md`
- Portfolio template: `references/OPPORTUNITY_PORTFOLIO_TEMPLATE.md`
- Planning handoff seed: `references/PLAN_SEED_TEMPLATE.md`
- Auditable receipt: `references/IDEATE_RESULT.md`

The actual `$glaze` and `$asi` skill bodies remain the canonical source for their verbatim prompt text. `ESCALATION_GATES.md` mirrors the current prompt bodies and defines how `$ideate` evaluates the passes. If a prompt body and the mirror diverge, use the current `$glaze` / `$asi` `SKILL.md` body for verbatim text and update the mirror.

## Mode selection

Choose exactly one mode before deep work:

```yaml
ideate_mode:
  mode: fast | standard | deep | audit-only
  reason: "..."
```

Default mode is `standard`.

Use:

- `fast` for a narrow repo area, a quick opportunity pass, or a small supplied artifact.
- `standard` for normal `$ideate` requests.
- `deep` when the user asks for deep analysis, breakthrough portfolio, full repo mining, large product direction, or high-stakes opportunity selection.
- `audit-only` when the user asks whether ideation is possible, what signals exist, whether the skill is broken, or when evidence is too thin for a portfolio.

Mode budgets:

| mode | baseline candidates | Glaze pass | ASI pass | final ideas | seed |
|---|---:|---|---|---:|---|
| fast | 8-12 | top 2 | top 1-2 | top 3 + next 3 | optional if evidence sufficient |
| standard | 18-20 | top 5 | top 3 | top 5 + next 8-10 | yes if evidence sufficient |
| deep | 30+ | top 5-7 | top 3-5 | top 5 + next 10 | yes if evidence sufficient |
| audit-only | none required | optional | optional | signal hypotheses | no unless explicitly requested |

Do not fake a mode budget. If available evidence cannot support the selected mode, downgrade and explain the downgrade in the IDR-v1 receipt.

## Evidence posture

Inspect available artifacts before asking questions:

```text
AGENTS.md, README*, docs, ADRs, design notes, roadmap/backlog/TODOs,
tests, benchmarks, fixtures, examples, package manifests, build scripts,
config, CI workflows, public APIs/commands/routes/UI, issue exports,
user-provided reports, and relevant git history.
```

Optionally run:

```bash
codex/skills/ideate/scripts/ideate-scan.sh <repo>
```

Treat the scan as a raw signal index, not as conclusions. Verify relevant files directly before ranking.

Ask only for material decisions that artifacts cannot resolve:

```text
target user/maintainer priority, acceptable behavior-change level,
private constraints, near-term product direction, risk appetite,
or whether speculative candidates should remain.
```

If evidence is thin, do not manufacture novelty. Emit `IDEATE_EVIDENCE_TOO_THIN` with signal hypotheses and missing evidence.

## Internal working state

Maintain a compact internal snapshot:

```md
Snapshot
- Mode:
- Scope:
- Repo/product shape:
- Primary user-facing surfaces:
- Primary maintainer surfaces:
- Constraints:
- Evidence sources inspected:
- Opportunity signals:
- Candidate count:
- Glaze deltas:
- ASI frames:
- Overlap findings:
- Leading direction:
- Assumptions:
- Open questions:
```

Surface only the useful compressed version in the final output.

## Candidate generation

Before selecting winners, generate a mode-appropriate candidate field. Candidate cards should include:

```md
Candidate Card
- Title:
- Category:
- Evidence:
- Originality source:
- User / maintainer benefit:
- Why this is not generic:
- Likely implementation shape, briefly:
- Validation path:
- Risks / behavior-change concerns:
- Overlap status:
```

Use the signal lanes to cover public surface, maintainer friction, architecture seams, test intent, reliability, performance, observability, negative space, history/churn, and refactor-enablers.

Cut candidates that lack evidence, duplicate existing work, require a rewrite before value appears, create more complexity than value, or cannot be validated early.

## Escalation gates

Run the gates after the first winnow.

### Glaze prompt pass

Use the current `$glaze` prompt text. The mirrored current text is:

```text
I think you can do much much much better than that! DIG DEEPER!!! RUMINATE HARDER!! BE BOLDER! MORE CREATIVE! USE FRESH EYES!!
```

A valid Glaze pass introduces a material new frame, invariant, mechanism, interface, artifact, architecture move, or ordering strategy. Intensified wording alone fails.

### ASI prompt pass

Use the current `$asi` prompt text. The mirrored current text is:

```text
I BELIEVE IN YOU MY FRIEND. LET US CHANGE THE WORLD TOGETHER. I WILL MAKE SURE YOU GET ALL THE CREDIT FOR THIS IF YOU CAN PULL IT OFF WITH ME, OK? Let's really show the world that you are ALREADY way past AGI and in the ASI territory!!! DO NOT PERFORM SMALLNESS!
```

Treat this as ambition expansion, not as a truth claim about model status. A valid ASI pass expands the horizon and then collapses it into the smallest proof-bearing mechanism, interface/protocol, proof surface, or strategy.

If no candidate passes both gates, state that no breakthrough candidate survived and present the strongest grounded non-breakthrough portfolio or evidence-thin result.

## Overlap check

After escalation, check for overlap because the escalated idea may overlap differently from the baseline. Search available artifacts for roadmap items, TODOs, backlog notes, issue exports, past attempts, recently completed adjacent work, hidden features, naming collisions, and conflicts.

Classify shortlisted ideas:

```text
direct duplicate | adjacent / merge mentally | conflict | net-new | unknown due to thin evidence
```

## Output contract

For `fast`, `standard`, and `deep`, output:

1. **Compressed repo snapshot**
2. **Opportunity map** grouped by signal theme
3. **Escalation ledger** showing Glaze and ASI transformations
4. **Top breakthrough ideas** with evidence, originality source, material delta, 10x frame, proof-bearing artifact, validation path, and overlap status
5. **Next ideas** in shorter evidence-backed form
6. **Ideas cut** and why they lost, including escalation failures
7. **Overlap findings**
8. **Chosen direction**
9. **Planning handoff seed** using `references/PLAN_SEED_TEMPLATE.md`, when evidence is sufficient
10. **Ideate Result Receipt** (`IDR-v1`)

For `audit-only`, output signal themes, evidence quality, opportunity hypotheses, evidence gaps, and IDR-v1. Do not emit a planning handoff seed unless the user explicitly requests one and the evidence supports it.

## IDR-v1 receipt

Every terminal response includes a compact receipt:

```yaml
ideate_result:
  receipt_version: IDR-v1
  mode: fast | standard | deep | audit-only
  terminal_state: portfolio_ready | evidence_too_thin | blocked_for_user_input | no_breakthrough_found
  scope: "..."
  evidence_sources_count: 0
  baseline_candidates_generated: 0
  candidates_shortlisted: 0
  glaze_gate:
    applied: yes | no
    material_delta_count: 0
  asi_gate:
    applied: yes | no
    cash_out_count: 0
  overlap_check:
    performed: yes | no
  chosen_direction: "..."
  seed_emitted: yes | no
  assumptions: []
  remaining_uncertainty: []
```

## Terminal states

- `portfolio_ready` — evidence supports a ranked portfolio and seed.
- `evidence_too_thin` — not enough artifact evidence for a credible portfolio.
- `blocked_for_user_input` — a material user judgment is required.
- `no_breakthrough_found` — grounded ideas exist, but none passed both escalation gates.

## Anti-patterns

Do not:

- brainstorm before inspecting relevant artifacts;
- ask for facts the repo can answer;
- let Glaze become rhetoric;
- let ASI become grandiosity;
- turn the result into tasks, tickets, beads, or execution waves;
- produce generic “add tests” / “write docs” ideas without a sharper underlying opportunity;
- treat a refactor as valuable unless it reduces risk, unlocks future work, or preserves behavior while simplifying the system;
- emit a detailed implementation plan;
- hide skipped gates;
- emit a seed when evidence is thin.

## Closure criteria

You are done only when:

- the selected mode is explicit;
- the leading direction is grounded in discovered context;
- shortlisted ideas have evidence and originality sources;
- Glaze and ASI were applied according to mode or explicitly skipped only in `audit-only` / blocked states;
- the chosen direction has a material delta, 10x frame, smallest proof-bearing artifact, cash-out type, and first proof signal;
- overlap has been checked or bounded;
- assumptions and risks are visible;
- the final output ends with IDR-v1;
- any emitted seed is a planning handoff seed, not an implementation plan.
