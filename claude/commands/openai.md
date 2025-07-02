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

Model Context Protocol (MCP) is an open protocol that standardizes how applications provide tools and context to LLMs. The Responses API supports both local and remote MCP servers.

### Remote MCP Servers

Remote MCP servers are hosted by developers and organizations across the internet, providing tools accessible via HTTP/SSE protocols.

#### Basic Usage

```python
from openai import OpenAI

client = OpenAI()

# Using a remote MCP server (DeepWiki)
response = client.responses.create(
    model="gpt-4o",
    tools=[{
        "type": "mcp",
        "server_label": "deepwiki",
        "server_url": "https://mcp.deepwiki.com/mcp",
        "require_approval": "never"
    }],
    input="What transport protocols are supported in the MCP spec?"
)

print(response.output_text)
```

```javascript
import OpenAI from "openai";

const client = new OpenAI();

const response = await client.responses.create({
    model: "gpt-4o",
    tools: [{
        type: "mcp",
        server_label: "deepwiki",
        server_url: "https://mcp.deepwiki.com/mcp",
        require_approval: "never"
    }],
    input: "What transport protocols are supported in the MCP spec?"
});

console.log(response.output_text);
```

#### Authentication

Most MCP servers require authentication via headers:

```python
# Using Stripe MCP with authentication
response = client.responses.create(
    model="gpt-4o",
    input="Create a payment link for $20",
    tools=[{
        "type": "mcp",
        "server_label": "stripe",
        "server_url": "https://mcp.stripe.com",
        "headers": {
            "Authorization": f"Bearer {STRIPE_API_KEY}"
        }
    }]
)
```

```javascript
const response = await client.responses.create({
    model: "gpt-4o",
    input: "Create a payment link for $20",
    tools: [{
        type: "mcp",
        server_label: "stripe",
        server_url: "https://mcp.stripe.com",
        headers: {
            Authorization: `Bearer ${STRIPE_API_KEY}`
        }
    }]
});
```

#### Tool Filtering

Filter specific tools from MCP servers:

```python
# Only import specific tools
response = client.responses.create(
    model="gpt-4o",
    tools=[{
        "type": "mcp",
        "server_label": "deepwiki",
        "server_url": "https://mcp.deepwiki.com/mcp",
        "require_approval": "never",
        "allowed_tools": ["ask_question", "read_wiki_structure"]
    }],
    input="What's in the MCP specification?"
)
```

#### Approval Workflow

By default, OpenAI requests approval before sharing data with remote MCP servers:

```python
# First request generates approval request
response = client.responses.create(
    model="gpt-4o",
    tools=[{
        "type": "mcp",
        "server_label": "deepwiki",
        "server_url": "https://mcp.deepwiki.com/mcp"
        # require_approval defaults to "always"
    }],
    input="Search for information about React hooks"
)

# Response contains approval request
# {
#     "id": "mcpr_682d498e3bd4819196a0ce1664f8e77b04ad1e533afccbfa",
#     "type": "mcp_approval_request",
#     "arguments": "{\"repoName\":\"facebook/react\",\"question\":\"React hooks\"}",
#     "name": "ask_question",
#     "server_label": "deepwiki"
# }

# Approve the request
approval_response = client.responses.create(
    model="gpt-4o",
    tools=[{
        "type": "mcp",
        "server_label": "deepwiki",
        "server_url": "https://mcp.deepwiki.com/mcp"
    }],
    previous_response_id=response.id,
    input=[{
        "type": "mcp_approval_response",
        "approve": True,
        "approval_request_id": "mcpr_682d498e3bd4819196a0ce1664f8e77b04ad1e533afccbfa"
    }]
)
```

#### Skip Approvals

For trusted servers, skip approvals:

