# Operator Library

Operators are the atomic units of methodology. They are cognitive moves that can be composed and applied.

## Operator Philosophy

> **Operators are verbs, not nouns.** They do things to the research state.

An operator is NOT:
- A personality trait ("be creative")
- A vague principle ("think critically")
- A domain-specific fact ("use PCR for DNA")

An operator IS:
- A reusable cognitive move
- Applicable across domains
- Has explicit triggers
- Has known failure modes
- Can be composed with other operators

## Operator Card Format

```markdown
### [Symbol] [Operator Name]

**Definition**: [One sentence - what it does]

**When-to-Use Triggers**:
- [Trigger 1]: When you notice [condition]
- [Trigger 2]: When [situation]
- [Trigger 3]: When [state]

**Failure Modes**:
- [Failure 1]: [How it goes wrong] → [consequence]
- [Failure 2]: [Another way] → [consequence]

**Prompt Module** (copy/paste for agents):
~~~text
[OPERATOR: [Symbol] [Name]]
1) [First step]
2) [Second step]
3) [Third step]

Output (required): [What to produce]
Optional: [Additional outputs]
Anchors: [Citation requirements]
~~~

**Canonical tag**: [lowercase-with-hyphens]

**Quote-bank anchors**: §n, §m, §p

**Transcript Anchors**: §n (context), §m (example), §p (warning)

**Sources**: [Which distillation(s) extracted this]
```

## Operator Types

### Decomposition Operators
Break complex things into tractable pieces.

Examples:
- **⊘ Level-Split** — Separate causal levels (program/interpreter, message/machine)
- **𝓛 Recode** — Change representation to reveal structure

### Testing Operators
Convert theories into discriminative experiments.

Examples:
- **✂ Exclusion-Test** — Design tests that kill hypotheses
- **⌂ Materialize** — "If true, what would I see?"
- **🎭 Potency-Check** — Distinguish "won't" from "can't"

### Hygiene Operators
Prevent self-deception and maintain rigor.

Examples:
- **ΔE Exception-Quarantine** — Isolate anomalies explicitly
- **⊞ Scale-Check** — Verify orders of magnitude
- **† Theory-Kill** — Discard failed hypotheses promptly

### Discovery Operators
Find new territory and avoid crowds.

Examples:
- **⊕ Cross-Domain** — Import patterns from other fields
- **∿ Dephase** — Work out of fashion
- **◊ Paradox-Hunt** — Use contradictions as beacons

### System Operators
Choose and optimize experimental systems.

Examples:
- **⟂ Object-Transpose** — Change what you're experimenting on
- **↑ Amplify** — Use biology's gain mechanisms
- **🔧 DIY/Bricolage** — Build what you need

## Operator Composition

Operators compose into pipelines:

```
Standard Diagnostic Chain:
⊘ → 𝓛 → ≡ → ✂
Level-split → Recode → Extract invariants → Exclusion tests

Theory-to-Test Pipeline:
𝓛 → ⌂ → ⚡
Recode → Materialize → Quickie pilot

Hygiene Layer:
⊞ → ΔE → †
Scale-check → Quarantine anomalies → Kill bad theories
```

### Composition Rules

1. **Order matters** — Level-split before recode usually
2. **Loops exist** — Test results → new hypotheses → new tests
3. **Not all apply** — Skip operators that don't fit the situation
4. **Name when used** — "Applying ⊘ Level-Split here..."

## Prompt Module Design

The prompt module is copy-paste ready for agents:

```text
[OPERATOR: ⊘ Level-Split]
1) Identify at least 1 level confusion (e.g., program vs interpreter).
2) Rewrite the claim as 2–3 level-typed hypotheses.
3) Add at least 1 discriminative test with potency check.

Output (required): 2–6 fenced `delta` JSON blocks targeting:
- hypothesis_slate (ADD/EDIT)
- discriminative_tests (ADD)
Optional: predictions_table (ADD), assumption_ledger (ADD)
Anchors: prefer transcript `§n`; otherwise `anchors: ["inference"]`.
```

### Prompt Module Requirements

1. **Numbered steps** — Clear sequence
2. **Concrete outputs** — What exactly to produce
3. **Format spec** — How to format (JSON, markdown, etc.)
4. **Anchor convention** — How to cite sources

## Symbol Selection

Choose symbols that are:
- **Mnemonic** — ✂ for cutting/exclusion
- **Distinctive** — Different from other operators
- **Unicode-compatible** — Works in markdown
- **Pronounceable** — Can be spoken ("scissors" for ✂)

### Symbol Registry

| Symbol | Name | Mnemonic |
|--------|------|----------|
| ⊘ | Level-Split | Null/empty between levels |
| 𝓛 | Recode | Script L for language/representation |
| ≡ | Invariant-Extract | Equivalence/identity |
| ✂ | Exclusion-Test | Cutting away hypotheses |
| ⌂ | Materialize | House/concrete |
| ⟂ | Object-Transpose | Perpendicular/change axis |
| ⊕ | Cross-Domain | Plus from outside |
| ⊞ | Scale-Check | Grid/measurement |
| ΔE | Exception-Quarantine | Delta/change in expectations |
| † | Theory-Kill | Death |
| ◊ | Paradox-Hunt | Diamond/jewel in contradiction |
| ∿ | Dephase | Wave out of phase |
| ↑ | Amplify | Arrow up |
| 🔧 | DIY | Wrench/tool |
| ⚡ | Quickie | Lightning fast |
| 👁 | HAL (Have A Look) | Eye |
| 🎭 | Potency-Check | Masks/theater |

## Integration with Kickoff

Operators are assigned to roles:

```typescript
const ROLE_OPERATORS: Record<AgentRole, string[]> = {
  hypothesis_generator: ["⊘ Level-Split", "⊕ Cross-Domain", "◊ Paradox-Hunt"],
  test_designer: ["✂ Exclusion-Test", "⌂ Materialize", "🎭 Potency-Check"],
  adversarial_critic: ["⊞ Scale-Check", "ΔE Exception-Quarantine", "† Theory-Kill"],
};
```

Kickoff messages include:
1. The triangulated kernel (all operators listed)
2. Role-specific operator focus (2-4 primary operators)
3. Full operator cards for assigned operators

## Validation Checklist

For each operator:
- [ ] Has symbol, name, canonical tag
- [ ] Definition is one sentence
- [ ] At least 3 triggers
- [ ] At least 2 failure modes
- [ ] Prompt module is complete
- [ ] Quote anchors reference real corpus entries
- [ ] Failure modes are specific (not generic "use wrong")
