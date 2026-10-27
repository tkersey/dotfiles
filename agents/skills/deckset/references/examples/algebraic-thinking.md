autoscale: true

# [fit] Abstraction

---

# [fit] A **total function** is a function<br>that is defined for every element in its domain.<br>In other words, for every possible input value from the domain,<br>the function produces exactly one output value in its codomain.

---

# [fit] `(Int, Int) → (Int, Int)`

---

# [fit] `(a, a) → (a, a)`

---

# [fit] `(a, b) → (b, a)`

---

# [fit] Parametricity

## [fit] being able to make (non-trivial) statements<br>about programs by knowing nothing more than their type.

---

# [fit] Parametric<br>polymorphism

## [fit] where a type variable behaves the same<br>regardless of instantiation of the type variable.

---

```typescript
// Define a Transform interface
interface Transform<T> {
  transform(value: T): T;
}

// Implementation for numbers
class NumberTransform implements Transform<number> {
  transform(value: number): number {
    return value + 1;
  }
}

// Implementation for strings
class StringTransform implements Transform<string> {
  transform(value: string): string {
    return value.toUpperCase();
  }
}
```

---

# [fit] Adhoc<br>polymorphism

## [fit] where a single function name<br>can refer to different implementations<br>based on the types of its arguments

---

# [fit] `a → a`

---

# [fit] `String → String`

---

# [fit] `(a → Bool) → [a] → [a]`

---

# [fit] `(a → Maybe b) → [a] → [b]`

---

# [fit] **Algebraic**

# [fit] **Thinking**

---

# [fit] **Curry-Howard-Lambek**<br>correspondence

| Logic                  | Types                     | Categories            |
| ---------------------- | ------------------------- | --------------------- |
| propositions           | types                     | objects               |
| proofs                 | terms                     | arrows                |
| proof of proposition A | inhabitation of type A    | arrow _f: t → A_      |
| **implication**        | **function type**         | **exponential**       |
| **conjunction**        | **product type**          | **product**           |
| **disjunction**        | **sum type**              | **coproduct**         |
| **falsity**            | **void type (empty)**     | **initial object**    |
| **truth**              | **unit type (singleton)** | **terminal object T** |

---

# [fit] **Numbers**

# [fit] **Multiplication**

# [fit] **Addition**

# [fit] **Exponentiation**

# [fit] **Division**

# [fit] in Types! 😮

---

# [fit] **Numbers**

---

# [fit] **Zero**

---

# [fit] **Void**

---

# [fit] `type Void = never;`

---

# [fit] **One**

---

# [fit] **Unit**

---

# [fit] `type Unit = void;`

---

# [fit] **Two**

---

# [fit] `2 = 1 + 1`

---

# [fit] `type Two = Void | Unit;`

---

# [fit] `type Bool = false | true;`

---

# [fit] **Three**

---

# [fit] `type RGB = "red" | "green" | "blue";`

---

# [fit] **Multiplication**

---

# [fit] `a × b`

---

# [fit] **Product**

---

# [fit] `type Pair<First, Second> = [First, Second];`

---

# [fit] How many values of type

# [fit] **`Pair<Bool, RGB>`**

# [fit] are there?

---

# [fit] `Pair<Bool, RGB>`

```typescript
const all: Pair<Bool, RGB>[] = [
  [true, "red"],
  [true, "green"],
  [true, "blue"],
  [false, "red"],
  [false, "green"],
  [false, "blue"],
];
```

---

# [fit] ≅

---

# [fit] Isomorphism

---

# [fit] Two types are isomorphic if they<br>have the same external behavior.

---

# [fit] One type can be implemented in<br>terms of the other or vice versa.

---

# [fit] **Laws**

---

# [fit] `0 × X = 0`

---

# [fit] `Pair<Void,X> ≅ Void`

---

# [fit] `1 × X ≅ X`

---

# [fit] `Pair<Unit,X> ≅ X`

---

# [fit] Commutativity

---

# [fit] `X × Y ≅ Y × X`

---

# [fit] `Pair<X,Y> ≅ Pair<Y,X>`

---

# [fit] Associativity

---

# [fit] `(a × b) ×  c ≅ a × (b × c)`

---

# [fit] `Pair<Pair<A, B>, C> ≅ Pair<A, Pair<B, C>>`

---

# [fit] **Addition**

---

# [fit] `a + b`

---

# [fit] **Sum**

---

# [fit] **Coproduct**

---

# [fit] `type Left<L> = { kind: "l"; value: L };`

# [fit] `type Right<R> = { kind: "r"; value: R };`

# [fit] `type Either<L, R> = Left<L> | Right<R>;``

---

# [fit] How many values of type

