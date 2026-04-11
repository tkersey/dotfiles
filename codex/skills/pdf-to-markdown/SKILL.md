---
name: pdf-to-markdown
description: Convert local PDF files or folders of PDFs into Markdown files using the bundled converter in this skill. Use this when the task is PDF-to-Markdown conversion inside the current workspace. Do not use it for OCR-heavy scanned PDFs, image extraction, or unrelated PDF summarization.
---

# PDF to Markdown

Use this skill when the user wants one or more local PDF files converted into Markdown files in the current workspace.

This skill is fully self-contained. The conversion pipeline lives inside `scripts/convert_pdf_to_markdown.py`, and the PDF parser dependency is vendored under `scripts/vendor/python/pypdf`. The skill does not install packages, call npm, or fetch code at runtime.

The implementation is intentionally modeled on the structure-detection pipeline from `jzillmann/pdf-to-markdown`, but packaged as a repo-local Codex skill rather than a browser app. See `references/upstream-notes.md` for the design lineage and the main behavioral differences.

## Default behavior

- Prefer the bundled script: `python3 scripts/convert_pdf_to_markdown.py ...`
- Do not write a one-off converter when the bundled script already fits the task.
- Do not modify the bundled parser unless the user explicitly wants the skill extended.
- Before converting, verify that each input path exists.
- After converting, report the output path, any skips, and any failures.

## Supported inputs

The script accepts either:

- a single PDF file, or
- a directory containing PDFs.

Flags:

- `--input <path>` or `-i <path>`: required. Accepts a PDF file or directory.
- `--output <path>` or `-o <path>`: optional.
- `--recursive` or `-r`: recurse through nested folders when the input is a directory.
- `--overwrite` or `-f`: overwrite existing Markdown output files.
- `--help`

## Output behavior

For a single file input:

- If `--output` is omitted, write a sibling Markdown file next to the PDF using the same base name.
- If `--output` points to a directory, write `<basename>.md` inside that directory.
- If `--output` looks like a `.md` file path, write exactly there.

For a directory input:

- If `--output` is omitted, write to a sibling directory named `<input>_markdown`.
- Preserve the relative folder structure of the input directory beneath the output root.

## Recommended workflow

1. Resolve the user’s input and desired output locations.
2. Run the bundled script:
   `python3 scripts/convert_pdf_to_markdown.py --input <...> [--output <...>] [--recursive] [--overwrite]`
3. Read the script output and confirm where the Markdown landed.
4. If the user asked for cleanup after conversion, edit the generated Markdown rather than changing the converter unless they explicitly want parser work.
5. Keep generated files in the workspace unless the user asked for a temporary destination.

## What the converter tries to preserve

The bundled converter aims to recover document structure rather than only dumping plain text. It includes heuristics for:

- title and heading detection
- table-of-contents detection and TOC-based heading recovery
- repeated header/footer removal
- paragraph reflow across wrapped lines and some page breaks
- unordered and numbered list detection, including nesting by indentation
- indented code-block detection
- basic inline bold/italic preservation
- simple table recognition when the PDF exposes column gaps

## When not to use

- The PDF is scanned or image-only and needs OCR.
- The task needs figures or embedded images extracted from the PDF.
- The task is question-answering, summarization, or citation over a PDF without Markdown conversion.
- The user wants pixel-perfect layout fidelity.

## Known rough edges

- Multi-column layouts can still interleave content.
- Table extraction is heuristic and works best when the PDF exposes column spacing clearly.
- Encrypted PDFs may fail if they require features beyond the bundled parser.
- OCR is intentionally out of scope.

Read `references/upstream-notes.md` for the implementation rationale and `references/THIRD_PARTY_NOTICES.md` for vendored dependency notices.
