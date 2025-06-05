# Implementing Meet and Join Semi-Lattices in TypeScript

## Task

You will learn about semi-lattices, fundamental algebraic structures that model partial orders and appear naturally in many programming contexts. A semi-lattice is a set with a binary operation that is associative, commutative, and idempotent.

## Core Concepts

### Semi-Lattice Definition

A semi-lattice consists of:

1. A type `A`
2. A binary operation that is:
   - **Associative**: `(a ∧ b) ∧ c = a ∧ (b ∧ c)`
   - **Commutative**: `a ∧ b = b ∧ a`
   - **Idempotent**: `a ∧ a = a`

### Meet vs Join Semi-Lattices

**Meet Semi-Lattice (∧)**: Computes the greatest lower bound (infimum)

- Think: intersection, minimum, AND
- Example: Set intersection, Math.min

**Join Semi-Lattice (∨)**: Computes the least upper bound (supremum)

- Think: union, maximum, OR
- Example: Set union, Math.max

### The Three Semi-Lattice Laws

Every valid semi-lattice MUST satisfy these laws:

1. **Associativity**: `op(op(a, b), c) === op(a, op(b, c))`

   - Grouping doesn't matter

2. **Commutativity**: `op(a, b) === op(b, a)`

   - Order doesn't matter

3. **Idempotency**: `op(a, a) === a`
   - Combining with self returns self

### TypeScript Interfaces

```typescript
// Base semi-lattice interface
interface SemiLattice<A> {
  readonly combine: (x: A, y: A) => A;
}

// Meet semi-lattice (greatest lower bound)
interface MeetSemiLattice<A> extends SemiLattice<A> {
  readonly meet: (x: A, y: A) => A;
}

// Join semi-lattice (least upper bound)
interface JoinSemiLattice<A> extends SemiLattice<A> {
  readonly join: (x: A, y: A) => A;
}

// When you have both, you get a lattice
interface Lattice<A> {
  readonly meet: (x: A, y: A) => A;
  readonly join: (x: A, y: A) => A;
}
```

## Common Implementations

### 1. Number Semi-Lattices

**Min as Meet Semi-Lattice**

```typescript
const MinSemiLattice: MeetSemiLattice<number> = {
  meet: (x, y) => Math.min(x, y),
  combine: (x, y) => Math.min(x, y),
};
// Laws verification:
// Associative: min(min(2, 3), 4) = min(2, min(3, 4)) = 2 ✓
// Commutative: min(3, 2) = min(2, 3) = 2 ✓
// Idempotent: min(5, 5) = 5 ✓
```

**Max as Join Semi-Lattice**

```typescript
const MaxSemiLattice: JoinSemiLattice<number> = {
  join: (x, y) => Math.max(x, y),
  combine: (x, y) => Math.max(x, y),
};
// Laws verification:
// Associative: max(max(2, 3), 4) = max(2, max(3, 4)) = 4 ✓
// Commutative: max(3, 2) = max(2, 3) = 3 ✓
// Idempotent: max(5, 5) = 5 ✓
```

### 2. Boolean Semi-Lattices

**AND as Meet Semi-Lattice**

```typescript
const BooleanMeet: MeetSemiLattice<boolean> = {
  meet: (x, y) => x && y,
  combine: (x, y) => x && y,
};
// Laws verification:
// Associative: (true && false) && true = true && (false && true) = false ✓
// Commutative: true && false = false && true = false ✓
// Idempotent: true && true = true, false && false = false ✓
```

**OR as Join Semi-Lattice**

```typescript
const BooleanJoin: JoinSemiLattice<boolean> = {
  join: (x, y) => x || y,
  combine: (x, y) => x || y,
};
// Laws verification:
// Associative: (true || false) || false = true || (false || false) = true ✓
// Commutative: true || false = false || true = true ✓
// Idempotent: true || true = true, false || false = false ✓
```

### 3. Set Semi-Lattices

**Intersection as Meet Semi-Lattice**

```typescript
function createSetMeet<T>(): MeetSemiLattice<Set<T>> {
  return {
    meet: (x, y) => {
      const result = new Set<T>();
      for (const item of x) {
        if (y.has(item)) result.add(item);
      }
      return result;
    },
    combine: function (x, y) {
      return this.meet(x, y);
    },
  };
}
// Laws verification:
// Associative: (A ∩ B) ∩ C = A ∩ (B ∩ C) ✓
// Commutative: A ∩ B = B ∩ A ✓
// Idempotent: A ∩ A = A ✓
```

