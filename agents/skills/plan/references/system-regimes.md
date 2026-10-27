# System Regimes

## Clear

Cause and effect are stable and directly observable.

Compile:

```text
procedure -> proof -> terminal
```

Use checklists and precise preconditions. Do not add adaptive machinery without evidence.

## Complicated

Cause and effect exists but requires analysis or specialist evidence.

Compile:

```text
inspect/analyze -> decide -> execute -> prove
```

The specialist output must be observable and bounded.

## Complex

Cause and effect emerges through interaction and hindsight.

Compile:

```text
small probe -> observation -> belief update -> next bounded action
```

Do not commit to a full route before the discriminating evidence exists.

## Chaotic

Safety, control, or observability is broken.

Compile:

```text
contain -> make safe -> restore observability -> reclassify
```

Ordinary mutation and optimization remain shielded until stabilization exit criteria pass.

## Reclassification

A policy may reclassify only through declared observations and rules.

Examples:

```text
chaotic -> complicated after observability restored
complex -> deterministic after a decision experiment resolves the route
complicated -> return_to_spec when analysis reveals a semantic contradiction
```
