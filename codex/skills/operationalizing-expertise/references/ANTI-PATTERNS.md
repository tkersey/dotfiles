# Anti-Patterns

Common mistakes when operationalizing expertise, and how to avoid them.

## Corpus Anti-Patterns

### Using Secondary Sources

**Problem**: Relying on summaries, Wikipedia, textbooks, or third-party interpretations.

**Why It Fails**:
- Secondary sources filter through someone else's understanding
- Nuances and context are lost
- Idiosyncratic methods are normalized away
- You capture the field's consensus, not the expert's edge

**Fix**: Always start with primary sources—interviews, original papers, direct recordings.

```markdown
# BAD: Secondary source
"According to the biography, Brenner believed in systematic experimentation."

# GOOD: Primary source with anchor
"You can only know [function] by asking what happens when it's not there." (§147)
```

### Corpus Without Anchors

**Problem**: Quotes floating without citation to specific source locations.

**Why It Fails**:
- Can't verify claims
- Can't find context when needed
- Can't distinguish expert's words from paraphrase
- Hallucinations become indistinguishable from evidence

**Fix**: Every quote gets `§n` anchor back to corpus segment.

---

## Distillation Anti-Patterns

### Single-Model Distillation

**Problem**: Using only one model to extract methodology.

**Why It Fails**:
- Each model has systematic biases
- GPT tends toward optimization framing
- Claude tends toward philosophical framing
- Gemini tends toward minimal framing
- You get model bias, not expert methodology

**Fix**: Always use 3+ models, then triangulate.

### Prompt Without Operator Focus

**Problem**: Generic "summarize this expert's methodology" prompts.

**Why It Fails**:
- Gets descriptions, not operators
- Returns what they discovered, not how they think
- Produces nouns (concepts) instead of verbs (moves)

**Fix**: Explicitly request operators with triggers and failure modes.

```markdown
# BAD PROMPT
"Summarize Sydney Brenner's scientific approach."

# GOOD PROMPT
"Extract reusable cognitive operators from this transcript.
For each operator:
- What triggers its use?
- What are the failure modes?
- Cite specific anchors (§n)."
```

### Accepting All Model Output

**Problem**: Including everything models extract without filtering.

**Why It Fails**:
- Models hallucinate connections
- Models project their training onto experts
- Unique extractions (1/3 models) are usually model bias

**Fix**: Only kernel-include items with 3/3 model agreement.

---

## Operator Anti-Patterns

### Operators as Personality Traits

**Problem**: Operators like "Be creative" or "Think critically."

**Why It Fails**:
- Not actionable
- No clear trigger
- Can't compose
- Everyone already "tries" to do this

**Fix**: Operators must be verbs with specific triggers and outputs.

```markdown
# BAD OPERATOR
"Be Creative"
- Think outside the box
- Generate novel ideas

# GOOD OPERATOR
"⊕ Cross-Domain Import"
Triggers:
- Field is stuck on same approaches
- Solution exists in adjacent domain
- Problem has structural analog elsewhere
Output: Candidate mechanism from foreign field with translation mapping
```

### Missing Failure Modes

**Problem**: Operators defined only by when they work.

**Why It Fails**:
- Real expertise includes knowing when NOT to apply
- Without failure modes, operators become cargo cult
- Can't debug when things go wrong

**Fix**: Every operator needs 2-4 specific failure modes.

### Jargon-Only Operators

**Problem**: Operators defined using the methodology's own jargon.

**Why It Fails**:
- Circular definitions
- Can't apply without already understanding
- Excludes newcomers

**Fix**: Define in plain English first, then add jargon as shorthand.

---

## Kernel Anti-Patterns

### No Markers

**Problem**: Kernel embedded in prose without extraction markers.

**Why It Fails**:
- Can't programmatically extract
- Can't version
- Can't embed in kickoff messages automatically

**Fix**: Always use HTML comment markers.

```markdown
<!-- TRIANGULATED_KERNEL_START -->
[kernel content]
<!-- TRIANGULATED_KERNEL_END -->
```

### Kernel Modification Per Role

