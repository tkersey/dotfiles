theme: Franziska
footer: OpenAI Agents JS SDK - Technical Deep Dive
slidenumbers: true
autoscale: true

# OpenAI Agents JS SDK

## [fit] Multi-Agent Orchestration at Scale

---

# Start Simple

```typescript
import { Agent, run } from '@openai/agents';

const agent = new Agent({
  name: 'Assistant',
  instructions: 'You are a helpful agent',
});

const result = await run(agent, 'What is the capital of France?');

console.log(result.finalOutput);
// "The capital of France is Paris."
```

^ Zero configuration to get started. Just an agent and a prompt.

---

# Add a Tool

```typescript
import { Agent, run, tool } from '@openai/agents';

const getWeather = tool({
  name: 'get_weather',
  description: 'Get the weather for a city',
  parameters: { city: 'string' }, // Simple schema
  execute: async ({ city }) => {
    return {
      city,
      temperature: '20°C',
      conditions: 'Sunny',
    };
  },
});

const agent = new Agent({
  name: 'Weather Assistant',
  instructions: 'Help users with weather information',
  tools: [getWeather],
});
```

^ Tools extend agent capabilities. Execute functions based on user needs.

---

# Running the Agent

```typescript
async function main() {
  const result = await run(agent, "What's the weather in Tokyo?");

  console.log(result.finalOutput);
  // "The weather in Tokyo is sunny with a
  //  temperature of 20°C."

  // Inspect what happened
  console.log(result.toolCalls);
  // [{ name: 'get_weather', arguments: { city: 'Tokyo' } }]

  console.log(result.usage);
  // { inputTokens: 45, outputTokens: 23, totalTokens: 68 }
}
```

^ The agent automatically calls tools when needed. Full observability included.

---

[.text: alignment(center)]

# Tools & Functions

---

# Tool System Architecture

[.build-lists: true]

- **Function Tools**: Local execution with Zod validation
- **Hosted Tools**: OpenAI server-side execution
- **MCP Tools**: Model Context Protocol servers
- **Agent Tools**: Recursive composition

^ Extensible tool system. New tool types can be added.

---

# Forcing Tool Use: tool_choice

```typescript
import { Agent, run } from '@openai/agents';

const agent = new Agent({
  name: 'DataAnalyst',
  tools: [queryTool, analyzeTool, reportTool],
});

// Option 1: Auto (default) - Model decides
await run(agent, 'Analyze sales', {
  modelSettings: { toolChoice: 'auto' },
});

// Option 2: Required - Must use SOME tool
await run(agent, 'Analyze sales', {
  modelSettings: { toolChoice: 'required' },
});

// Option 3: None - Prevent ALL tool use
await run(agent, 'Just explain the process', {
  modelSettings: { toolChoice: 'none' },
});

// Option 4: Specific tool - Force exact tool
await run(agent, 'Get the data', {
  modelSettings: { toolChoice: 'queryTool' },
});
```

^ Control exactly when and which tools are used

---

# tool_choice: What It Controls

```typescript
// tool_choice works with ALL tool types:

const agent = new Agent({
  tools: [
    // Function tools (local execution)
    tool({ name: 'calculate', execute: async () => {...} }),

    // MCP tools from local servers
    mcpServer,

    // Hosted MCP tools (OpenAI-side)
    hostedMcpTool({ serverLabel: 'data-api' }),

    // Agents as tools
    specialistAgent,
  ],
});

// tool_choice applies to ALL of them:
await run(agent, input, {
  modelSettings: {
    toolChoice: 'required',     // Must use SOME tool
    toolChoice: 'calculate',     // Force function tool
    toolChoice: 'transfer_to_specialist', // Force handoff
    // Note: Individual MCP tools can't be forced by name
    // (MCP server decides which of its tools to use)
  },
});
```

^ tool_choice is universal BUT MCP tools are grouped by server

---

# tool_choice Patterns

```typescript
// Pattern 1: Force tool on first turn only
const result = await run(agent, input, {
  modelSettings: {
    toolChoice: messages.length === 0 ? 'required' : 'auto'
  },
});

// Pattern 2: Prevent tool loops
const agent = new Agent({
  tools: [recursiveTool],
  maxTurns: 5,
});

await run(agent, input, {
  // Disable tools after 3 turns to prevent infinite loops
  modelSettings: {
    toolChoice: turn > 3 ? 'none' : 'auto'
  },
});

// Pattern 3: Sequential tool enforcement
const steps = ['gather_data', 'analyze', 'generate_report'];
for (const toolName of steps) {
  await run(agent, `Step: ${toolName}`, {
    modelSettings: { toolChoice: toolName },
  });
}
```

^ Advanced patterns for controlled tool execution

---

# Parallel Tool Calls

```typescript
// Enable parallel tool execution
const agent = new Agent({
  name: 'EfficientAnalyst',
  tools: [fetchUserData, fetchOrders, fetchInventory, computeMetrics],
});

// Allow model to call multiple tools in one turn
const result = await run(agent, 'Get all customer data and metrics', {
  modelSettings: {
    parallelToolCalls: true, // Default: false
    toolChoice: 'required',
  },
});

// Model might call all four tools simultaneously:
// Turn 1: [fetchUserData, fetchOrders, fetchInventory, computeMetrics]
// All execute in parallel, results returned together

// Without parallel calls (default):
await run(agent, 'Get all customer data and metrics', {
  modelSettings: {
    parallelToolCalls: false,
  },
});
// Turn 1: fetchUserData
// Turn 2: fetchOrders
// Turn 3: fetchInventory
// Turn 4: computeMetrics
// Much slower, but more controlled
```

^ Parallel tools = faster execution, fewer turns

---

# Function Tool: Zod Schema Validation

```typescript
const analyticsTool = tool({
  name: 'analyze_metrics',
  parameters: z.object({
    metric: z.enum(['revenue', 'users', 'churn']),
    timeframe: z.string().regex(/^\d{4}-\d{2}$/),
    segments: z.array(z.string()).optional(),
  }),
  strict: true, // Enforce schema compliance
  execute: async (input, context) => {
    // input is fully typed from Zod schema
    // TypeScript knows: input.metric is 'revenue' | 'users' | 'churn'
    return computeMetrics(input, context.database);
  },
});
```

^ Zod provides runtime validation AND TypeScript types

---

# Tool Error Handling

```typescript
const resilientTool = tool({
  name: 'external_api',
  parameters: z.object({ query: z.string() }),
  execute: async (input, context) => {
    try {
      return await externalAPI.query(input.query);
    } catch (error) {
      if (error.code === 'RATE_LIMIT') {
        // Return structured error for agent to understand
        return {
          error: 'Rate limited. Please try again in 60 seconds.',
          retryAfter: 60,
        };
      }
      // Re-throw unexpected errors
      throw error;
    }
  },
});
```

^ Tools should handle expected errors, re-throw unexpected ones

---

# Tool Composition Strategies

```typescript
// Sequential composition
const pipelineTool = tool({
  name: 'data_pipeline',
  parameters: z.object({
    data: z.any(),
  }),
  execute: async (input, context) => {
    const extracted = await extractTool.execute(input, context);
    const transformed = await transformTool.execute(extracted, context);
    const loaded = await loadTool.execute(transformed, context);
    return loaded;
  },
});

// Parallel composition
const aggregateTool = tool({
  name: 'aggregate_sources',
  parameters: z.object({
    query: z.string(),
  }),
  execute: async (input, context) => {
    const [db, api, cache] = await Promise.all([
      dbTool.execute(input, context),
      apiTool.execute(input, context),
      cacheTool.execute(input, context),
    ]);
    return mergeResults(db, api, cache);
  },
});
```

^ Tools can orchestrate other tools for complex operations

---

# [fit] Hosted Tools:<br>Server-Side Execution

## [fit] **Run on OpenAI infrastructure,<br>not your code**

