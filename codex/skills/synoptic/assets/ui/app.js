(function () {
  "use strict";

  const UI_SCHEMA = "synoptic-ui/v1";
  const token = new URLSearchParams(window.location.search).get("token") || "";
  const elements = Object.fromEntries([
    "app", "round-label", "pr-summary", "refresh-button", "finish-button", "stop-button",
    "primary-gate", "queue", "queue-count", "queue-empty", "tabs", "welcome", "review",
    "diff-title", "diff-state", "stale-banner", "diff", "conversation-title", "session-status",
    "interrupt-button", "close-button", "conversation", "message-form", "message-input",
    "global-approvals", "toast-region"
  ].map((id) => [id.replaceAll("-", "_"), document.getElementById(id)]));

  const state = {
    socket: null,
    reconnectTimer: null,
    stopped: false,
    connected: false,
    primaryReady: false,
    pullRequest: null,
    queue: [],
    tabs: new Map(),
    actions: new Map(),
    conversations: new Map(),
    approvals: new Map(),
    drafts: new Map(),
    pendingMessage: null,
    activeSessionId: null,
    openingPath: null,
    seq: 0,
    round: 1,
    renderedDiffSessionId: null,
    renderedDiffValue: null,
    renderedConversationSessionId: null,
    renderedMessageCount: 0,
    renderedMessageRevisions: [],
    conversationContainers: null
  };

  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined && text !== null) node.textContent = String(text);
    return node;
  }

  function clear(node) {
    while (node.firstChild) node.removeChild(node.firstChild);
  }

  function toast(message, kind) {
    const node = el("div", `toast${kind ? ` ${kind}` : ""}`, message);
    elements.toast_region.append(node);
    window.setTimeout(() => node.remove(), 5200);
  }

  function normalizeStatus(value) {
    return String(value || "current").replaceAll("-", "_");
  }

  function statusLabel(value) {
    return normalizeStatus(value).replaceAll("_", " ");
  }

  function parseJson(value) {
    if (typeof value !== "string") return value;
    try { return JSON.parse(value); } catch (_) { return null; }
  }

  function conversationFor(sessionId) {
    if (!state.conversations.has(sessionId)) state.conversations.set(sessionId, []);
    return state.conversations.get(sessionId);
  }

  function activeTab() {
    return state.activeSessionId ? state.tabs.get(state.activeSessionId) || null : null;
  }

  function saveActiveDraft() {
    if (!state.activeSessionId || state.pendingMessage?.sessionId === state.activeSessionId) return;
    state.drafts.set(state.activeSessionId, elements.message_input.value);
  }

  function loadActiveDraft() {
    elements.message_input.value = state.activeSessionId ? state.drafts.get(state.activeSessionId) || "" : "";
  }

  function activateSession(sessionId) {
    if (sessionId === state.activeSessionId) return;
    saveActiveDraft();
    state.activeSessionId = sessionId;
    loadActiveDraft();
  }

  function applySnapshot(snapshot) {
    if (!snapshot || snapshot.schema !== "synoptic-bootstrap/v1") throw new Error("Unsupported Synoptic bootstrap schema");
    state.pullRequest = snapshot.pullRequest || null;
    state.primaryReady = Boolean(snapshot.primaryReady);
    state.queue = Array.isArray(snapshot.queue) ? snapshot.queue : [];
    state.round = Number(snapshot.round || 1);
    state.seq = Math.max(state.seq, Number(snapshot.seq || 0));
    state.approvals.clear();

    const nextTabs = new Map();
    for (const tab of Array.isArray(snapshot.tabs) ? snapshot.tabs : []) {
      const sessionId = tab.sessionId || tab.id;
      const previous = state.tabs.get(sessionId);
      nextTabs.set(sessionId, Object.assign({}, previous, tab, {
        sessionId,
        staleOrigin: previous?.staleOrigin || normalizeStatus(tab.status) === "stale_origin",
        completed: previous?.completed || normalizeStatus(tab.status) === "completed",
        turnActive: tab.turnActive === undefined ? Boolean(previous?.turnActive) : Boolean(tab.turnActive),
        turnFailed: tab.turnFailed === undefined ? Boolean(previous?.turnFailed) : Boolean(tab.turnFailed)
      }));
      conversationFor(sessionId);
    }
    state.tabs = nextTabs;
    state.openingPath = null;

    state.actions.clear();
    for (const card of Array.isArray(snapshot.actions) ? snapshot.actions : []) state.actions.set(card.id, card);
    if (state.activeSessionId && !state.tabs.has(state.activeSessionId)) activateSession(null);
    if (!state.activeSessionId && state.tabs.size) activateSession(Array.from(state.tabs.keys()).at(-1));
    reconcilePendingAfterSnapshot();
    render();
  }

  async function bootstrap() {
    if (!token) throw new Error("The launch token is missing. Open the exact URL returned by `synoptic launch`.");
    const response = await fetch(`/api/bootstrap?token=${encodeURIComponent(token)}`, { cache: "no-store" });
    if (!response.ok) throw new Error(`Bootstrap failed (${response.status})`);
    applySnapshot(await response.json());
    connect();
  }

  function connect() {
    if (state.stopped) return;
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const socket = new WebSocket(`${protocol}//${window.location.host}/ws?token=${encodeURIComponent(token)}`);
    state.socket = socket;
    socket.addEventListener("open", () => {
      state.connected = true;
      send("snapshot.get", {});
      renderHeader();
    });
    socket.addEventListener("message", (event) => {
      let envelope;
      try { envelope = JSON.parse(event.data); } catch (_) {
        toast("Synoptic sent an invalid browser event.", "error");
        return;
      }
      handleEnvelope(envelope);
    });
    socket.addEventListener("close", () => {
      state.connected = false;
      markPendingOutcomeUnknown();
      state.approvals.clear();
      state.openingPath = null;
      renderHeader();
      if (!state.stopped) {
        toast("Connection lost. Reconnecting…");
        window.clearTimeout(state.reconnectTimer);
        state.reconnectTimer = window.setTimeout(connect, 900);
      }
    });
    socket.addEventListener("error", () => socket.close());
  }

  function send(type, payload, requestId) {
    if (!state.socket || state.socket.readyState !== WebSocket.OPEN) {
      toast("Synoptic is reconnecting; try again in a moment.", "error");
      return false;
    }
    const envelope = { schema: UI_SCHEMA, type, payload };
    if (requestId) envelope.requestId = requestId;
    state.socket.send(JSON.stringify(envelope));
    return true;
  }

  function handleEnvelope(envelope) {
    if (!envelope || envelope.schema !== UI_SCHEMA || typeof envelope.type !== "string") return;
    const seq = Number(envelope.seq || 0);
    if (envelope.type !== "snapshot" && seq && seq <= state.seq) return;
    state.seq = Math.max(state.seq, seq);
    const payload = envelope.payload || {};

    switch (envelope.type) {
      case "snapshot":
        applySnapshot(payload);
        return;
      case "primary.status":
        if (payload.status === "completed" || payload.status === "ready") state.primaryReady = true;
        if (payload.status === "failed") toast("Common review context failed. Refresh to retry.", "error");
        break;
      case "queue.updated":
        if (Array.isArray(payload.queue)) state.queue = payload.queue;
        else if (Array.isArray(payload)) state.queue = payload;
        break;
      case "session.opened":
        onSessionOpened(payload);
        break;
      case "session.closed":
        onSessionClosed(payload);
        break;
      case "session.status":
        onSessionStatus(payload);
        break;
      case "session.item.started":
      case "session.item.delta":
      case "session.item.completed":
        onVisibleItem(payload);
        break;
      case "session.file_changed":
        markSessionStale(payload.sessionId);
        break;
      case "action.prepared":
        state.actions.set(payload.id, payload);
        ensureActiveSession(payload.sessionId);
        break;
      case "action.superseded":
        updateAction(payload.id, { status: "superseded" });
        break;
      case "action.status":
        updateAction(payload.id, payload);
        if (["succeeded", "failed", "outcome-unknown", "invalidated"].includes(payload.status)) send("snapshot.get", {});
        break;
      case "approval.requested":
        state.approvals.set(payload.approvalId, payload);
        if (!payload.sessionId) toast("The background context session needs command approval.");
        break;
      case "approval.resolved":
        state.approvals.delete(payload.approvalId);
        break;
      case "file.completed":
        if (payload.sessionId) updateTab(payload.sessionId, {
          status: "completed",
          completed: true,
          turnActive: false,
          turnFailed: false
        });
        send("snapshot.get", {});
        break;
      case "file.excluded":
        toast(payload.syncError ? `${payload.path}: exclusion sync failed` : `${payload.path}: excluded as ${payload.reason}`, payload.syncError ? "error" : undefined);
        send("snapshot.get", {});
        break;
      case "pr.refreshed":
        toast("Pull request refreshed.");
        send("snapshot.get", {});
        break;
      case "round.finished":
        state.round = Number(payload.round || state.round + 1);
        toast(`Round ${state.round} is ready.`);
        send("snapshot.get", {});
        break;
      case "warning":
        toast(payload.message || payload.code || "Synoptic warning", "error");
        break;
      case "error":
        toast(payload.message || payload.code || "Synoptic command failed", "error");
        if (payload.requestId && payload.requestId === state.pendingMessage?.id) restorePendingMessage();
        state.openingPath = null;
        break;
      case "app.stopped":
        state.stopped = true;
        toast("Synoptic stopped.");
        break;
      default:
        break;
    }
    render();
  }

  function onSessionOpened(payload) {
    const sessionId = payload.sessionId;
    if (!sessionId) return;
    const previous = state.tabs.get(sessionId) || {};
    state.tabs.set(sessionId, Object.assign(previous, {
      id: sessionId,
      sessionId,
      path: payload.path,
      revisionKey: payload.revisionKey,
      status: previous.status || "current",
      staleOrigin: previous.staleOrigin || normalizeStatus(previous.status) === "stale_origin",
      completed: previous.completed || normalizeStatus(previous.status) === "completed",
      turnActive: previous.turnActive || Boolean(payload.initialReview),
      turnFailed: false,
      reused: Boolean(payload.reused),
      initialReview: Boolean(payload.initialReview),
      diff: payload.diff || previous.diff || { state: "unavailable", text: null }
    }));
    activateSession(sessionId);
    state.openingPath = null;
    const messages = conversationFor(sessionId);
    if (!messages.length) messages.push({ kind: "system", text: payload.initialReview ? "Initial review started. Findings will appear here." : "Session opened. Send a message when you are ready to begin." });
  }

  function onSessionClosed(payload) {
    const sessionId = payload.sessionId || state.activeSessionId;
    if (!sessionId) return;
    if (state.activeSessionId === sessionId) saveActiveDraft();
    state.tabs.delete(sessionId);
    state.drafts.delete(sessionId);
    if (state.activeSessionId === sessionId) {
      state.activeSessionId = null;
      activateSession(state.tabs.size ? Array.from(state.tabs.keys()).at(-1) : null);
    }
  }

  function onSessionStatus(payload) {
    const sessionId = payload.sessionId;
    if (!sessionId) return;
    const tab = state.tabs.get(sessionId);
    const status = payload.status || "current";
    if (status === "turn-started") acceptPendingMessage(sessionId);
    updateTab(sessionId, {
      status: status === "turn-started" || status === "interrupted" ? tab?.status || "current" : normalizeStatus(status),
      staleOrigin: tab?.staleOrigin || normalizeStatus(status) === "stale_origin",
      completed: tab?.completed || normalizeStatus(status) === "completed",
      turnActive: status === "turn-started" ? true : Boolean(tab?.turnActive),
      turnFailed: status === "turn-started" ? false : Boolean(tab?.turnFailed)
    });
  }

  function onVisibleItem(payload) {
    const sessionId = payload.sessionId;
    const method = payload.method || "item";
    const raw = parseJson(payload.raw) || payload.raw || {};
    if (!sessionId) {
      if (method === "approval.requested" && raw.approvalId) state.approvals.set(raw.approvalId, raw);
      return;
    }
    ensureActiveSession(sessionId);
    if (method === "session.file_changed") {
      markSessionStale(sessionId);
      send("snapshot.get", {});
      return;
    }
    if (method === "approval.requested" && raw.approvalId) {
      state.approvals.set(raw.approvalId, raw);
      return;
    }
    if (method === "approval.resolved") {
      state.approvals.delete(raw.approvalId);
      return;
    }

    if (method === "turn/started") {
      updateTab(sessionId, { turnActive: true, turnFailed: false });
      return;
    }

    const messages = conversationFor(sessionId);
    const delta = visibleDelta(method, raw);
    if (delta !== null) {
      const last = messages.at(-1);
      if (last && last.kind === "assistant" && last.streaming) {
        last.text += delta;
        last.revision = Number(last.revision || 0) + 1;
      }
      else messages.push({ kind: "assistant", text: delta, streaming: true });
      updateTab(sessionId, { turnActive: true, turnFailed: false });
      return;
    }

    if (method.includes("turn/completed") || method === "turn/completed") {
      const last = messages.at(-1);
      if (last && last.kind === "assistant") {
        last.streaming = false;
        last.revision = Number(last.revision || 0) + 1;
      }
      const terminalStatus = raw?.params?.turn?.status || raw?.turn?.status || "completed";
      if (terminalStatus === "failed") {
        messages.push({ kind: "warning", text: readableEvent(method, raw) });
        updateTab(sessionId, { turnActive: false, turnFailed: true });
      } else {
        updateTab(sessionId, { turnActive: false, turnFailed: false });
      }
      return;
    }
    if (method.includes("turn/failed") || method.includes("error")) {
      messages.push({ kind: "warning", text: readableEvent(method, raw) });
      updateTab(sessionId, { turnActive: false, turnFailed: true });
      return;
    }

    const detail = readableEvent(method, raw);
    if (detail) {
      const eventKey = detailEventKey(method, raw);
      const prior = messages.findLast(
        (message) => message.kind === "detail" && message.eventKey === eventKey
      );
      if (method.toLowerCase().includes("delta") && prior) {
        prior.text += detail;
        prior.revision = Number(prior.revision || 0) + 1;
      } else {
        messages.push({ kind: "detail", title: detailTitle(method, raw), text: detail, eventKey });
      }
    }
  }

  function visibleDelta(method, raw) {
    const params = raw && raw.params ? raw.params : raw;
    if (!["item/agentMessage/delta", "item/agent_message/delta"].includes(method)) return null;
    const candidates = [params?.delta, params?.text, params?.content, params?.item?.delta, params?.item?.text];
    for (const value of candidates) if (typeof value === "string") return value;
    return null;
  }

  function readableEvent(method, raw) {
    const params = raw && raw.params ? raw.params : raw;
    const item = params?.item || params;
    if (item?.type === "commandExecution" || item?.type === "command_execution") {
      return [item.command, item.aggregatedOutput || item.output, item.exitCode !== undefined ? `exit ${item.exitCode}` : null].filter(Boolean).join("\n\n");
    }
    if (typeof item?.summary === "string") return item.summary;
    if (typeof params?.message === "string") return params.message;
    if (typeof raw === "string") return raw;
    try { return JSON.stringify(raw, null, 2); } catch (_) { return String(raw || method); }
  }

  function detailTitle(method, raw) {
    const params = raw && raw.params ? raw.params : raw;
    const item = params?.item || params;
    if (item?.type === "commandExecution" || item?.type === "command_execution") return "Command";
    if (method.toLowerCase().includes("reason")) return "Reasoning summary";
    if (method.toLowerCase().includes("tool")) return "Tool activity";
    return method.replaceAll("/", " · ");
  }

  function detailEventKey(method, raw) {
    const params = raw && raw.params ? raw.params : raw;
    const item = params?.item || params;
    return [method, item?.id, params?.itemId, params?.turnId].filter(Boolean).join(":");
  }

  function updateTab(sessionId, patch) {
    const current = state.tabs.get(sessionId);
    if (current) state.tabs.set(sessionId, Object.assign({}, current, patch));
  }

  function updateAction(id, patch) {
    const current = state.actions.get(id);
    if (current) state.actions.set(id, Object.assign({}, current, patch));
  }

  function markSessionStale(sessionId) {
    if (sessionId) updateTab(sessionId, { status: "stale_origin", staleOrigin: true });
    toast("A reviewed file changed and returned to the queue.");
  }

  function tabStatus(tab) {
    if (tab?.turnFailed) return "turn_failed";
    if (tab?.turnActive) return "turn_active";
    if (tab?.staleOrigin) return "stale_origin";
    if (tab?.completed) return "completed";
    return normalizeStatus(tab?.status);
  }

  function acceptPendingMessage(sessionId) {
    const pending = state.pendingMessage;
    if (!pending || pending.sessionId !== sessionId) return;
    conversationFor(sessionId).push({ kind: "user", text: pending.text });
    state.pendingMessage = null;
  }

  function restorePendingMessage() {
    const pending = state.pendingMessage;
    if (!pending) return;
    state.drafts.set(pending.sessionId, pending.text);
    state.pendingMessage = null;
    if (state.activeSessionId === pending.sessionId) loadActiveDraft();
  }

  function markPendingOutcomeUnknown() {
    if (state.pendingMessage) state.pendingMessage.outcomeUnknown = true;
  }

  function reconcilePendingAfterSnapshot() {
    const pending = state.pendingMessage;
    if (!pending?.outcomeUnknown) return;
    conversationFor(pending.sessionId).push({
      kind: "warning",
      text: `Delivery outcome is unknown after reconnect. Check the conversation before resending:\n\n${pending.text}`
    });
    state.pendingMessage = null;
  }

  function ensureActiveSession(sessionId) {
    if (!state.activeSessionId && state.tabs.has(sessionId)) state.activeSessionId = sessionId;
  }

  function render() {
    elements.app.setAttribute("aria-busy", "false");
    renderHeader();
    renderQueue();
    renderTabs();
    renderReview();
    renderGlobalApprovals();
  }

  function renderHeader() {
    elements.round_label.textContent = `Round ${state.round}`;
    clear(elements.pr_summary);
    if (!state.pullRequest) {
      elements.pr_summary.append(el("span", "pr-meta", state.connected ? "Resolving pull request…" : "Connecting…"));
    } else {
      const pr = state.pullRequest;
      const link = el("a", "", `${pr.repository}#${pr.number} · ${pr.title}`);
      link.href = pr.url;
      link.target = "_blank";
      link.rel = "noreferrer";
      elements.pr_summary.append(link);
      elements.pr_summary.append(el("span", "branch-chip", `${pr.baseRefName} ← ${pr.headRefName}`));
      if (pr.isDraft) elements.pr_summary.append(el("span", "status-pill", "draft"));
    }
    elements.refresh_button.disabled = !state.connected;
    elements.finish_button.disabled = !state.connected;
    elements.stop_button.disabled = !state.connected;
  }

  function renderQueue() {
    elements.primary_gate.classList.toggle("hidden", state.primaryReady);
    elements.queue_count.textContent = String(state.queue.length);
    clear(elements.queue);
    for (const file of state.queue) {
      const row = el("button", "queue-row");
      row.type = "button";
      row.setAttribute("role", "listitem");
      row.disabled = !state.primaryReady || state.openingPath === file.path;
      if (activeTab()?.path === file.path) row.classList.add("active");
      row.append(el("span", "queue-path", file.path));
      const delta = el("span", "queue-delta");
      delta.append(el("span", "addition", `+${file.additions || 0}`));
      delta.append(el("span", "deletion", `−${file.deletions || 0}`));
      row.append(delta);
      const subline = el("span", "queue-subline");
      subline.append(el("span", `dot${file.activeSessionId ? " live" : ""}`));
      subline.append(document.createTextNode(`${file.changeType || "changed"} · ${statusLabel(file.viewedState || "unviewed")}`));
      if (file.exclusionSyncError) subline.append(el("span", "sync-error", "exclusion sync failed"));
      else if (file.activeSessionId) subline.append(el("span", "", "session open"));
      row.append(subline);
      row.addEventListener("click", () => openFile(file));
      elements.queue.append(row);
    }
    elements.queue_empty.classList.toggle("hidden", !state.primaryReady || state.queue.length > 0);
  }

  function openFile(file) {
    if (file.activeSessionId && state.tabs.has(file.activeSessionId)) {
      activateSession(file.activeSessionId);
      render();
      return;
    }
    state.openingPath = file.path;
    renderQueue();
    if (!send("file.open", { path: file.path })) state.openingPath = null;
  }

  function renderTabs() {
    clear(elements.tabs);
    for (const tab of state.tabs.values()) {
      const button = el("button", "tab");
      button.type = "button";
      button.setAttribute("role", "tab");
      button.setAttribute("aria-selected", String(tab.sessionId === state.activeSessionId));
      const normalized = tabStatus(tab);
      button.append(el("span", `tab-state ${normalized}`));
      const suffix = tab.staleOrigin || normalized === "stale_origin" ? " · prior revision" : "";
      button.append(el("span", "tab-label", `${tab.path}${suffix}`));
      button.addEventListener("click", () => { activateSession(tab.sessionId); render(); });
      elements.tabs.append(button);
    }
  }

  function renderReview() {
    const tab = activeTab();
    elements.welcome.classList.toggle("hidden", Boolean(tab));
    elements.review.classList.toggle("hidden", !tab);
    if (!tab) {
      state.renderedDiffSessionId = null;
      state.renderedDiffValue = null;
      state.renderedConversationSessionId = null;
      state.conversationContainers = null;
      return;
    }
    elements.diff_title.textContent = tab.path;
    const normalized = tabStatus(tab);
    elements.diff_state.className = `status-pill ${normalized}`;
    elements.diff_state.textContent = tab.diff?.state === "text" ? "current diff" : tab.diff?.state || "unavailable";
    elements.stale_banner.classList.toggle(
      "hidden",
      !tab.staleOrigin && normalized !== "stale_origin"
    );
    elements.conversation_title.textContent = tab.path;
    elements.session_status.className = `status-pill ${normalized}`;
    elements.session_status.textContent = statusLabel(normalized);
    elements.interrupt_button.disabled = !state.connected || normalized !== "turn_active";
    elements.close_button.disabled = !state.connected;
    elements.message_input.disabled = !state.connected || Boolean(state.pendingMessage);
    renderDiff(tab.diff, tab.sessionId);
    renderConversation(tab.sessionId);
  }

  function renderDiff(diff, sessionId) {
    if (state.renderedDiffSessionId === sessionId && state.renderedDiffValue === diff) return;
    state.renderedDiffSessionId = sessionId;
    state.renderedDiffValue = diff;
    clear(elements.diff);
    if (!diff || diff.state === "unavailable") {
      elements.diff.append(el("div", "diff-message", "The current pull-request diff is unavailable. Refresh to revalidate the file."));
      return;
    }
    if (diff.state === "binary") {
      elements.diff.append(el("div", "diff-message", "Git reports this as a binary or non-text change."));
      return;
    }
    const table = el("table", "diff-table");
    const body = document.createElement("tbody");
    let oldLine = null;
    let newLine = null;
    let inHunk = false;
    const diffText = String(diff.text || "");
    const lines = diffText.split("\n");
    if (diffText.endsWith("\n") && lines.at(-1) === "") lines.pop();
    for (const line of lines) {
      let kind = "context";
      let prefix = line.slice(0, 1);
      if (line.startsWith("@@")) {
        kind = "hunk";
        inHunk = true;
        const match = line.match(/^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@/);
        oldLine = match ? Number(match[1]) : null;
        newLine = match ? Number(match[2]) : null;
      } else if (line === "\\ No newline at end of file") kind = "meta";
      else if (line.startsWith("diff --git")) {
        kind = "meta";
        inHunk = false;
      } else if (!inHunk) kind = "meta";
      else if (line.startsWith("+")) kind = "added";
      else if (inHunk && line.startsWith("-")) kind = "removed";
      const row = el("tr", `diff-row ${kind}`);
      const oldCell = el("td", "line-number");
      const newCell = el("td", "line-number new");
      if (kind === "context") { oldCell.textContent = oldLine ?? ""; newCell.textContent = newLine ?? ""; if (oldLine !== null) oldLine += 1; if (newLine !== null) newLine += 1; }
      if (kind === "added") { newCell.textContent = newLine ?? ""; if (newLine !== null) newLine += 1; }
      if (kind === "removed") { oldCell.textContent = oldLine ?? ""; if (oldLine !== null) oldLine += 1; }
      const code = el("td", "diff-code");
      if (["added", "removed", "context"].includes(kind)) {
        code.append(el("span", "diff-prefix", prefix || " "));
        code.append(document.createTextNode(line.slice(1)));
      } else code.textContent = line;
      row.append(oldCell, newCell, code);
      body.append(row);
    }
    table.append(body);
    elements.diff.append(table);
  }

  function renderConversation(sessionId) {
    const messages = conversationFor(sessionId);
    if (!messages.length) messages.push({ kind: "system", text: "This running session was restored from the current Synoptic process. New visible items will appear here." });
    if (state.renderedConversationSessionId !== sessionId || !state.conversationContainers) {
      clear(elements.conversation);
      state.conversationContainers = {
        messages: el("div", "conversation-messages"),
        approvals: el("div", "conversation-approvals"),
        actions: el("div", "conversation-actions")
      };
      elements.conversation.append(
        state.conversationContainers.messages,
        state.conversationContainers.approvals,
        state.conversationContainers.actions
      );
      state.renderedConversationSessionId = sessionId;
      state.renderedMessageCount = 0;
      state.renderedMessageRevisions = [];
    }
    const containers = state.conversationContainers;
    if (state.renderedMessageCount > messages.length) {
      clear(containers.messages);
      state.renderedMessageCount = 0;
      state.renderedMessageRevisions = [];
    }
    for (let index = 0; index < state.renderedMessageCount; index += 1) {
      const revision = Number(messages[index].revision || 0);
      if (state.renderedMessageRevisions[index] !== revision) {
        containers.messages.children[index].replaceWith(renderMessage(messages[index]));
        state.renderedMessageRevisions[index] = revision;
      }
    }
    for (let index = state.renderedMessageCount; index < messages.length; index += 1) {
      containers.messages.append(renderMessage(messages[index]));
      state.renderedMessageRevisions[index] = Number(messages[index].revision || 0);
    }
    state.renderedMessageCount = messages.length;
    clear(containers.approvals);
    clear(containers.actions);
    for (const approval of state.approvals.values()) {
      if (approval.sessionId === sessionId) containers.approvals.append(renderApproval(approval));
    }
    for (const card of state.actions.values()) {
      if (card.sessionId === sessionId) containers.actions.append(renderAction(card));
    }
    elements.conversation.scrollTop = elements.conversation.scrollHeight;
  }

  function renderMessage(message) {
    if (message.kind === "detail") {
      const details = el("details", "detail-item");
      details.append(el("summary", "", message.title));
      details.append(el("pre", "", message.text));
      return details;
    }
    const node = el("article", `message ${message.kind}`);
    const author = message.kind === "assistant" ? "Codex" : message.kind === "user" ? "You" : message.kind === "warning" ? "Warning" : "Synoptic";
    node.append(el("div", "message-head", author));
    node.append(el("div", "message-body", message.text));
    return node;
  }

  function renderAction(card) {
    const node = el("article", `action-card ${normalizeStatus(card.status)}`);
    const top = el("div", "action-top");
    const copy = el("div");
    copy.append(el("div", "action-kind", `${card.kind} · ${statusLabel(card.status)}`));
    copy.append(el("div", "action-summary", card.effectSummary));
    top.append(copy);
    node.append(top);
    const target = card.target || {};
    const targetParts = [`${target.repository || ""}#${target.pullRequest || ""}`];
    if (target.path) targetParts.push(target.path);
    if (target.startLine) targetParts.push(`lines ${target.startLine}–${target.line}${target.side ? ` ${target.side}` : ""}`);
    else if (target.line) targetParts.push(`line ${target.line}${target.side ? ` ${target.side}` : ""}`);
    if (target.threadId) targetParts.push(`thread ${target.threadId}`);
    if (target.commentId) targetParts.push(`comment ${target.commentId}`);
    node.append(el("div", "action-target", targetParts.filter(Boolean).join(" · ")));
    if (card.body) node.append(el("div", "action-body", card.body));
    if (card.graphql) {
      const details = el("details", "detail-item");
      details.append(el("summary", "", `GraphQL · ${card.graphql.operationName}`));
      details.append(el("pre", "", `${card.graphql.document}\n\n${JSON.stringify(card.graphql.variables, null, 2)}`));
      node.append(details);
    }
    if (card.status === "pending") {
      const controls = el("div", "action-controls");
      const reject = el("button", "button reject", "Reject");
      reject.type = "button";
      reject.addEventListener("click", () => send("action.reject", { cardId: card.id }));
      const confirm = el("button", "button confirm", "Confirm action");
      confirm.type = "button";
      confirm.addEventListener("click", () => send("action.confirm", { cardId: card.id }));
      controls.append(reject, confirm);
      node.append(controls);
    }
    return node;
  }

  function renderApproval(approval) {
    const node = el("article", "approval-card");
    node.append(el("div", "action-kind", approval.ownerKind === "primary" ? "Background command approval" : "Command approval"));
    node.append(el("div", "action-summary", approval.method || "Codex approval request"));
    node.append(el("div", "action-body", readableEvent(approval.method || "approval", approval.request || {})));
    const controls = el("div", "action-controls");
    for (const decision of Array.isArray(approval.decisions) ? approval.decisions : []) {
      const label = typeof decision === "string" ? decision : decision?.decision || decision?.type || "respond";
      const button = el("button", `button ${String(label).toLowerCase().includes("decline") ? "reject" : ""}`, label);
      button.type = "button";
      button.addEventListener("click", () => {
        const payload = { approvalId: approval.approvalId, decision };
        if (approval.sessionId) payload.sessionId = approval.sessionId;
        send("approval.resolve", payload);
      });
      controls.append(button);
    }
    node.append(controls);
    return node;
  }

  function renderGlobalApprovals() {
    clear(elements.global_approvals);
    for (const approval of state.approvals.values()) {
      if (!approval.sessionId) elements.global_approvals.append(renderApproval(approval));
    }
    elements.global_approvals.classList.toggle("hidden", !elements.global_approvals.children.length);
  }

  elements.refresh_button.addEventListener("click", () => {
    elements.refresh_button.disabled = true;
    send("pr.refresh", {});
  });
  elements.finish_button.addEventListener("click", () => {
    elements.finish_button.disabled = true;
    send("round.finish", {});
  });
  elements.stop_button.addEventListener("click", () => {
    if (window.confirm("Stop this Synoptic workspace? Unpublished conversations and pending cards are disposable.")) send("app.stop", {});
  });
  elements.interrupt_button.addEventListener("click", () => {
    if (state.activeSessionId) send("session.interrupt", { sessionId: state.activeSessionId });
  });
  elements.close_button.addEventListener("click", () => {
    if (state.activeSessionId) send("session.close", { sessionId: state.activeSessionId });
  });
  elements.message_form.addEventListener("submit", (event) => {
    event.preventDefault();
    const sessionId = state.activeSessionId;
    const text = elements.message_input.value.trim();
    if (!sessionId || !text) return;
    const tab = state.tabs.get(sessionId);
    const active = Boolean(tab?.turnActive);
    const requestId = window.crypto.randomUUID();
    const sent = !state.pendingMessage && send(
      "session.message",
      { sessionId, text, active },
      requestId
    );
    if (sent) {
      state.pendingMessage = { id: requestId, sessionId, text, outcomeUnknown: false };
      state.drafts.delete(sessionId);
      elements.message_input.value = "";
      renderReview();
    }
  });
  elements.message_input.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      elements.message_form.requestSubmit();
    }
  });
  elements.message_input.addEventListener("input", saveActiveDraft);

  bootstrap().catch((error) => {
    elements.app.setAttribute("aria-busy", "false");
    toast(error.message || String(error), "error");
    clear(elements.pr_summary);
    elements.pr_summary.append(el("span", "pr-meta", "Unable to start Synoptic"));
  });
}());
