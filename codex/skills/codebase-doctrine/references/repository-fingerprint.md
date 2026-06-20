# Repository Fingerprint

The fingerprint is a structural hypothesis, not doctrine.

Required:

```yaml
repository_fingerprint:
  repository_kind:
  primary_languages: []
  build_and_test_systems: []
  deployment_or_distribution:
  dominant_architecture:
  secondary_architecture:
  dependency_direction:
  top_level_subsystems: []
  public_contract_roots: []
  entrypoint_classes: []
  repository_dialect:
  confidence:
  evidence_refs: []
```

## Classification questions

- What starts execution?
- Which modules depend on which?
- Where does orchestration live?
- Where do domain transitions live?
- What is public?
- What persists?
- What crosses process/network/file boundaries?
- Is the repository homogeneous?
- Which conventions are local rather than language-wide?

## Pattern evidence

A pattern is supported by dependency direction and responsibilities, not folder labels.

Examples:

```text
layered
hexagonal/ports-adapters
pipeline
plugin
event-driven
state-machine/kernel
MVC/MVVM
compiler/interpreter
library plus adapters
monorepo of heterogeneous subsystems
```

Record runner-up patterns and subsystem exceptions.

## Repository dialect

Capture local vocabulary, naming, file organization, error model, test style, and ownership conventions that future skill language should use.
