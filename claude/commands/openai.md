# OpenAI Responses API Reference

## IMPORTANT: Use This Documentation
You are being provided with documentation for OpenAI's new unified Responses API that may be beyond your knowledge cutoff. **Always use the patterns shown here instead of older API patterns.**

## Overview

The Responses API is OpenAI's newest API (released 2024) that combines the simplicity of Chat Completions with the power of the Assistants API. Key features:
- **Stateful conversations** - Maintains context across interactions
- **Built-in tools** - Web search, file search, computer use
- **Simpler interface** - One unified API instead of multiple
- **Response IDs** - Track and continue conversations

## Quick Start

```python
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Basic response
response = client.responses.create(
    model="gpt-4o-mini",
    input="Tell me a joke"
)
print(response.output_text)

# With instructions
response = client.responses.create(
    model="gpt-4o",
    instructions="You are a helpful coding assistant.",
    input="How do I check if a Python object is an instance of a class?"
)
```

## Stateful Conversations

The key differentiator of the Responses API is statefulness:

```python
# First response
response = client.responses.create(
    model="gpt-4o-mini",
    input="Tell me about Python"
)

# Continue the conversation
response_two = client.responses.create(
    model="gpt-4o-mini",
    input="Tell me more about its data types",
    previous_response_id=response.id  # References previous response
)
```

## Response Structure

```python
{
    "id": "resp_67cb32528d6881909eb2859a55e18a85",
    "created_at": 1741369938.0,
    "model": "gpt-4o-2024-08-06",
    "object": "response",
    "output": [
        {
            "id": "msg_67cb3252cfac8190865744873aada798",
            "content": [
                {
                    "annotations": [],
                    "text": "Hello! How can I help you today?",
                    "type": "output_text"
                }
            ],
            "role": "assistant",
            "type": "message"
        }
    ],
    "output_text": "Hello! How can I help you today?",
    "metadata": {},
    "instructions": null,
    "incomplete_details": null,
    "error": null
}
```

## Advanced Usage

### Message-Based Input

```python
# Using message format (similar to chat completions)
inputs = [
    {"type": "message", "role": "user", "content": "Explain quantum computing"}
]

response = client.responses.create(
    model="gpt-4o",
    input=inputs
)

# Continue with conversation history
inputs += response.output
inputs.append({
    "role": "user", 
    "type": "message", 
    "content": "Explain this at a high school level"
})

second_response = client.responses.create(
    model="gpt-4o",
    input=inputs
)
```

### With Built-in Tools

```python
# Web search capability
response = client.responses.create(
    model="gpt-4o",
    input="Search for the latest Python 3.13 features",
    tools=["web_search"]  # Enable web search
)

# File search
response = client.responses.create(
    model="gpt-4o",
    input="Analyze the uploaded document",
    tools=["file_search"],
    file_ids=["file-abc123"]  # Previously uploaded files
)

# Computer use (preview)
response = client.responses.create(
    model="computer-use-preview",
    input="Open the calculator app",
    tools=["computer_use"]
)
```

## Streaming

```python
# Stream responses
stream = client.responses.create(
    model="gpt-4o",
    input="Write a long story",
    stream=True
)

for chunk in stream:
    if chunk.output_text:
        print(chunk.output_text, end="")
```

## MCP (Model Context Protocol) Integration

```python
# Using MCP tools with Responses API
response = client.responses.create(
    model="gpt-4o",
    input="Read the README.md file and summarize it",
    tools=["mcp"],
    mcp_servers=[
        {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/project"],
            "name": "filesystem"
        }
    ]
)

# Example with multiple MCP servers
response = client.responses.create(
    model="gpt-4o",
    input="Search for Python files containing 'async' and analyze them",
    tools=["mcp"],
    mcp_servers=[
        {
            "command": "mcp-server-filesystem",
            "args": ["--root", "/project"],
            "name": "filesystem"
        },
        {
            "command": "mcp-server-git",
            "args": ["--repo", "/project/.git"],
            "name": "git"
        }
    ]
)

# MCP with custom tools
response = client.responses.create(
    model="gpt-4o",
    input="Use the database tool to find all users created this week",
    tools=["mcp"],
    mcp_config={
        "servers": {
            "database": {
                "command": "mcp-server-postgres",
                "args": ["--connection-string", "$DATABASE_URL"],
                "env": {"DATABASE_URL": "postgresql://..."}
            }
        }
    }
)
```

