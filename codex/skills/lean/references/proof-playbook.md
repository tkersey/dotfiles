# Proof playbook

## Read the goal before touching tactics

For every stuck proof, identify:

- the goal's outermost shape: equality, implication, conjunction, existential, inductive constructor, etc.
- the relevant hypotheses already in context
- the head symbols in the goal
- whether the target is really a definitional equality problem in disguise

The fastest proof often comes from restating the goal into a friendlier form, not from adding more automation.

## Tactic ladder

Use this escalation order.

### 1. Definitional equality and simplification

Start with:

```lean
rfl
```

then:

```lean
simp
simpa
simp_all
```

Common patterns:

```lean
simpa [foo, bar] using h
simp [foo, bar] at h
```

Use `simp` when you want canonical simplification and normalization.

### 2. Targeted rewriting

Use `rw` when you want a specific rewrite in a chosen direction.

```lean
rw [h]
rw [← Nat.add_assoc]
```

Use:

- `nth_rewrite` for a specific occurrence
- `conv` when only a subterm should change
- `change` when the target is definitionally equal to a better-looking statement

### 3. Structural proof steps

Pick tactics that match the logical shape.

- implication / universal quantifier:
  ```lean
  intro x
  intro h
  ```

- conjunction / iff:
  ```lean
  constructor
  ```

- existential:
  ```lean
  refine ⟨witness, ?_⟩
  ```

- disjunction:
  ```lean
  left
  -- or
  right
  ```

- using intermediate claims:
  ```lean
  have h1 : P := by
    ...
  ```

- goal replacement:
  ```lean
  suffices h : Q from ...
  ```

### 4. Case splits and induction

For data or evidence in context:

```lean
cases h
rcases h with ...
```

For recursive structures:

```lean
induction xs with
| nil => ...
| cons x xs ih => ...
```

When the theorem follows a recursive function's call graph more closely than the data structure, prefer:

```lean
fun_induction f args
```

This is often the right move for theorems about well-founded or nontrivially recursive definitions.

## `simp` versus `rw`

Keep this distinction sharp:

- `simp` is for canonical simplification, repeated use of simplification lemmas, and inside-out normalization
- `rw` is for selected rewrites that you want to control manually

As a rule:

- use `simp` to expose the obvious normal form of a goal
- use `rw` when proof intent depends on a particular algebraic or definitional step
- do not replace every `simp` with `rw`, and do not expect `rw` to behave like full simplification

When proof stability matters, use:

```lean
simp only [lemma1, lemma2, ...]
```

## Automation: use deliberately, not first

Good escalation order after simplification:

```lean
exact?
apply?
aesop?
```

Then domain-specific automation if imports support it:

- `grind` for SMT-style contradiction search and mixed reasoning
- `linarith` for linear arithmetic
- `omega` for Presburger-style natural/integer arithmetic
- `ring` for polynomial ring equalities
- `norm_num` for arithmetic normalization on numerals

Automation is most reliable after the goal has been normalized and irrelevant hypotheses are cleaned up.

## Generated suggestions

If a suggestion-producing tactic or command gives a proof:

1. verify it really uses available imports
2. simplify the script if it is noisy
3. keep the generated version only if it is already short and robust

A dense, fragile block of automation is usually worse than one helper lemma plus a short concluding proof.

## Theorem discovery

Never fabricate theorem names.

Use this routine:

1. identify the key constants in the goal
2. inspect candidate declarations with:
   ```lean
   #check candidateName
   #print candidateName
   ```
3. search the local repository and imported dependencies
4. inspect nearby files for the style and theorem names actually in use

In practice, searching for the head symbol or constructor name is often enough to find the right lemma family.

## Local helper lemmas beat giant final proofs

When a proof becomes hard to read, split it.

Prefer:

- one helper lemma per recursion invariant
- one helper lemma per algebraic normalization step
- one final theorem that composes those helpers

This makes later maintenance easier and reduces dependence on brittle automation.

## Common proof refactors

### Turn a direct proof into `simpa`

Instead of:

```lean
have h' := foo h
exact h'
```

prefer:

```lean
simpa using foo h
```

### Generalize the accumulator

When tail recursion is involved, the induction hypothesis usually needs the accumulator generalized:

```lean
induction xs generalizing acc with
| nil => ...
| cons x xs ih => ...
```

### State the stronger theorem first

If the desired theorem is too weak for induction, strengthen it, prove the stronger form, then derive the public theorem as a corollary.

## Debugging checklist

If a proof still fails:

- inspect the exact goal state
- check whether hidden coercions or implicit arguments are changing the target
- unfold only the necessary definitions
- see whether a missing import is the real problem
- try a stronger induction hypothesis
- try functional induction
- try proving a more general theorem and specializing it afterward
