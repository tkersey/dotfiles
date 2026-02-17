#!/usr/bin/env node
// Cas JSONL proxy for `codex app-server`.
//
// - Reads JSONL commands from stdin.
// - Spawns `codex app-server` and performs initialize/initialized handshake.
// - Emits JSONL events on stdout (lossless; includes raw app-server messages).
// - Auto-accepts v2 approvals.
// - Forwards server requests to the orchestrator and fails fast on timeout.

import { spawn } from "node:child_process";
import { createHash, randomUUID } from "node:crypto";
import { once } from "node:events";
import { mkdir, readFile, rename, rm, writeFile } from "node:fs/promises";
import { homedir } from "node:os";
import { dirname, isAbsolute, resolve } from "node:path";
import { createInterface } from "node:readline";

const CAS_EVENT_VERSION = 1;
const JSONRPC_INVALID_PARAMS = -32602;
const JSONRPC_REQUEST_TIMEOUT = -32000;

function nowMs() {
  return Date.now();
}

function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function safeJsonParse(line) {
  try {
    return { ok: true, value: JSON.parse(line) };
  } catch (err) {
    return {
      ok: false,
      error: err instanceof Error ? err : new Error(String(err)),
    };
  }
}

function isStringArray(value) {
  return Array.isArray(value) && value.every((v) => typeof v === "string");
}

function validateDynamicToolCallResult(result) {
  if (!isObject(result)) {
    return { ok: false, message: "item/tool/call result must be an object" };
  }
  if (!Array.isArray(result.contentItems)) {
    return { ok: false, message: "item/tool/call result.contentItems must be an array" };
  }
  if (typeof result.success !== "boolean") {
    return { ok: false, message: "item/tool/call result.success must be a boolean" };
  }
  for (const item of result.contentItems) {
    if (!isObject(item) || typeof item.type !== "string") {
      return {
        ok: false,
        message: "item/tool/call contentItems entries must be objects with type",
      };
    }
    if (item.type === "inputText") {
      if (typeof item.text !== "string") {
        return {
          ok: false,
          message: "item/tool/call inputText entries require string text",
        };
      }
      continue;
    }
    if (item.type === "inputImage") {
      if (typeof item.imageUrl !== "string") {
        return {
          ok: false,
          message: "item/tool/call inputImage entries require string imageUrl",
        };
      }
      continue;
    }
    return {
      ok: false,
      message: `item/tool/call contentItems has unsupported type: ${item.type}`,
    };
  }
  return { ok: true };
}

function validateToolRequestUserInputResult(result) {
  if (!isObject(result)) {
    return { ok: false, message: "item/tool/requestUserInput result must be an object" };
  }
  if (!isObject(result.answers)) {
    return {
      ok: false,
      message: "item/tool/requestUserInput result.answers must be an object",
    };
  }
  for (const [questionId, value] of Object.entries(result.answers)) {
    if (!isObject(value) || !isStringArray(value.answers)) {
      return {
        ok: false,
        message:
          `item/tool/requestUserInput result.answers.${questionId} must be ` +
          "{ answers: string[] }",
      };
    }
  }
  return { ok: true };
}

function validateChatgptAuthTokensRefreshResult(result) {
  if (!isObject(result)) {
    return {
      ok: false,
      message: "account/chatgptAuthTokens/refresh result must be an object",
    };
  }
  if (typeof result.idToken !== "string" || typeof result.accessToken !== "string") {
    return {
      ok: false,
      message:
        "account/chatgptAuthTokens/refresh result requires string idToken and accessToken",
    };
  }
  return { ok: true };
}

function validateServerRequestResult(method, result) {
  if (method === "item/tool/call") return validateDynamicToolCallResult(result);
  if (method === "item/tool/requestUserInput") {
    return validateToolRequestUserInputResult(result);
  }
  if (method === "account/chatgptAuthTokens/refresh") {
    return validateChatgptAuthTokensRefreshResult(result);
  }
  return { ok: true };
}

function defaultStateFileForCwd(cwd) {
  const normalized = resolve(cwd);
  const digest = createHash("sha256").update(normalized).digest("hex").slice(0, 16);
  return resolve(homedir(), ".codex", "cas", "state", `${digest}.json`);
}

function classifyJsonRpc(msg) {
  if (!isObject(msg)) {
    return { kind: "unknown", method: null, id: null };
  }

  const hasMethod = typeof msg.method === "string";
  const hasId = typeof msg.id === "string" || typeof msg.id === "number";
  const hasResult = Object.prototype.hasOwnProperty.call(msg, "result");
  const hasError = Object.prototype.hasOwnProperty.call(msg, "error");

  if (hasMethod && hasId)
    return { kind: "request", method: msg.method, id: msg.id };
  if (hasMethod && !hasId)
    return { kind: "notification", method: msg.method, id: null };
  if (hasId && (hasResult || hasError))
    return { kind: "response", method: null, id: msg.id };

  return {
    kind: "unknown",
    method: hasMethod ? msg.method : null,
    id: hasId ? msg.id : null,
  };
}

