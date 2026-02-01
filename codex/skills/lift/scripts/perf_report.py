#!/usr/bin/env python3
"""
Generate a performance report template in Markdown.
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

TEMPLATE = """# Performance Report: {title}

Date: {report_date}
Owner: {owner}
System: {system}

## 1. Performance Contract

- Metric:
- Target:
- Percentile:
- Dataset:
- Environment:
- Constraints:

## 2. Baseline

- Measurement method:
- Sample size:
- Results (p50/p95/p99):
- Notes:

## 3. Bottleneck Evidence

- Profile or trace summary:
- Hot paths:
- Bound classification (CPU/memory/I/O/lock/tail):

## 4. Hypothesis

- Cause:
- Expected impact:
- Risks:

## 5. Experiment Plan

- Change description:
- Control variables:
- Success criteria:

## 6. Results

- Variant measurements:
- Delta vs baseline:
- Confidence:

## 7. Trade-offs

- Correctness:
- Maintainability:
- Cost or resource impact:

## 8. Regression Guard

- Benchmark or budget:
- Alert or threshold:

## 9. Next Steps

- Follow-up experiments:
- Rollout plan:
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a performance report template.")
    parser.add_argument("--title", default="Untitled", help="Report title")
    parser.add_argument("--owner", default="", help="Owner or team")
    parser.add_argument("--system", default="", help="System or component")
    parser.add_argument("--output", default="perf-report.md", help="Output path")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    content = TEMPLATE.format(
        title=args.title,
        report_date=date.today().isoformat(),
        owner=args.owner or "",
        system=args.system or "",
    )

    output_path = Path(args.output)
    output_path.write_text(content)
    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
