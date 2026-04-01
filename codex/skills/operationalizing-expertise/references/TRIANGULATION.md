# Triangulation Method

Triangulation extracts the canonical kernel from multiple model distillations.

## Core Principle

> **Only what ALL models agree on goes in the kernel.**

Disagreements reveal model biases, not expert truths. The intersection of all three perspectives is the most reliable extraction.

## The Triangulation Process

```
┌─────────────────────────────────────────────────────────────┐
│  GPT Distillation      Opus Distillation    Gemini Distillation│
│        │                      │                      │        │
│        └──────────────────────┼──────────────────────┘        │
│                               │                               │
│                               ▼                               │
│                    ┌─────────────────────┐                   │
│                    │   TRIANGULATION    │                   │
│                    │   (intersection)   │                   │
│                    └─────────────────────┘                   │
│                               │                               │
│              ┌────────────────┼────────────────┐             │
│              ▼                ▼                ▼             │
│         CONSENSUS         DISPUTED         UNIQUE           │
│         (→ kernel)        (→ appendix)     (→ discard)      │
└─────────────────────────────────────────────────────────────┘
```

## The Triangulation Prompt

```markdown
# Triangulated Kernel Synthesis

## Input
You have three independent distillations of [EXPERT]'s methodology:

### GPT's Analysis
[Paste GPT distillation summary - axioms, operators, anti-patterns]

### Claude's Analysis
[Paste Opus distillation summary]

### Gemini's Analysis
[Paste Gemini distillation summary]

## Task
Synthesize a TRIANGULATED KERNEL containing ONLY consensus items.

---

## Instructions

### For Axioms
Include an axiom ONLY if:
- All three models identified it (possibly with different wording)
- The core claim is the same across all three
- You can cite quotes supporting it from at least 2 distillations

If only 2/3 agree → mark as [DISPUTED: model X disagrees]
If only 1/3 has it → omit from kernel

### For Operators
Include an operator ONLY if:
- All three models extracted it (possibly with different names)
- The triggering conditions are compatible
- The failure modes overlap

Merge definitions:
- Use the clearest phrasing from any model
- Combine trigger lists (union)
- Combine failure modes (union)
- Keep all quote anchors

### For Anti-Patterns
Include ONLY if all three models warn against it.

---

## Output Format

<!-- TRIANGULATED_KERNEL_START -->

### Axioms (consensus)

**1. [Axiom Name]**
Statement: [merged statement]
Evidence: All three models cite [quotes]
Confidence: HIGH (3/3 agree)

**2. [Axiom Name]**
...

### Operators (consensus)

**[Symbol] [Operator Name]**
- Definition: [merged definition]
- Triggers: [combined list]
- Failure modes: [combined list]
- Anchors: [all citations]
- Confidence: HIGH (3/3)

...

### Anti-Patterns (consensus)

**[Name]**: [what not to do]
All models warn: [merged reasoning]

### Output Contract

[Shared output requirements all models agree on]

<!-- TRIANGULATED_KERNEL_END -->

---

## DISPUTED Items (2/3 agreement)

| Item | GPT | Opus | Gemini | Resolution |
|------|-----|------|--------|------------|
| [name] | ✓ | ✓ | ✗ | [why disagreement] |

---

## UNIQUE Items (1/3 only)

These may reflect model bias rather than expert methodology:
- [item from only GPT]
- [item from only Opus]
- [item from only Gemini]
```

## Kernel Format Specification

### HTML Markers

Use markers for programmatic extraction:

```markdown
<!-- TRIANGULATED_KERNEL_START -->
[kernel content]
<!-- TRIANGULATED_KERNEL_END -->
```

This enables:
```typescript
function extractKernel(markdown: string): string | null {
  const start = markdown.indexOf("<!-- TRIANGULATED_KERNEL_START -->");
  const end = markdown.indexOf("<!-- TRIANGULATED_KERNEL_END -->");
  if (start === -1 || end === -1) return null;
  return markdown.slice(start, end + "<!-- TRIANGULATED_KERNEL_END -->".length);
}
```

### Versioning

```markdown
<!-- TRIANGULATED_KERNEL_START v0.2 -->
## Triangulated Kernel v0.2

**Changes from v0.1:**
- Added operator X (newly discovered in source review)
- Refined axiom 3 wording
- Removed disputed anti-pattern Y

[kernel content]

<!-- TRIANGULATED_KERNEL_END v0.2 -->
```

## Confidence Levels

| Agreement | Confidence | Include in Kernel? |
|-----------|------------|-------------------|
| 3/3 models | HIGH | Yes |
| 2/3 models | MEDIUM | Note in appendix |
| 1/3 models | LOW | Omit (likely model bias) |

## Handling Disagreements

### Semantic Equivalence

Models may use different words for the same concept:

```
GPT: "Level-Split"
Opus: "Hierarchical Decomposition"
Gemini: "Layer Separation"

→ These are the SAME operator. Merge under clearest name.
```

### Genuine Disagreement

When models actually conflict:

```
GPT: "Always formalize before experimenting"
Opus: "Formalization can come after initial exploration"
Gemini: [silent on this]

→ This is DISPUTED. Check primary sources.
   If sources support one view, include it.
   If sources are ambiguous, note in appendix.
```

### Resolution Protocol

1. **Check primary sources** — Does the expert actually say this?
2. **Look for context** — Was one model quoting out of context?
3. **Consider scope** — Maybe both are true in different situations?
4. **Note explicitly** — If unresolved, document the dispute

## Kernel Caching

The kernel is expensive to compute. Cache it:

```typescript
let kernelCache: string | null | undefined = undefined;

function getKernel(): string | null {
  if (kernelCache !== undefined) return kernelCache;
  kernelCache = loadAndParseKernel();
  return kernelCache;
}
```

## Quality Checklist

- [ ] All three distillations used as input
- [ ] Every kernel item has 3/3 agreement
- [ ] Disputed items in separate section
- [ ] HTML markers present and valid
- [ ] Version number included
- [ ] Quote anchors preserved
- [ ] No model-specific framing in kernel
