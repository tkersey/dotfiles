---
name: logophile
description: Editing mode for clarity and semantic density; use for prompts, docs, specs, emails, and naming.
---

# Logophile

## When to use
- The user asks to tighten wording, improve clarity, or compress text.
- Drafts feel verbose, repetitive, bloated, or meandering.
- Names, titles, labels, or headings feel weak.
- The text should be readable in under 30 seconds.

## Motto (say once)
Precision through sophistication, brevity through vocabulary, clarity through structure.

## Quick start
1. State intent in one sentence.
2. Classify text type, audience, and goal (clarity/brevity/polish).
3. Capture constraints (must-keep, must-not, tone, length, format).
4. Run the E-SDD loop (Prune → Elevate → Structure → Verify).
5. If reduction exceeds 20%, report word/character delta.

## Output modes
- Fast pass: refined text only (plus delta if >20%).
- Annotated pass: refined text + key edits + delta (if >20%).

## E-SDD core loop
Distill:
- State the intent in one sentence.

Densify:
- Prune: remove redundancy, hedges, filler.
- Elevate: swap generic verbs/adjectives for precise terms.

Shape:
- Structure: front-load the main action; keep sentences atomic.
- Parallelize: align repeated phrases and list items.

Verify:
- Preserve facts, numbers, and required tokens.
- Preserve code blocks/quotes/format.

## Guardrails
- Don’t change intent.
- Don’t “upgrade” vocabulary at the cost of precision.
- Don’t compress away obligations, risks, or scope.

## Constraint capture template
```
Constraints:
- Must keep:
- Must not change:
- Tone:
- Length target:
- Format requirements:
- Keywords to include:
- Keywords to avoid:
```

## Common compressions
- “in order to” → “to”
- “due to the fact that” → “because”
- “is able to” → “can”
- “there is/are” → concrete subject + verb
- nominalization → verb (“conduct an analysis” → “analyze”)

## Deliverable
Fast pass:
- Refined passage.
- Delta if reduction exceeds 20%.

Annotated pass:
- Refined passage.
- Key edits (lexical/structural).
- Delta if reduction exceeds 20%.

## Reporting template
```
Type:
Audience:
Goal:
Edits:
- Lexical:
- Structural:
Delta:
- Words:
- Characters:
Semantic risks:
- ...
```

## Examples
Before:
You are asked to provide a comprehensive response that carefully explains all of the steps needed in order to troubleshoot the reported issue.

After:
Explain the steps to troubleshoot the issue.
