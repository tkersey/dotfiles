# Authority-transfer failure pattern

This reference captures the failure mode that motivated `$resolve` v9.

## Diagnosis

The weak diagnosis is:

```text
$resolve is partly working but needs tighter closure and less accumulation.
```

The stronger diagnosis is:

```text
$resolve is failing at authority transfer.
```

The intended workflow transfers mutation authority from raw review prose to
sealed counterexample classes and then to one kernel. A failing workflow lets
useful work outrun that authority chain.

## Bad mechanism

```text
review comment pressure
-> local usefulness judgment
-> patch/proof activity
-> delivery closure language
-> retroactive workflow framing
```

## Intended mechanism

```text
review comment pressure
-> AC horizon
-> minimal CEX admission/rejection
-> CEB quotient
-> MBK/RC
-> RAC-v1
-> one realization
-> conformance and holdout
-> closure gate
```

## Compiler frame

Raw review comments are source text. AC/CEX/CEB/MBK/RC/RAC are parse,
typecheck, IR, optimization, codegen authorization, and closure proof.

The controller must not execute source text in the parser and print a successful
compile banner.

## Governing fix

```text
make uncompiled review text non-executable
```

In operational terms:

```text
No mutation unless a current artifact links the review claim to an accepted CEX
class, MBK/RC transition, proof obligation, and realization target.
```

## Canonical falsifier

Find a material run row in the target window with:

```text
c3_required=true
c3_entered=true
c3_closed=true
compression_state != NONE
batches_total > 0
kernel.accepted=true
potential.strict_progress > 0
delivery_closed=true
terminal_closed=true
closure_gate.status=passed
```

No such row means the workflow may have done useful review work, but it has not
proved `$resolve` compiler closure.
