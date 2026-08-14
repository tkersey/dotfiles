# Probe Catalog

Load this reference only when the material judgment graph needs a deeper domain probe or a high-regret decision needs one strongest stress test. These are search prompts, not mandatory lanes.

## General decision probes

### Problem layer

- What observable problem exists independently of the proposed solution?
- Would solving the named layer leave the motivating failure unchanged?
- What counterexample would show that the request targets a symptom?

### Scope and non-goals

- Which adjacent capability would materially change ownership, proof, or delivery?
- What tempting extension must remain excluded?
- Does a new answer expand the authoritative ask or merely clarify it?

### Authority and source of truth

- Who may make this commitment?
- Which representation, system, or actor remains authoritative during disagreement?
- Is the proposed owner capable of enforcing the claimed invariant?

### Success and proof

- What observation would make success defensible?
- What anti-metric prevents a local win from hiding a global regression?
- Is the requested proof available now, or does it require an experiment?

### Compatibility, rollout, and rollback

- Is compatibility a requirement, preference, or explicitly accepted break?
- What irreversible boundary is crossed at cutover?
- What must remain recoverable, and until when?

### Risk and stewardship

- Who accepts the residual risk?
- What failure mode changes the design rather than only the implementation?
- Who owns support, maintenance, invalidation, and retirement?

## Domain probes

### Software and systems

Use when public contracts, state, concurrency, failure isolation, data migration, security boundaries, or operational ownership are consequential.

Candidate questions:

- Which state or interface is authoritative?
- What must be impossible rather than merely checked?
- Which compatibility contract is user-owned?
- What failure must remain isolated or recoverable?
- Which proof requires runtime evidence rather than inspection?

### Product and workflow

Use when the primary user, behavior change, adoption path, success metric, pricing, support burden, or user-visible scope remains genuinely normative.

Candidate questions:

- Whose outcome dominates when stakeholder incentives conflict?
- What behavior must change for the work to count as successful?
- Which user-visible compromise is acceptable?
- What adoption or support burden is authorized?

### Data, AI, and evaluation

Use when ground truth, acceptable error, review authority, unsafe outputs, retention, or escalation policy requires user judgment.

Candidate questions:

- Who defines correctness where labels disagree?
- Which failure class is unacceptable even at lower aggregate performance?
- When must a human review, override, or escalate?
- What data use or retention boundary is authorized?

### Security and compliance

Use when trust, privacy, secrets, auditability, fail-closed behavior, or regulatory risk crosses an authority boundary.

Candidate questions:

- Which assets and actors define the threat boundary?
- Which residual risk can the user actually accept?
- What must fail closed?
- Who owns incident response and audit evidence?

### CLI and developer tools

Use when command contracts, automation compatibility, stdout/stderr behavior, exit codes, configuration precedence, or destructive operations are public commitments.

Candidate questions:

- Which existing scripts or clients must remain valid?
- What output is machine-consumed rather than human-facing?
- Which operation requires dry-run, idempotency, or explicit confirmation?
- What constitutes a breaking change?

## Stress-test operators

Choose at most the strongest relevant operator for a live high-regret decision:

- **Contradiction** — two locked commitments cannot both hold.
- **Counterexample** — one concrete case defeats an overbroad claim.
- **Root-layer** — the proposed choice does not address the motivating failure.
- **Second-order** — the choice changes incentives, support load, ownership, or future constraints.
- **Failure scenario** — partial failure, dirty state, concurrency, abuse, or rollback exposes a missing commitment.
- **Authority test** — the named decision-maker or owner cannot authorize or enforce the choice.
- **Proof test** — the proposed success criterion cannot distinguish success from a plausible failure.

Do not apply every operator. A probe earns its place only when its answer could change or prune the material judgment graph.

## Observation boundary

Reclassify a question as `observation-needed` when its discriminator depends on experience or evidence that conversation does not contain, including:

- interaction feel or comprehension;
- empirical user behavior;
- latency, throughput, cost, or reliability;
- integration feasibility;
- model quality or failure distribution;
- migration behavior on real data;
- comparative maintainability visible only in a concrete slice.

Select the smallest reversible evidence-producing action:

```text
throwaway prototype
narrow implementation spike
benchmark
trace or log capture
sample migration
usability observation
small evaluation set
fault injection
```

State the decision, probe, discriminator, and unblocked descendants. Do not design a full experiment when a smaller observation can decide the branch.
