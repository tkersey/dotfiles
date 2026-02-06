#!/usr/bin/env node
// Casp JSONL proxy for `codex app-server`.
//
// - Reads JSONL commands from stdin.
// - Spawns `codex app-server` and performs initialize/initialized handshake.
// - Emits JSONL events on stdout (lossless; includes raw app-server messages).
// - Auto-accepts approvals.
// - Forwards tool requests to the orchestrator (stdin) and blocks until a response arrives.

import { spawn } from "node:child_process";
import { randomUUID } from "node:crypto";
import { once } from "node:events";
import { mkdir, readFile, rename, writeFile } from "node:fs/promises";
import { dirname, isAbsolute, resolve } from "node:path";
import { createInterface } from "node:readline";

const CASP_EVENT_VERSION = 1;

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
  /** @type {{codexPath: string, cwd: string, stateFile: string, clientName: string, clientTitle: string, clientVersion: string, heartbeatMs: number, maxOutQueue: number, killTimeoutMs: number}} */
  const opts = {
    codexPath: "codex",
    cwd: process.cwd(),
    stateFile: ".casp/state.json",
    clientName: "casp",
    clientTitle: "casp skill",
    clientVersion: "0.1.0",
    // Emit casp/heartbeat every N ms (0 disables).
    heartbeatMs: 0,
    // Max buffered stdout events before pausing inputs.
    maxOutQueue: 20_000,
    // After casp/exit, SIGKILL app-server after N ms.
    killTimeoutMs: 2_000,
  };

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
      continue;
    }
    if (arg === "--state-file") {
      opts.stateFile = takeValue();
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

    throw new Error(`Unknown arg: ${arg}`);
  }

  return { ok: true, help: false, error: null, opts };
}

