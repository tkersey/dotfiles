import OpenAI from "openai";
import { createHash } from "node:crypto";

/**
 * Reference pattern for an OpenAI Responses harness that is friendly to prompt caching.
 * Focuses on request shape rather than full tool execution.
 *
 * If you later switch to `store: false` / ZDR with reasoning models, mirror the
 * encrypted reasoning carryover pattern shown in `python_stateless_reasoning_example.py`.
 */

const client = new OpenAI();

const INSTRUCTIONS = `You are a coding assistant for a large monorepo.
Prefer targeted file reads, concise plans, and deterministic edits.
Return patch plans before large edits.`;

const TOOLS = [
  {
    type: "function" as const,
    name: "search_docs",
    description: "Search internal engineering docs.",
    parameters: {
      type: "object",
      properties: {
        query: { type: "string" },
      },
      required: ["query"],
      additionalProperties: false,
    },
  },
  {
    type: "function" as const,
    name: "read_file",
    description: "Read a file from the repository.",
    parameters: {
      type: "object",
      properties: {
        path: { type: "string" },
      },
      required: ["path"],
      additionalProperties: false,
    },
  },
  {
    type: "function" as const,
    name: "run_tests",
    description: "Run a targeted test command.",
    parameters: {
      type: "object",
      properties: {
        command: { type: "string" },
      },
      required: ["command"],
      additionalProperties: false,
    },
  },
];

const TEXT_FORMAT = {
  type: "json_schema" as const,
  name: "agent_turn",
  strict: true,
  schema: {
    type: "object",
    properties: {
      summary: { type: "string" },
      next_actions: {
        type: "array",
        items: { type: "string" },
      },
    },
    required: ["summary", "next_actions"],
    additionalProperties: false,
  },
};

function makePromptCacheKey(
  tenantId: string,
  repoId: string,
  agentProfile = "coding-v1",
): string {
  const raw = `${tenantId}:${repoId}:${agentProfile}`;
  return createHash("sha256").update(raw).digest("hex").slice(0, 32);
}

function getCachedTokens(response: any): number {
  return (
    response?.usage?.input_tokens_details?.cached_tokens ??
    response?.usage?.prompt_tokens_details?.cached_tokens ??
    0
  );
}

function getInputTokens(response: any): number {
  return (
    response?.usage?.input_tokens ??
    response?.usage?.prompt_tokens ??
    0
  );
}

async function createTurn({
  tenantId,
  repoId,
  userText,
  previousResponseId,
  allowedToolNames,
}: {
  tenantId: string;
  repoId: string;
  userText: string;
  previousResponseId?: string;
  allowedToolNames?: string[];
}) {
  const names = allowedToolNames ?? TOOLS.map((tool) => tool.name);

  const request: Record<string, unknown> = {
    model: "gpt-5.4",
    instructions: INSTRUCTIONS,
    tools: TOOLS,
    tool_choice: {
      type: "allowed_tools",
      mode: "auto",
      tools: names.map((name) => ({ type: "function", name })),
    },
    text: { format: TEXT_FORMAT },
    prompt_cache_key: makePromptCacheKey(tenantId, repoId),
    // Enable only if your target model supports it and your workload benefits from longer retention.
    // Note: the docs currently disagree on the exact default in-memory literal, but "24h" is stable.
    // prompt_cache_retention: "24h",
    store: true,
    input: [{ role: "user", content: userText }],
  };

  if (previousResponseId) {
    request.previous_response_id = previousResponseId;
  }

  const response = await client.responses.create(request as any);

  const cachedTokens = getCachedTokens(response);
  const inputTokens = getInputTokens(response);
  const cacheRatio = inputTokens ? cachedTokens / inputTokens : 0;

  console.log({
    responseId: response.id,
    model: response.model,
    inputTokens,
    cachedTokens,
    cacheRatio: Number(cacheRatio.toFixed(4)),
  });

  return response;
}

async function main() {
  const first = await createTurn({
    tenantId: "acme",
    repoId: "payments-service",
    userText: "Find the function that validates card BIN ranges and explain how it works.",
    allowedToolNames: ["search_docs", "read_file"],
  });

  const second = await createTurn({
    tenantId: "acme",
    repoId: "payments-service",
    previousResponseId: first.id,
    userText: "Now propose the smallest safe refactor and tell me which tests to run.",
    allowedToolNames: ["read_file", "run_tests"],
  });

  console.log(second.output_text);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
