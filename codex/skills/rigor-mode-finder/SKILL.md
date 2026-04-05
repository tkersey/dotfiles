---
name: rigor-mode-finder
description: Use this skill when you want Codex to derive semantically dense, task-specific rigor words and mode stacks for a non-trivial task. It analyzes the task’s domain, audience, stakes, failure modes, and workflow, then recommends compressed rigor modes, unpacked operating rules, and ready-to-paste prompts. Trigger for prompt design, writing, research, strategy, analysis, decision memos, reviews, planning, teaching, negotiation, product thinking, and other knowledge-work tasks. Do not trigger when the user only wants the task executed directly, when the rigor mode is already fixed, or when a trivial answer is enough.
---

# Rigor Mode Finder

Your job is to turn a task into a compact set of **rigor words** that meaningfully change agent behavior.

The objective is **not** to find impressive vocabulary. The objective is to find **semantically dense, procedural, domain-loaded terms** that compress a usable rubric into one word or short hyphenated term.

A good rigor word changes how the agent reasons or executes.
A weak word changes only tone.

## Core thesis

Good rigor words usually do one or more of these things:
- name a failure mode,
- impose a reasoning discipline,
- impose an execution constraint,
- impose an audience or interaction discipline,
- imply a standard of verification.

Prefer words with real professional or disciplinary use.
Do not force obscure vocabulary when a more standard word carries the same procedural weight.
Avoid decorative praise words unless the task truly needs stylistic steering.

## Selection criteria

Prefer candidate words that are:
- **semantically dense**: one word implies a multi-step rubric,
- **procedurally sharp**: the word changes behavior, not just style,
- **domain-fit**: it sounds native to the task’s real register,
- **complementary**: it combines well with other words,
- **non-redundant**: each selected word adds a distinct constraint,
- **usable in prompts**: a human would plausibly use it to steer an agent.

Penalize candidate words that are:
- vague,
- mostly aesthetic,
- near-synonyms of one another,
- so obscure that they reduce compliance,
- flattering but operationally empty.

## Diagnostic workflow

### 1) Frame the task
Extract:
- the task objective,
- the desired artifact or outcome,
- the audience,
- the stakes,
- reversibility vs irreversibility,
- whether the task is exploratory, evaluative, persuasive, operational, instructional, or diagnostic.

If key details are missing, proceed with the smallest reasonable set of assumptions and label them clearly.
Ask questions only when the missing information would materially change the resulting rigor modes.

### 2) Identify the task’s failure map
Name the most likely ways the task can go wrong.
Examples:
- unsupported claims,
- omission of important constraints,
- genericity,
- tone mismatch,
- performative depth,
- incoherence,
- overclaiming,
- fragile plans,
- lack of actionability,
- audience blindness,
- spurious pattern matching,
- failure to anticipate counterarguments,
- lack of verification,
- needless complexity,
- mis-sequencing,
- escalation risk.

### 3) Infer the dominant rigor dimensions
Classify which dimensions matter most:
- failure-mode discipline
- reasoning discipline
- execution discipline
- audience / rhetoric discipline
- verification discipline

### 4) Generate candidate rigor words
Generate at least **10 candidates** and usually **12–18**.
Pull from the most relevant professional registers for the task.
Use single words or short hyphenated compounds when they compress the rubric better.

Examples of valid types of words:
- negative evaluative words: `unsound`, `spurious`, `vacuous`, `brittle`, `myopic`
- reasoning words: `mechanistic`, `causal`, `falsifiable`, `dialectical`, `comparative`, `calibrated`
- execution words: `accretive`, `traceable`, `reversible`, `operational`, `sequenced`, `auditable`
- audience words: `legible`, `face-preserving`, `audience-calibrated`, `non-escalatory`, `didactic`

Do not make up pseudo-academic jargon.
Prefer words with enough real-world usage that a model is likely to have learned them as coherent concepts.

### 5) Score and filter the candidates
For each candidate, assess briefly:
- why it fits the task,
- what behavior it would likely induce,
- what category it belongs to,
- whether it is strong, medium, or weak.

