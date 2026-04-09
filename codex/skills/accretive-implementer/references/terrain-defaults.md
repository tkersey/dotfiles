# Terrain defaults

## Brownfield defaults
Use these defaults in legacy, high-entropy, or partially trusted code:
- minimize surface area
- prefer characterization or a tight repro when behavior is unclear
- prefer adapters and seams at boundaries over scattered caller-side repairs
- prefer the existing primitive or canonical helper before a bespoke wrapper
- cut temporary observability first when uncertainty is high, then remove it once proof exists

## Greenfield defaults
Use these defaults when you control the shape:
- start with the boundary and define failure behavior early
- choose a normal form when it will delete branching
- prefer one obvious path for each rule
- defer abstraction until it earns itself
- add the smallest fast proof signal that makes the contract executable