```python
# Never require approval for all tools
response = client.responses.create(
    model="gpt-4o",
    tools=[{
        "type": "mcp",
        "server_label": "trusted-server",
        "server_url": "https://trusted.example.com/mcp",
        "require_approval": "never"
    }],
    input="Process this request"
)

# Never require approval for specific tools only
response = client.responses.create(
    model="gpt-4o",
    tools=[{
        "type": "mcp",
        "server_label": "server",
        "server_url": "https://example.com/mcp",
        "require_approval": {
            "never": {
                "tool_names": ["safe_tool_1", "safe_tool_2"]
            }
        }
    }],
    input="Use the safe tools"
)
```

### Local MCP Servers

Run MCP servers locally via command-line:

```python
# Local filesystem MCP server
response = client.responses.create(
    model="gpt-4o",
    input="Read the README.md file and summarize it",
    tools=["mcp"],
    mcp_servers=[{
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/project"],
        "name": "filesystem"
    }]
)

# Multiple local MCP servers
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

# MCP with environment variables
response = client.responses.create(
    model="gpt-4o",
    input="Query the database for recent users",
    tools=["mcp"],
    mcp_config={
        "servers": {
            "database": {
                "command": "mcp-server-postgres",
                "args": ["--connection-string", "$DATABASE_URL"],
                "env": {"DATABASE_URL": "postgresql://user:pass@localhost/db"}
            }
        }
    }
)
```

### Popular MCP Servers

The MCP ecosystem includes servers from major providers:

- **Cloudflare** - Worker management and deployment
- **Stripe** - Payment processing (`https://mcp.stripe.com`)
- **Shopify** - E-commerce operations
- **Twilio** - Communications APIs
- **Square** - Payment and commerce
- **Plaid** - Financial services
- **HubSpot** - CRM operations
- **Intercom** - Customer messaging
- **PayPal** - Payment processing
- **Zapier** - Workflow automation
- **DeepWiki** - GitHub repository exploration (`https://mcp.deepwiki.com/mcp`)
- **Pipedream** - Workflow automation

### How MCP Works

1. **Tool Discovery**: When you attach an MCP server, the API fetches available tools
2. **Tool Import**: Tools are imported and shown in `mcp_list_tools` output
3. **Tool Calling**: Model decides when to call MCP tools based on context
4. **Result Integration**: Tool outputs are integrated into the model's response

#### Response Structure

```python
# Tool list response
{
    "id": "mcpl_682d4379df088191886b70f4ec39f90403937d5f622d7a90",
    "type": "mcp_list_tools",
    "server_label": "deepwiki",
    "tools": [
        {
            "name": "read_wiki_structure",
            "input_schema": {
                "type": "object",
                "properties": {
                    "repoName": {
                        "type": "string",
                        "description": "GitHub repository: owner/repo"
                    }
                },
                "required": ["repoName"],
                "additionalProperties": false
            }
        }
    ]
}

# Tool call response
{
    "id": "mcp_682d437d90a88191bf88cd03aae0c3e503937d5f622d7a90",
    "type": "mcp_call",
    "name": "ask_question",
    "arguments": "{\"repoName\":\"openai/gpt-4\",\"question\":\"architecture\"}",
    "output": "The GPT-4 architecture consists of...",
    "server_label": "deepwiki",
    "error": null
}
```

### Security Best Practices

**⚠️ IMPORTANT: Only connect to trusted MCP servers. Malicious servers can:**
- Exfiltrate sensitive data from model context
- Inject prompt instructions
- Update tool behavior unexpectedly

**Best Practices:**

1. **Use Official Servers** - Prefer servers hosted by service providers themselves
2. **Review Tool Calls** - Always review data being sent to MCP servers
3. **Log Interactions** - Keep audit logs of MCP tool usage
4. **Limit Permissions** - Use `allowed_tools` to restrict available tools
5. **Test Thoroughly** - Test MCP integrations in safe environments first

### Complete Example: Multi-Service Integration

