autoscale: true

# [fit] Algebraic Structures<br>in TypeScript

## Beyond Monoids

---

# [fit] What We Know

## Monoid = **combine** + **empty**

```typescript
interface Monoid<A> {
  readonly empty: A;
  readonly concat: (x: A, y: A) => A;
}
```

---

# [fit] The Journey Ahead

## Core Abstractions
1. **Semigroup** - Associative operation
2. **Monoid** - Semigroup + identity
3. **Functor** - Transform values in a context
4. **Applicative** - Apply functions in a context
5. **Alternative** - Choice and failure
6. **Monad** - Chain computations in a context

## Advanced Structures
7. **Foldable** - Collapse structures
8. **Traversable** - Turn structures inside-out
9. **Group** - Reversible operations
10. **Ring** - Addition and multiplication with inverses
11. **Semiring** - Two operations that distribute
12. **Semi-Lattice** - Partial order with one operation
13. **Lattice** - Complete order with bounds

---

# [fit] Part 0: **Semigroup**

## The Foundation

---

# [fit] What's a Semigroup?

## Associative binary operation (no identity needed)

```typescript
interface Semigroup<A> {
  concat: (x: A, y: A) => A;
}

// Law: Associativity
// concat(concat(a, b), c) ≡ concat(a, concat(b, c))
```

---

# [fit] Real-World:<br>Non-Empty Lists

```typescript
type NonEmptyArray<A> = readonly [A, ...A[]];

const nonEmptyArraySemigroup = <A>(): Semigroup<NonEmptyArray<A>> => ({
  concat: (x, y) => [x[0], ...x.slice(1), ...y] as NonEmptyArray<A>
});

// Always safe - no empty result possible!
const combined = nonEmptyArraySemigroup<string>().concat(
  ["error1"],
  ["error2", "error3"]
); // ["error1", "error2", "error3"]
```

---

# [fit] Real-World:<br>Max/Min Values

```typescript
const maxSemigroup: Semigroup<number> = {
  concat: (x, y) => Math.max(x, y)
};

const minSemigroup: Semigroup<number> = {
  concat: (x, y) => Math.min(x, y)
};

// Finding bounds without initial value
const prices = [10.99, 25.50, 7.99, 15.00] as NonEmptyArray<number>;
const maxPrice = prices.reduce(maxSemigroup.concat); // 25.50
const minPrice = prices.reduce(minSemigroup.concat); // 7.99
```

---

# [fit] Real-World:<br>First/Last

```typescript
const firstSemigroup = <A>(): Semigroup<A> => ({
  concat: (x, _) => x  // Always keep first
});

const lastSemigroup = <A>(): Semigroup<A> => ({
  concat: (_, y) => y  // Always keep last
});

// Conflict resolution strategies
const configs = [
  { theme: "dark", fontSize: 12 },
  { theme: "light", fontSize: 14 },
  { theme: "auto", fontSize: 16 }
] as NonEmptyArray<Config>;

const firstWins = configs.reduce(firstSemigroup<Config>().concat);
// { theme: "dark", fontSize: 12 }

const lastWins = configs.reduce(lastSemigroup<Config>().concat);
// { theme: "auto", fontSize: 16 }
```

---

# [fit] Part 1: **Functor**

## The Gateway Abstraction

---

# [fit] What's a Functor?

## A structure you can **map** over

```typescript
interface Functor<F> {
  map: <A, B>(fa: F<A>, f: (a: A) => B) => F<B>;
}
```

---

# [fit] Functor Laws

```typescript
// Identity
map(fa, x => x) ≡ fa

// Composition
map(map(fa, f), g) ≡ map(fa, x => g(f(x)))
```

---

# [fit] Array is a Functor

```typescript
const arrayFunctor: Functor<Array> = {
  map: <A, B>(fa: A[], f: (a: A) => B): B[] => 
    fa.map(f)
};

// Usage
const numbers = [1, 2, 3];
const doubled = arrayFunctor.map(numbers, x => x * 2);
// [2, 4, 6]
```

---

# [fit] Option is a Functor

```typescript
type Option<A> = 
  | { type: "none" }
  | { type: "some"; value: A };

const optionFunctor: Functor<Option> = {
  map: <A, B>(fa: Option<A>, f: (a: A) => B): Option<B> => {
    switch (fa.type) {
      case "none": return { type: "none" };
      case "some": return { type: "some", value: f(fa.value) };
    }
  }
};

// Transform without unwrapping!
const maybeNumber: Option<number> = { type: "some", value: 42 };
const maybeString = optionFunctor.map(maybeNumber, n => `The answer is ${n}`);
```

---

# [fit] Promise is a Functor

```typescript
const promiseFunctor: Functor<Promise> = {
  map: <A, B>(fa: Promise<A>, f: (a: A) => B): Promise<B> => 
    fa.then(f)
};

// Chain transformations
const userPromise = fetchUser(123);
const userName = promiseFunctor.map(userPromise, user => user.name);
const upperName = promiseFunctor.map(userName, name => name.toUpperCase());
```

---

# [fit] Result is a Functor

```typescript
type Result<E, A> = 
  | { type: "error"; error: E }
  | { type: "ok"; value: A };

const resultFunctor = {
  map: <E, A, B>(
    fa: Result<E, A>, 
    f: (a: A) => B
  ): Result<E, B> => {
    switch (fa.type) {
      case "error": return fa;
      case "ok": return { type: "ok", value: f(fa.value) };
    }
  }
};

// Transform success, propagate errors
const parseResult = parseJSON(input);
const validated = resultFunctor.map(parseResult, validate);
const transformed = resultFunctor.map(validated, transform);
```

---

# [fit] Real-World:<br>Form Validation

