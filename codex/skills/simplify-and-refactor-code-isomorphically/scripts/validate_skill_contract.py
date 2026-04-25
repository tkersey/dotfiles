#!/usr/bin/env python3
"""Validate the simplify-and-refactor-code-isomorphically skill contract.

This is the high-level read-only validator. It catches broken references,
missing marker files, stale entry-point pathology-catalog wording, and script
syntax issues.
"""

from __future__ import annotations

import py_compile
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
SELF_TEST = ROOT / "SELF-TEST.md"
REFERENCES = ROOT / "references"
SCRIPTS = ROOT / "scripts"
ASSETS = ROOT / "assets"
SUBAGENTS = ROOT / "subagents"

REQUIRED_FILES = [
    "SKILL.md",
    "SELF-TEST.md",
    "CHANGELOG.md",
    "references/VALIDATION.md",
    "references/TRIANGULATED-KERNEL.md",
    "references/OPERATOR-CARDS.md",
    "references/CORPUS.md",
    "references/VIBE-CODED-PATHOLOGIES.md",
    "scripts/extract_kernel.sh",
    "scripts/validate_operators.py",
    "scripts/validate_corpus.py",
    "scripts/validate_skill_contract.py",
]


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def strip_markdown_code(text: str) -> str:
    """Remove code spans/blocks while preserving line numbers for link checks."""
    stripped_lines: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if re.match(r"^ {0,3}(```|~~~)", line):
            in_fence = not in_fence
            stripped_lines.append("")
            continue
        if in_fence:
            stripped_lines.append("")
        else:
            line = re.sub(
                r"\[([^\]\n]*`[^\]\n]*)\]\(",
                lambda match: f"[{match.group(1).replace('`', '')}](",
                line,
            )
            stripped_lines.append(re.sub(r"`[^`]*`", "", line))
    return "\n".join(stripped_lines)


def github_heading_slug(heading: str) -> str:
    """Approximate GitHub Markdown heading IDs for local anchor validation."""
    heading = heading.strip().lower()
    heading = re.sub(r"!\[([^\]\n]*)\]\([^)]+\)", r"\1", heading)
    heading = re.sub(r"\[([^\]\n]+)\]\([^)]+\)", r"\1", heading)
    heading = heading.replace("`", "").replace("*", "").replace("~", "")
    heading = re.sub(r"[^\w\s-]", "", heading)
    return re.sub(r"\s", "-", heading)


