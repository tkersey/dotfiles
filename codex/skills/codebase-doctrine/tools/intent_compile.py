#!/usr/bin/env -S uv run --with pyyaml python
"""Compile DIG-v2 plus an optional bounded grill closure into deterministic CDI-v2."""

from __future__ import annotations

import argparse
from copy import deepcopy
from typing import Any

from common import dump_data, load_data, sha256_digest, unwrap
from intent_gate import expected_intent_id, validate_value


def compile_intent(
    gate_wrapper: dict[str, Any],
    grill_wrapper: dict[str, Any] | None = None,
) -> dict[str, Any]:
    kind, errors, _warnings = validate_value(gate_wrapper, kind="dig")
    if errors:
        raise ValueError("invalid DIG-v2: " + "; ".join(errors))
    gate = unwrap(gate_wrapper, "doctrine_intent_gate")
    grill_required = gate.get("grill_required") in {"yes", True}
    gate_id = gate["gate_id"]
    gate_digest = sha256_digest(gate)

    if not grill_required:
        if grill_wrapper is not None:
            raise ValueError("grill packet supplied for a direct DIG")
        seed = deepcopy(gate["direct_intent_seed"])
        source = {
            "kind": "direct",
            "intent_gate_id": gate_id,
            "intent_gate_digest": gate_digest,
            "grill_packet_digest": None,
        }
    else:
        if grill_wrapper is None:
            raise ValueError("DIG requires a grill closure packet")
        _kind, grill_errors, _warnings = validate_value(
            grill_wrapper,
            kind="grill",
            require_plan=True,
        )
        if grill_errors:
            raise ValueError("invalid grill closure: " + "; ".join(grill_errors))
        grill = unwrap(grill_wrapper, "grill_decision_packet")
        closure = grill["codebase_doctrine_closure"]
        if closure["source_gate_id"] != gate_id:
            raise ValueError("grill closure source_gate_id does not match DIG")
        expected_handoff_digest = sha256_digest(gate["grill_handoff"])
        if closure["source_handoff_digest"] != expected_handoff_digest:
            raise ValueError("grill closure source_handoff_digest does not match DIG handoff")
        gap_ids = {
            row["gap_id"]
            for row in gate.get("material_user_judgment_gaps", [])
            if isinstance(row, dict) and row.get("gap_id")
        }
        resolved = set(closure.get("resolved_gap_ids", []))
        deferred = set(closure.get("deferred_gap_ids", []))
        if deferred:
            raise ValueError("material grill gaps remain deferred")
        if resolved != gap_ids:
            missing = sorted(gap_ids - resolved)
            extra = sorted(resolved - gap_ids)
            raise ValueError(f"grill gap closure mismatch: missing={missing} extra={extra}")
        seed = deepcopy(closure["doctrine_projection"])
        source = {
            "kind": "grill",
            "intent_gate_id": gate_id,
            "intent_gate_digest": gate_digest,
            "grill_packet_digest": sha256_digest(grill),
        }

    body: dict[str, Any] = {
        "intent_version": "CDI-v2",
        "intent_id": "",
        "source": source,
        **seed,
        "doctrine_allowed": "yes",
    }
    body["intent_id"] = expected_intent_id(body)
    wrapper = {"codebase_doctrine_intent": body}
    _kind, errors, _warnings = validate_value(wrapper, kind="cdi")
    if errors:
        raise ValueError("compiled CDI-v2 failed validation: " + "; ".join(errors))
    return wrapper


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("gate")
    parser.add_argument("--grill")
    parser.add_argument("--format", choices=("yaml", "json"), default="yaml")
    parser.add_argument("--output")
    args = parser.parse_args()
    try:
        gate = load_data(args.gate)
        grill = load_data(args.grill) if args.grill else None
        compiled = compile_intent(gate, grill)
        rendered = dump_data(compiled, args.format)
        if args.output:
            from pathlib import Path

            Path(args.output).write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
        return 0
    except Exception as exc:
        print(dump_data({"intent_compile": {"verdict": "fail", "error": str(exc)}}, "json"), end="")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
