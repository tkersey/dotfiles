#!/usr/bin/env node
// Run many independent cas sessions in parallel and execute one request per instance.
//
// Purpose:
// - Demonstrate effective concurrency beyond the per-session subagent cap.
// - Provide a reusable instance runner for orchestrating identical requests.

import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { CasClient } from "./cas_client.mjs";

function usage() {
  return [
    "cas_instance_runner.mjs",
    "",
    "Usage:",
    "  node scripts/cas_instance_runner.mjs --cwd DIR [options]",
    "",
    "Required:",
    "  --cwd DIR                        Workspace for each instance's app-server.",
    "",
    "Options:",
    "  --instances N                       Number of parallel instances (default: 12).",
    "  --method NAME                    App-server method (default: thread/list).",
    "  --params-json JSON               Params as inline JSON object.",
    "  --params-file PATH               Params from JSON file.",
    "  --state-file-dir DIR             Directory for per-instance state files (optional).",
    "  --request-timeout-ms N           Timeout per request (default: 30000).",
    "  --server-request-timeout-ms N    Forwarded server-request timeout for proxy.",
    "  --exec-approval VALUE            Exec approval: auto|accept|acceptForSession|decline|cancel.",
    "  --file-approval VALUE            File approval: auto|accept|acceptForSession|decline|cancel.",
    "  --read-only                      Decline exec + file approvals (safe for scout instances).",
    "  --opt-out-notification-method M  Suppress a notification method (repeatable).",
    "  --client-prefix NAME             Prefix for instance client names (default: cas-instance).",
    "  --sample N                       Number of sample results in output (default: 3).",
    "  --json                           Emit JSON output (default: false).",
    "  --verbose                        Emit per-instance start/request status to stderr.",
    "  --help                           Show this help.",
    "",
    "Examples:",
    "  node scripts/cas_instance_runner.mjs --cwd ~/.dotfiles --instances 12",
    "  node scripts/cas_instance_runner.mjs --cwd ~/.dotfiles --method thread/list --params-json '{\"cursor\":null,\"limit\":1}' --json",
  ].join("\n");
}

function parseArgs(argv) {
  const opts = {
    cwd: null,
    instances: 12,
    method: "thread/list",
    paramsJson: null,
    paramsFile: null,
    stateFileDir: null,
    requestTimeoutMs: 30_000,
    serverRequestTimeoutMs: null,
    execApproval: null,
    fileApproval: null,
    readOnly: false,
    optOutNotificationMethods: [],
    clientPrefix: "cas-instance",
    sample: 3,
    json: false,
    verbose: false,
  };

  const args = [...argv];
  while (args.length) {
    const a = args.shift();
    if (!a) break;
    if (a === "--help" || a === "-h") return { ok: false, help: true, error: null, opts: null };

    const take = () => {
      const v = args.shift();
      if (!v) throw new Error(`Missing value for ${a}`);
      return v;
    };

    if (a === "--cwd") {
      opts.cwd = take();
      continue;
    }
    if (a === "--instances") {
      opts.instances = Number(take());
      continue;
    }
    if (a === "--method") {
      opts.method = take();
      continue;
    }
    if (a === "--params-json") {
      opts.paramsJson = take();
      continue;
    }
    if (a === "--params-file") {
      opts.paramsFile = take();
      continue;
    }
    if (a === "--state-file-dir") {
      opts.stateFileDir = take();
      continue;
    }
    if (a === "--request-timeout-ms") {
      opts.requestTimeoutMs = Number(take());
      continue;
    }
    if (a === "--server-request-timeout-ms") {
      opts.serverRequestTimeoutMs = Number(take());
      continue;
    }
    if (a === "--exec-approval") {
      opts.execApproval = take();
      continue;
    }
    if (a === "--file-approval") {
      opts.fileApproval = take();
      continue;
    }
    if (a === "--read-only") {
      opts.readOnly = true;
      continue;
    }
    if (a === "--opt-out-notification-method") {
      opts.optOutNotificationMethods.push(take());
      continue;
    }
    if (a === "--client-prefix") {
      opts.clientPrefix = take();
      continue;
    }
    if (a === "--sample") {
      opts.sample = Number(take());
      continue;
    }
    if (a === "--json") {
      opts.json = true;
      continue;
    }
    if (a === "--verbose") {
      opts.verbose = true;
      continue;
    }
    throw new Error(`Unknown arg: ${a}`);
  }

  if (!opts.cwd) throw new Error("Missing --cwd");
  if (!Number.isInteger(opts.instances) || opts.instances <= 0) {
    throw new Error("--instances must be a positive integer");
  }
  if (!Number.isInteger(opts.requestTimeoutMs) || opts.requestTimeoutMs <= 0) {
    throw new Error("--request-timeout-ms must be a positive integer");
  }
  if (opts.serverRequestTimeoutMs !== null && (!Number.isInteger(opts.serverRequestTimeoutMs) || opts.serverRequestTimeoutMs < 0)) {
    throw new Error("--server-request-timeout-ms must be >= 0");
  }
  if (opts.execApproval !== null && (typeof opts.execApproval !== "string" || !opts.execApproval)) {
    throw new Error("--exec-approval must be a non-empty string");
  }
  if (opts.fileApproval !== null && (typeof opts.fileApproval !== "string" || !opts.fileApproval)) {
    throw new Error("--file-approval must be a non-empty string");
  }
  if (!Number.isInteger(opts.sample) || opts.sample < 0) {
    throw new Error("--sample must be >= 0");
  }
  if (opts.paramsJson && opts.paramsFile) {
    throw new Error("Specify only one of --params-json or --params-file");
  }
  if (opts.stateFileDir !== null && (typeof opts.stateFileDir !== "string" || !opts.stateFileDir)) {
    throw new Error("--state-file-dir must be a non-empty string");
  }

  return { ok: true, help: false, error: null, opts };
}