def markdown_anchors_from_text(text: str) -> set[str]:
    """Return heading anchors generated for Markdown text."""
    anchors: set[str] = set()
    counts: dict[str, int] = {}
    in_fence = False
    for line in text.splitlines():
        if re.match(r"^ {0,3}(```|~~~)", line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = re.match(r"^ {0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not match:
            continue
        slug = github_heading_slug(match.group(1))
        if not slug:
            continue
        count = counts.get(slug, 0)
        anchor = slug if count == 0 else f"{slug}-{count}"
        counts[slug] = count + 1
        anchors.add(anchor)
    return anchors


def markdown_anchors(path: Path) -> set[str]:
    """Return heading anchors generated for a Markdown file."""
    return markdown_anchors_from_text(read(path))


def extract_description(skill_text: str) -> str:
    match = re.search(r"^description:\s*>-\n(?P<body>(?:  .+\n)+)", skill_text, re.M)
    if not match:
        return ""
    lines = [line.strip() for line in match.group("body").splitlines()]
    return " ".join(lines).strip()


def validate_frontmatter(failures: list[str]) -> None:
    text = read(SKILL)
    if not text.startswith("---\n"):
        fail(f"{SKILL}: frontmatter must start at byte 0", failures)
    description = extract_description(text)
    if not description:
        fail(f"{SKILL}: missing description body", failures)
    if len(description) > 200:
        fail(f"{SKILL}: description too long ({len(description)} chars)", failures)
    if "Use when" not in description:
        fail(f"{SKILL}: description must include 'Use when'", failures)
    if re.search(r"\b(I can help|I'll help|Let me)\b", text):
        fail(f"{SKILL}: contains first-person helper phrasing", failures)


def validate_required_files(failures: list[str]) -> None:
    for rel in REQUIRED_FILES:
        path = ROOT / rel
        if not path.exists():
            fail(f"missing required file: {rel}", failures)


def validate_reference_tocs(failures: list[str]) -> None:
    for path in sorted(REFERENCES.glob("*.md")):
        first_40 = "\n".join(read(path).splitlines()[:40])
        if "## Contents" not in first_40:
            fail(f"{path}: missing ## Contents in first 40 lines", failures)


def validate_anchor_slugger(failures: list[str]) -> None:
    samples = {
        "M-R5 — `Box<dyn Trait>` for closed set → `enum`": "m-r5--boxdyn-trait-for-closed-set--enum",
        "M-R4 — sibling `fn parse_X` → generic `fn parse<T: FromStr>`": "m-r4--sibling-fn-parse_x--generic-fn-parset-fromstr",
        "Autopsy 2: the `BaseRepository<T>` over-abstraction": "autopsy-2-the-baserepositoryt-over-abstraction",
        "P1 over-defensive try/catch (see [VIBE-CODED-PATHOLOGIES.md §P1](VIBE-CODED-PATHOLOGIES.md#p1--over-defensive-trycatch))": "p1-over-defensive-trycatch-see-vibe-coded-pathologiesmd-p1",
    }
    for heading, expected in samples.items():
        actual = github_heading_slug(heading)
        if actual != expected:
            fail(f"anchor slug mismatch for {heading!r}: expected {expected}, got {actual}", failures)


def validate_markdown_anchor_parser(failures: list[str]) -> None:
    sample = """# Top

   ## Indented valid heading

    ## Indented code heading

   ```
   ## Fenced hidden heading
   ```

~~~
## Tilde fenced hidden heading
~~~

## Duplicate
## Duplicate
"""
    expected = {"top", "indented-valid-heading", "duplicate", "duplicate-1"}
    actual = markdown_anchors_from_text(sample)
    if actual != expected:
        fail(f"Markdown anchor parser regression: expected {sorted(expected)}, got {sorted(actual)}", failures)


def validate_links(failures: list[str]) -> None:
    markdown_files = [
        SKILL,
        SELF_TEST,
        ROOT / "CHANGELOG.md",
        *sorted(REFERENCES.glob("*.md")),
        *sorted(ASSETS.glob("*.md")),
        *sorted(SUBAGENTS.glob("*.md")),
    ]
    link_re = re.compile(r"(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)")
    external_prefixes = ("http://", "https://", "mailto:", "resource://", "app://", "plugin://")
    anchor_cache: dict[Path, set[str]] = {}

    for source in markdown_files:
        original_text = read(source)
        text = strip_markdown_code(original_text)
        for match in link_re.finditer(text):
            target = match.group(1).strip()
            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1]
            if target.startswith(external_prefixes):
                continue
            if "#" in target:
                path_part, fragment = target.split("#", 1)
            else:
                path_part, fragment = target, ""
            resolved = source.resolve() if not path_part else (source.parent / unquote(path_part)).resolve()
            if not resolved.exists():
                line_no = text.count("\n", 0, match.start()) + 1
                fail(f"{source}:{line_no}: broken local link: {target}", failures)
                continue
            if fragment and resolved.suffix.lower() == ".md":
                fragment = unquote(fragment).strip().lower()
                anchor_cache.setdefault(resolved, markdown_anchors(resolved))
                if fragment not in anchor_cache[resolved]:
                    line_no = text.count("\n", 0, match.start()) + 1
                    fail(f"{source}:{line_no}: broken local anchor: {target}", failures)


def validate_kernel(failures: list[str]) -> None:
    path = REFERENCES / "TRIANGULATED-KERNEL.md"
    text = read(path)
    if "<!-- KERNEL-START -->" not in text:
        fail(f"{path}: missing KERNEL-START marker", failures)
    if "<!-- KERNEL-END -->" not in text:
        fail(f"{path}: missing KERNEL-END marker", failures)


def validate_p40_consistency(failures: list[str]) -> None:
    skill_text = read(SKILL)
    script_text = read(SCRIPTS / "ai_slop_detector.sh")
    if "P1-P21" in skill_text or "P1-P21" in script_text:
        fail("stale P1-P21 wording remains in SKILL.md or ai_slop_detector.sh", failures)
    expected_markers = {
        SKILL: ("P1-P40",),
        SCRIPTS / "ai_slop_detector.sh": ("P1-P40", "P22", "P40"),
        REFERENCES / "VIBE-CODED-PATHOLOGIES.md": ("P22", "P40"),
    }
    for path, markers in expected_markers.items():
        text = read(path)
        for marker in markers:
            if marker not in text:
                fail(f"{path}: missing pathology-catalog marker {marker}", failures)


def validate_scripts(failures: list[str]) -> None:
    bash = shutil.which("bash")
    for path in sorted(SCRIPTS.iterdir()):
        if not path.is_file():
            continue
        first = path.read_text(encoding="utf-8", errors="replace").splitlines()[:1]
        if not first or not first[0].startswith("#!"):
            fail(f"{path}: missing shebang", failures)
        if path.stat().st_mode & 0o111 == 0:
            fail(f"{path}: not executable", failures)
        if path.suffix == ".sh":
            if bash is None:
                fail("bash not found; cannot syntax-check shell scripts", failures)
                continue
            result = subprocess.run([bash, "-n", str(path)], capture_output=True, text=True)
            if result.returncode != 0:
                fail(f"{path}: bash -n failed: {result.stderr.strip()}", failures)
        elif path.suffix == ".py":
            try:
                py_compile.compile(str(path), doraise=True)
            except py_compile.PyCompileError as exc:
                fail(f"{path}: py_compile failed: {exc}", failures)


def run_child_validators(failures: list[str]) -> None:
    for script in ("validate_operators.py", "validate_corpus.py"):
        path = SCRIPTS / script
        result = subprocess.run([sys.executable, str(path)], capture_output=True, text=True)
        if result.returncode != 0:
            fail(f"{path}: failed\n{result.stdout}{result.stderr}", failures)


def main() -> int:
    failures: list[str] = []
    validate_required_files(failures)
    validate_frontmatter(failures)
    validate_reference_tocs(failures)
    validate_anchor_slugger(failures)
    validate_markdown_anchor_parser(failures)
    validate_links(failures)
    validate_kernel(failures)
    validate_p40_consistency(failures)
    validate_scripts(failures)
    run_child_validators(failures)

    if failures:
        print("skill contract validation: FAIL")
        for item in failures:
            print(f"- {item}")
        return 1

    print("skill contract validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
