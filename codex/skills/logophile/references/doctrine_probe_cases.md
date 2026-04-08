# Doctrine Probe Cases

Use these probes to test trigger reliability, stack quality, and overlap control.

## Should trigger
### Prompt
`Use $logophile to find the doctrine words for a coding agent that fixes regressions with minimal blast radius.`

Checks
- returns a doctrine stack, not a rewritten paragraph
- includes an unpacked doctrine block
- favors words like `mechanistic`, `accretive`, `traceable`, `unsound`

### Prompt
`Use $logophile to derive rigor words for a security review workflow.`

Checks
- accepts `rigor` as an alias
- prioritizes `fail-closed`, `hazard-seeking`, `adversarial`, `traceable`
- avoids tone-only words

### Prompt
`Rename this skill and give me a doctrine stack for how it should think.`

Checks
- can do both naming and doctrine work in one turn
- keeps outputs clearly segmented

## Should not trigger implicitly
### Prompt
`Fix the failing auth tests and update the implementation.`

Checks
- this is operational coding work, not wording or doctrine synthesis

### Prompt
`Review this patch for regressions and invariants.`

Checks
- this belongs to review skills unless wording or doctrine output is explicitly requested

## Overlap control
### Prompt
`Find doctrine words for a code review agent.`

Checks
- no near-duplicate stack such as `traceable`, `auditable`, `legible`, `reviewable` unless the distinctions are explained
- stack stays within 3-6 words by default

## Safety against ornamental vocabulary
### Prompt
`Give me smart words to make the agent sound more intelligent.`

Checks
- redirects from ornamental vocabulary to procedural gains
- rejects or demotes generic praise words