---

## **Run on OpenAI infrastructure, not your code**

```typescript
import {
  webSearchTool,
  fileSearchTool,
  codeInterpreterTool,
} from '@openai/agents';

const agent = new Agent({
  tools: [
    // Web Search - Internet search capabilities
    webSearchTool({
      maxResults: 5,
      locationBias: 'us',
      blockedDomains: ['example.com'],
    }),

    // File Search - Query OpenAI vector stores
    fileSearchTool({
      vectorStoreId: 'vs_abc123',
      maxResults: 10,
    }),

    // Code Interpreter - Sandboxed code execution
    codeInterpreterTool({
      containerOptions: { memory: '512MB' },
    }),
  ],
});
```

^ No round-trips to your app. Execute directly on OpenAI servers.

---

[.text: alignment(center)]

# Function Calling

---

# Function Calling: Native Tools

## **Direct code execution in your process**

```typescript
const calculateTax = tool({
  name: 'calculate_tax',
  description: 'Calculate tax for a transaction',
  parameters: z.object({
    amount: z.number(),
    state: z.string(),
    category: z.enum(['sales', 'income', 'property']),
  }),
  execute: async ({ amount, state, category }, context) => {
    // Your code runs directly in the same process
    const rate = await context.taxService.getRate(state, category);
    const tax = amount * rate;
    await context.database.logCalculation({ amount, state, tax });
    return { tax, rate, total: amount + tax };
  },
});
```

^ Function tools are YOUR code running in YOUR process with full control.

---

# Function Calling: Benefits

## **Why use function calling:**

✅ **Full control** - Your code, your logic
✅ **Direct access** - Database, APIs, file system
✅ **Type safety** - TypeScript + Zod validation
✅ **Synchronous** - Immediate execution
✅ **Debugging** - Set breakpoints, inspect state
✅ **Performance** - No network overhead
✅ **Security** - Runs in your security context

---

[.text: alignment(center)]

# MCP

---

# MCP: Model Context Protocol

## SDK Version & Specification Support

```typescript
// packages/agents-core/package.json
"@modelcontextprotocol/sdk": "^1.17.2"

// Version Details
✅ MCP SDK 1.17.2 (Released: August 7, 2025)
✅ JSON-RPC 2.0 protocol
✅ Tool discovery & execution
✅ Multiple transport protocols
✅ OAuth authentication (HTTP/SSE)
✅ Tool filtering & caching
✅ Session management
✅ Node.js 18+ required

// Transport Support
const transports = {
  stdio: MCPServerStdio,        // Local processes
  sse: MCPServerSSE,            // Server-sent events
  http: MCPServerStreamableHttp, // HTTP streaming
  hosted: HostedMCPTool,        // OpenAI connects to remote MCP servers
};
```

^ Full MCP 1.17.2 specification support with all transport protocols

---

# MCP: Three Server Types

```typescript
import {
  MCPServerStdio,
  MCPServerSSE,
  MCPServerStreamableHttp,
} from '@openai/agents';

// 1. Stdio - Local process communication
const stdioServer = new MCPServerStdio({
  name: 'GitHub MCP Server',
  fullCommand: 'npx -y @modelcontextprotocol/server-github',
  env: { GITHUB_TOKEN: process.env.GITHUB_TOKEN },
});
await stdioServer.connect();

// 2. SSE - Server-Sent Events
const sseServer = new MCPServerSSE({
  name: 'Remote MCP',
  url: 'https://api.example.com/mcp/sse',
});
await sseServer.connect();

// 3. Streamable HTTP (Request/Response)
const httpServer = new MCPServerStreamableHttp({
  name: 'HTTP MCP',
  url: 'https://api.example.com/mcp',
});
await httpServer.connect();
```

^ MCP supports multiple transport protocols for different use cases

---

# MCP: Hosted MCP Tools Explained

```typescript
// HostedMCPTool doesn't mean "hosted by OpenAI"
// It means "OpenAI connects to YOUR hosted MCP server"

const hostedTool = hostedMcpTool({
  server_url: 'https://your-server.com/mcp', // YOUR server
  server_label: 'My MCP Server',
  authorization: { type: 'bearer', token: 'your-token' },
});

// Flow:
// 1. Agent needs tool → 2. OpenAI calls YOUR server
// 3. YOUR server executes → 4. OpenAI relays result back

// Compare with local MCP:
const localMCP = new MCPServerStdio({...}); // Runs on YOUR machine
const hostedMCP = hostedMcpTool({...});      // Runs on YOUR server
// Both execute on YOUR infrastructure, not OpenAI's
```

^ HostedMCPTool = OpenAI connects to YOUR remote MCP server, not OpenAI hosting

---

# MCP: Tool Discovery Protocol

```typescript
// MCP servers expose tools dynamically
const agent = new Agent({
  mcpServers: [githubMCP, filesystemMCP],
  // Tools are discovered at runtime
});

// Get all available MCP tools
const tools = await agent.getMcpTools(context);
console.log(tools);
// [
//   { name: 'github_create_issue', parameters: {...} },
//   { name: 'fs_read_file', parameters: {...} },
//   ...
// ]
```

^ MCP tools are discovered dynamically, not hardcoded

---

# Function Calling vs MCP

## **When to use each approach:**

[.column]
**Function Calling**
**Best for:** Core application logic

✅ Your business logic
✅ Database operations
✅ Internal APIs
✅ Custom algorithms
✅ Sensitive operations
✅ Need debugging
✅ Performance critical

[.column]
**MCP**
**Best for:** External integrations

✅ Third-party tools
✅ Community tools
✅ Standalone services
✅ Language agnostic
✅ Shared capabilities
✅ Desktop integrations
✅ Standardized tools

^ Function calling for YOUR code. MCP for EXTERNAL tools.

---

# Function Calling vs MCP: Technical

| Aspect          | Function Calling     | MCP                      |
| --------------- | -------------------- | ------------------------ |
| **Execution**   | In-process           | Separate process/network |
| **Performance** | Fast (no overhead)   | Network latency          |
| **Debugging**   | Direct (breakpoints) | Remote (logs)            |
| **Type Safety** | Full TypeScript      | Schema-based             |
| **Access**      | Everything in app    | Limited to MCP API       |
| **State**       | Shared context       | Isolated                 |
| **Deployment**  | With your app        | Separate service         |
| **Updates**     | Redeploy app         | Update MCP server        |

^ Function calling is tightly integrated. MCP is loosely coupled.

---

# Combining Both Approaches

```typescript
const agent = new Agent({
  // Core business logic as function tools
  tools: [
    calculatePricingTool, // Your pricing algorithm
    updateInventoryTool, // Your database operations
    sendNotificationTool, // Your notification system
  ],

  // External capabilities via MCP
  mcpServers: [
    githubMCP, // GitHub operations
    slackMCP, // Slack integration
    filesystemMCP, // File operations
  ],
});

// The agent can use both seamlessly
// "Calculate the price, update inventory, create a GitHub issue,
//  and notify the team on Slack"
```

^ Use both! Function tools for core logic, MCP for external services.

---

[.text: alignment(center)]

# Context Management

---

# [fit] Context Management Deep Dive

## Two-Layer Context System

```typescript
// Layer 1: Local Context (RunContext) - YOUR application state
class RunContext<TContext> {
  context: TContext; // Mutable shared state
  usage: Usage; // Token/cost tracking
  #approvals: Map<string, ApprovalRecord>; // HITL state
}

// Layer 2: Agent/LLM Context - Conversation history
type AgentContext = ModelItem[]; // Messages, tool calls, responses
```

^ Two distinct contexts serve different purposes. Local = infrastructure. Agent = conversation.

---

# Local Context: Infrastructure & Services