function deriveRoutingKeys(msg, requestMethodHint = null) {
  /** @type {{threadId: string|null, turnId: string|null, itemId: string|null}} */
  const out = { threadId: null, turnId: null, itemId: null };

  const roots = [];
  if (isObject(msg)) {
    if (isObject(msg.params)) roots.push(msg.params);
    if (isObject(msg.result)) roots.push(msg.result);
  }

  for (const root of roots) {
    if (!out.threadId && typeof root.threadId === "string")
      out.threadId = root.threadId;
    if (!out.turnId && typeof root.turnId === "string")
      out.turnId = root.turnId;
    if (!out.itemId && typeof root.itemId === "string")
      out.itemId = root.itemId;

    if (
      !out.threadId &&
      isObject(root.thread) &&
      typeof root.thread.id === "string"
    ) {
      out.threadId = root.thread.id;
    }
    if (
      !out.turnId &&
      isObject(root.turn) &&
      typeof root.turn.id === "string"
    ) {
      out.turnId = root.turn.id;
    }
    if (
      !out.itemId &&
      isObject(root.item) &&
      typeof root.item.id === "string"
    ) {
      out.itemId = root.item.id;
    }
  }

  if (
    !out.threadId &&
    requestMethodHint &&
    isObject(msg) &&
    isObject(msg.result)
  ) {
    if (
      (requestMethodHint === "thread/start" ||
        requestMethodHint === "thread/resume" ||
        requestMethodHint === "thread/fork" ||
        requestMethodHint === "thread/read" ||
        requestMethodHint === "thread/rollback" ||
        requestMethodHint === "thread/unarchive") &&
      isObject(msg.result.thread) &&
      typeof msg.result.thread.id === "string"
    ) {
      out.threadId = msg.result.thread.id;
    }
  }

  return out;
}

function parseArgs(argv) {
  /** @type {{codexPath: string, cwd: string, stateFile: string, clientName: string, clientTitle: string, clientVersion: string, heartbeatMs: number, maxOutQueue: number, killTimeoutMs: number, serverRequestTimeoutMs: number, optOutNotificationMethods: string[], execApprovalDecision: "auto"|"accept"|"acceptForSession"|"decline"|"cancel", fileApprovalDecision: "auto"|"accept"|"acceptForSession"|"decline"|"cancel"}} */
  const opts = {
    codexPath: "codex",
    cwd: process.cwd(),
    stateFile: defaultStateFileForCwd(process.cwd()),
    clientName: "cas",
    clientTitle: "cas skill",
    clientVersion: "0.1.0",
    // Emit cas/heartbeat every N ms (0 disables).
    heartbeatMs: 0,
    // Max buffered stdout events before pausing inputs.
    maxOutQueue: 20_000,
    // After cas/exit, SIGKILL app-server after N ms.
    killTimeoutMs: 2_000,
    // Fail forwarded server requests that have no orchestrator response.
    serverRequestTimeoutMs: 30_000,
    // v2 approval auto-response policy.
    // - exec: "auto" preserves cas's default behavior (accept execpolicy amendments when proposed).
    // - file: "auto" is an alias for acceptForSession.
    execApprovalDecision: "auto",
    fileApprovalDecision: "auto",
    // Optional initialize capability to suppress selected notifications.
    optOutNotificationMethods: [],
  };
  let explicitStateFile = false;

  const args = [...argv];
  while (args.length) {
    const arg = args.shift();
    if (!arg) break;

    if (arg === "--help" || arg === "-h") {
      return { ok: false, help: true, error: null, opts: null };
    }

    const takeValue = () => {
      const v = args.shift();
      if (!v) throw new Error(`Missing value for ${arg}`);
      return v;
    };

    if (arg === "--codex") {
      opts.codexPath = takeValue();
      continue;
    }
    if (arg === "--cwd") {
      opts.cwd = takeValue();
      if (!explicitStateFile) {
        opts.stateFile = defaultStateFileForCwd(opts.cwd);
      }
      continue;
    }
    if (arg === "--state-file") {
      opts.stateFile = takeValue();
      explicitStateFile = true;
      continue;
    }
    if (arg === "--client-name") {
      opts.clientName = takeValue();
      continue;
    }
    if (arg === "--client-title") {
      opts.clientTitle = takeValue();
      continue;
    }
    if (arg === "--client-version") {
      opts.clientVersion = takeValue();
      continue;
    }
    if (arg === "--heartbeat-ms") {
      opts.heartbeatMs = Number(takeValue());
      continue;
    }
    if (arg === "--max-out-queue") {
      opts.maxOutQueue = Number(takeValue());
      continue;
    }
    if (arg === "--kill-timeout-ms") {
      opts.killTimeoutMs = Number(takeValue());
      continue;
    }
    if (arg === "--server-request-timeout-ms") {
      opts.serverRequestTimeoutMs = Number(takeValue());
      continue;
    }
    if (arg === "--exec-approval") {
      opts.execApprovalDecision = /** @type {any} */ (takeValue());
      continue;
    }
    if (arg === "--file-approval") {
      opts.fileApprovalDecision = /** @type {any} */ (takeValue());
      continue;
    }
    if (arg === "--read-only") {
      opts.execApprovalDecision = "decline";
      opts.fileApprovalDecision = "decline";
      continue;
    }
    if (arg === "--opt-out-notification-method") {
      opts.optOutNotificationMethods.push(takeValue());
      continue;
    }

    throw new Error(`Unknown arg: ${arg}`);
  }

  const execDecisions = new Set(["auto", "accept", "acceptForSession", "decline", "cancel"]);
  const fileDecisions = new Set(["auto", "accept", "acceptForSession", "decline", "cancel"]);
  if (!execDecisions.has(opts.execApprovalDecision)) {
    throw new Error(
      `--exec-approval must be one of: ${Array.from(execDecisions).join(", ")}`,
    );
  }
  if (!fileDecisions.has(opts.fileApprovalDecision)) {
    throw new Error(
      `--file-approval must be one of: ${Array.from(fileDecisions).join(", ")}`,
    );
  }

  return { ok: true, help: false, error: null, opts };
}