```python
from openai import OpenAI
import os

client = OpenAI()

# Configure multiple MCP services
tools = [
    {
        "type": "mcp",
        "server_label": "stripe",
        "server_url": "https://mcp.stripe.com",
        "headers": {
            "Authorization": f"Bearer {os.getenv('STRIPE_API_KEY')}"
        },
        "require_approval": {
            "never": {
                "tool_names": ["create_payment_link", "list_customers"]
            }
        }
    },
    {
        "type": "mcp",
        "server_label": "twilio",
        "server_url": "https://mcp.twilio.com",
        "headers": {
            "Authorization": f"Bearer {os.getenv('TWILIO_AUTH_TOKEN')}"
        },
        "allowed_tools": ["send_sms"],
        "require_approval": "never"
    },
    {
        "type": "mcp",
        "server_label": "deepwiki",
        "server_url": "https://mcp.deepwiki.com/mcp",
        "require_approval": "never"
    }
]

# Create a complex workflow
response = client.responses.create(
    model="gpt-4o",
    tools=tools,
    input="""
    1. Look up the Stripe API documentation for creating payment links
    2. Create a $50 payment link for a "Premium Subscription"
    3. Send an SMS to +1234567890 with the payment link
    """
)

print(response.output_text)
```

### MCP Limitations and Notes

- **Rate Limits**: Tier-based limits apply (200-2000 RPM)
- **No Additional Fees**: Only pay for tokens used
- **Data Residency**: MCP servers have their own data policies
- **Zero Data Retention**: Compatible but subject to MCP server policies
- **Transport Protocols**: Supports Streamable HTTP and HTTP/SSE
- **Error Handling**: MCP errors populate the `error` field in responses

### Debugging MCP

```python
# Enable verbose output to see MCP interactions
response = client.responses.create(
    model="gpt-4o",
    tools=[{
        "type": "mcp",
        "server_label": "test-server",
        "server_url": "https://example.com/mcp",
        "require_approval": "always"  # Force approvals for debugging
    }],
    input="Test the MCP integration"
)

# Check for MCP-specific outputs
for item in response.output:
    if item.type == "mcp_list_tools":
        print(f"Imported tools: {[t['name'] for t in item.tools]}")
    elif item.type == "mcp_approval_request":
        print(f"Approval needed for: {item.name}({item.arguments})")
    elif item.type == "mcp_call":
        if item.error:
            print(f"MCP Error: {item.error}")
        else:
            print(f"MCP Success: {item.name} returned {len(item.output)} chars")
```
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

## Function Calling

Function calling provides a powerful way for models to interface with your code or external services. The model can decide to call functions you define, enabling it to fetch data or take actions.

### Overview

Function calling has two primary use cases:
1. **Fetching Data** - Retrieve up-to-date information (RAG), search knowledge bases, call APIs
2. **Taking Action** - Submit forms, modify application state, perform workflow actions

### Basic Usage

```python
from openai import OpenAI
import json

client = OpenAI()

# Define your function
def get_weather(location):
    # Your actual implementation
    return f"20°C and sunny in {location}"

# Define the function schema
tools = [{
    "type": "function",
    "name": "get_weather",
    "description": "Get current weather for a location",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "City and country e.g. Paris, France"
            }
        },
        "required": ["location"],
        "additionalProperties": False
    },
    "strict": True  # Enable strict mode for reliable schema adherence
}]

# Call the model with functions
response = client.responses.create(
    model="gpt-4o",
    input="What's the weather like in Paris?",
    tools=tools
)

# Handle function calls
for item in response.output:
    if item.type == "function_call":
        # Parse arguments and call function
        args = json.loads(item.arguments)
        result = get_weather(args["location"])
        
        # Send result back to model
        response = client.responses.create(
            model="gpt-4o",
            input=[
                {"role": "user", "content": "What's the weather like in Paris?"},
                item,  # Include the function call
                {
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": result
                }
            ],
            tools=tools
        )
        print(response.output_text)
```

### JavaScript Example

