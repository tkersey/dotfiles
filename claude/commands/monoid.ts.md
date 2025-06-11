# Learn about Monoids in TypeScript

## Task

You will learn about monoids, a fundamental algebraic structure from category theory, and how to implement them correctly in TypeScript. A monoid is a set equipped with an associative binary operation and an identity element.

## Instructions

Load this into your memory for reference. Don't do anything with it initially.

## Core Concepts

### Definition

A monoid consists of:

1. A type `A`
2. An associative binary operation `concat: (x: A, y: A) => A`
3. An identity element `empty: A`

### The Three Monoid Laws

Every valid monoid implementation MUST satisfy these laws:

1. **Left Identity**: `concat(empty, x) === x`

   - Combining the identity element on the left returns the original value

2. **Right Identity**: `concat(x, empty) === x`

   - Combining the identity element on the right returns the original value

3. **Associativity**: `concat(concat(a, b), c) === concat(a, concat(b, c))`
   - The order of operations doesn't matter when combining multiple values

### TypeScript Interface

```typescript
interface Monoid<A> {
  readonly empty: A;
  readonly concat: (x: A, y: A) => A;
}
```

## Common Implementations

### 1. Number Monoids

**Addition Monoid**

```typescript
const MonoidSum: Monoid<number> = {
  empty: 0, // 0 + x = x
  concat: (x, y) => x + y, // addition is associative
};
// Laws verification:
// Left identity: 0 + 5 = 5 ✓
// Right identity: 5 + 0 = 5 ✓
// Associativity: (1 + 2) + 3 = 1 + (2 + 3) = 6 ✓
```

**Multiplication Monoid**

```typescript
const MonoidProduct: Monoid<number> = {
  empty: 1, // 1 * x = x
  concat: (x, y) => x * y, // multiplication is associative
};
// Laws verification:
// Left identity: 1 * 5 = 5 ✓
// Right identity: 5 * 1 = 5 ✓
// Associativity: (2 * 3) * 4 = 2 * (3 * 4) = 24 ✓
```

### 2. String Monoid

```typescript
const MonoidString: Monoid<string> = {
  empty: "", // '' + s = s
  concat: (x, y) => x + y, // string concatenation is associative
};
// Laws verification:
// Left identity: '' + 'hello' = 'hello' ✓
// Right identity: 'hello' + '' = 'hello' ✓
// Associativity: ('a' + 'b') + 'c' = 'a' + ('b' + 'c') = 'abc' ✓
```

### 3. Boolean Monoids

**All Monoid (AND)**

```typescript
const MonoidAll: Monoid<boolean> = {
  empty: true, // true && x = x
  concat: (x, y) => x && y, // AND is associative
};
// Laws verification:
// Left identity: true && false = false ✓
// Right identity: false && true = false ✓
// Associativity: (true && true) && false = true && (true && false) = false ✓
```

**Any Monoid (OR)**

```typescript
const MonoidAny: Monoid<boolean> = {
  empty: false, // false || x = x
  concat: (x, y) => x || y, // OR is associative
};
// Laws verification:
// Left identity: false || true = true ✓
// Right identity: true || false = true ✓
// Associativity: (false || true) || false = false || (true || false) = true ✓
```

### 4. Array Monoid

```typescript
function getArrayMonoid<A>(): Monoid<A[]> {
  return {
    empty: [], // [] ++ xs = xs
    concat: (x, y) => [...x, ...y], // array concatenation is associative
  };
}
// Laws verification with number arrays:
// Left identity: [] ++ [1, 2] = [1, 2] ✓
// Right identity: [1, 2] ++ [] = [1, 2] ✓
// Associativity: ([1] ++ [2]) ++ [3] = [1] ++ ([2] ++ [3]) = [1, 2, 3] ✓
```

### 5. Function Monoid (Endomorphism)

