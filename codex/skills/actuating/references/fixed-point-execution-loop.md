# Fixed-Point Execution Loop

## Ownership

`$actuating` selects the route.

`$fixed-point-driver` realizes it.

```text
current GCR
-> valid AFR
-> ARH-v1
-> implementation
-> focused proof
-> FPSR-v1
-> st proof/complete
-> new GCR
```

## Required handoff

```text
run/slice/GCR/AFR IDs
selected task IDs
selected route
canonical owner
permitted scope
forbidden actions
surface budget
counterexample class
invariant
proof obligations
```

## Driver results

```text
valid
  route realized within boundary and focused proof passed

return_to_frontier
  new observation, owner change, scope expansion, or route invalidation

blocked
  environment/dependency/authority prevents realization

invalid
  boundary/surface/proof contract violated
```

## No hidden route selection

The driver must not:

```text
change owner
merge classes
introduce a new distinction
expand file/symbol scope
invent a fallback
```

It returns instead.
