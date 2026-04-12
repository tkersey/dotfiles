# Program correctness patterns

## The default architecture

For verified programming in Lean, separate:

1. **specification**
2. **implementation**
3. **proof of agreement**

Do not jump straight into proving a complicated optimized function correct. First write the simplest mathematically clear model.

## The core refinement pattern

Use this shape repeatedly:

```lean
def spec (input : α) : β := ...

def impl (input : α) : β := ...

theorem impl_eq_spec (input : α) : impl input = spec input := by
  ...
```

If the implementation is optimized or tail-recursive, prove helper invariants first.

## Tail-recursive equivalence pattern

A common proof shape:

```lean
def sum : List Nat → Nat
  | [] => 0
  | x :: xs => x + sum xs

def sumTR (xs : List Nat) : Nat :=
  let rec go (acc : Nat) : List Nat → Nat
    | [] => acc
    | x :: xs => go (acc + x) xs
  go 0 xs

theorem go_eq (acc : Nat) (xs : List Nat) :
    (let rec go (acc : Nat) : List Nat → Nat
      | [] => acc
      | x :: xs => go (acc + x) xs
     ; go acc xs) = acc + sum xs := by
  induction xs generalizing acc with
  | nil =>
      simp [sum]
  | cons x xs ih =>
      simp [sum, ih, Nat.add_assoc, Nat.add_left_comm, Nat.add_comm]
```

The public theorem is then usually a one-line corollary obtained by setting the initial accumulator.

The key idea is not the exact syntax above; it is the invariant:  
**the helper with accumulator equals accumulator combined with the declarative spec**.

## Pure core, impure wrapper

For programs that eventually use `IO`, prefer this split:

```lean
def core (input : α) : β := ...

def main : IO Unit := do
  let out := core ...
  ...
```

Prove theorems about `core`, not about the entire `IO` program unless the user explicitly wants a semantics-level result.

## Total definitions first

Prefer total recursive functions.

Use well-founded recursion and termination proofs when structural recursion is not obvious.

Typical tools:

- `termination_by`
- `decreasing_by`

If proving termination is cumbersome, that is often a signal to rethink the recursion or introduce a cleaner helper theorem.

Avoid `partial` for logic-facing definitions. It makes later correctness proofs much worse.

## Invariant-carrying data

When the program manipulates values that should satisfy a predicate, prefer:

- a `structure` bundling fields with proofs
- a `Subtype`
- an explicit theorem that the function preserves the predicate

Example shape:

```lean
def PositiveNat := {n : Nat // 0 < n}
```

This is often more maintainable than pushing every invariant into a heavily indexed family of types.

## Arrays and imperative-looking code

Lean lets you write efficient code, but the proof strategy should stay mathematical.

When the implementation uses arrays, loops, or local mutation:

1. define a simple list-like or mathematical specification
2. relate the low-level state to the spec with an invariant
3. prove each update preserves the invariant
4. conclude final equivalence

Do not try to prove correctness by staring only at low-level updates. Always introduce a logical model.

## Bounds and local obligations

With arrays and indexed access, keep proof obligations local.

Good pattern:

- establish the bound exactly where the index is computed
- pass that proof directly into the indexing operation
- avoid carrying complicated bound terms far through the code if a local `have` solves it cleanly

## Strengthen the theorem when needed

When the public theorem is too weak for induction, prove a stronger helper first.

Typical examples:

- generalize an accumulator
- quantify over an arbitrary suffix or environment
- strengthen equality to a relational invariant over intermediate states

Then recover the final user-facing theorem as a specialization.

## Proof placement

Keep these items close together:

- the function
- its key helper lemmas
- its main correctness theorem

This prevents the proof architecture from becoming invisible to future readers.

## Practical correctness checklist

For every program you verify, ask:

- what is the cleanest mathematical spec?
- is the implementation total?
- if optimized, what is the refinement theorem?
- what invariant explains the loop or accumulator?
- can the public theorem be derived from a stronger helper?
- is `IO` isolated from the pure reasoning core?
- are all proof obligations discharged without placeholders?
