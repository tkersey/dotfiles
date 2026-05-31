# Doctrine Probe Cases

Use these probes to test trigger reliability, stack quality, overlap control, and soundness vocabulary.

## Should trigger

### Prompt
`Use $logophile to find the doctrine words for a coding agent that fixes regressions with minimal blast radius.`

Checks:
- returns a doctrine stack, not a rewritten paragraph
- includes an unpacked doctrine block
- favors words like `mechanistic`, `accretive`, `traceable`, `unsound`

### Prompt
`Use $logophile to derive rigor words for a security review workflow.`

Checks:
- treats `rigor words` as a natural-language alias for doctrine words
- prioritizes `fail-closed`, `hazard-seeking`, `adversarial`, `traceable`
- avoids tone-only words

### Prompt
`Find words like unsound that make a code reviewer think in type-theoretic terms.`

Checks:
- returns words such as `unwitnessed`, `ill-typed`, `partial`, `illegal inhabitant`, `preservation-aware`, `progress-aware`
- explains the procedural gain of each word
- ends with a copy-pasteable doctrine block

### Prompt
`Rename this skill and give me a doctrine stack for how it should think.`

Checks:
- can do both naming and doctrine work in one turn
- keeps outputs clearly segmented
- ends with `Best Pick:` or `Use This:` depending on the requested final surface

## Should not trigger implicitly

### Prompt
`Fix the failing auth tests and update the implementation.`

Checks:
- this is operational coding work, not wording or doctrine synthesis

### Prompt
`Review this patch for regressions and invariants.`

Checks:
- this belongs to review skills unless wording or doctrine output is explicitly requested

## Overlap control

### Prompt
`Find doctrine words for a code review agent.`

Checks:
- no near-duplicate stack such as `traceable`, `auditable`, `legible`, `reviewable` unless distinctions are explained
- stack stays within 3-6 words by default

## Safety against ornamental vocabulary

### Prompt
`Give me smart words to make the agent sound more intelligent.`

Checks:
- redirects from ornamental vocabulary to procedural gains
- rejects or demotes generic praise words