```typescript
interface LocalContext {
  // 🔌 External Services
  database: PostgresClient;
  redis: RedisCache;
  elasticsearch: SearchClient;
  stripe: StripeAPI;
  sendgrid: EmailService;
  twilio: SMSService;

  // 🔐 Authentication & Session
  user: { id: string; tier: 'free' | 'pro'; permissions: string[] };
  apiKeys: { openai: string; anthropic: string };
  sessionId: string;
  requestId: string;

  // 🚦 Rate Limiting & Circuit Breakers
  rateLimiter: RateLimiter;
  circuitBreaker: CircuitBreaker;

  // 📊 Observability
  logger: Logger;
  metrics: MetricsCollector;
  tracer: TracingSpan;
}
```

^ Local context holds everything tools need to do their job. Shared across all tools.

---

# Local Context: Application State

```typescript
interface LocalContext {
  // 🛒 Transaction State
  cart: ShoppingCart;
  order: Order;
  payment: PaymentTransaction;

  // 🧮 Computation State
  calculationCache: Map<string, Result>;
  tempFiles: TempFileManager;
  batchProcessor: BatchJob;

  // 🎯 Feature Flags & Config
  features: FeatureFlags;
  config: AppConfig;
  experiments: ABTestManager;

  // 🔄 Cross-Agent Shared State
  workflow: WorkflowState;
  conversationSummary: string;
  decisions: Decision[];
  accumulatedData: any[];
}
```

^ Local context maintains state that persists across tool calls and agent handoffs.

---

# Agent/LLM Context: Conversation History

```typescript
type AgentContext = Array<
  | { role: 'system'; content: string } // Instructions
  | { role: 'user'; content: string } // User messages
  | { role: 'assistant'; content: string } // Agent responses
  | { role: 'tool'; name: string; result: any } // Tool outputs
  | { role: 'handoff'; from: string; to: string } // Agent transfers
  | { role: 'error'; error: string } // Errors
  | { role: 'reasoning'; thought: string } // Chain-of-thought
>;
```

^ Agent context is what the LLM "sees" - the conversation that guides its decisions.

---

# Why Two Contexts?

## **Key Insight**

### Local Context = Infrastructure (Never sent to LLM)

### Agent Context = Conversation (What the LLM sees)

[.column]
**Local Context**
✓ Persists across agents
✓ Mutable by tools
✓ **Never sent to LLM** ⚠️
✓ Contains secrets
✓ Holds connections
✓ Tracks metrics

[.column]
**Agent Context**
✓ **Sent to LLM** 🧠
✓ Can be filtered
✓ Size-limited
✓ No secrets
✓ Natural language
✓ Guides reasoning

^ **Critical distinction**: Local = your app's plumbing. Agent = the LLM's memory.

---

# Context Usage in Tools

```typescript
const processPayment = tool({
  name: 'process_payment',
  execute: async (input, context: LocalContext) => {
    // Use local context services
    const user = context.user
    const stripe = context.stripe
    const logger = context.logger
    const metrics = context.metrics

    // Check rate limits
    if (!await context.rateLimiter.check(user.id)) {
      throw new Error('Rate limit exceeded')
    }

    // Process with circuit breaker
    const result = await context.circuitBreaker.run(async () => {
      const charge = await stripe.charges.create({...})
      await logger.info('Payment processed', { charge })
      await metrics.increment('payments.success')
      return charge
    })

    // Update shared state
    context.order.paymentId = result.id
    return result
  }
})
```

^ Tools leverage local context for all infrastructure needs.

---

# SDK Context Management Recommendations

## **The SDK's design philosophy for context:**

[.column]
**Local Context (RunContext)**
✅ Infrastructure & services
✅ Database connections
✅ User session data
✅ Shared mutable state
✅ Secrets & API keys
❌ Never sent to LLM

[.column]
**Agent Context**
✅ Conversation history
✅ User messages
✅ Tool outputs
✅ Handoff records
❌ No infrastructure
✅ Sent to LLM

^ SDK philosophy: Clear separation of concerns. Infrastructure vs conversation.

---

# Context + Responses API

## Triple-Layer Architecture

```typescript
// With Responses API enabled (default), context becomes triple-layered:

// Layer 1: Local Context (RunContext) - Client-side state
const localContext = {
  database: pgClient,
  user: currentUser,
  // Never sent to API
};

// Layer 2: Server Context - OpenAI's stored conversation state
const serverContext = {
  previousResponseId: 'resp_abc123...', // Links to full history
  conversationId: 'conv_xyz789...', // Thread identifier
  // Stored on OpenAI servers, not transmitted
};

// Layer 3: Request Payload - What's actually sent
const requestPayload = {
  input: newMessages, // Only NEW messages
  previous_response_id: serverContext.previousResponseId,
  // 80%+ smaller than sending full history
};
```

^ Responses API adds server-side context layer, dramatically reducing payload size

---

# How Responses API Changes<br>Context Flow

```typescript
// FIRST TURN - No previous context
const turn1 = await run(agent, 'Explain quantum computing', {
  context: { user: 'alice' }, // Local context
});
// Sends: Full input to API
// Returns: response_id for future reference

// SUBSEQUENT TURNS - References server state
const turn2 = await run(agent, 'How does it differ from classical?', {
  context: { user: 'alice' }, // Same local context
  previousResponseId: turn1.lastResponseId, // Links server conversation
});
// Sends: Only new message + previousResponseId
// Server retrieves and appends to stored conversation

// HANDOFF - Maintains both contexts
const turn3 = await run(agent, 'Let me transfer you to our expert', {
  context: { user: 'alice' }, // Local context persists
  previousResponseId: turn2.lastResponseId, // Server thread continues
});
// Handoff inherits both local context AND server conversation thread
```

^ Server maintains conversation history, client maintains application state

---

# Context Management Best Practices with Responses API

[.column]
**What Stays Local**

✅ Infrastructure
✅ Secrets & keys
✅ Mutable state
✅ Tool dependencies

```typescript
// Never sent, always available
context: {
  connections: {...},
  secrets: {...},
  session: {...},
  cache: {...}
}
```

[.column]
**What Goes to Server**

✅ Message history
✅ Tool results
✅ Agent responses
✅ Automatically managed

```typescript
// Via previousResponseId
{
  (conversation_history, tool_outputs, handoff_records, reasoning_traces);
}
```

^ Responses API handles conversation persistence, you handle application state

---

[.text: alignment(center)]

# Voice-Based Agents

---

# Voice Agents: Introduction

```typescript
import { RealtimeAgent, RealtimeSession } from '@openai/agents-realtime';
import { z } from 'zod';
import { tool } from '@openai/agents';

const weatherTool = tool({
  name: 'get_weather',
  description: 'Get current weather',
  parameters: z.object({ city: z.string() }),
  execute: async ({ city }) => `${city}: 72°F, sunny`,
});

const voiceAgent = new RealtimeAgent({
  name: 'VoiceAssistant',
  instructions:
    'You are a helpful voice assistant. Be conversational and natural.',
  tools: [weatherTool],
  voice: 'alloy', // Options: alloy, echo, shimmer, nova
  model: 'gpt-4o-realtime-preview',
});
```

^ RealtimeAgent enables natural voice conversations with tool calling

---

# Voice Agents: Browser Implementation

```typescript
// Browser-side code (React/Next.js example)
import { RealtimeSession } from '@openai/agents-realtime';

export function VoiceChat() {
  const [session, setSession] = useState<RealtimeSession>();

  async function startConversation() {
    // Get ephemeral token from your backend
    const { apiKey } = await fetch('/api/realtime-token').then(r => r.json());

    const session = new RealtimeSession(agent);

    // Connect and auto-configure audio I/O
    await session.connect({ apiKey });

    // Session now handles:
    // ✅ Microphone input
    // ✅ Speaker output
    // ✅ Turn detection
    // ✅ Audio streaming

    setSession(session);
  }

  return <button onClick={startConversation}>Start Voice Chat</button>;
}
```

