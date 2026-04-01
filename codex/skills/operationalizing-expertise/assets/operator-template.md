# Operator Template

Copy this template when adding new operators to the library.

---

### [SYMBOL] [Operator Name]

**Definition**: [One sentence describing what this operator does—use a verb phrase]

**When-to-Use Triggers**:
- [Trigger 1]: When you notice [specific condition]
- [Trigger 2]: When [situation description]
- [Trigger 3]: When [another situation]
- [Trigger 4]: When [optional additional trigger]

**Failure Modes**:
- [Failure 1]: [How it goes wrong] → [consequence]
- [Failure 2]: [Another failure mode] → [consequence]
- [Failure 3]: [Optional third failure mode]

**Prompt Module** (copy-paste for agents):
```text
[OPERATOR: [SYMBOL] [Name]]
1) [First concrete step]
2) [Second step]
3) [Third step]

Output (required): [What to produce, format specification]
Optional: [Additional outputs]
Anchors: [Citation requirements, e.g., "prefer §n; otherwise mark [inference]"]
```

**Canonical tag**: [lowercase-with-hyphens]

**Quote-bank anchors**: §[n], §[m], §[p]

**Transcript Anchors**: §[n] (context), §[m] (example), §[p] (warning)

**Sources**: [Which model distillation(s) extracted this—e.g., "GPT-5.2, Opus 4.5"]

---

## Template Checklist

Before adding to the library, verify:

- [ ] Symbol is mnemonic and distinctive
- [ ] Definition is exactly one sentence
- [ ] At least 3 when-to-use triggers
- [ ] At least 2 failure modes with consequences
- [ ] Prompt module has numbered steps
- [ ] Prompt module specifies output format
- [ ] Canonical tag is lowercase with hyphens
- [ ] Quote anchors reference real corpus entries
- [ ] Sources list which models extracted this

## Symbol Selection Guide

Choose symbols that are:
- **Mnemonic**: Visually suggests the operation
- **Distinctive**: Different from existing operators
- **Unicode-compatible**: Works in markdown
- **Pronounceable**: Can be spoken in discussion

| Good Symbols | Why |
|--------------|-----|
| ✂ | Cutting/exclusion |
| ⊘ | Empty/null (level separation) |
| ⊕ | Addition from outside |
| ⟂ | Perpendicular/orthogonal |
| ↑ | Amplification |
| † | Death/killing |
| ◊ | Diamond/jewel (valuable find) |

| Avoid | Why |
|-------|-----|
| ★ | Too generic |
| → | Overused |
| ● | No mnemonic value |
| 🔴 | Color doesn't render consistently |

## Example: Well-Formed Operator

### ✂ Exclusion-Test

**Definition**: Derive forbidden patterns from a hypothesis, then design tests that probe them.

**When-to-Use Triggers**:
- Multiple rival hypotheses compete for the same observations
- You need maximum discriminative leverage per experiment
- Looking to make progress by eliminating rather than confirming
- Current data is consistent with too many explanations

**Failure Modes**:
- Running supportive experiments → confirms but doesn't distinguish
- Accepting false dichotomies → misses the third alternative
- Weak likelihood ratio tests → inconclusive even when "passed"

**Prompt Module** (copy-paste for agents):
```text
[OPERATOR: ✂ Exclusion-Test]
1) List 2-4 rival hypotheses currently under consideration.
2) For each hypothesis, derive at least 1 forbidden pattern ("If H is true, we should NEVER see X").
3) Design a test that probes the forbidden pattern with maximum likelihood ratio.
4) Score the test: likelihood_ratio (0-3), cost (0-3), speed (0-3), ambiguity (0-3).

Output (required): 1-3 fenced `delta` blocks with operation: "ADD", section: "discriminative_tests"
Optional: predictions_table (ADD)
Anchors: prefer §n; mark [inference] when extrapolating.
```

**Canonical tag**: exclusion-test

**Quote-bank anchors**: §69, §103, §147

**Transcript Anchors**: §69 (elimination logic), §103 (example), §147 (potency check)

**Sources**: GPT-5.2, Opus 4.5, Gemini 3 (3/3 consensus)