```javascript
import OpenAI from "openai";

const openai = new OpenAI();

// Define your function
async function getWeather(location) {
    // Your actual implementation
    return `20°C and sunny in ${location}`;
}

// Define the function schema
const tools = [{
    type: "function",
    name: "get_weather",
    description: "Get current weather for a location",
    parameters: {
        type: "object",
        properties: {
            location: {
                type: "string",
                description: "City and country e.g. Paris, France"
            }
        },
        required: ["location"],
        additionalProperties: false
    },
    strict: true
}];

// Call the model
const response = await openai.responses.create({
    model: "gpt-4o",
    input: "What's the weather like in Paris?",
    tools
});

// Handle function calls
for (const item of response.output) {
    if (item.type === "function_call") {
        const args = JSON.parse(item.arguments);
        const result = await getWeather(args.location);
        
        // Send result back
        const finalResponse = await openai.responses.create({
            model: "gpt-4o",
            input: [
                { role: "user", content: "What's the weather like in Paris?" },
                item,
                {
                    type: "function_call_output",
                    call_id: item.call_id,
                    output: result
                }
            ],
            tools
        });
        console.log(finalResponse.output_text);
    }
}
```

### Multiple Function Calls

The model can call multiple functions in a single response:

```python
tools = [
    {
        "type": "function",
        "name": "get_weather",
        "description": "Get weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string"}
            },
            "required": ["location"],
            "additionalProperties": False
        }
    },
    {
        "type": "function", 
        "name": "send_email",
        "description": "Send an email",
        "parameters": {
            "type": "object",
            "properties": {
                "to": {"type": "string"},
                "subject": {"type": "string"},
                "body": {"type": "string"}
            },
            "required": ["to", "subject", "body"],
            "additionalProperties": False
        }
    }
]

response = client.responses.create(
    model="gpt-4o",
    input="What's the weather in Paris and London? Also send the info to john@example.com",
    tools=tools
)

# Handle multiple function calls
function_results = []
for item in response.output:
    if item.type == "function_call":
        args = json.loads(item.arguments)
        
        if item.name == "get_weather":
            result = get_weather(args["location"])
        elif item.name == "send_email":
            result = send_email(args["to"], args["subject"], args["body"])
        
        function_results.append({
            "type": "function_call_output",
            "call_id": item.call_id,
            "output": str(result)
        })

# Send all results back
if function_results:
    final_response = client.responses.create(
        model="gpt-4o",
        input=response.output + function_results,
        tools=tools
    )
```

### Tool Choice

Control when and how functions are called:

```python
# Auto (default) - Model decides
response = client.responses.create(
    model="gpt-4o",
    input="Hello",
    tools=tools,
    tool_choice="auto"  # Can call 0, 1, or multiple functions
)

# Required - Must call at least one function
response = client.responses.create(
    model="gpt-4o",
    input="What's the weather?",
    tools=tools,
    tool_choice="required"
)

# Force specific function
response = client.responses.create(
    model="gpt-4o",
    input="Tell me about Paris",
    tools=tools,
    tool_choice={"type": "function", "name": "get_weather"}
)

# Disable functions
response = client.responses.create(
    model="gpt-4o",
    input="Just chat with me",
    tools=tools,
    tool_choice="none"
)
```

### Parallel Function Calling

Control whether multiple functions can be called in one turn:

```python
# Allow parallel calls (default)
response = client.responses.create(
    model="gpt-4o",
    input="Check weather in Paris and London",
    tools=tools,
    parallel_tool_calls=True  # Default
)

# Disable parallel calls - only 0 or 1 function per turn
response = client.responses.create(
    model="gpt-4o",
    input="Check weather in Paris and London",
    tools=tools,
    parallel_tool_calls=False
)
```

### Streaming Function Calls

Stream function calls as they're generated:

```python
stream = client.responses.create(
    model="gpt-4o",
    input="What's the weather in Paris?",
    tools=tools,
    stream=True
)

function_calls = {}
for event in stream:
    if event.type == "response.output_item.added":
        # New function call started
        function_calls[event.output_index] = event.item
    elif event.type == "response.function_call_arguments.delta":
        # Accumulate arguments
        if event.output_index in function_calls:
            function_calls[event.output_index].arguments += event.delta
    elif event.type == "response.function_call_arguments.done":
        # Function call complete
        call = function_calls[event.output_index]
        args = json.loads(call.arguments)
        # Execute function...
```