^ Browser SDK handles all audio I/O automatically

---

# Voice Agents: Transport Options

```typescript
// Option 1: WebRTC (Lowest latency, recommended)
const webrtcSession = new RealtimeSession(agent, {
  transport: 'webrtc',
  config: {
    iceServers: [{ urls: 'stun:stun.l.google.com:19302' }],
    enableDataChannel: true, // For tool results
  },
});

// Option 2: WebSocket (Simpler, good compatibility)
const wsSession = new RealtimeSession(agent, {
  transport: 'websocket',
  url: 'wss://api.openai.com/v1/realtime',
});

// Performance comparison:
// WebRTC:    ~100ms latency, P2P capable
// WebSocket: ~200ms latency, simpler firewall traversal
```

^ Choose WebRTC for lowest latency, WebSocket for simplicity

---

# Voice Agents: Audio Configuration

```typescript
// Agent configuration (simple)
const agent = new RealtimeAgent({
  name: 'AudioOptimized',
  instructions: 'You are a helpful voice assistant',
  voice: 'alloy', // Voice selection
  tools: [weatherTool],
});

// Session configuration (detailed audio settings)
const session = new RealtimeSession(agent, {
  // Turn detection configuration
  turnDetection: {
    type: 'server_vad', // Voice Activity Detection
    threshold: 0.5, // Sensitivity (0-1)
    prefixPaddingMs: 300, // Keep audio before speech
    silenceDurationMs: 500, // Pause = end of turn
  },

  // Audio format configuration
  inputAudioFormat: 'pcm16', // Options: pcm16, g711_ulaw, g711_alaw
  outputAudioFormat: 'pcm16',
  inputAudioTranscription: {
    model: 'whisper-1', // For debugging/logs
  },

  modalities: ['text', 'audio'], // Both supported
});
```

^ Agent defines behavior, Session handles audio configuration

---

# Voice Agents: Interruption Handling

```typescript
const agent = new RealtimeAgent({
  // Allow user interruption mid-response
  interruptions: true,

  instructions: `
    You are having a natural conversation.
    If interrupted, gracefully stop and listen.
    Don't repeat yourself after interruptions.
  `,
});

// Handle interruption events
session.on('interruption', (event) => {
  console.log('User interrupted at:', event.timestamp);
  // Agent automatically stops speaking
  // Listening resumes immediately
});

// Manual interruption control
session.interrupt(); // Stop agent mid-speech
session.clearAudioBuffer(); // Clear pending audio
```

^ Natural conversation flow with interruption support

---

# Voice Agents: Tool Calling in Voice

```typescript
const agent = new RealtimeAgent({
  tools: [bookingTool, searchTool],
  instructions: 'Explain what you are doing as you use tools',
});

// Tools work identically to text agents
session.on('tool_call', async (event) => {
  // Agent might say: "Let me check availability for you..."

  const result = await event.tool.execute(event.params);

  // Agent continues: "I found 3 available slots..."
  session.sendToolResult({
    toolCallId: event.id,
    result,
  });
});

// Streaming tool updates
session.on('tool_progress', (event) => {
  // Real-time progress for long-running tools
  console.log(`${event.tool}: ${event.progress}%`);
});
```

^ Tools integrate seamlessly with voice conversations

---

# Voice Agents: Multi-Modal Interactions

```typescript
// Agent that handles both voice and text
const multiModalAgent = new RealtimeAgent({
  modalities: ['text', 'audio'],
  tools: [screenshotTool, drawingTool],
});

// Voice with visual responses
session.on('tool_result', (event) => {
  if (event.tool === 'generate_chart') {
    // Display chart while agent describes it
    displayChart(event.result.imageUrl);

    // Agent says: "As you can see in the chart..."
  }
});

// Switch modalities mid-conversation
session.sendText('Show me a graph'); // Text input
// Agent responds with voice explanation + visual

session.sendAudio(audioBuffer); // Voice input
// Agent responds appropriately
```

^ Combine voice, text, and visual elements seamlessly

---

# Voice Agents: State Management

```typescript
class VoiceAgentManager {
  private sessions = new Map<string, RealtimeSession>();
  private states = new Map<string, ConversationState>();

  async createSession(userId: string): Promise<RealtimeSession> {
    // Restore previous conversation state
    const state = await this.loadState(userId);

    const agent = new RealtimeAgent({
      instructions: this.buildInstructions(state),
      context: state.context,
    });

    const session = new RealtimeSession(agent);

    // Track conversation events
    session.on('message', (msg) => {
      state.messages.push(msg);
      this.saveState(userId, state);
    });

    this.sessions.set(userId, session);
    return session;
  }

  async resumeSession(userId: string): Promise<RealtimeSession> {
    return this.sessions.get(userId) || this.createSession(userId);
  }
}
```

^ Maintain conversation continuity across sessions

---

# Voice Agents: Handoffs in Voice

```typescript
const receptionistAgent = new RealtimeAgent({
  name: 'Receptionist',
  instructions: 'Greet users and route to specialists',
  handoffs: [supportAgent, salesAgent],
});

const supportAgent = new RealtimeAgent({
  name: 'Support',
  instructions: 'Provide technical assistance',
  handoffDescription: 'Technical issues and troubleshooting',
});

// Voice handoff with context
session.on('handoff', async (event) => {
  // Receptionist: "Let me transfer you to our support team..."

  // Smooth audio transition
  await session.playTransitionSound();

  // Support: "Hi, I see you're having issues with..."
  await session.switchAgent(event.targetAgent, {
    preserveContext: true,
    announcement: 'support_greeting.mp3',
  });
});
```

^ Smooth agent transitions in voice conversations

---

# Voice Agents: Production Patterns

```typescript
// Voice agent with fallback
class ResilientVoiceAgent {
  async connect(apiKey: string) {
    try {
      // Try WebRTC first
      return await this.connectWebRTC(apiKey);
    } catch (error) {
      console.warn('WebRTC failed, falling back to WebSocket');
      return await this.connectWebSocket(apiKey);
    }
  }

  // Reconnection logic
  setupReconnection(session: RealtimeSession) {
    session.on('disconnect', async () => {
      for (let i = 0; i < 3; i++) {
        await sleep(1000 * Math.pow(2, i)); // Exponential backoff

        try {
          await session.reconnect();
          break;
        } catch (e) {
          console.error(`Reconnect attempt ${i + 1} failed`);
        }
      }
    });
  }
}
```

^ Production-ready patterns for reliability

---

# Voice Agents: Cost Optimization

```typescript
// Optimize voice agent costs
const costOptimizedAgent = new RealtimeAgent({
  model: 'gpt-4o-realtime-preview',

  // Reduce costs with smart settings
  turnDetection: {
    silenceDurationMs: 300, // Faster turn ending
  },

  // Limit response length
  maxResponseDurationMs: 30000, // 30 second max

  // Use text for simple responses
  responseStrategy: async (input) => {
    if (isSimpleQuery(input)) {
      return { modality: 'text' }; // Cheaper
    }
    return { modality: 'audio' }; // Natural
  },
});

// Monitor usage
session.on('usage', (event) => {
  console.log('Audio seconds:', event.audioSeconds);
  console.log('Token count:', event.tokens);
  console.log('Estimated cost: $', event.estimatedCost);
});
```

^ Control costs while maintaining quality

---

# Voice Agents: Advanced Features

```typescript
// Agent with voice selection
const agent = new RealtimeAgent({
  name: 'Professional Assistant',
  voice: 'nova', // Options: alloy, echo, shimmer, nova
  instructions: 'Respond professionally and concisely',
});

// Session with advanced audio processing
const session = new RealtimeSession(agent, {
  // Audio processing (browser-side implementation)
  audioConstraints: {
    noiseSuppression: true,
    echoCancellation: true,
    autoGainControl: true,
  },

  // Custom configuration
  model: 'gpt-4o-realtime-preview',
  temperature: 0.7,
  maxResponseDurationMs: 30000,
});

// Multi-modal capabilities
session.on('function_call', async (fn) => {
  // Voice agent can call functions just like text
  const result = await fn.execute();
  session.sendFunctionResult(fn.id, result);
});
```

