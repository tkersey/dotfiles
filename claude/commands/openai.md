# OpenAI API Responses: Complete Technical Reference

## OpenAI's unified Responses API

OpenAI has introduced a new Responses API that combines features from Chat Completions and Assistants APIs, representing a significant evolution in API design. This stateful API maintains conversation context across interactions while providing built-in tools for web search, file search, and computer use capabilities. The API supports multimodal inputs including text, audio, and images, while simplifying orchestration compared to previous implementations.

## Response structure and core fields

The basic response object from OpenAI's API contains several key fields that developers need to understand. Each response includes a unique **`id`** identifier (formatted as "resp\_" followed by a hash), an **`object`** field indicating the response type, and the **`model`** field showing which model generated the response. The **`created`** timestamp tracks when the response was generated, while the **`choices`** array contains the actual generated completions.

**Python example:**

```python
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)

# Accessing response fields
print(response.id)  # "resp_abc123..."
print(response.choices[0].message.content)
print(response.usage.total_tokens)
```

**TypeScript example:**

```typescript
const response = await client.chat.completions.create({
  model: "gpt-4",
  messages: [{ role: "user", content: "Hello" }],
});

// Accessing response fields
console.log(response.id); // "resp_abc123..."
console.log(response.choices[0].message.content);
console.log(response.usage.total_tokens);
```

Within the choices array, each choice object contains an **`index`** indicating its position, a **`message`** object with `role` and `content` fields, and a **`finish_reason`** explaining why generation stopped (typically "stop", "length", or "tool_calls"). The response also includes **`usage`** statistics showing token consumption broken down by input tokens, output tokens, and total tokens used.

## Response format options and structured outputs

OpenAI supports three primary response formats that developers can specify. The default text response returns unstructured text content. For applications requiring structured data, developers can request **JSON object responses** by setting `response_format` to `{"type": "json_object"}`. The most powerful option is **structured outputs using JSON Schema**, which allows precise control over the response structure:

**Python:**

```python
response_format={
    "type": "json_schema",
    "json_schema": {
        "name": "schema_name",
        "strict": True,
        "schema": {...}
    }
}
```

**TypeScript:**

```typescript
response_format: {
    type: "json_schema",
    json_schema: {
        name: "schema_name",
        strict: true,
        schema: {...}
    }
}
```

When using structured outputs, certain constraints apply: root objects cannot use `anyOf` types, all fields must be marked as required, and the system supports only a subset of the JSON Schema specification. Setting `strict: true` ensures exact schema adherence.

## HTTP status codes and error handling architecture

The API uses standard HTTP status codes to indicate request outcomes. A **200** status indicates success, while **400** signals bad requests with invalid parameters. Authentication failures return **401**, permission issues generate **403**, and **404** indicates invalid endpoints. Rate limiting triggers **429** responses, and server errors produce **500** status codes.

Error responses follow a consistent structure containing an **`error`** object with four key fields: `message` provides human-readable error descriptions, `type` categorizes the error (such as "invalid_request_error"), `param` identifies problematic parameters when applicable, and `code` supplies machine-readable error identifiers.

**Python error handling:**

```python
from openai import OpenAI, APIError, RateLimitError, APIConnectionError

client = OpenAI()

try:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello"}]
    )
except RateLimitError as e:
    print(f"Rate limit exceeded: {e.message}")
    # Implement exponential backoff
except APIConnectionError as e:
    print(f"Connection error: {e.message}")
    # Retry with backoff
except APIError as e:
    print(f"API error: {e.message}, Status: {e.status_code}")
```

**TypeScript error handling:**

```typescript
import OpenAI from "openai";
import { APIError, RateLimitError, APIConnectionError } from "openai/error";

const client = new OpenAI();

try {
  const response = await client.chat.completions.create({
    model: "gpt-4",
    messages: [{ role: "user", content: "Hello" }],
  });
} catch (error) {
  if (error instanceof RateLimitError) {
    console.error(`Rate limit exceeded: ${error.message}`);
    // Implement exponential backoff
  } else if (error instanceof APIConnectionError) {
    console.error(`Connection error: ${error.message}`);
    // Retry with backoff
  } else if (error instanceof APIError) {
    console.error(`API error: ${error.message}, Status: ${error.status}`);
  }
}
```

Common error types include `APIConnectionError` for connectivity issues, `RateLimitError` for quota exceeded, `APIStatusError` for non-200 responses, and `BadRequestError` for malformed requests.

## Rate limiting headers and monitoring

OpenAI implements sophisticated rate limiting tracked through response headers. The **`x-ratelimit-limit-requests`** and **`x-ratelimit-limit-tokens`** headers show maximum allowed requests and tokens per time window. Current availability is tracked via **`x-ratelimit-remaining-requests`** and **`x-ratelimit-remaining-tokens`**, while **`x-ratelimit-reset-requests`** and **`x-ratelimit-reset-tokens`** indicate when limits reset.

Developers can access these headers through raw response objects:

**Python:**

```python
raw_response = client.responses.with_raw_response.create(...)
remaining_tokens = raw_response.headers.get('x-ratelimit-remaining-tokens')
```

**TypeScript:**

```typescript
const rawResponse = await client.responses.withResponse().create(...);
const remainingTokens = rawResponse.headers['x-ratelimit-remaining-tokens'];
```

## Streaming responses for real-time applications

For applications requiring incremental output, OpenAI supports streaming responses. By setting `stream=True`, developers receive response chunks as they're generated rather than waiting for completion. This works with both synchronous and asynchronous implementations, enabling real-time user interfaces and reducing perceived latency for long generations.

**Python example:**