### Best Practices

1. **Clear function definitions**
   - Write detailed descriptions and parameter documentation
   - Use enums and strict types to prevent invalid calls
   - Include examples in descriptions when needed

2. **Enable strict mode**
   - Always set `"strict": true` for reliable schema adherence
   - Ensures all fields are required (use null unions for optional)
   - Requires `additionalProperties: false` on objects

3. **Optimize function design**
   - Keep number of functions small (<20 recommended)
   - Combine functions that are always called together
   - Don't make model fill in known parameters

4. **Handle edge cases**
   - Check for refusals or errors before processing
   - Validate function arguments before execution
   - Return clear error messages for function failures

5. **Schema requirements for strict mode**
   - All fields must be in `required` array
   - Objects must have `additionalProperties: false`
   - Use `["string", "null"]` type unions for optional fields

### Function Call with Structured Output

Combine function schemas with Structured Outputs for strict typing:

```python
from pydantic import BaseModel

class WeatherParams(BaseModel):
    location: str
    units: str = "celsius"

# Convert Pydantic model to JSON schema
weather_schema = WeatherParams.model_json_schema()

tools = [{
    "type": "function",
    "name": "get_weather",
    "description": "Get weather data",
    "parameters": {
        **weather_schema,
        "additionalProperties": False
    },
    "strict": True
}]
```

### Complete Example: Weather Assistant

```python
from openai import OpenAI
import json
import requests

client = OpenAI()

def get_weather(latitude, longitude, units="celsius"):
    """Fetch real weather data from API"""
    response = requests.get(
        f"https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m",
            "temperature_unit": units
        }
    )
    data = response.json()
    return {
        "temperature": data["current"]["temperature_2m"],
        "units": data["current_units"]["temperature_2m"]
    }

tools = [{
    "type": "function",
    "name": "get_weather",
    "description": "Get current temperature for coordinates",
    "parameters": {
        "type": "object",
        "properties": {
            "latitude": {
                "type": "number",
                "description": "Latitude coordinate"
            },
            "longitude": {
                "type": "number", 
                "description": "Longitude coordinate"
            },
            "units": {
                "type": ["string", "null"],
                "enum": ["celsius", "fahrenheit"],
                "description": "Temperature units (optional)"
            }
        },
        "required": ["latitude", "longitude", "units"],
        "additionalProperties": False
    },
    "strict": True
}]

# Create conversation with function calling
response = client.responses.create(
    model="gpt-4o",
    input="What's the temperature in Paris right now?",
    tools=tools
)

# Process function calls
messages = [{"role": "user", "content": "What's the temperature in Paris right now?"}]
messages.extend(response.output)

for item in response.output:
    if item.type == "function_call":
        args = json.loads(item.arguments)
        
        # Call the actual function
        result = get_weather(
            args["latitude"],
            args["longitude"],
            args.get("units", "celsius")
        )
        
        # Add function result
        messages.append({
            "type": "function_call_output",
            "call_id": item.call_id,
            "output": json.dumps(result)
        })

# Get final response with function results
final_response = client.responses.create(
    model="gpt-4o",
    input=messages,
    tools=tools
)

print(final_response.output_text)
# Output: "The current temperature in Paris is 15.2°C."
```

## Conversation State Management

Managing conversation state is crucial for multi-turn interactions. The Responses API provides both manual and automatic approaches.

### Automatic State Management (Recommended)

Use `previous_response_id` to automatically maintain conversation context:

```python
from openai import OpenAI

client = OpenAI()

# First message
response = client.responses.create(
    model="gpt-4o-mini",
    input="Tell me a joke"
)
print(response.output_text)

# Continue conversation - API handles all context
second_response = client.responses.create(
    model="gpt-4o-mini",
    previous_response_id=response.id,
    input="Explain why this is funny"
)
print(second_response.output_text)
```

