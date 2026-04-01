# Case Study: brenner_bot

brenner_bot operationalized Sydney Brenner's scientific methodology into a multi-agent research coordination system. This case study shows the complete implementation.

## Overview

| Component | Implementation |
|-----------|----------------|
| **Expert** | Sydney Brenner (Nobel laureate, molecular biology) |
| **Corpus** | 236-segment Web of Stories interview transcript |
| **Models** | GPT-5.2, Claude Opus 4.5, Gemini 3 |
| **Output** | Next.js 16 web app + CLI coordination system |

## Corpus Structure

```
brenner_bot/
├── complete_brenner_transcript.md    # 236 segments
├── quote_bank_restored_primitives.md # ~200 anchored quotes
├── initial_metaprompt.md             # First distillation prompt
├── gpt_pro_extended_reasoning_responses/
│   ├── batch_1.md
│   ├── batch_2.md
│   └── batch_3.md
├── opus_45_responses/
│   ├── batch_1.md
│   ├── batch_2.md
│   └── batch_3.md
├── gemini_3_deep_think_responses/
│   └── batch_1-3.md
└── specs/
    ├── triangulated_kernel.md        # THE kernel
    ├── operator_library_v0.1.md      # 17 operators
    └── role_prompts_v0.1.md          # Per-role prompts
```

## The Metaprompt

The initial prompt that started distillation:

```markdown
# Sydney Brenner Methodology Extraction

You have access to the complete Web of Stories interview with Sydney Brenner
(236 segments, ~50,000 words).

## Your Task

Extract a systematic, actionable methodology that captures HOW Brenner thinks,
not just WHAT he discovered.

Focus on:
1. **Epistemic axioms** — What must always be true?
2. **Operators** — Reusable cognitive moves he applies repeatedly
3. **Anti-patterns** — What he explicitly warns against
4. **Decision procedures** — Step-by-step processes he describes

## Output Requirements

For each operator:
- Symbol (memorable Unicode character)
- Name (2-3 words)
- One-sentence definition
- When-to-use triggers (3-5)
- Failure modes (2-4)
- Quote anchors (§n from transcript)

## Example Format

### ⊘ Level-Split
**Definition**: Separate conceptually blended categories into distinct causal roles.
**Triggers**:
- Debating "regulation vs structure" without clarity
- Theory conflates information with implementation
**Failure Modes**:
- Arguing inside a blended category
- Jumping logical levels
**Anchors**: §45-46, §105, §205
```

## Distillation Results

### GPT-5.2 Analysis

**Lens**: Systematic, optimization-focused

**Key extraction**: Framed methodology as "evidence per week" optimization
- Maximize: likelihood ratio × speed
- Minimize: ambiguity × cost

**Unique emphasis**: Decision theory framing, explicit algorithms

### Claude Opus 4.5 Analysis

**Lens**: Philosophical, epistemic

**Key extraction**: "Reality has a generative grammar"
- Axioms as non-negotiable beliefs
- Machine-language constraint
- Levels as types

**Unique emphasis**: Deep epistemology, historical context

### Gemini 3 Analysis

**Lens**: Minimal, operational

**Key extraction**: Compact operator taxonomy
- 12 core operators (vs GPT's 17, Opus's 15)
- Focus on actionable triggers

**Unique emphasis**: What can be applied immediately

## Triangulated Kernel (actual)

```markdown
<!-- BRENNER_TRIANGULATED_KERNEL_START -->

### Axioms (non-negotiable)

1) **Reality has a generative grammar.** Prefer causal machinery over description.
2) **To understand is to reconstruct.** Specify how to build the phenomenon.
3) **Machine-language constraint.** Proper simulation uses the object's primitives.
4) **Levels are types.** Keep program/interpreter, message/machine separated.

### Objective function

Maximize **evidence per week**:
- Discrimination: push likelihood ratios up
- Speed: shorten loop time
- Low ambiguity: prefer digital handles
- Cost containment: make decisive tests cheap

### Operator algebra

**Always-on guards**:
- Third alternative: always include "both could be wrong"
- Potency: distinguish "won't" from "can't"
- Scale: be imprisoned in physics
- Anomaly hygiene: quarantine exceptions explicitly

**Default compositions**:
- Diagnostic chain: ⊘ → 𝓛 → ≡ → ✂
- Theory-to-test: 𝓛 → ⌂ → ⚡
- Hygiene layer: ⊞ → ΔE → †

<!-- BRENNER_TRIANGULATED_KERNEL_END -->
```

## Operator Library (excerpt)

### ⊘ Level-Split

**Definition**: Separate conceptually blended categories into distinct causal roles.

**Triggers**:
- Debating "regulation vs structure" without clarity
- Theory conflates information with implementation
- Debugging wrong subsystem (haven't typed the failure)
- Same outcome could have different causes (chastity vs impotence)

**Failure Modes**:
- Arguing inside blended category
- Jumping logical levels
- Confusing description with explanation

**Quote Anchors**: §45-46, §50, §59, §105, §147, §205

### ✂ Exclusion-Test

**Definition**: Derive forbidden patterns, design tests that probe them.

**Triggers**:
- Multiple rival hypotheses
- Looking for maximum discriminative leverage
- Need to make progress by eliminating

**Failure Modes**:
- Running supportive experiments
- Accepting false dichotomies
- Weak likelihood ratio tests

**Quote Anchors**: §69, §103, §147

## Jargon Implementation

```typescript
// apps/web/src/lib/jargon.ts

const jargonDictionary: Record<string, JargonTerm> = {
  "level-split": {
    term: "Level-split",
    short: "Decompose a problem into distinct levels of organization (⊘).",
    long: "The operator ⊘ separates a problem into levels (atoms → molecules → cells). Each level has its own rules. Confusion arises when you mix levels.",
    analogy: "Separate a building into floors. Plumbing on floor 3 doesn't require knowing every brick.",
    why: "Brenner emphasizes biology operates across multiple levels. Anchors: §45-46, §105.",
    related: ["recode", "scale-prison"],
    category: "operators",
  },
  // ... 80+ more terms
};
```

## Session Kickoff (actual code)

```typescript
// apps/web/src/lib/session-kickoff.ts

export function composeKickoffMessages(config: KickoffConfig): KickoffMessage[] {
  return config.recipients.map(recipient => {
    const role = getAgentRole(recipient);  // Maps "Codex" → hypothesis_generator

    return {
      to: recipient,
      subject: `KICKOFF: [${config.threadId}] ${config.researchQuestion.slice(0, 60)}`,
      body: composeKickoffBody(config, role),
      ackRequired: true,
      role,
    };
  });
}
```

## Results

### Quantitative

| Metric | Value |
|--------|-------|
| Corpus segments | 236 |
| Quote bank entries | 200+ |
| Operators extracted | 17 |
| Jargon terms | 80+ |
| Role prompts | 4 |

### Qualitative

- **Multi-model triangulation** revealed genuine consensus vs model bias
- **Operators are reusable** across scientific domains, not just biology
- **Progressive disclosure** makes methodology accessible to newcomers
- **Session kickoff** enables deterministic multi-agent coordination

## Lessons Learned

1. **Primary sources are essential** — The 236-segment transcript was irreplaceable
2. **Three models > one model** — Each caught what others missed
3. **Operators compose** — The algebra structure (chains, layers) emerged from analysis
4. **Markers enable parsing** — HTML comments work well for extraction
5. **Role assignment matters** — Different agents need different operators
