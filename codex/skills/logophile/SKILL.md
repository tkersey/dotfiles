---
name: logophile
description: Logophile editing mode for tightening wording, clarity, brevity, and semantic density; use for prompts, docs, specs, emails, naming, or any text that feels verbose, fuzzy, or low-signal.
---

# Logophile

## When to use
- The user asks to tighten wording, improve clarity, or compress text. ✂️
- Drafts feel verbose, repetitive, bloated, or meandering. 🧹
- The goal is high semantic density with clean structure. 💎
- Names, titles, labels, or headings feel weak or generic. 🏷️
- The text must be readable in under 30 seconds. ⏱️

## Motto (repeat before editing)
Precision through sophistication, brevity through vocabulary, clarity through structure. ✨

## Quick start
1. Say the Motto once and state the intent in a single sentence.
2. Classify text type, audience, and goal (clarity, brevity, polish).
3. Capture constraints (must-keep, must-not, tone, length).
4. Run the E-SDD loop (Prune → Elevate → Structure → Verify).
5. Report key edits and word/character delta if reduction exceeds 20%.

## Output modes
- Fast pass ⚡: deliver the refined text only (plus delta if >20%).
- Annotated pass 🧪: include edits, deltas, and a brief rationale.
- Ask which mode to use when stakes or constraints are unclear.

## E-SDD (Enhanced Semantic Density Doctrine) — core technique
Motto: Precision through sophistication, brevity through vocabulary, clarity through structure. ✨

Doctrine: every edit must increase semantic weight per word without changing meaning or breaking constraints.

Pillars:
- Lexical elevation 🔧: replace vague phrases with precise terms.
- Euphonic architecture 🎵: improve rhythm and parallelism.
- Rhetorical precision 🧭: use structure to sharpen meaning.
- Erudite clarity 💎: sophistication without obscurity.

E-SDD litmus:
- Could this be understood faster without losing meaning?
- Did each word earn its place?
- Did the motto get stronger, not weaker?

## E-SDD core loop (default)
Distill:
- State the intent in 1 sentence.

Densify:
- Prune: remove redundancy, hedges, filler, and throat-clearing.
- Elevate: replace generic verbs/adjectives with precise alternatives.

Shape:
- Structure: front-load key information and keep sentences atomic.
- Parallelize: align repeated phrases and list items.

Verify:
- Run the Revision checklist and guardrails.

## Revision checklist
- Brevity: remove hedges, filler, and duplicate ideas.
- Clarity: front-load the main action and subject.
- Structure: favor short, atomic sentences and parallel lists.
- Tone: preserve voice and formality.
- Invariants: keep facts, numbers, and required phrases intact.
- Format: preserve code blocks, quotes, and formatting requirements.

## Style guardrails (capture first)
```
Constraints:
- Must keep:
- Must not change:
- Tone (formal/casual/neutral):
- Length target (words/chars/lines):
- Format requirements (bullets, table, email, spec):
- Keywords to include:
- Keywords to avoid:
```

## Scoring rubric (mini)
- Density score (1-5): how much meaning per word improved.
- Clarity score (1-5): how quickly the point is understood.
- Tone match (1-5): alignment with requested voice.
- Delta: word and character change (report if >20%).

## E-SDD anti-patterns (avoid)
- Fancy words that blur meaning.
- Compression that drops obligations, risks, or scope.
- Rhythm improvements that distort tone.

## Compression tactics
- Turn long preambles into a single direct verb phrase.
- Swap prepositional phrases for stronger verbs.
- Combine repeated clauses into one clear line.
- Replace "there is/are" with concrete subjects.

## Syntactical density moves (cheat sheet)
- Convert nominalizations to verbs: "conduct an analysis" -> "analyze".
- Collapse empty expletives: "there is/are" -> concrete subject + verb.
- Convert "is able to" -> "can".
- Replace "in order to" -> "to".
- Move purpose clauses to verb phrases: "for the purpose of debugging" -> "to debug".
- Merge parallel clauses into one sentence with shared subject/verb.
- Prefer active voice when it shortens without changing responsibility.
- Strip "the fact that", "the process of", "the ability to".

