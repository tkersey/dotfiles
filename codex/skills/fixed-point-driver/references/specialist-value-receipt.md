# Specialist Value Receipt

Record value for each accepted or rejected specialist packet:

| role | packet status | artifact state id match | scope match | uncertainty class | route changed | finding added | proof changed | risk retired | value | used for | reason |
|---|---|---|---|---|---|---|---|---|---|---|---|

Classify value:

- `positive`: changed route, added a material finding, changed proof, or retired a plausible material risk
- `neutral`: valid packet with no material delta
- `negative`: stale, wrong-scope, transport-invalid, misleading, or avoidably duplicative packet
