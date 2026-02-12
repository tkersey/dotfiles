// Minimal JS client for casp_proxy.mjs.
//
// - Spawns the casp proxy as a subprocess.
// - Exposes request() -> Promise(result) with id correlation.
// - Emits all casp events (lossless) for orchestration.

import { spawn } from "node:child_process";
import { randomUUID } from "node:crypto";
import { EventEmitter } from "node:events";
import { dirname, resolve } from "node:path";
import { createInterface } from "node:readline";
import { fileURLToPath } from "node:url";

function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function safeJsonParse(line) {
  try {
    return { ok: true, value: JSON.parse(line) };
  } catch (err) {
    return { ok: false, error: err instanceof Error ? err : new Error(String(err)) };
  }
}

function defaultProxyScriptPath() {
  const here = dirname(fileURLToPath(import.meta.url));
  return resolve(here, "casp_proxy.mjs");
}

export class CaspClient extends EventEmitter {
  /**
   * @param {{
   *   nodePath?: string,
   *   proxyScript?: string,
   *   codexPath?: string,
   *   cwd?: string,
   *   stateFile?: string,
   *   clientName?: string,
   *   clientTitle?: string,
   *   clientVersion?: string,
   *   serverRequestTimeoutMs?: number,
   *   optOutNotificationMethods?: string[],
   * }} [opts]
   */
  constructor(opts = {}) {
    super();

    this.opts = {
      nodePath: opts.nodePath ?? process.execPath,
      proxyScript: opts.proxyScript ?? defaultProxyScriptPath(),
      codexPath: opts.codexPath,
      cwd: opts.cwd,
      stateFile: opts.stateFile,
      clientName: opts.clientName,
      clientTitle: opts.clientTitle,
      clientVersion: opts.clientVersion,
      serverRequestTimeoutMs: opts.serverRequestTimeoutMs,
      optOutNotificationMethods: opts.optOutNotificationMethods,
    };

    /** @type {import('node:child_process').ChildProcess | null} */
    this.child = null;

    /** @type {Map<string|number, { resolve: (value: any) => void, reject: (err: Error) => void, timeout: NodeJS.Timeout | null }>} */
    this.pending = new Map();

    /** @type {Promise<void> | null} */
    this.readyPromise = null;
    this._readyResolve = null;
    this._readyReject = null;
  }

  isRunning() {
    return Boolean(this.child && this.child.exitCode === null);
  }

  async start() {
    if (this.readyPromise) return this.readyPromise;

    this.readyPromise = new Promise((resolve, reject) => {
      this._readyResolve = resolve;
      this._readyReject = reject;
    });

    const args = [this.opts.proxyScript];
    if (this.opts.codexPath) args.push("--codex", this.opts.codexPath);
    if (this.opts.cwd) args.push("--cwd", this.opts.cwd);
    if (this.opts.stateFile) args.push("--state-file", this.opts.stateFile);
    if (this.opts.clientName) args.push("--client-name", this.opts.clientName);
    if (this.opts.clientTitle) args.push("--client-title", this.opts.clientTitle);
    if (this.opts.clientVersion) args.push("--client-version", this.opts.clientVersion);
    if (Number.isFinite(this.opts.serverRequestTimeoutMs)) {
      args.push("--server-request-timeout-ms", String(this.opts.serverRequestTimeoutMs));
    }
    if (Array.isArray(this.opts.optOutNotificationMethods)) {
      for (const method of this.opts.optOutNotificationMethods) {
        if (typeof method !== "string" || !method) continue;
        args.push("--opt-out-notification-method", method);
      }
    }

    const child = spawn(this.opts.nodePath, args, {
      stdio: ["pipe", "pipe", "pipe"],
      env: { ...process.env },
    });
    this.child = child;

    child.on("error", (err) => {
      const e = err instanceof Error ? err : new Error(String(err));
      this._failAllPending(e);
      this._readyReject?.(e);
      this.emit("error", e);
    });

    child.on("exit", (code, signal) => {
      const e = new Error(
        `casp proxy exited (code=${code ?? "null"}, signal=${signal ?? "null"})`,
      );
      this._failAllPending(e);

      // If we were still waiting for ready, fail it.
      this._readyReject?.(e);

      this.emit("exit", { code, signal });
    });

    if (child.stderr) {
      const rlErr = createInterface({ input: child.stderr, crlfDelay: Infinity });
      rlErr.on("line", (line) => {
        // Debug channel: do not parse.
        this.emit("proxyStderr", line);
      });
    }

    if (child.stdout) {
      const rl = createInterface({ input: child.stdout, crlfDelay: Infinity });
      rl.on("line", (line) => {
        this._onProxyLine(line);
      });
    }

    return this.readyPromise;
  }

