# Fixed-Point Execution Loop

```text
current GCR
-> prepared ASL
-> validated FPS
-> bounded realization
-> focused proof
-> FPSR
-> matrix/$st frontier update
```

`$actuating` selects the route.

`$fixed-point-driver` realizes the selected route.

## Required handoff

- GCR and ASL refs;
- `$st` task IDs;
- owner/invariant;
- selected VMX rows;
- selected normal form;
- rejected routes;
- patch boundary;
- forbidden actions;
- surface budget;
- focused proof obligations;
- stop conditions.

## Stop conditions

Return to frontier when:

- a new counterexample class appears;
- authority/owner changes;
- boundary expansion is needed;
- a missing proof obligation was not represented;
- the selected normal form no longer covers the case.

Do not immediately patch the new observation.
