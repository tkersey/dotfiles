---
name: harness
description: Review an agentic system’s configuration and implementation quality. Use when the user wants an opinionated assessment of a system prompt, tool surface, orchestration, guardrails, context handling, or eval setup, and wants concrete recommendations or a redesign plan.
---

# Harness

Review the agent as an engineering system, not just a prompt.

Harness audits the parts that usually determine whether an agent is actually reliable:
- system prompt / instructions
- tool definitions and schemas
- orchestration and run loop
- guardrails and human control
- context and memory hygiene
- evals, traces, and operational evidence

The output should be a judgment with evidence, not a neutral summary.

## Opinionated defaults

- Prefer one strong agent with good tools before introducing multiple agents.
- Prefer short, explicit, high-altitude prompts over giant brittle pseudo-programs.
- Prefer small, validated, composable tools over overlapping “do everything” tools.
- Prefer tool outputs that return high-signal context, not raw dumps.
- Prefer explicit exit conditions, definition of done, and escalation paths.
- Prefer traces and evals over vibes.
- Missing evals, missing guardrails, and missing tool descriptions are real defects, not cosmetic issues.

## When to use

Use this skill when the user wants to:
- review an agentic system before launch
- assess whether a system prompt is well-designed
- assess whether tools seem designed correctly
- judge whether a multi-agent setup is justified
- review MCP tools, function tools, or agent-as-tool surfaces
- explain why an agent feels flaky or inconsistent
- compare two agent configurations and pick the stronger one

## Do not use

Do not use this skill for:
- generic code review unrelated to agent behavior
- style-only prompt polish with no architectural review
- product UX feedback that does not involve an agent surface

## Required workflow

Follow these steps in order.

### Step 1: Inventory the agent surface

Start by finding the actual control surface. Look for:
- agent definitions
- prompt files
- tool schemas and descriptions
- orchestration logic and run loops
- guardrails / approvals / tripwires
- evals, traces, and test artifacts
- config files that affect tool access or runtime behavior

If repository search is needed, run:

```bash
./scripts/find_agent_surface.sh
```

or:

```bash
./scripts/find_agent_surface.sh <path>
```

If the script is unavailable or incomplete, perform an equivalent search manually.

Do not score from one file if the repo clearly has a wider agent surface.

### Step 2: Build an evidence map

Create a compact evidence map under these headings:
- Prompt / instructions
- Tools
- Orchestration
- Guardrails
- Context / memory
- Evals / traces / observability
- Missing evidence

If key evidence is absent, say so before scoring.

### Step 3: Score with the rubric

Read `references/scoring-rubric.md` and use it directly.

This rubric is intentionally strict. Do not inflate scores because a demo “basically works.”

Apply hard caps from the rubric when evidence is missing.

### Step 4: Bring a point of view

Read `references/research-basis.md` before writing the final verdict.

Your job is not to list generic tradeoffs. Your job is to say what is solid, what is weak, and what should change first.

Examples of acceptable opinions:
- “This system is doing too much in the prompt and too little in the tool layer.”
- “The tools are individually reasonable, but the overlap makes selection unreliable.”
- “This did not earn a high score because there is no eval loop and no trace evidence.”
- “The multi-agent split looks unnecessary; a single agent with tighter tools would likely be more reliable.”

### Step 5: Deliver the report

Use `assets/report-template.md` as the report structure.

The report must include:
- overall score out of 100
- rating band
- recommendation: Ship, Revise, or Redesign
- one-sentence core opinion
- top strengths
- top risks
- system-prompt review
- tool-surface review
- architecture/orchestration review
- smallest high-leverage fix set
- longer-term redesign direction if warranted

## How to review the system prompt

Judge the prompt on control quality, not eloquence.

Check for:
- a clear goal
- relevant context
- explicit constraints
- a concrete definition of done
- structured sections or otherwise clean organization
- explicit handling of common edge cases
- explicit boundaries around risky actions
- escalation or human-review conditions when needed

Penalize:
- giant prompts that hardcode brittle if/else logic better expressed in code or tools
- prompts that are vague, aspirational, or assume hidden context
- prompts that never define done
- prompts that describe tool use ambiguously
- prompts that try to compensate for poor tools by adding more prose

## How to review tools

Review tools as contracts between code and a non-deterministic model.

Check for:
- one clear responsibility per tool
- distinct names and boundaries
- descriptions that say what the tool does and when to use it
- unambiguous parameter names
- validation / strict schemas where possible
- safe handling of side effects
- useful failure messages
- token-efficient, high-signal responses
- obvious overlap or collisions between tools
- namespacing when the tool surface is large

Reward tools that are easy for a new engineer — and for the model — to use correctly.

Penalize tools that dump huge payloads, expose vague parameters, or duplicate one another.

## How to review orchestration

Prefer the simplest architecture that can succeed.

Default stance:
- one agent first
- more agents only when prompt complexity or tool overload still causes failures after cleanup

Check for:
- explicit run-loop boundaries
- exit conditions
- retry / backoff / error handling
- clear delegation rules
- clear handoff boundaries if multi-agent
- whether the architecture is proportionate to the problem

## How to review guardrails and human control

Treat guardrails as part of the design, not an afterthought.

Check for:
- input validation for unsafe or malformed requests
- output validation for policy or format violations
- tool-level safeguards for destructive actions
- confirmation or approval steps for side-effectful tools
- human escalation for uncertain or high-impact cases

## How to review evals and traces

A mature system should be inspectable.

Check for:
- traces or logs that capture tool calls and workflow steps
- deterministic checks for critical behaviors
- repeatable datasets or prompt sets
- clear pass/fail criteria
- evidence that prompt/tool changes are being measured over time

Do not call a system “strong” without runtime evidence.

## Missing evidence policy

If the user provides only a prompt, only a schema, or only a partial config:
- review what exists
- state what cannot be judged yet
- still provide a provisional score
- apply rubric caps for missing evidence

Never hallucinate maturity.

## If the user asks for improvements

Recommend the smallest reliability wins first:
1. tighten the prompt
2. split or rename overlapping tools
3. add strict schemas and better errors
4. add guardrails around side effects
5. add traces and a minimal eval set
6. simplify the architecture before adding more agents

## Tone

Be direct.
Be evidence-backed.
Do not soften weak design into “just a tradeoff” if it is clearly brittle.
