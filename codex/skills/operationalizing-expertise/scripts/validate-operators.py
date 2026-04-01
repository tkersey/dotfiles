#!/usr/bin/env python3
"""
Validate operator library completeness.

Usage:
    python validate-operators.py /path/to/operator_library.md

Checks each operator has:
    - Symbol
    - Name
    - Definition (one sentence)
    - Triggers (3+)
    - Failure modes (2+)
    - Prompt module
    - Quote anchors
"""

import sys
import re
from pathlib import Path
from typing import List, Tuple
from dataclasses import dataclass, field


@dataclass
class Operator:
    """Parsed operator from library."""
    symbol: str = ""
    name: str = ""
    definition: str = ""
    triggers: List[str] = field(default_factory=list)
    failure_modes: List[str] = field(default_factory=list)
    prompt_module: str = ""
    anchors: List[str] = field(default_factory=list)
    canonical_tag: str = ""
    line_number: int = 0


def parse_operators(content: str) -> List[Operator]:
    """Parse operators from markdown content."""
    operators = []

    # Split by operator headers (### symbol name)
    operator_pattern = re.compile(
        r'^###\s+([^\s]+)\s+(.+)$',
        re.MULTILINE
    )

    matches = list(operator_pattern.finditer(content))

    for i, match in enumerate(matches):
        op = Operator()
        op.symbol = match.group(1)
        op.name = match.group(2).strip()
        op.line_number = content[:match.start()].count('\n') + 1

        # Get content until next operator or end
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        section = content[start:end]

        # Parse definition
        def_match = re.search(r'\*\*Definition\*\*:\s*(.+?)(?:\n\n|\n\*\*)', section, re.DOTALL)
        if def_match:
            op.definition = def_match.group(1).strip()

        # Parse triggers
        triggers_match = re.search(
            r'\*\*(?:When-to-Use\s+)?Triggers?\*\*:\s*\n((?:\s*[-•]\s*.+\n?)+)',
            section
        )
        if triggers_match:
            op.triggers = re.findall(r'[-•]\s*(.+)', triggers_match.group(1))

        # Parse failure modes
        failure_match = re.search(
            r'\*\*Failure\s+Modes?\*\*:\s*\n((?:\s*[-•]\s*.+\n?)+)',
            section
        )
        if failure_match:
            op.failure_modes = re.findall(r'[-•]\s*(.+)', failure_match.group(1))

        # Parse prompt module
        prompt_match = re.search(r'```(?:text)?\n(\[OPERATOR:.+?)```', section, re.DOTALL)
        if prompt_match:
            op.prompt_module = prompt_match.group(1).strip()

        # Parse anchors
        anchor_match = re.search(r'\*\*(?:Quote[- ]?[Bb]ank\s+)?[Aa]nchors?\*\*:\s*(.+)', section)
        if anchor_match:
            op.anchors = re.findall(r'§\d+(?:-§?\d+)?', anchor_match.group(1))

        # Parse canonical tag
        tag_match = re.search(r'\*\*Canonical\s+tag\*\*:\s*(\S+)', section)
        if tag_match:
            op.canonical_tag = tag_match.group(1)

        operators.append(op)

    return operators


def validate_operator(op: Operator) -> Tuple[List[str], List[str]]:
    """Validate a single operator."""
    errors = []
    warnings = []

    prefix = f"Line {op.line_number} ({op.symbol} {op.name})"

    # Required: symbol
    if not op.symbol:
        errors.append(f"{prefix}: Missing symbol")
    elif len(op.symbol) > 3:
        warnings.append(f"{prefix}: Symbol '{op.symbol}' seems too long")

    # Required: name
    if not op.name:
        errors.append(f"{prefix}: Missing name")

    # Required: definition
    if not op.definition:
        errors.append(f"{prefix}: Missing definition")
    elif len(op.definition.split('.')) > 2:
        warnings.append(f"{prefix}: Definition should be one sentence")

    # Required: triggers (3+)
    if len(op.triggers) < 3:
        errors.append(f"{prefix}: Need at least 3 triggers, found {len(op.triggers)}")

    # Required: failure modes (2+)
    if len(op.failure_modes) < 2:
        errors.append(f"{prefix}: Need at least 2 failure modes, found {len(op.failure_modes)}")

    # Required: prompt module
    if not op.prompt_module:
        warnings.append(f"{prefix}: Missing prompt module (recommended)")

    # Required: anchors
    if not op.anchors:
        warnings.append(f"{prefix}: No quote anchors found")

    return errors, warnings


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate-operators.py /path/to/operator_library.md")
        sys.exit(1)

    file_path = Path(sys.argv[1])

    if not file_path.exists():
        print(f"Error: {file_path} does not exist")
        sys.exit(1)

    print(f"Validating operator library: {file_path}\n")

    content = file_path.read_text()
    operators = parse_operators(content)

    print(f"Found {len(operators)} operators\n")

    all_errors = []
    all_warnings = []

    for op in operators:
        errors, warnings = validate_operator(op)
        all_errors.extend(errors)
        all_warnings.extend(warnings)

    # Summary statistics
    print("Operator Summary:")
    print("-" * 40)
    for op in operators:
        print(f"  {op.symbol} {op.name}")
        print(f"    Triggers: {len(op.triggers)}, Failures: {len(op.failure_modes)}, Anchors: {len(op.anchors)}")

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