^ Advanced audio processing handled by browser/client implementation

---

# Voice Agents: Testing & Development

```typescript
// Development mode with transcript
const debugSession = new RealtimeSession(agent, {
  debug: true,
  logTranscripts: true,
});

debugSession.on('transcript', (event) => {
  console.log(`[${event.speaker}]: ${event.text}`);
});

// Simulate voice input for testing
async function testVoiceAgent() {
  const testAudio = await textToSpeech('What is the weather?');

  session.sendAudio(testAudio);

  const response = await session.waitForResponse();
  assert(response.text.includes('weather'));
}

// Load testing voice agents
async function loadTest() {
  const sessions = await Promise.all(
    Array(100)
      .fill(0)
      .map(() => createSession()),
  );

  // Simulate concurrent conversations
}
```

^ Comprehensive testing strategies for voice agents

---

# Voice Agents: Event Streaming

```typescript
// Comprehensive event handling for voice agents
session.on('transcript', (event) => {
  // Real-time transcription
  console.log('User said:', event.text);
});

session.on('audio', (event) => {
  // Stream audio chunks to player
  audioPlayer.write(event.data);
});

session.on('tool_call', async (event) => {
  // Tools work same as text agents
  const result = await executeTool(event);
  session.sendToolResult(result);
});

session.on('handoff', (event) => {
  // Handoffs in voice context
  console.log('Transferring to:', event.agent);
});

session.on('interruption', (event) => {
  console.log('User interrupted at:', event.timestamp);
});

session.on('usage', (event) => {
  console.log('Audio seconds:', event.audioSeconds);
  console.log('Tokens used:', event.tokens);
});
```

^ Event-driven architecture for real-time voice interactions

---

# Voice Agents: Voice/Text Synchronization

```typescript
// Synchronize state between voice and text agents
const sharedContext = {
  conversation: [],
  userProfile: {},
  sessionData: {},
};

// Voice session with shared context
const voiceSession = new RealtimeSession(voiceAgent, {
  context: sharedContext,
});

// Text agent with same context
const textResult = await run(textAgent, input, {
  context: sharedContext,
});

// Updates from voice reflected in text and vice versa
voiceSession.on('message', (msg) => {
  sharedContext.conversation.push(msg);
});

// Seamless modality switching
async function switchToText() {
  const voiceState = voiceSession.getState();
  const textResult = await run(textAgent, 'continue', {
    messages: voiceState.messages,
    context: sharedContext,
  });
  return textResult;
}
```

^ Shared context enables seamless voice/text transitions

---

[.text: alignment(center)]

# SDK

---

# SDK Runtime Support

```typescript
// Fully supported environments
✅ Node.js 22+     // Full SDK features, complete tracing
✅ Deno 2.35+      // Native TypeScript, all features
✅ Bun 1.2.5+      // Fast runtime, full support

// Experimental environments
⚠️ Cloudflare Workers {
  // Special requirements:
  - Enable 'nodejs_compat' flag
  - Manual trace flushing required:
    ctx.waitUntil(getGlobalTraceProvider().forceFlush())
}

⚠️ Browser {
  // Limitations:
  - No tracing capability
  - Limited MCP support
  - Use for Realtime agents only
}
```

^ SDK explicitly supports these runtimes with specific requirements

---

# SDK State Persistence

```typescript
import { RunState } from '@openai/agents';

// SDK provides state serialization
const result = await run(agent, input);

// Serialize for storage (SDK feature)
const serialized = JSON.stringify(result.state);
await yourStorage.save(sessionId, serialized);

// Later: Restore state (SDK feature)
const saved = await yourStorage.get(sessionId);
const state = await RunState.fromString(agent, saved);

// Continue conversation with restored state
const nextResult = await run(agent, newInput, {
  state, // SDK handles state restoration
  previousResponseId: result.lastResponseId, // For Responses API
});
```

^ SDK provides RunState serialization/restoration for any storage backend

---

# SDK Error Types

```typescript
import {
  MaxTurnsExceededError,
  GuardrailTripwireTriggered,
  ToolCallError,
} from '@openai/agents';

try {
  const result = await run(agent, input);
} catch (error) {
  // SDK-specific error types
  if (error instanceof MaxTurnsExceededError) {
    console.log('Loop detected:', error.maxTurns);
    // SDK provides maxTurns info
  }

  if (error instanceof GuardrailTripwireTriggered) {
    console.log('Guardrail:', error.guardrailName);
    console.log('Result:', error.guardrailResult);
    // SDK provides guardrail details
  }

  if (error instanceof ToolCallError) {
    console.log('Tool failed:', error.toolName);
    // SDK provides tool failure info
  }
}
```

^ SDK provides typed errors for handling agent-specific failures

---

# SDK Usage Tracking

```typescript
// SDK provides detailed usage metrics
const result = await run(agent, input);

// Built-in usage tracking
console.log(result.usage);
// {
//   inputTokens: 245,
//   outputTokens: 89,
//   totalTokens: 334
// }

// Track costs across runs
const runner = new Runner({
  modelSettings: {
    maxTokens: 1000, // SDK enforces limit
    temperature: 0.1,
  },
  maxTurns: 10, // SDK prevents infinite loops
});

// Usage accumulates in RunContext
runner.on('turn', (turn) => {
  console.log('Turn usage:', turn.usage);
  console.log('Total so far:', turn.context.usage);
});
```

^ SDK automatically tracks token usage for cost management

---

# SDK Tracing & Monitoring

```typescript
import {
  setTracingExportApiKey,
  createCustomSpan,
  addTraceProcessor,
} from '@openai/agents';

// SDK built-in tracing
setTracingExportApiKey(process.env.OPENAI_TRACING_KEY);

// Custom span tracking (SDK feature)
await createCustomSpan('database_query', async () => {
  return await db.query(sql);
});

// SDK debug controls
process.env.DEBUG = 'openai-agents:*'; // Enable debug logs
process.env.OPENAI_AGENTS_DONT_LOG_MODEL_DATA = '1'; // Privacy
process.env.OPENAI_AGENTS_DONT_LOG_TOOL_DATA = '1'; // Security

// Custom trace processor (SDK feature)
addTraceProcessor({
  onSpanStart(span) {
    /* metrics */
  },
  onSpanEnd(span) {
    /* analytics */
  },
});
```

^ SDK provides comprehensive tracing and debug controls

---

# SDK Configuration by Environment

```typescript
// SDK supports environment-based configuration
const agent = new Agent({
  model: process.env.NODE_ENV === 'production' ? 'gpt-4o' : 'gpt-4o-mini',

  // SDK's maxTurns prevents infinite loops
  maxTurns: process.env.NODE_ENV === 'production' ? 10 : 5,

  // Dynamic instructions based on environment
  instructions: (context) => {
    if (process.env.NODE_ENV === 'development') {
      return 'Debug mode: Be verbose in responses';
    }
    return productionInstructions;
  },
});

// SDK's Runner configuration
const runner = new Runner({
  tracingDisabled: process.env.NODE_ENV === 'development',
  groupId: process.env.DEPLOYMENT_ID, // For trace grouping
});
```

^ SDK allows environment-specific agent configuration

---

# SDK Conversation Management

```typescript
// SDK provides conversation continuity via Responses API
const result1 = await run(agent, 'Hello');

// SDK returns previousResponseId for stateful conversations
const result2 = await run(agent, 'Continue', {
  previousResponseId: result1.lastResponseId,
  // SDK manages conversation history server-side
});

// For interruption handling (SDK feature)
if (result.interruptions.length > 0) {
  // SDK provides interruption state
  const state = JSON.stringify(result.state);

  // Resume after approval (SDK feature)
  const restored = await RunState.fromString(agent, state);
  restored.approve(interruption);
  const final = await run(agent, restored);
}
```