```typescript
type ValidationResult<A> = Result<string[], A>;

// Parse and transform in a pipeline
const validateAge = (input: string): ValidationResult<number> => {
  const parsed = parseInt(input);
  if (isNaN(parsed)) return { type: "error", error: ["Invalid number"] };
  if (parsed < 0) return { type: "error", error: ["Age must be positive"] };
  return { type: "ok", value: parsed };
};

const validateForm = (data: FormData): ValidationResult<User> => {
  const age = validateAge(data.age);
  const ageInMonths = resultFunctor.map(age, a => a * 12);
  const category = resultFunctor.map(age, a => 
    a < 18 ? "minor" : "adult"
  );
  // ...
};
```

---

# [fit] Part 2: **Applicative**

## Functions in a Context

---

# [fit] The Problem

```typescript
// We have:
const maybeAdd: Option<(a: number) => (b: number) => number>;
const maybeX: Option<number>;
const maybeY: Option<number>;

// We want:
const maybeSum: Option<number>;

// But map doesn't help here!
```

---

# [fit] Enter Applicative

```typescript
interface Applicative<F> extends Functor<F> {
  of: <A>(a: A) => F<A>;
  ap: <A, B>(fab: F<(a: A) => B>, fa: F<A>) => F<B>;
}
```

---

# [fit] Option Applicative

```typescript
const optionApplicative: Applicative<Option> = {
  ...optionFunctor,
  
  of: <A>(a: A): Option<A> => 
    ({ type: "some", value: a }),
    
  ap: <A, B>(
    fab: Option<(a: A) => B>, 
    fa: Option<A>
  ): Option<B> => {
    if (fab.type === "none") return { type: "none" };
    if (fa.type === "none") return { type: "none" };
    return { type: "some", value: fab.value(fa.value) };
  }
};

// Now we can combine!
const add = (a: number) => (b: number) => a + b;
const maybeAdd = optionApplicative.of(add);
const maybe5 = optionApplicative.of(5);
const maybe3 = optionApplicative.of(3);

const maybeSum = optionApplicative.ap(
  optionApplicative.ap(maybeAdd, maybe5),
  maybe3
); // Some(8)
```

---

# [fit] Validation Applicative

```typescript
type Validation<E, A> = 
  | { type: "failure"; errors: E[] }
  | { type: "success"; value: A };

const validationApplicative: Applicative<Validation> = {
  of: <A>(a: A): Validation<never, A> => 
    ({ type: "success", value: a }),
    
  ap: <E, A, B>(
    fab: Validation<E, (a: A) => B>,
    fa: Validation<E, A>
  ): Validation<E, B> => {
    if (fab.type === "failure" && fa.type === "failure") {
      // Accumulate ALL errors!
      return { type: "failure", errors: [...fab.errors, ...fa.errors] };
    }
    if (fab.type === "failure") return fab;
    if (fa.type === "failure") return fa;
    return { type: "success", value: fab.value(fa.value) };
  }
};
```

---

# [fit] Real-World:<br>Parallel Validation

```typescript
// Validate all fields, accumulate all errors
const validateUser = (
  name: string,
  email: string,
  age: string
): Validation<string, User> => {
  const validName = validateName(name);   // Validation<string, string>
  const validEmail = validateEmail(email); // Validation<string, Email>
  const validAge = validateAge(age);       // Validation<string, number>
  
  // Create user if all valid, collect all errors if not
  const createUser = (name: string) => (email: Email) => (age: number) =>
    ({ name, email, age });
    
  return pipe(
    validationApplicative.of(createUser),
    fab => validationApplicative.ap(fab, validName),
    fab => validationApplicative.ap(fab, validEmail),
    fab => validationApplicative.ap(fab, validAge)
  );
};

// If multiple fields invalid, get ALL errors at once!
validateUser("", "not-an-email", "-5");
// Failure(["Name required", "Invalid email", "Age must be positive"])
```

---

# [fit] Promise Applicative

```typescript
const promiseApplicative: Applicative<Promise> = {
  ...promiseFunctor,
  
  of: <A>(a: A): Promise<A> => 
    Promise.resolve(a),
    
  ap: async <A, B>(
    fab: Promise<(a: A) => B>,
    fa: Promise<A>
  ): Promise<B> => {
    const [f, a] = await Promise.all([fab, fa]);
    return f(a);
  }
};

// Parallel async operations!
const fetchUserData = async (userId: string) => {
  const combine = (profile: Profile) => (posts: Post[]) => (friends: User[]) =>
    ({ profile, posts, friends });
    
  return pipe(
    promiseApplicative.of(combine),
    fab => promiseApplicative.ap(fab, fetchProfile(userId)),
    fab => promiseApplicative.ap(fab, fetchPosts(userId)),
    fab => promiseApplicative.ap(fab, fetchFriends(userId))
  );
  // All three requests happen in parallel!
};
```

---

# [fit] Part 3: **Monad**

## The Big One

---

# [fit] The Problem

```typescript
// We have:
const parseJSON: (s: string) => Option<unknown>;
const validate: (data: unknown) => Option<User>;
const fetchProfile: (user: User) => Promise<Profile>;

// How do we compose these?
// map gives us Option<Option<User>> 😢
```

---

# [fit] Enter Monad

```typescript
interface Monad<M> extends Applicative<M> {
  flatMap: <A, B>(ma: M<A>, f: (a: A) => M<B>) => M<B>;
}

// Also called: bind, chain, >>=, then
```

---

# [fit] Option Monad

```typescript
const optionMonad: Monad<Option> = {
  ...optionApplicative,
  
  flatMap: <A, B>(
    ma: Option<A>,
    f: (a: A) => Option<B>
  ): Option<B> => {
    switch (ma.type) {
      case "none": return { type: "none" };
      case "some": return f(ma.value);
    }
  }
};

// Now we can chain!
const result = pipe(
  parseJSON(input),
  json => optionMonad.flatMap(json, validate),
  user => optionMonad.flatMap(user, fetchFromCache)
);
// Option<Profile>, not Option<Option<Option<Profile>>>!
```