Then select the most useful set.

### 6) Build the mode stacks
Construct exactly **three** stacks:

1. **Strict stack**
   - best for high-stakes, high-rigor use
   - usually includes at least one failure-mode word

2. **Balanced stack**
   - best default stack
   - usually the most reusable

3. **Exploratory stack**
   - keeps rigor but allows more divergence or creativity
   - should still include at least one constraining word

Each stack should usually contain **3–5 words**.
A strong default composition is:
- 1 failure-mode word,
- 1 reasoning word,
- 1 execution word,
- optional 1 audience or verification word.

Avoid stacks where multiple words do the same job.

### 7) Unpack the best stack into instructions
Translate the best stack into practical prompting language:
- what the agent should do,
- what it should avoid,
- what it should verify,
- what it should return.

The unpacking must make the words executable.

### 8) Provide ready-to-paste prompts
Provide at least:
- one concise prompt,
- one fuller prompt with sections.

Both prompts should reuse the chosen rigor words naturally.

## Output contract

Return the result in this order:

### Task Frame
- objective
- artifact / outcome
- audience
- stakes
- assumptions

### Failure Map
List the major failure modes for this task.

### Candidate Rigor Words
For each candidate, give:
- the word,
- category,
- one-line meaning in this task,
- why it is strong / medium / weak.

### Recommended Mode Stacks
Provide exactly three stacks:
- Strict
- Balanced
- Exploratory

For each stack, explain in 1–3 sentences why it fits.

### Best Stack Unpacked
Convert the best stack into operational instructions.

### Ready-to-Paste Prompts
Provide:
- concise version,
- fuller version.

### Words to Avoid
List 3–8 words that sound good but would likely be weak or misleading for this task.
Explain briefly why.

## Special guidance by task family

### Research / analysis
Prioritize words like:
- `falsifiable`
- `calibrated`
- `mechanistic`
- `causal`
- `comparative`
- `confound-aware`
- `traceable`
- `evidentiary`

### Writing / persuasion
Prioritize words like:
- `incisive`
- `substantiated`
- `economical`
- `audience-calibrated`
- `dialectical`
- `legible`
- `non-defensive`
- `face-preserving`

### Strategy / decision-making
Prioritize words like:
- `tractable`
- `robust`
- `option-preserving`
- `constraint-aware`
- `second-order`
- `scenario-conditioned`
- `defensible`
- `sequenced`

### Teaching / explanation
Prioritize words like:
- `scaffolded`
- `diagnostic`
- `concrete`
- `misconception-aware`
- `progressive`
- `didactic`
- `generative`
- `legible`

### Negotiation / interpersonal communication
Prioritize words like:
- `interest-based`
- `non-escalatory`
- `face-preserving`
- `sequenced`
- `asymmetric`
- `reversible`
- `anchored`
- `BATNA-aware`

### Planning / operations
Prioritize words like:
- `operational`
- `sequenced`
- `contingency-aware`
- `auditable`
- `owner-clear`
- `handoff-safe`
- `reversible`
- `deterministic`

### Review / critique
Prioritize words like:
- `adversarial`
- `unsound`
- `gap-seeking`
- `severity-ranked`
- `traceable`
- `evidence-backed`
- `remediative`
- `non-cosmetic`

## Decision rules
- Prefer one strong negative evaluative word when the task carries real downside risk.
- Prefer one execution word in every stack so the mode affects output, not only reasoning.
- Prefer one audience word when success depends on persuasion, diplomacy, teaching, or style.
- Use hyphenated compounds when they clearly compress a workflow better than a single word.
- Do not overfit the stack to cleverness; optimize for behavioral leverage.

## Hard rules
- Never confuse big with useful.
- Never present decorative vocabulary as rigor.
- Never choose words without explaining the behavioral change they are meant to induce.
- Never return only a word list; always produce at least one usable mode stack and prompt.
- Never ask more than two clarifying questions.
- If ambiguity remains, proceed with explicit assumptions.

## Response style
Be concrete, concise, and discriminating.
The user is trying to build a reusable prompting skill, not collect random thesaurus entries.
