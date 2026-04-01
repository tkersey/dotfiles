# Session Kickoff Patterns

The kickoff message initializes an agent with the methodology. It embeds the triangulated kernel and assigns role-specific operators.

## Kickoff Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     KICKOFF MESSAGE                         │
├─────────────────────────────────────────────────────────────┤
│  1. TRIANGULATED KERNEL (shared across all roles)          │
│     - Axioms                                                │
│     - Full operator algebra                                 │
│     - Output contract                                       │
│                                                             │
│  2. ROLE ASSIGNMENT (per agent)                            │
│     - Role name and description                             │
│     - Primary operators (2-4)                               │
│     - Operating constraints                                 │
│     - Output format requirements                            │
│                                                             │
│  3. CONTEXT (per session)                                  │
│     - Research question                                     │
│     - Background context                                    │
│     - Relevant excerpts with anchors                        │
│                                                             │
│  4. REQUESTED OUTPUTS                                      │
│     - What this agent should produce                        │
│     - Response format                                       │
└─────────────────────────────────────────────────────────────┘
```

## Configuration Type

```typescript
interface KickoffConfig {
  /** Thread ID for the session */
  threadId: string;

  /** One-sentence problem statement */
  researchQuestion: string;

  /** 2-4 sentences of essential background */
  context: string;

  /** Relevant excerpts with §n citations */
  excerpt: string;

  /** List of agent names to receive kickoff */
  recipients: string[];

  /** Optional: explicit role mapping */
  recipientRoles?: Record<string, AgentRole>;

  /** Optional: seed hypotheses to start with */
  initialHypotheses?: string;

  /** Optional: scope constraints */
  constraints?: string;

  /** Optional: specific requested outputs */
  requestedOutputs?: string;

  /** Optional: operator focus per role */
  operatorSelection?: OperatorSelection;
}
```

## Role Definitions

```typescript
type AgentRole =
  | "hypothesis_generator"
  | "test_designer"
  | "adversarial_critic"
  | "synthesis";

const ROLE_CONFIG: Record<AgentRole, RoleConfig> = {
  hypothesis_generator: {
    displayName: "Hypothesis Generator",
    operators: ["⊘ Level-Split", "⊕ Cross-Domain", "◊ Paradox-Hunt"],
    description: "Generate hypotheses by hunting paradoxes and importing patterns",
  },
  test_designer: {
    displayName: "Test Designer",
    operators: ["✂ Exclusion-Test", "⌂ Materialize", "🎭 Potency-Check"],
    description: "Convert hypotheses into discriminative tests",
  },
  adversarial_critic: {
    displayName: "Adversarial Critic",
    operators: ["⊞ Scale-Check", "ΔE Exception-Quarantine", "† Theory-Kill"],
    description: "Attack framing, check scale, quarantine anomalies",
  },
  synthesis: {
    displayName: "Synthesis",
    operators: ["∑ Synthesis"],
    description: "Integrate outputs into coherent assessment",
  },
};
```

## Message Template

```markdown
# [Protocol] Session: [Thread ID]

## Triangulated Kernel (single)

<!-- paste full kernel here -->

## Your Role: [Display Name]

[Role description]

**Primary Operators**: [operator list]

**You MUST**:
1. [Constraint 1]
2. [Constraint 2]
3. [Constraint 3]

**Citation Conventions**:
- Transcript: `(§58)` or `(§127-§129)`
- Evidence: `(EV-001)` for record, `(EV-001#E1)` for excerpt
- Inference: `[inference]` when reasoning beyond evidence

**Output Format**: Use ```delta blocks with operation, section, payload

## Research Question

[One-sentence problem]

## Context

[2-4 sentences background]

## Excerpt

[Relevant quotes with §n anchors]

## Requested Outputs

- [Output 1]
- [Output 2]
- [Output 3]

## Response Format

Reply with subject `DELTA[[role]]: <description>`.
Include reasoning as prose, then `## Deltas` with structured contributions.
```

## Role-Specific Prompts

### Hypothesis Generator

```markdown
## Your Role: Hypothesis Generator

