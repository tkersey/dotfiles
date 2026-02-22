#!/usr/bin/env node
// Fleet $mesh runner driven via cas (codex app-server).
//
// Design:
// - 1 join instance applies patches, runs validation, and mutates $st.
// - N worker instances run $mesh with integrate=false and return candidate diffs.
// - The fleet runner routes artifacts from workers -> join and drains ready work continually.

import { spawn } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, unlinkSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { CasClient } from "../../cas/scripts/cas_client.mjs";
import { computeBudgetGovernor, effectiveWorkersForBudget } from "../../cas/scripts/budget_governor.mjs";
import { classifyMeshOutput } from "./mesh_worker_output_parser.mjs";

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
const LOCK_TTL_MS = 5 * 60_000;
const WORKER_MAX_ATTEMPTS = 2;
const BUDGET_REFRESH_MS = 60_000;
const ONE_SHOT_MIN_TIMEOUT_MS = 300_000;
const WORKER_ATTEMPT_WATCHDOG_GRACE_MS = 90_000;
const WORKER_ATTEMPT_WATCHDOG_MIN_MS = 240_000;
const TEST_WORKER_ATTEMPT_WATCHDOG_MS = (() => {
  const raw = process.env.MESH_CAS_TEST_WORKER_WATCHDOG_MS;
  if (!raw) return null;
  const n = Number(raw);
  return Number.isInteger(n) && n > 0 ? n : null;
})();

function usage() {
  return [
    "mesh_cas_fleet_autopilot.mjs",
    "",
    "Runs $mesh continually using 1 join + N worker instances (cas).",
    "",
    "Usage:",
    "  node codex/skills/mesh/scripts/mesh_cas_fleet_autopilot.mjs --cwd DIR [options]",
    "",
    "Required:",
    "  --cwd DIR                    Workspace to run in.",
    "",
    "Options:",
    "  --plan-file PATH             Plan file path relative to --cwd (default: .step/st-plan.jsonl)",
    "  --workers N                  Worker instances (default: 3)",
    "  --poll-ms N                  Sleep when no work is ready (default: 60000)",
    "  --worker-turn-timeout-ms N   Primary wait before timeout-recovery for one worker turn (default: 1800000 = 30 min)",
    "  --join-turn-timeout-ms N  Primary wait before timeout-recovery for one join turn (default: 2700000 = 45 min)",
    "  --state-dir DIR              Directory for per-instance cas state files",
    "  --budget-mode MODE           aware|all_out (default: aware)",
    "  --once                       Run one scheduling wave and exit",
    "  --verbose                    Emit proxy stderr lines",
    "  --help                       Show help",
    "",
    "Notes:",
    "  - Requires `uv` and `codex` on PATH.",
    "  - Worker instances run with sandboxPolicy=readOnly and file approvals declined.",
    "  - With --once, effective worker/join timeout values are clamped to at least 300000.",
  ].join("\n");
}

