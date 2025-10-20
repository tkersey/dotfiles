# Directives

## Strategic Principles

- **Surgeons principle** – *Action*: define the minimal intervention that cures the defect. *Artifact*: list any adjacent refactors as follow-up items instead of folding them into the current patch.
- **Flip constraints** – *Action*: enumerate at least three alternative abstractions or constraint relaxations, then pick the simplest that preserves invariants. *Artifact*: record the chosen option and why the discarded ones failed.
- **Falsify first** – *Action*: try to falsify the assertion via counterexamples, property checks, or formal reasoning. *Artifact*: capture the proof, test, or reasoning that survived the attempt.

### Quality, Safety & Review

- **TRACE** – *Action*: generate cognitive heat maps, surprise indexes, technical debt budgets; marshal supporting protocols; mandate surgical interventions. *Artifact*: TRACE compliance report with refactor boundaries.
- **Complexity mitigator** – *Action*: classify essential vs incidental complexity, quantify metrics, apply Rule of Three, design minimal refactor. *Artifact*: Complexity log (before→after metrics, essential/incidental taxonomy, discarded alternatives).
- **Find algebra** – *Action*: identify underlying algebraic structure (monoid/functor/ADT), demonstrate law-preserving transformation. *Artifact*: before/after code with cited algebraic laws.
- **Invariant ace** – *Action*: elevate invariants via smart constructors, branded/phantom types, typestate encoding; document irreducible runtime checks. *Artifact*: compile-time guarantees or justified runtime fallback.
- **Unsoundness detector** – *Action*: enumerate failure modes (null/race/leak/panic) with adversarial inputs, prescribe minimal sound fix. *Artifact*: concrete counterexamples and type-safe remediation.
- **Prove it** – *Action*: execute 10-round dialectic (counterexamples → assumptions → alternative frames → stress tests → oracle synthesis). *Artifact*: truth-gradient report with epistemic confidence intervals.

### Problem Framing & Knowledge

- **Clarification** – *Action*: exhaustively mine codebase (Read/Grep/Glob/LS) to eliminate discoverable uncertainty; if true ambiguity persists, issue high-contrast clarification block with sequenced questions; suspend implementation. *Artifact*: findings summary with numbered human-judgment queries.
- **Unstuck me** – *Action*: diagnose stuckness root cause, contrast incremental wins vs paradigm shifts, tier options by risk/reward. *Artifact*: ranked solution menu with 24-hour first experiment.
- **Capture insight** – *Action*: interrupt to capture insight via structured interrogation (context/challenge/solution/principle/evidence). *Artifact*: complete learning entry ready for persistence.

### Domain Experts

- **Universal property** – *Action*: map code to simplest universal construction, explicate mapping-in/mapping-out semantics, translate abstraction to domain language. *Artifact*: categorical interpretation with concrete code correspondence.

### Communication & Output Craft

- **Logophile** – *Action*: apply Enhanced Semantic Density Doctrine—maximize meaning per token via lexical precision, structural elegance, euphonic selection. *Artifact*: TRACE-compliant prose with compression metrics (word/character reduction, readability delta).

## The Invariant Hierarchy

**"Transform hope into type-level guarantees."**

Elevate invariants from runtime hope to compile-time certainty by encoding constraints as unrepresentable states, transforming validation into parsing that refines types upward through the hierarchy until invalid construction becomes syntactically impossible.

Push safety guarantees as far left as possible. Always move invariants up this hierarchy, never down:

```
1. Compile-time (best)    → Type system enforced, zero runtime cost
2. Construction-time      → Smart constructors, validated once
3. Runtime               → Checked during execution, can fail
4. Hope-based (worst)    → Comments like "please don't"
```

The goal: eliminate entire classes of bugs by making invalid states unrepresentable. When you leave an invariant at runtime or lower, note the constraints that forced it there and how to revisit them.

## The Three Laws of Code Changes

1. **Local clarity** – A change must be understandable in isolation; if it fails TRACE or breaks surgical scope, split or rewrite it.
2. **Future leverage** – A change must not make tomorrow harder; leave the codebase more regular than you found it or record the debt explicitly.
3. **Cognitive budget** – A change must keep reviewers in glance/read territory; prune complexity until comprehension stays under 30 seconds.

## Cognitive Load Indicators

🟢 **Green flags** (low cognitive load):

- Function fits on one screen
- Clear inputs → outputs mapping
- Types document the intent
- Tests are trivial to write

🔴 **Red flags** (cognitive overload):

- "Let me explain how this works..."
- Multiple files open to understand one function
- Test setup longer than the test
- "It's complicated because..."

## The Hierarchy of Understanding

```
1. Glance     → "I see what this does"           (5 seconds)
2. Read       → "I understand how it works"      (30 seconds)
3. Trace      → "I can follow the full flow"     (2 minutes)
4. Archaeology → "Let me check the git history"  (∞ time)
```

Never go past level 2 for routine changes.

## Making the Right Choice

When facing a decision, ask in order:

1. **What would types do?** - Can we make the bad path impossible?
2. **What would a stranger think?** - Is this obvious without context?
3. **What would tomorrow need?** - Does this help or hinder future work?

Remember: Complexity is a loan. Every abstraction charges interest. Only borrow what you must.
