# Emulator Architecture

`$emulator` owns the contract and evaluation boundary for designed worlds and
session-derived partial charts.

```text
repositories, tests, design       sessions through Seq
             \                         /
              -> source-bound charts <-
                         |
                         v
             emulator-spec.yaml atlas closure
                         |
                         v
                 fresh actor runs
                         |
                         v
 hard oracles -> state diff -> trace invariants -> protected dimensions
              -> reward -> cost/latency -> residual judgment
                         |
                         v
                 EER-v1 and eligible datasets
```

Historical material nominates decisions and evaluators. It never supplies a
fresh comparison arm.
The complete normative precedence and failure semantics are owned by
`eer-v1.md`; this diagram does not shorten or override them.

## Responsibility split

| Owner | Owns | Does not own |
|---|---|---|
| Seq | Physical session discovery, source-event identity/order, messages, turns, tools, workers, tokens, and query limitations | Correction semantics, chart type, replayability, evaluator authority, or candidate quality |
| `$emulator` | Source bundles, charts, support boundaries, actor/evaluator projections, atlas closure, resets, evaluators, comparisons, EER-v1, datasets, and STOP | Truth of raw facts, undiscoverable user preference, live-harness adoption, or publication authority |
| CAS or selected existing runner | Fresh process/container execution, runtime identity, tool transport, actor trace, and terminal status | Chart authority or evaluator semantics |
| Git and task tools | Repository identity, reset state, fixtures, tests, state effects, and deterministic assertions | Harness policy |
| Human owner | Ambiguous correction adjudication, experimental factor, adoption, external publication, and privacy relaxation | Physical source facts |
| `$grill-me` | Material unresolved user judgments | Environment implementation |

The first implementation changes no Seq or CAS surface. If an existing actor
route cannot run a chart, use another already-supported runner or report the
chart blocked.

## Contract boundary

`emulator-spec.yaml` is the root of one recursive content-addressed closure,
not necessarily one physical file. The ordered root chart list binds exact chart
bytes. Each chart binds all external source, actor, world, reset, fixture, tool,
and evaluator bytes that can affect execution or judgment.

```text
same root bytes + ordered chart bytes + recursively bound assets
  -> same atlas identity
```

Changing a referenced byte without updating its parent fingerprint invalidates
the environment. Source bundles preserve exact Seq query specs and result
envelopes; free-form transcript paraphrase is not provenance.

## Partial transition boundary

Every action receives exactly one support class:

```text
executable    a resettable implementation can produce the next state
judgeable     the decision can be evaluated without a next state
denied        the contract deterministically forbids the action
observed_only history witnessed it, but no fresh counterfactual is supported
unsupported   the environment has no honest execution or judgment
```

`step` exists only for `executable`. Unknown transitions remain unknown. A
model-generated transition belongs to a separately designed chart and cannot
inherit source-faithful authority.

## Visibility boundary

The actor invocation receives only a fingerprinted actor projection. Historical
suffix, correction, recovery, outcome, grader labels, and holdout evaluators are
evaluator-only. Selection or training requires proof of the actor-readable
inventory and accessible tool roots; file-level separation alone is
insufficient.

## Comparison boundary

Both baseline and candidate arms are fresh. They bind the same chart, actor
packet, world/reset, effects, evaluator, runtime configuration, repeat policy,
and split identity. Only the selected semantic factor may differ; when that
factor owns declared runtime keys, runtime parity is evaluated after applying
exactly that validated key-local delta.

```text
hard failure or protected regression -> cannot be repaired by preference
unsupported or invalid environment -> not an agent failure
recommendation -> evidence only, never mutation authority
```

Use `$grill-me` only when source evidence cannot settle a material human
judgment. Missing authority is a gap or STOP, never permission to invent.
