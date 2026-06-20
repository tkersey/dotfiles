# Parser and Verifier Completeness

Parser safety and semantic verification are independent obligations.

## Parser totality contract

```yaml
parser_totality:
  input_domain:
  max_input:
  count_bounds:
  length_bounds:
  varint_or_LEB_bounds:
  unknown_case_policy:
  duplicate_case_policy:
  ordering_policy:
  resource_budget:
  panic_or_trap_forbidden:
  fuzz_or_differential_oracle:
```

Prove:

- arbitrary bytes do not panic or trap;
- malformed length/count arithmetic cannot overflow;
- loops always advance or terminate;
- allocations are bounded/admitted;
- unknown and custom sections are deliberate;
- duplicate/order/canonical forms are explicit;
- EOF/truncation is handled without out-of-bounds reads.

## Semantic verifier contract

```yaml
verifier_completeness:
  promised_property:
  public_predicate:
  strongest_internal_predicate:
  predicate_parity:
  declared_metadata: []
  observed_values: []
  lower_bounds: []
  upper_bounds: []
  final_state_or_stack_shape:
  all_relevant_entities: []
  invalid_well_formed_cases: []
  mutation_matrix: []
```

## Semantic mutation matrix

Mutate one property at a time:

```text
wrong opcode/tag
unknown/custom section
duplicate section
wrong order
huge count
malformed or non-canonical varint/LEB
declared metadata mismatch
lower-bound violation
upper-bound violation
extra memory/export/entity
missing required entity
dropped or extra stack result
wrong final result type/shape
stale generated constant
valid encoding with invalid semantics
```

Each mutation must fail through the public predicate downstream code actually uses.

## Strongest predicate rule

Example/debug checks may not be stricter than:

```text
passed()
verify()
isValid()
validationReport().passed
```

If multiple predicates exist, document their ordering and ensure the public authority uses the strongest relevant one.

## Fuzzing

Fuzzing is excellent for totality and parser state exploration.

It does not by itself prove that the verifier checks the promised property.

Combine:

```text
fuzz/differential parser oracle
+ semantic mutation matrix
+ property/state-machine tests where appropriate
```
