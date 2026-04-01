# Corpus Architecture

The corpus is the foundation. Without quality primary sources, all downstream work is speculation.

## Directory Structure

```
corpus/
├── primary/
│   ├── transcripts/           # Interview transcripts, lectures
│   │   └── complete_transcript.md
│   ├── papers/                # Published works
│   │   └── key_paper_1.md
│   └── interviews/            # Recorded conversations
│       └── interview_notes.md
├── quote_bank/
│   └── quote_bank.md          # Anchored excerpts with §n refs
├── distillations/
│   ├── gpt_distillation.md    # GPT's synthesis
│   ├── opus_distillation.md   # Claude's synthesis
│   └── gemini_distillation.md # Gemini's synthesis
├── raw_responses/
│   ├── gpt_responses/         # Full model outputs
│   ├── opus_responses/
│   └── gemini_responses/
└── specs/
    ├── triangulated_kernel.md # THE kernel
    └── operator_library.md    # Formal operators
```

## Primary Source Quality Criteria

### Essential Characteristics

1. **First-hand** — Expert's own words, not summaries
2. **Comprehensive** — Covers methodology, not just results
3. **Diverse contexts** — Different talks, times, audiences
4. **Traceable** — Can cite specific sections

### Source Ranking

| Source Type | Quality | Why |
|-------------|---------|-----|
| Interview transcripts | A+ | Unfiltered thinking process |
| Lecture recordings | A | Shows pedagogy and priorities |
| Book chapters (solo) | A- | Edited but first-hand |
| Research papers | B+ | Methodology often implicit |
| Book chapters (edited) | B | May be compressed/altered |
| Secondary summaries | C | Avoid if possible |

## Quote Bank Format

```markdown
# Quote Bank: [Expert Name]

## §1 — [Topic/Theme]
> "Exact quote from primary source"
— Source: [Document Name], [location/timestamp]
Tags: operator-name, theme-tag

## §2 — [Topic/Theme]
> "Another exact quote"
— Source: [Document Name], [location/timestamp]
Tags: another-operator, methodology
```

### Quote Selection Criteria

Select quotes that:
1. **State axioms** — "You must always..."
2. **Demonstrate operators** — "The way I approach this is..."
3. **Warn against anti-patterns** — "Never..."
4. **Define terminology** — "What I mean by X is..."

### Anchoring Convention

Use `§n` for quote references:
- `§42` — Quote bank entry 42
- `§42-45` — Range of quotes
- `(§42)` — Inline citation
- `[inference]` — Not directly from corpus

## Document Format Guidelines

### Transcripts

```markdown
# Complete [Expert] Transcript

## Segment 1: [Title]
[Full text of segment]

## Segment 2: [Title]
[Full text]
...
```

- Number segments for easy reference
- Preserve speaker turns if dialogue
- Mark unclear audio as [inaudible]
- Include timestamps if available

### Papers

```markdown
# [Paper Title]
Authors: [names]
Source: [journal/conference]

## Abstract
[Full abstract]

## Methodology Section
[Full methodology — this is the gold]

## Key Quotes
[Extracted methodology statements]
```

Focus extraction on:
- Methodology descriptions
- Design rationale
- Explicit heuristics
- Failure analysis

## Corpus Validation

```python
# scripts/validate-corpus.py
def validate_corpus(path: str) -> bool:
    checks = [
        has_primary_sources(path),
        has_quote_bank(path),
        quotes_have_anchors(path),
        anchors_resolve(path),
        has_minimum_quotes(path, min=50),
    ]
    return all(checks)
```

### Minimum Requirements

| Component | Minimum | Ideal |
|-----------|---------|-------|
| Primary sources | 3 | 10+ |
| Quote bank entries | 50 | 200+ |
| Segments/sections | 20 | 100+ |
| Model distillations | 3 | 3 (GPT, Opus, Gemini) |

## Common Mistakes

| Mistake | Why It Fails | Fix |
|---------|--------------|-----|
| Using summaries | Loses nuance | Go to primary sources |
| No quote anchors | Can't verify claims | Add §n to every quote |
| Single source | Incomplete picture | Gather diverse contexts |
| Paraphrasing | Loses expert's voice | Use exact quotes |
| Missing timestamps | Can't verify | Include location/time |