# [fit] **`Either<Bool, RGB>`**

# [fit] are there?

---

# [fit] `Either<Bool, RGB>`

```typescript
const all: Either<Bool, RGB>[] = [
  { k: "l", v: false },
  { k: "l", v: true },
  { k: "r", v: "red" },
  { k: "r", v: "green" },
  { k: "r", v: "blue" },
];
```

---

# [fit] `1 + a`

---

# [fit] `type Nothing = { k: "nothing" };`

# [fit] `type Just<T> = { k: "just"; v: T };`

# [fit] `type Maybe<T> = Nothing | Just<T>;`

---

# [fit] **Laws**

---

# [fit] `0 + X ≅ X`

---

# [fit] `Either<Void,X> ≅ X`

---

# [fit] Commutativity

---

# [fit] `X + Y ≅ Y + X`

---

# [fit] `Either<X,Y> ≅ Either<Y,X>`

---

# [fit] Associativity

---

# [fit] `(a + b) + c ≅ a + (b + c)`

---

# [fit] `Either<Either<A, B>, C> ≅ Either<A, Either<B, C>>`

---

# [fit] `coproduct ←→ product`

---

# [fit] Duality

---

# [fit] `(V → F, V → S) → (V → Pair<F, S>)`

---

# [fit] `(L → V, R → V) → (Either<L,R> → V)`

---

# [fit] `Either<A,B> → C ← Pair<A,B>`

---

# [fit] **Exponentiation**

---

# [fit] **R<sup>A</sup>**

---

# [fit] `type Reader<A, R> = (a: A) => R;`

---

# [fit] How many values of type

# [fit] **RGB<sup>Bool</sup>**

# [fit] are there?

---

# [fit] `(b: Bool) => RGB`

```typescript
const boolToRGB: ((b: Bool) => RGB)[] = [
  (_) => "red",
  (_) => "green",
  (_) => "blue",
  (b) => (b ? "red" : "green"),
  (b) => (b ? "red" : "blue"),
  (b) => (b ? "green" : "red"),
  (b) => (b ? "green" : "blue"),
  (b) => (b ? "blue" : "red"),
  (b) => (b ? "blue" : "green"),
];
```

---

# [fit] Laws

---

# [fit] **1<sup>A</sup> ≅ 1**

---

# [fit] `A → Unit ≅ Unit`

---

# [fit] **A<sup>1</sup> ≅ A**

---

# [fit] `Unit → A ≅ A`

---

# [fit] `(B × C)ᴬ = Bᴬ × Cᴬ`

---

# [fit] `A → Pair<B,C> ≅ Pair<A → B, A → C>`

---

# [fit] `Cᴮᴬ = (Cᴮ)ᴬ`

---

# [fit] `Pair<A,B> → C ≅ A → B → C`

---

# [fit] `Curry ≅ Uncurry`

---

# [fit] **Curry**

```typescript
const curry =
  <A, B, C>(fn: (a: A, b: B) => C): ((a: A) => (b: B) => C) =>
  (a: A) =>
  (b: B) =>
    fn(a, b);
```

---

# [fit] **Uncurry**

```typescript
const uncurry =
  <A, B, C>(fn: (a: A) => (b: B) => C): ((a: A, b: B) => C) =>
  (a: A, b: B) =>
    fn(a)(b);
```

---

# [fit] **Division**

---

# [fit] **Recursion**

---

# [fit] **Lists**

---

# [fit] `1 + A × List<A>`

---

```typescript
class Nil<A> {
  readonly _tag = "Nil" as const;
  private _phantom!: A;
}

class Cons<A> {
  readonly _tag = "Cons" as const;
  constructor(
    readonly head: A,
    readonly tail: List<A>,
  ) {}
}

type List<A> = Nil<A> | Cons<A>;
```

---

# [fit] `List<A> = 1 + A × List<A>`

---

# [fit] `List<A> - A × List<A> = 1`

---

# [fit] `List<A> × (1 - A) = 1`

---

# [fit] `List<A> = 1 / (1 - A)`

---

# [fit] A **Taylor series** is a way to represent a function<br>as an infinite sum of polynomial terms,<br>calculated from the function's derivatives at a single point.

---

# [fit] `List<A> = 1 + A × List<A>`

---

# [fit] **`List<A> = 1 + A × (1 + A × List<A>)`**

---

# [fit] `List<A> = 1 + A + (A×A) × List<A>`

---

# [fit] `List<A> = 1 + A + (A×A) × (1 + A × List<A>)`

---

# [fit] `List<A> = 1 + A + (A×A) + (A×A×A) × List<A>`

---

# [fit] `List<A> = 1 + A + (A×A) + (A×A×A) × (1 + A × List<A>)`

