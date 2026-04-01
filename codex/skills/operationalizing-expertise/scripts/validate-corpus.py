#!/usr/bin/env python3
"""
Validate corpus structure and quote bank anchors.

Usage:
    python validate-corpus.py /path/to/corpus/

Checks:
    - Required directories exist
    - Primary sources are present
    - Quote bank entries have valid anchors
    - Anchors reference existing corpus segments
"""

import sys
import re
from pathlib import Path
from typing import List, Dict, Tuple

# Required directories in a valid corpus
REQUIRED_DIRS = [
    "primary_sources",
    "quote_bank",
]

# Optional but expected directories
OPTIONAL_DIRS = [
    "distillations",
    "distillations/gpt",
    "distillations/claude",
    "distillations/gemini",
    "specs",
]

# Anchor pattern: §n or §n-m
ANCHOR_PATTERN = re.compile(r'§(\d+)(?:-§?(\d+))?')


def find_corpus_segments(corpus_path: Path) -> Dict[int, str]:
    """Find all segment numbers in primary sources."""
    segments = {}

    for source_file in corpus_path.glob("primary_sources/**/*.md"):
        content = source_file.read_text()
        # Look for segment markers like "## Segment 45" or "### §45"
        for match in re.finditer(r'(?:Segment|§)\s*(\d+)', content):
            seg_num = int(match.group(1))
            segments[seg_num] = str(source_file)

    return segments


def validate_quote_bank(corpus_path: Path, valid_segments: Dict[int, str]) -> List[str]:
    """Validate quote bank entries have valid anchors."""
    errors = []

    quote_bank_path = corpus_path / "quote_bank"
    if not quote_bank_path.exists():
        return ["quote_bank directory not found"]

    for quote_file in quote_bank_path.glob("**/*.md"):
        content = quote_file.read_text()

        for line_num, line in enumerate(content.split('\n'), 1):
            for match in ANCHOR_PATTERN.finditer(line):
                start = int(match.group(1))
                end = int(match.group(2)) if match.group(2) else start

                for seg in range(start, end + 1):
                    if seg not in valid_segments:
                        errors.append(
                            f"{quote_file}:{line_num}: Invalid anchor §{seg} - "
                            f"no matching corpus segment"
                        )

    return errors


def validate_structure(corpus_path: Path) -> Tuple[List[str], List[str]]:
    """Validate corpus directory structure."""
    errors = []
    warnings = []

    for required_dir in REQUIRED_DIRS:
        dir_path = corpus_path / required_dir
        if not dir_path.exists():
            errors.append(f"Missing required directory: {required_dir}")
        elif not any(dir_path.iterdir()):
            warnings.append(f"Empty directory: {required_dir}")

    for optional_dir in OPTIONAL_DIRS:
        dir_path = corpus_path / optional_dir
        if not dir_path.exists():
            warnings.append(f"Missing optional directory: {optional_dir}")

    return errors, warnings


def validate_primary_sources(corpus_path: Path) -> List[str]:
    """Validate primary sources exist and have content."""
    errors = []

    primary_path = corpus_path / "primary_sources"
    if not primary_path.exists():
        return ["primary_sources directory not found"]

    md_files = list(primary_path.glob("**/*.md"))
    if not md_files:
        errors.append("No markdown files in primary_sources")
        return errors

    total_words = 0
    for md_file in md_files:
        content = md_file.read_text()
        words = len(content.split())
        total_words += words

        if words < 100:
            errors.append(f"{md_file}: Only {words} words - seems too short")

    if total_words < 5000:
        errors.append(f"Total corpus is only {total_words} words - need more content")

    return errors


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate-corpus.py /path/to/corpus/")
        sys.exit(1)

    corpus_path = Path(sys.argv[1])

    if not corpus_path.exists():
        print(f"Error: {corpus_path} does not exist")
        sys.exit(1)

    print(f"Validating corpus at: {corpus_path}\n")

    all_errors = []
    all_warnings = []

    # Validate structure
    print("Checking directory structure...")
    errors, warnings = validate_structure(corpus_path)
    all_errors.extend(errors)
    all_warnings.extend(warnings)

    # Validate primary sources
    print("Checking primary sources...")
    errors = validate_primary_sources(corpus_path)
    all_errors.extend(errors)

    # Find valid segments
    print("Finding corpus segments...")
    segments = find_corpus_segments(corpus_path)
    print(f"  Found {len(segments)} segments")

    # Validate quote bank anchors
    print("Validating quote bank anchors...")
    errors = validate_quote_bank(corpus_path, segments)
    all_errors.extend(errors)

    # Report results
    print("\n" + "=" * 60)

    if all_warnings:
        print(f"\nWarnings ({len(all_warnings)}):")
        for warning in all_warnings:
            print(f"  - {warning}")

    if all_errors:
        print(f"\nErrors ({len(all_errors)}):")
        for error in all_errors:
            print(f"  - {error}")
        print("\nValidation FAILED")
        sys.exit(1)
    else:
        print("\nValidation PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
