# World/boundary handoff trace

## universalist selected

- Signal: public contract determines internals.
- Seam: one payment endpoint.
- Boundary kind: projection.
- Artifact: lifted implementation.
- Proof signal: `project(realize(case)) == required(case)`.

## kan elaborates

- `A`: public contract cases.
- `B`: internal handler/service world.
- `C0`: observable HTTP response/audit behavior.
- `P`: run handler and observe response.
- `F`: required public behavior.
- Candidate: `Lft_P F`.

## representation pass

- Yoneda: public observations.
- Coyoneda: candidate realizer + projection path.
- Defunctionalization: observation and realizer constructors.
