# Context Rendering

The inquiry produces several different surfaces. Do not collapse them.

```text
research record
  Search history, raw evidence, rival models, and working hypotheses used to keep
  the investigation honest.

doctrine
  The compressed latent constitution that explains important repository shape
  and changes future decisions.

consumer context
  The smallest doctrine projection required by one maintainer, agent, task, or
  change horizon.

evidence appendix
  Concrete support, exceptions, and unresolved questions needed to evaluate
  consequential doctrine claims.
```

The research record is not the doctrine. The doctrine is not automatically the
right active context for every consumer.

## Default repository doctrine

Render readable Markdown:

```markdown
# Repository Doctrine

## Scope and consumer
The repository state and change horizon this doctrine addresses.

## Governing pressures
The requirements, risks, and historical pressures that organize the system.

## Jurisdictions and authorities
Who may create, transition, certify, publish, transfer, roll back, retire, and
invalidate important state and evidence.

## Load-bearing laws
The small set of laws whose absence could cause plausible wrong decisions.

## Freedoms and non-laws
What may change and which current behavior must not be cargo-culted.

## Wound memory and rejected routes
Recurring failures, selection pressures, and currently applicable negative
routes.

## Governed aporia
Real contradictions or underdetermination that future work must keep visible.

## Change index
How likely classes of future change should use the doctrine.

## Knowledge destinations
Where durable doctrine should be enforced or retained.

## Evidence appendix
Compact references, exceptions, counterevidence, and open discriminating
questions.

## Confidence and next inquiries
Where the doctrine is strong, conditional, provisional, or blocked.
```

## Law form

Use this form for every consequential law:

```markdown
### [Law name]

**Law.** [What must remain true.]

**Jurisdiction.** [Where, when, and for which state or operation it applies.]

**Selection pressure.** [Why the repository needs this law.]

**Evidence.** [Current observations and exact references.]

**Counterexample.** [A violating trace or unacceptable observation.]

**Permitted variation.** [Representations, algorithms, layouts, or control flow
that may change.]

**Operational consequence.** [What future implementation, review, migration, or
planning must do differently.]

**Proof burden.** [What must establish preservation or intentional refinement.]

**Invalidators.** [Changes that would make the law obsolete, local, or contested.]
```

Do not omit permitted variation. The consumer must know what it may change as
clearly as what it must preserve.

## Authority form

For each consequential authority state:

```markdown
### [Authority or jurisdiction]

- **Owns:** state, evidence, certificate, or effect.
- **May:** create, mutate, validate, certify, publish, transfer, roll back,
  retire, or invalidate.
- **Canonical paths:** the transitions that exercise the authority.
- **Boundary:** where the authority begins and ends.
- **Shadow or bypass paths:** plausible competing owners.
- **Exceptions:** exceptional authority and its owner.
- **Evidence:** current references.
- **Invalidators:** changes that would move or split the authority.
```

## Governed-aporia form

```markdown
### [Tension]

- **Claim A / jurisdiction:** ...
- **Claim B / jurisdiction:** ...
- **Evidence for each:** ...
- **Why the tension matters:** ...
- **Bounded operating rule:** how future work proceeds before resolution.
- **Unsafe or conditional operations:** ...
- **Resolution surface:** evidence or owner decision that could close it.
```

Do not degrade aporia into generic uncertainty. State its operational effect.

## Change index

Index doctrine by likely work rather than by file tree.

Examples:

```text
add a new state transition
change a public boundary
migrate storage or schema
replace an internal representation
change validation or failure policy
introduce concurrency or retries
remove a fallback or duplicate check
change publication or rollback
add a repository-specific skill
```

For each class state:

```text
inspect
preserve
free to change
reject or treat as suspicious
prove
reopen when
```

## Task-context projection

For a named change `q`, render only doctrine that changes `q`.

```markdown
# Doctrine Context: [change]

## Inspect
## Preserve
## Free to change
## Reject or treat as suspicious
## Prove
## Governed aporia
## Reopen when
## Evidence
```

Do not load the entire repository doctrine into a consumer that needs only one
jurisdiction or law family.

## Refresh rendering

A refresh report should say:

```text
retained doctrine
revised doctrine and why
new doctrine and why
retired doctrine and why
new or resolved aporia
proof that must be rerun
consumer contexts invalidated or changed
```

Do not pretend a textual diff between doctrine documents is semantic refresh.

## Audit rendering

Compare guidance, skills, code, tests, tooling, CI, and negative evidence against
the doctrine. Report:

- missing doctrine;
- stale or contradicted guidance;
- cargo-cult restrictions with no current law;
- doctrine enforced by the wrong owner;
- duplicated authorities;
- proof that establishes examples but not laws;
- skills that should be narrowed, retired, or replaced by stronger enforcement.

## Portfolio rendering

Render portfolio decisions only after doctrine exists and only when requested.
For each candidate explain the recurring judgment, governing law, independent
trigger, observable value, stronger alternative considered, and retirement
condition.

## Format rule

Markdown is the default because the primary consumer is a model or human making
repository decisions. Use YAML or JSON only when an actual downstream owner
supplies a machine contract. Do not invent a machine contract to simulate rigor.
