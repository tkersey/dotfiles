from __future__ import annotations

"""Minimal stateless reasoning pattern for OpenAI Responses + prompt-caching-aware chaining.

Use this when:
- you are using reasoning models
- `store=False` or Zero Data Retention is in effect
- you still want to carry forward prior reasoning state between turns

Key rule:
- request `include=["reasoning.encrypted_content"]`
- append the returned reasoning item(s) from `response.output` to your next `input`
"""

from typing import Any
import json

from openai import OpenAI

client = OpenAI()

TOOLS = [
    {
        "type": "function",
        "name": "get_weather",
        "description": "Return the current temperature for a city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string"},
            },
            "required": ["city"],
            "additionalProperties": False,
        },
    }
]


def first_turn() -> Any:
    response = client.responses.create(
        model="o4-mini",
        input=[{"role": "user", "content": "What's the weather in Paris right now?"}],
        tools=TOOLS,
        store=False,
        include=["reasoning.encrypted_content"],
        # You can also set a stable prompt_cache_key if this workflow reuses a long common prefix.
        # prompt_cache_key="weather-agent:prod",
    )
    return response


def second_turn(prior_response: Any) -> Any:
    # In stateless mode, carry forward the entire prior output array, which includes
    # any encrypted reasoning item plus the tool call item(s).
    context = list(getattr(prior_response, "output", []) or [])

    tool_call = next((item for item in context if getattr(item, "type", None) == "function_call"), None)
    if tool_call is None:
        raise RuntimeError("Expected a function_call item in prior_response.output")

    arguments = json.loads(getattr(tool_call, "arguments", "{}") or "{}")
    city = arguments.get("city", "Paris")

    # Mock tool result.
    temperature_c = 20

    context.append(
        {
            "type": "function_call_output",
            "call_id": getattr(tool_call, "call_id"),
            "output": json.dumps({"city": city, "temperature_c": temperature_c}),
        }
    )

    response = client.responses.create(
        model="o4-mini",
        input=context,
        tools=TOOLS,
        store=False,
        include=["reasoning.encrypted_content"],
        # Reuse the same stable prompt_cache_key if you use one above.
        # prompt_cache_key="weather-agent:prod",
    )
    return response


if __name__ == "__main__":
    first = first_turn()
    print("First response ID:", getattr(first, "id", None))
    for item in getattr(first, "output", []) or []:
        print("Output item:", getattr(item, "type", None))

    second = second_turn(first)
    print("Second response ID:", getattr(second, "id", None))
    print(getattr(second, "output_text", None))
