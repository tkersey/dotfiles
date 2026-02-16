#!/usr/bin/env node
// Fleet $mesh runner driven via casp (codex app-server).
//
// Design:
// - 1 integrator instance applies patches, runs validation, and mutates $st.
// - N worker instances run $mesh with integrate=false and return candidate diffs.
// - The fleet runner routes artifacts from workers -> integrator and drains ready work continually.

import { spawn } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { CaspClient } from "../../casp/scripts/casp_client.mjs";

function usage() {
  return [
    "mesh_casp_fleet_autopilot.mjs",
    "",
    "Runs $mesh continually using 1 integrator + N worker instances (casp).",
    "",
    "Usage:",
    "  node codex/skills/mesh/scripts/mesh_casp_fleet_autopilot.mjs --cwd DIR [options]",
    "",
    "Required:",
    "  --cwd DIR                    Workspace to run in.",
    "",
    "Options:",
    "  --plan-file PATH             Plan file path relative to --cwd (default: .step/st-plan.jsonl)",
    "  --workers N                  Worker instances (default: 3)",
    "  --poll-ms N                  Sleep when no work is ready (default: 60000)",
    "  --worker-turn-timeout-ms N   Max time for one worker $mesh turn (default: 1800000 = 30 min)",
    "  --integrator-turn-timeout-ms N  Max time for one integrator turn (default: 2700000 = 45 min)",
    "  --state-dir DIR              Directory for per-instance casp state files",
    "  --once                       Run one scheduling wave and exit",
    "  --verbose                    Emit proxy stderr lines",
    "  --help                       Show help",
    "",
    "Notes:",
    "  - Requires `uv` and `codex` on PATH.",
    "  - Worker instances run with sandboxPolicy=readOnly and file approvals declined.",
  ].join("\n");
}

