# Algebraic Structure Analysis Prompt

## Use this prompt to have Claude analyze code for algebraic structure opportunities:

---

Please analyze this code for opportunities to use algebraic structures (monoids, semigroups, semi-lattices, etc.). Look for:

**1. Combining Operations**

- Functions that combine two values of the same type: `(T, T) => T`
- Reduce/fold operations with initial values
- Merging or aggregating data
- Configuration or state composition

**2. Common Patterns That Suggest Algebraic Structures**

- Array concatenation, string joining → Monoid
- Min/max operations, set intersections/unions → Semi-lattice
- Associative operations without identity → Semigroup
- Operations with both + and × that distribute → Semiring

**3. Code Smells That Algebraic Structures Could Fix**

- Repeated reduce patterns with different operations
- Complex nested conditionals for combining values
- Ad-hoc merge functions that could be generalized
- Inconsistent handling of empty/null cases

**For each opportunity identified, please provide:**

1. **What structure fits**: Name the algebraic structure and why it applies
2. **Current code**: The existing implementation
3. **Refactored code**: How it would look using the algebraic structure
4. **Benefits gained**:
   - Type safety improvements
   - Reusability opportunities
   - Testing simplifications
   - Performance optimizations
   - Code clarity gains

**Example format:**

```
OPPORTUNITY: User preferences merging
STRUCTURE: Monoid (associative merge with empty default)
CURRENT: Custom merge logic with null checks
REFACTORED: ConfigMonoid with generic fold operation
BENEFITS: Reusable for all config types, laws guarantee correctness
```

Focus on practical improvements over theoretical purity. Only suggest algebraic structures where they provide clear value through better abstractions, testability, or code reuse.

---

## Alternative Shorter Version:

Analyze this code for algebraic structure patterns. Identify where operations like:

- Combining values of the same type
- Reduce/fold with initial values
- Min/max/intersection/union operations
- Associative operations

...could be refactored using monoids, semigroups, or semi-lattices. Show before/after code and explain the practical benefits.
