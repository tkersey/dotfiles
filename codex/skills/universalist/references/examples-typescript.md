# TypeScript Examples (ADD)

## Table of contents
- Tagged unions
- Product types
- Smart constructors
- Monoid combine
- Validation
- Lattice for permissions
- Semiring-like scoring
- State machine transitions
- Fold with monoid
- Normalization
- Homomorphism

## Tagged unions
```ts
type PaymentStatus =
  | { tag: "Pending" }
  | { tag: "Settled"; ref: string }
  | { tag: "Failed"; reason: string };
```

## Product types
```ts
type Money = { amount: number; currency: string };
```

## Smart constructors
```ts
type NonEmpty = { tag: "NonEmpty"; value: string };

function mkNonEmpty(s: string): NonEmpty | null {
  return s.length === 0 ? null : { tag: "NonEmpty", value: s };
}
```

## Monoid combine
```ts
type Log = { lines: string[] };
const emptyLog: Log = { lines: [] };

function combineLog(a: Log, b: Log): Log {
  return { lines: [...a.lines, ...b.lines] };
}
```

## Validation
```ts
type Validation<E, A> =
  | { tag: "Failure"; errors: E[] }
  | { tag: "Success"; value: A };

function combineValidation<E, A>(a: Validation<E, A>, b: Validation<E, A>): Validation<E, A> {
  if (a.tag === "Failure" && b.tag === "Failure") {
    return { tag: "Failure", errors: [...a.errors, ...b.errors] };
  }
  if (a.tag === "Failure") return a;
  if (b.tag === "Failure") return b;
  return a;
}
```

## Lattice for permissions
```ts
type Perm = Set<string>;

function join(a: Perm, b: Perm): Perm {
  return new Set([...a, ...b]);
}

function meet(a: Perm, b: Perm): Perm {
  return new Set([...a].filter(x => b.has(x)));
}
```

## Semiring-like scoring
```ts
type Score = number;
const add = (a: Score, b: Score) => a + b;
const mul = (a: Score, b: Score) => a * b;
```

## State machine transitions
```ts
type State = "Draft" | "Review" | "Approved" | "Published";

function step(s: State): State {
  switch (s) {
    case "Draft": return "Review";
    case "Review": return "Approved";
    case "Approved": return "Published";
    default: return "Published";
  }
}
```

## Fold with monoid
```ts
function foldLog(logs: Log[]): Log {
  return logs.reduce((acc, l) => combineLog(acc, l), emptyLog);
}
```

## Normalization
```ts
type Expr = { tag: "Lit"; n: number } | { tag: "Add"; a: Expr; b: Expr };

function normalize(e: Expr): Expr {
  if (e.tag === "Add" && e.a.tag === "Lit" && e.a.n === 0) return normalize(e.b);
  if (e.tag === "Add") return { tag: "Add", a: normalize(e.a), b: normalize(e.b) };
  return e;
}
```

## Homomorphism
```ts
// length is a homomorphism from concatenation to addition:
// length(a + b) === length(a) + length(b)
```
