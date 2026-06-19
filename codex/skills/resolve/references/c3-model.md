# C³ Model

```text
immutable base B
monotone counterexample basis C
disposable candidates P
minimal surviving delivery patch P*
```

A new branch-liable counterexample invalidates the candidate:

```text
C := C ∪ {counterexample}
discard P
regenerate from B
```

Never patch the candidate in response to new review evidence.