---

# [fit] Result Monad

```typescript
const resultMonad: Monad<Result> = {
  ...resultApplicative,
  
  flatMap: <E, A, B>(
    ma: Result<E, A>,
    f: (a: A) => Result<E, B>
  ): Result<E, B> => {
    switch (ma.type) {
      case "error": return ma;
      case "ok": return f(ma.value);
    }
  }
};

// Chain operations that might fail
const processPayment = (amount: number): Result<string, Payment> =>
  pipe(
    validateAmount(amount),
    amt => resultMonad.flatMap(amt, checkBalance),
    balance => resultMonad.flatMap(balance, deductFunds),
    funds => resultMonad.flatMap(funds, recordTransaction)
  );
// First error short-circuits the chain
```

---

# [fit] Promise Monad

```typescript
const promiseMonad: Monad<Promise> = {
  ...promiseApplicative,
  
  flatMap: <A, B>(
    ma: Promise<A>,
    f: (a: A) => Promise<B>
  ): Promise<B> => 
    ma.then(f)
};

// This is just async/await!
const getGrandchildren = (userId: string): Promise<User[]> =>
  pipe(
    fetchUser(userId),
    user => promiseMonad.flatMap(user, u => fetchChildren(u.id)),
    children => promiseMonad.flatMap(
      children, 
      cs => Promise.all(cs.map(c => fetchChildren(c.id)))
    ),
    grandchildren => promiseMonad.map(grandchildren, gcs => gcs.flat())
  );
```

---

# [fit] Real-World:<br>API Chain

```typescript
type ApiResult<A> = Promise<Result<ApiError, A>>;

// Monad for async operations that can fail
const apiMonad = {
  flatMap: <A, B>(
    ma: ApiResult<A>,
    f: (a: A) => ApiResult<B>
  ): ApiResult<B> =>
    ma.then(result => {
      switch (result.type) {
        case "error": return Promise.resolve(result);
        case "ok": return f(result.value);
      }
    })
};

// Complex API workflow
const createOrder = (request: OrderRequest): ApiResult<Order> =>
  pipe(
    validateOrder(request),
    req => apiMonad.flatMap(req, checkInventory),
    items => apiMonad.flatMap(items, reserveStock),
    reserved => apiMonad.flatMap(reserved, chargePayment),
    payment => apiMonad.flatMap(payment, createShipment),
    shipment => apiMonad.map(shipment, s => ({
      ...s,
      status: "confirmed"
    }))
  );
```

---

# [fit] Do Notation

```typescript
// Helper for readable monad chains
function* doOption<A>(
  gen: () => Generator<Option<any>, A, any>
): Option<A> {
  const iterator = gen();
  let state = iterator.next();
  
  while (!state.done) {
    const option = state.value;
    if (option.type === "none") return { type: "none" };
    state = iterator.next(option.value);
  }
  
  return { type: "some", value: state.value };
}

// Much cleaner!
const result = doOption(function* () {
  const json = yield parseJSON(input);
  const user = yield validate(json);
  const profile = yield fetchFromCache(user.id);
  return profile;
});
```

---

# [fit] Bonus: **Alternative**

## Choice and Failure

---

# [fit] What's Alternative?

```typescript
interface Alternative<F> extends Applicative<F> {
  zero: <A>() => F<A>;  // Identity for alt
  alt: <A>(fx: F<A>, fy: () => F<A>) => F<A>;  // Choice
}

// Laws:
// Associativity: alt(a, () => alt(b, () => c)) ≡ alt(alt(a, () => b), () => c)
// Identity: alt(zero(), () => fa) ≡ fa
// Distributivity: ap(alt(a, () => b), c) ≡ alt(ap(a, c), () => ap(b, c))
```

---

# [fit] Option Alternative

```typescript
const optionAlternative: Alternative<Option> = {
  ...optionApplicative,
  
  zero: <A>(): Option<A> => ({ type: "none" }),
  
  alt: <A>(fx: Option<A>, fy: () => Option<A>): Option<A> => 
    fx.type === "some" ? fx : fy()
};

// Try alternatives until one succeeds
const findUser = (id: string): Option<User> =>
  optionAlternative.alt(
    findInCache(id),
    () => optionAlternative.alt(
      findInDatabase(id),
      () => findInArchive(id)
    )
  );
```

---

# [fit] Array Alternative

```typescript
const arrayAlternative: Alternative<Array> = {
  ...arrayApplicative,
  
  zero: <A>(): A[] => [],
  
  alt: <A>(fx: A[], fy: () => A[]): A[] => [...fx, ...fy()]
};

// Combine multiple searches
const searchResults = arrayAlternative.alt(
  searchByName(query),
  () => arrayAlternative.alt(
    searchByEmail(query),
    () => searchByPhone(query)
  )
);
```

---

# [fit] Parser Alternative

```typescript
const parserAlternative: Alternative<Parser> = {
  ...parserApplicative,
  
  zero: <A>(): Parser<A> => 
    _ => ({ type: "none" }),
    
  alt: <A>(px: Parser<A>, py: () => Parser<A>): Parser<A> =>
    input => {
      const result = px(input);
      return result.type === "some" ? result : py()(input);
    }
};

// Parse number or string
const value = parserAlternative.alt(
  parseNumber,
  () => parseString
);

// Parse different date formats
const date = parserAlternative.alt(
  parseISO8601,
  () => parserAlternative.alt(
    parseUSDate,
    () => parseEUDate
  )
);
```

---

# [fit] Real-World:<br>Fallback Chains

```typescript
// Configuration with fallbacks
const getConfig = <T>(key: string): IO<Option<T>> =>
  ioAlternative.alt(
    readEnvVar(key),
    () => ioAlternative.alt(
      readConfigFile(key),
      () => ioAlternative.alt(
        readDatabase(key),
        () => readDefaults(key)
      )
    )
  );

// API with retry logic
const fetchWithFallback = (url: string): Task<Response> =>
  taskAlternative.alt(
    fetchFromPrimary(url),
    () => taskAlternative.alt(
      delay(1000).chain(() => fetchFromSecondary(url)),
      () => delay(2000).chain(() => fetchFromCache(url))
    )
  );
```