---

# [fit] `List<A> = 1 + A + (A×A) + (A×A×A) + (A×A×A×A) × List<A>`

---

# [fit] `List<A> = 1 / (1 - A)`

```haskell
List<A> = 1 / (1 - A)
        = 1 + A + A×A + A×A×A + A×A×A×A + ...
        = 1 + A + A² + A³ + A⁴ + ...
```

---

# [fit] Algebraic<br>structures

---

# [fit] **Group-like**

# [fit] **one** binary operation

---

# [fit] **Ring-like**

# [fit] **two** binary operations,

# [fit] often called addition and multiplication,

# [fit] with multiplication distributing over addition.

---

# [fit] **Lattice-like**

# [fit] **two** or more binary operations,

# [fit] including operations called meet and join,

# [fit] connected by the [absorption law](https://en.wikipedia.org/wiki/Absorption_law)

---

# [fit] **Module-like**

# [fit] composite systems involving two sets

# [fit] and employing at least two binary operations

---

# [fit] **Algebra-like**

# [fit] composite system defined over two sets,

# [fit] a ring R and an R-module M equipped with

# [fit] an operation called multiplication

---

# [fit] **Group-like**

# [fit] structures

---

# [fit] **Magma**

---

# [fit] A type with a<br>(closed) binary operation

---

# [fit] `A × A → A`

---

# [fit] `A × A → A`

```typescript
interface Magma<A> {
  readonly concat: (x: A, y: A) => A;
}
```

---

# [fit] **Semigroup**

---

# [fit] A magma where<br>the operation is associative

---

# [fit] `A × A → A`

```typescript
interface Semigroup<A> extends Magma<A> {}
```

---

# [fit] `concat(concat(a, b), c) ≅ concat(a, concat(b, c))`

---

# [fit] **Monoid**

---

# [fit] A semigroup with<br>an identity element

---

# [fit] `A × A + 1 → A`

```typescript
interface Monoid<A> extends Semigroup<A> {
  readonly empty: A;
}
```

---

# [fit] `concat(empty, x) ≅ x`

# [fit] `concat(x, empty) ≅ x`

---

# [fit] **Monoid<br>Examples**

---

# [fit] **Sum**

````typescript
const Sum: Monoid<number> = {
  concat: (x, y) => x + y,
  empty: 0
};
```

---

# [fit] **Sum**

```typescript
const values = [5, 10, 3];

let total = Sum.empty; // start at 0

for (const n of values) {
  total = Sum.concat(total, n); // accumulate via concat
}

console.log(total); // 18
````

---

# [fit] **Product**

````typescript
const Product: Monoid<number> = {
  concat: (x, y) => x * y,
  empty: 1
};
```
---

# [fit] **Product**

```typescript
const values = [5, 10, 3];

let total = Product.empty; // start at 1

for (const n of values) {
  total = Product.concat(total, n); // accumulate via concat
}

console.log(total); // 150
````

---

# [fit] **Endo**

```typescript
type Endo<A> = (a: A) => A;

const getEndoMonoid = <A>(): Monoid<Endo<A>> => ({
  concat: (f, g) => (x) => f(g(x)),
  empty: (x) => x,
});
```

---

# [fit] **Endo**

```typescript
const EndoNumber = getEndoMonoid<number>();

const multiplyBy =
  (n: number): Endo<number> =>
  (x) =>
    x * n;
const functions = values.map(multiplyBy); // [x => x*5, x => x*10, x => x*3]

let composedFunction = EndoNumber.empty;
for (const fn of functions) {
  composedFunction = EndoNumber.concat(composedFunction, fn);
}

const endoResult = composedFunction(1);
console.log("Endo result:", endoResult); // 150
```

---

# [fit] **List**

```typescript
const arrayMonoid = <T>(): Monoid<T[]> => ({
  concat: (x: T[], y: T[]) => [...x, ...y],
  empty: [],
});

const stringArrayMonoid = arrayMonoid<string>();

const a = ["hello", "world"];
const b = ["foo", "bar"];
const c = ["baz"];

const result1 = stringArrayMonoid.concat(a, b);
console.log(result1); // ["hello", "world", "foo", "bar"]

const result2 = stringArrayMonoid.concat(a, stringArrayMonoid.empty);
console.log(result2); // ["hello", "world"]
```

---

# [fit] Algebraic<br>Thinking

---

# [fit] No means no

---

