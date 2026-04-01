# Idea Evaluation Rubric

## Quick Score Card

Rate each idea 1-5 on each criterion:

| Criterion | 1 (Poor) | 3 (Acceptable) | 5 (Excellent) |
|-----------|----------|----------------|---------------|
| **Robust** | Breaks on edge cases | Handles common cases | Handles all cases gracefully |
| **Reliable** | Intermittent failures | Usually works | Always works |
| **Performant** | Noticeably slow | Acceptable speed | Imperceptibly fast |
| **Intuitive** | Confusing UX | Learnable | Obvious immediately |
| **User-friendly** | Frustrating | Neutral | Delightful |
| **Ergonomic** | Adds friction | No change | Reduces friction |
| **Useful** | Solves nothing | Solves minor pain | Solves major pain |
| **Compelling** | Nobody wants | Nice to have | Must have |
| **Accretive** | Negative value | Marginal value | Clear value |
| **Pragmatic** | Impossible | Difficult | Straightforward |

**Threshold:** Ideas scoring <3 average should be cut.

---

## Detailed Criteria

### Robust
- Does it handle empty input?
- Does it handle malformed input?
- Does it handle unicode?
- Does it handle concurrent access?
- Does it fail gracefully?

### Reliable
- Does it work the first time?
- Does it work the 1000th time?
- Does it work under load?
- Does it work offline?
- Does it recover from errors?

### Performant
- Is latency acceptable (<100ms for interactive)?
- Is throughput sufficient?
- Does it scale with data size?
- Does it use resources efficiently?
- Is it cache-friendly?

### Intuitive
- Can users predict behavior?
- Are defaults sensible?
- Is naming clear?
- Is documentation needed?
- Do errors explain themselves?

### User-friendly
- Is the happy path smooth?
- Are error messages helpful?
- Is recovery easy?
- Is undo available?
- Is help accessible?

### Ergonomic
- How many steps to accomplish goal?
- How much typing required?
- Are shortcuts available?
- Does it remember preferences?
- Does it reduce cognitive load?

### Useful
- What problem does it solve?
- How often does the problem occur?
- How painful is the problem?
- Are there workarounds?
- Does it create new problems?

### Compelling
- Would users request this?
- Would users pay for this?
- Would users switch for this?
- Would users recommend this?
- Would users miss this?

### Accretive
- Does it add capability?
- Does it reduce complexity?
- Does it improve existing features?
- Does it open new possibilities?
- Is the value measurable?

### Pragmatic
- Is the technology mature?
- Do we have the skills?
- Is the scope clear?
- Are dependencies manageable?
- Is the timeline reasonable?

---

## Winnowing Process

### Round 1: Hard Cuts
Remove any idea that scores 1 on ANY criterion.

### Round 2: Threshold
Remove any idea scoring <3 average.

### Round 3: Ranking
Sort remaining by weighted average:
- Useful: 2x weight
- Pragmatic: 2x weight
- Accretive: 1.5x weight
- Others: 1x weight

### Round 4: Synergy
Consider which ideas complement each other. A weaker idea that enables a stronger idea may be worth keeping.

---

## Red Flags

Immediate disqualification:
- "Users will figure it out"
- "We'll document it later"
- "It's technically correct"
- "Nobody does it differently"
- "We've always done it this way"
