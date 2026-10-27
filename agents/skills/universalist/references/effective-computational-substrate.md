# Effective Computational Substrate

## Purpose

The substrate is the executable floor beneath Universal Architecture. It is the bridge between categorical specification and running software.

## Substrate components

### Computation representation

Examples:

- AST / free syntax / bytecode / command IR;
- closures or defunctionalized frames;
- state machines or coalgebras;
- process/message syntax;
- target-language functions, when inspection is not required.

### Evaluation

Name the total or partial function that gives syntax meaning:

```text
eval / run / compile / handle / lower / interpret
```

A universal-evaluation claim must say which programs and inputs it covers.

### Recursion and partiality

Universal computation requires an honest source of unbounded iteration or equivalent expressive power:

- general recursion;
- fixed-point/iteration operator;
- while/process loop over unbounded data;
- partial-map or lifting structure;
- an external runtime already known to be computationally universal.

Do not smuggle nontermination through unspecified host behavior.

### Effects and primitives

Represent external capabilities explicitly:

```text
FileIO
Network
Clock
Random
Database
ForeignAPI
HumanApproval
ModelCall
GPUKernel
```

Each primitive needs a handler, failure semantics, observation surface, and test/simulation strategy.

### State and interaction

For servers, UIs, protocols, workflows, and agents, model ongoing behavior rather than pretending the system is one terminating function.

```text
State × Input -> Output × State
```

or another coalgebraic/process form.

### Resources

Record at least the resource dimensions capable of invalidating the architecture:

```text
time
space
latency
throughput
contention
network cost
failure/retry
security/capability
persistence
deployment topology
```

## Substrate acceptance gate

A substrate is accepted only if one end-to-end witness can be represented, executed, observed, and verified through the declared architecture.
