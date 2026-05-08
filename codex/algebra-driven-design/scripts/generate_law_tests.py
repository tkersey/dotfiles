#!/usr/bin/env python3
"""Generate law-test skeletons for ADD analyses.

Input JSON shape:
{
  "language": "python-hypothesis",
  "carrier": "Plan",
  "strategy": "plans()",
  "observe": "observe",
  "operations": [
    {
      "name": "then",
      "function": "compose_plan",
      "identity": "empty_plan()",
      "laws": ["associativity", "left_identity", "right_identity"]
    },
    {
      "name": "mergeEvidence",
      "function": "merge_evidence",
      "identity": "empty_evidence()",
      "laws": ["associativity", "commutativity", "idempotency"]
    }
  ]
}

Usage:
  python scripts/generate_law_tests.py --input laws.json --output test_laws.py
  python scripts/generate_law_tests.py --input laws.json --language typescript-fast-check
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any

LAW_ALIASES = {
    "assoc": "associativity",
    "associative": "associativity",
    "associativity": "associativity",
    "identity": "identity",
    "left_identity": "left_identity",
    "right_identity": "right_identity",
    "comm": "commutativity",
    "commutativity": "commutativity",
    "commutative": "commutativity",
    "idem": "idempotency",
    "idempotent": "idempotency",
    "idempotency": "idempotency",
    "annihilator": "annihilator",
    "absorbing": "annihilator",
}


def safe_name(text: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9_]+", "_", text.strip())
    text = re.sub(r"_+", "_", text).strip("_").lower()
    return text or "operation"


def normalize_laws(raw: Any) -> set[str]:
    if not raw:
        return set()
    if isinstance(raw, str):
        raw = [raw]
    laws: set[str] = set()
    for law in raw:
        key = str(law).strip().lower().replace("-", "_").replace(" ", "_")
        value = LAW_ALIASES.get(key, key)
        if value == "identity":
            laws.add("left_identity")
            laws.add("right_identity")
        else:
            laws.add(value)
    return laws


def py_expr_observe(observe: str, expr: str) -> str:
    if observe in {"", "identity", "None", None}:  # type: ignore[comparison-overlap]
        return expr
    return f"{observe}({expr})"


def generate_python(data: dict[str, Any]) -> str:
    strategy = data.get("strategy") or data.get("constructor_strategy") or "values()"
    observe = data.get("observe", "observe")
    operations = data.get("operations", [])

    lines: list[str] = [
        "# Generated ADD law-test skeletons.",
        "# Fill in imports, strategies, operation functions, and observation function.",
        "# Requires: pytest + hypothesis if run as-is.",
        "from hypothesis import given",
        "",
        "# TODO: import your domain operations and strategies.",
        "# from your_project.domain import observe, values",
        "",
    ]

    for op in operations:
        if not isinstance(op, dict):
            continue
        fname = op.get("function") or op.get("name") or "combine"
        op_name = safe_name(op.get("name") or fname)
        identity = op.get("identity")
        annihilator = op.get("annihilator") or op.get("zero") or op.get("absorbing")
        laws = normalize_laws(op.get("laws", []))

        if "associativity" in laws:
            left = py_expr_observe(observe, f"{fname}({fname}(a, b), c)")
            right = py_expr_observe(observe, f"{fname}(a, {fname}(b, c))")
            lines += [
                f"@given(a={strategy}, b={strategy}, c={strategy})",
                f"def test_{op_name}_associative(a, b, c):",
                f"    assert {left} == {right}",
                "",
            ]

        if "commutativity" in laws:
            left = py_expr_observe(observe, f"{fname}(a, b)")
            right = py_expr_observe(observe, f"{fname}(b, a)")
            lines += [
                f"@given(a={strategy}, b={strategy})",
                f"def test_{op_name}_commutative(a, b):",
                f"    assert {left} == {right}",
                "",
            ]

        if identity and "left_identity" in laws:
            left = py_expr_observe(observe, f"{fname}({identity}, a)")
            right = py_expr_observe(observe, "a")
            lines += [
                f"@given(a={strategy})",
                f"def test_{op_name}_left_identity(a):",
                f"    assert {left} == {right}",
                "",
            ]

        if identity and "right_identity" in laws:
            left = py_expr_observe(observe, f"{fname}(a, {identity})")
            right = py_expr_observe(observe, "a")
            lines += [
                f"@given(a={strategy})",
                f"def test_{op_name}_right_identity(a):",
                f"    assert {left} == {right}",
                "",
            ]

        if "idempotency" in laws:
            # For binary operations, idempotency is op(a,a)=a. For unary functions, users should edit.
            arity = int(op.get("arity", 2) or 2)
            if arity == 1:
                left = py_expr_observe(observe, f"{fname}({fname}(a))")
                right = py_expr_observe(observe, f"{fname}(a)")
                body = f"    assert {left} == {right}"
            else:
                left = py_expr_observe(observe, f"{fname}(a, a)")
                right = py_expr_observe(observe, "a")
                body = f"    assert {left} == {right}"
            lines += [
                f"@given(a={strategy})",
                f"def test_{op_name}_idempotent(a):",
                body,
                "",
            ]

        if annihilator and "annihilator" in laws:
            left = py_expr_observe(observe, f"{fname}({annihilator}, a)")
            right = py_expr_observe(observe, str(annihilator))
            lines += [
                f"@given(a={strategy})",
                f"def test_{op_name}_left_annihilator(a):",
                f"    assert {left} == {right}",
                "",
            ]
            left = py_expr_observe(observe, f"{fname}(a, {annihilator})")
            lines += [
                f"@given(a={strategy})",
                f"def test_{op_name}_right_annihilator(a):",
                f"    assert {left} == {right}",
                "",
            ]

        unknown = laws - {"associativity", "commutativity", "left_identity", "right_identity", "idempotency", "annihilator"}
        for law in sorted(unknown):
            lines += [
                f"def test_{op_name}_{safe_name(law)}():",
                f"    # TODO: implement custom law '{law}' for {fname}.",
                "    raise NotImplementedError",
                "",
            ]

    return "\n".join(lines).rstrip() + "\n"


def ts_observe(observe: str, expr: str) -> str:
    if observe in {"", "identity", "None", None}:  # type: ignore[comparison-overlap]
        return expr
    return f"{observe}({expr})"


def generate_typescript(data: dict[str, Any]) -> str:
    arb = data.get("arbitrary") or data.get("strategy") or "valueArb"
    observe = data.get("observe", "observe")
    operations = data.get("operations", [])

    lines: list[str] = [
        "// Generated ADD law-test skeletons.",
        "// Fill in imports, arbitraries, operation functions, and observation function.",
        "import fc from \"fast-check\";",
        "",
    ]

    for op in operations:
        if not isinstance(op, dict):
            continue
        fname = op.get("function") or op.get("name") or "combine"
        op_name = safe_name(op.get("name") or fname)
        identity = op.get("identity")
        annihilator = op.get("annihilator") or op.get("zero") or op.get("absorbing")
        laws = normalize_laws(op.get("laws", []))

        def test_block(name: str, arbs: str, body: str) -> None:
            lines.extend([
                f"test(\"{op_name} {name}\", () => {{",
                "  fc.assert(",
                f"    fc.property({arbs}, ({', '.join(['a','b','c'][:arbs.count(',')+1])}) => {{",
                f"      {body}",
                "    })",
                "  );",
                "});",
                "",
            ])

        if "associativity" in laws:
            left = ts_observe(observe, f"{fname}({fname}(a, b), c)")
            right = ts_observe(observe, f"{fname}(a, {fname}(b, c))")
            test_block("associative", f"{arb}, {arb}, {arb}", f"expect({left}).toEqual({right});")

        if "commutativity" in laws:
            left = ts_observe(observe, f"{fname}(a, b)")
            right = ts_observe(observe, f"{fname}(b, a)")
            lines.extend([
                f"test(\"{op_name} commutative\", () => {{",
                "  fc.assert(",
                f"    fc.property({arb}, {arb}, (a, b) => {{",
                f"      expect({left}).toEqual({right});",
                "    })",
                "  );",
                "});",
                "",
            ])

        if identity and "left_identity" in laws:
            left = ts_observe(observe, f"{fname}({identity}, a)")
            right = ts_observe(observe, "a")
            lines.extend([
                f"test(\"{op_name} left identity\", () => {{",
                "  fc.assert(",
                f"    fc.property({arb}, (a) => {{",
                f"      expect({left}).toEqual({right});",
                "    })",
                "  );",
                "});",
                "",
            ])

        if identity and "right_identity" in laws:
            left = ts_observe(observe, f"{fname}(a, {identity})")
            right = ts_observe(observe, "a")
            lines.extend([
                f"test(\"{op_name} right identity\", () => {{",
                "  fc.assert(",
                f"    fc.property({arb}, (a) => {{",
                f"      expect({left}).toEqual({right});",
                "    })",
                "  );",
                "});",
                "",
            ])

        if "idempotency" in laws:
            arity = int(op.get("arity", 2) or 2)
            if arity == 1:
                left = ts_observe(observe, f"{fname}({fname}(a))")
                right = ts_observe(observe, f"{fname}(a)")
            else:
                left = ts_observe(observe, f"{fname}(a, a)")
                right = ts_observe(observe, "a")
            lines.extend([
                f"test(\"{op_name} idempotent\", () => {{",
                "  fc.assert(",
                f"    fc.property({arb}, (a) => {{",
                f"      expect({left}).toEqual({right});",
                "    })",
                "  );",
                "});",
                "",
            ])

        if annihilator and "annihilator" in laws:
            left = ts_observe(observe, f"{fname}({annihilator}, a)")
            right = ts_observe(observe, str(annihilator))
            lines.extend([
                f"test(\"{op_name} left annihilator\", () => {{",
                "  fc.assert(",
                f"    fc.property({arb}, (a) => {{",
                f"      expect({left}).toEqual({right});",
                "    })",
                "  );",
                "});",
                "",
            ])
            left = ts_observe(observe, f"{fname}(a, {annihilator})")
            lines.extend([
                f"test(\"{op_name} right annihilator\", () => {{",
                "  fc.assert(",
                f"    fc.property({arb}, (a) => {{",
                f"      expect({left}).toEqual({right});",
                "    })",
                "  );",
                "});",
                "",
            ])

    return "\n".join(lines).rstrip() + "\n"


def load_input(path: str | None) -> dict[str, Any]:
    if path:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return json.load(sys.stdin)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate ADD law-test skeletons.")
    parser.add_argument("--input", "-i", help="Input JSON path. Reads stdin if omitted.")
    parser.add_argument("--output", "-o", help="Output file path. Writes stdout if omitted.")
    parser.add_argument("--language", "-l", choices=["python-hypothesis", "typescript-fast-check"], help="Override input language.")
    args = parser.parse_args()

    try:
        data = load_input(args.input)
    except Exception as exc:  # noqa: BLE001
        print(f"error: failed to read input JSON: {exc}", file=sys.stderr)
        return 2

    language = args.language or data.get("language", "python-hypothesis")
    if language == "python-hypothesis":
        output = generate_python(data)
    elif language == "typescript-fast-check":
        output = generate_typescript(data)
    else:
        print(f"error: unsupported language {language!r}", file=sys.stderr)
        return 2

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