**Union as Join Semi-Lattice**

```typescript
function createSetJoin<T>(): JoinSemiLattice<Set<T>> {
  return {
    join: (x, y) => new Set([...x, ...y]),
    combine: function (x, y) {
      return this.join(x, y);
    },
  };
}
// Laws verification:
// Associative: (A ∪ B) ∪ C = A ∪ (B ∪ C) ✓
// Commutative: A ∪ B = B ∪ A ✓
// Idempotent: A ∪ A = A ✓
```

### 4. Object/Record Semi-Lattices

**Nested Object Merge as Join Semi-Lattice**

```typescript
interface Config {
  [key: string]: any;
}

const ConfigJoin: JoinSemiLattice<Config> = {
  join: (x, y) => ({ ...x, ...y }),
  combine: function (x, y) {
    return this.join(x, y);
  },
};
// Note: This is idempotent for shallow merges
// Deep merge would require recursive implementation
```

### 5. Time/Date Semi-Lattices

**Latest Time as Join Semi-Lattice**

```typescript
const DateJoin: JoinSemiLattice<Date> = {
  join: (x, y) => (x > y ? x : y),
  combine: function (x, y) {
    return this.join(x, y);
  },
};

// Earliest Time as Meet Semi-Lattice
const DateMeet: MeetSemiLattice<Date> = {
  meet: (x, y) => (x < y ? x : y),
  combine: function (x, y) {
    return this.meet(x, y);
  },
};
```

### 6. Permission/Access Control Semi-Lattices

```typescript
enum Permission {
  None = 0,
  Read = 1,
  Write = 2,
  Execute = 4,
  Admin = 7, // Read | Write | Execute
}

// Bitwise OR as Join (granting more permissions)
const PermissionJoin: JoinSemiLattice<Permission> = {
  join: (x, y) => x | y,
  combine: function (x, y) {
    return this.join(x, y);
  },
};

// Bitwise AND as Meet (restricting to common permissions)
const PermissionMeet: MeetSemiLattice<Permission> = {
  meet: (x, y) => x & y,
  combine: function (x, y) {
    return this.meet(x, y);
  },
};
```

## Validation Functions

### Generic Semi-Lattice Law Validation

```typescript
function validateSemiLatticeLaws<A>(
  sl: SemiLattice<A>,
  equals: (x: A, y: A) => boolean,
  testValues: A[],
): { valid: boolean; errors: string[] } {
  const errors: string[] = [];

  // Test associativity
  for (const a of testValues) {
    for (const b of testValues) {
      for (const c of testValues) {
        const left = sl.combine(sl.combine(a, b), c);
        const right = sl.combine(a, sl.combine(b, c));
        if (!equals(left, right)) {
          errors.push(
            `Associativity failed: ((${a} ∧ ${b}) ∧ ${c}) ≠ (${a} ∧ (${b} ∧ ${c}))`,
          );
        }
      }
    }
  }

  // Test commutativity
  for (const a of testValues) {
    for (const b of testValues) {
      const ab = sl.combine(a, b);
      const ba = sl.combine(b, a);
      if (!equals(ab, ba)) {
        errors.push(`Commutativity failed: ${a} ∧ ${b} ≠ ${b} ∧ ${a}`);
      }
    }
  }

  // Test idempotency
  for (const a of testValues) {
    const aa = sl.combine(a, a);
    if (!equals(aa, a)) {
      errors.push(`Idempotency failed: ${a} ∧ ${a} ≠ ${a}`);
    }
  }

  return { valid: errors.length === 0, errors };
}
```

### Property-Based Testing Example

```typescript
import * as fc from "fast-check";

// Property test for any semi-lattice
function semiLatticeProperties<A>(
  sl: SemiLattice<A>,
  arb: fc.Arbitrary<A>,
  equals: (x: A, y: A) => boolean,
) {
  // Associativity property
  fc.assert(
    fc.property(arb, arb, arb, (a, b, c) => {
      const left = sl.combine(sl.combine(a, b), c);
      const right = sl.combine(a, sl.combine(b, c));
      return equals(left, right);
    }),
  );

  // Commutativity property
  fc.assert(
    fc.property(arb, arb, (a, b) => {
      return equals(sl.combine(a, b), sl.combine(b, a));
    }),
  );

  // Idempotency property
  fc.assert(
    fc.property(arb, (a) => {
      return equals(sl.combine(a, a), a);
    }),
  );
}
```

