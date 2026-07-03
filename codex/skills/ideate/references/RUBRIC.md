# Idea Evaluation Rubric

Score only after evidence gathering. Arithmetic helps ranking, but judgment owns the final call.

## Layers

1. **Ordinary codebase value** — useful, evidenced, feasible, maintainable.
2. **Breakthrough quality** — Glaze and ASI materially transformed the idea into a stronger, proof-bearing direction.

## Core criteria

| Criterion | Weight | Question |
|---|---:|---|
| Useful | 2.0x | Does it solve real user/maintainer pain, risk, or opportunity? |
| Evidence strength | 2.0x | Is it grounded in concrete repo/product signals? |
| Leverage | 2.0x | Does it unlock future work, reduce repeated friction, or lower future risk? |
| Pragmatic | 2.0x | Is the first proof step realistic? |
| User / maintainer value | 2.0x | Will the intended beneficiary care? |
| Originality / latentness | 1.5x | Is it non-obvious but natural after seeing evidence? |
| Architecture fit | 1.5x | Does it fit existing system shape? |
| Validation cheapness | 1.5x | Can we learn early without full commitment? |
| Behavior stability | 1.5x | Can risk be contained or made behavior-preserving? |
| Maintenance delta | 1.25x | Does it reduce or contain future burden? |
| Strategic fit | 1.25x | Does it reinforce the project direction? |

## Breakthrough criteria

| Criterion | Weight | Question |
|---|---:|---|
| Glaze material delta | 2.5x | Did the idea gain a new frame, invariant, mechanism, interface, artifact, architecture move, or ordering strategy? |
| ASI cash-out | 2.5x | Did the 10x frame collapse into a concrete mechanism, interface, proof surface, or strategy? |
| Ambition compression | 2.0x | Is the first artifact small while preserving the larger insight? |
| System leverage | 2.0x | Does it change a leverage surface, coordination pattern, proof surface, or option set? |
| Proof signal clarity | 2.0x | Can we observe meaningful evidence early? |
| Grounded boldness | 1.75x | Is it bolder without leaving repo evidence? |
| Dominance over baseline | 1.75x | Is the escalated idea clearly better than its baseline? |
| Naming / framing power | 1.0x | Is the frame crisp enough for future planners? |

## Scoring guide

- **5**: strong evidence, high value, clear fit, material escalation, obvious next-step candidate.
- **4**: good evidence/value with credible material delta and manageable uncertainty.
- **3**: plausible but mixed on evidence, value, fit, or escalation.
- **2**: weak, generic, high-risk, low-leverage, or only superficially escalated.
- **1**: cut.

## Hard cuts

Cut if:

- no repo/product evidence and speculation was not requested;
- just “add tests” or “write docs” without a sharper opportunity;
- refactor has no behavior-preservation strategy;
- duplicate of existing roadmap/TODO/recent work without a compelling delta;
- requires a large rewrite before value appears;
- optimizes an area with no evidence of pain;
- depends on miracle assumptions;
- creates more complexity than value;
- cannot be validated until late;
- is mostly implementation detail disguised as strategy;
- Glaze adds rhetoric but no material delta;
- ASI cannot produce a mechanism/interface/proof surface/strategy;
- ASI artifact is too large, vague, or untestable;
- escalated version loses evidence contact.

## Escalation failure labels

- **Glaze failed: no material delta**
- **Glaze failed: rhetoric only**
- **ASI failed: no cash-out**
- **ASI failed: too large**
- **ASI failed: ungrounded**
- **ASI failed: no proof signal**

## Tie-breakers

Prefer:

1. smallest artifact that preserves largest insight;
2. cheapest credible validation;
3. asymmetric leverage;
4. proof surface;
5. coordination surface;
6. reversibility;
7. clarity of ownership;
8. portfolio diversity;
9. behavior stability.

## Mode-aware ranking

- `fast`: optimize for signal, reversibility, and immediate learning.
- `standard`: balance ordinary value and breakthrough quality.
- `deep`: reward systemic leverage and proof-bearing novelty, but still cut ungrounded ambition.
- `audit-only`: do not force a winner; rank signal hypotheses by evidence quality.