  /**
   * Send a JSONL message to the proxy.
   * @param {any} msg
   */
  send(msg) {
    if (!this.child || !this.child.stdin) {
      throw new Error("casp client not started");
    }
    this.child.stdin.write(`${JSON.stringify(msg)}\n`);
  }

  /**
   * Request an app-server method via the proxy.
   * @param {string} method
   * @param {any} [params]
   * @param {{ id?: string|number, clientRequestId?: string, timeoutMs?: number }} [opts]
   */
  request(method, params, opts = {}) {
    if (typeof method !== "string" || !method) {
      throw new Error("request(method): method must be a non-empty string");
    }

    const id = opts.id ?? `casp-${randomUUID()}`;
    const clientRequestId = opts.clientRequestId ?? String(id);
    const timeoutMs = opts.timeoutMs ?? 60_000;

    /** @type {any} */
    const msg = {
      type: "casp/request",
      clientRequestId,
      id,
      method,
    };
    if (params !== undefined) msg.params = params;

    if (this.pending.has(id)) {
      throw new Error(`Duplicate request id: ${id}`);
    }

    const promise = new Promise((resolve, reject) => {
      const timeout =
        timeoutMs > 0
          ? setTimeout(() => {
              this.pending.delete(id);
              reject(new Error(`Request timed out: ${method} (${id})`));
            }, timeoutMs)
          : null;
      this.pending.set(id, { resolve, reject, timeout });
    });

    this.send(msg);
    return promise;
  }

  /**
   * Start a new thread with safe defaults.
   *
   * Note: `thread/start` requires `experimentalRawEvents` on the wire.
   * casp defaults it to `false` if you omit it.
   *
   * @param {any} [params]
   * @param {{ id?: string|number, clientRequestId?: string, timeoutMs?: number }} [opts]
   */
  startThread(params = {}, opts = {}) {
    const p = isObject(params) ? { ...params } : {};
    if (!Object.prototype.hasOwnProperty.call(p, "experimentalRawEvents")) {
      p.experimentalRawEvents = false;
    }
    return this.request("thread/start", p, opts);
  }

  /**
   * Resume an existing thread.
   *
   * @param {any} params
   * @param {{ id?: string|number, clientRequestId?: string, timeoutMs?: number }} [opts]
   */
  resumeThread(params, opts = {}) {
    if (!isObject(params)) {
      throw new Error("resumeThread(params): params must be an object");
    }
    if (typeof params.threadId !== "string" || !params.threadId) {
      throw new Error("resumeThread(params): threadId is required");
    }
    return this.request("thread/resume", params, opts);
  }

  /**
   * List experimental features (paginated).
   *
   * @param {any} [params]
   * @param {{ id?: string|number, clientRequestId?: string, timeoutMs?: number }} [opts]
   */
  listExperimentalFeatures(params = {}, opts = {}) {
    const p = isObject(params) ? { ...params } : {};
    return this.request("experimentalFeature/list", p, opts);
  }

  /**
   * Steer an active turn by appending user input mid-turn.
   *
   * @param {any} params
   * @param {{ id?: string|number, clientRequestId?: string, timeoutMs?: number }} [opts]
   */
  steerTurn(params, opts = {}) {
    if (!isObject(params)) {
      throw new Error("steerTurn(params): params must be an object");
    }
    if (typeof params.threadId !== "string" || !params.threadId) {
      throw new Error("steerTurn(params): threadId is required");
    }
    if (typeof params.expectedTurnId !== "string" || !params.expectedTurnId) {
      throw new Error("steerTurn(params): expectedTurnId is required");
    }
    if (!Array.isArray(params.input)) {
      throw new Error("steerTurn(params): input must be an array");
    }

    const p = {
      ...params,
      input: params.input.map((it) => {
        if (!isObject(it) || it.type !== "text") return it;
        if (Object.prototype.hasOwnProperty.call(it, "text_elements")) return it;
        return { ...it, text_elements: [] };
      }),
    };

    return this.request("turn/steer", p, opts);
  }