**Problem**: Different roles get different versions of the kernel.

**Why It Fails**:
- Kernel is the invariant truth
- Modifications introduce inconsistency
- Agents can't coordinate on shared axioms

**Fix**: Kernel is identical everywhere. Role-specific content goes in role assignment section.

### Disputed Items in Kernel

**Problem**: Including items where only 2/3 models agree.

**Why It Fails**:
- The third model's disagreement might be correct
- Kernel should be high-confidence only
- Disputed items belong in appendix

**Fix**: Kernel = 3/3 agreement only. Document 2/3 items separately.

---

## Jargon Anti-Patterns

### Jargon Explaining Jargon

**Problem**: Definitions that use other methodology terms.

**Why It Fails**:
- Circular understanding required
- Newcomers can't bootstrap
- Progressive disclosure fails

**Fix**: `short` and `long` use plain English. Jargon only in `related`.

```markdown
# BAD
"Level-split: Apply the recode operator to separate levels before scale-checking."

# GOOD
"Level-split: Decompose a problem into distinct levels of organization.
Think of it like separating a building into floors—plumbing problems
on floor 3 don't require knowing every brick in the foundation."
```

### Missing Analogies

**Problem**: Technical definitions without intuitive comparisons.

**Why It Fails**:
- Non-experts can't grasp concepts
- Learning curve is steep
- Methodology feels academic, not practical

**Fix**: Every term needs an analogy from a familiar domain.

### Too Many Related Terms

**Problem**: 10+ related terms per entry.

**Why It Fails**:
- Overwhelming
- Loses the graph structure (everything connects to everything)
- Doesn't guide exploration

**Fix**: Maximum 4 related terms, chosen for discovery value.

---

## Kickoff Anti-Patterns

### No Role Assignment

**Problem**: All agents get identical kickoff messages.

**Why It Fails**:
- Agents don't know their focus
- Operator application is random
- Coordination breaks down

**Fix**: Each role gets specific operators and constraints.

### Missing Acknowledgement

**Problem**: Kickoffs sent without `ack_required: true`.

**Why It Fails**:
- Can't verify agents received and processed kickoff
- Coordination timing is uncertain
- Failed deliveries go unnoticed

**Fix**: All kickoffs require acknowledgement.

### Context Without Anchors

**Problem**: Research question and context without corpus citations.

**Why It Fails**:
- Agents can't verify claims
- Can't trace reasoning back to sources
- Hallucinations propagate

**Fix**: Context sections include `§n` anchors.

---

## Integration Anti-Patterns

### Building UI Before Kernel

**Problem**: Starting with user interface before methodology is stable.

**Why It Fails**:
- UI encodes assumptions that become constraints
- Kernel changes break UI
- Premature optimization of the wrong thing

**Fix**: Order: Corpus → Distillation → Kernel → Test kickoffs → Then UI.

### No Validation Scripts

**Problem**: Manual verification of corpus, operators, anchors.

**Why It Fails**:
- Errors accumulate
- Broken anchors aren't caught
- Operators without required fields slip through

**Fix**: Automated validation in CI/CD.

### Treating Operators as Fixed

**Problem**: Operators defined once and never revised.

**Why It Fails**:
- Real methodology evolves with application
- New failure modes are discovered
- Some operators prove more useful than others

**Fix**: Version the kernel. Track operator usage. Iterate.

---

## Summary Table

| Anti-Pattern | Category | Key Fix |
|--------------|----------|---------|
| Secondary sources | Corpus | Use only primary sources |
| No anchors | Corpus | Every quote gets §n |
| Single model | Distillation | Use 3+ models |
| Generic prompts | Distillation | Request operators explicitly |
| Personality traits | Operators | Make operators actionable verbs |
| No failure modes | Operators | 2-4 failure modes per operator |
| No markers | Kernel | HTML comment markers |
| Modified kernel | Kernel | Kernel is invariant |
| Jargon in definitions | Jargon | Plain English first |
| No analogies | Jargon | Every term needs analogy |
| No role assignment | Kickoff | Role-specific operators |
| UI before kernel | Integration | Methodology first, UI last |