function parseParams(opts) {
  if (opts.paramsJson) {
    return JSON.parse(opts.paramsJson);
  }
  if (opts.paramsFile) {
    const raw = readFileSync(opts.paramsFile, "utf-8");
    return JSON.parse(raw);
  }
  if (opts.method === "thread/list") {
    return { cursor: null, limit: 1 };
  }
  return {};
}

function summarizeResult(method, result) {
  if (method === "thread/list") {
    return {
      firstThreadId: result?.data?.[0]?.id ?? null,
      rows: Array.isArray(result?.data) ? result.data.length : 0,
    };
  }
  if (method === "thread/read") {
    return {
      threadId: result?.thread?.id ?? null,
      turns: Array.isArray(result?.turns) ? result.turns.length : null,
    };
  }
  if (result && typeof result === "object") {
    return { keys: Object.keys(result).slice(0, 8) };
  }
  return { value: result ?? null };
}

function writeOutput(opts, payload) {
  if (opts.json) {
    process.stdout.write(`${JSON.stringify(payload, null, 2)}\n`);
    return;
  }

  const lines = [];
  lines.push("cas_instance_runner summary");
  lines.push(`cwd: ${payload.cwd}`);
  lines.push(`method: ${payload.method}`);
  lines.push(`instances requested: ${payload.instances_requested}`);
  lines.push(`instances started:   ${payload.instances_started}`);
  lines.push(`requests ok:      ${payload.requests_ok}`);
  lines.push(`requests failed:  ${payload.requests_failed}`);
  lines.push(
    `timing ms: start=${payload.timing_ms.start_all_clients}, request=${payload.timing_ms.run_all_requests}, total=${payload.timing_ms.total}`,
  );
  if (payload.sample_results.length) {
    lines.push("sample results:");
    for (const r of payload.sample_results) {
      lines.push(`- instance ${r.instance}: ${r.ok ? "ok" : "fail"} ${JSON.stringify(r.summary ?? r.error)}`);
    }
  }
  process.stdout.write(`${lines.join("\n")}\n`);
}

