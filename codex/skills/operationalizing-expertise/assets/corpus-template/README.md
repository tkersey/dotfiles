# Corpus Template

This is a template corpus structure for operationalizing expertise.

## Directory Structure

```
corpus/
├── README.md                 # This file
├── primary_sources/          # Original expert materials
│   └── [expert]_transcript.md
├── quote_bank/               # Anchored quotes
│   └── quotes_[topic].md
├── distillations/            # Model analyses
│   ├── gpt/
│   │   └── batch_1.md
│   ├── claude/
│   │   └── batch_1.md
│   └── gemini/
│       └── batch_1.md
└── specs/                    # Synthesized outputs
    ├── triangulated_kernel.md
    ├── operator_library.md
    └── role_prompts.md
```

## Setup Steps

1. **Add Primary Sources** → `primary_sources/`
   - Transcripts, interviews, papers, lectures
   - Mark segments with `## Segment N` or `### §N`

2. **Extract Quote Bank** → `quote_bank/`
   - Pull key quotes with §n anchors
   - Organize by topic or theme

3. **Run Distillations** → `distillations/`
   - Use metaprompt from skill docs
   - Process with GPT, Claude, Gemini
   - Save raw responses

4. **Triangulate** → `specs/triangulated_kernel.md`
   - Use triangulation prompt
   - Only include 3/3 consensus items
   - Use HTML markers

5. **Build Operator Library** → `specs/operator_library.md`
   - Use operator template
   - Validate with scripts

## Validation

```bash
# Validate corpus structure
python scripts/validate-corpus.py /path/to/corpus/

# Extract and validate kernel
python scripts/extract-kernel.py /path/to/corpus/specs/ --validate

# Validate operator library
python scripts/validate-operators.py /path/to/corpus/specs/operator_library.md
```
