# Research Basis for Harness

This file explains the design stance behind the Harness skill.

Harness is built from primary-source guidance on agent construction, tool design, context management, and evaluation. It intentionally turns those findings into a stricter review style than a generic architecture summary.

## Core principles carried into Harness

## 1) Start simpler than you think

OpenAI and Anthropic both recommend starting with the simplest architecture that can work.

Harness therefore assumes:
- a single agent with strong tools is the default
- multi-agent designs should be justified by real prompt complexity, tool overload, or clear specialization needs
- adding agents is not a free win; it increases control and debugging complexity

## 2) Prompt quality is about control, not prose

The best sources converge on the same idea:
- the system prompt should be clear and direct
- it should sit at the “right altitude”
- it should define the job without becoming a giant brittle program

Harness therefore rewards prompts that:
- state goal, context, constraints, and done criteria
- structure instructions clearly
- handle important edge cases
- tell the model when to escalate or stop

Harness penalizes prompts that:
- are too vague
- assume hidden context
- encode lots of brittle branching logic better expressed in code, tools, or tests

## 3) Tools are contracts, not just functions

Modern agent guidance treats tools as one of the main determinants of reliability.

Harness therefore gives heavy weight to:
- one responsibility per tool
- explicit descriptions
- unambiguous parameter names
- strict validation
- good error messages
- high-signal outputs
- namespacing and boundary clarity when tool surfaces get large

Harness is deliberately harsh on overlapping tools because overlap often creates tool-selection failures that people try to patch with more prompting.

## 4) Context is finite and should be curated

Recent guidance emphasizes context engineering rather than just prompt engineering.

Harness therefore treats the following as real design issues:
- giant tool payloads
- raw dumps of low-value fields
- no pagination or filtering for large results
- memory or retrieval without clear scoping

A system can have a good prompt and still be unreliable because the model is repeatedly forced to reason over low-signal context.

## 5) Guardrails and side-effect control matter

Guardrails are not optional polish for systems that can act.

Harness penalizes:
- destructive tools with no confirmation path
- weak tool-level safeguards
- unclear human escalation rules
- absent handling for unsafe or malformed requests

## 6) No evidence loop, no high score

OpenAI’s current guidance on traces, graders, datasets, and skill evals strongly suggests that mature agent systems need runtime evidence, not just a nice prompt and a good demo.

That is why Harness uses score caps when:
- traces are absent
- evals are absent
- critical process checks are absent

This is an opinionated choice, but it is grounded in the idea that unobserved systems are easy to overrate.

## Source map

The stance above is primarily grounded in these sources:

- OpenAI — **Agent Skills – Codex**
  - Skills are directories with `SKILL.md`, optional scripts, references, and assets.
  - Descriptions matter because they drive implicit skill matching.
  - Official guidance recommends focused skills and instructions-first design.

- OpenAI — **Best practices – Codex**
  - Good guidance is reusable, practical, and grounded in clear goals, constraints, and done criteria.
  - Complex tasks benefit from planning and repository-specific guidance.

- OpenAI — **A practical guide to building AI agents**
  - Agent foundations are model + tools + instructions.
  - Tools should be standardized, reusable, and well-defined.
  - Start with a single agent; split only when prompt complexity or tool overload truly requires it.
  - Instructions should come from real operating documents, define explicit actions, and capture edge cases.

- OpenAI Agents SDK — **Tools**
  - Tool descriptions should be short and explicit.
  - Strict input validation is a design advantage.
  - One responsibility per tool improves reasoning.

- OpenAI Agents SDK — **Guardrails**
  - Tool, input, and output guardrails are distinct and should be applied at the right workflow boundaries.

- OpenAI — **Evaluate agent workflows** and **Evaluation best practices**
  - Traces, graders, datasets, and eval runs form the quality loop.
  - Combine metrics with human judgment.
  - Avoid vibe-based evaluation.

- OpenAI — **Testing Agent Skills Systematically with Evals**
  - Skills should be evaluated like prompts.
  - Success should be defined across outcomes, process, style, and efficiency.
  - Trigger behavior and runtime behavior should be measured, not guessed.

- Anthropic — **Building effective agents**
  - Successful systems tend to use simple, composable patterns.
  - Workflows and agents are distinct; added autonomy should be justified.
  - The augmented LLM is the basic unit: model plus retrieval, tools, and memory.

- Anthropic — **Writing effective tools for agents**
  - Tool boundaries, namespacing, token-efficient outputs, and prompt-engineered descriptions materially affect agent performance.
  - Tool outputs should return high-signal context, not irrelevant identifiers or dumps.
  - Small refinements to tool descriptions can produce large gains.

- Anthropic — **Effective context engineering for AI agents**
  - Context is finite.
  - The system prompt should be clear and use simple language at the right altitude.
  - Good context engineering is about the smallest high-signal set of tokens that still drives correct behavior.

- Yao et al. — **ReAct: Synergizing Reasoning and Acting in Language Models**
  - Interleaving reasoning and actions can improve performance and interpretability.
  - This supports reviewing not only final outputs, but also action trajectories and tool use.

## What is intentionally opinionated in Harness

These are design choices, not direct quotations from any single source:
- no traces/evals means no elite score
- unclear tool surfaces are a first-order defect
- multi-agent complexity should be presumed guilty until justified
- prompt bloat is usually a symptom of weak architecture, not sophistication

That is the point of this skill: it should bring judgment, not just description.
