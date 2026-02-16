#!/usr/bin/env node
// Continual $mesh runner driven via casp (codex app-server).
//
// This avoids `codex exec` and does not require the automation DB.
// It runs $mesh in a persistent app-server thread on an interval.

import { createHash } from "node:crypto";
import { existsSync, readFileSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { CaspClient } from "../../casp/scripts/casp_client.mjs";

function usage() {
  return [
    "mesh_casp_autopilot.mjs",
    "",
    "Runs $mesh continually via casp (codex app-server).",
    "",
    "Usage:",
    "  node codex/skills/mesh/scripts/mesh_casp_autopilot.mjs --cwd DIR [options]",
    "",
    "Required:",
    "  --cwd DIR                Workspace to run in.",
    "",
    "Options:",
    "  --plan-file PATH         Plan file path relative to --cwd (default: .step/st-plan.jsonl)",
    "  --poll-ms N              Sleep between runs (default: 60000)",
    "  --turn-timeout-ms N      Max time for one $mesh run (default: 2700000 = 45 min)",
    "  --state-file PATH        casp state file path (default: ~/.codex/casp/state/<cwd-hash>.json)",
    "  --once                   Run once and exit",
    "  --verbose                Emit proxy stderr lines",
    "  --help                   Show help",
    "",
    "Notes:",
    "  - Requires `codex` on PATH (casp spawns `codex app-server`).",
    "  - Uses the local skill at codex/skills/mesh/.",
  ].join("\n");
}

function parseArgs(argv) {
  const opts = {
    cwd: null,
    planFile: ".step/st-plan.jsonl",
    pollMs: 60_000,
    turnTimeoutMs: 45 * 60_000,
    stateFile: null,
    once: false,
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
    if (a === "--plan-file") {
      opts.planFile = take();
      continue;
    }
    if (a === "--poll-ms") {
      opts.pollMs = Number(take());
      continue;
    }
    if (a === "--turn-timeout-ms") {
      opts.turnTimeoutMs = Number(take());
      continue;
    }
    if (a === "--state-file") {
      opts.stateFile = take();
      continue;
    }
    if (a === "--once") {
      opts.once = true;
      continue;
    }
    if (a === "--verbose") {
      opts.verbose = true;
      continue;
    }

    throw new Error(`Unknown arg: ${a}`);
  }

  if (!opts.cwd) throw new Error("Missing --cwd");
  if (!Number.isInteger(opts.pollMs) || opts.pollMs < 0) {
    throw new Error("--poll-ms must be an integer >= 0");
  }
  if (!Number.isInteger(opts.turnTimeoutMs) || opts.turnTimeoutMs <= 0) {
    throw new Error("--turn-timeout-ms must be a positive integer");
  }
  if (typeof opts.planFile !== "string" || !opts.planFile.trim()) {
    throw new Error("--plan-file must be a non-empty string");
  }
  if (opts.stateFile !== null && (typeof opts.stateFile !== "string" || !opts.stateFile.trim())) {
    throw new Error("--state-file must be a non-empty string");
  }

  return { ok: true, help: false, error: null, opts };
}

function defaultStateFileForCwd(cwd) {
  const normalized = resolve(cwd);
  const digest = createHash("sha256").update(normalized).digest("hex").slice(0, 16);
  return resolve(homedir(), ".codex", "casp", "state", `${digest}.json`);
}

function readCurrentThreadId(stateFile) {
  try {
    if (!existsSync(stateFile)) return null;
    const raw = readFileSync(stateFile, "utf-8");
    const parsed = JSON.parse(raw);
    if (!parsed || typeof parsed !== "object") return null;
    if (parsed.v !== 1) return null;
    return typeof parsed.currentThreadId === "string" && parsed.currentThreadId
      ? parsed.currentThreadId
      : null;
  } catch {
    return null;
  }
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function summarize(text) {
  if (typeof text !== "string") return "";
  for (const line of text.split("\n")) {
    const cleaned = line.trim();
    if (!cleaned) continue;
    if (cleaned.startsWith("Echo:")) continue;
    return cleaned.slice(0, 200);
  }
  return "";
}

async function ensureThread({ client, cwd, stateFile }) {
  const existing = readCurrentThreadId(stateFile);
  if (existing) {
    try {
      await client.resumeThread({ threadId: existing });
      return existing;
    } catch {
      // Fall through to start a new thread.
    }
  }

  const startRes = await client.startThread({ cwd });
  const threadId = startRes?.thread?.id ?? null;
  if (!threadId) throw new Error("thread/start did not return thread.id");
  return threadId;
}

async function runMeshOnce({ client, threadId, planFile, meshSkillPath, timeoutMs }) {
  const prompt = `$mesh plan_file=${planFile} adapter=auto parallel_tasks=auto max_tasks=auto headless=true`;
  const input = [
    { type: "text", text: prompt, text_elements: [] },
    { type: "skill", name: "mesh", path: meshSkillPath },
  ];

  return client.startTurnAndCollect(
    {
      threadId,
      input,
    },
    { timeoutMs },
  );
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
  const stateFile = opts.stateFile ?? defaultStateFileForCwd(opts.cwd);

  const here = dirname(fileURLToPath(import.meta.url));
  const meshSkillPath = resolve(here, "..");

  let stopping = false;
  process.on("SIGINT", () => {
    stopping = true;
  });
  process.on("SIGTERM", () => {
    stopping = true;
  });

  let backoffMs = 1_000;

  while (!stopping) {
    const client = new CaspClient({
      cwd: opts.cwd,
      stateFile,
      clientName: "mesh-autopilot",
      clientTitle: "mesh casp autopilot",
      clientVersion: "0.1.0",
    });

    client.on("casp/error", (ev) => {
      process.stderr.write(`[casp] error: ${ev?.message ?? "unknown"}\n`);
    });
    if (opts.verbose) {
      client.on("proxyStderr", (line) => {
        process.stderr.write(`[proxy] ${line}\n`);
      });
    }

    // Do not allow server-initiated requests to stall forever.
    client.on("casp/serverRequest", (ev) => {
      const method = typeof ev.method === "string" ? ev.method : "<unknown>";
      if (method === "item/tool/call") {
        client.respondError(ev.id, "Dynamic tool calls not implemented by mesh_casp_autopilot", {
          code: -32000,
          data: { method },
        });
        return;
      }
      if (method === "item/tool/requestUserInput") {
        client.respondError(ev.id, "User input not available in headless autopilot", {
          code: -32000,
          data: { method },
        });
        return;
      }
      if (method === "account/chatgptAuthTokens/refresh") {
        client.respondError(ev.id, "Auth token refresh not implemented by mesh_casp_autopilot", {
          code: -32000,
          data: { method },
        });
        return;
      }

      client.respondError(ev.id, `Unhandled server request: ${method}`, {
        code: -32601,
        data: { method },
      });
    });

    try {
      await client.start();
      backoffMs = 1_000;

      const threadId = await ensureThread({
        client,
        cwd: opts.cwd,
        stateFile,
      });

      process.stderr.write(
        `mesh_casp_autopilot_ready cwd=${opts.cwd} plan_file=${opts.planFile} state_file=${stateFile} thread_id=${threadId}\n`,
      );

      while (!stopping) {
        const startedAt = Date.now();
        let ok = false;
        try {
          const collected = await runMeshOnce({
            client,
            threadId,
            planFile: opts.planFile,
            meshSkillPath,
            timeoutMs: opts.turnTimeoutMs,
          });
          const status = collected?.turn?.status ?? null;
          const line = summarize(collected?.agentMessageText ?? "");
          const elapsedMs = Date.now() - startedAt;
          process.stderr.write(
            `mesh_casp_autopilot_run ok status=${status ?? "null"} elapsed_ms=${elapsedMs} summary=${JSON.stringify(line)}\n`,
          );
          ok = true;
        } catch (err) {
          const elapsedMs = Date.now() - startedAt;
          const msg = err instanceof Error ? err.message : String(err);
          process.stderr.write(
            `mesh_casp_autopilot_run fail elapsed_ms=${elapsedMs} error=${JSON.stringify(msg)}\n`,
          );
        }

        if (opts.once) {
          stopping = true;
          break;
        }
        if (opts.pollMs <= 0) {
          // Tight loop requested.
          continue;
        }
        if (!ok) {
          // On failure, give the system a short breather.
          await sleep(Math.min(opts.pollMs, 10_000));
        } else {
          await sleep(opts.pollMs);
        }
      }

      await client.close();
      break;
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      process.stderr.write(
        `mesh_casp_autopilot_client fail error=${JSON.stringify(msg)} backoff_ms=${backoffMs}\n`,
      );
      try {
        await client.close();
      } catch {
        // ignore
      }
      await sleep(backoffMs);
      backoffMs = Math.min(backoffMs * 2, 60_000);
    }
  }

  return 0;
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
