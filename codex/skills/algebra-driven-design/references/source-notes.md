# Source Notes and Provenance

This skill is an original synthesis for applying Algebra-Driven Design to architecture, codebase implementation, and agentic workflows. It is not a copy of any source. It draws on public descriptions of ADD, related functional programming practice, property-based testing, law discovery, and the Agent Skills format.

## Core ADD sources

### Algebra-Driven Design by Sandy Maguire

- Title: `Algebra-Driven Design: Elegant Software from Simple Building Blocks`
- Author: Sandy Maguire
- Publication: self-published, first edition 2020
- Public description: ADD is presented as a method for finding the essential algebra behind programs, reasoning about correctness with laws, deriving programs, finding observations, exploiting symmetry, and generating large test suites.
- Homepage/repository/package sources:
  - https://www.extrema.is/articles/haskell-books/algebra-driven-design
  - https://github.com/isovector/algebra-driven-design
  - https://hackage.haskell.org/package/algebra-driven-design

Important usage note: the public GitHub repository for the book states that the source material is licensed under Creative Commons Attribution-NonCommercial-NoDerivatives 4.0. This skill does not reproduce the book. It uses independent explanation and applied synthesis.

### Reviews and contextual explanations

- Michael Sperber review, Journal of Functional Programming / Cambridge Core, 2024.
  - Public summaries describe ADD as a method for designing combinator libraries using algebraic principles, with a first half on abstractions and laws and a second half on deriving implementations.
  - https://www.cambridge.org/core/product/31F9331736F7EE664C017E5C340DD0D6/core-reader
- Michael Sperber German review on funktionale-programmierung.de.
  - Describes combinator models, observation/equality, laws, QuickCheck, QuickSpec, and implementation derivation.
  - https://funktionale-programmierung.de/2024/01/22/review-maguire-algebra-driven-design.html

## Property-based testing and law discovery

### QuickCheck

- QuickCheck is a Haskell property-based testing library for testing program properties over randomly generated cases.
- Package/documentation:
  - https://hackage.haskell.org/package/QuickCheck
  - https://hackage-content.haskell.org/package/QuickCheck/docs/Test-QuickCheck.html
- Foundational paper:
  - Koen Claessen and John Hughes, `QuickCheck: A Lightweight Tool for Random Testing of Haskell Programs`, 2000.

### QuickSpec

- QuickSpec discovers candidate equational laws from Haskell functions using QuickCheck-style testing.
- Package/documentation:
  - https://hackage.haskell.org/package/quickspec-2.2

## Agent Skills format and skill packaging

### OpenAI Skills in ChatGPT

- OpenAI describes skills as reusable, shareable workflows that can include instructions, examples, and code, and can be automatically used when helpful.
- OpenAI states that skills follow the Agent Skills open standard and are supported in ChatGPT, Codex, and the API, with product availability depending on plan and workspace settings.
- Source:
  - https://help.openai.com/en/articles/20001066-skills-in-chatgpt

### Agent Skills specification

- Agent Skills are directories containing at least a `SKILL.md` file, plus optional `scripts/`, `references/`, and `assets/` directories.
- The standard uses progressive disclosure: metadata for discovery, `SKILL.md` for activation, and resources loaded as needed.
- Sources:
  - https://agentskills.io/specification
  - https://openagentskills.dev/docs/specification

### Microsoft Agent Framework skills documentation

- Microsoft documents Agent Skills as portable packages of instructions, scripts, and resources that provide specialized capabilities and domain expertise.
- It also describes script execution and warns that scripts should be sandboxed and governed in production.
- Source:
  - https://learn.microsoft.com/en-us/agent-framework/agents/skills

### OpenAI Agent Builder / Agents SDK / Evals

- OpenAI Agent Builder describes workflows as combinations of agents, tools, and control-flow logic.
- OpenAI Agents SDK documentation describes agentic applications involving tools, handoffs, state/traces, and orchestration.
- OpenAI agent evals documentation describes evaluation of agent workflows and trace grading.
- Sources:
  - https://platform.openai.com/docs/guides/agent-builder
  - https://platform.openai.com/docs/guides/agents-sdk/
  - https://platform.openai.com/docs/guides/agent-evals

## Internal design choices in this skill

This skill intentionally expands ADD beyond its original Haskell-heavy context into architecture, codebase refactoring, APIs, data systems, and agentic workflows. These extensions are applied synthesis, not claims that the original book covers every topic in this exact way.

The skill uses the following interpretation:

```text
ADD core = carriers + operations + observations + laws + implementation derivation + executable validation.
```

The skill's applied extensions:

```text
Architecture = law-preserving boundaries and runtime mechanisms.
Codebase implementation = carriers/operations/laws mapped to types/interfaces/tests.
Agentic workflow = algebra over plans, tools, evidence, validation, approval, memory, traces, and artifacts.
Skill creation = packaging the ADD method, knowledge, scripts, templates, and evals as an Agent Skill.
```

## Citation guidance for agents using this skill

When producing user-facing reports, cite current external sources if making factual claims about:

- OpenAI product behavior or availability;
- Agent Skills standard details;
- current tool/library versions;
- laws/regulations/standards;
- recent technology changes;
- current facts in researched domains.

For conceptual ADD analysis, cite source notes when relevant, but do not overclaim that a source states this skill's applied architecture or agentic extensions verbatim.