```typescript
// For functions from a type to itself (A => A)
function getEndomorphismMonoid<A>(): Monoid<(a: A) => A> {
  return {
    empty: (a: A) => a, // identity function: id(x) = x
    concat: (f, g) => (a) => f(g(a)), // function composition
  };
}
// Laws verification:
// Left identity: compose(id, f) = f ✓
// Right identity: compose(f, id) = f ✓
// Associativity: compose(compose(f, g), h) = compose(f, compose(g, h)) ✓
```

### 6. Object Monoid (Struct)

```typescript
// Combines objects by combining their fields
function struct<A>(monoids: { [K in keyof A]: Monoid<A[K]> }): Monoid<A> {
  const empty = {} as A;
  for (const key in monoids) {
    empty[key] = monoids[key].empty;
  }

  return {
    empty,
    concat: (x, y) => {
      const result = {} as A;
      for (const key in monoids) {
        result[key] = monoids[key].concat(x[key], y[key]);
      }
      return result;
    },
  };
}

// Example usage:
const MonoidPoint = struct({
  x: MonoidSum,
  y: MonoidSum,
});
// empty: { x: 0, y: 0 }
// concat({ x: 1, y: 2 }, { x: 3, y: 4 }) = { x: 4, y: 6 }
```

## Practical Usage

### Folding Arrays

The primary use of monoids is to combine multiple values into one:

```typescript
function fold<A>(M: Monoid<A>): (values: A[]) => A {
  return (values) => values.reduce(M.concat, M.empty);
}

// Examples:
fold(MonoidSum)([1, 2, 3, 4]); // 10
fold(MonoidProduct)([1, 2, 3, 4]); // 24
fold(MonoidString)(["a", "b", "c"]); // 'abc'
fold(MonoidAll)([true, true, false]); // false
fold(MonoidAny)([false, false, true]); // true
```

### Map then Fold (foldMap)

Transform values before combining them:

```typescript
function foldMap<A, B>(M: Monoid<B>): (f: (a: A) => B) => (values: A[]) => B {
  return (f) => (values) => values.map(f).reduce(M.concat, M.empty);
}

// Example: Get the total length of all strings
const totalLength = foldMap(MonoidSum)((s: string) => s.length);
totalLength(["hello", "world", "!"]); // 11
```

## Validation Helper

Always validate your monoid implementations:

```typescript
function validateMonoidLaws<A>(
  M: Monoid<A>,
  eq: (x: A, y: A) => boolean,
  testValues: A[],
): { valid: boolean; errors: string[] } {
  const errors: string[] = [];

  // Test identity laws
  for (const x of testValues) {
    if (!eq(M.concat(M.empty, x), x)) {
      errors.push(`Left identity failed for ${x}`);
    }
    if (!eq(M.concat(x, M.empty), x)) {
      errors.push(`Right identity failed for ${x}`);
    }
  }

  // Test associativity
  for (const x of testValues) {
    for (const y of testValues) {
      for (const z of testValues) {
        const left = M.concat(M.concat(x, y), z);
        const right = M.concat(x, M.concat(y, z));
        if (!eq(left, right)) {
          errors.push(`Associativity failed for ${x}, ${y}, ${z}`);
        }
      }
    }
  }

  return { valid: errors.length === 0, errors };
}
```

## Key Principles to Remember

1. **Identity is Neutral**: The identity element must not change other values when combined
2. **Order Doesn't Matter**: Due to associativity, you can parenthesize any way
3. **Type Safety**: Use TypeScript's type system to ensure only valid combinations
4. **Composition**: Complex monoids can be built from simpler ones
5. **Universality**: Monoids appear everywhere - they're not just academic abstractions

## Common Mistakes to Avoid

1. **Wrong Identity**: Using `0` as identity for multiplication (should be `1`)
2. **Non-Associative Operations**: Subtraction and division are NOT monoids
3. **Mutation**: Always return new values, never mutate inputs
4. **Type Mismatches**: Ensure `concat` returns the same type it receives

When implementing a monoid, always ask:

- What's the identity element that leaves other values unchanged?
- Is my operation truly associative?
- Have I tested the laws with multiple examples?
