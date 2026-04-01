#!/usr/bin/env python3
"""
Extract triangulated kernel from spec files.

Usage:
    python extract-kernel.py /path/to/specs/
    python extract-kernel.py /path/to/specs/ --output kernel.md
    python extract-kernel.py /path/to/specs/ --validate

Finds and extracts content between kernel markers:
    <!-- TRIANGULATED_KERNEL_START -->
    ...content...
    <!-- TRIANGULATED_KERNEL_END -->
"""

import sys
import re
import argparse
from pathlib import Path
from typing import Optional, List, Tuple

# Kernel marker patterns
KERNEL_START = re.compile(r'<!--\s*(\w+_)?TRIANGULATED_KERNEL_START(\s+v[\d.]+)?\s*-->')
KERNEL_END = re.compile(r'<!--\s*(\w+_)?TRIANGULATED_KERNEL_END(\s+v[\d.]+)?\s*-->')

# Required kernel sections
REQUIRED_SECTIONS = [
    "Axiom",
    "Operator",
]

OPTIONAL_SECTIONS = [
    "Anti-Pattern",
    "Output Contract",
    "Objective",
]


def find_kernel_in_file(file_path: Path) -> Optional[Tuple[str, str, str]]:
    """
    Find kernel in a file.

    Returns:
        Tuple of (full_marker_content, kernel_content, version) or None
    """
    content = file_path.read_text()

    start_match = KERNEL_START.search(content)
    if not start_match:
        return None

    end_match = KERNEL_END.search(content, start_match.end())
    if not end_match:
        print(f"Warning: Found start marker but no end marker in {file_path}")
        return None

    full_content = content[start_match.start():end_match.end()]
    kernel_content = content[start_match.end():end_match.start()].strip()
    version = start_match.group(2).strip() if start_match.group(2) else "v0.1"

    return (full_content, kernel_content, version)


def find_kernel(specs_path: Path) -> Optional[Tuple[Path, str, str, str]]:
    """
    Find kernel across all spec files.

    Returns:
        Tuple of (file_path, full_content, kernel_content, version) or None
    """
    for spec_file in specs_path.glob("**/*.md"):
        result = find_kernel_in_file(spec_file)
        if result:
            full_content, kernel_content, version = result
            return (spec_file, full_content, kernel_content, version)

    return None


def validate_kernel(kernel_content: str) -> Tuple[List[str], List[str]]:
    """Validate kernel has required sections."""
    errors = []
    warnings = []

    for section in REQUIRED_SECTIONS:
        if section.lower() not in kernel_content.lower():
            errors.append(f"Missing required section: {section}")

    for section in OPTIONAL_SECTIONS:
        if section.lower() not in kernel_content.lower():
            warnings.append(f"Missing optional section: {section}")

    # Check for anchor references
    anchor_count = len(re.findall(r'§\d+', kernel_content))
    if anchor_count < 3:
        warnings.append(f"Only {anchor_count} anchor references - consider adding more")

    # Check for operator symbols
    operator_pattern = re.compile(r'[⊘⊕⊞✂⌂†◊∿↑🔧⚡👁🎭≡𝓛ΔE⟂∑]')
    operators = operator_pattern.findall(kernel_content)
    if not operators:
        warnings.append("No operator symbols found")
    else:
        print(f"  Found {len(operators)} operator symbols")

    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description="Extract triangulated kernel")
    parser.add_argument("specs_path", help="Path to specs directory")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--validate", "-v", action="store_true",
                        help="Validate kernel structure")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Suppress informational output")

    args = parser.parse_args()

    specs_path = Path(args.specs_path)

    if not specs_path.exists():
        print(f"Error: {specs_path} does not exist")
        sys.exit(1)

    result = find_kernel(specs_path)

    if not result:
        print("Error: No triangulated kernel found")
        print("Looking for markers like:")
        print("  <!-- TRIANGULATED_KERNEL_START -->")
        print("  <!-- TRIANGULATED_KERNEL_END -->")
        sys.exit(1)

    file_path, full_content, kernel_content, version = result

    if not args.quiet:
        print(f"Found kernel in: {file_path}")
        print(f"Version: {version}")
        print(f"Content length: {len(kernel_content)} chars")

    if args.validate:
        print("\nValidating kernel structure...")
        errors, warnings = validate_kernel(kernel_content)

        if warnings:
            print(f"\nWarnings ({len(warnings)}):")
            for warning in warnings:
                print(f"  - {warning}")

        if errors:
            print(f"\nErrors ({len(errors)}):")
            for error in errors:
                print(f"  - {error}")
            print("\nValidation FAILED")
            sys.exit(1)
        else:
            print("\nValidation PASSED")

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(full_content)
        if not args.quiet:
            print(f"\nKernel written to: {output_path}")
    elif not args.validate:
        # Print kernel content to stdout
        print("\n" + "=" * 60)
        print(full_content)
        print("=" * 60)


if __name__ == "__main__":
    main()