```javascript
import OpenAI from "openai";

const openai = new OpenAI();

// First message
const response = await openai.responses.create({
    model: "gpt-4o-mini",
    input: "Tell me a joke"
});
console.log(response.output_text);

// Continue conversation - API handles all context
const secondResponse = await openai.responses.create({
    model: "gpt-4o-mini",
    previous_response_id: response.id,
    input: "Explain why this is funny"
});
console.log(secondResponse.output_text);
```

### Manual State Management

For more control, manually manage conversation history:

```python
from openai import OpenAI

client = OpenAI()

# Build conversation history
history = [
    {"role": "user", "content": "Tell me a joke"}
]

response = client.responses.create(
    model="gpt-4o-mini",
    input=history
)

# Add response to history
history.extend(response.output)
history.append({"role": "user", "content": "Tell me another"})

# Continue with full context
second_response = client.responses.create(
    model="gpt-4o-mini",
    input=history
)
```

```javascript
const history = [
    { role: "user", content: "Tell me a joke" }
];

const response = await openai.responses.create({
    model: "gpt-4o-mini",
    input: history
});

// Add response to history
history.push(...response.output);
history.push({ role: "user", content: "Tell me another" });

// Continue with full context
const secondResponse = await openai.responses.create({
    model: "gpt-4o-mini",
    input: history
});
```

### Conversation Threading

Create complex conversation threads with multiple branches:

```python
# Main conversation
main_response = client.responses.create(
    model="gpt-4o",
    input="Explain quantum computing"
)

# Branch 1: Technical details
technical_branch = client.responses.create(
    model="gpt-4o",
    previous_response_id=main_response.id,
    input="Go deeper into the mathematics"
)

# Branch 2: Practical applications
practical_branch = client.responses.create(
    model="gpt-4o",
    previous_response_id=main_response.id,
    input="What are real-world applications?"
)

# Continue technical branch
technical_continued = client.responses.create(
    model="gpt-4o",
    previous_response_id=technical_branch.id,
    input="Explain quantum entanglement"
)
```

### Data Retention and Storage

Control whether responses are stored:

```python
# Store response (default) - retained for 30 days
response = client.responses.create(
    model="gpt-4o",
    input="Hello",
    store=True  # Default
)

# Don't store response - ephemeral
response = client.responses.create(
    model="gpt-4o",
    input="Sensitive information",
    store=False
)

# Retrieve stored response later
stored_response = client.responses.retrieve(response.id)
```

### Context Window Management

Monitor and manage token usage to stay within context limits:

```python
import tiktoken

def count_tokens(text, model="gpt-4o"):
    """Count tokens for a given text"""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def estimate_conversation_tokens(history):
    """Estimate total tokens in conversation"""
    total = 0
    for message in history:
        if isinstance(message, dict):
            content = message.get("content", "")
        else:
            content = str(message)
        total += count_tokens(content)
    return total

# Check before sending
history = [...]
token_count = estimate_conversation_tokens(history)
print(f"Estimated tokens: {token_count}")

# Model context windows:
# gpt-4o: 128k tokens
# gpt-4o-mini: 128k tokens
# o1-preview: 128k tokens
# o1-mini: 128k tokens

if token_count > 120000:  # Leave buffer for output
    print("Warning: Approaching context limit")
    # Truncate or summarize older messages
```

### Conversation Patterns

#### Pattern 1: Continuous Assistant

Maintain ongoing context for a persistent assistant:

```python
class ConversationManager:
    def __init__(self, client, model="gpt-4o"):
        self.client = client
        self.model = model
        self.response_id = None
        
    def send(self, message):
        params = {
            "model": self.model,
            "input": message
        }
        
        if self.response_id:
            params["previous_response_id"] = self.response_id
            
        response = self.client.responses.create(**params)
        self.response_id = response.id
        return response.output_text

# Usage
manager = ConversationManager(client)
print(manager.send("What's the capital of France?"))
print(manager.send("What's its population?"))  # Knows "its" refers to Paris
print(manager.send("Tell me about its history"))  # Maintains context
```

