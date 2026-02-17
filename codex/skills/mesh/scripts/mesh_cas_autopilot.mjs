#!/usr/bin/env node
// Continual $mesh runner driven via cas (codex app-server).
//
// This avoids `codex exec` and does not require the automation DB.
// It runs $mesh in a persistent app-server thread on an interval.

import { createHash } from "node:crypto";
import { existsSync, readFileSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { CasClient } from "../../cas/scripts/cas_client.mjs";
import { computeBudgetGovernor, meshArgsForBudget } from "../../cas/scripts/budget_governor.mjs";

if (!process.env.UV_CACHE_DIR) {
  process.env.UV_CACHE_DIR = "/tmp/uv-cache";
}

function resolveStPlanScript() {
  const codexHome = process.env.CODEX_HOME ?? resolve(homedir(), ".codex");
  const claudeHome = process.env.CLAUDE_HOME ?? resolve(homedir(), ".claude");
  const codexStPlanScript = resolve(codexHome, "skills", "st", "scripts", "st_plan.py");
  if (existsSync(codexStPlanScript)) return codexStPlanScript;
  return resolve(claudeHome, "skills", "st", "scripts", "st_plan.py");
}

const ST_PLAN_SCRIPT = resolveStPlanScript();
const DEFAULT_ST_INIT_CMD = `uv run "${ST_PLAN_SCRIPT}" init --file .step/st-plan.jsonl`;
const ONE_SHOT_MIN_TIMEOUT_MS = 300_000;

function usage() {
  return [
    "mesh_cas_autopilot.mjs",
    "",
    "Runs $mesh continually via cas (codex app-server).",
    "",
    "Usage:",
    "  node codex/skills/mesh/scripts/mesh_cas_autopilot.mjs --cwd DIR [options]",
    "",
    "Required:",
    "  --cwd DIR                Workspace to run in.",
    "",
    "Options:",
    "  --plan-file PATH         Plan file path relative to --cwd (default: .step/st-plan.jsonl)",
    "  --poll-ms N              Sleep between runs (default: 60000)",
    "  --turn-timeout-ms N      Primary wait before timeout-recovery steer/reconcile (default: 2700000 = 45 min)",
    "  --state-file PATH        cas state file path (default: ~/.codex/cas/state/<cwd-hash>.json)",
    "  --budget-mode MODE       aware|all_out (default: aware)",
    "  --once                   Run once and exit",
    "  --verbose                Emit proxy stderr lines",
    "  --help                   Show help",
    "",
    "Notes:",
    "  - Requires `codex` on PATH (cas spawns `codex app-server`).",
    "  - Uses the local skill at codex/skills/mesh/.",
    "  - With --once, effective --turn-timeout-ms is clamped to at least 300000.",
  ].join("\n");
}

function parseArgs(argv) {
  const opts = {
    cwd: null,
    planFile: ".step/st-plan.jsonl",
    pollMs: 60_000,
    turnTimeoutMs: 45 * 60_000,
    stateFile: null,
    budgetMode: "aware",
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
    if (a === "--budget-mode") {
      opts.budgetMode = take();
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
  if (opts.budgetMode !== "aware" && opts.budgetMode !== "all_out") {
    throw new Error("--budget-mode must be one of: aware, all_out");
  }

  return { ok: true, help: false, error: null, opts };
}

function defaultStateFileForCwd(cwd) {
  const normalized = resolve(cwd);
  const digest = createHash("sha256").update(normalized).digest("hex").slice(0, 16);
  return resolve(homedir(), ".codex", "cas", "state", `${digest}.json`);
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

function utcCompact(date = new Date()) {
  const iso = date.toISOString();
  return iso.slice(0, 19).replace(/[-:]/g, "").replace(/\.\d+Z$/, "Z");
}

function ensureHeadlessPlanFile({ cwd, planFile }) {
  const planPath = resolve(cwd, planFile);
  if (existsSync(planPath)) return { ok: true, planPath };

  const initCmd =
    planFile === ".step/st-plan.jsonl"
      ? DEFAULT_ST_INIT_CMD
      : `uv run "${ST_PLAN_SCRIPT}" init --file ${planFile}`;
  process.stderr.write(
    `mesh_headless_stop headless_stop_reason=plan_missing plan_file=${planFile} action=${JSON.stringify(initCmd)}\n`,
  );
  return { ok: false, planPath };
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

  const startRes = await client.startThread({ cwd, experimentalRawEvents: true });
  const threadId = startRes?.thread?.id ?? null;
  if (!threadId) throw new Error("thread/start did not return thread.id");
  return threadId;
}

async function runMeshOnce({ client, threadId, planFile, meshSkillPath, timeoutMs, parallelTasks, maxTasks }) {
  const budgetSec = Math.max(30, Math.floor(timeoutMs / 1000));
  const pt = parallelTasks ?? "auto";
  const mt = maxTasks ?? "auto";
  const prompt = [
    `$mesh plan_file=${planFile} adapter=auto parallel_tasks=${pt} max_tasks=${mt} headless=true`,
    "",
    `Runtime budget: ${budgetSec}s for this turn.`,
    "Execution policy:",
    "- Prioritize completing at least one ready task.",
    "- If delegation latency is high, use the fallback 3-role swarm early.",
    "- If budget is nearly exhausted, emit current status and finish the turn.",
  ].join("\n");
  const timeoutSteerText = [
    "Timeout budget reached.",
    "Stop further exploration now and finalize this turn immediately.",
    "Return concise task status, validation outcomes, and next pending work.",
  ].join(" ");
  const input = [
    { type: "text", text: prompt, text_elements: [] },
    { type: "skill", name: "mesh", path: meshSkillPath },
  ];

  return client.startTurnAndCollect(
    {
      threadId,
      input,
    },
    {
      timeoutMs,
      onTimeoutSteerText: timeoutSteerText,
      timeoutSteerGraceMs: Math.max(15_000, Math.min(60_000, Math.floor(timeoutMs * 0.25))),
      timeoutSteerRequestTimeoutMs: 10_000,
    },
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
  if (opts.once && opts.turnTimeoutMs < ONE_SHOT_MIN_TIMEOUT_MS) {
    const requested = opts.turnTimeoutMs;
    opts.turnTimeoutMs = ONE_SHOT_MIN_TIMEOUT_MS;
    process.stderr.write(
      `mesh_timeout_clamp adapter=cas_autopilot mode=once field=turn_timeout_ms requested_ms=${requested} applied_ms=${opts.turnTimeoutMs} minimum_ms=${ONE_SHOT_MIN_TIMEOUT_MS}\n`,
    );
  }
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
    let capabilityBlocked = false;
    let capabilityReason = null;
    const client = new CasClient({
      cwd: opts.cwd,
      stateFile,
      clientName: "mesh-autopilot",
      clientTitle: "mesh cas autopilot",
      clientVersion: "0.1.0",
    });

    client.on("cas/error", (ev) => {
      const detail = ev?.error ? ` detail=${JSON.stringify(ev.error)}` : "";
      process.stderr.write(`[cas] error: ${ev?.message ?? "unknown"}${detail}\n`);
    });
    if (opts.verbose) {
      client.on("proxyStderr", (line) => {
        process.stderr.write(`[proxy] ${line}\n`);
      });
    }

    // Do not allow server-initiated requests to stall forever.
    client.on("cas/serverRequest", (ev) => {
      const method = typeof ev.method === "string" ? ev.method : "<unknown>";
      if (method === "item/tool/call") {
        capabilityBlocked = true;
        capabilityReason = "adapter_missing_capability";
        process.stderr.write(
          "mesh_adapter_capability adapter=cas_autopilot item_tool_call=unsupported headless=true\n",
        );
        client.respondError(ev.id, "adapter_missing_capability: dynamic tool calls unavailable in headless autopilot", {
          code: -32000,
          data: { method, reason: "adapter_missing_capability" },
        });
        return;
      }
      if (method === "item/tool/requestUserInput") {
        capabilityBlocked = true;
        capabilityReason = "adapter_missing_capability";
        process.stderr.write(
          "mesh_adapter_capability adapter=cas_autopilot request_user_input=unsupported headless=true\n",
        );
        client.respondError(ev.id, "User input not available in headless autopilot", {
          code: -32000,
          data: { method, reason: "adapter_missing_capability" },
        });
        return;
      }
      if (method === "account/chatgptAuthTokens/refresh") {
        client.respondError(ev.id, "Auth token refresh not implemented by mesh_cas_autopilot", {
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
      const planCheck = ensureHeadlessPlanFile({ cwd: opts.cwd, planFile: opts.planFile });
      if (!planCheck.ok) return 0;

      await client.start();
      backoffMs = 1_000;

      const threadId = await ensureThread({
        client,
        cwd: opts.cwd,
        stateFile,
      });

      process.stderr.write(
        `mesh_cas_autopilot_ready cwd=${opts.cwd} plan_file=${opts.planFile} state_file=${stateFile} thread_id=${threadId}\n`,
      );

      while (!stopping) {
        const meshRunId = utcCompact();

        let gov = null;
        let govErr = null;
        if (opts.budgetMode === "aware") {
          try {
            const resp = await client.request("account/rateLimits/read", {}, { timeoutMs: 20_000 });
            gov = computeBudgetGovernor(resp);
          } catch (err) {
            govErr = err instanceof Error ? err.message : String(err);
            gov = { tier: "unknown", usedPercent: null, elapsedPercent: null, deltaPercent: null, resetsAt: null };
          }
        } else {
          gov = { tier: "unknown", usedPercent: null, elapsedPercent: null, deltaPercent: null, resetsAt: null };
        }

        const meshBudget = meshArgsForBudget({ mode: opts.budgetMode, tier: gov?.tier });
        const elapsedPct = gov && Number.isFinite(gov.elapsedPercent) ? gov.elapsedPercent.toFixed(1) : "null";
        const deltaPct = gov && Number.isFinite(gov.deltaPercent) ? gov.deltaPercent.toFixed(1) : "null";

        process.stderr.write(
          `mesh_preflight mesh_run_id=${meshRunId} plan_file=${opts.planFile} adapter=cas_autopilot ids=none budget_mode=${opts.budgetMode} tier=${meshBudget.chosenTier} used_percent=${gov?.usedPercent ?? "null"} elapsed_percent=${elapsedPct} delta_percent=${deltaPct} resets_at=${gov?.resetsAt ?? "null"} overrides=max_tasks=${meshBudget.maxTasks},parallel_tasks=${meshBudget.parallelTasks}${govErr ? ` rate_limits_error=${JSON.stringify(govErr)}` : ""}\n`,
        );
        const startedAt = Date.now();
        let ok = false;
        try {
          const collected = await runMeshOnce({
            client,
            threadId,
            planFile: opts.planFile,
            meshSkillPath,
            timeoutMs: opts.turnTimeoutMs,
            parallelTasks: meshBudget.parallelTasks,
            maxTasks: meshBudget.maxTasks,
          });
          const status = collected?.turn?.status ?? null;
          const line = summarize(collected?.agentMessageText ?? "");
          const elapsedMs = Date.now() - startedAt;
          process.stderr.write(
            `mesh_cas_autopilot_run ok mesh_run_id=${meshRunId} status=${status ?? "null"} elapsed_ms=${elapsedMs} summary=${JSON.stringify(line)}\n`,
          );
          ok = true;
        } catch (err) {
          const elapsedMs = Date.now() - startedAt;
          const msg = err instanceof Error ? err.message : String(err);
          process.stderr.write(
            `mesh_cas_autopilot_run fail mesh_run_id=${meshRunId} elapsed_ms=${elapsedMs} error=${JSON.stringify(msg)}\n`,
          );
        }

        if (capabilityBlocked) {
          const reason = capabilityReason ?? "adapter_missing_capability";
          process.stderr.write(
            `mesh_headless_stop headless_stop_reason=${reason} delegation_did_not_run=true action=\"switch to worker-capable runtime/session and retry\"\n`,
          );
          stopping = true;
          break;
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
        `mesh_cas_autopilot_client fail error=${JSON.stringify(msg)} backoff_ms=${backoffMs}\n`,
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