function helpText() {
  return [
    "cas_proxy.mjs - JSONL proxy for `codex app-server`",
    "",
    "Usage:",
    "  node scripts/cas_proxy.mjs [--codex codex] [--cwd DIR]",
    "                        [--state-file ~/.codex/cas/state/<workspace-hash>.json]",
    "                        [--heartbeat-ms 0] [--max-out-queue 20000] [--kill-timeout-ms 2000]",
    "                        [--server-request-timeout-ms 30000]",
    "                        [--exec-approval auto|accept|acceptForSession|decline|cancel]",
    "                        [--file-approval auto|accept|acceptForSession|decline|cancel]",
    "                        [--read-only]",
    "                        [--opt-out-notification-method METHOD]",
    "",
    "stdin JSONL:",
    '  { "type": "cas/request", "clientRequestId": "...", "method": "thread/start", "params": { ... } }',
    '  { "type": "cas/respond", "id": 123, "result": { ... } }',
    '  { "type": "cas/respond", "id": 123, "error": { ... } }',
    '  { "type": "cas/state/get" }',
    '  { "type": "cas/stats/get" }',
    '  { "type": "cas/exit" }',
    "",
    "stdout JSONL:",
    "  cas emits events like cas/ready, cas/fromServer, cas/toServer, cas/error.",
  ].join("\n");
}

async function readStateFile(stateFile) {
  try {
    const raw = await readFile(stateFile, "utf8");
    const parsed = JSON.parse(raw);
    if (!isObject(parsed) || parsed.v !== 1)
      return { v: 1, currentThreadId: null };
    return {
      v: 1,
      currentThreadId:
        typeof parsed.currentThreadId === "string"
          ? parsed.currentThreadId
          : null,
    };
  } catch {
    // Missing file is fine.
    return { v: 1, currentThreadId: null };
  }
}

async function writeStateFile(stateFile, state) {
  await mkdir(dirname(stateFile), { recursive: true });
  // Use a unique temp path to avoid rename races across concurrent writers.
  const tmp = `${stateFile}.${process.pid}.${randomUUID()}.tmp`;
  try {
    await writeFile(tmp, JSON.stringify(state), "utf8");
    await rename(tmp, stateFile);
  } finally {
    // Best-effort cleanup in case write/rename fails mid-flight.
    try {
      await rm(tmp, { force: true });
    } catch {
      // Ignore cleanup errors.
    }
  }
}

class CasProxy {
  /** @param {{codexPath: string, cwd: string, stateFile: string, clientName: string, clientTitle: string, clientVersion: string, heartbeatMs: number, maxOutQueue: number, killTimeoutMs: number, serverRequestTimeoutMs: number, optOutNotificationMethods: string[], execApprovalDecision: "auto"|"accept"|"acceptForSession"|"decline"|"cancel", fileApprovalDecision: "auto"|"accept"|"acceptForSession"|"decline"|"cancel"}} opts */
  constructor(opts) {
    this.opts = opts;
    this.cwd = opts.cwd;
    this.sessionId = `cas-${randomUUID()}`;
    this.seq = 0;
    this.ready = false;
    this.child = null;
    this.nextId = 1;

    this.appServerUserAgent = null;

    this.startedAtMs = nowMs();

    this.stats = {
      clientLines: 0,
      serverLines: 0,
      clientParseErrors: 0,
      serverParseErrors: 0,
      toServerMessages: 0,
      fromServerMessages: 0,
      stdoutWrites: 0,
      stdoutBackpressureCount: 0,
      autoApprovals: 0,
      forwardedServerRequests: 0,
      ioPauses: 0,
      ioResumes: 0,
      outQueueHighWater: 0,
    };

    // Outbound stdout backpressure handling.
    /** @type {Array<string>} */
    this.outQueue = [];
    this.outQueueCursor = 0;
    this.flushing = false;
    this.ioPaused = false;
    this.ioPauseReason = null;

    /** @type {ReturnType<typeof setInterval> | null} */
    this.heartbeatTimer = null;

    /** @type {{ code: number, reason: string, requestedAtMs: number } | null} */
    this.exitAfterFlush = null;
    /** @type {ReturnType<typeof setTimeout> | null} */
    this.exitHardTimer = null;

    // Readline interfaces (for pause/resume).
    this.stdinRl = null;
    this.childStdoutRl = null;
    this.childStderrRl = null;

    this.exitRequested = false;

    /** @type {Map<string|number, { clientRequestId: string|null, method: string|null, internal: boolean, threadIdHint: string|null, turnIdHint: string|null, itemIdHint: string|null }>} */
    this.pendingClientRequests = new Map();

    /** @type {Map<string|number, { resolve: (msg: any) => void, reject: (err: Error) => void, timeout: ReturnType<typeof setTimeout> | null }>} */
    this.pendingResponseWaiters = new Map();

    /** @type {Map<string|number, { method: string, params: any, timeout: ReturnType<typeof setTimeout> | null, startedAtMs: number }>} */
    this.pendingServerRequests = new Map();

    /** @type {Array<any>} */
    this.bufferedInput = [];

    this.state = { v: 1, currentThreadId: null };
    this.stateFileAbs = null;
  }