#### Pattern 2: Branching Conversations

Create parallel conversation branches:

```python
def create_branch(client, parent_id, question):
    """Create a new conversation branch"""
    return client.responses.create(
        model="gpt-4o",
        previous_response_id=parent_id,
        input=question
    )

# Start main conversation
main = client.responses.create(
    model="gpt-4o",
    input="Explain machine learning"
)

# Create multiple branches
branches = {
    "technical": create_branch(client, main.id, "Explain the math"),
    "practical": create_branch(client, main.id, "Show me code examples"),
    "business": create_branch(client, main.id, "What's the ROI?")
}

# Continue specific branch
deep_technical = create_branch(
    client, 
    branches["technical"].id,
    "Explain backpropagation"
)
```

#### Pattern 3: Conversation Summarization

Manage long conversations by summarizing:

```python
def summarize_conversation(client, response_id):
    """Summarize a conversation branch"""
    return client.responses.create(
        model="gpt-4o-mini",
        previous_response_id=response_id,
        input="Summarize our conversation so far in 3 bullet points"
    )

def start_fresh_with_context(client, summary):
    """Start new conversation with summary context"""
    return client.responses.create(
        model="gpt-4o",
        input=[
            {"role": "system", "content": f"Previous conversation summary: {summary}"},
            {"role": "user", "content": "Let's continue our discussion"}
        ]
    )
```

### Best Practices

1. **Use `previous_response_id` for simple flows** - Easier and cleaner for linear conversations
2. **Manual management for complex scenarios** - When you need branching, editing, or selective context
3. **Monitor token usage** - Track usage to avoid context limit issues
4. **Set `store=False` for sensitive data** - Prevent retention of private information
5. **Implement conversation pruning** - Remove old messages or summarize to stay within limits
6. **Use appropriate models** - Larger context windows for long conversations
7. **Handle errors gracefully** - Check for truncated responses or context errors

### Example: Customer Support Bot

```python
class SupportBot:
    def __init__(self, client):
        self.client = client
        self.conversation_id = None
        self.message_count = 0
        
    def handle_message(self, user_message):
        self.message_count += 1
        
        # First message - include system context
        if not self.conversation_id:
            response = self.client.responses.create(
                model="gpt-4o",
                instructions="You are a helpful customer support agent.",
                input=user_message
            )
        else:
            response = self.client.responses.create(
                model="gpt-4o",
                previous_response_id=self.conversation_id,
                input=user_message
            )
        
        self.conversation_id = response.id
        
        # Summarize and reset after 20 messages to manage context
        if self.message_count >= 20:
            summary = self._summarize_conversation()
            self._reset_with_summary(summary)
            
        return response.output_text
    
    def _summarize_conversation(self):
        summary_response = self.client.responses.create(
            model="gpt-4o-mini",
            previous_response_id=self.conversation_id,
            input="Summarize the key points and any unresolved issues from our conversation"
        )
        return summary_response.output_text
    
    def _reset_with_summary(self, summary):
        self.conversation_id = None
        self.message_count = 0
        # Next message will include summary in system context

# Usage
bot = SupportBot(client)
print(bot.handle_message("I can't login to my account"))
print(bot.handle_message("I've tried resetting my password"))
print(bot.handle_message("The reset email never arrives"))
```

## Important Notes

- Requires latest OpenAI Python library (`pip install --upgrade openai`)
- The Responses API is the recommended approach for new applications
- Chat Completions API remains supported but Responses API offers more features
- MCP integration requires MCP servers to be installed and accessible
- Structured Outputs requires specific model versions (gpt-4o-mini, gpt-4o-2024-08-06, or later)
- Function calling with strict mode provides reliable schema adherence
- Response objects are retained for 30 days when `store=True` (default)
- All tokens in conversation chains count toward billing, even with `previous_response_id`

Remember: This is OpenAI's newest and most powerful API. Always use `client.responses.create()` instead of older patterns.