  /**
   * Fetch a casp proxy stats snapshot.
   * @param {{ timeoutMs?: number }} [opts]
   */
  getStats(opts = {}) {
    const timeoutMs = opts.timeoutMs ?? 2_000;

    return new Promise((resolve, reject) => {
      let timer = null;

      const cleanup = () => {
        this.off("casp/stats", onStats);
        if (timer) clearTimeout(timer);
      };

      const onStats = (ev) => {
        if (!isObject(ev)) return;
        if (ev.type !== "casp/stats") return;
        if (ev.kind !== "get") return;
        cleanup();
        resolve(ev.snapshot);
      };

      this.on("casp/stats", onStats);

      if (timeoutMs > 0) {
        timer = setTimeout(() => {
          cleanup();
          reject(new Error("Timed out waiting for casp/stats"));
        }, timeoutMs);
      }

      this.send({ type: "casp/stats/get" });
    });
  }

  /**
   * Start a turn and collect its streamed item lifecycle until `turn/completed`.
   *
   * This exists because `turn/started` and `turn/completed` currently include an empty `turn.items`.
   * The canonical item list is the `item/*` notification stream.
   *
   * @param {any} turnStartParams
   * @param {{ timeoutMs?: number }} [opts]
   */
  async startTurnAndCollect(turnStartParams, opts = {}) {
    if (!isObject(turnStartParams)) {
      throw new Error("startTurnAndCollect: turnStartParams must be an object");
    }
    if (typeof turnStartParams.threadId !== "string" || !turnStartParams.threadId) {
      throw new Error("startTurnAndCollect: threadId is required");
    }

    const threadId = turnStartParams.threadId;
    const timeoutMs = opts.timeoutMs ?? 10 * 60_000;

    /** @type {Map<string, any>} */
    const itemsById = new Map();
    /** @type {Array<string>} */
    const itemOrder = [];
    /** @type {Map<string, string>} */
    const agentMessageTextByItemId = new Map();

    /** @type {Array<any>} */
    const buffered = [];
    const maxBuffer = 10_000;

    let expectedTurnId = null;
    let finalTurn = null;

    let timer = null;

    let done = false;
    /** @type {(() => void) | null} */
    let doneResolve = null;
    const donePromise = new Promise((resolve) => {
      doneResolve = resolve;
    });
    const finish = () => {
      if (done) return;
      done = true;
      doneResolve?.();
    };

    const processEvent = (ev) => {
      if (!isObject(ev)) return;
      if (ev.type !== "casp/fromServer") return;
      if (ev.kind !== "notification") return;
      if (ev.threadId !== threadId) return;
      if (expectedTurnId && ev.turnId && ev.turnId !== expectedTurnId) return;

      const method = ev.method;
      if (typeof method !== "string") return;
      const msg = isObject(ev.msg) ? ev.msg : null;
      const params = msg && isObject(msg.params) ? msg.params : null;
      if (!params) return;

      if (method === "turn/completed") {
        const turn = params.turn;
        if (isObject(turn) && typeof turn.id === "string") {
          if (!expectedTurnId) expectedTurnId = turn.id;
          if (expectedTurnId === turn.id) {
            finalTurn = turn;
            finish();
            return;
          }
        }
      }

      if (method === "item/started" || method === "item/completed") {
        const item = params.item;
        if (isObject(item) && typeof item.id === "string") {
          if (!itemsById.has(item.id)) itemOrder.push(item.id);
          itemsById.set(item.id, item);
          if (item.type === "agentMessage" && typeof item.text === "string") {
            agentMessageTextByItemId.set(item.id, item.text);
          }
        }
      }

      if (method === "item/agentMessage/delta") {
        const itemId = typeof params.itemId === "string" ? params.itemId : ev.itemId;
        const delta = typeof params.delta === "string" ? params.delta : null;
        if (itemId && delta) {
          const prev = agentMessageTextByItemId.get(itemId) ?? "";
          agentMessageTextByItemId.set(itemId, `${prev}${delta}`);
        }
      }
    };

    const onFromServer = (ev) => {
      if (!isObject(ev)) return;
      if (ev.type !== "casp/fromServer") return;
      if (ev.kind !== "notification") return;
      if (ev.threadId !== threadId) return;

      if (!expectedTurnId && buffered.length < maxBuffer) buffered.push(ev);
      if (expectedTurnId) processEvent(ev);
    };

    this.on("casp/fromServer", onFromServer);

    const cleanup = () => {
      this.off("casp/fromServer", onFromServer);
      if (timer) clearTimeout(timer);
    };

    try {
      const timeoutPromise =
        timeoutMs > 0
          ? new Promise((_, reject) => {
              timer = setTimeout(() => {
                reject(new Error("Timed out waiting for turn/completed"));
              }, timeoutMs);
            })
          : null;

      const startResult = await this.request("turn/start", turnStartParams);
      const turnId =
        isObject(startResult) && isObject(startResult.turn) && typeof startResult.turn.id === "string"
          ? startResult.turn.id
          : null;
      if (!turnId) throw new Error("turn/start did not return turn.id");
      expectedTurnId = turnId;

      for (const ev of buffered) processEvent(ev);

      if (timeoutPromise) await Promise.race([donePromise, timeoutPromise]);
      else await donePromise;

      if (!finalTurn) throw new Error("turn/completed observed without final turn payload");

      const items = itemOrder
        .map((id) => itemsById.get(id))
        .filter((it) => it !== undefined);

      let agentMessageText = null;
      for (let i = items.length - 1; i >= 0; i -= 1) {
        const it = items[i];
        if (isObject(it) && it.type === "agentMessage" && typeof it.text === "string") {
          agentMessageText = it.text;
          break;
        }
      }

      // If the final item didn't include text yet, fall back to delta-accumulation.
      if (!agentMessageText) {
        for (let i = itemOrder.length - 1; i >= 0; i -= 1) {
          const id = itemOrder[i];
          const text = agentMessageTextByItemId.get(id);
          if (text) {
            agentMessageText = text;
            break;
          }
        }
      }

      return {
        threadId,
        turnId: expectedTurnId,
        turn: finalTurn,
        items,
        agentMessageText,
      };
    } finally {
      cleanup();
    }
  }

