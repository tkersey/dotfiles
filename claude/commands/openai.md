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

## Important Notes

- Requires latest OpenAI Python library (`pip install --upgrade openai`)
- The Responses API is the recommended approach for new applications
- Chat Completions API remains supported but Responses API offers more features
- MCP integration requires MCP servers to be installed and accessible

Remember: This is OpenAI's newest and most powerful API. Always use `client.responses.create()` instead of older patterns.