async function main() {
  let parsed;
  try {
    parsed = parseArgs(process.argv.slice(2));
  } catch (err) {
    process.stderr.write(`${err instanceof Error ? err.message : String(err)}\n${usage()}\n`);
    return 2;
  }

  if (!parsed.ok) {
    if (parsed.help) {
      process.stderr.write(`${usage()}\n`);
      return 0;
    }
    process.stderr.write(`${parsed.error ?? "invalid args"}\n`);
    return 2;
  }

  const opts = parsed.opts;
  if (opts.instances > 1 && !opts.stateFileDir) {
    process.stderr.write(
      "Note: by default, state is derived from --cwd, so parallel instances may share it. " +
        "Use --state-file-dir for per-instance state isolation.\n",
    );
  }
  let params;
  try {
    params = parseParams(opts);
  } catch (err) {
    process.stderr.write(`Invalid params JSON: ${err instanceof Error ? err.message : String(err)}\n`);
    return 2;
  }

  const clients = Array.from({ length: opts.instances }, (_, i) => {
    const stateFile = opts.stateFileDir
      ? resolve(opts.stateFileDir, `${opts.clientPrefix}-${i + 1}.json`)
      : undefined;
    const client = new CasClient({
      cwd: opts.cwd,
      stateFile,
      clientName: `${opts.clientPrefix}-${i + 1}`,
      serverRequestTimeoutMs:
        opts.serverRequestTimeoutMs === null ? undefined : opts.serverRequestTimeoutMs,
      execApprovalDecision: opts.execApproval === null ? undefined : opts.execApproval,
      fileApprovalDecision: opts.fileApproval === null ? undefined : opts.fileApproval,
      readOnly: opts.readOnly,
      optOutNotificationMethods: opts.optOutNotificationMethods,
    });
    if (opts.verbose) {
      client.on("proxyStderr", (line) =>
        process.stderr.write(`[proxy:${i + 1}] ${line}\n`),
      );
      client.on("cas/error", (ev) =>
        process.stderr.write(`[cas:${i + 1}] ${ev?.message ?? "unknown error"}\n`),
      );
    }
    return client;
  });

  const startAt = Date.now();
  const startResults = await Promise.all(
    clients.map(async (c, idx) => {
      try {
        await c.start();
        if (opts.verbose) process.stderr.write(`[start:${idx + 1}] ok\n`);
        return { instance: idx + 1, ok: true, client: c };
      } catch (err) {
        const msg = err instanceof Error ? err.message : String(err);
        if (opts.verbose) process.stderr.write(`[start:${idx + 1}] fail: ${msg}\n`);
        return { instance: idx + 1, ok: false, error: msg, client: c };
      }
    }),
  );
  const afterStart = Date.now();

  const started = startResults.filter((r) => r.ok);
  const requestResults = await Promise.all(
    started.map(async (r) => {
      try {
        const result = await r.client.request(opts.method, params, {
          timeoutMs: opts.requestTimeoutMs,
        });
        if (opts.verbose) process.stderr.write(`[request:${r.instance}] ok\n`);
        return {
          instance: r.instance,
          ok: true,
          summary: summarizeResult(opts.method, result),
        };
      } catch (err) {
        const msg = err instanceof Error ? err.message : String(err);
        if (opts.verbose) process.stderr.write(`[request:${r.instance}] fail: ${msg}\n`);
        return { instance: r.instance, ok: false, error: msg };
      }
    }),
  );
  const afterReq = Date.now();

  await Promise.allSettled(clients.map((c) => c.close()));

  const requestsOk = requestResults.filter((r) => r.ok).length;
  const requestsFailed = requestResults.length - requestsOk;
  const payload = {
    demo: "cas-instance-runner",
    cwd: opts.cwd,
    state_file_dir: opts.stateFileDir,
    method: opts.method,
    params,
    instances_requested: opts.instances,
    instances_started: started.length,
    start_failures: startResults.filter((r) => !r.ok).map((r) => ({
      instance: r.instance,
      error: r.error,
    })),
    requests_ok: requestsOk,
    requests_failed: requestsFailed,
    timing_ms: {
      start_all_clients: afterStart - startAt,
      run_all_requests: afterReq - afterStart,
      total: afterReq - startAt,
    },
    sample_results: requestResults.slice(0, opts.sample),
  };

  writeOutput(opts, payload);
  return requestsFailed === 0 && payload.start_failures.length === 0 ? 0 : 1;
}

main()
  .then((code) => {
    process.exitCode = code;
  })
  .catch((err) => {
    process.stderr.write(
      `Fatal: ${err instanceof Error ? err.stack ?? err.message : String(err)}\n`,
    );
    process.exitCode = 1;
  });
