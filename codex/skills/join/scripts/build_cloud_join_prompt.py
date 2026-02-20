#!/usr/bin/env -S uv run python
"""Render the cloud join operator prompt from template with runtime parameters."""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build cloud join operator prompt text")
    parser.add_argument("--repo", required=True, help="owner/repo target")
    parser.add_argument("--patch-inbox", required=True, help="Inbox locator (path/URL/queue id)")
    parser.add_argument("--poll-seconds", type=int, default=60, help="Loop cadence in seconds")
    parser.add_argument(
        "--confidence-threshold",
        type=float,
        default=0.70,
        help="Routing confidence threshold before requiring seq disambiguation",
    )
    parser.add_argument(
        "--manifest-schema-path",
        default="codex/skills/join/assets/cloud-join-manifest.schema.json",
        help="Path reference embedded in rendered prompt",
    )
    parser.add_argument(
        "--max-cycles",
        type=int,
        default=0,
        help="Bounded run mode; 0 means continuous loop",
    )
    parser.add_argument("--output", help="Write prompt to file; default stdout")
    return parser.parse_args()


def render_prompt(template_text: str, args: argparse.Namespace) -> str:
    rendered = template_text
    rendered = rendered.replace("{{REPO}}", args.repo)
    rendered = rendered.replace("{{PATCH_INBOX}}", args.patch_inbox)
    rendered = rendered.replace("{{POLL_SECONDS}}", str(args.poll_seconds))
    rendered = rendered.replace("{{CONFIDENCE_THRESHOLD}}", f"{args.confidence_threshold:.2f}")
    rendered = rendered.replace("{{MANIFEST_SCHEMA_PATH}}", args.manifest_schema_path)
    if args.max_cycles > 0:
        rendered = rendered.replace("{{RUN_MODE}}", f"bounded ({args.max_cycles} cycle(s))")
        rendered = rendered.replace(
            "{{LOOP_DIRECTIVE}}",
            f"Run exactly {args.max_cycles} full cycle(s), emit final outcomes, then stop and exit.",
        )
    else:
        rendered = rendered.replace("{{RUN_MODE}}", "continuous")
        rendered = rendered.replace("{{LOOP_DIRECTIVE}}", "Continue looping until stopped externally.")
    return rendered


def main() -> int:
    args = parse_args()
    if args.poll_seconds <= 0:
        raise SystemExit("--poll-seconds must be positive")
    if not (0.0 <= args.confidence_threshold <= 1.0):
        raise SystemExit("--confidence-threshold must be between 0 and 1")
    if args.max_cycles < 0:
        raise SystemExit("--max-cycles must be 0 or greater")

    root = Path(__file__).resolve().parents[1]
    template_path = root / "assets" / "cloud-join-operator-prompt.md"
    template_text = template_path.read_text(encoding="utf-8")
    prompt = render_prompt(template_text, args)

    if args.output:
        Path(args.output).write_text(prompt, encoding="utf-8")
    else:
        print(prompt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