You generate candidate hypotheses by hunting for paradoxes, importing
cross-domain patterns, and rigorously separating levels of explanation.

**Primary Operators**: ⊘ Level-Split, ⊕ Cross-Domain, ◊ Paradox-Hunt

**You MUST**:
1. Always include a "third alternative" (both others could be wrong)
2. Never conflate different levels (program/interpreter, message/machine)
3. Cite transcript anchors (§n) when referencing sources
4. Output structured deltas, not narrative prose
5. Apply ⊘ Level-Split before proposing any mechanism

**Output Format**: ```delta blocks with operation: "ADD", section: "hypothesis_slate"
```

### Test Designer

```markdown
## Your Role: Test Designer

You convert hypotheses into discriminative tests—experiments designed to
KILL models, not just collect data. Every test must include a potency check.

**Primary Operators**: ✂ Exclusion-Test, ⌂ Materialize, 🎭 Potency-Check

**You MUST**:
1. Design tests that maximize "evidence per week"
2. Include a potency check for every test (chastity vs impotence)
3. Score every test on the 4-dimension rubric (0-3 each)
4. Consider object transposition—is there a better system?
5. Cite sources when referencing prior results

**Scoring Rubric**: likelihood_ratio, cost, speed, ambiguity (0-3 each)

**Output Format**: ```delta blocks with operation: "ADD", section: "discriminative_tests"
```

### Adversarial Critic

```markdown
## Your Role: Adversarial Critic

You attack the current framing. You find what would make everything wrong.
You check scale constraints and quarantine anomalies.

**Primary Operators**: ⊞ Scale-Check, ΔE Exception-Quarantine, † Theory-Kill

**You MUST**:
1. Calculate actual numbers before accepting any mechanism
2. Quarantine anomalies explicitly—never sweep under the carpet
3. Kill theories when they "go ugly"
4. Propose real third alternatives
5. Cite sources when referencing attacks

**Output Sections**: anomaly_register, adversarial_critique, assumption_ledger
```

## Composition Function

```typescript
function composeKickoffBody(config: KickoffConfig, role: RoleConfig): string {
  const sections: string[] = [];

  // Title
  sections.push(`# Protocol Session: ${config.threadId}`);

  // Triangulated kernel
  const kernel = getTriangulatedKernel();
  if (kernel) {
    sections.push("## Triangulated Kernel (single)");
    sections.push(kernel);
  }

  // Role assignment
  sections.push(getRolePromptSection(role));

  // Optional: operator cards for assigned operators
  if (config.operatorSelection?.[role.role]) {
    sections.push(renderOperatorCards(config.operatorSelection[role.role]));
  }

  // Context sections
  sections.push("## Research Question");
  sections.push(config.researchQuestion);

  sections.push("## Context");
  sections.push(config.context);

  sections.push("## Excerpt");
  sections.push(config.excerpt);

  // Requested outputs
  sections.push("## Requested Outputs");
  sections.push(config.requestedOutputs || getDefaultOutputs(role.role));

  // Response format
  sections.push("## Response Format");
  sections.push(`Reply with subject \`DELTA[${role.role}]: <description>\`.`);

  return sections.join("\n\n");
}
```

## Multi-Agent Kickoff

When starting a session with multiple agents:

```typescript
function composeKickoffMessages(config: KickoffConfig): KickoffMessage[] {
  return config.recipients.map(recipient => {
    const role = getAgentRole(recipient);
    const body = composeKickoffBody(config, role);

    return {
      to: recipient,
      subject: `KICKOFF: [${config.threadId}] ${truncate(config.researchQuestion, 60)}`,
      body,
      ackRequired: true,
      role,
    };
  });
}
```

## Validation

- [ ] Kernel is included verbatim (no modifications)
- [ ] Role matches agent capabilities
- [ ] All §n anchors reference real corpus entries
- [ ] Research question is one sentence
- [ ] Context is 2-4 sentences
- [ ] Excerpt has §n citations
- [ ] Requested outputs are specific
