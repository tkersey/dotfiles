# Jargon Glossary Patterns

A progressive disclosure glossary makes domain terminology accessible to newcomers while remaining useful to experts.

## The Progressive Disclosure Principle

```
TOOLTIP (100 chars)
    │
    ▼ (click/hover)
SHORT (1 sentence)
    │
    ▼ (expand)
LONG (2-4 sentences)
    │
    ▼ (optional)
ANALOGY ("Think of it like...")
```

Each level adds depth without forcing everyone to read everything.

## Term Structure

```typescript
interface JargonTerm {
  /** The display term (e.g., "C. elegans", "Level-Split") */
  term: string;

  /** One-line definition for quick tooltips (~100 chars) */
  short: string;

  /** Full explanation in plain English (2-4 sentences) */
  long: string;

  /** "Think of it like..." analogy for non-experts */
  analogy?: string;

  /** Why this term matters in this methodology */
  why?: string;

  /** Related term keys for discovery (2-4 terms max) */
  related?: string[];

  /** Category for filtering */
  category: JargonCategory;
}
```

## Categories

```typescript
type JargonCategory =
  | "operators"    // Methodology operators
  | "core"         // Core expert concepts
  | "domain"       // Domain-specific terms
  | "methodology"  // Scientific method terms
  | "project";     // Project-specific terms
```

## Writing Guidelines

### Short (Tooltip)

**Goal**: Immediate understanding, ~100 characters

```markdown
# BAD (too long, too technical)
"The process of separating conceptually blended categories into distinct causal
roles so that reasoning can proceed cleanly without level confusion"

# GOOD (concise, actionable)
"Decompose a problem into distinct levels of organization (⊘)."
```

### Long (Full Definition)

**Goal**: Complete understanding, 2-4 sentences

```markdown
# BAD (still too abstract)
"Level-Split is an operator that helps with decomposition."

# GOOD (concrete, with examples)
"The operator ⊘ separates a problem into levels (e.g., atoms → molecules
→ cells → organisms). Each level has its own rules. Confusion arises when
you mix levels or try to explain one level purely in terms of another.
Distinguish program from interpreter, message from machine."
```

### Analogy

**Goal**: Intuitive grasp for non-experts

```markdown
# TEMPLATE
"Think of it like [familiar domain example]."

# EXAMPLES
- Level-Split: "Separate a building into floors. Plumbing problems on
  floor 3 don't require knowing every brick in the foundation."

- Exclusion-Test: "Sherlock Holmes: 'When you have eliminated the
  impossible, whatever remains must be the truth.'"

- Object-Transpose: "Darwin studied barnacles, not humans, to understand
  evolution. The right object makes intractable questions tractable."
```

### Why

**Goal**: Explain relevance to this methodology

```markdown
# TEMPLATE
"[EXPERT] emphasizes this because [reason]. Transcript anchors: §n, §m."

# EXAMPLE
"Brenner emphasizes that biology operates across multiple levels.
Failing to level-split leads to confused explanations.
Anchors: §45-46 (Von Neumann), §105 (message vs machine)."
```

### Related

**Goal**: Enable discovery

```markdown
# GOOD (2-4 related terms)
related: ["recode", "scale-prison", "object-transpose"]

# BAD (too many, or unrelated)
related: ["everything", "the-whole-methodology", "random-term"]
```

## Dictionary Organization

```typescript
// Keys are lowercase with hyphens
const jargonDictionary: Record<string, JargonTerm> = {
  // Operators
  "level-split": { ... },
  "recode": { ... },
  "exclusion-test": { ... },

  // Core concepts
  "third-alternative": { ... },
  "evidence-per-week": { ... },

  // Domain terms
  "c-elegans": { ... },
  "knockout": { ... },

  // Methodology
  "falsifiability": { ... },
  "likelihood-ratio": { ... },
};
```

### Key Conventions

- **Lowercase with hyphens**: `level-split`, not `LevelSplit`
- **No special characters**: `c-elegans`, not `C. elegans`
- **Singular form**: `hypothesis`, not `hypotheses`

## Lookup Function

```typescript
function getJargon(key: string): JargonTerm | undefined {
  // Normalize key
  const normalized = key
    .toLowerCase()
    .replace(/[^a-z0-9]/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '');

  return jargonDictionary[normalized];
}

// Fuzzy matching for flexible lookups
function findJargon(query: string): JargonTerm[] {
  const normalized = query.toLowerCase();
  return Object.values(jargonDictionary)
    .filter(term =>
      term.term.toLowerCase().includes(normalized) ||
      term.short.toLowerCase().includes(normalized)
    );
}
```

## UI Integration

### Tooltip Component

```tsx
function JargonTooltip({ termKey }: { termKey: string }) {
  const term = getJargon(termKey);
  if (!term) return null;

  return (
    <Tooltip content={term.short}>
      <span className="jargon-term">{term.term}</span>
    </Tooltip>
  );
}
```

### Auto-Highlighting

```tsx
function JargonText({ text }: { text: string }) {
  const terms = Object.keys(jargonDictionary);
  const pattern = new RegExp(`\\b(${terms.join('|')})\\b`, 'gi');

  return text.split(pattern).map((part, i) => {
    const term = getJargon(part);
    if (term) {
      return <JargonTooltip key={i} termKey={part} />;
    }
    return part;
  });
}
```

## Validation Checklist

For each term:
- [ ] `short` is ≤100 characters
- [ ] `long` is 2-4 sentences
- [ ] `analogy` uses familiar domain
- [ ] `why` includes transcript anchors where applicable
- [ ] `related` has 2-4 terms, all exist in dictionary
- [ ] `category` is valid
- [ ] Key is lowercase with hyphens

## Common Mistakes

| Mistake | Why It Fails | Fix |
|---------|--------------|-----|
| Circular definitions | "X is when you do X" | Use different words |
| No analogy | Non-experts can't grasp | Add familiar comparison |
| Too many related | Overwhelming | Max 4 related terms |
| Jargon in definition | Still unclear | Use plain English |
| Missing anchors | Can't verify | Add §n citations |