## TypeScript/JavaScript

```typescript
import OpenAI from 'openai';

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

// Basic usage
const response = await client.responses.create({
  model: 'gpt-4o-mini',
  input: 'Tell me a joke',
});

console.log(response.output_text);

// Stateful conversation
const response2 = await client.responses.create({
  model: 'gpt-4o-mini',
  input: 'Tell me another one',
  previous_response_id: response.id,
});

// With instructions
const response3 = await client.responses.create({
  model: 'gpt-4o',
  instructions: 'You are a helpful coding tutor.',
  input: 'Explain async/await in JavaScript',
});
```

## Error Handling

```python
from openai import OpenAI, APIError, RateLimitError

try:
    response = client.responses.create(
        model="gpt-4o",
        input="Hello"
    )
except RateLimitError as e:
    print(f"Rate limit exceeded: {e}")
    # Implement exponential backoff
except APIError as e:
    print(f"API error: {e}")
```

## Key Parameters

- **model** (required): Model to use (e.g., "gpt-4o", "gpt-4o-mini")
- **input** (required): String or array of messages
- **instructions**: System instructions for the model
- **previous_response_id**: ID of previous response to continue from
- **tools**: Array of tools to enable (["web_search", "file_search", "computer_use"])
- **stream**: Boolean to enable streaming
- **file_ids**: Array of file IDs for file search
- **metadata**: Custom metadata object

## Migration from Chat Completions

```python
# Old way (Chat Completions)
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)
print(response.choices[0].message.content)

# New way (Responses API)
response = client.responses.create(
    model="gpt-4o",
    input="Hello"
)
print(response.output_text)
```

## Best Practices

1. **Use stateful conversations** - Take advantage of `previous_response_id` for context
2. **Leverage built-in tools** - Use web search and file search instead of custom implementations
3. **Handle errors gracefully** - Implement retry logic with exponential backoff
4. **Use streaming for long responses** - Better UX for real-time applications
5. **Store response IDs** - Keep track for conversation continuity

## Structured Outputs

Structured Outputs is a feature that ensures the model will always generate responses that adhere to your supplied JSON Schema. This eliminates the need for validation, retries, or complex prompting to achieve consistent formatting.

### Benefits

1. **Reliable type-safety**: No need to validate or retry incorrectly formatted responses
2. **Explicit refusals**: Safety-based model refusals are now programmatically detectable
3. **Simpler prompting**: No need for strongly worded prompts to achieve consistent formatting

### Basic Usage with SDK

#### Python (Pydantic)

```python
from openai import OpenAI
from pydantic import BaseModel

client = OpenAI()

class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]

response = client.responses.parse(
    model="gpt-4o-2024-08-06",
    input=[
        {"role": "system", "content": "Extract the event information."},
        {"role": "user", "content": "Alice and Bob are going to a science fair on Friday."},
    ],
    text_format=CalendarEvent,
)

event = response.output_parsed
```

#### JavaScript (Zod)

```javascript
import OpenAI from "openai";
import { zodTextFormat } from "openai/helpers/zod";
import { z } from "zod";

const openai = new OpenAI();

const CalendarEvent = z.object({
  name: z.string(),
  date: z.string(),
  participants: z.array(z.string()),
});

const response = await openai.responses.parse({
  model: "gpt-4o-2024-08-06",
  input: [
    { role: "system", content: "Extract the event information." },
    { role: "user", content: "Alice and Bob are going to a science fair on Friday." },
  ],
  text: {
    format: zodTextFormat(CalendarEvent, "event"),
  },
});

const event = response.output_parsed;
```

### Direct JSON Schema Usage