  /**
   * Respond to a forwarded server request.
   * @param {string|number} id
   * @param {{ result?: any, error?: any }} payload
   */
  respond(id, payload) {
    if (!(typeof id === "string" || typeof id === "number")) {
      throw new Error("respond(id): id must be string|number");
    }
    if (!isObject(payload)) {
      throw new Error("respond(id, payload): payload must be an object");
    }
    const hasResult = Object.prototype.hasOwnProperty.call(payload, "result");
    const hasError = Object.prototype.hasOwnProperty.call(payload, "error");
    if (hasResult === hasError) {
      throw new Error("respond(id, payload): include exactly one of result or error");
    }

    /** @type {any} */
    const msg = { type: "casp/respond", id };
    if (hasError) msg.error = payload.error;
    else msg.result = payload.result;
    this.send(msg);
  }

  /**
   * Send a JSON-RPC error response for a forwarded server request.
   * @param {string|number} id
   * @param {string} message
   * @param {{ code?: number, data?: any }} [opts]
   */
  respondError(id, message, opts = {}) {
    if (typeof message !== "string" || !message) {
      throw new Error("respondError(id, message): message must be a non-empty string");
    }
    /** @type {any} */
    const error = {
      code: Number.isInteger(opts.code) ? opts.code : -32000,
      message,
    };
    if (Object.prototype.hasOwnProperty.call(opts, "data")) {
      error.data = opts.data;
    }
    this.respond(id, { error });
  }

  async close() {
    if (!this.child) return;
    try {
      this.send({ type: "casp/exit" });
    } catch {
      // ignore
    }
  }

  _onProxyLine(line) {
    if (!line.trim()) return;

    const parsed = safeJsonParse(line);
    if (!parsed.ok) {
      this.emit("casp/nonJson", { line, error: parsed.error.message });
      return;
    }

    const event = parsed.value;
    this.emit("event", event);
    if (isObject(event) && typeof event.type === "string") {
      this.emit(event.type, event);
    }

    if (isObject(event) && event.type === "casp/ready") {
      this._readyResolve?.();
      this._readyResolve = null;
      this._readyReject = null;
      return;
    }

    if (
      isObject(event) &&
      event.type === "casp/fromServer" &&
      event.kind === "response" &&
      (typeof event.id === "string" || typeof event.id === "number")
    ) {
      const pending = this.pending.get(event.id);
      if (!pending) return;

      if (pending.timeout) clearTimeout(pending.timeout);
      this.pending.delete(event.id);

      const msg = isObject(event.msg) ? event.msg : {};
      if (Object.prototype.hasOwnProperty.call(msg, "error")) {
        pending.reject(new Error(JSON.stringify(msg.error)));
      } else {
        pending.resolve(msg.result);
      }
    }
  }

  _failAllPending(err) {
    for (const [id, pending] of this.pending.entries()) {
      if (pending.timeout) clearTimeout(pending.timeout);
      pending.reject(err);
      this.pending.delete(id);
    }
  }
}