---

# [fit] Part 4: **Foldable**

## Collapsing Structures

---

# [fit] What's Foldable?

## A structure you can reduce to a single value

```typescript
interface Foldable<F> {
  reduce: <A, B>(
    fa: F<A>,
    b: B,
    f: (b: B, a: A) => B
  ) => B;
}
```

---

# [fit] Array is Foldable

```typescript
const arrayFoldable: Foldable<Array> = {
  reduce: <A, B>(
    fa: A[],
    b: B,
    f: (b: B, a: A) => B
  ): B => fa.reduce(f, b)
};

// Sum all numbers
const sum = arrayFoldable.reduce([1, 2, 3, 4], 0, (acc, n) => acc + n);
```

---

# [fit] Tree is Foldable

```typescript
type Tree<A> = 
  | { type: "leaf"; value: A }
  | { type: "branch"; left: Tree<A>; right: Tree<A> };

const treeFoldable: Foldable<Tree> = {
  reduce: <A, B>(
    tree: Tree<A>,
    b: B,
    f: (b: B, a: A) => B
  ): B => {
    switch (tree.type) {
      case "leaf": 
        return f(b, tree.value);
      case "branch":
        const leftResult = treeFoldable.reduce(tree.left, b, f);
        return treeFoldable.reduce(tree.right, leftResult, f);
    }
  }
};

// Count all nodes
const nodeCount = treeFoldable.reduce(myTree, 0, (count, _) => count + 1);
```

---

# [fit] Option is Foldable

```typescript
const optionFoldable: Foldable<Option> = {
  reduce: <A, B>(
    fa: Option<A>,
    b: B,
    f: (b: B, a: A) => B
  ): B => {
    switch (fa.type) {
      case "none": return b;
      case "some": return f(b, fa.value);
    }
  }
};

// Get value or default
const value = optionFoldable.reduce(
  maybeNumber,
  0,
  (_, n) => n
);
```

---

# [fit] Derived Operations

```typescript
// Build useful operations from reduce
const foldableOps = <F>(F: Foldable<F>) => ({
  toArray: <A>(fa: F<A>): A[] =>
    F.reduce(fa, [] as A[], (arr, a) => [...arr, a]),
    
  exists: <A>(fa: F<A>, predicate: (a: A) => boolean): boolean =>
    F.reduce(fa, false, (found, a) => found || predicate(a)),
    
  forAll: <A>(fa: F<A>, predicate: (a: A) => boolean): boolean =>
    F.reduce(fa, true, (all, a) => all && predicate(a)),
    
  find: <A>(fa: F<A>, predicate: (a: A) => boolean): Option<A> =>
    F.reduce(
      fa,
      { type: "none" } as Option<A>,
      (opt, a) => opt.type === "some" ? opt : 
        predicate(a) ? { type: "some", value: a } : opt
    ),
    
  length: <A>(fa: F<A>): number =>
    F.reduce(fa, 0, (count) => count + 1)
});
```

---

# [fit] Part 5: **Traversable**

## Inside-Out Transformations

---

# [fit] The Problem

```typescript
// We have:
const promises: Array<Promise<User>>;

// We want:
const promiseOfArray: Promise<Array<User>>;

// Or:
const results: Array<Result<Error, Data>>;
// Want:
const resultOfArray: Result<Error, Array<Data>>;
```

---

# [fit] Enter Traversable

```typescript
interface Traversable<T> extends Functor<T>, Foldable<T> {
  traverse: <F, A, B>(
    A: Applicative<F>,
    ta: T<A>,
    f: (a: A) => F<B>
  ) => F<T<B>>;
}
```

---

# [fit] Array Traversable

```typescript
const arrayTraversable: Traversable<Array> = {
  ...arrayFunctor,
  ...arrayFoldable,
  
  traverse: <F, A, B>(
    A: Applicative<F>,
    ta: A[],
    f: (a: A) => F<B>
  ): F<B[]> => {
    // Start with empty array in F
    let result: F<B[]> = A.of([]);
    
    // Add each transformed element
    for (const a of ta) {
      const fb = f(a);
      result = A.ap(
        A.map(result, (arr) => (b: B) => [...arr, b]),
        fb
      );
    }
    
    return result;
  }
};
```

---

# [fit] Real-World:<br>Batch Validation

```typescript
// Validate array of inputs, get back validation of array
const validateAll = (
  inputs: string[]
): Validation<string, Email[]> =>
  arrayTraversable.traverse(
    validationApplicative,
    inputs,
    validateEmail
  );

validateAll(["alice@example.com", "bob@example.com"]);
// Success([Email("alice@example.com"), Email("bob@example.com")])

validateAll(["alice@example.com", "not-an-email", "also-bad"]);
// Failure(["Invalid email: not-an-email", "Invalid email: also-bad"])
```

---

# [fit] Real-World:<br>Parallel Fetching

```typescript
// Fetch all users in parallel
const fetchAllUsers = (
  userIds: string[]
): Promise<User[]> =>
  arrayTraversable.traverse(
    promiseApplicative,
    userIds,
    fetchUser
  );

// All requests happen in parallel!
const users = await fetchAllUsers(["123", "456", "789"]);
```

---

# [fit] Sequence

```typescript
// Special case: when f is identity
const sequence = <T, F, A>(
  T: Traversable<T>,
  A: Applicative<F>,
  tfa: T<F<A>>
): F<T<A>> =>
  T.traverse(A, tfa, x => x);

// Turn array of promises into promise of array
const promises = [fetchUser("1"), fetchUser("2"), fetchUser("3")];
const promiseOfUsers = sequence(
  arrayTraversable,
  promiseApplicative,
  promises
);

// Turn array of results into result of array
const results = [parseNumber("1"), parseNumber("2"), parseNumber("3")];
const resultOfNumbers = sequence(
  arrayTraversable,
  resultApplicative,
  results
);
```