```typescript
// ❌ BAD: Using null/undefined to mean something specific
interface BadSubscriptionPlan {
  name: string;
  maxUsers: number | null; // null means "unlimited users"
  maxStorage: number | null; // null means "unlimited storage"
}

const enterprisePlan: BadSubscriptionPlan = {
  name: "Enterprise",
  maxUsers: null, // This means unlimited, not "we don't know"
  maxStorage: null, // This means unlimited, not "not set"
};

function checkUserLimit(
  plan: BadSubscriptionPlan,
  currentUsers: number,
): boolean {
  if (plan.maxUsers === null) {
    // null means unlimited, so always allow
    return true;
  }
  return currentUsers <= plan.maxUsers;
}
```

---

```typescript
// ✅ GOOD: Be explicit about what you mean
type Limited = { type: "limited"; max: number };
type Unlimited = { type: "unlimited" };
type StorageLimit = Limited | Unlimited;

interface GoodSubscriptionPlan {
  name: string;
  userLimit: Limited | Unlimited;
  storageLimit: StorageLimit;
}

const goodEnterprisePlan: GoodSubscriptionPlan = {
  name: "Enterprise",
  userLimit: { type: "unlimited" }, // Clear meaning
  storageLimit: { type: "unlimited" }, // Clear meaning
};

function checkUserLimitGood(
  plan: GoodSubscriptionPlan,
  currentUsers: number,
): boolean {
  switch (plan.userLimit.type) {
    case "unlimited":
      return true;
    case "limited":
      return currentUsers <= plan.userLimit.max;
  }
}
```

---

# [fit] Parse

# [fit] Don't Validate

---

````typescript
// ❌ BAD: Validation approach
function validateEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function sendEmail(email: string, message: string) {
  if (!validateEmail(email)) {
    throw new Error("Invalid email");
  }
  // email is still just a string here!
}```
````

---

```typescript
// ✅ GOOD: Parse approach
type Email = { readonly _tag: "Email"; readonly value: string };

function parseEmail(input: string): Email | null {
  if (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input)) {
    return { _tag: "Email", value: input };
  }
  return null;
}

function sendEmailSafe(email: Email, message: string) {
  // email is guaranteed to be valid here!
  console.log(`Sending to ${email.value}: ${message}`);
}
```

---

```typescript
// ❌ BAD: Validation approach

function validateNonEmpty<T>(arr: T[]): boolean {
  return arr.length > 0;
}

function getFirstElement<T>(arr: T[]): T {
  if (!validateNonEmpty(arr)) {
    throw new Error("Array is empty!");
  }
  return arr[0]; // TypeScript still thinks this could be undefined!
}
```

---

````typescript
// ✅ GOOD: Parse approach
type NonEmptyArray<T> = readonly [T, ...T[]];

function parseNonEmptyArray<T>(arr: readonly T[]): NonEmptyArray<T> | null {
  if (arr.length === 0) return null;
  return arr as NonEmptyArray<T>;
}

// Now all these functions are completely safe with no defensive checks:

function head<T>(arr: NonEmptyArray<T>): T {
  return arr[0]; // Always defined!
}```
````

---

# [fit] Make impossible<br>states impossible

---

```typescript
// ❌ BAD: Invalid states are possible

interface BadUserStatus {
  isLoggedIn: boolean;
  username?: string;
  lastLoginTime?: Date;
  isGuest: boolean;
  guestId?: string;
  isPremium: boolean;
  subscriptionExpiry?: Date;
}

// Functions need defensive checks everywhere
function greetUser(user: BadUserStatus): string {
  if (user.isLoggedIn && user.username) {
    if (user.isGuest) {
      // Wait, how can they be logged in with username AND be a guest?
      return "Hello... uh...";
    }
    return `Welcome back, ${user.username}`;
  } else if (user.isGuest && user.guestId) {
    return `Welcome, Guest ${user.guestId}`;
  } else {
    return "Please log in";
  }
}
```

---

```typescript
// ✅ GOOD: Make impossible states impossible
type Guest = {
  type: "guest";
  guestId: string;
};

type FreeUser = {
  type: "free";
  username: string;
  lastLoginTime: Date;
};

type PremiumUser = {
  type: "premium";
  username: string;
  lastLoginTime: Date;
  subscriptionExpiry: Date;
};

type LoggedOut = {
  type: "logged-out";
};

type UserStatus = Guest | FreeUser | PremiumUser | LoggedOut;
```

---

```typescript
// ✅ GOOD: Make impossible states impossible
// Clean, exhaustive handling with no defensive checks
function greetUserGood(user: UserStatus): string {
  switch (user.type) {
    case "guest":
      return `Welcome, Guest ${user.guestId}`;
    case "free":
      return `Welcome back, ${user.username}`;
    case "premium":
      return `Welcome back, ${user.username} ⭐`;
    case "logged-out":
      return "Please log in";
  }
}
```

---

# [fit] Composing prompts

---

# [fit] Customizing tabs<br> different clients