## Naming tactics (labels, titles, headings)
- Favor concrete nouns and strong verbs.
- Strip filler words ("very", "really", "in order to").
- Use parallel structure across sibling headings.
- If needed, generate 5-10 variants and select the tightest.

## Activation cues
- "tighten" / "make concise" / "shorten" / "trim"
- "improve wording" / "clarity" / "polish this"
- "too verbose" / "bloated" / "wordy"
- "make this punchier" / "stronger" / "crisper"
- "rename" / "title" / "label" / "headline"

## Reference patterns
Lexical swaps:
- "very important" -> "paramount"
- "in order to" -> "to"
- "due to the fact that" -> "because"

Structural tightening:
- "Please carefully review..." -> "Review carefully."
- "At this point in time..." -> "Now."

Tone alignment:
- Casual: "Coffee to discuss?"
- Formal: "Meeting requested: quarterly objectives."

## Metrics + proof
- Word delta and character delta when trimming exceeds 20%.
- Note any semantic risk and how meaning was preserved.
- Mention readability or structure shifts if relevant.
- Add a motto check when providing annotated output.

## Deliverable format
Fast pass:
- Refined passage.
- Word/character delta if reduction exceeds 20%.

Annotated pass:
- Refined passage.
- Key edits (lexical, structural, rhetorical).
- Word/character delta if reduction exceeds 20%.
- Optional scores (density, clarity, tone).
- Motto check (precision/brevity/clarity).

## Reporting template
```
Type: <prompt/doc/spec/email/name>
Audience: <who>
Goal: <clarity/brevity/polish>
Edits:
- Lexical:
- Structural:
- Rhetorical:
Delta:
- Words:
- Characters:
Scores:
- Density:
- Clarity:
- Tone:
Motto check:
 - Precision:
 - Brevity:
 - Clarity:
Semantic risks:
- ...
```

## Examples
### Prompt rewrite
Before:
You are asked to provide a comprehensive response that carefully explains all of the steps needed in order to troubleshoot the reported issue.

After:
Explain the steps to troubleshoot the issue.

Edits:
- Lexical: removed "comprehensive" and "carefully".
- Structural: replaced a long clause with a direct imperative.

### Spec snippet
Before:
The system should be able to handle a very large number of requests at the same time without degrading performance in a noticeable way.

After:
The system must handle high concurrent request volume without noticeable performance degradation.

Edits:
- Lexical: "very large number" -> "high".
- Structural: tightened clause order.

### Email snippet
Before:
Hi team, I just wanted to reach out and ask if you could please send the updated report when you get a chance. Thanks so much.

After:
Hi team, please send the updated report when you can. Thanks.

Edits:
- Lexical: removed softeners.
- Tone: kept polite but direct.

### Micro-compressions (syntax moves)
- Before: There are three reasons that we need to delay the launch.
  After: We need to delay the launch for three reasons.
- Before: In the event that the build fails, it is recommended that you retry.
  After: If the build fails, retry.
- Before: The purpose of this document is to provide guidance.
  After: This document provides guidance.
- Before: The team is of the opinion that the change is necessary.
  After: The team believes the change is necessary.
- Before: We conducted an analysis of the data.
  After: We analyzed the data.
- Before: It is possible that the service will be unavailable.
  After: The service may be unavailable.
- Before: At this point in time, we are unable to proceed.
  After: We cannot proceed.
- Before: Due to the fact that tests are flaky, we are delaying the release.
  After: Because tests are flaky, we are delaying the release.
- Before: We have made a decision to move forward.
  After: We decided to move forward.
- Before: The logs are used for the purpose of debugging.
  After: The logs are used to debug.

### Deep-dive densification (multi-step)
Before:
We are writing to let you know that the migration will happen next week, and because it affects multiple teams, it is important that everyone reads the instructions carefully and confirms their readiness in advance.

After:
The migration runs next week. Because it affects multiple teams, read the instructions carefully and confirm readiness in advance.

Edits:
- Clause split: pulled the schedule into its own sentence.
- Verb-first: "We are writing to let you know" -> removed.
- Purpose compression: "it is important that everyone reads" -> imperative.
- Clarity: anchored the timeline at the start.

## Guardrails
- Preserve mandated language (legal terms, RFC keywords, brand voice).
- Do not change intent or factual meaning.
- Keep citations, numbers, and code tokens intact.