## Practical Usage Patterns

### Folding with Semi-Lattices

```typescript
function foldSemiLattice<A>(sl: SemiLattice<A>, values: A[]): A | undefined {
  if (values.length === 0) return undefined;
  return values.reduce(sl.combine);
}

// Examples:
const numbers = [5, 2, 8, 1, 9];
const minimum = foldSemiLattice(MinSemiLattice, numbers); // 1
const maximum = foldSemiLattice(MaxSemiLattice, numbers); // 9

const sets = [new Set([1, 2, 3]), new Set([2, 3, 4]), new Set([3, 4, 5])];
const intersection = foldSemiLattice(createSetMeet<number>(), sets); // Set([3])
const union = foldSemiLattice(createSetJoin<number>(), sets); // Set([1,2,3,4,5])
```

### Building Bounded Semi-Lattices

```typescript
interface BoundedMeetSemiLattice<A> extends MeetSemiLattice<A> {
  readonly top: A; // Identity for meet
}

interface BoundedJoinSemiLattice<A> extends JoinSemiLattice<A> {
  readonly bottom: A; // Identity for join
}

// Example: Bounded number semi-lattices
const BoundedMin: BoundedMeetSemiLattice<number> = {
  meet: (x, y) => Math.min(x, y),
  combine: (x, y) => Math.min(x, y),
  top: Infinity,
};

const BoundedMax: BoundedJoinSemiLattice<number> = {
  join: (x, y) => Math.max(x, y),
  combine: (x, y) => Math.max(x, y),
  bottom: -Infinity,
};
```

### Lattice from Semi-Lattices

```typescript
function createLattice<A>(
  meetSL: MeetSemiLattice<A>,
  joinSL: JoinSemiLattice<A>,
): Lattice<A> {
  return {
    meet: meetSL.meet,
    join: joinSL.join,
  };
}

// Complete lattice for sets within a universe
class SetLattice<T> implements Lattice<Set<T>> {
  constructor(private universe: Set<T>) {}

  meet(x: Set<T>, y: Set<T>): Set<T> {
    return new Set([...x].filter((item) => y.has(item)));
  }

  join(x: Set<T>, y: Set<T>): Set<T> {
    return new Set([...x, ...y]);
  }
}
```

## Real-World Applications

### 1. Configuration Management

```typescript
// Merging configurations with precedence
const ConfigSemiLattice: JoinSemiLattice<Config> = {
  join: (base, override) => ({ ...base, ...override }),
  combine: function (x, y) {
    return this.join(x, y);
  },
};
```

### 2. Security and Access Control

```typescript
// Least privilege principle using meet
const SecurityMeet: MeetSemiLattice<SecurityLevel> = {
  meet: (x, y) => Math.min(x, y), // Most restrictive
  combine: function (x, y) {
    return this.meet(x, y);
  },
};
```

### 3. Event Timestamp Processing

```typescript
// Finding latest update across distributed systems
const TimestampJoin: JoinSemiLattice<number> = {
  join: Math.max,
  combine: Math.max,
};
```

### 4. CSS Specificity Resolution

```typescript
interface CSSRule {
  specificity: number;
  styles: Record<string, string>;
}

const CSSJoin: JoinSemiLattice<CSSRule> = {
  join: (x, y) => (x.specificity > y.specificity ? x : y),
  combine: function (x, y) {
    return this.join(x, y);
  },
};
```

## Key Principles to Remember

1. **Idempotency is Key**: The defining feature that distinguishes semi-lattices from monoids
2. **Order Independence**: Both associativity and commutativity mean order doesn't matter
3. **Natural Hierarchies**: Semi-lattices model partial orders naturally
4. **Composition**: Complex semi-lattices can be built from simpler ones
5. **Duality**: Meet and join are often dual operations

## Common Mistakes to Avoid

1. **Forgetting Idempotency**: `x - y` is associative and has identity 0, but not idempotent
2. **Assuming Totality**: Not all elements may be comparable in a partial order
3. **Confusing Bounds**: Top is identity for meet, bottom is identity for join
4. **Breaking Commutativity**: Order-dependent operations cannot form semi-lattices

When implementing a semi-lattice, always verify:

- Does combining an element with itself return that element?
- Can I reorder and regroup operations freely?
- Does my operation model some form of "combining" or "choosing"?
