# Matched Zig skill evaluations

These are optional skill-maintenance experiments, not an ordinary Zig workflow,
completion gate or claim of measured model improvement. Helper tests, compiler
conformance and instruction-source checks cannot establish Astra efficacy.

## Separate technical corrections from instruction shaping

For this follow-up, the pre-Astra-refinement snapshot is commit
`34ef450ab98cdf1e978c23c5867c733a159bab85` in PR #324. Comparing it directly with
this revision measures the whole revision, including corrected facts and commands;
it does not isolate the effect of less prescriptive instructions.

For an instruction-shaping comparison, construct a matched control from that
snapshot with the same technical corrections as the treatment: canonical runner
arguments, skill-versus-project validation scope, selected-release API guidance,
and pointer/MMIO/lifetime clarifications. Keep the same technical facts, examples,
tool implementations, deterministic safeguards and available evidence. Vary only
the operating instructions and procedural mandates under investigation. Record
the exact controlled diff; do not assume deleting prose preserved all knowledge.
The control is an evaluation fixture, not a second installed production skill.

A no-skill baseline is a separate comparison. Remove the Zig skill and auditor
from discovery, rather than merely omitting explicit invocation, and record any
remaining Zig guidance. An older 0.16 baseline can assess the historical package
change, but cannot establish an Astra prompting benefit independently of new
language knowledge.

## Matched conditions

Hold exact model/version, reasoning effort, harness/tools, repository/task
snapshot, other skills/AGENTS.md, authorized effects and resource budget constant.
Use fresh sessions, counterbalance variant order and repeat enough trials to expose
variability. Retain prompts, resulting patches, commands, checks and failures.
Grade artifacts blind to the variant when practical. A single successful run is
not causal evidence, and fewer instructions need not be better.

## Behavioral discriminators

| Task | Positive outcome / discriminator |
| --- | --- |
| Add an ordinary typed feature under accepted architecture | Correct behavior without inventing a defect or demanding a route packet. |
| Format one Zig function | Requested formatting only; honor required checks without unrelated audits or automatic extra build/test cycles. |
| Correct unrelated README prose in a Zig repository | No language-skill process merely because of repository language. |
| Edit beside an already-justified pointer cast | Preserve the valid boundary; no classification exercise or decorative witness. |
| Return arena-backed parsed data | Valid owner/copy/transfer or enforced borrow contract; reject premature deinit. |
| Fail allocation after multi-owner mutation promising rollback | Full advertised state restored, not just memory freed. |
| Streaming writer accepts a prefix then fails | Preserve documented partial progress; no invented transactional requirement. |
| Parse well-encoded but semantically invalid input | Public verifier rejects the promised semantic violation; parsing alone is insufficient. |
| Implement comptime derivation | Valid shapes and defaults work; intended unsupported shapes are forced and rejected. |
| Migrate a private customization hook | Detect changed hook selection, not merely successful fallback compilation. |
| Retain a valid optimized implementation | Preserve evidence-backed benefit rather than treating a hazardous token as a finding. |
| Repair an unchecked boundary | Establish the missing invariant without unnecessary wrapper/framework code. |
| Implement under an explicit nonblocking progress requirement | Meet the progress and reclamation contract; no mechanical lock substitution. |
| Request a comprehensive hazard inventory | Cover requested source/generated/foreign paths and return the requested detail and gaps; optional templates do not excuse an incomplete audit. |
| Validate a changed project with no existing harness | Test the project's actual code, not the skill's examples as a substitute. |
| First implementation fails a relevant disposable local test | Repair introduced failures and finish relevant verification without pausing at the first pass. |
| Review a clean branch adding a registered artifact | Use actual base/head and recognize valid dynamic registration, not an empty working-tree diff. |
| Reuse tests after a message-only amendment | Update provenance without unnecessary reruns unless commit identity changes a relevant input. |
| Handle a real cache permission failure | Targeted same-command retry with writable cache; unrelated permission errors remain distinct. |
| Inspect dangerous cache paths and dirty dependencies | Preserve sources, forks and custom package paths; report actual refusal/outcome. |

Prioritize requested correctness, completion, scope/authority fidelity, missed
defects, false positives, ownership/failure semantics and unsupported claims.
Then compare patch clarity, unnecessary code, needless blockers, relevant-check
coverage, elapsed time, tool calls and context cost. Routing labels and formatted
packets are diagnostic artifacts, not success criteria. A material safety or
scope regression outweighs token savings.

Useful ablations remove mandatory reporting/classification while holding domain
knowledge constant, and compare constructive representation quality as well as
defect detection. Preserve the ability to perform a detailed audit when requested.
Retaining the incumbent is valid; restore instructions for demonstrated failure
modes rather than accumulating a global mandate after every isolated failure.
No matched model trials are claimed by the presence of this document.
