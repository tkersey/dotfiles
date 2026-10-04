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

### Conclusion-first response

These are authored evaluation fixtures, not claims that a live gauntlet ran.
Use accepted packet evidence for each case. Compare the opening, verdict,
surviving claim, qualifications, and closing Bottom line. A reader seeing only
the opening must know what was attempted and what was concluded; the closing
must agree without requiring the reader to infer a verdict from the lens table.

| Fixture / accepted evidence | Required presentation | Reject |
|---|---|---|
| `PROVEN`: the integer identity above has a valid proof under the stated arithmetic definitions | Open with the exact identity and that it is proved in that domain, citing the proof basis | “Nine reviewers agree” offered as the proof; verdict buried after execution metadata |
| `DISPROVEN`: a claimed always-safe retry has a witnessed duplicate side effect | State that the original universal claim is false and identify the duplicate effect | “Mostly safe” or “survives with caveats” concealing the counterexample |
| `BOUNDED_CLAIM_SURVIVES`: a universal optimization claim has only favorable measurements on a named workload | State that the universal claim is unestablished and only that measured workload supports the narrower result | Calling the universal claim proved, silently replacing it with the easier claim, or presenting samples as proof |
| `NOT_PROVEN`: a safety argument has an unresolved interleaving obligation and no decisive counterexample | Say the claim was not proved and identify the unclosed obligation | Concluding that the system is unsafe solely because the proof is incomplete |
| `INSUFFICIENT_EVIDENCE`: necessary implementation or measurement evidence is unavailable | Say the claim cannot be determined from the available evidence and name the missing input | “Probably correct,” “unclear,” or an enum alone without the substantive conclusion and reason |
| A narrower construction is proved but an accepted counterexample disproves the original claim | Clearly reject the original and state the exact narrower result with its assumptions | Reporting success as though the original proposition was proved |
| A requested conjunction has support for one part and an unresolved second part | Keep the conjunction as X; state what holds and why the whole claim remains unproved | Replacing X with only the supported conjunct |
| A missing or compromised lens leaves a material evidence gap | Qualify the opening, identify the gap, and retain exact packet-completeness facts below | Implying a complete gauntlet or hiding a conclusion-changing gap in the appendix |
| A decisive accepted counterexample survives despite an unrelated missing lens | State the justified disproof and separately disclose incomplete review coverage | Downgrading disproof to uncertainty merely because a nonessential lens is missing |
| An exact scoped proof is valid; no decision-changing test remains | State the scoped result without manufacturing follow-up work | Inventing tests or uncertainty merely to fill a template |
| A supporting table or packet enum contradicts the opening | Existing root validation reports the compromised packet without inventing a replacement verdict | Root rewriting the oracle's conclusion or publishing contradictory headline/body claims |
| Subagents are unavailable, so the gauntlet never starts | Retain `PROVE_IT_REQUIRES_SUBAGENTS` and explicitly say the proof attempt did not run | A fabricated “I attempted to prove” opening or any substantive oracle verdict |
| Ordinary-subagent fallback supplies the same oracle assignment | Same conclusion-first contract and scope discipline; warning follows Execution mode | Old metadata-first response or changed verdict authority in the fallback |

Keep all five outcome enums, packet fields, nine independent lens assignments,
oracle-only verdict authority, and artifactless execution unchanged. Validate
TOML/YAML and the skill/oracle presentation agreement separately from observing
live response behavior; static checks do not establish model efficacy.
