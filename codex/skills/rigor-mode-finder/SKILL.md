---
name: rigor-mode-finder
description: Use this skill when the task is to discover which semantically dense rigor words and compressed rubrics should prime an agent for a particular job. Trigger for requests like find the best words for this task, synthesize a rigor stack, translate a task into doctrine words, or compare strict versus light rigor modes for research, writing, analysis, coding, strategy, design, operations, teaching, or negotiation.
---

# Rigor Mode Finder

This skill does **mode synthesis**, not task execution.

Its job is to read a task, infer the dominant failure pressures, and produce a compact rigor-word stack that can prime another agent into a sharper operating mode.

## Core thesis

Treat good rigor words as **compressed rubrics**.

Strong words usually do one of three things:
1. name a failure mode
2. name a reasoning discipline
3. name an execution discipline

The best stacks combine all three.

## Operating procedure

1. Read the task and classify:
   - task family
   - audience
   - stakes
   - uncertainty profile
   - likely failure modes

2. Infer the dominant failure pressures:
   - hallucination / false confidence
   - vagueness / vacuity
   - poor decomposition
   - weak causality
   - hidden assumptions
   - poor source discipline
   - style over substance
   - operational fragility
   - edge-case blindness
   - ethical / strategic / reputational risk
   - mismatch between ambition and evidence

3. Propose:
   - one recommended rigor stack
   - one stricter variant
   - one lighter variant

4. Unpack each word into observable behavior.

5. Produce a prompt-ready doctrine block.

## Selection rules

Prefer words that are:
- semantically dense
- procedural rather than merely flattering
- loaded with institutional review standards
- discriminative for the task at hand

Avoid words that mostly improve tone rather than procedure, such as:
- nuanced
- sophisticated
- insightful
- elegant
- thoughtful
unless the task really needs them.

## Output contract

Return sections in this order:
- Task Reading
- Dominant Failure Pressures
- Recommended Rigor Stack
- Why These Words
- Unpacked Doctrine
- Prompt-Ready Mode Block
- Stricter Variant
- Lighter Variant
- Words to Avoid

## Hard rules
- Do not return a generic stack if the task has a distinct risk profile.
- Do not recommend more words than the task can realistically support.
- Prefer 3 to 5 words for the main stack unless the user explicitly asks for a larger lexicon.
- Separate failure-mode words from reasoning-mode words and execution-mode words when helpful.