```python
# Synchronous streaming
stream = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")

# Asynchronous streaming
async def stream_response():
    stream = await client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Tell me a story"}],
        stream=True
    )

    async for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="")
```

**TypeScript example:**

```typescript
// Streaming response
const stream = await client.chat.completions.create({
  model: "gpt-4",
  messages: [{ role: "user", content: "Tell me a story" }],
  stream: true,
});

for await (const chunk of stream) {
  const content = chunk.choices[0]?.delta?.content;
  if (content) {
    process.stdout.write(content);
  }
}

// Alternative using event handlers
const stream = await client.beta.chat.completions.stream({
  model: "gpt-4",
  messages: [{ role: "user", content: "Tell me a story" }],
});

stream.on("content", (delta, snapshot) => {
  process.stdout.write(delta);
});

const finalResponse = await stream.finalChatCompletion();
```

## Tool integration and function calling

The Responses API includes built-in tools that extend model capabilities. **Web search** enables real-time information retrieval, **file search** processes uploaded documents, **computer use** allows interface interactions, and **code interpreter** executes and analyzes code. When models determine tool use is needed, responses include tool calls with structured parameters that applications must handle and respond to appropriately.

**Python tool handling:**

```python
# Define a function tool
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string"}
            },
            "required": ["location"]
        }
    }
}]

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
    tools=tools,
    tool_choice="auto"
)

# Handle tool calls
if response.choices[0].finish_reason == "tool_calls":
    tool_calls = response.choices[0].message.tool_calls
    for tool_call in tool_calls:
        if tool_call.function.name == "get_weather":
            # Execute function and return result
            weather_data = get_weather(tool_call.function.arguments)
```

**TypeScript tool handling:**

```typescript
// Define a function tool
const tools = [
  {
    type: "function" as const,
    function: {
      name: "get_weather",
      description: "Get current weather",
      parameters: {
        type: "object",
        properties: {
          location: { type: "string" },
        },
        required: ["location"],
      },
    },
  },
];

const response = await client.chat.completions.create({
  model: "gpt-4",
  messages: [{ role: "user", content: "What's the weather in Paris?" }],
  tools: tools,
  tool_choice: "auto",
});

// Handle tool calls
if (response.choices[0].finish_reason === "tool_calls") {
  const toolCalls = response.choices[0].message.tool_calls;
  for (const toolCall of toolCalls) {
    if (toolCall.function.name === "get_weather") {
      // Execute function and return result
      const weatherData = await getWeather(toolCall.function.arguments);
    }
  }
}
```

## Multimodal capabilities and content handling

The API processes multiple input types through a unified interface. Image inputs are specified using `input_image` content types with URLs or base64-encoded data. Text and images can be combined in single requests, enabling sophisticated multimodal applications. Response handling remains consistent regardless of input modality, simplifying implementation.

**Python multimodal example:**

```python
# Image with text input
response = client.chat.completions.create(
    model="gpt-4-vision-preview",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "What's in this image?"},
            {
                "type": "image_url",
                "image_url": {
                    "url": "https://example.com/image.jpg",
                    "detail": "high"  # "low", "high", or "auto"
                }
            }
        ]
    }]
)

# Base64 encoded image
import base64

with open("image.jpg", "rb") as image_file:
    base64_image = base64.b64encode(image_file.read()).decode('utf-8')

response = client.chat.completions.create(
    model="gpt-4-vision-preview",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "Describe this image"},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            }
        ]
    }]
)
```

**TypeScript multimodal example:**

```typescript
// Image with text input
const response = await client.chat.completions.create({
  model: "gpt-4-vision-preview",
  messages: [
    {
      role: "user",
      content: [
        { type: "text", text: "What's in this image?" },
        {
          type: "image_url",
          image_url: {
            url: "https://example.com/image.jpg",
            detail: "high", // "low", "high", or "auto"
          },
        },
      ],
    },
  ],
});

// Base64 encoded image
import * as fs from "fs";

const imageBuffer = fs.readFileSync("image.jpg");
const base64Image = imageBuffer.toString("base64");

const response = await client.chat.completions.create({
  model: "gpt-4-vision-preview",
  messages: [
    {
      role: "user",
      content: [
        { type: "text", text: "Describe this image" },
        {
          type: "image_url",
          image_url: {
            url: `data:image/jpeg;base64,${base64Image}`,
          },
        },
      ],
    },
  ],
});
```

## Response metadata and diagnostic information

Beyond the primary content, responses include valuable metadata. The **`response_metadata`** field contains model-specific information, while **`system_fingerprint`** identifies the exact model configuration used. Token usage breakdowns help monitor costs and optimize prompts. The **`finish_reason`** field provides insights into why generation stopped, crucial for debugging truncated outputs.

## Best practices for production implementations

Successful API integration requires careful attention to several areas. **Error handling** should include try-catch blocks with appropriate retry logic for transient failures. **Rate limit monitoring** prevents service disruptions by tracking usage through response headers. **Structured outputs** ensure consistent data formats crucial for downstream processing. **Security practices** mandate storing API keys in environment variables, never in code. For optimal performance, implement request pooling, connection reuse, and appropriate timeout configurations.

## Migration path and deprecation timeline

OpenAI has deprecated the Assistants API, which will cease functioning in the first half of 2026. The Responses API serves as the replacement, offering improved functionality and simplified implementation. Developers should begin migration promptly to avoid service disruptions. The new API's unified approach reduces code complexity while providing more powerful capabilities, making migration beneficial beyond mere compliance.

This comprehensive reference covers the essential technical details developers need when working with OpenAI API responses. The combination of structured outputs, streaming capabilities, multimodal support, and integrated tools provides a powerful foundation for building sophisticated AI applications.