  baseEvent(type) {
    this.seq += 1;
    return {
      type,
      v: CAS_EVENT_VERSION,
      seq: this.seq,
      ts: nowMs(),
      sessionId: this.sessionId,
      pid: process.pid,
    };
  }

  outQueueDepth() {
    return this.outQueue.length - this.outQueueCursor;
  }

  emit(event) {
    const line = `${JSON.stringify(event)}\n`;
    this.outQueue.push(line);

    const depth = this.outQueueDepth();
    if (depth > this.stats.outQueueHighWater) this.stats.outQueueHighWater = depth;
    if (this.opts.maxOutQueue > 0 && depth >= this.opts.maxOutQueue) {
      this.pauseIo(`outQueue>=${this.opts.maxOutQueue}`);
    }

    void this.flushOutQueue();
  }

  pauseIo(reason) {
    if (this.ioPaused) return;
    this.ioPaused = true;
    this.ioPauseReason = reason;
    this.stats.ioPauses += 1;

    for (const rl of [this.childStdoutRl, this.childStderrRl, this.stdinRl]) {
      if (!rl) continue;
      try {
        rl.pause();
      } catch {
        // Ignore closed interfaces (common when stdin is a pipe).
      }
    }

    this.emit({
      ...this.baseEvent("cas/ioPaused"),
      reason,
    });
  }

  resumeIo(reason) {
    if (!this.ioPaused) return;
    this.ioPaused = false;
    this.ioPauseReason = null;
    this.stats.ioResumes += 1;

    for (const rl of [this.childStdoutRl, this.childStderrRl, this.stdinRl]) {
      if (!rl) continue;
      try {
        rl.resume();
      } catch {
        // Ignore closed interfaces.
      }
    }

    this.emit({
      ...this.baseEvent("cas/ioResumed"),
      reason,
    });
  }

  requestExit(code, reason) {
    if (this.exitAfterFlush) return;
    this.exitAfterFlush = { code, reason, requestedAtMs: nowMs() };

    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }

    for (const pending of this.pendingServerRequests.values()) {
      if (pending.timeout) clearTimeout(pending.timeout);
    }
    this.pendingServerRequests.clear();

    this.failAllResponseWaiters(new Error(`cas exiting: ${reason}`));

    this.exitHardTimer = setTimeout(() => {
      process.exit(code);
    }, 2000);
    this.exitHardTimer.unref?.();

