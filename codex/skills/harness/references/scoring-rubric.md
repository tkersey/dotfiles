# Harness Scoring Rubric

This rubric is intentionally strict.

An agentic system is not high quality because it looked good in one demo. It is high quality when its prompt, tools, control flow, and evidence loop make good behavior likely and bad behavior observable.

## Score bands

- **90–100: Disciplined**
  - Strong prompt, strong tool contracts, strong control surface, and real evaluation evidence.
- **80–89: Strong**
  - Solid design with manageable defects. Worth shipping with targeted fixes.
- **65–79: Serviceable but shaky**
  - Likely useful, but reliability risks are still material.
- **50–64: Brittle**
  - Important parts of the system are under-specified, overlapping, or unobserved.
- **0–49: Unsound**
  - The system should be redesigned before anyone trusts it.

## Recommendation mapping

- **Ship**: usually 85+
- **Revise**: usually 65–84
- **Redesign**: usually below 65

Override those defaults if a hard-cap condition clearly dominates.

## Hard caps

Apply these caps even if other parts look good.

- **No traces or repeatable eval evidence:** cap at **79**
- **Side-effectful tools without confirmations / approvals / guardrails:** cap at **69**
- **No explicit exit condition or no definition of done:** cap at **64**
- **Major overlap or ambiguity in key tools:** cap at **64**
- **Review based on only a prompt snippet or partial artifact:** provisional only, cap at **74**

These caps are opinionated by design. Harness assumes that reliability without evidence is overstated.

## Dimensions

## 1) System prompt and instructions — 20 points

### Excellent (17–20)
- Clear goal, context, constraints, and done condition
- Prompt is organized and easy for the model to follow
- Edge cases and escalation points are covered
- Language is direct and concrete
- The prompt guides behavior without turning into brittle pseudo-code

### Adequate (11–16)
- Goal and constraints are mostly clear
- Some structure exists
- A few important edge cases or done criteria are missing
- The prompt is somewhat verbose or somewhat vague, but still usable

### Weak (0–10)
- Vague, aspirational, or contradictory
- Missing done condition
- Assumes hidden context
- Bloated with brittle control logic
- Uses prose to compensate for weak tools

## 2) Tool surface and schemas — 20 points

### Excellent (17–20)
- Tools have clear names, boundaries, and responsibilities
- Descriptions explain what the tool does and when to use it
- Parameters are unambiguous and validated
- Tool responses are high-signal and token-efficient
- Tool overlap is minimal and intentional

### Adequate (11–16)
- Tools mostly make sense, but some overlap or vague parameters remain
- Validation exists for key tools, but not consistently
- Responses are usable but somewhat noisy

### Weak (0–10)
- Tools overlap heavily or compete with one another
- Names and descriptions are vague
- Parameters are ambiguous
- Validation is weak or absent
- Responses dump raw payloads or irrelevant fields

## 3) Orchestration and run loop — 15 points

### Excellent (13–15)
- Architecture matches the problem
- Single-agent by default unless specialization is clearly justified
- Exit conditions and delegation rules are explicit
- Retries / boundaries / loop limits exist
- Multi-agent handoffs are crisp when used

### Adequate (8–12)
- Architecture is plausible but not especially sharp
- Some boundaries are present, but loop or handoff rules are soft
- Multi-agent split may be helpful but is not clearly proven

### Weak (0–7)
- Too many agents for the problem
- Control flow is implicit or fragile
- No clear exit conditions
- Delegation logic is muddled

## 4) Guardrails and human control — 10 points

### Excellent (9–10)
- Risky inputs are validated
- Risky outputs are checked
- Destructive or side-effectful tools are gated
- Human review or confirmation exists where appropriate

### Adequate (5–8)
- Some protections exist, but coverage is partial
- Human control exists but is inconsistent

### Weak (0–4)
- Side-effectful actions can happen with minimal safety controls
- No clear approval path
- Unsafe inputs or outputs are largely unmanaged

## 5) Context management and memory hygiene — 10 points

### Excellent (9–10)
- Context is curated rather than dumped
- Retrieval, memory, and tool outputs are scoped and high-signal
- Large payloads are paginated, filtered, or truncated sensibly
- Context growth appears intentional

### Adequate (5–8)
- Context mostly works, but some unnecessary payloads or weak scoping remain

### Weak (0–4)
- Context is noisy, oversized, or poorly bounded
- Tool outputs overwhelm the model
- Memory policy is absent or confused

## 6) Evals, traces, and observability — 15 points

### Excellent (13–15)
- Traces or logs make runs inspectable
- Deterministic checks exist for critical behavior
- Repeatable prompt sets / datasets / graders exist
- Changes can be measured over time

### Adequate (8–12)
- Some runtime evidence exists, but it is ad hoc or incomplete
- Tests cover outcomes but not process

### Weak (0–7)
- Little or no runtime evidence
- No repeatable evaluation loop
- Quality claims are mostly vibe-based

## 7) Failure handling and operational robustness — 10 points

### Excellent (9–10)
- Clear handling for malformed input, tool failure, missing data, and partial completion
- Error messages help the model recover
- Operational limits are visible and intentional

### Adequate (5–8)
- Some failure paths are handled, but recovery is uneven

### Weak (0–4)
- Errors are opaque or ignored
- Tool failures likely produce thrashing or silent bad output
- Operational behavior is mostly optimistic

## Scoring notes

- Score conservatively when evidence is partial.
- Missing artifacts are not neutral; they create uncertainty and should reduce the score.
- A beautiful prompt does not rescue a confused tool surface.
- A large tool catalog is not automatically bad; overlapping, weakly described tools are bad.
- Multi-agent systems should earn their complexity.

## Report language

The report should always answer these questions explicitly:
1. **How good is the system prompt?**
2. **Do the tools seem designed correctly?**
3. **Is the architecture proportionate to the problem?**
4. **Would you trust this in production? Why or why not?**
5. **What should be fixed first?**