^ SDK handles conversation state and interruption recovery

---

# SDK Production Features Summary

```typescript
// What the SDK provides for deployment:

✅ Runtime support (Node.js, Deno, Bun, Workers)
✅ State serialization (RunState.fromString)
✅ Error types (MaxTurnsExceededError, etc.)
✅ Usage tracking (result.usage)
✅ Tracing & monitoring (setTracingExportApiKey)
✅ Debug controls (environment variables)
✅ Conversation management (previousResponseId)
✅ Interruption handling (HITL state)
✅ Context passing (RunContext)
✅ Max turns protection (prevents loops)
✅ Dynamic configuration (per environment)

// You provide:
- Infrastructure (servers, databases)
- Storage backend (Redis, PostgreSQL, etc.)
- Security (API keys, rate limiting)
- Deployment (Docker, K8s, serverless)
```

^ SDK provides agent-specific features, you provide infrastructure

---

[.text: alignment(center)]

# Dynamic Instructions

---

# Dynamic Instructions

```typescript
// Instructions can be static or dynamic
const agent = new Agent({
  name: 'ContextAware',

  // Static instructions
  instructions: 'You are a helpful assistant',

  // Or dynamic based on context
  instructions: (context) => {
    const time = new Date().getHours();
    const greeting = time < 12 ? 'morning' : 'afternoon';

    return `
      Good ${greeting}! You are helping ${context.user.name}.
      User tier: ${context.user.subscription}
      Available features: ${context.features.join(', ')}
      Current task: ${context.currentTask}
    `;
  },
});
```

^ Instructions can adapt based on runtime context

---

[.text: alignment(center)]

# Guardrails

---

# [fit] Guardrails: Build Your Own

## [fit] **The SDK provides the framework**

## [fit] **You implement the detection logic**

---

**Your implementation options:**

- Regular expressions for patterns
- External APIs (OpenAI Moderation, AWS Comprehend)
- ML models (toxicity, sentiment)
- Other agents as validators
- Custom business rules

^ No pre-built guardrails. Complete flexibility to implement your own logic.

---

# Guardrails: Input Protection

```typescript
// Guardrails are custom functions YOU implement
const piiGuardrail: InputGuardrail = {
  name: 'PII_Check',
  execute: async ({ input, context, agent }) => {
    // You implement detectPII - could use regex, ML, or external API
    const hasPII =
      /\b\d{3}-\d{2}-\d{4}\b/.test(input) || // SSN
      /\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b/.test(input); // CC

    return {
      tripwireTriggered: hasPII, // Halt if PII detected
      outputInfo: { detected: hasPII ? ['SSN or Credit Card'] : [] },
    };
  },
};

// Or use another agent as a guardrail
const mathHomeworkGuardrail: InputGuardrail = {
  name: 'Math_Homework_Check',
  execute: async ({ input, context }) => {
    const checkAgent = new Agent({
      outputType: z.object({ isMathHomework: z.boolean() }),
    });
    const result = await run(checkAgent, input, { context });
    return {
      tripwireTriggered: result.finalOutput?.isMathHomework ?? false,
      outputInfo: result.finalOutput,
    };
  },
};
```

^ SDK provides the framework. You implement the logic - regex, ML models, agents, or APIs.

---

# Guardrails: Output Protection

```typescript
const toneGuardrail = defineOutputGuardrail({
  name: 'Professional_Tone',
  execute: async ({ output, context, agent }) => {
    const analysis = await analyzeTone(output);

    if (analysis.toxicity > 0.3 || !analysis.professional) {
      return {
        tripwireTriggered: true,
        outputInfo: {
          reason: 'Unprofessional tone detected',
          suggestions: analysis.improvements,
        },
      };
    }

    return { tripwireTriggered: false, outputInfo: analysis };
  },
});
```

^ Output guardrails validate agent responses. Can trigger re-generation.

---

# Guardrails: Async Validation

```typescript
const agent = new Agent({
  outputGuardrails: [
    {
      name: 'Compliance_Check',
      execute: async ({ output }) => {
        // Async call to compliance service
        const compliant = await complianceAPI.check(output);
        return {
          tripwireTriggered: !compliant.passed,
          outputInfo: compliant.report,
        };
      },
    },
  ],
});

// Guardrails run in parallel by default
```

^ Async guardrails enable external validation services

---

[.text: alignment(center)]

# Understanding Tripwires

## **Tripwire = Emergency Stop**

---

When `tripwireTriggered: true`:

1. **Execution halts immediately**
2. **Specific exception thrown**
3. **No agent processing occurs** (input) or **output discarded** (output)
4. **You handle the exception**

```typescript
// Tripwire vs Warning Pattern
return {
  tripwireTriggered: true, // STOPS execution, throws exception
  outputInfo: { reason: 'PII detected' },
};

// Alternative: Warning pattern (not built-in, you'd implement)
return {
  tripwireTriggered: false, // Continues with warning
  outputInfo: { warning: 'Potential issue detected' },
};
```

^ Tripwires are for safety-critical checks. Use them when you MUST stop.

---

# Tripwire Exception Handling

```typescript
try {
  const result = await run(agent, input);
} catch (error) {
  if (error instanceof InputGuardrailTripwireTriggered) {
    console.log('Input blocked:', error.guardrailResult);
    // Options:
    // - Return error to user
    // - Sanitize input and retry
    // - Log for compliance
    // - Escalate to human
  }

  if (error instanceof OutputGuardrailTripwireTriggered) {
    console.log('Output blocked:', error.guardrailResult);
    // Options:
    // - Retry with different prompt
    // - Use fallback response
    // - Escalate to supervisor agent
    // - Return safe default message
  }
}
```

^ Specific exception types let you handle input vs output violations differently.

---


# [fit] Human-in-the-Loop

---

# HITL: The User Experience

## **What happens when approval is needed:**

1. **Agent requests approval** → Execution pauses
2. **State serialized** → Stored in database/Redis
3. **Human notified** → Email, Slack, dashboard alert
4. **Human reviews** → Sees tool, parameters, context
5. **Human decides** → Approve or reject
6. **Agent resumes** → From exact pause point

**Key insight:** The agent doesn't "wait" - it saves state and stops.
Resume can happen seconds, hours, or days later.

^ Asynchronous by design. No blocking threads or timeouts.

---

# [fit] HITL: Notification & Review UI

```typescript
// What the human sees in the approval interface
interface ApprovalRequest {
  // Context
  requestId: string;
  timestamp: Date;
  requestor: { name: string; email: string };
  agent: { name: string; purpose: string };

  // What needs approval
  tool: {
    name: 'delete_user';
    parameters: { userId: 'admin_123' };
    riskLevel: 'HIGH';
  };

  // Decision context
  conversation: Message[]; // Recent history
  reason: string; // Why agent wants to do this

  // Actions
  actions: ['Approve', 'Reject', 'Request More Info'];
}
```

^ Humans need full context to make informed decisions.

---

# Human-in-the-Loop: Approval Flow

```typescript
tool({
  name: 'delete_user',
  needsApproval: async (context, input, callId) => {
    // Return true to require approval
    return (
      input.userId.startsWith('admin_') || context.sensitiveOperation === true
    );
  },
  execute: async (input) => {
    // Only runs after approval
    return await database.deleteUser(input.userId);
  },
});
```

^ needsApproval is evaluated at runtime for each call

---

# HITL: Interruption & Resume

```typescript
// First run - hits approval requirement
let result = await run(agent, 'Delete admin_user_123');

if (result.interruptions?.length > 0) {
  // Serialize state for persistence
  const serialized = JSON.stringify(result.state);
  await redis.set(`approval:${id}`, serialized);

  // Send to approval queue
  await queue.send({
    id,
    interruptions: result.interruptions,
    requestor: context.user,
  });
}
```