function parseArgs(argv) {
  const opts = {
    cwd: null,
    planFile: ".step/st-plan.jsonl",
    workers: 3,
    pollMs: 60_000,
    workerTurnTimeoutMs: 30 * 60_000,
    integratorTurnTimeoutMs: 45 * 60_000,
    stateDir: null,
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
    if (a === "--workers") {
      opts.workers = Number(take());
      continue;
    }
    if (a === "--poll-ms") {
      opts.pollMs = Number(take());
      continue;
    }
    if (a === "--worker-turn-timeout-ms") {
      opts.workerTurnTimeoutMs = Number(take());
      continue;
    }
    if (a === "--integrator-turn-timeout-ms") {
      opts.integratorTurnTimeoutMs = Number(take());
      continue;
    }
    if (a === "--state-dir") {
      opts.stateDir = take();
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
  if (!Number.isInteger(opts.workers) || opts.workers < 0) {
    throw new Error("--workers must be an integer >= 0");
  }
  if (!Number.isInteger(opts.pollMs) || opts.pollMs < 0) {
    throw new Error("--poll-ms must be an integer >= 0");
  }
  if (!Number.isInteger(opts.workerTurnTimeoutMs) || opts.workerTurnTimeoutMs <= 0) {
    throw new Error("--worker-turn-timeout-ms must be a positive integer");
  }
  if (!Number.isInteger(opts.integratorTurnTimeoutMs) || opts.integratorTurnTimeoutMs <= 0) {
    throw new Error("--integrator-turn-timeout-ms must be a positive integer");
  }
  if (typeof opts.planFile !== "string" || !opts.planFile.trim()) {
    throw new Error("--plan-file must be a non-empty string");
  }
  if (opts.stateDir !== null && (typeof opts.stateDir !== "string" || !opts.stateDir.trim())) {
    throw new Error("--state-dir must be a non-empty string");
  }

  return { ok: true, help: false, error: null, opts };
}

function cwdHash(cwd) {
  const normalized = resolve(cwd);
  return createHash("sha256").update(normalized).digest("hex").slice(0, 16);
}

function defaultFleetStateDir(cwd) {
  const digest = cwdHash(cwd);
  return resolve(homedir(), ".codex", "casp", "state", "mesh-fleet", digest);
}

function stateFileForInstance(stateDir, name) {
  return resolve(stateDir, `${name}.json`);
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
    return cleaned.slice(0, 220);
  }
  return "";
}

function extractDiff(text) {
  if (typeof text !== "string" || !text) return null;

  const fenceIdx = text.indexOf("```diff");
  if (fenceIdx !== -1) {
    const after = text.slice(fenceIdx + "```diff".length);
    const end = after.indexOf("```");
    if (end !== -1) {
      const body = after.slice(0, end).replace(/^\n/, "");
      const trimmed = body.trim();
      if (trimmed) return trimmed;
    }
  }

  const lines = text.split("\n");
  let start = -1;
  for (let i = 0; i < lines.length; i += 1) {
    if (lines[i].startsWith("diff --git ")) {
      start = i;
      break;
    }
  }
  if (start !== -1) {
    const body = lines.slice(start).join("\n").trim();
    return body || null;
  }

  return null;
}

function extractMeshScopeFromNotes(notes) {
  if (typeof notes !== "string" || !notes) return { scope: null, hasGlobs: false };
  const start = notes.indexOf("```mesh");
  if (start === -1) return { scope: null, hasGlobs: false };
  const after = notes.slice(start + "```mesh".length);
  const end = after.indexOf("```");
  if (end === -1) return { scope: null, hasGlobs: false };
  const block = after.slice(0, end);

  const scope = [];
  let inScope = false;
  for (const rawLine of block.split("\n")) {
    const line = rawLine.replace(/\r$/, "");
    const trimmed = line.trim();
    if (!trimmed) continue;

    if (/^[a-zA-Z_][a-zA-Z0-9_]*\s*:/.test(trimmed)) {
      inScope = trimmed.startsWith("scope:");
      continue;
    }
    if (!inScope) continue;
    if (!trimmed.startsWith("-")) continue;
    let v = trimmed.slice(1).trim();
    if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) {
      v = v.slice(1, -1);
    }
    if (v) scope.push(v);
  }

  if (!scope.length) return { scope: null, hasGlobs: false };
  const hasGlobs = scope.some((p) => /[*?\[]/.test(p));
  return { scope, hasGlobs };
}

function scopesDisjoint(a, b) {
  if (!a || !b) return false;
  for (const p of a) {
    if (b.includes(p)) return false;
  }
  return true;
}

function runJsonCommand(cmd, args, opts = {}) {
  const cwd = opts.cwd ?? process.cwd();
  const timeoutMs = opts.timeoutMs ?? 60_000;

  return new Promise((resolve, reject) => {
    const child = spawn(cmd, args, {
      cwd,
      stdio: ["ignore", "pipe", "pipe"],
      env: { ...process.env },
    });

    let stdout = "";
    let stderr = "";
    const timer =
      timeoutMs > 0
        ? setTimeout(() => {
            child.kill("SIGKILL");
            reject(new Error(`Timed out: ${cmd} ${args.join(" ")}`));
          }, timeoutMs)
        : null;

    child.stdout?.on("data", (buf) => {
      stdout += buf.toString("utf-8");
    });
    child.stderr?.on("data", (buf) => {
      stderr += buf.toString("utf-8");
    });
    child.on("error", (err) => {
      if (timer) clearTimeout(timer);
      reject(err);
    });
    child.on("exit", (code) => {
      if (timer) clearTimeout(timer);
      if (code !== 0) {
        reject(new Error(`Command failed (${code}): ${stderr.trim() || stdout.trim()}`));
        return;
      }
      try {
        resolve(JSON.parse(stdout));
      } catch (err) {
        reject(new Error(`Failed to parse JSON output: ${err instanceof Error ? err.message : String(err)}`));
      }
    });
  });
}

async function readPlanSnapshot({ cwd, planFileRel, stScriptPath }) {
  const planPath = resolve(cwd, planFileRel);
  if (!existsSync(planPath)) {
    return { ok: false, error: `plan_missing:${planPath}`, planPath, items: [] };
  }

  const payload = await runJsonCommand(
    "uv",
    [
      "run",
      stScriptPath,
      "show",
      "--file",
      planPath,
      "--allow-multiple-in-progress",
      "--format",
      "json",
    ],
    { cwd },
  );
  const items = Array.isArray(payload?.items) ? payload.items : [];
  return { ok: true, error: null, planPath, items };
}

async function ensureThread({ client, cwd, stateFile, startParams = {} }) {
  const existing = readCurrentThreadId(stateFile);
  if (existing) {
    try {
      await client.resumeThread({ threadId: existing });
      return existing;
    } catch {
      // Fall through to start a new thread.
    }
  }

  const params = { ...(typeof startParams === "object" && startParams ? startParams : {}), cwd };
  const startRes = await client.startThread(params);
  const threadId = startRes?.thread?.id ?? null;
  if (!threadId) throw new Error("thread/start did not return thread.id");
  return threadId;
}

async function runWorkerMesh({
  client,
  threadId,
  taskId,
  planFileRel,
  meshSkillPath,
  absCwd,
  timeoutMs,
}) {
  const prompt = `$mesh ids=${taskId} plan_file=${planFileRel} integrate=false adapter=auto parallel_tasks=1 max_tasks=1 headless=true`;
  const input = [
    { type: "text", text: prompt, text_elements: [] },
    { type: "skill", name: "mesh", path: meshSkillPath },
  ];

  // Constrain worker instances to read-only filesystem access.
  const sandboxPolicy = {
    type: "readOnly",
    access: {
      type: "restricted",
      includePlatformDefaults: true,
      readableRoots: [absCwd],
    },
  };

  return client.startTurnAndCollect(
    {
      threadId,
      input,
      sandboxPolicy,
    },
    { timeoutMs },
  );
}

async function runIntegratorMeshFull({
  client,
  threadId,
  taskId,
  planFileRel,
  meshSkillPath,
  timeoutMs,
}) {
  const prompt = `$mesh ids=${taskId} plan_file=${planFileRel} adapter=auto parallel_tasks=1 max_tasks=1 headless=true`;
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

async function runIntegratorApply({
  client,
  threadId,
  taskId,
  planFileRel,
  meshSkillPath,
  diffText,
  timeoutMs,
}) {
  const prompt = [
    `$mesh ids=${taskId} plan_file=${planFileRel} adapter=auto parallel_tasks=1 max_tasks=1 headless=true`,
    "",
    "Integrator override:",
    "- Skip proposal/critique/synthesis/vote.",
    "- Treat the patch below as the synthesized diff and go directly to integration + validation + persistence.",
    "- If the patch does not apply cleanly, fall back to running full $mesh for this id.",
    "",
    "Patch:",
    "```diff",
    diffText.trimEnd(),
    "```",
  ].join("\n");

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
  const absCwd = resolve(opts.cwd);
  const stateDir = resolve(opts.stateDir ?? defaultFleetStateDir(absCwd));
  mkdirSync(stateDir, { recursive: true });

  // Prevent two fleet runners from sharing the same casp state files.
  const lockPath = resolve(stateDir, "fleet.lock.json");
  if (existsSync(lockPath)) {
    try {
      const prev = JSON.parse(readFileSync(lockPath, "utf-8"));
      const prevPid = Number(prev?.pid);
      if (Number.isInteger(prevPid) && prevPid > 1) {
        process.kill(prevPid, 0);
        process.stderr.write(
          `mesh_fleet_lock_held state_dir=${stateDir} pid=${prevPid}\n`,
        );
        return 2;
      }
    } catch {
      process.stderr.write(`mesh_fleet_lock_unreadable state_dir=${stateDir}\n`);
      return 2;
    }
  }
  writeFileSync(
    lockPath,
    JSON.stringify({ pid: process.pid, startedAt: new Date().toISOString() }, null, 2) + "\n",
    "utf-8",
  );

  const here = dirname(fileURLToPath(import.meta.url));
  const meshSkillPath = resolve(here, "..");
  const stScriptPath = resolve(here, "..", "..", "st", "scripts", "st_plan.py");

  const integratorStateFile = stateFileForInstance(stateDir, "integrator");
  const integrator = {
    name: "integrator",
    stateFile: integratorStateFile,
    client: new CaspClient({
      cwd: absCwd,
      stateFile: integratorStateFile,
      clientName: "mesh-fleet-integrator",
      clientTitle: "mesh casp fleet integrator",
      clientVersion: "0.1.0",
    }),
    threadId: null,
    busy: false,
  };

  /** @type {Array<{name: string, stateFile: string, client: any, threadId: string|null, busy: boolean}>} */
  const workers = Array.from({ length: opts.workers }, (_, i) => {
    const name = `worker-${i + 1}`;
    const stateFile = stateFileForInstance(stateDir, name);
    const client = new CaspClient({
      cwd: absCwd,
      stateFile,
      clientName: `mesh-fleet-${name}`,
      clientTitle: "mesh casp fleet worker",
      clientVersion: "0.1.0",
      // Allow commands (for reading/search), but decline file writes.
      execApprovalDecision: "acceptForSession",
      fileApprovalDecision: "decline",
    });
    return { name, stateFile, client, threadId: null, busy: false };
  });

  let stopping = false;
  process.on("SIGINT", () => {
    stopping = true;
  });
  process.on("SIGTERM", () => {
    stopping = true;
  });

  function wireClientLogs(prefix, client) {
    client.on("casp/error", (ev) => {
      process.stderr.write(`[${prefix}] casp/error: ${ev?.message ?? "unknown"}\n`);
    });
    if (opts.verbose) {
      client.on("proxyStderr", (line) => {
        process.stderr.write(`[${prefix}] proxy: ${line}\n`);
      });
    }
  }

  wireClientLogs(integrator.name, integrator.client);
  for (const w of workers) wireClientLogs(w.name, w.client);

  // If the server asks for dynamic tools/user input/auth refresh, fail deterministically.
  // (We rely on casp's built-in approval auto-handling for approvals.)
  function installHeadlessServerRequestPolicy(prefix, client) {
    client.on("casp/serverRequest", (ev) => {
      const method = typeof ev.method === "string" ? ev.method : "<unknown>";
      if (method === "item/tool/call") {
        client.respondError(ev.id, `${prefix}: tool calls not implemented`, {
          code: -32000,
          data: { method },
        });
        return;
      }
      if (method === "item/tool/requestUserInput") {
        client.respondError(ev.id, `${prefix}: user input unavailable in fleet autopilot`, {
          code: -32000,
          data: { method },
        });
        return;
      }
      if (method === "account/chatgptAuthTokens/refresh") {
        client.respondError(ev.id, `${prefix}: auth refresh not implemented`, {
          code: -32000,
          data: { method },
        });
        return;
      }
      client.respondError(ev.id, `${prefix}: unhandled server request: ${method}`, {
        code: -32601,
        data: { method },
      });
    });
  }

  installHeadlessServerRequestPolicy("integrator", integrator.client);
  for (const w of workers) installHeadlessServerRequestPolicy(w.name, w.client);

  async function restartInstance(instance, makeClient, startParams) {
    const prior = instance.client;
    try {
      await prior.close();
    } catch {
      // ignore
    }

    instance.client = makeClient();
    wireClientLogs(instance.name, instance.client);
    installHeadlessServerRequestPolicy(instance.name, instance.client);
    await instance.client.start();
    instance.threadId = await ensureThread({
      client: instance.client,
      cwd: absCwd,
      stateFile: instance.stateFile,
      startParams,
    });
  }

  // Start all instances.
  await Promise.all([integrator.client.start(), ...workers.map((w) => w.client.start())]);
  integrator.threadId = await ensureThread({
    client: integrator.client,
    cwd: absCwd,
    stateFile: integrator.stateFile,
    startParams: { sandbox: "workspace-write" },
  });
  for (const w of workers) {
    w.threadId = await ensureThread({
      client: w.client,
      cwd: absCwd,
      stateFile: w.stateFile,
      startParams: { sandbox: "read-only" },
    });
  }

  process.stderr.write(
    `mesh_casp_fleet_autopilot_ready cwd=${absCwd} plan_file=${opts.planFile} workers=${workers.length} state_dir=${stateDir} integrator_thread=${integrator.threadId}\n`,
  );

  /** @type {Set<string>} */
  const reservedTaskIds = new Set();
  /** @type {Array<{id: string, step: string, notes: string|null, scope: string[]|null, hasGlobs: boolean}>} */
  let queue = [];

  /** @type {Map<string, { worker: any, taskId: string, startedAt: number, promise: Promise<any> }>} */
  const inflight = new Map();

  async function refreshQueue() {
    const snapshot = await readPlanSnapshot({ cwd: absCwd, planFileRel: opts.planFile, stScriptPath });
    if (!snapshot.ok) {
      process.stderr.write(`mesh_casp_fleet_autopilot_no_plan plan_file=${opts.planFile} path=${snapshot.planPath}\n`);
      return [];
    }

    const items = snapshot.items;
    const inProgress = items.filter((it) => it?.status === "in_progress");
    const ready = items.filter((it) => it?.status === "pending" && it?.dep_state === "ready");

    const candidates = (inProgress.length ? inProgress : ready)
      .filter((it) => it && typeof it.id === "string" && it.id)
      .map((it) => {
        const notes = typeof it.notes === "string" ? it.notes : null;
        const { scope, hasGlobs } = extractMeshScopeFromNotes(notes);
        return {
          id: it.id,
          step: typeof it.step === "string" ? it.step : "",
          notes,
          scope,
          hasGlobs,
        };
      });

    return candidates;
  }

  function dequeueWork(freeWorkers) {
    const assigned = [];
    const usedScopes = [];

    for (const w of freeWorkers) {
      let pickIdx = -1;
      for (let i = 0; i < queue.length; i += 1) {
        const t = queue[i];
        if (reservedTaskIds.has(t.id)) continue;

        // If any scope is unknown or globbed, treat as conflicting with everything.
        if (!t.scope || t.hasGlobs) {
          if (assigned.length > 0) continue;
          pickIdx = i;
          break;
        }

        let ok = true;
        for (const s of usedScopes) {
          if (!scopesDisjoint(t.scope, s)) {
            ok = false;
            break;
          }
        }
        if (!ok) continue;
        pickIdx = i;
        break;
      }

      if (pickIdx === -1) break;
      const task = queue.splice(pickIdx, 1)[0];
      reservedTaskIds.add(task.id);
      if (task.scope && !task.hasGlobs) usedScopes.push(task.scope);
      assigned.push({ worker: w, task });
    }

    return assigned;
  }

  async function runWorkerTask(worker, task) {
    const startedAt = Date.now();
    worker.busy = true;

    try {
      const collected = await runWorkerMesh({
        client: worker.client,
        threadId: worker.threadId,
        taskId: task.id,
        planFileRel: opts.planFile,
        meshSkillPath,
        absCwd,
        timeoutMs: opts.workerTurnTimeoutMs,
      });

      const elapsedMs = Date.now() - startedAt;
      const msg = collected?.agentMessageText ?? "";
      const diff = extractDiff(msg);
      const summaryLine = summarize(msg);

      process.stderr.write(
        `mesh_fleet_worker_done worker=${worker.name} task=${task.id} elapsed_ms=${elapsedMs} has_diff=${diff ? "yes" : "no"} summary=${JSON.stringify(summaryLine)}\n`,
      );

      return {
        ok: Boolean(diff),
        taskId: task.id,
        worker: worker.name,
        elapsedMs,
        diff,
        raw: msg,
        error: null,
      };
    } catch (err) {
      const elapsedMs = Date.now() - startedAt;
      const msg = err instanceof Error ? err.message : String(err);

      process.stderr.write(
        `mesh_fleet_worker_fail worker=${worker.name} task=${task.id} elapsed_ms=${elapsedMs} error=${JSON.stringify(msg)}\n`,
      );

      // One restart+retry attempt.
      try {
        await restartInstance(
          worker,
          () =>
            new CaspClient({
              cwd: absCwd,
              stateFile: worker.stateFile,
              clientName: `mesh-fleet-${worker.name}`,
              clientTitle: "mesh casp fleet worker",
              clientVersion: "0.1.0",
              execApprovalDecision: "acceptForSession",
              fileApprovalDecision: "decline",
            }),
          { sandbox: "read-only" },
        );

        const collected = await runWorkerMesh({
          client: worker.client,
          threadId: worker.threadId,
          taskId: task.id,
          planFileRel: opts.planFile,
          meshSkillPath,
          absCwd,
          timeoutMs: opts.workerTurnTimeoutMs,
        });

        const retryMsg = collected?.agentMessageText ?? "";
        const diff = extractDiff(retryMsg);
        const summaryLine = summarize(retryMsg);

        process.stderr.write(
          `mesh_fleet_worker_retry_done worker=${worker.name} task=${task.id} has_diff=${diff ? "yes" : "no"} summary=${JSON.stringify(summaryLine)}\n`,
        );

        return {
          ok: Boolean(diff),
          taskId: task.id,
          worker: worker.name,
          elapsedMs: Date.now() - startedAt,
          diff,
          raw: retryMsg,
          error: diff ? null : msg,
        };
      } catch (err2) {
        const msg2 = err2 instanceof Error ? err2.message : String(err2);
        return {
          ok: false,
          taskId: task.id,
          worker: worker.name,
          elapsedMs,
          diff: null,
          raw: "",
          error: msg2,
        };
      }
    } finally {
      worker.busy = false;
    }
  }

  async function integrateOne(result) {
    if (!result.diff) {
      // Fallback: have the integrator attempt the task normally.
      if (integrator.busy) {
        while (integrator.busy && !stopping) await sleep(250);
      }
      if (stopping) return;

      integrator.busy = true;
      const startedAt = Date.now();
      try {
        const collected = await runIntegratorMeshFull({
          client: integrator.client,
          threadId: integrator.threadId,
          taskId: result.taskId,
          planFileRel: opts.planFile,
          meshSkillPath,
          timeoutMs: opts.integratorTurnTimeoutMs,
        });
        const elapsedMs = Date.now() - startedAt;
        const status = collected?.turn?.status ?? null;
        const summaryLine = summarize(collected?.agentMessageText ?? "");
        process.stderr.write(
          `mesh_fleet_integrator_fallback task=${result.taskId} from=${result.worker} elapsed_ms=${elapsedMs} status=${status ?? "null"} summary=${JSON.stringify(summaryLine)}\n`,
        );
      } catch (err) {
        const elapsedMs = Date.now() - startedAt;
        const msg = err instanceof Error ? err.message : String(err);
        process.stderr.write(
          `mesh_fleet_integrator_fallback_fail task=${result.taskId} from=${result.worker} elapsed_ms=${elapsedMs} error=${JSON.stringify(msg)}\n`,
        );
      } finally {
        integrator.busy = false;
      }
      return;
    }
    if (integrator.busy) {
      // Simple backpressure: wait until integrator is free.
      while (integrator.busy && !stopping) await sleep(250);
    }
    if (stopping) return;

    integrator.busy = true;
    const startedAt = Date.now();
    try {
      const collected = await runIntegratorApply({
        client: integrator.client,
        threadId: integrator.threadId,
        taskId: result.taskId,
        planFileRel: opts.planFile,
        meshSkillPath,
        diffText: result.diff,
        timeoutMs: opts.integratorTurnTimeoutMs,
      });
      const elapsedMs = Date.now() - startedAt;
      const status = collected?.turn?.status ?? null;
      const summaryLine = summarize(collected?.agentMessageText ?? "");
      process.stderr.write(
        `mesh_fleet_integrated task=${result.taskId} from=${result.worker} elapsed_ms=${elapsedMs} status=${status ?? "null"} summary=${JSON.stringify(summaryLine)}\n`,
      );
    } catch (err) {
      const elapsedMs = Date.now() - startedAt;
      const msg = err instanceof Error ? err.message : String(err);
      process.stderr.write(
        `mesh_fleet_integrate_fail task=${result.taskId} from=${result.worker} elapsed_ms=${elapsedMs} error=${JSON.stringify(msg)}\n`,
      );
    } finally {
      integrator.busy = false;
    }
  }

  async function schedulingWave() {
    // Fill the queue.
    const candidates = await refreshQueue();
    const candidateIds = new Set(candidates.map((c) => c.id));
    queue = queue.filter((q) => candidateIds.has(q.id));
    for (const c of candidates) {
      if (reservedTaskIds.has(c.id)) continue;
      if (queue.find((q) => q.id === c.id)) continue;
      queue.push(c);
    }

    // Spawn worker runs.
    const free = workers.filter((w) => !w.busy && !inflight.has(w.name));
    const assigned = dequeueWork(free);
    for (const { worker, task } of assigned) {
      const p = runWorkerTask(worker, task);
      inflight.set(worker.name, { worker, taskId: task.id, startedAt: Date.now(), promise: p });
    }

    if (inflight.size === 0) return false;

    // Wait for at least one worker to finish.
    const raced = await Promise.race(
      Array.from(inflight.values()).map((slot) =>
        slot.promise
          .then((res) => ({ slot, ok: true, res }))
          .catch((err) => ({ slot, ok: false, err })),
      ),
    );

    inflight.delete(raced.slot.worker.name);
    reservedTaskIds.delete(raced.slot.taskId);

    if (!raced.ok) {
      const msg = raced.err instanceof Error ? raced.err.message : String(raced.err);
      process.stderr.write(
        `mesh_fleet_worker_promise_rejected worker=${raced.slot.worker.name} task=${raced.slot.taskId} error=${JSON.stringify(msg)}\n`,
      );
      return true;
    }

    await integrateOne(raced.res);
    return true;
  }

  let didAnyWork = false;
  while (!stopping) {
    let progressed = false;
    try {
      progressed = await schedulingWave();
      if (progressed) didAnyWork = true;
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      process.stderr.write(`mesh_fleet_wave_error error=${JSON.stringify(msg)}\n`);
    }

    if (opts.once) break;

    if (!progressed) {
      if (opts.pollMs > 0) await sleep(opts.pollMs);
      else await sleep(1_000);
    }
  }

  // Close instances.
  await Promise.allSettled([integrator.client.close(), ...workers.map((w) => w.client.close())]);
  process.stderr.write(`mesh_casp_fleet_autopilot_exit did_any_work=${didAnyWork ? "yes" : "no"}\n`);
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
