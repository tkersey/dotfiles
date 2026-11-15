# Syntax / Semantics Certificate

A Syntax/Semantics Certificate records an explicit syntax, its semantic world, and the interpreter/laws connecting them.
Use it only when the receiving workflow needs an explicit certificate; reuse an
existing argument carrying these facts. See the
[construction argument](syntax-semantics-pivot.md#from-construction-rules-to-interpretation).

```text
Syntax/Semantics Certificate

Artifact:
  Plan / ToolOperation / PolicyRule / ContextSchema / Workflow / Patch / MemoryQuery / Operation IR:

Syntax world:
  constructors:
  formation rules:
  invalid forms:
  totality requirements:

Semantic world:
  required judgment and bound inputs/context:
  effects:
  observations:
  invariants:
  equivalence notion:

Interpreter / handler / compiler / renderer:
  function/module:
  owner:
  totality boundary:
  relevant semantic assumptions and invalidators:

Soundness law:
  primitive and composition justification:
  justified interpretation agrees with interpretation after evidence erasure:

Required coverage:
  required successful behavior and observable distinctions:

Execution correspondence:
  connection from the semantic argument to the actual implementation:

Preservation law:
  required contract, observational equivalence, or permitted refinement:

Falsifier:
  accepted syntax with invalid semantics:
  admitted description with a different actual effect:
  needed semantic behavior not expressible in syntax:

Status:
  planned / implemented / verified / obstructed
```

Use this when an agentic, workflow, policy, context, tool, or patch boundary is hard because syntax and semantics are collapsed.