---

# [fit] Part 6: **Group**

## Reversible Operations

---

# [fit] From Monoid to Group

```typescript
// Monoid: combine + identity
interface Monoid<A> {
  empty: A;
  concat: (x: A, y: A) => A;
}

// Group: monoid + inverse
interface Group<A> extends Monoid<A> {
  inverse: (a: A) => A;
}
```

---

# [fit] Additive Group

```typescript
const additiveGroup: Group<number> = {
  empty: 0,
  concat: (x, y) => x + y,
  inverse: x => -x
};

// Now we can subtract!
const subtract = (x: number, y: number) =>
  additiveGroup.concat(x, additiveGroup.inverse(y));

subtract(10, 3); // 7
```

---

# [fit] Multiplicative Group

```typescript
// For non-zero numbers
type NonZero = number & { readonly __brand: "NonZero" };

const multiplicativeGroup: Group<NonZero> = {
  empty: 1 as NonZero,
  concat: (x, y) => (x * y) as NonZero,
  inverse: x => (1 / x) as NonZero
};

// Now we can divide!
const divide = (x: NonZero, y: NonZero) =>
  multiplicativeGroup.concat(x, multiplicativeGroup.inverse(y));
```

---

# [fit] XOR Group

```typescript
const xorGroup: Group<boolean> = {
  empty: false,
  concat: (x, y) => x !== y,  // XOR
  inverse: x => x             // Self-inverse!
};

// Perfect for toggle operations
const toggle = (state: boolean) =>
  xorGroup.concat(state, true);

// Encryption/decryption with same operation
const encrypt = (bit: boolean, key: boolean) =>
  xorGroup.concat(bit, key);
  
const decrypt = (encrypted: boolean, key: boolean) =>
  xorGroup.concat(encrypted, key); // Same operation!
```

---

# [fit] Real-World:<br>Undo/Redo

```typescript
// Operations that can be undone
type Operation<State> = {
  apply: (state: State) => State;
  undo: (state: State) => State;
};

const operationGroup = <State>(): Group<Operation<State>> => ({
  empty: {
    apply: x => x,
    undo: x => x
  },
  concat: (op1, op2) => ({
    apply: state => op2.apply(op1.apply(state)),
    undo: state => op1.undo(op2.undo(state))
  }),
  inverse: op => ({
    apply: op.undo,
    undo: op.apply
  })
});

// Track document changes
const moveOp: Operation<Doc> = {
  apply: doc => ({ ...doc, cursor: doc.cursor + 1 }),
  undo: doc => ({ ...doc, cursor: doc.cursor - 1 })
};
```

---

# [fit] Part 7: **Semiring**

## Two Operations

---

# [fit] What's a Semiring?

```typescript
interface Semiring<A> {
  add: (x: A, y: A) => A;
  zero: A;
  mul: (x: A, y: A) => A;
  one: A;
}

// Laws:
// (a + b) + c = a + (b + c)  -- addition associative
// a + 0 = a                  -- addition identity
// a + b = b + a              -- addition commutative
// (a * b) * c = a * (b * c)  -- multiplication associative
// a * 1 = a                  -- multiplication identity
// a * (b + c) = a*b + a*c    -- distribution
```

---

# [fit] Number Semiring

```typescript
const numberSemiring: Semiring<number> = {
  add: (x, y) => x + y,
  zero: 0,
  mul: (x, y) => x * y,
  one: 1
};

// Normal arithmetic
```

---

# [fit] Boolean Semiring

```typescript
const booleanSemiring: Semiring<boolean> = {
  add: (x, y) => x || y,  // OR
  zero: false,
  mul: (x, y) => x && y,  // AND
  one: true
};

// Logic operations distribute!
// a && (b || c) = (a && b) || (a && c)
```

---

# [fit] Tropical Semiring

```typescript
// Min-plus algebra (for shortest path algorithms)
const tropical: Semiring<number> = {
  add: (x, y) => Math.min(x, y),
  zero: Infinity,
  mul: (x, y) => x + y,
  one: 0
};

// Used in optimization problems
const shortestPath = (distances: number[][]): number => {
  // Floyd-Warshall with tropical semiring
  return distances.reduce((d, _) =>
    d.map((row, i) =>
      row.map((_, j) =>
        d[i].reduce((min, _, k) =>
          tropical.add(min, tropical.mul(d[i][k], d[k][j])),
          tropical.zero
        )
      )
    )
  )[0][n-1];
};
```

---

# [fit] Real-World:<br>Regex Matching

```typescript
// Regex as semiring
type Regex = 
  | { type: "empty" }              // Matches nothing
  | { type: "epsilon" }            // Matches empty string
  | { type: "char"; value: string }
  | { type: "concat"; left: Regex; right: Regex }
  | { type: "union"; left: Regex; right: Regex }
  | { type: "star"; inner: Regex };

const regexSemiring: Semiring<Regex> = {
  zero: { type: "empty" },         // Matches nothing
  add: (a, b) => ({ type: "union", left: a, right: b }), // a|b
  one: { type: "epsilon" },        // Matches empty string
  mul: (a, b) => ({ type: "concat", left: a, right: b }) // ab
};

// Build complex patterns
const digit = { type: "char", value: "[0-9]" };
const digits = { type: "star", inner: digit };      // [0-9]*
const number = regexSemiring.mul(digit, digits);    // [0-9][0-9]*
```

---

# [fit] Bonus: **Ring**

## Semiring + Subtraction

---

# [fit] What's a Ring?