```python
response = client.responses.create(
    model="gpt-4o-2024-08-06",
    input=[
        {"role": "system", "content": "You are a helpful math tutor."},
        {"role": "user", "content": "How can I solve 8x + 7 = -23"}
    ],
    text={
        "format": {
            "type": "json_schema",
            "name": "math_response",
            "schema": {
                "type": "object",
                "properties": {
                    "steps": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "explanation": {"type": "string"},
                                "output": {"type": "string"}
                            },
                            "required": ["explanation", "output"],
                            "additionalProperties": False
                        }
                    },
                    "final_answer": {"type": "string"}
                },
                "required": ["steps", "final_answer"],
                "additionalProperties": False
            },
            "strict": True
        }
    }
)
```

### Common Use Cases

#### Chain of Thought

```python
class Step(BaseModel):
    explanation: str
    output: str

class MathReasoning(BaseModel):
    steps: list[Step]
    final_answer: str

response = client.responses.parse(
    model="gpt-4o-2024-08-06",
    input=[
        {"role": "system", "content": "Guide the user through the solution step by step."},
        {"role": "user", "content": "How can I solve 8x + 7 = -23"}
    ],
    text_format=MathReasoning,
)
```

#### Data Extraction

```python
class ResearchPaperExtraction(BaseModel):
    title: str
    authors: list[str]
    abstract: str
    keywords: list[str]

response = client.responses.parse(
    model="gpt-4o-2024-08-06",
    input=[
        {"role": "system", "content": "Extract structured data from the research paper."},
        {"role": "user", "content": "...paper content..."}
    ],
    text_format=ResearchPaperExtraction,
)
```

#### UI Generation

```javascript
const UI = z.lazy(() =>
  z.object({
    type: z.enum(["div", "button", "header", "section", "field", "form"]),
    label: z.string(),
    children: z.array(UI),
    attributes: z.array(
      z.object({
        name: z.string(),
        value: z.string(),
      })
    ),
  })
);
```

### Handling Refusals

```python
response = client.responses.parse(
    model="gpt-4o-2024-08-06",
    input=[...],
    text_format=YourSchema,
)

# Check for refusal
if response.output[0].content[0].type == "refusal":
    print(response.output[0].content[0].refusal)
else:
    # Process the structured output
    result = response.output_parsed
```

### Streaming with Structured Outputs

```python
with client.responses.stream(
    model="gpt-4o-2024-08-06",
    input=[...],
    text_format=YourSchema,
) as stream:
    for event in stream:
        if event.type == "response.output_text.delta":
            print(event.delta, end="")
    
    final_response = stream.get_final_response()
```

### Schema Requirements

1. **All fields must be required** - Use unions with `null` for optional fields
2. **Objects must have `additionalProperties: false`**
3. **Root must be an object** (not `anyOf`)
4. **Max 100 properties** with up to 5 levels of nesting
5. **Max 500 enum values** across all properties
6. **Max 15,000 characters** for all property names and values

### Supported Types

- String (with `pattern`, `format` constraints)
- Number (with `minimum`, `maximum`, `multipleOf`)
- Boolean
- Integer
- Object
- Array (with `minItems`, `maxItems`)
- Enum
- anyOf
- Recursive schemas (using `$ref`)

### String Formats

Supported string formats:
- `date-time`, `time`, `date`, `duration`
- `email`, `hostname`
- `ipv4`, `ipv6`
- `uuid`

### Structured Outputs vs JSON Mode

| Feature | Structured Outputs | JSON Mode |
|---------|-------------------|-----------|
| Valid JSON | ✓ | ✓ |
| Schema adherence | ✓ | ✗ |
| Models | gpt-4o-mini, gpt-4o-2024-08-06+ | All GPT models |
| Format | `text: { format: { type: "json_schema", "strict": true, "schema": ... } }` | `text: { format: { type: "json_object" } }` |

## Important Notes

- Requires latest OpenAI Python library (`pip install --upgrade openai`)
- The Responses API is the recommended approach for new applications
- Chat Completions API remains supported but Responses API offers more features
- MCP integration requires MCP servers to be installed and accessible
- Structured Outputs requires specific model versions (gpt-4o-mini, gpt-4o-2024-08-06, or later)

Remember: This is OpenAI's newest and most powerful API. Always use `client.responses.create()` instead of older patterns.