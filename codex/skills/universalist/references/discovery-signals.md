# Discovery signals

Use these signals to find places where a stronger shape of truth may be cheaper than the current code.

## Signal table

| Signal | Likely construction | First seam | Proof hint | Reduction preflight |
|---|---|---|---|---|
| lifecycle encoded with `status`, booleans, nullables | coproduct | decoder, DTO mapper, reducer | exhaustive handling, invalid fixture rejection | Would a simple enum be enough? |
| same stable predicate in controller/service/storage | refined type / equalizer | parser or constructor | valid/invalid/normalization tests | Is the predicate stable and domain-owned? |
| two records must agree on tenant/account/version | pullback witness | aggregate constructor | mismatch rejection, projection preservation | Is agreement checked repeatedly or across trust boundary? |
| large branch chooses pricing/render/policy behavior | exponential | strategy/function injection | fixture parity | Is a table or direct branch clearer? |
| rule/workflow syntax mixed with eval/explain/log | free construction / AST | syntax data + one interpreter | differential interpreter tests | Are there at least two interpreters or a real need to persist/explain syntax? |
| fields travel together and are projected independently | product | value object/record | constructor/projection consistency | Would an existing record/object already suffice? |
| operations allowed only in certain states | coproduct + transition table | command handler/reducer | valid/invalid transition tests | Is current framework state wrapper useful or incidental? |

## Evidence quality

Strong evidence:

- multiple call sites with the same obligation;
- tests or fixtures showing invalid combinations;
- bug reports or comments about mismatch/invalid state;
- public boundary requiring compatibility;
- branches where adding one case requires many edits;
- duplicated normalization or parsing.

Weak evidence:

- one occurrence;
- speculative future variants;
- naming dislike;
- category jargon without a seam;
- no proof surface;
- construction would require a new library or framework.

## Output fields for scouts

When scouting, include:

```md
signal:
construction:
evidence:
first_seam:
boundary_hint:
blast_radius_estimate:
proof_hint:
reduce_preflight:
false_positive_risk:
```