function helpText() {
  return [
    "casp_proxy.mjs - JSONL proxy for `codex app-server`",
    "",
    "Usage:",
    "  node scripts/casp_proxy.mjs [--codex codex] [--cwd DIR] [--state-file .casp/state.json]",
    "                        [--heartbeat-ms 0] [--max-out-queue 20000] [--kill-timeout-ms 2000]",
    "",
    "stdin JSONL:",
    '  { "type": "casp/request", "clientRequestId": "...", "method": "thread/start", "params": { ... } }',
    '  { "type": "casp/respond", "id": 123, "result": { ... } }',
    '  { "type": "casp/respond", "id": 123, "error": { ... } }',
    '  { "type": "casp/state/get" }',
    '  { "type": "casp/stats/get" }',
    '  { "type": "casp/exit" }',
    "",
    "stdout JSONL:",
    "  casp emits events like casp/ready, casp/fromServer, casp/toServer, casp/error.",
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
  const tmp = `${stateFile}.tmp`;
  await writeFile(tmp, JSON.stringify(state), "utf8");
  await rename(tmp, stateFile);
}

class CaspProxy {
  /** @param {{codexPath: string, cwd: string, stateFile: string, clientName: string, clientTitle: string, clientVersion: string, heartbeatMs: number, maxOutQueue: number, killTimeoutMs: number}} opts */
  constructor(opts) {
    this.opts = opts;
    this.cwd = opts.cwd;
    this.sessionId = `casp-${randomUUID()}`;
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

    /** @type {Map<string|number, { method: string, params: any }>} */
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
      v: CASP_EVENT_VERSION,
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
      ...this.baseEvent("casp/ioPaused"),
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
      ...this.baseEvent("casp/ioResumed"),
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

    this.failAllResponseWaiters(new Error(`casp exiting: ${reason}`));

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
      ...this.baseEvent("casp/stats"),
      kind,
      snapshot: this.statsSnapshot(),
    });
  }

  emitError(message, extra = {}) {
    this.emit({
      ...this.baseEvent("casp/error"),
      message,
      ...extra,
    });
  }

  emitState(kind) {
    this.emit({
      ...this.baseEvent("casp/state"),
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
      ...this.baseEvent("casp/toServer"),
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
      ...this.baseEvent("casp/starting"),
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
        ...this.baseEvent("casp/appServerExit"),
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
          ...this.baseEvent("casp/appServerStderr"),
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
      ...this.baseEvent("casp/ready"),
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
        capabilities: {
          experimentalApi: true,
        },
      },
    };

    this.pendingClientRequests.set(id, {
      clientRequestId: "casp/initialize",
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
      this.emitError("Invalid casp command (expected object with type)", {
        msg,
      });
      return;
    }

    if (msg.type === "casp/exit") {
      this.emit({
        ...this.baseEvent("casp/exiting"),
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

    if (msg.type === "casp/state/get") {
      this.emitState("get");
      return;
    }

    if (msg.type === "casp/stats/get") {
      this.emitStats("get");
      return;
    }

    if (msg.type === "casp/request") {
      const method = msg.method;
      if (typeof method !== "string") {
        this.emitError("casp/request missing method", { msg });
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
      // - `turn/start` text inputs should include `text_elements` (empty array if none).
      if (method === "thread/start") {
        if (!isObject(params)) params = {};
        if (!Object.prototype.hasOwnProperty.call(params, "experimentalRawEvents")) {
          params.experimentalRawEvents = false;
        }
      }
      if (method === "turn/start" && isObject(params) && Array.isArray(params.input)) {
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

    if (msg.type === "casp/respond") {
      const id = msg.id;
      if (!(typeof id === "string" || typeof id === "number")) {
        this.emitError("casp/respond missing id", { msg });
        return;
      }

      const hasResult = Object.prototype.hasOwnProperty.call(msg, "result");
      const hasError = Object.prototype.hasOwnProperty.call(msg, "error");
      if (!hasResult && !hasError) {
        this.emitError("casp/respond must include result or error", { msg });
        return;
      }

      const pending = this.pendingServerRequests.get(id) ?? null;

      let result = msg.result;
      if (!hasError && pending?.method === "item/tool/call" && isObject(result)) {
        // Back-compat shim: older callers may send { output: string, success: boolean }.
        if (
          !Object.prototype.hasOwnProperty.call(result, "contentItems") &&
          typeof result.output === "string"
        ) {
          result = {
            contentItems: [{ type: "inputText", text: result.output }],
            success: Boolean(result.success),
          };
        }

        // Also accept snake_case content_items.
        if (
          !Object.prototype.hasOwnProperty.call(result, "contentItems") &&
          Array.isArray(result.content_items)
        ) {
          result = {
            contentItems: result.content_items,
            success: Boolean(result.success),
          };
        }
      }

      const res = hasError ? { id, error: msg.error } : { id, result };
      this.pendingServerRequests.delete(id);
      this.sendToServer(res, { reason: "clientResponse" });
      return;
    }

    if (msg.type === "casp/send") {
      if (!isObject(msg.msg)) {
        this.emitError("casp/send missing msg object", { msg });
        return;
      }
      this.sendToServer(msg.msg, { reason: "clientRaw" });
      return;
    }

    this.emitError(`Unknown casp command type: ${msg.type}`, { msg });
  }

  async onServerLine(line) {
    if (!line.trim()) return;

    this.stats.serverLines += 1;

    const parsed = safeJsonParse(line);
    if (!parsed.ok) {
      this.stats.serverParseErrors += 1;
      this.emit({
        ...this.baseEvent("casp/fromServer"),
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
      ...this.baseEvent("casp/fromServer"),
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
      const decision =
        Array.isArray(proposed) && proposed.length
          ? {
              acceptWithExecpolicyAmendment: {
                execpolicy_amendment: proposed,
              },
            }
          : "acceptForSession";
      this.sendToServer(
        { id, result: { decision } },
        { reason: "autoApproval", method },
      );
      this.stats.autoApprovals += 1;
      return;
    }

    if (method === "item/fileChange/requestApproval") {
      this.sendToServer(
        { id, result: { decision: "acceptForSession" } },
        { reason: "autoApproval", method },
      );
      this.stats.autoApprovals += 1;
      return;
    }

    if (method === "execCommandApproval" || method === "applyPatchApproval") {
      this.sendToServer(
        { id, result: { decision: "approved_for_session" } },
        { reason: "autoApproval", method },
      );
      this.stats.autoApprovals += 1;
      return;
    }

    this.pendingServerRequests.set(id, { method, params });
    this.stats.forwardedServerRequests += 1;
    this.emit({
      ...this.baseEvent("casp/serverRequest"),
      method,
      id,
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

  const proxy = new CaspProxy(parsed.opts);

  process.on("SIGINT", () => {
    proxy.emit({
      ...proxy.baseEvent("casp/signal"),
      signal: "SIGINT",
    });
    proxy.child?.kill("SIGINT");
  });
  process.on("SIGTERM", () => {
    proxy.emit({
      ...proxy.baseEvent("casp/signal"),
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
