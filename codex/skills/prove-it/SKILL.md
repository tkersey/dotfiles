---
name: prove-it
description: "Stress-test absolute, sweeping, overconfident, or suspiciously clean claims through an artifactless parallel subagent gauntlet. Dispatch nine independent evidence lenses concurrently, then give all packets to one oracle that alone owns the final verdict and final response. Requires subagents; never fake the gauntlet in the root thread."
metadata:
  version: "3.2.0"
  activation_cost: high
  default_depth: high
---
# Prove It

## Mission

Pressure-test a normalized claim through independent evidence generation and one
separate terminal adjudicator.

## Activation

Use for explicit prove/disprove/stress-test requests or claims whose truth
depends on hidden quantifiers, edge cases, adversaries, baselines, definitions,
or operating conditions.

Do not use for ordinary uncertainty that can be resolved directly.

## Root contract

```text
normalize claim and scope
-> dispatch rounds 1-9 concurrently
-> collect nine independent packets
-> dispatch round 10 oracle with all packets
-> validate and relay the oracle's final_response
```

Non-negotiable:

- rounds 1-9 use the reusable `prove_it_lens` role with distinct assignments;
- the nine lenses are dispatched before synthesis;
- lenses do not see one another and do not choose the final verdict;
- round 10 uses `prove_it_oracle` only after fan-in;
- the oracle alone chooses the terminal enum and writes final response text;
- root validates completeness and relays, but does not add a competing verdict;
- create no progress files, run directories, transcripts, manifests, or prompt
  dumps.

When subagents are unavailable, stop with:

```text
PROVE_IT_REQUIRES_SUBAGENTS
```

Do not simulate the ten rounds in root prose.

## Conditional disclosure

The complete execution contract is preserved byte-for-byte in
[FULL_CONTRACT.md](FULL_CONTRACT.md). Do not load it merely to decide whether the
skill applies.

Load it only after activation, when constructing or validating:

- the nine lens assignments and their modes;
- round packet schemas;
- oracle packet schema and terminal enum;
- fallback transport rules;
- lens-specific pressure questions;
- completeness and compromise handling.

Its frontmatter is archived source, not a second skill definition.

## Guardrails

- Evidence packets are not votes.
- Missing or failed lenses remain explicit inputs to the oracle.
- No worker may claim access to hidden chain of thought.
- Root must report a compromised oracle packet rather than silently rewriting
  its verdict.