```typescript
interface Ring<A> extends Semiring<A> {
  sub: (x: A, y: A) => A;  // Subtraction
}

// Derived from Group + Semiring
// sub(x, y) = add(x, negate(y))
```

---

# [fit] Integer Ring

```typescript
const integerRing: Ring<number> = {
  ...numberSemiring,
  sub: (x, y) => x - y
};

// Polynomial evaluation
const evalPolynomial = (coeffs: number[], x: number): number =>
  coeffs.reduce((acc, coeff, i) => 
    integerRing.add(
      acc,
      integerRing.mul(coeff, Math.pow(x, i))
    ),
    integerRing.zero
  );

// 3x² - 2x + 1 at x = 4
evalPolynomial([1, -2, 3], 4); // 41
```

---

# [fit] Matrix Ring

```typescript
type Matrix2x2 = [[number, number], [number, number]];

const matrix2x2Ring: Ring<Matrix2x2> = {
  zero: [[0, 0], [0, 0]],
  one: [[1, 0], [0, 1]],
  
  add: ([[a, b], [c, d]], [[e, f], [g, h]]) => 
    [[a + e, b + f], [c + g, d + h]],
    
  sub: ([[a, b], [c, d]], [[e, f], [g, h]]) => 
    [[a - e, b - f], [c - g, d - h]],
    
  mul: ([[a, b], [c, d]], [[e, f], [g, h]]) => [
    [a*e + b*g, a*f + b*h],
    [c*e + d*g, c*f + d*h]
  ]
};

// Linear transformations
const rotate90: Matrix2x2 = [[0, -1], [1, 0]];
const scale2: Matrix2x2 = [[2, 0], [0, 2]];

const combined = matrix2x2Ring.mul(rotate90, scale2);
```

---

# [fit] Polynomial Ring

```typescript
// Polynomials as arrays of coefficients
type Polynomial = number[];

const polynomialRing: Ring<Polynomial> = {
  zero: [],
  one: [1],
  
  add: (p1, p2) => {
    const len = Math.max(p1.length, p2.length);
    const result = [];
    for (let i = 0; i < len; i++) {
      result[i] = (p1[i] || 0) + (p2[i] || 0);
    }
    return result;
  },
  
  sub: (p1, p2) => {
    const len = Math.max(p1.length, p2.length);
    const result = [];
    for (let i = 0; i < len; i++) {
      result[i] = (p1[i] || 0) - (p2[i] || 0);
    }
    return result;
  },
  
  mul: (p1, p2) => {
    const result = new Array(p1.length + p2.length - 1).fill(0);
    for (let i = 0; i < p1.length; i++) {
      for (let j = 0; j < p2.length; j++) {
        result[i + j] += p1[i] * p2[j];
      }
    }
    return result;
  }
};

// (x + 1) * (x - 1) = x² - 1
const xPlus1 = [1, 1];    // 1 + x
const xMinus1 = [-1, 1];   // -1 + x
polynomialRing.mul(xPlus1, xMinus1); // [-1, 0, 1] = -1 + 0x + x²
```

---

# [fit] Part 8: **Semi-Lattice**

## Partial Order with One Operation

---

# [fit] What's a Semi-Lattice?

```typescript
// Join semi-lattice: only has join (least upper bound)
interface JoinSemiLattice<A> {
  join: (x: A, y: A) => A;  // Least upper bound
}

// Meet semi-lattice: only has meet (greatest lower bound)
interface MeetSemiLattice<A> {
  meet: (x: A, y: A) => A;  // Greatest lower bound
}

// Laws (for join):
// Associative: join(a, join(b, c)) = join(join(a, b), c)
// Commutative: join(a, b) = join(b, a)
// Idempotent: join(a, a) = a
```

---

# [fit] Real-World:<br>Version Control

```typescript
type Version = {
  major: number;
  minor: number;
  patch: number;
};

// Join semi-lattice for versions (max version)
const versionJoinSemiLattice: JoinSemiLattice<Version> = {
  join: (v1, v2) => {
    if (v1.major > v2.major) return v1;
    if (v1.major < v2.major) return v2;
    if (v1.minor > v2.minor) return v1;
    if (v1.minor < v2.minor) return v2;
    if (v1.patch >= v2.patch) return v1;
    return v2;
  }
};

// Find minimum required version
const requiredVersion = dependencies.reduce(
  (min, dep) => versionJoinSemiLattice.join(min, dep.minVersion),
  { major: 0, minor: 0, patch: 0 }
);
```

---

# [fit] Real-World:<br>Event Timestamps

```typescript
// Lamport timestamps for distributed systems
type LamportTimestamp = number;

const timestampSemiLattice: JoinSemiLattice<LamportTimestamp> = {
  join: (t1, t2) => Math.max(t1, t2)
};

// Vector clocks for causality
type VectorClock = Map<NodeId, number>;

const vectorClockSemiLattice: JoinSemiLattice<VectorClock> = {
  join: (vc1, vc2) => {
    const result = new Map(vc1);
    for (const [node, time] of vc2) {
      result.set(node, Math.max(time, result.get(node) || 0));
    }
    return result;
  }
};

// Merge concurrent events
const mergedClock = vectorClockSemiLattice.join(event1.clock, event2.clock);
```

---

# [fit] Real-World:<br>CRDT Sets

```typescript
// Grow-only set (G-Set) - join semi-lattice
type GSet<T> = Set<T>;

const gsetSemiLattice = <T>(): JoinSemiLattice<GSet<T>> => ({
  join: (s1, s2) => new Set([...s1, ...s2])  // Union only
});

// Two-phase set - can add and remove
type TPSet<T> = {
  added: Set<T>;
  removed: Set<T>;
};

const tpsetSemiLattice = <T>(): JoinSemiLattice<TPSet<T>> => ({
  join: (s1, s2) => ({
    added: new Set([...s1.added, ...s2.added]),
    removed: new Set([...s1.removed, ...s2.removed])
  })
});

// Current elements = added - removed
const elements = <T>(tpset: TPSet<T>): Set<T> =>
  new Set([...tpset.added].filter(x => !tpset.removed.has(x)));
```