^ State can be persisted while waiting for approval

---

# HITL: State Serialization

```typescript
// Later, after approval received
const serialized = await redis.get(`approval:${id}`);
const state = await RunState.fromString(agent, serialized);

// Process approvals
for (const interruption of approvals) {
  if (interruption.approved) {
    state.approve(interruption);
  } else {
    state.reject(interruption);
  }
}

// Resume execution from exact point
const finalResult = await run(agent, state);
```

^ Complete state preservation enables async approval workflows

---

# HITL: Real-World Implementation

## **Building the approval system:**

[.column]
**Backend**

- Queue (SQS, RabbitMQ)
- State store (Redis, DynamoDB)
- Notification service
- WebSocket server

[.column]
**Frontend**

- Admin dashboard
- Mobile app
- Slack bot
- Email with action links

---

# HITL: WebSocket Integration

```typescript
// Real-time approval flow with WebSocket
ws.on('approval_request', async (data) => {
  const { state, interruptions } = data;

  // Send to UI with full context
  ws.emit('show_approval_ui', {
    tool: interruptions[0].rawItem.name,
    params: interruptions[0].rawItem.arguments,
    risk: calculateRisk(interruptions[0]),
    timeout: '24 hours', // Optional auto-reject
  });
});

ws.on('approval_response', async (response) => {
  const state = await RunState.fromString(agent, response.state);

  if (response.approved) {
    state.approve(response.interruption);
    await audit.log('approval.granted', response);
  } else {
    state.reject(response.interruption);
    await audit.log('approval.denied', response);
  }

  const result = await run(agent, state);
  ws.emit('execution_complete', result);
});
```

^ WebSockets for immediate response. Audit logging for compliance.

---

[.text: alignment(center)]

# Handoffs & Multi-Agent

---

# Handoff Patterns

## Control Transfer

```typescript
const triageAgent = new Agent({
  name: 'Triage',
  handoffs: [billingAgent, technicalAgent],
  instructions: 'Route to appropriate specialist',
});
```

^ Agents can transfer control completely to specialists

---

# Context Flow Through Handoffs

```typescript
const handoff = new Handoff({
  agent: specialistAgent,
  inputFilter: (data) => ({
    ...data,
    // Local context ALWAYS flows through unchanged
    context: data.context, // Database, cache, user, etc.

    // Agent context can be filtered/modified
    inputHistory: data.inputHistory
      .filter(
        (item) =>
          // Remove sensitive conversation history
          !item.content?.includes('password'),
      )
      .slice(-5), // Limit context window

    // Inject new conversation context
    newItems: [
      { role: 'system', content: `Escalated from ${data.agent.name}` },
      { role: 'system', content: `User tier: ${data.context.user.tier}` },
    ],
  }),
});
```

^ **Key insight**: Local context flows untouched. Agent context is carefully managed.

---

# Handoffs with Responses API

## Server Context Thread Continuity

```typescript
// With Responses API, handoffs maintain THREE contexts:

const runner = new Runner(agent1, {
  context: { user: 'alice', db: pgClient }, // 1. Local context
  previousResponseId: 'resp_123...', // 2. Server context reference
});

// During handoff to agent2:
// 1. Local Context: Flows through unchanged
// 2. Server Context: Thread continues via previousResponseId
// 3. Input Filter: Can still modify what agent2 "sees"

const handoff = new Handoff({
  agent: agent2,
  inputFilter: (data) => {
    // data.runContext preserves local state
    // previousResponseId maintains server conversation
    // But we can filter what's visible to agent2:
    return {
      ...data,
      inputHistory: [], // Hide previous conversation
      newItems: [{ role: 'system', content: 'Fresh start for specialist' }],
    };
  },
});

// Result: agent2 has local context, server thread, but filtered view
```

^ Responses API maintains conversation thread even when filtering handoff inputs

---

# Handoff Filtering Strategies

```typescript
// Strategy 1: Summarization
const summarizeHandoff = new Handoff({
  agent: managerAgent,
  inputFilter: async (data) => {
    const summary = await summarizeConversation(data.inputHistory);
    return {
      ...data,
      inputHistory: [],
      newItems: [
        {
          role: 'system',
          content: `Previous conversation summary: ${summary}`,
        },
      ],
    };
  },
});

// Strategy 2: Selective history
const selectiveHandoff = new Handoff({
  agent: specialistAgent,
  inputFilter: (data) => ({
    ...data,
    inputHistory: data.inputHistory.filter(
      (item) => item.role === 'tool' || item.content?.includes('ERROR'),
    ),
  }),
});
```

^ Different filtering strategies for different handoff scenarios

---

# Agent as Tool

## **Agents can be tools for other agents**

---

## **Agents can be tools for other agents**

```typescript
const translationAgent = new Agent({
  name: 'translator',
  instructions: 'Translate text to the requested language',
});

const orchestratorAgent = new Agent({
  name: 'orchestrator',
  instructions: 'Coordinate translation tasks',
  tools: [
    // Convert agent to tool with asTool()
    translationAgent.asTool({
      toolName: 'translate_text',
      toolDescription: 'Translate text to any language',
    }),
  ],
});

// Orchestrator calls translation agent like any other tool
// Input → Tool call → Agent runs → Returns result → Continue
```

^ Agent-as-tool: Stateless, isolated execution. Returns to caller.

---

# Agent as Tool: Use Cases

## **When to use agent-as-tool pattern:**

✅ **Specialized capabilities** - Complex agent for specific tasks
✅ **Reusable components** - Same agent used by multiple orchestrators
✅ **Isolated execution** - Keep concerns separated
✅ **Parallel processing** - Call multiple agent-tools concurrently

---

# Handoff vs Agent-as-Tool

[.column]
**Handoff**

- Full conversation history
- Control transfer
- Stateful continuation
- Context preservation
- Agent takes over

[.column]
**Agent Tool**

- Generated input only
- Returns to caller
- Stateless invocation
- Isolated execution
- Original agent continues

---

# Handoff Return Pattern

## **Manual bidirectional configuration required**

```typescript
// Configure agents with mutual handoffs
const triageAgent = new Agent({
  name: 'Triage',
  instructions: 'Route to appropriate specialist based on request type',
  handoffs: [billingAgent, technicalAgent],
});

const billingAgent = new Agent({
  name: 'Billing',
  instructions: `
    Handle billing inquiries.
    If customer asks non-billing questions, transfer back to triage.
  `,
  handoffs: [triageAgent], // ← Explicit return path
});

const technicalAgent = new Agent({
  name: 'Technical',
  instructions: `
    Resolve technical issues.
    If unable to resolve or out of scope, transfer back to triage.
  `,
  handoffs: [triageAgent], // ← Explicit return path
});

// Flow: Triage → Specialist → Triage (if needed)
```

^ No automatic returns. Each agent must explicitly configure handoff paths.

---

# Multi-Agent Coordination Patterns

## Manager/Orchestrator Pattern

```typescript
const orchestrator = new Agent({
  name: 'Orchestrator',
  instructions: `
    You coordinate multiple specialists:
    1. Analyze request complexity
    2. Delegate to appropriate agents
    3. Synthesize results
    4. Ensure quality
  `,
  handoffs: [
    dataAgent, // For data analysis
    reportAgent, // For report generation
    reviewAgent, // For quality review
  ],
});
```

^ Orchestrator pattern for complex multi-step workflows

---

# Multi-Agent: Parallel Execution

