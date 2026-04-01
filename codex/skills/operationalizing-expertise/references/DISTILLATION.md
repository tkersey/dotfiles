# Multi-Model Distillation

The key insight: Different models have different analytical strengths. Use all three.

## Why Three Models?

| Model | Lens | Strength |
|-------|------|----------|
| **GPT** | Systematic/Optimization | Formal structure, decision procedures |
| **Claude** | Philosophical/Epistemic | Nuance, underlying beliefs, axioms |
| **Gemini** | Minimal/Operational | Compact extraction, actionable steps |

**Triangulation Rule:** If all three models extract the same insight, it's probably real. If only one does, it might be model bias.

## The Distillation Prompt

### Master Prompt Template

```markdown
# [Expert Name] Methodology Distillation

## Context
You are analyzing the complete works of [EXPERT NAME], a renowned expert in [DOMAIN].
They are known for [KEY CONTRIBUTION].

## Attached Sources
1. [Source 1 name] — [description, word count]
2. [Source 2 name] — [description, word count]
3. [Source 3 name] — [description, word count]
[...]

## Your Task
Extract a systematic, actionable methodology from these sources.

---

## Required Sections

### 1. Axioms (3-5 items)
Non-negotiable beliefs that underpin [EXPERT]'s approach.
Format:
- **Axiom Name**: One-line statement
  - Evidence: Direct quote with source reference
  - Implication: What this means for practice

### 2. Operators (8-15 items)
Recurring cognitive moves [EXPERT] applies. For each:

#### [Symbol] [Operator Name]
- **Definition**: One sentence
- **When to use**: 3-5 trigger conditions
- **Failure modes**: 2-4 ways it can go wrong
- **Quote anchors**: 2-3 quotes demonstrating use
- **Related operators**: What it pairs with

### 3. Anti-Patterns (5-10 items)
What [EXPERT] explicitly warns AGAINST.
Format:
- **Anti-pattern name**: What NOT to do
  - Why it fails: [EXPERT]'s reasoning
  - Quote: Direct evidence

### 4. Terminology (15-30 items)
Key jargon with definitions.
Format:
| Term | Short Definition | Full Explanation |
|------|------------------|------------------|

### 5. Decision Procedures (3-5 items)
Explicit step-by-step processes [EXPERT] describes.
Format:
```
PROCEDURE: [Name]
1. [Step]
2. [Step]
3. [Step]
IF [condition] THEN [action]
```

---

## Output Format
- Use ## headers for sections
- Include direct quotes with source citations
- Mark inferences explicitly as [inference]
- Prefer [EXPERT]'s exact terminology
```

## Model-Specific Instructions

### For GPT

Add to prompt:
```
Focus on:
- Formal decision procedures
- Optimization objectives (what is being maximized?)
- Systematic loops and checkpoints
- Quantitative criteria where mentioned

Output style: Systematic, structured, with explicit algorithms.
```

### For Claude (Opus)

Add to prompt:
```
Focus on:
- Underlying epistemology and beliefs
- Philosophical foundations
- Nuanced distinctions [EXPERT] makes
- The "why" behind methodological choices

Output style: Philosophical, nuanced, with rich context.
```

### For Gemini

Add to prompt:
```
Focus on:
- Minimum viable kernel
- Most actionable operators
- Compact, executable procedures
- What can be applied immediately

Output style: Minimal, operational, action-oriented.
```

## Processing Raw Responses

### Batch Processing

If source material exceeds context:

```
BATCH 1: Sources 1-3
"Analyze these sources. Extract operators and axioms.
Output partial distillation for later synthesis."

BATCH 2: Sources 4-6
"Continuing analysis. Here are sources 4-6.
Add to previous extraction, note new operators."

FINAL: Synthesis
"Synthesize all batches into unified distillation.
Resolve conflicts, merge duplicates, note coverage gaps."
```

### Response Storage

```
raw_responses/
├── gpt_responses/
│   ├── batch_1.md
│   ├── batch_2.md
│   └── synthesis.md
├── opus_responses/
│   ├── batch_1.md
│   └── synthesis.md
└── gemini_responses/
    └── single_pass.md
```

Store EVERYTHING. Raw responses contain insights you'll mine later.

## Quality Indicators

### Good Distillation Signs
- Direct quotes outnumber paraphrases
- Operators have specific trigger conditions
- Axioms are falsifiable (you could disagree)
- Anti-patterns have clear failure mechanisms
- Terminology includes expert's actual words

### Red Flags
- Mostly model's own framing
- Generic advice not specific to expert
- No direct quotes
- Operators without failure modes
- Axioms that are tautologies

## Iteration

### First Pass → Refinement

After initial distillation:

```
Review this distillation against the sources.

1. Which operators have weak evidence?
2. Which axioms might be overstated?
3. What did we miss that the expert emphasizes?
4. What terminology is still unclear?

Revise with corrections and additions.
```

### Cross-Model Comparison

After all three distillations:

```
Compare these three distillations:
- GPT's version
- Claude's version
- Gemini's version

Create a COMPARISON table:
| Insight | GPT | Claude | Gemini | Consensus? |
|---------|-----|--------|--------|------------|

Note where they AGREE (high confidence)
and DISAGREE (needs resolution).
```
