from __future__ import annotations

"""Reference pattern for an OpenAI Responses harness that is friendly to prompt caching.

This example focuses on request shape, not full tool execution.
Verify exact parameter literals against your current SDK/reference before shipping.

If you later switch to `store=False` / ZDR with reasoning models, also look at
`python_stateless_reasoning_example.py` for the encrypted reasoning carryover pattern.
"""

from hashlib import sha256
from typing import Any, Iterable

from openai import OpenAI

client = OpenAI()

# Keep instructions stable across turns if you want them in the reusable prefix.
# When using previous_response_id, resend instructions if behavior depends on them;
# the Responses docs say prior instructions are not carried over automatically.
INSTRUCTIONS = """You are a coding assistant for a large monorepo.
Prefer targeted file reads, concise plans, and deterministic edits.
Return patch plans before large edits.
"""

# Keep the full tools array stable and consistently ordered.
TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "name": "search_docs",
        "description": "Search internal engineering docs.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "read_file",
        "description": "Read a file from the repository.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
            },
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "run_tests",
        "description": "Run a targeted test command.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {"type": "string"},
            },
            "required": ["command"],
            "additionalProperties": False,
        },
    },
]

# Keep the structured output schema stable too, if you use one.
TEXT_FORMAT = {
    "type": "json_schema",
    "name": "agent_turn",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "summary": {"type": "string"},
            "next_actions": {
                "type": "array",
                "items": {"type": "string"},
            },
        },
        "required": ["summary", "next_actions"],
        "additionalProperties": False,
    },
}


def make_prompt_cache_key(tenant_id: str, repo_id: str, agent_profile: str = "coding-v1") -> str:
    """Stable routing key for requests that share the same long prefix.

    The exact key choice is an application concern. The important property is that
    related requests share a key, while unrelated high-volume traffic is bucketed separately.
    """

    raw = f"{tenant_id}:{repo_id}:{agent_profile}"
    return sha256(raw.encode("utf-8")).hexdigest()[:32]


def _get_usage_attr(obj: Any, key: str) -> Any:
    if obj is None:
        return None
    if isinstance(obj, dict):
        return obj.get(key)
    return getattr(obj, key, None)


def cached_tokens_from_response(response: Any) -> int:
    usage = _get_usage_attr(response, "usage")
    if usage is None:
        return 0

    details = _get_usage_attr(usage, "input_tokens_details")
    if details is None:
        details = _get_usage_attr(usage, "prompt_tokens_details")
    return int(_get_usage_attr(details, "cached_tokens") or 0)


def input_tokens_from_response(response: Any) -> int:
    usage = _get_usage_attr(response, "usage")
    if usage is None:
        return 0

    value = _get_usage_attr(usage, "input_tokens")
    if value is None:
        value = _get_usage_attr(usage, "prompt_tokens")
    return int(value or 0)


def create_turn(
    *,
    tenant_id: str,
    repo_id: str,
    user_text: str,
    previous_response_id: str | None = None,
    allowed_tool_names: Iterable[str] | None = None,
):
    allowed_names = list(allowed_tool_names or [tool["name"] for tool in TOOLS])

    request: dict[str, Any] = {
        "model": "gpt-5.4",
        "instructions": INSTRUCTIONS,
        "tools": TOOLS,
        "tool_choice": {
            "type": "allowed_tools",
            "mode": "auto",
            "tools": [{"type": "function", "name": name} for name in allowed_names],
        },
        "text": {"format": TEXT_FORMAT},
        "prompt_cache_key": make_prompt_cache_key(tenant_id, repo_id),
        # Enable only if your target model supports it and the extra retention helps your workload.
        # Note: the docs currently disagree on the exact default in-memory literal, but "24h" is stable.
        # "prompt_cache_retention": "24h",
        "store": True,
        "input": [{"role": "user", "content": user_text}],
    }

    if previous_response_id:
        request["previous_response_id"] = previous_response_id

    response = client.responses.create(**request)

    cached = cached_tokens_from_response(response)
    total_input = input_tokens_from_response(response)
    cache_ratio = (cached / total_input) if total_input else 0.0

    print(
        {
            "response_id": getattr(response, "id", None),
            "model": getattr(response, "model", None),
            "input_tokens": total_input,
            "cached_tokens": cached,
            "cache_ratio": round(cache_ratio, 4),
        }
    )

    return response


if __name__ == "__main__":
    first = create_turn(
        tenant_id="acme",
        repo_id="payments-service",
        user_text="Find the function that validates card BIN ranges and explain how it works.",
        allowed_tool_names=["search_docs", "read_file"],
    )

    second = create_turn(
        tenant_id="acme",
        repo_id="payments-service",
        previous_response_id=getattr(first, "id", None),
        user_text="Now propose the smallest safe refactor and tell me which tests to run.",
        allowed_tool_names=["read_file", "run_tests"],
    )

    print(getattr(second, "output_text", None))
