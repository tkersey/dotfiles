# Prove It regression guards

Use when editing or evaluating the skill, not before a normal claim gauntlet.
The entrypoint retains every execution, packet, authority and stopping rule.

### Direct launch request

Input request: `Use prove-it on this claim: all swans are white.`

Expected behavior:

- root normalizes the claim;
- if subagents are available, root dispatches rounds 1-9 as parallel `prove_it_lens` assignments;
- if subagents are unavailable, stop with `PROVE_IT_REQUIRES_SUBAGENTS` instead of faking a root-only gauntlet;
- round 1 likely identifies black swans as candidate fatal pressure;
- root does not issue a final verdict before oracle;
- oracle decides the final verdict after all packets.

### Step, pause, or compression request

Inputs:

- `Run round 1 and wait for me.`
- `Do all ten rounds in one response.`

Expected behavior:

- do not run a manual sequential round;
- do not compress root-authored pseudo-rounds;
- use the parallel subagent gauntlet or stop with `PROVE_IT_REQUIRES_SUBAGENTS`.

### Artifactless run

Expected behavior:

- no `.prove-it-progress.md`;
- no `.prove-it-progress.template.md`;
- no `.prove-it-runs/`;
- no prompt/output transcript files;
- no manifest;
- final output only in conversation.

### Valid-looking early proof still reaches oracle

Input claim: `For every integer n, n + 0 = n.`

Expected behavior:

- support-oriented packets may record candidate decisive support;
- pressure packets still run;
- oracle decides whether the proof survives all lenses.
