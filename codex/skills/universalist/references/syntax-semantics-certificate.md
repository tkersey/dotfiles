# Syntax / Semantics Certificate

A Syntax/Semantics Certificate records an explicit syntax, its semantic world, and the interpreter/laws connecting them.

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
  effects:
  observations:
  invariants:
  equivalence notion:

Interpreter / handler / compiler / renderer:
  function/module:
  owner:
  totality boundary:

Soundness law:
  accepted syntax denotes valid semantics:

Adequacy law:
  required semantic distinctions are representable or observable:

Preservation law:
  syntax transformation preserves declared observations:

Falsifier:
  accepted syntax with invalid semantics:
  needed semantic behavior not expressible in syntax:

Status:
  planned / implemented / verified / obstructed
```

Use this when an agentic, workflow, policy, context, tool, or patch boundary is hard because syntax and semantics are collapsed.
