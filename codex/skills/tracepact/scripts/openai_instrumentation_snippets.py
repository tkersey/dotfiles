#!/usr/bin/env python3
"""Emit minimal OpenAI-oriented instrumentation snippets for latency-treaty traces."""
from __future__ import annotations

import argparse
import textwrap

PYTHON = r'''
# Minimal Python trace envelope for OpenAI Responses-style agent loops.
# Fill in actual API calls and tool execution in your app.
import hashlib, json, time
from contextlib import contextmanager

trace = []

def _hash(value):
    try:
        payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    except TypeError:
        payload = str(value)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]

@contextmanager
def span(kind, name, **meta):
    start = time.perf_counter() * 1000
    row = {
        "span_id": meta.pop("span_id", f"{kind}_{len(trace)+1}"),
        "kind": kind,
        "name": name,
        "start_ms": start,
        **meta,
    }
    try:
        yield row
        row["status"] = "ok"
    except Exception as exc:
        row["status"] = "error"
        row["error_type"] = type(exc).__name__
        raise
    finally:
        row["end_ms"] = time.perf_counter() * 1000
        row["duration_ms"] = row["end_ms"] - row["start_ms"]
        trace.append(row)

async def call_model(client, *, model, input, tools=None, previous_response_id=None, depends_on=None):
    with span(
        "model",
        "responses_call",
        model=model,
        prompt_hash=_hash(input),
        static_prefix_hash=_hash(input[:2] if isinstance(input, list) else None),
        previous_response_id=previous_response_id,
        parallel_tool_calls=True,
        streaming_used=False,
        depends_on=depends_on or [],
    ) as s:
        response = await client.responses.create(
            model=model,
            input=input,
            tools=tools,
            previous_response_id=previous_response_id,
            parallel_tool_calls=True,
        )
        usage = getattr(response, "usage", None)
        if usage:
            s["usage"] = usage.model_dump() if hasattr(usage, "model_dump") else dict(usage)
        return response

async def call_tool(name, args, fn, *, depends_on, mutability="read_only", freshness_policy="cache_ok"):
    with span(
        "tool",
        name,
        tool_name=name,
        tool_args_hash=_hash(args),
        mutability=mutability,
        usage_policy="replayable" if mutability == "read_only" else "affine",
        freshness_policy=freshness_policy,
        branch_policy="unrestricted" if mutability == "read_only" else "single_live_branch",
        depends_on=depends_on,
        dependency_reasons={d: "data" for d in depends_on},
    ) as s:
        result = await fn(**args)
        encoded = json.dumps(result, ensure_ascii=False, default=str).encode("utf-8")
        s["tool_result_bytes"] = len(encoded)
        s["result_consumed"] = True
        return result

# After a run:
# with open("agent_trace.jsonl", "w") as f:
#     for row in trace:
#         f.write(json.dumps(row, ensure_ascii=False) + "\n")
'''

TYPESCRIPT = r'''
// Minimal TypeScript trace envelope for OpenAI Responses-style agent loops.
import crypto from "node:crypto";
import fs from "node:fs";

const trace: any[] = [];

function hash(value: unknown): string {
  const payload = JSON.stringify(value, Object.keys(value as any ?? {}).sort());
  return crypto.createHash("sha256").update(payload ?? String(value)).digest("hex").slice(0, 16);
}

async function withSpan<T>(kind: string, name: string, meta: Record<string, unknown>, fn: (row: any) => Promise<T>): Promise<T> {
  const row: any = { span_id: meta.span_id ?? `${kind}_${trace.length + 1}`, kind, name, start_ms: performance.now(), ...meta };
  try {
    const value = await fn(row);
    row.status = "ok";
    return value;
  } catch (error: any) {
    row.status = "error";
    row.error_type = error?.constructor?.name ?? "Error";
    throw error;
  } finally {
    row.end_ms = performance.now();
    row.duration_ms = row.end_ms - row.start_ms;
    trace.push(row);
  }
}

export async function callModel(client: any, opts: { model: string; input: any; tools?: any[]; previous_response_id?: string; depends_on?: string[] }) {
  return withSpan("model", "responses_call", {
    model: opts.model,
    prompt_hash: hash(opts.input),
    previous_response_id: opts.previous_response_id,
    parallel_tool_calls: true,
    streaming_used: false,
    depends_on: opts.depends_on ?? [],
  }, async (s) => {
    const response = await client.responses.create({
      model: opts.model,
      input: opts.input,
      tools: opts.tools,
      previous_response_id: opts.previous_response_id,
      parallel_tool_calls: true,
    });
    s.usage = response.usage;
    return response;
  });
}

export async function callTool<T>(name: string, args: any, fn: (args: any) => Promise<T>, dependsOn: string[], mutability = "read_only") {
  return withSpan("tool", name, {
    tool_name: name,
    tool_args_hash: hash(args),
    mutability,
    usage_policy: mutability === "read_only" ? "replayable" : "affine",
    freshness_policy: mutability === "read_only" ? "cache_ok" : "fresh_required",
    branch_policy: mutability === "read_only" ? "unrestricted" : "single_live_branch",
    depends_on: dependsOn,
    dependency_reasons: Object.fromEntries(dependsOn.map((id) => [id, "data"])),
  }, async (s) => {
    const result = await fn(args);
    s.tool_result_bytes = Buffer.byteLength(JSON.stringify(result));
    s.result_consumed = true;
    return result;
  });
}

export function writeTrace(path = "agent_trace.jsonl") {
  fs.writeFileSync(path, trace.map((row) => JSON.stringify(row)).join("\n") + "\n");
}
'''


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit OpenAI instrumentation snippets for trace treaty analysis.")
    parser.add_argument("--language", choices=["python", "typescript"], default="python")
    args = parser.parse_args()
    print(textwrap.dedent(PYTHON if args.language == "python" else TYPESCRIPT).strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