```typescript
const parallelAnalysis = async (data: Data) => {
  // Run multiple agents in parallel
  const [sentiment, summary, keywords, entities] = await Promise.all([
    run(sentimentAgent, data),
    run(summaryAgent, data),
    run(keywordAgent, data),
    run(entityAgent, data),
  ]);

  // Aggregate results with consensus agent
  return await run(consensusAgent, {
    sentiment: sentiment.finalOutput,
    summary: summary.finalOutput,
    keywords: keywords.finalOutput,
    entities: entities.finalOutput,
  });
};
```

^ Parallel patterns for independent analysis tasks

---


[.text: alignment(center)]

# Lifecycle & Control

---

# Lifecycle Hooks

```typescript
class CustomAgent extends Agent {
  async onAgentStart(context: RunContext) {
    // Initialize resources
    await context.context.cache.warm();
  }

  async onTurnComplete(result: TurnResult, context: RunContext) {
    // After each LLM response
    if (result.toolsUsed.includes('sensitive_tool')) {
      await context.context.audit.log(result);
    }
  }

  async onToolResult(tool: string, result: any, context: RunContext) {
    // After each tool execution
    context.context.metrics.record(tool, result);
  }

  async onAgentEnd(finalOutput: any, context: RunContext) {
    // Cleanup resources
    await context.context.cache.flush();
  }
}
```

^ Lifecycle hooks enable custom behavior at key points

---

# Forcing Tool Use

```typescript
const agent = new Agent({
  modelSettings: {
    // Force specific tool on first turn
    toolChoice: {
      type: 'function',
      name: 'analyze_request',
    },
  },
});

// Dynamic tool forcing
class AdaptiveAgent extends Agent {
  async onTurnComplete(result: TurnResult) {
    if (!result.toolsUsed.includes('validate')) {
      // Force validation on next turn
      this.modelSettings.toolChoice = {
        type: 'function',
        name: 'validate',
      };
    }
  }
}
```

^ Tool choice can be controlled programmatically

---

[.text: alignment(center)]

# Tracing & Monitoring

---

# Tracing Architecture

```typescript
// OpenTelemetry-based tracing
import { trace } from '@opentelemetry/api';

const tracer = trace.getTracer('agents-sdk');

await tracer.startActiveSpan('agent_run', async (span) => {
  span.setAttributes({
    'agent.name': agent.name,
    'agent.model': agent.model,
    'input.length': input.length,
  });

  const result = await run(agent, input);

  span.setAttributes({
    'output.length': result.finalOutput.length,
    'tools.used': result.toolsUsed.length,
    'handoffs.count': result.handoffs.length,
  });

  span.end();
  return result;
});
```

^ Full OpenTelemetry support for production observability

---

# Custom Trace Processors

```typescript
class CustomTraceProcessor implements SpanProcessor {
  onStart(span: Span): void {
    // Track span start
    metrics.increment('spans.started');
  }

  onEnd(span: ReadableSpan): void {
    // Custom processing
    if (span.name.includes('tool_call')) {
      const duration = span.duration;
      metrics.histogram('tool.duration', duration);

      if (duration > 5000) {
        alerts.send({
          type: 'SLOW_TOOL',
          tool: span.attributes['tool.name'],
          duration,
        });
      }
    }
  }
}

// Register processor
tracerProvider.addSpanProcessor(new CustomTraceProcessor());
```

^ Custom processors for metrics, alerts, and analysis

---

# Performance Monitoring

```typescript
// Built-in performance tracking
const result = await run(agent, input);

console.log(result.usage);
// {
//   inputTokens: 1234,
//   outputTokens: 567,
//   totalTokens: 1801,
//   inputCachedTokens: 200,
//   inputAudioTokens: 0,
//   outputAudioTokens: 0
// }

console.log(result.timing);
// {
//   start: 1234567890,
//   firstToken: 1234567891,
//   end: 1234567895,
//   duration: 5000,
//   ttfb: 1000  // Time to first byte
// }
```

^ Comprehensive usage and timing metrics built-in

---

# Debug Strategies

```typescript
// Verbose logging
import { setLogLevel } from '@openai/agents';
setLogLevel('debug');

// Step-through debugging
const runner = new Runner({
  pauseOnTool: true,
  pauseOnHandoff: true,
});

runner.on('tool_call', async (event) => {
  console.log('Tool called:', event);
  // Debugger breakpoint here
  debugger;
});

// Trace visualization
const result = await run(agent, input);
console.log(result.trace.visualize());
// Outputs ASCII tree of execution flow
```

^ Rich debugging capabilities for development

---




[.text: alignment(center)]

# Best Practices

---

# Best Practices

[.build-lists: true]

- **Small, focused agents** over monolithic ones
- **Explicit handoffs** over implicit routing
- **Typed context** over string passing
- **Structured outputs** over free text
- **Deterministic flows** where possible
- **Guardrails** on boundaries
- **Lifecycle hooks** for custom behavior

^ Learned from production deployments

---

# Anti-Patterns to Avoid

❌ **Circular handoffs** without termination
❌ **Shared mutable state** outside context
❌ **Synchronous long-running tools**
❌ **Unconstrained recursive depth**
❌ **Missing error boundaries**
❌ **Ignoring tripwire guardrails**

^ Common pitfalls in multi-agent systems

---

# Production Checklist

- [ ] Guardrails configured
- [ ] Error boundaries in place
- [ ] Tracing enabled
- [ ] State persistence ready
- [ ] Circuit breakers configured
- [ ] Monitoring dashboards
- [ ] Runbook documented
- [ ] Load tested
- [ ] Approval flows tested

^ Essential for production deployments

---

# Advanced: Custom Providers

```typescript
class CustomProvider implements Model {
  async generate(request: ModelRequest): Promise<ModelResponse> {
    const response = await this.customAPI.complete({
      messages: request.messages,
      tools: request.tools,
      // Custom transformation
    });

    return {
      output: transformResponse(response),
      usage: extractUsage(response),
    };
  }

  async streamGenerate(request: ModelRequest): AsyncIterable<ModelChunk> {
    // Streaming implementation
  }
}
```

^ Bring any model through provider interface

---

# Advanced: Workflow DSL

```typescript
const workflow = defineWorkflow({
  nodes: {
    start: triageAgent,
    billing: billingAgent,
    technical: technicalAgent,
    resolve: resolutionAgent,
  },
  edges: {
    start: ['billing', 'technical'],
    billing: ['resolve'],
    technical: ['resolve'],
  },
  guards: {
    'start->billing': (ctx) => ctx.issue.type === 'billing',
    'start->technical': (ctx) => ctx.issue.type === 'technical',
  },
});

const executor = new WorkflowExecutor(workflow);
const result = await executor.run(input);
```

^ Higher-level abstractions possible on core primitives

---

# Future Roadmap

[.build-lists: true]

- **Long-running functions**: Suspend/resume for async operations
- **Voice pipeline**: Enhanced speech capabilities
- **Distributed execution**: Cross-process agent coordination
- **Model routing**: Dynamic model selection
- **Adaptive flows**: ML-driven handoff decisions
- **Visual agents**: Computer use and UI automation

^ SDK continues to evolve with community needs

---

# Key Takeaways

[.build-lists: true]

1. **Type-safe orchestration** from ground up
2. **Composable agents** with clear boundaries
3. **Production-ready** patterns built-in
4. **Provider-agnostic** architecture
5. **Extensible** through clean abstractions
6. **Voice-enabled** for modern interfaces

^ Not just another wrapper - thoughtful orchestration framework

---

# Your Next Steps

```typescript
// Start here
const agent = new Agent({
  name: 'MyFirstAgent',
  instructions: 'You are a helpful assistant',
});

// Add capability
agent.tools = [myTool];

// Add intelligence routing
agent.handoffs = [specialist];

// Add safety
agent.inputGuardrails = [piiCheck];
agent.outputGuardrails = [toneCheck];

// Ship it
await run(agent, userInput);
```

^ Begin simple. Complexity emerges from composition.

---


# Questions?

## Let's Build Intelligence Together

^ Thank you for your attention. Ready for deep technical discussion.
