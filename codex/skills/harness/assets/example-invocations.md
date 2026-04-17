# Example invocations

Use these prompts with `$harness` or by invoking the skill implicitly.

## Full architecture review
Review this agentic system. Focus on the system prompt, tool design, orchestration, guardrails, and eval quality. Use Harness and bring an opinion.

## Prompt-first review
Use Harness to review this system prompt. Tell me whether it is too vague, too brittle, or about right. Score it provisionally and tell me what evidence is still missing.

## Tool-surface review
Use Harness to review the tool layer in this repo. Do the tools seem designed correctly? Focus on overlap, descriptions, schemas, side effects, and response shape.

## Pre-launch audit
Use Harness to decide whether this agent is ready to ship. If not, tell me the minimum change set I should make before launch.

## Compare two versions
Use Harness to compare these two agent configs and pick the stronger one. Explain which one has the better prompt, better tools, and better evidence loop.