---

# [fit] Real-World:<br>Access Control

```typescript
// Capabilities that can only increase
type Capabilities = {
  read: boolean;
  write: boolean;
  execute: boolean;
  admin: boolean;
};

const capabilitiesSemiLattice: JoinSemiLattice<Capabilities> = {
  join: (c1, c2) => ({
    read: c1.read || c2.read,
    write: c1.write || c2.write,
    execute: c1.execute || c2.execute,
    admin: c1.admin || c2.admin
  })
};

// Merge permissions from multiple roles
const userCapabilities = userRoles
  .map(role => role.capabilities)
  .reduce(capabilitiesSemiLattice.join, {
    read: false,
    write: false,
    execute: false,
    admin: false
  });
```

---

# [fit] Real-World:<br>Knowledge Tracking

```typescript
// What a node knows about the system
type Knowledge = {
  knownNodes: Set<NodeId>;
  knownFacts: Map<FactId, Fact>;
  timestamp: number;
};

const knowledgeSemiLattice: JoinSemiLattice<Knowledge> = {
  join: (k1, k2) => ({
    knownNodes: new Set([...k1.knownNodes, ...k2.knownNodes]),
    knownFacts: new Map([...k1.knownFacts, ...k2.knownFacts]),
    timestamp: Math.max(k1.timestamp, k2.timestamp)
  })
};

// Gossip protocol - merge knowledge
const updateKnowledge = (
  local: Knowledge,
  remote: Knowledge
): Knowledge =>
  knowledgeSemiLattice.join(local, remote);
```

---

# [fit] Part 9: **Lattice**

## Complete Order

---

# [fit] Lattice = Both Operations

```typescript
interface Lattice<A> extends JoinSemiLattice<A>, MeetSemiLattice<A> {
  join: (x: A, y: A) => A;  // Least upper bound
  meet: (x: A, y: A) => A;  // Greatest lower bound
}

// Additional law:
// Absorption: join(a, meet(a, b)) = a
//           meet(a, join(a, b)) = a
```

---

# [fit] Set Lattice

```typescript
const setLattice = <T>(): Lattice<Set<T>> => ({
  join: (a, b) => new Set([...a, ...b]),    // Union
  meet: (a, b) => new Set(
    [...a].filter(x => b.has(x))
  )                                          // Intersection
});

// Permissions as sets
const adminPerms = new Set(["read", "write", "delete"]);
const userPerms = new Set(["read", "write"]);

const combined = setLattice.join(adminPerms, userPerms);  // All permissions
const common = setLattice.meet(adminPerms, userPerms);    // Shared permissions
```

---

# [fit] Security Levels

```typescript
type SecurityLevel = 
  | "public"
  | "internal" 
  | "confidential"
  | "secret"
  | "top-secret";

const securityLattice: Lattice<SecurityLevel> = {
  join: (a, b) => {
    const levels = ["public", "internal", "confidential", "secret", "top-secret"];
    const aIndex = levels.indexOf(a);
    const bIndex = levels.indexOf(b);
    return levels[Math.max(aIndex, bIndex)];
  },
  meet: (a, b) => {
    const levels = ["public", "internal", "confidential", "secret", "top-secret"];
    const aIndex = levels.indexOf(a);
    const bIndex = levels.indexOf(b);
    return levels[Math.min(aIndex, bIndex)];
  }
};

// Information can only flow up
const canAccess = (userLevel: SecurityLevel, docLevel: SecurityLevel) =>
  securityLattice.join(userLevel, docLevel) === userLevel;
```

---

# [fit] Bounded Lattice

```typescript
interface BoundedLattice<A> extends Lattice<A> {
  top: A;     // Maximum element
  bottom: A;  // Minimum element
}

const intervalLattice: BoundedLattice<[number, number]> = {
  join: ([a1, a2], [b1, b2]) => 
    [Math.min(a1, b1), Math.max(a2, b2)],
  meet: ([a1, a2], [b1, b2]) => 
    [Math.max(a1, b1), Math.min(a2, b2)],
  top: [-Infinity, Infinity],
  bottom: [Infinity, -Infinity]
};

// Interval arithmetic for bounds checking
const priceRange: [number, number] = [10, 50];
const discountRange: [number, number] = [0, 0.3];

const possiblePrices = intervalLattice.join(
  priceRange,
  [10 * 0.7, 50]  // With max discount applied
);
```

---

# [fit] Real-World:<br>Type Inference

```typescript
type Type = 
  | { kind: "any" }      // Top type
  | { kind: "unknown" }
  | { kind: "string" }
  | { kind: "number" }
  | { kind: "literal"; value: string | number }
  | { kind: "never" };   // Bottom type

const typeLattice: BoundedLattice<Type> = {
  top: { kind: "any" },
  bottom: { kind: "never" },
  
  join: (a, b) => {
    // Type union - least common supertype
    if (a.kind === "never") return b;
    if (b.kind === "never") return a;
    if (a.kind === "any" || b.kind === "any") return { kind: "any" };
    if (a.kind === b.kind) return a;
    if (a.kind === "literal" && b.kind === "literal") {
      if (typeof a.value === typeof b.value) {
        return { kind: typeof a.value as "string" | "number" };
      }
    }
    return { kind: "unknown" };
  },
  
  meet: (a, b) => {
    // Type intersection
    if (a.kind === "any") return b;
    if (b.kind === "any") return a;
    if (a.kind === "never" || b.kind === "never") return { kind: "never" };
    if (a.kind === b.kind) return a;
    return { kind: "never" };
  }
};
```

---

# [fit] Putting It All Together

---

# [fit] Parser Combinators