    void this.flushOutQueue();
  }

  async flushOutQueue() {
    if (this.flushing) return;
    this.flushing = true;
    try {
      while (this.outQueueCursor < this.outQueue.length) {
        const chunk = this.outQueue[this.outQueueCursor];
        const ok = process.stdout.write(chunk);
        this.stats.stdoutWrites += 1;
        if (!ok) {
          this.stats.stdoutBackpressureCount += 1;
          try {
            await once(process.stdout, "drain");
          } catch {
            break;
          }
        }
        this.outQueueCursor += 1;
      }

      if (this.outQueueCursor >= this.outQueue.length) {
        this.outQueue = [];
        this.outQueueCursor = 0;
        if (
          this.ioPaused &&
          typeof this.ioPauseReason === "string" &&
          this.ioPauseReason.startsWith("outQueue") &&
          this.outQueueDepth() < this.opts.maxOutQueue / 2
        ) {
          this.resumeIo("outQueue drained");
        }
      }
    } finally {
      this.flushing = false;
    }

    if (this.exitAfterFlush && this.outQueueDepth() === 0) {
      if (this.exitHardTimer) clearTimeout(this.exitHardTimer);
      process.exit(this.exitAfterFlush.code);
    }
  }

  statsSnapshot() {
    return {
      startedAtMs: this.startedAtMs,
      uptimeMs: nowMs() - this.startedAtMs,
      ready: this.ready,
      cwd: this.cwd,
      appServerUserAgent: this.appServerUserAgent,
      stateFile: this.stateFileAbs,
      state: this.state,
      pendingClientRequests: this.pendingClientRequests.size,
      pendingServerRequests: this.pendingServerRequests.size,
      outQueueDepth: this.outQueueDepth(),
      ioPaused: this.ioPaused,
      ioPauseReason: this.ioPauseReason,
      appServerPid: this.child?.pid ?? null,
      stats: this.stats,
    };
  }

  emitStats(kind) {
    this.emit({
      ...this.baseEvent("cas/stats"),
      kind,
      snapshot: this.statsSnapshot(),
    });
  }

  emitError(message, extra = {}) {
    this.emit({
      ...this.baseEvent("cas/error"),
      message,
      ...extra,
    });
  }

  emitState(kind) {
    this.emit({
      ...this.baseEvent("cas/state"),
      kind,
      stateFile: this.stateFileAbs,
      state: this.state,
    });
  }

  toAbsStateFile() {
    if (!this.stateFileAbs) {
      const sf = this.opts.stateFile;
      this.stateFileAbs = isAbsolute(sf) ? sf : resolve(this.cwd, sf);
    }
    return this.stateFileAbs;
  }

  async loadState() {
    const sf = this.toAbsStateFile();
    this.state = await readStateFile(sf);
  }

  async updateCurrentThreadId(threadId) {
    if (!threadId || typeof threadId !== "string") return;
    if (this.state.currentThreadId === threadId) return;

    this.state = { ...this.state, currentThreadId: threadId };
    try {
      await writeStateFile(this.toAbsStateFile(), this.state);
      this.emitState("updated");
    } catch (err) {
      this.emitError("Failed to write state file", { error: String(err) });
    }
  }

  allocId() {
    const id = this.nextId;
    this.nextId += 1;
    return id;
  }

  waitForResponse(id, timeoutMs = 10_000) {
    if (!(typeof id === "string" || typeof id === "number")) {
      return Promise.reject(new Error("waitForResponse: id must be string|number"));
    }
    if (this.pendingResponseWaiters.has(id)) {
      return Promise.reject(new Error(`waitForResponse: duplicate waiter for id ${id}`));
    }

    return new Promise((resolve, reject) => {
      const timeout =
        timeoutMs > 0
          ? setTimeout(() => {
              this.pendingResponseWaiters.delete(id);
              reject(new Error(`Timed out waiting for response id ${id}`));
            }, timeoutMs)
          : null;
      this.pendingResponseWaiters.set(id, { resolve, reject, timeout });
    });
  }

  failAllResponseWaiters(err) {
    const error = err instanceof Error ? err : new Error(String(err));
    for (const [id, waiter] of this.pendingResponseWaiters.entries()) {
      if (waiter.timeout) clearTimeout(waiter.timeout);
      waiter.reject(error);
      this.pendingResponseWaiters.delete(id);
    }
  }

  clearPendingServerRequest(id) {
    const pending = this.pendingServerRequests.get(id) ?? null;
    if (!pending) return null;
    if (pending.timeout) clearTimeout(pending.timeout);
    this.pendingServerRequests.delete(id);
    return pending;
  }

  sendServerRequestError(id, method, code, message, data, reason) {
    const error = { code, message };
    if (data !== undefined) error.data = data;
    this.sendToServer(
      { id, error },
      {
        reason,
        method,
      },
    );
  }

  sendToServer(msg, meta = {}) {
    if (!this.child || !this.child.stdin) {
      this.emitError("app-server not running", { meta, msg });
      return;
    }

    try {
      this.child.stdin.write(`${JSON.stringify(msg)}\n`);
    } catch (err) {
      this.emitError("Failed to write to app-server stdin", {
        error: String(err),
        msg,
      });
      return;
    }

    this.stats.toServerMessages += 1;

    const cls = classifyJsonRpc(msg);
    const routing = deriveRoutingKeys(msg);

    this.emit({
      ...this.baseEvent("cas/toServer"),
      kind: cls.kind,
      method: cls.method,
      id: cls.id,
      threadId: routing.threadId,
      turnId: routing.turnId,
      itemId: routing.itemId,
      ...meta,
      msg,
    });
  }

  async start() {
    await this.loadState();
    this.emitState("loaded");

    this.emit({
      ...this.baseEvent("cas/starting"),
      codexPath: this.opts.codexPath,
      stateFile: this.toAbsStateFile(),
      cwd: this.cwd,
    });

    const child = spawn(this.opts.codexPath, ["app-server"], {
      stdio: ["pipe", "pipe", "pipe"],
      cwd: this.cwd,
      env: { ...process.env },
    });
    this.child = child;

    child.on("error", (err) => {
      this.emitError("Failed to spawn codex app-server", { error: String(err) });
      this.requestExit(1, "spawn-error");
    });

    child.on("exit", (code, signal) => {
      this.emit({
        ...this.baseEvent("cas/appServerExit"),
        code,
        signal,
      });

      if (this.exitRequested) {
        this.requestExit(0, "client-exit");
        return;
      }

      this.requestExit(code ?? 1, "app-server-exit");
    });

    if (child.stderr) {
      const rlErr = createInterface({
        input: child.stderr,
        crlfDelay: Infinity,
      });
      this.childStderrRl = rlErr;
      rlErr.on("line", (line) => {
        this.emit({
          ...this.baseEvent("cas/appServerStderr"),
          line,
        });
      });
    }

    if (child.stdout) {
      const rl = createInterface({ input: child.stdout, crlfDelay: Infinity });
      this.childStdoutRl = rl;
      rl.on("line", (line) => {
        void this.onServerLine(line);
      });
    }

    const rlIn = createInterface({ input: process.stdin, crlfDelay: Infinity });
    this.stdinRl = rlIn;
    rlIn.on("line", (line) => {
      void this.onClientLine(line);
    });

    await this.handshake();

    this.ready = true;
    this.emit({
      ...this.baseEvent("cas/ready"),
      codexPath: this.opts.codexPath,
      cwd: this.cwd,
      stateFile: this.toAbsStateFile(),
      appServerPid: child.pid ?? null,
      appServerUserAgent: this.appServerUserAgent,
    });

    if (this.opts.heartbeatMs > 0) {
      this.heartbeatTimer = setInterval(() => {
        this.emitStats("heartbeat");
      }, this.opts.heartbeatMs);
      this.heartbeatTimer.unref?.();
    }

    for (const msg of this.bufferedInput) {
      await this.handleClientMessage(msg);
    }
    this.bufferedInput = [];
  }

  async handshake() {
    const capabilities = {
      experimentalApi: true,
    };
    if (this.opts.optOutNotificationMethods.length > 0) {
      capabilities.optOutNotificationMethods = [
        ...new Set(this.opts.optOutNotificationMethods),
      ];
    }

    const id = this.allocId();
    const initialize = {
      method: "initialize",
      id,
      params: {
        clientInfo: {
          name: this.opts.clientName,
          title: this.opts.clientTitle,
          version: this.opts.clientVersion,
        },
        capabilities,
      },
    };

    this.pendingClientRequests.set(id, {
      clientRequestId: "cas/initialize",
      method: "initialize",
      internal: true,
      threadIdHint: null,
      turnIdHint: null,
      itemIdHint: null,
    });

    this.sendToServer(initialize, { reason: "handshake" });

    let response;
    try {
      response = await this.waitForResponse(id, 10_000);
    } catch (err) {
      this.emitError("Handshake failed: initialize timed out", { error: String(err) });
      this.requestExit(1, "handshake-timeout");
      throw err;
    }

    if (isObject(response) && Object.prototype.hasOwnProperty.call(response, "error")) {
      this.emitError("Handshake failed: initialize returned error", {
        error: response.error,
      });
      this.requestExit(1, "handshake-error");
      throw new Error("initialize returned error");
    }

    if (isObject(response) && isObject(response.result)) {
      const ua = response.result.userAgent;
      if (typeof ua === "string") this.appServerUserAgent = ua;
    }

    this.sendToServer({ method: "initialized" }, { reason: "handshake" });
  }

  async onClientLine(line) {
    if (!line.trim()) return;

    this.stats.clientLines += 1;

    const parsed = safeJsonParse(line);
    if (!parsed.ok) {
      this.stats.clientParseErrors += 1;
      this.emitError("Failed to parse client JSONL", {
        line,
        error: parsed.error.message,
      });
      return;
    }

    if (!this.ready) {
      this.bufferedInput.push(parsed.value);
      return;
    }

    await this.handleClientMessage(parsed.value);
  }

  async handleClientMessage(msg) {
    if (!isObject(msg) || typeof msg.type !== "string") {
      this.emitError("Invalid cas command (expected object with type)", {
        msg,
      });
      return;
    }

    if (msg.type === "cas/exit") {
      this.emit({
        ...this.baseEvent("cas/exiting"),
        reason: "client",
      });

      this.exitRequested = true;
      this.pauseIo("client-exit");

      const child = this.child;
      if (child && child.exitCode === null) {
        child.kill("SIGTERM");
        if (this.exitHardTimer) clearTimeout(this.exitHardTimer);
        if (this.opts.killTimeoutMs > 0) {
          const timer = setTimeout(() => {
            if (child.exitCode === null) child.kill("SIGKILL");
          }, this.opts.killTimeoutMs);
          timer.unref?.();
        }
      } else {
        this.requestExit(0, "client-exit");
      }
      return;
    }

    if (msg.type === "cas/state/get") {
      this.emitState("get");
      return;
    }

    if (msg.type === "cas/stats/get") {
      this.emitStats("get");
      return;
    }

    if (msg.type === "cas/request") {
      const method = msg.method;
      if (typeof method !== "string") {
        this.emitError("cas/request missing method", { msg });
        return;
      }

      const id =
        typeof msg.id === "string" || typeof msg.id === "number"
          ? msg.id
          : this.allocId();
      let params = Object.prototype.hasOwnProperty.call(msg, "params")
        ? msg.params
        : undefined;
      const clientRequestId =
        typeof msg.clientRequestId === "string" ? msg.clientRequestId : null;

      // Best-effort ergonomics.
      // - `thread/start` requires `experimentalRawEvents` on the wire.
      // - `turn/start` and `turn/steer` text inputs should include `text_elements` (empty array if none).
      if (method === "thread/start") {
        if (!isObject(params)) params = {};
        if (!Object.prototype.hasOwnProperty.call(params, "experimentalRawEvents")) {
          params.experimentalRawEvents = false;
        }
      }
      if (
        (method === "turn/start" || method === "turn/steer") &&
        isObject(params) &&
        Array.isArray(params.input)
      ) {
        params = {
          ...params,
          input: params.input.map((it) => {
            if (!isObject(it) || it.type !== "text") return it;
            if (Object.prototype.hasOwnProperty.call(it, "text_elements")) return it;
            return { ...it, text_elements: [] };
          }),
        };
      }

      let threadIdHint = null;
      let turnIdHint = null;
      let itemIdHint = null;
      if (isObject(params)) {
        if (typeof params.threadId === "string") threadIdHint = params.threadId;
        if (typeof params.turnId === "string") turnIdHint = params.turnId;
        if (!turnIdHint && typeof params.expectedTurnId === "string") {
          turnIdHint = params.expectedTurnId;
        }
        if (typeof params.itemId === "string") itemIdHint = params.itemId;
      }

      this.pendingClientRequests.set(id, {
        clientRequestId,
        method,
        internal: false,
        threadIdHint,
        turnIdHint,
        itemIdHint,
      });

      const req = { method, id, params };
      this.sendToServer(req, { reason: "clientRequest", clientRequestId });
      return;
    }

    if (msg.type === "cas/respond") {
      const id = msg.id;
      if (!(typeof id === "string" || typeof id === "number")) {
        this.emitError("cas/respond missing id", { msg });
        return;
      }

      const hasResult = Object.prototype.hasOwnProperty.call(msg, "result");
      const hasError = Object.prototype.hasOwnProperty.call(msg, "error");
      if (!hasResult && !hasError) {
        this.emitError("cas/respond must include result or error", { msg });
        return;
      }

      const pending = this.pendingServerRequests.get(id) ?? null;
      if (!pending) {
        this.emitError("cas/respond id does not match a pending server request", {
          id,
          msg,
        });
        return;
      }

      if (hasError) {
        this.clearPendingServerRequest(id);
        this.sendToServer(
          { id, error: msg.error },
          { reason: "clientResponse", method: pending.method },
        );
        return;
      }

      const validation = validateServerRequestResult(pending.method, msg.result);
      if (!validation.ok) {
        this.clearPendingServerRequest(id);
        this.emitError("Invalid cas/respond payload for server request", {
          id,
          method: pending.method,
          validationError: validation.message,
        });
        this.sendServerRequestError(
          id,
          pending.method,
          JSONRPC_INVALID_PARAMS,
          validation.message,
          undefined,
          "clientResponseValidationError",
        );
        return;
      }

      this.clearPendingServerRequest(id);
      this.sendToServer(
        { id, result: msg.result },
        { reason: "clientResponse", method: pending.method },
      );
      return;
    }

    if (msg.type === "cas/send") {
      if (!isObject(msg.msg)) {
        this.emitError("cas/send missing msg object", { msg });
        return;
      }
      this.sendToServer(msg.msg, { reason: "clientRaw" });
      return;
    }

    this.emitError(`Unknown cas command type: ${msg.type}`, { msg });
  }

  async onServerLine(line) {
    if (!line.trim()) return;

    this.stats.serverLines += 1;

    const parsed = safeJsonParse(line);
    if (!parsed.ok) {
      this.stats.serverParseErrors += 1;
      this.emit({
        ...this.baseEvent("cas/fromServer"),
        kind: "nonJson",
        method: null,
        id: null,
        threadId: null,
        turnId: null,
        itemId: null,
        line,
      });
      return;
    }

    /** @type {any} */
    const msg = parsed.value;

    this.stats.fromServerMessages += 1;

    const cls = classifyJsonRpc(msg);

    if (
      cls.kind === "response" &&
      cls.id !== null &&
      this.pendingResponseWaiters.has(cls.id)
    ) {
      const waiter = this.pendingResponseWaiters.get(cls.id);
      if (waiter?.timeout) clearTimeout(waiter.timeout);
      this.pendingResponseWaiters.delete(cls.id);
      waiter?.resolve(msg);
    }

    let clientRequestId = null;
    let requestMethodHint = null;
    let requestHints = { threadIdHint: null, turnIdHint: null, itemIdHint: null };
    let isInternal = false;
    if (
      cls.kind === "response" &&
      cls.id !== null &&
      this.pendingClientRequests.has(cls.id)
    ) {
      const pending = this.pendingClientRequests.get(cls.id);
      clientRequestId = pending?.clientRequestId ?? null;
      requestMethodHint = pending?.method ?? null;

      requestHints = {
        threadIdHint: pending?.threadIdHint ?? null,
        turnIdHint: pending?.turnIdHint ?? null,
        itemIdHint: pending?.itemIdHint ?? null,
      };
      isInternal = Boolean(pending?.internal);

      if (
        isInternal &&
        requestMethodHint === "initialize" &&
        isObject(msg.result) &&
        typeof msg.result.userAgent === "string"
      ) {
        this.appServerUserAgent = msg.result.userAgent;
      }

      this.pendingClientRequests.delete(cls.id);
    }

    const routing = deriveRoutingKeys(msg, requestMethodHint);
    if (!routing.threadId && requestHints.threadIdHint)
      routing.threadId = requestHints.threadIdHint;
    if (!routing.turnId && requestHints.turnIdHint) routing.turnId = requestHints.turnIdHint;
    if (!routing.itemId && requestHints.itemIdHint) routing.itemId = requestHints.itemIdHint;

    this.emit({
      ...this.baseEvent("cas/fromServer"),
      kind: cls.kind,
      method: cls.method,
      id: cls.id,
      requestMethod: requestMethodHint,
      clientRequestId,
      internal: isInternal,
      threadId: routing.threadId,
      turnId: routing.turnId,
      itemId: routing.itemId,
      msg,
    });

    if (routing.threadId) {
      await this.updateCurrentThreadId(routing.threadId);
    }

    if (cls.kind === "request" && cls.method && cls.id !== null) {
      await this.handleServerRequest(msg);
    }
  }

  async handleServerRequest(msg) {
    const method = msg.method;
    const id = msg.id;
    const params = isObject(msg.params) ? msg.params : {};

    if (method === "item/commandExecution/requestApproval") {
      const proposed =
        params.proposedExecpolicyAmendment ?? params.proposed_execpolicy_amendment;

      let decision;
      if (this.opts.execApprovalDecision === "auto") {
        decision =
          Array.isArray(proposed) && proposed.length
            ? {
                acceptWithExecpolicyAmendment: {
                  execpolicy_amendment: proposed,
                },
              }
            : "acceptForSession";
      } else {
        decision = this.opts.execApprovalDecision;
      }

      this.sendToServer(
        { id, result: { decision } },
        { reason: "autoApproval", method },
      );
      this.stats.autoApprovals += 1;
      return;
    }

    if (method === "item/fileChange/requestApproval") {
      const decision =
        this.opts.fileApprovalDecision === "auto"
          ? "acceptForSession"
          : this.opts.fileApprovalDecision;
      this.sendToServer(
        { id, result: { decision } },
        { reason: "autoApproval", method },
      );
      this.stats.autoApprovals += 1;
      return;
    }

    if (method === "execCommandApproval" || method === "applyPatchApproval") {
      this.emitError("Deprecated server request rejected (cas is v2-only)", {
        id,
        method,
      });
      this.sendServerRequestError(
        id,
        method,
        JSONRPC_INVALID_PARAMS,
        `Unsupported deprecated server request: ${method}`,
        {
          supportedMode: "v2-only",
        },
        "legacyUnsupported",
      );
      return;
    }

    const timeout =
      this.opts.serverRequestTimeoutMs > 0
        ? setTimeout(() => {
            const pending = this.clearPendingServerRequest(id);
            if (!pending) return;
            this.emitError("Timed out waiting for orchestrator response", {
              id,
              method: pending.method,
              timeoutMs: this.opts.serverRequestTimeoutMs,
            });
            this.emit({
              ...this.baseEvent("cas/serverRequestTimeout"),
              id,
              method: pending.method,
              timeoutMs: this.opts.serverRequestTimeoutMs,
              threadId: typeof pending.params.threadId === "string" ? pending.params.threadId : null,
              turnId: typeof pending.params.turnId === "string" ? pending.params.turnId : null,
              itemId: typeof pending.params.itemId === "string" ? pending.params.itemId : null,
            });
            this.sendServerRequestError(
              id,
              pending.method,
              JSONRPC_REQUEST_TIMEOUT,
              `Timed out waiting for orchestrator response to ${pending.method}`,
              undefined,
              "serverRequestTimeout",
            );
          }, this.opts.serverRequestTimeoutMs)
        : null;
    timeout?.unref?.();

    this.pendingServerRequests.set(id, {
      method,
      params,
      timeout,
      startedAtMs: nowMs(),
    });
    this.stats.forwardedServerRequests += 1;
    this.emit({
      ...this.baseEvent("cas/serverRequest"),
      method,
      id,
      timeoutMs: this.opts.serverRequestTimeoutMs,
      threadId: typeof params.threadId === "string" ? params.threadId : null,
      turnId: typeof params.turnId === "string" ? params.turnId : null,
      itemId: typeof params.itemId === "string" ? params.itemId : null,
      msg,
    });
  }
}

async function main() {
  const parsed = parseArgs(process.argv.slice(2));
  if (!parsed.ok) {
    if (parsed.help) {
      process.stderr.write(`${helpText()}\n`);
      return 0;
    }
    process.stderr.write(`${parsed.error ?? "invalid args"}\n`);
    return 2;
  }

  const proxy = new CasProxy(parsed.opts);

  process.on("SIGINT", () => {
    proxy.emit({
      ...proxy.baseEvent("cas/signal"),
      signal: "SIGINT",
    });
    proxy.child?.kill("SIGINT");
  });
  process.on("SIGTERM", () => {
    proxy.emit({
      ...proxy.baseEvent("cas/signal"),
      signal: "SIGTERM",
    });
    proxy.child?.kill("SIGTERM");
  });

  await proxy.start();
  return 0;
}

main()
  .then((code) => {
    process.exitCode = code;
  })
  .catch((err) => {
    process.stderr.write(
      `Fatal: ${err instanceof Error ? (err.stack ?? err.message) : String(err)}\n`,
    );
    process.exitCode = 1;
  });
