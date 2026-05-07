# Plugin API as Lan trace

Problem: add exporters to an existing AST.

Kan data:

```text
C = core AST constructors and rewrites
D = plugin-capable AST/exporter surface
K = inclusion of core AST into plugin AST
F = existing semantics: eval, typecheck, pretty-print
Candidate = Lan_K F
η = embed old semantics into plugin semantics
```

Witness object:

```text
d = MarkdownExporter target
```

Pointwise reading:

```text
Lan_K F(d) = generated/default exporter behavior from all core constructors that map into MarkdownExporter, quotiented by core rewrites.
```

Tests:

```text
prettyOld(expr) == prettyPlugin(embed(expr))
evalOld(expr) == evalPlugin(embed(expr))
rewriteOld(expr).then(embed).pretty == embed(expr).then(rewritePlugin).pretty
```

Architecture result:

- core semantics stay in `core/interpreter`;
- plugin API receives embedded core nodes;
- exporters must call central core semantic functions for core nodes;
- law tests live in `laws/plugin-core-compat.test`.