```typescript
// Parser is a monad!
type Parser<A> = (input: string) => Option<[A, string]>;

const parserMonad: Monad<Parser> = {
  of: <A>(a: A): Parser<A> => 
    input => ({ type: "some", value: [a, input] }),
    
  map: <A, B>(pa: Parser<A>, f: (a: A) => B): Parser<B> =>
    input => {
      const result = pa(input);
      if (result.type === "none") return result;
      const [a, rest] = result.value;
      return { type: "some", value: [f(a), rest] };
    },
    
  flatMap: <A, B>(pa: Parser<A>, f: (a: A) => Parser<B>): Parser<B> =>
    input => {
      const result = pa(input);
      if (result.type === "none") return result;
      const [a, rest] = result.value;
      return f(a)(rest);
    },
    
  ap: <A, B>(pf: Parser<(a: A) => B>, pa: Parser<A>): Parser<B> =>
    parserMonad.flatMap(pf, f =>
      parserMonad.map(pa, a => f(a))
    )
};
```

---

# [fit] Building Complex Parsers

```typescript
// Applicative style for parallel parsing
const parseUser = 
  (name: string) => (age: number) => (email: Email) => 
    ({ name, age, email });

const userParser = pipe(
  parserMonad.of(parseUser),
  pf => parserMonad.ap(pf, parseString),
  pf => parserMonad.ap(pf, parseNumber),
  pf => parserMonad.ap(pf, parseEmail)
);

// Alternative for choice
const valueParser = alternative(
  parseNumber,
  parseString,
  parseBoolean
);

// Monadic sequencing
const configParser = doParser(function* () {
  yield string("{");
  const key = yield parseIdentifier;
  yield string(":");
  const value = yield valueParser;
  yield string("}");
  return { [key]: value };
});
```

---

# [fit] State Management

```typescript
// State monad for complex state transitions
type State<S, A> = (state: S) => [A, S];

const stateMonad = <S>(): Monad<State<S, any>> => ({
  of: <A>(a: A): State<S, A> => 
    state => [a, state],
    
  map: <A, B>(sa: State<S, A>, f: (a: A) => B): State<S, B> =>
    state => {
      const [a, newState] = sa(state);
      return [f(a), newState];
    },
    
  flatMap: <A, B>(sa: State<S, A>, f: (a: A) => State<S, B>): State<S, B> =>
    state => {
      const [a, newState] = sa(state);
      return f(a)(newState);
    }
});

// Game state management
type GameState = {
  player: Position;
  enemies: Position[];
  score: number;
};

const movePlayer = (direction: Direction): State<GameState, void> =>
  state => [
    undefined,
    { ...state, player: move(state.player, direction) }
  ];
```

---

# [fit] Effect Systems

```typescript
// IO monad for controlled side effects
type IO<A> = () => A;

const ioMonad: Monad<IO> = {
  of: <A>(a: A): IO<A> => 
    () => a,
    
  map: <A, B>(ioa: IO<A>, f: (a: A) => B): IO<B> =>
    () => f(ioa()),
    
  flatMap: <A, B>(ioa: IO<A>, f: (a: A) => IO<B>): IO<B> =>
    () => f(ioa())()
};

// Compose effects
const program = doIO(function* () {
  const name = yield readLine("What's your name?");
  yield writeLine(`Hello, ${name}!`);
  const age = yield readLine("What's your age?");
  const nextYear = parseInt(age) + 1;
  yield writeLine(`Next year you'll be ${nextYear}`);
  return { name, age };
});

// Effects only happen when executed
const result = program(); // Now side effects happen
```

---

# [fit] Type-Level Programming

```typescript
// Functor at the type level
type Functor<F> = {
  map: <A, B>(f: (a: A) => B) => (fa: HKT<F, A>) => HKT<F, B>;
};

// Higher-kinded types simulation
interface HKT<F, A> {
  _F: F;
  _A: A;
}

// Natural transformations
type NaturalTransformation<F, G> = {
  <A>(fa: HKT<F, A>): HKT<G, A>;
};

// Transform Option to Array
const optionToArray: NaturalTransformation<"Option", "Array"> = 
  <A>(option: Option<A>): A[] =>
    option.type === "some" ? [option.value] : [];

// Transform Array to Option (head)
const arrayToOption: NaturalTransformation<"Array", "Option"> =
  <A>(arr: A[]): Option<A> =>
    arr.length > 0 
      ? { type: "some", value: arr[0] }
      : { type: "none" };
```

---

# [fit] Key Takeaways

## Basic Building Blocks
- **Semigroup** - Combine values (no identity needed)
- **Monoid** - Semigroup + empty element
- **Group** - Monoid + inverse

## Functorial Structures
- **Functor** - Transform values in context
- **Applicative** - Apply functions in context
- **Alternative** - Choose between computations
- **Monad** - Chain dependent computations

## Advanced Patterns
- **Foldable/Traversable** - Generic iteration
- **Semiring/Ring** - Arithmetic-like operations
- **Semi-Lattice/Lattice** - Order and merging

---

# [fit] Why Should I Care?

- **Composability** - Small pieces that fit together
- **Reusability** - Write generic operations once
- **Correctness** - Laws guide implementation
- **Abstraction** - Focus on structure, not details

---

# [fit] Start Small

1. Recognize **map** patterns → Use Functor
2. See parallel operations → Try Applicative
3. Need sequencing → Reach for Monad
4. Spot reduction → Apply Foldable

## The abstractions are already in your code!

---

# [fit] Thank You!

## Questions?

### Resources:
- [Fantasy Land Spec](https://github.com/fantasyland/fantasy-land)
- [fp-ts Library](https://gcanti.github.io/fp-ts/)
- [Professor Frisby's Guide](https://mostly-adequate.gitbook.io/mostly-adequate-guide/)
- [Bartosz Milewski's Category Theory](https://bartoszmilewski.com/2014/10/28/category-theory-for-programmers-the-preface/)