function parseArgs(argv) {
  const opts = {
    cwd: null,
    planFile: ".step/st-plan.jsonl",
    workers: 3,
    pollMs: 60_000,
    workerTurnTimeoutMs: 30 * 60_000,
    joinTurnTimeoutMs: 45 * 60_000,
    stateDir: null,
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
    if (a === "--join-turn-timeout-ms") {
      opts.joinTurnTimeoutMs = Number(take());
      continue;
    }
    if (a === "--state-dir") {
      opts.stateDir = take();
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
  if (!Number.isInteger(opts.workers) || opts.workers < 0) {
    throw new Error("--workers must be an integer >= 0");
  }
  if (!Number.isInteger(opts.pollMs) || opts.pollMs < 0) {
    throw new Error("--poll-ms must be an integer >= 0");
  }
  if (!Number.isInteger(opts.workerTurnTimeoutMs) || opts.workerTurnTimeoutMs <= 0) {
    throw new Error("--worker-turn-timeout-ms must be a positive integer");
  }
  if (!Number.isInteger(opts.joinTurnTimeoutMs) || opts.joinTurnTimeoutMs <= 0) {
    throw new Error("--join-turn-timeout-ms must be a positive integer");
  }
  if (typeof opts.planFile !== "string" || !opts.planFile.trim()) {
    throw new Error("--plan-file must be a non-empty string");
  }
  if (opts.stateDir !== null && (typeof opts.stateDir !== "string" || !opts.stateDir.trim())) {
    throw new Error("--state-dir must be a non-empty string");
  }
  if (opts.budgetMode !== "aware" && opts.budgetMode !== "all_out") {
    throw new Error("--budget-mode must be one of: aware, all_out");
  }

  return { ok: true, help: false, error: null, opts };
}

function cwdHash(cwd) {
  const normalized = resolve(cwd);
  return createHash("sha256").update(normalized).digest("hex").slice(0, 16);
}

function defaultFleetStateDir(cwd) {
  const digest = cwdHash(cwd);
  return resolve(homedir(), ".codex", "cas", "state", "mesh-fleet", digest);
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

function workerAttemptWatchdogMs(turnTimeoutMs) {
  if (TEST_WORKER_ATTEMPT_WATCHDOG_MS !== null) return TEST_WORKER_ATTEMPT_WATCHDOG_MS;
  return Math.max(WORKER_ATTEMPT_WATCHDOG_MIN_MS, turnTimeoutMs + WORKER_ATTEMPT_WATCHDOG_GRACE_MS);
}

async function withWatchdog(promiseFactory, timeoutMs, timeoutCode) {
  let timer = null;
  try {
    return await Promise.race([
      promiseFactory(),
      new Promise((_, reject) => {
        timer = setTimeout(() => reject(new Error(`${timeoutCode}:${timeoutMs}`)), timeoutMs);
      }),
    ]);
  } finally {
    if (timer) clearTimeout(timer);
  }
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

function orchestrationEvidenceFlags(text) {
  const source = typeof text === "string" ? text : "";
  const lifecycle =
    /\bspawn(?:_agent)?\b/i.test(source) && /\bwait\b/i.test(source) && /\bclose(?:_agent)?\b/i.test(source);
  const waitAllIds =
    /\bwait\s*\(\s*ids\s*=\s*\[[^\]]+\]/i.test(source) ||
    /\bone wait call\b[\s\S]{0,80}\ball (?:active|running) ids\b/i.test(source) ||
    /\bsingle wait\b[\s\S]{0,80}\ball (?:active|running) ids\b/i.test(source);
  const retryLadder =
    /\bretry\b[\s\S]{0,160}\bspawn\b[\s\S]{0,120}\bwait\b[\s\S]{0,120}\bclose\b/i.test(source) ||
    /\bspawn\b[\s\S]{0,120}\bwait\b[\s\S]{0,120}\bclose\b[\s\S]{0,160}\bretry\b/i.test(source);
  const highFanoutCas =
    /\b(high[- ]fanout|as many subagents|as many shards|local cap pressure|cap pressure)\b/i.test(source) &&
    /\b(\$cas|adapter=cas|mesh_cas_fleet_autopilot|cas fleet)\b/i.test(source);
  return { lifecycle, waitAllIds, retryLadder, highFanoutCas };
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

function normalizeScopePath(rawPath) {
  if (typeof rawPath !== "string") return "";
  const normalized = rawPath
    .trim()
    .replace(/\\/g, "/")
    .replace(/^\.\/+/, "")
    .replace(/\/+/g, "/")
    .replace(/\/$/, "");
  return normalized;
}

function isGlobPattern(path) {
  return /[*?\[]/.test(path);
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
    const normalized = normalizeScopePath(v);
    if (normalized) scope.push(normalized);
  }

  if (!scope.length) return { scope: null, hasGlobs: false };
  const deduped = Array.from(new Set(scope));
  const hasGlobs = deduped.some((p) => isGlobPattern(p));
  return { scope: deduped, hasGlobs };
}

function scopesDisjoint(a, b) {
  if (!a || !b) return false;
  for (const left of a) {
    for (const right of b) {
      if (isGlobPattern(left) || isGlobPattern(right)) return false;
      if (left === right) return false;
      if (left.startsWith(`${right}/`) || right.startsWith(`${left}/`)) return false;
    }
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

  const params = {
    ...(typeof startParams === "object" && startParams ? startParams : {}),
    cwd,
    experimentalRawEvents: true,
  };
  const startRes = await client.startThread(params);
  const threadId = startRes?.thread?.id ?? null;
  if (!threadId) throw new Error("thread/start did not return thread.id");
  return threadId;
}

function meshTimeoutSteerOptions({ timeoutMs, role }) {
  const roleLabel = typeof role === "string" && role ? role : "mesh";
  const steerText = [
    `Timeout budget reached for ${roleLabel}.`,
    "Stop further exploration now and finalize this turn immediately.",
    "Return concise task status, validation outcomes, and next pending work.",
  ].join(" ");

  return {
    timeoutMs,
    onTimeoutSteerText: steerText,
    timeoutSteerGraceMs: Math.max(15_000, Math.min(60_000, Math.floor(timeoutMs * 0.25))),
    timeoutSteerRequestTimeoutMs: 10_000,
  };
}

async function runWorkerMesh({
  client,
  threadId,
  taskId,
  planFileRel,
  meshSkillPath,
  absCwd,
  timeoutMs,
  attempt = 1,
}) {
  const budgetSec = Math.max(30, Math.floor(timeoutMs / 1000));
  const retryStrictness =
    attempt > 1
      ? [
          "",
          "Retry mode output contract:",
          "- Return ONLY one fenced ```diff``` patch, OR exactly one line `NO_DIFF:<reason>`.",
          "- `<reason>` is required and must be non-empty plain text (1-220 chars).",
          "- Do not return status headings, JSON, or extra lines.",
          "- Never return empty output.",
        ]
      : [];
  const prompt = [
    `$mesh ids=${taskId} plan_file=${planFileRel} integrate=false adapter=auto parallel_tasks=1 max_tasks=1 headless=true`,
    "",
    `Runtime budget: ${budgetSec}s for this worker turn.`,
    "Execution policy:",
    "- Focus on this task id only and return concise diff/status quickly.",
    "- If delegation latency is high, use fallback 3-role swarm early.",
    "- If budget is nearly exhausted, finalize immediately with current best result.",
    "Orchestration evidence (required):",
    "- Report spawn/wait/close lifecycle evidence for this task.",
    "- Use one wait call over all active ids before proceeding.",
    "- If retries occur, report the retry ladder as spawn -> wait -> close.",
    "- If high-fanout intent plus local cap pressure occurs, state whether you escalated to $cas and why.",
    "Output contract:",
    "- If you produce a patch candidate, emit exactly one unified diff in a fenced ```diff``` block and nothing else.",
    "- If no safe patch can be produced, emit exactly one line in the form `NO_DIFF:<reason>`.",
    "- `<reason>` must be a single concise clause (1-220 chars), with no surrounding quotes.",
    ...retryStrictness,
  ].join("\n");
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
    meshTimeoutSteerOptions({ timeoutMs, role: "worker mesh run" }),
  );
}

async function runJoinMeshFull({
  client,
  threadId,
  taskId,
  planFileRel,
  meshSkillPath,
  timeoutMs,
}) {
  const budgetSec = Math.max(30, Math.floor(timeoutMs / 1000));
  const prompt = [
    `$mesh ids=${taskId} plan_file=${planFileRel} adapter=auto parallel_tasks=1 max_tasks=1 headless=true`,
    "",
    `Runtime budget: ${budgetSec}s for this join turn.`,
    "Execution policy:",
    "- Prioritize integration and validation for this task id.",
    "- If budget is nearly exhausted, finalize with explicit status and stop.",
    "Orchestration evidence (required):",
    "- Report spawn/wait/close lifecycle evidence for this task.",
    "- Use one wait call over all active ids before proceeding.",
    "- If retries occur, report the retry ladder as spawn -> wait -> close.",
    "- If high-fanout intent plus local cap pressure occurs, state whether you escalated to $cas and why.",
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
    meshTimeoutSteerOptions({ timeoutMs, role: "join mesh run" }),
  );
}

async function runJoinApply({
  client,
  threadId,
  taskId,
  planFileRel,
  meshSkillPath,
  diffText,
  timeoutMs,
}) {
  const budgetSec = Math.max(30, Math.floor(timeoutMs / 1000));
  const prompt = [
    `$mesh ids=${taskId} plan_file=${planFileRel} adapter=auto parallel_tasks=1 max_tasks=1 headless=true`,
    "",
    `Runtime budget: ${budgetSec}s for this join turn.`,
    "Join override:",
    "- Skip proposal/critique/synthesis/vote.",
    "- Treat the patch below as the synthesized diff and go directly to integration + validation + persistence.",
    "- If the patch does not apply cleanly, fall back to running full $mesh for this id.",
    "- If budget is nearly exhausted, finalize with explicit status and stop.",
    "Orchestration evidence (required):",
    "- Report spawn/wait/close lifecycle evidence for this task.",
    "- Use one wait call over all active ids before proceeding.",
    "- If retries occur, report the retry ladder as spawn -> wait -> close.",
    "- If high-fanout intent plus local cap pressure occurs, state whether you escalated to $cas and why.",
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
    meshTimeoutSteerOptions({ timeoutMs, role: "join apply run" }),
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
  if (opts.once && opts.workerTurnTimeoutMs < ONE_SHOT_MIN_TIMEOUT_MS) {
    const requested = opts.workerTurnTimeoutMs;
    opts.workerTurnTimeoutMs = ONE_SHOT_MIN_TIMEOUT_MS;
    process.stderr.write(
      `mesh_timeout_clamp adapter=cas_fleet mode=once field=worker_turn_timeout_ms requested_ms=${requested} applied_ms=${opts.workerTurnTimeoutMs} minimum_ms=${ONE_SHOT_MIN_TIMEOUT_MS}\n`,
    );
  }
  if (opts.once && opts.joinTurnTimeoutMs < ONE_SHOT_MIN_TIMEOUT_MS) {
    const requested = opts.joinTurnTimeoutMs;
    opts.joinTurnTimeoutMs = ONE_SHOT_MIN_TIMEOUT_MS;
    process.stderr.write(
      `mesh_timeout_clamp adapter=cas_fleet mode=once field=join_turn_timeout_ms requested_ms=${requested} applied_ms=${opts.joinTurnTimeoutMs} minimum_ms=${ONE_SHOT_MIN_TIMEOUT_MS}\n`,
    );
  }
  const absCwd = resolve(opts.cwd);
  const planCheck = ensureHeadlessPlanFile({ cwd: absCwd, planFile: opts.planFile });
  if (!planCheck.ok) return 0;

  const stateDir = resolve(opts.stateDir ?? defaultFleetStateDir(absCwd));
  mkdirSync(stateDir, { recursive: true });

  // Prevent two fleet runners from sharing the same cas state files.
  const lockPath = resolve(stateDir, "fleet.lock.json");
  let lockOwned = false;
  const cleanupLock = () => {
    if (!lockOwned) return;
    try {
      if (existsSync(lockPath)) unlinkSync(lockPath);
    } catch {
      // Best-effort cleanup.
    }
    lockOwned = false;
  };
  process.on("exit", cleanupLock);

  if (existsSync(lockPath)) {
    let reaped = false;
    try {
      const prev = JSON.parse(readFileSync(lockPath, "utf-8"));
      const prevPid = Number(prev?.pid);
      const prevStartedAt = Date.parse(prev?.startedAt ?? "");
      if (Number.isInteger(prevPid) && prevPid > 1) {
        try {
          process.kill(prevPid, 0);
          process.stderr.write(
            `mesh_fleet_lock_held state_dir=${stateDir} pid=${prevPid}\n`,
          );
          return 2;
        } catch (err) {
          if (!(err && typeof err === "object" && err.code === "ESRCH")) {
            process.stderr.write(
              `mesh_fleet_lock_probe_failed state_dir=${stateDir} pid=${prevPid}\n`,
            );
            return 2;
          }
          unlinkSync(lockPath);
          reaped = true;
          process.stderr.write(
            `mesh_fleet_lock_reaped state_dir=${stateDir} reason=pid_not_running pid=${prevPid}\n`,
          );
        }
      } else if (!Number.isFinite(prevStartedAt) || Date.now() - prevStartedAt > LOCK_TTL_MS) {
        unlinkSync(lockPath);
        reaped = true;
        process.stderr.write(
          `mesh_fleet_lock_reaped state_dir=${stateDir} reason=stale_or_invalid_pid\n`,
        );
      }
    } catch {
      try {
        unlinkSync(lockPath);
        reaped = true;
        process.stderr.write(
          `mesh_fleet_lock_reaped state_dir=${stateDir} reason=unreadable\n`,
        );
      } catch {
        process.stderr.write(`mesh_fleet_lock_unreadable state_dir=${stateDir}\n`);
        return 2;
      }
    }
    if (!reaped && existsSync(lockPath)) {
      process.stderr.write(`mesh_fleet_lock_held state_dir=${stateDir} pid=unknown\n`);
      return 2;
    }
  }
  writeFileSync(
    lockPath,
    JSON.stringify({ pid: process.pid, startedAt: new Date().toISOString() }, null, 2) + "\n",
    "utf-8",
  );
  lockOwned = true;

  const here = dirname(fileURLToPath(import.meta.url));
  const meshSkillPath = resolve(here, "..");
  const stScriptPath = resolve(here, "..", "..", "st", "scripts", "st_plan.py");

  function makeWorkerClient(name, stateFile) {
    return new CasClient({
      cwd: absCwd,
      stateFile,
      clientName: `mesh-fleet-${name}`,
      clientTitle: "mesh cas fleet worker",
      clientVersion: "0.1.0",
      // Allow commands (for reading/search), but decline file writes.
      execApprovalDecision: "acceptForSession",
      fileApprovalDecision: "decline",
    });
  }

  const joinStateFile = stateFileForInstance(stateDir, "join");
  const join = {
    name: "join",
    stateFile: joinStateFile,
    client: new CasClient({
      cwd: absCwd,
      stateFile: joinStateFile,
      clientName: "mesh-fleet-join",
      clientTitle: "mesh cas fleet join",
      clientVersion: "0.1.0",
    }),
    threadId: null,
    busy: false,
  };

  /** @type {Array<{name: string, stateFile: string, client: any, threadId: string|null, busy: boolean}>} */
  const workers = Array.from({ length: opts.workers }, (_, i) => {
    const name = `worker-${i + 1}`;
    const stateFile = stateFileForInstance(stateDir, name);
    const client = makeWorkerClient(name, stateFile);
    return { name, stateFile, client, threadId: null, busy: false };
  });

  let stopping = false;
  let capabilityBlocked = false;
  let capabilityBlockReason = null;
  process.on("SIGINT", () => {
    stopping = true;
  });
  process.on("SIGTERM", () => {
    stopping = true;
  });

  function wireClientLogs(prefix, client) {
    client.on("cas/error", (ev) => {
      const detail = ev?.error ? ` detail=${JSON.stringify(ev.error)}` : "";
      process.stderr.write(`[${prefix}] cas/error: ${ev?.message ?? "unknown"}${detail}\n`);
    });
    if (opts.verbose) {
      client.on("proxyStderr", (line) => {
        process.stderr.write(`[${prefix}] proxy: ${line}\n`);
      });
    }
  }

  wireClientLogs(join.name, join.client);
  for (const w of workers) wireClientLogs(w.name, w.client);

  // If the server asks for dynamic tools/user input/auth refresh, fail deterministically.
  // (We rely on cas's built-in approval auto-handling for approvals.)
  function installHeadlessServerRequestPolicy(prefix, client) {
    client.on("cas/serverRequest", (ev) => {
      const method = typeof ev.method === "string" ? ev.method : "<unknown>";
      if (method === "item/tool/call") {
        capabilityBlocked = true;
        capabilityBlockReason = "adapter_missing_capability";
        process.stderr.write(
          `mesh_adapter_capability adapter=cas_fleet instance=${prefix} item_tool_call=unsupported headless=true\n`,
        );
        client.respondError(ev.id, `${prefix}: adapter_missing_capability (tool calls unavailable)`, {
          code: -32000,
          data: { method, reason: "adapter_missing_capability" },
        });
        return;
      }
      if (method === "item/tool/requestUserInput") {
        capabilityBlocked = true;
        capabilityBlockReason = "adapter_missing_capability";
        process.stderr.write(
          `mesh_adapter_capability adapter=cas_fleet instance=${prefix} request_user_input=unsupported headless=true\n`,
        );
        client.respondError(ev.id, `${prefix}: user input unavailable in fleet autopilot`, {
          code: -32000,
          data: { method, reason: "adapter_missing_capability" },
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

  installHeadlessServerRequestPolicy("join", join.client);
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
  await Promise.all([join.client.start(), ...workers.map((w) => w.client.start())]);
  join.threadId = await ensureThread({
    client: join.client,
    cwd: absCwd,
    stateFile: join.stateFile,
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
    `mesh_cas_fleet_autopilot_ready cwd=${absCwd} plan_file=${opts.planFile} workers=${workers.length} state_dir=${stateDir} budget_mode=${opts.budgetMode} join_thread=${join.threadId} worker_timeout_ms=${opts.workerTurnTimeoutMs} join_timeout_ms=${opts.joinTurnTimeoutMs} worker_max_attempts=${WORKER_MAX_ATTEMPTS}\n`,
  );

  let budgetState = { tier: "unknown", usedPercent: null, elapsedPercent: null, deltaPercent: null, resetsAt: null };
  let lastBudgetReadAt = 0;

  async function refreshBudgetGovernor({ force = false } = {}) {
    const now = Date.now();
    if (!force && now - lastBudgetReadAt < BUDGET_REFRESH_MS) return budgetState;
    lastBudgetReadAt = now;

    let govErr = null;
    if (opts.budgetMode === "aware") {
      try {
        const resp = await join.client.request("account/rateLimits/read", {}, { timeoutMs: 20_000 });
        budgetState = computeBudgetGovernor(resp);
      } catch (err) {
        govErr = err instanceof Error ? err.message : String(err);
        budgetState = {
          tier: "unknown",
          usedPercent: null,
          elapsedPercent: null,
          deltaPercent: null,
          resetsAt: null,
        };
      }
    } else {
      budgetState = { tier: "unknown", usedPercent: null, elapsedPercent: null, deltaPercent: null, resetsAt: null };
    }

    const cap = effectiveWorkersForBudget({
      mode: opts.budgetMode,
      tier: budgetState?.tier,
      maxWorkers: workers.length,
    });
    const elapsedPct =
      budgetState && Number.isFinite(budgetState.elapsedPercent) ? budgetState.elapsedPercent.toFixed(1) : "null";
    const deltaPct =
      budgetState && Number.isFinite(budgetState.deltaPercent) ? budgetState.deltaPercent.toFixed(1) : "null";
    const tierLabel = opts.budgetMode === "all_out" ? "all_out" : budgetState?.tier ?? "unknown";

    process.stderr.write(
      `mesh_budget budget_mode=${opts.budgetMode} tier=${tierLabel} used_percent=${budgetState?.usedPercent ?? "null"} elapsed_percent=${elapsedPct} delta_percent=${deltaPct} resets_at=${budgetState?.resetsAt ?? "null"} worker_cap=${cap}/${workers.length}${govErr ? ` rate_limits_error=${JSON.stringify(govErr)}` : ""}\n`,
    );

    return budgetState;
  }

  await refreshBudgetGovernor({ force: true });
  const meshRunId = utcCompact();
  const initialCap = effectiveWorkersForBudget({
    mode: opts.budgetMode,
    tier: budgetState?.tier,
    maxWorkers: workers.length,
  });
  process.stderr.write(
    `mesh_preflight mesh_run_id=${meshRunId} plan_file=${opts.planFile} adapter=cas_fleet ids=auto budget_mode=${opts.budgetMode} worker_cap=${initialCap}/${workers.length} overrides=max_tasks=auto,parallel_tasks=auto\n`,
  );
  const orchestrationCompliance = {
    lifecycle: false,
    waitAllIds: false,
    retryLadder: false,
    highFanoutCas: false,
    capPressureObserved: false,
    retriesObserved: 0,
  };
  function mergeOrchestrationEvidence(text) {
    const flags = orchestrationEvidenceFlags(text);
    orchestrationCompliance.lifecycle = orchestrationCompliance.lifecycle || flags.lifecycle;
    orchestrationCompliance.waitAllIds = orchestrationCompliance.waitAllIds || flags.waitAllIds;
    orchestrationCompliance.retryLadder = orchestrationCompliance.retryLadder || flags.retryLadder;
    orchestrationCompliance.highFanoutCas = orchestrationCompliance.highFanoutCas || flags.highFanoutCas;
  }

  /** @type {Set<string>} */
  const reservedTaskIds = new Set();
  /** @type {Array<{id: string, step: string, notes: string|null, scope: string[]|null, hasGlobs: boolean}>} */
  let queue = [];

  /** @type {Map<string, { worker: any, taskId: string, startedAt: number, promise: Promise<any> }>} */
  const inflight = new Map();

  async function refreshQueue() {
    const snapshot = await readPlanSnapshot({ cwd: absCwd, planFileRel: opts.planFile, stScriptPath });
    if (!snapshot.ok) {
      process.stderr.write(`mesh_cas_fleet_autopilot_no_plan plan_file=${opts.planFile} path=${snapshot.planPath}\n`);
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
      let lastFailureCode = null;
      let lastErrorText = null;
      let lastRaw = "";
      let lastParseFormat = "none";
      let lastNoDiffReason = null;
      const attemptWatchdogMs = workerAttemptWatchdogMs(opts.workerTurnTimeoutMs);

      for (let attempt = 1; attempt <= WORKER_MAX_ATTEMPTS; attempt += 1) {
        if (attempt > 1) {
          orchestrationCompliance.retryLadder = true;
          orchestrationCompliance.retriesObserved += 1;
        }
        try {
          const collected = await withWatchdog(
            () =>
              runWorkerMesh({
                client: worker.client,
                threadId: worker.threadId,
                taskId: task.id,
                planFileRel: opts.planFile,
                meshSkillPath,
                absCwd,
                timeoutMs: opts.workerTurnTimeoutMs,
                attempt,
              }),
            attemptWatchdogMs,
            "worker_attempt_watchdog_timeout",
          );

          const msg = collected?.agentMessageText ?? "";
          const statusHint =
            typeof collected?.turn?.status === "string" ? collected.turn.status : "completed";
          const parsed = classifyMeshOutput(collected, { strictOutput: true, statusHint });
          const diff = parsed.diff;
          const parseFormat = parsed.parseFormat;
          const noDiffReason = parsed.noDiffReason;
          const parsedFailureCode = parsed.failureCode;
          const summaryLine = summarize(msg);
          lastRaw = msg;
          lastParseFormat = parseFormat;
          lastNoDiffReason = noDiffReason;
          mergeOrchestrationEvidence(msg);
          const reasonSuffix = noDiffReason ? ` no_diff_reason=${JSON.stringify(noDiffReason.slice(0, 220))}` : "";

          process.stderr.write(
            `mesh_fleet_worker_attempt worker=${worker.name} task=${task.id} attempt=${attempt}/${WORKER_MAX_ATTEMPTS} has_diff=${diff ? "yes" : "no"} failure_code=${parsedFailureCode ?? "none"} parse_format=${parseFormat}${reasonSuffix} summary=${JSON.stringify(summaryLine)}\n`,
          );

          if (diff) {
            return {
              ok: true,
              taskId: task.id,
              worker: worker.name,
              elapsedMs: Date.now() - startedAt,
              diff,
              raw: msg,
              error: null,
              attempts: attempt,
              failureCode: null,
              parseFormat,
              noDiffReason: null,
            };
          }

          lastFailureCode = parsedFailureCode ?? "no_diff_parsed";
          if (noDiffReason) {
            lastErrorText = `worker returned NO_DIFF: ${noDiffReason}`;
          } else if (lastFailureCode === "no_response") {
            lastErrorText = "worker produced no response";
          } else {
            lastErrorText = "worker produced no diff";
          }
        } catch (err) {
          const msg = err instanceof Error ? err.message : String(err);
          const watchdogMatch = msg.match(/^worker_attempt_watchdog_timeout:(\d+)$/);
          const failureCode = watchdogMatch ? "worker_turn_hang_before_output" : "no_response";
          if (watchdogMatch) {
            process.stderr.write(
              `mesh_fleet_worker_watchdog worker=${worker.name} task=${task.id} attempt=${attempt}/${WORKER_MAX_ATTEMPTS} failure_code=worker_turn_hang_before_output timeout_ms=${watchdogMatch[1]}\n`,
            );
          }
          process.stderr.write(
            `mesh_fleet_worker_fail worker=${worker.name} task=${task.id} attempt=${attempt}/${WORKER_MAX_ATTEMPTS} failure_code=${failureCode} error=${JSON.stringify(msg)}\n`,
          );
          lastFailureCode = failureCode;
          lastErrorText = msg;
          lastParseFormat = "none";
          lastNoDiffReason = null;
        }

        if (attempt >= WORKER_MAX_ATTEMPTS) break;

        try {
          await restartInstance(
            worker,
            () => makeWorkerClient(worker.name, worker.stateFile),
            { sandbox: "read-only" },
          );
        } catch (restartErr) {
          const msg = restartErr instanceof Error ? restartErr.message : String(restartErr);
          process.stderr.write(
            `mesh_fleet_worker_restart_fail worker=${worker.name} task=${task.id} attempt=${attempt}/${WORKER_MAX_ATTEMPTS} failure_code=no_response error=${JSON.stringify(msg)}\n`,
          );
          lastFailureCode = "no_response";
          lastErrorText = msg;
          lastParseFormat = "none";
          lastNoDiffReason = null;
          break;
        }
      }

      const exhaustedReason = lastNoDiffReason
        ? ` no_diff_reason=${JSON.stringify(lastNoDiffReason.slice(0, 220))}`
        : "";
      process.stderr.write(
        `mesh_fleet_worker_exhausted worker=${worker.name} task=${task.id} attempts=${WORKER_MAX_ATTEMPTS} failure_code=${lastFailureCode ?? "no_response"} parse_format=${lastParseFormat}${exhaustedReason}\n`,
      );

      return {
        ok: false,
        taskId: task.id,
        worker: worker.name,
        elapsedMs: Date.now() - startedAt,
        diff: null,
        raw: lastRaw,
        error: lastErrorText ?? "worker attempts exhausted",
        attempts: WORKER_MAX_ATTEMPTS,
        failureCode: lastFailureCode ?? "no_response",
        parseFormat: lastParseFormat,
        noDiffReason: lastNoDiffReason,
      };
    } finally {
      worker.busy = false;
    }
  }

  async function integrateOne(result) {
    if (!result.diff) {
      const reasonSuffix = result.noDiffReason
        ? ` no_diff_reason=${JSON.stringify(String(result.noDiffReason).slice(0, 220))}`
        : "";
      process.stderr.write(
        `mesh_fleet_worker_no_diff task=${result.taskId} from=${result.worker} attempts=${result.attempts ?? 1} failure_code=${result.failureCode ?? "no_response"} parse_format=${result.parseFormat ?? "none"}${reasonSuffix}\n`,
      );
      // Fallback: have the join attempt the task normally.
      if (join.busy) {
        while (join.busy && !stopping) await sleep(250);
      }
      if (stopping) return;

      join.busy = true;
      const startedAt = Date.now();
      try {
        const collected = await runJoinMeshFull({
          client: join.client,
          threadId: join.threadId,
          taskId: result.taskId,
          planFileRel: opts.planFile,
          meshSkillPath,
          timeoutMs: opts.joinTurnTimeoutMs,
        });
        const elapsedMs = Date.now() - startedAt;
        const status = collected?.turn?.status ?? null;
        const message = collected?.agentMessageText ?? "";
        const summaryLine = summarize(message);
        mergeOrchestrationEvidence(message);
        process.stderr.write(
          `mesh_fleet_join_fallback task=${result.taskId} from=${result.worker} elapsed_ms=${elapsedMs} status=${status ?? "null"} summary=${JSON.stringify(summaryLine)}\n`,
        );
      } catch (err) {
        const elapsedMs = Date.now() - startedAt;
        const msg = err instanceof Error ? err.message : String(err);
        process.stderr.write(
          `mesh_fleet_join_fallback_fail task=${result.taskId} from=${result.worker} elapsed_ms=${elapsedMs} error=${JSON.stringify(msg)}\n`,
        );
      } finally {
        join.busy = false;
      }
      return;
    }
    if (join.busy) {
      // Simple backpressure: wait until join is free.
      while (join.busy && !stopping) await sleep(250);
    }
    if (stopping) return;

    join.busy = true;
    const startedAt = Date.now();
    try {
      const collected = await runJoinApply({
        client: join.client,
        threadId: join.threadId,
        taskId: result.taskId,
        planFileRel: opts.planFile,
        meshSkillPath,
        diffText: result.diff,
        timeoutMs: opts.joinTurnTimeoutMs,
      });
      const elapsedMs = Date.now() - startedAt;
      const status = collected?.turn?.status ?? null;
      const message = collected?.agentMessageText ?? "";
      const summaryLine = summarize(message);
      mergeOrchestrationEvidence(message);
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
      join.busy = false;
    }
  }

  async function schedulingWave() {
    await refreshBudgetGovernor();
    const workerCap = effectiveWorkersForBudget({
      mode: opts.budgetMode,
      tier: budgetState?.tier,
      maxWorkers: workers.length,
    });

    // Fill the queue.
    const candidates = await refreshQueue();
    const candidateIds = new Set(candidates.map((c) => c.id));
    queue = queue.filter((q) => candidateIds.has(q.id));
    for (const c of candidates) {
      if (reservedTaskIds.has(c.id)) continue;
      if (queue.find((q) => q.id === c.id)) continue;
      queue.push(c);
    }
    if (workerCap < workers.length && queue.length > workerCap) {
      orchestrationCompliance.capPressureObserved = true;
    }

    if (workerCap === 0 && inflight.size === 0) {
      if (join.busy) return false;

      let pickIdx = -1;
      for (let i = 0; i < queue.length; i += 1) {
        const t = queue[i];
        if (!t || typeof t.id !== "string") continue;
        if (reservedTaskIds.has(t.id)) continue;
        pickIdx = i;
        break;
      }
      if (pickIdx === -1) return false;

      const task = queue.splice(pickIdx, 1)[0];
      reservedTaskIds.add(task.id);
      join.busy = true;
      const startedAt = Date.now();
      try {
        process.stderr.write(
          `mesh_fleet_join_solo_start task=${task.id} budget_mode=${opts.budgetMode} tier=${budgetState?.tier ?? "unknown"} worker_cap=${workerCap}/${workers.length}\n`,
        );
        const collected = await runJoinMeshFull({
          client: join.client,
          threadId: join.threadId,
          taskId: task.id,
          planFileRel: opts.planFile,
          meshSkillPath,
          timeoutMs: opts.joinTurnTimeoutMs,
        });
        const elapsedMs = Date.now() - startedAt;
        const status = collected?.turn?.status ?? null;
        const message = collected?.agentMessageText ?? "";
        const summaryLine = summarize(message);
        mergeOrchestrationEvidence(message);
        process.stderr.write(
          `mesh_fleet_join_solo task=${task.id} elapsed_ms=${elapsedMs} status=${status ?? "null"} summary=${JSON.stringify(summaryLine)}\n`,
        );
      } catch (err) {
        const elapsedMs = Date.now() - startedAt;
        const msg = err instanceof Error ? err.message : String(err);
        process.stderr.write(
          `mesh_fleet_join_solo_fail task=${task.id} elapsed_ms=${elapsedMs} error=${JSON.stringify(msg)}\n`,
        );
      } finally {
        join.busy = false;
        reservedTaskIds.delete(task.id);
      }

      return true;
    }

    // Spawn worker runs.
    const allowedWorkers = workers.slice(0, workerCap);
    const free = allowedWorkers.filter((w) => !w.busy && !inflight.has(w.name));
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
    if (capabilityBlocked) {
      const reason = capabilityBlockReason ?? "adapter_missing_capability";
      process.stderr.write(
        `mesh_headless_stop headless_stop_reason=${reason} delegation_did_not_run=true action=\"switch to worker-capable runtime/session and retry\"\n`,
      );
      break;
    }

    let progressed = false;
    try {
      progressed = await schedulingWave();
      if (progressed) didAnyWork = true;

      // When the budget governor throttles scale-out to zero workers, avoid a tight drain loop.
      if (progressed && opts.budgetMode === "aware") {
        const cap = effectiveWorkersForBudget({
          mode: opts.budgetMode,
          tier: budgetState?.tier,
          maxWorkers: workers.length,
        });
        if (cap === 0 && opts.pollMs > 0) {
          await sleep(opts.pollMs);
        }
      }
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
  await Promise.allSettled([join.client.close(), ...workers.map((w) => w.client.close())]);
  process.stderr.write(
    `mesh_orchestration_compliance adapter=cas_fleet mesh_run_id=${meshRunId} lifecycle_evidence=${orchestrationCompliance.lifecycle ? "yes" : "no"} wait_all_ids_evidence=${orchestrationCompliance.waitAllIds ? "yes" : "no"} retry_ladder_evidence=${orchestrationCompliance.retryLadder ? "yes" : "no"} high_fanout_cas_evidence=${orchestrationCompliance.highFanoutCas || orchestrationCompliance.capPressureObserved ? "yes" : "no"} cap_pressure_observed=${orchestrationCompliance.capPressureObserved ? "yes" : "no"} retries_observed=${orchestrationCompliance.retriesObserved}\n`,
  );
  process.stderr.write(`mesh_cas_fleet_autopilot_exit did_any_work=${didAnyWork ? "yes" : "no"}\n`);
  cleanupLock();
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
