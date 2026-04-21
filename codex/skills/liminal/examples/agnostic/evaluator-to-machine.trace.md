# Evaluator-to-Machine Trace

Use this trace when explaining why defunctionalization gives a machine rather than just a lower-level syntax.

## Source term

```text
((lambda x. x + 1) 41)
```

## Higher-order evaluator shape

```text
eval(term, env, k)

k ::= lambda v. v
    | lambda f. eval(arg, env, lambda a. apply(f, a, k))
    | lambda a. apply(f, a, k)
```

The continuations are higher-order functions whose free variables carry pending work.

## Defunctionalized continuation constructors

```text
Kont ::= Halt
       | Arg(arg, env, kont)
       | Fun(fun_value, kont)
```

Dispatcher:

```text
continue(Halt, v) = v
continue(Arg(arg, env, k), f) = eval(arg, env, Fun(f, k))
continue(Fun(f, k), a) = apply(f, a, k)
```

## Corresponding machine-state shape

```text
State ::= Eval(term, env, kont)
        | Apply(fun_value, arg_value, kont)
        | Continue(kont, value)
```

## Check

The evaluator step that calls a higher-order continuation should correspond to exactly one `Continue` transition using a first-order constructor. When environments are explicit, include closure conversion in the derivation chain.

Source anchors: `[DEF-DN-2001]`, `[DEF-AGER-2003]`, `[DEF-REFUNC-2007]`.
