#!/usr/bin/env python3
"""Generate a ranked design-mindset from Codex sessions.

Reads ~/.codex/sessions/**/*.jsonl (by default) and produces a top-N list of
software design heuristics derived from repeated assistant patterns, weighted by
user approval.

Output is intentionally "list only": no scores, no quotes, no file paths.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional


@dataclass(frozen=True)
class Heuristic:
    key: str
    bullet: str
    pattern: re.Pattern[str]


def _strip_leading_echo(text: str) -> str:
    """Remove the leading 'Echo:' line (and one following blank) if present."""
    lines = text.splitlines()
    if not lines:
        return text

    if lines[0].startswith("Echo:"):
        lines = lines[1:]
        if lines and lines[0].strip() == "":
            lines = lines[1:]
        return "\n".join(lines)

    return text


def _iter_session_files(sessions_root: Path) -> Iterable[Path]:
    if not sessions_root.exists():
        return []
    return sorted(sessions_root.rglob("*.jsonl"))


def _message_text(payload: dict) -> Optional[str]:
    """Extract concatenated text fields from a Codex session message payload."""
    content = payload.get("content")
    if not isinstance(content, list):
        return None

    parts: list[str] = []
    for item in content:
        if not isinstance(item, dict):
            continue
        text = item.get("text")
        if isinstance(text, str) and text:
            parts.append(text)

    if not parts:
        return None

    return "\n".join(parts)


def _is_skippable_user_message(text: str) -> bool:
    stripped = text.strip()
    # Ignore injected boilerplate blocks (common in session replays).
    return stripped.startswith("# AGENTS.md instructions") or stripped.startswith(
        "<environment_context>"
    )


APPROVAL_RE = re.compile(
    r"\b("
    r"thanks|thank you|great|awesome|perfect|nice|love|excellent|amazing|good stuff|"
    r"nailed it|exactly|lgtm|looks good|ship it|go ahead|proceed|continue|"
    r"yep|yeah|yes|ok|okay|cool|sounds good"
    r")\b",
    re.IGNORECASE,
)

DISAPPROVAL_RE = re.compile(
    r"\b("
    r"wrong|doesn't|does not|don't|do not|not working|failed|error|issue|bug|"
    r"stop|hold on|wait|regression"
    r")\b",
    re.IGNORECASE,
)

DIRECTIVE_RE = re.compile(
    r"^\s*("
    r"run|rerun|fix|add|remove|change|refactor|implement|ship|merge|squash|"
    r"commit|push|start|continue|proceed|next|move on|update|cleanup"
    r")\b",
    re.IGNORECASE,
)


def _looks_like_approval(user_text: str) -> bool:
    stripped = user_text.strip()

    if DISAPPROVAL_RE.search(stripped):
        return False

    # 1) Keyword approvals.
    if APPROVAL_RE.search(stripped):
        return True

    # 2) Very short acknowledgements.
    # Examples: "2", "ok", "yep".
    if len(stripped) <= 6 and stripped:
        return True

    # 3) Next-step directives: imperative follow-on instructions.
    if DIRECTIVE_RE.search(stripped):
        return True

    return False


def _default_sessions_root() -> Path:
    return Path.home() / ".codex" / "sessions"


def _design_heuristics() -> list[Heuristic]:
    # NOTE: These are intentionally broad. They are meant to detect patterns
    # across varied session content without quoting or leaking snippets.
    return [
        Heuristic(
            key="add_laws",
            bullet="Reach for Algebra-Driven Design when structure repeats (combine/merge, map/fold/compose, variant explosion).",
            pattern=re.compile(
                r"\b(algebra-driven|\bADD\b|monoid|semigroup|functor|applicative|monad|"
                r"identity law|associativity|law check|executable law|round-?trip|"
                r"combine|merge|map|fold|compose|homomorphism)\b",
                re.IGNORECASE,
            ),
        ),
        Heuristic(
            key="minimal_algebra",
            bullet="Prefer the smallest algebra/type model that explains the behavior; avoid overfitting.",
            pattern=re.compile(
                r"\b(smallest algebra|minimal algebra|avoid overfitting|pick the minimal|"
                r"smallest.*(fits|that fits))\b",
                re.IGNORECASE,
            ),
        ),
        Heuristic(
            key="law_check",
            bullet="When you go algebraic, add at least one executable law check (or compensate with a tight test/assertion/log).",
            pattern=re.compile(
                r"\b(executable law|law check|identity\b|associativity\b|functor identity|"
                r"functor composition|round-?trip|homomorphism)\b",
                re.IGNORECASE,
            ),
        ),
        Heuristic(
            key="derive_ops",
            bullet="Derive operations from the model to collapse ad-hoc branching.",
            pattern=re.compile(
                r"\b(derive operations|reduce ad-?hoc branching|collapse branching|"
                r"operations from the algebra|encode the rules)\b",
                re.IGNORECASE,
            ),
        ),
        Heuristic(
            key="close_loop",
            bullet="Don’t claim done without a validation signal (tests/lint/typecheck/logs).",
            pattern=re.compile(
                r"\b(close the loop|validation signal|validate|verification|prove with|"
                r"run (tests|lint|typecheck)|tests? (pass|passed)|format.*ok|build.*ok)\b",
                re.IGNORECASE,
            ),
        ),
        Heuristic(
            key="fastest_signal",
            bullet="Prefer the fastest credible local loop (focused test/repro) before broad suites.",
            pattern=re.compile(
                r"\b(local-first|fastest credible signal|focused tests?|tight loop|"
                r"characterization test|reduce uncertainty first|instrumentation)\b",
                re.IGNORECASE,
            ),
        ),
        Heuristic(
            key="clarify_contract",
            bullet="Clarify the contract (what ‘working’ means) before cutting code.",
            pattern=re.compile(
                r"\b(clarify|unambiguous|ambiguous|acceptance criteria|success criteria|"
                r"contract|restate .*working|working for this change)\b",
                re.IGNORECASE,
            ),
        ),
        Heuristic(
            key="stop_and_ask",
            bullet="Stop and ask when requirements are ambiguous or product-sensitive; don’t guess semantics.",
            pattern=re.compile(
                r"\b(stop and ask|don\W*t guess|do not guess|requirements are ambiguous|"
                r"ask before.*semantic|product-sensitive)\b",
                re.IGNORECASE,
            ),
        ),
        Heuristic(
            key="invariants",
            bullet="Name invariants at risk; make illegal states unrepresentable where feasible.",
            pattern=re.compile(
                r"\b(invariant|illegal state|unrepresentable|type-first|"
                r"smart constructor|tagged union|typestate|compile-time|construction-time)\b",
                re.IGNORECASE,
            ),
        ),
        Heuristic(
            key="types_over_branching",
            bullet="Prefer data + types over branching and boolean flags.",
            pattern=re.compile(
                r"\b(boolean soup|flag soup|avoid boolean|data structures? over|"
                r"tagged union|sum type|coproduct|product type)\b",
                re.IGNORECASE,
            ),
        ),
        Heuristic(
            key="trace",
            bullet="Use TRACE to keep code legible: type-first, readable in 30 seconds, atomic, low cognitive load, essential-only.",
            pattern=re.compile(
                r"\b(TRACE|cognitive heat map|cognitive load|atomic|essential complexity|"
                r"incidental complexity|readability)\b",
                re.IGNORECASE,
            ),
        ),
        Heuristic(
            key="complexity_moves",
            bullet="Reduce complexity mechanically: guard clauses > nesting; flatten → rename → extract.",
            pattern=re.compile(
                r"\b(guard clause|reduce nesting|flatten|rename\s*→\s*extract|"
                r"rename then extract|extract function)\b",
                re.IGNORECASE,
            ),
        ),
        Heuristic(
            key="footguns",
            bullet="Defuse footguns by design: make misuse hard via naming, parameter order, or richer types.",
            pattern=re.compile(
                r"\b(footgun|misuse|misuse-prone|confusing params?|named parameters|"
                r"make misuse impossible|typestate)\b",
                re.IGNORECASE,
            ),
        ),
        Heuristic(
            key="failure_modes",
            bullet="Treat failure modes as part of the design surface (nullability, error paths, resource lifetimes).",
            pattern=re.compile(
                r"\b(error handling|failure mode|nullable|nullability|error paths?|"
                r"resource lifetime|crash|corruption)\b",
                re.IGNORECASE,
            ),
        ),
        Heuristic(
            key="error_paths_invariants",
            bullet="Ensure error paths preserve invariants; prove it with focused checks.",
            pattern=re.compile(
                r"\b(error paths? must|all error paths|preserve invariants|"
                r"prove with.*(test|assertion|log))\b",
                re.IGNORECASE,
            ),
        ),
        Heuristic(
            key="characterize_then_refactor",
            bullet="Before refactoring, pin behavior with a characterization test or instrumentation.",
            pattern=re.compile(
                r"\b(characterization test|instrumentation|reduce uncertainty first|"
                r"repro contract)\b",
                re.IGNORECASE,
            ),
        ),
        Heuristic(
            key="reversible",
            bullet="Prefer reversible progress: small, reviewable steps that are easy to undo.",
            pattern=re.compile(
                r"\b(reversible|easy to undo|easy to review|reviewable|small commits?|"
                r"micro-commit)\b",
                re.IGNORECASE,
            ),
        ),
        Heuristic(
            key="diff_hygiene",
            bullet="Keep the diff clean: avoid incidental edits; remove debug scaffolding and dead code.",
            pattern=re.compile(
                r"\b(unrelated diffs|diff clean|incidental edits|remove debug|"
                r"debug scaffolding|dead code)\b",
                re.IGNORECASE,
            ),
        ),
        Heuristic(
            key="minimal_incision",
            bullet="Make the smallest change that could be correct (minimal incision).",
            pattern=re.compile(
                r"\b(minimal incision|smallest change|smallest diff|minimal collateral|"
                r"minimal churn|surgical)\b",
                re.IGNORECASE,
            ),
        ),
        Heuristic(
            key="no_scope_creep",
            bullet="Prevent scope creep: stay inside the request; ask before widening.",
            pattern=re.compile(
                r"\b(scope creep|stay inside|out of scope|ask before widening|"
                r"widening scope)\b",
                re.IGNORECASE,
            ),
        ),
        Heuristic(
            key="evidence_before_abstraction",
            bullet="Earn abstractions: gather instances (rule of three), run the seam test, and keep a break-glass scenario.",
            pattern=re.compile(
                r"\b(evidence before abstraction|rule of three|3\+ instances|"
                r"seam test|break-glass|premature abstraction)\b",
                re.IGNORECASE,
            ),
        ),
    ]


def _scan_sessions(
    sessions_root: Path,
    heuristics: list[Heuristic],
    *,
    approval_weight: int,
) -> list[tuple[int, int, int, Heuristic]]:
    total_counts: dict[str, int] = {h.key: 0 for h in heuristics}
    approved_counts: dict[str, int] = {h.key: 0 for h in heuristics}

    pending_hits: Optional[set[str]] = None

    for fp in _iter_session_files(sessions_root):
        try:
            with fp.open("r", encoding="utf-8") as f:
                pending_hits = None
                for raw in f:
                    line = raw.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except Exception:
                        continue

                    if obj.get("type") != "response_item":
                        continue

                    payload = obj.get("payload")
                    if (
                        not isinstance(payload, dict)
                        or payload.get("type") != "message"
                    ):
                        continue

                    role = payload.get("role")
                    if role not in {"assistant", "user"}:
                        continue

                    text = _message_text(payload)
                    if not text:
                        continue

                    if role == "assistant":
                        assistant_text = _strip_leading_echo(text)
                        hits: set[str] = set()
                        for h in heuristics:
                            if h.pattern.search(assistant_text):
                                hits.add(h.key)
                        for key in hits:
                            total_counts[key] += 1
                        pending_hits = hits
                        continue

                    # role == user
                    if pending_hits is None:
                        continue

                    if _is_skippable_user_message(text):
                        # Ignore boilerplate user blocks without breaking pairing.
                        continue

                    if _looks_like_approval(text):
                        for key in pending_hits:
                            approved_counts[key] += 1

                    pending_hits = None
        except OSError:
            continue

    ranked: list[tuple[int, int, int, Heuristic]] = []
    for h in heuristics:
        total = total_counts[h.key]
        approved = approved_counts[h.key]
        score = total + approval_weight * approved
        ranked.append((score, total, approved, h))

    ranked.sort(key=lambda t: (t[0], t[1], t[2]), reverse=True)
    return ranked


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a top-N design heuristic list from Codex session logs.",
    )
    parser.add_argument(
        "--sessions",
        type=str,
        default=None,
        help="Sessions root (default: ~/.codex/sessions)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=20,
        help="Number of heuristics to output (default: 20)",
    )
    parser.add_argument(
        "--approval-weight",
        type=int,
        default=3,
        help="Weight multiplier for approved messages (default: 3)",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = _parse_args(argv)

    sessions_root = (
        Path(args.sessions).expanduser() if args.sessions else _default_sessions_root()
    )

    if not sessions_root.exists():
        print(f"error: sessions directory not found: {sessions_root}", file=sys.stderr)
        return 2

    heuristics = _design_heuristics()
    ranked = _scan_sessions(
        sessions_root,
        heuristics,
        approval_weight=max(0, int(args.approval_weight)),
    )

    top_n = max(1, int(args.top))
    emitted = 0

    print(f"Top {top_n} design heuristics (derived from sessions):")
    for score, total, approved, h in ranked:
        if total == 0 and approved == 0:
            continue
        print(f"- {h.bullet}")
        emitted += 1
        if emitted >= top_n:
            break

    if emitted < top_n:
        print(
            f"\n(note: only {emitted} heuristics matched the current corpus)",
            file=sys.stderr,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
