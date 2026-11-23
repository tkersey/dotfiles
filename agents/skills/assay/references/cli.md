# Optional Assay CLI

The Assay CLI is proposed for `tkersey/skills-zig`; this skill package does not
ship the executable. The assessment method works with existing domain tools and
evidence. A specification is not evidence that a command exists or ran.

## Select a verified interface

When an installed Assay CLI would help, establish that it is the skills-zig
implementation and inspect its installed help and capability response.
Use only commands, input versions, and output schemas that this executable
actually supports. Do not install it or substitute a same-named tool merely
because the skill activated.

The proposed v1 operations are `assay capabilities`, `assay assess`,
`assay compare`, and `assay explain`. Confirm flags from installed help;
do not invent behavior for an older or incompatible binary. If unavailable,
continue with native evidence and report only an actual dependent tooling gap.

## Bind inputs and consume results

The proposed CLI passively assesses explicit contract, subject, and evidence
inputs; existing authorized runners produce the observations. It supplies no
sandbox, agent runtime, execution permission, or new evidence store.

Supply the accepted contract and exact assessed subject. Distinguish verified
artifact bytes from an asserted manifest; a hash establishes identity, not
authority or truthful observation. Preserve the trusted source and scope of
imported domain judgments. A serialized `supported` field alone is not proof.

Read both operation status and assessment judgment. Under the proposed v1
interface, `assess` exits 0 for supported, 1 for refuted, 3 for unresolved, and
2 for an invalid invocation or input/integrity failure. A successful `compare`
or `explain` operation can describe a refuted or unresolved candidate; its
exit 0 does not qualify that candidate.

Inspect the decisive obligations, reasons, evidence applicability, and limits.
Do not promote a CLI result into a broader purpose, causal, population, or
production-readiness claim. Existing owners govern adoption and completion.
