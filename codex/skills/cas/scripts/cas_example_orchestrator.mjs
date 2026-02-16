#!/usr/bin/env node
// Example orchestration client using CasClient.
//
// This script is agent-friendly: it prints JSON to stdout and diagnostics to stderr.

import { CasClient } from "./cas_client.mjs";

function usage() {
  return [
    "cas_example_orchestrator.mjs",
    "",
    "Usage:",
    "  node scripts/cas_example_orchestrator.mjs --cwd DIR --list-threads [N]",
    "  node scripts/cas_example_orchestrator.mjs --cwd DIR --list-experimental-features [N]",
    "  node scripts/cas_example_orchestrator.mjs --cwd DIR --resume-thread THREAD_ID",
    "  node scripts/cas_example_orchestrator.mjs --cwd DIR --steer-turn THREAD_ID EXPECTED_TURN_ID TEXT",
    "  node scripts/cas_example_orchestrator.mjs --cwd DIR --read-thread THREAD_ID [--include-turns]",
    "  node scripts/cas_example_orchestrator.mjs --cwd DIR --compact-thread THREAD_ID",
    "  node scripts/cas_example_orchestrator.mjs --cwd DIR --prompt TEXT [--thread-id THREAD_ID] [--opt-out-notification-method METHOD...]",
    "",
    "Notes:",
    "  - --cwd controls where the app-server runs; cas state defaults to ~/.codex/cas/state/<workspace-hash>.json.",
    "  - --prompt requires a working login and (usually) network access.",
    "  - This example is v2-only and fails fast on unimplemented server requests.",
  ].join("\n");
}

function parseArgs(argv) {
  /** @type {{ cwd: string|null, listThreads: number|null, listExperimentalFeatures: number|null, resumeThread: string|null, steerTurn: { threadId: string, expectedTurnId: string, text: string } | null, readThread: string|null, compactThread: string|null, includeTurns: boolean, prompt: string|null, threadId: string|null, optOutNotificationMethods: string[] }} */
  const out = {
    cwd: null,
    listThreads: null,
    listExperimentalFeatures: null,
    resumeThread: null,
    steerTurn: null,
    readThread: null,
    compactThread: null,
    includeTurns: false,
    prompt: null,
    threadId: null,
    optOutNotificationMethods: [],
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
      out.cwd = take();
      continue;
    }
    if (a === "--list-threads") {
      const maybe = args[0];
      if (maybe && !maybe.startsWith("--")) {
        out.listThreads = Number(take());
      } else {
        out.listThreads = 10;
      }
      continue;
    }
    if (a === "--list-experimental-features") {
      const maybe = args[0];
      if (maybe && !maybe.startsWith("--")) {
        out.listExperimentalFeatures = Number(take());
      } else {
        out.listExperimentalFeatures = 25;
      }
      continue;
    }
    if (a === "--resume-thread") {
      out.resumeThread = take();
      continue;
    }
    if (a === "--steer-turn") {
      out.steerTurn = {
        threadId: take(),
        expectedTurnId: take(),
        text: take(),
      };
      continue;
    }
    if (a === "--read-thread") {
      out.readThread = take();
      continue;
    }
    if (a === "--compact-thread") {
      out.compactThread = take();
      continue;
    }
    if (a === "--include-turns") {
      out.includeTurns = true;
      continue;
    }
    if (a === "--prompt") {
      out.prompt = take();
      continue;
    }
    if (a === "--thread-id") {
      out.threadId = take();
      continue;
    }
    if (a === "--opt-out-notification-method") {
      out.optOutNotificationMethods.push(take());
      continue;
    }

    throw new Error(`Unknown arg: ${a}`);
  }

  return { ok: true, help: false, error: null, opts: out };
}

function writeJson(obj) {
  process.stdout.write(`${JSON.stringify(obj)}\n`);
}

function logErr(line) {
  process.stderr.write(`${line}\n`);
}

async function main() {
  const parsed = parseArgs(process.argv.slice(2));
  if (!parsed.ok) {
    if (parsed.help) {
      logErr(usage());
      return 0;
    }
    logErr(parsed.error ?? "invalid args");
    return 2;
  }

  const opts = parsed.opts;
  if (!opts.cwd) {
    logErr("Missing --cwd");
    logErr(usage());
    return 2;
  }

  const client = new CasClient({
    cwd: opts.cwd,
    optOutNotificationMethods: opts.optOutNotificationMethods,
  });

  // Print all proxy events to stderr for debugging.
  client.on("cas/error", (ev) => logErr(`cas/error: ${ev.message}`));
  client.on("proxyStderr", (line) => logErr(`proxy stderr: ${line}`));

  // Do not let server-initiated requests stall: always respond deterministically.
  client.on("cas/serverRequest", (ev) => {
    const method = typeof ev.method === "string" ? ev.method : "<unknown>";
    if (method === "item/tool/call") {
      // Example policy: do not implement tools here; just return a clear error.
      client.respond(ev.id, {
        result: {
          contentItems: [
            { type: "inputText", text: "Tool call not implemented by this example" },
          ],
          success: false,
        },
      });
      return;
    }

    if (method === "item/tool/requestUserInput") {
      client.respondError(ev.id, "requestUserInput not implemented by this example", {
        code: -32000,
        data: { method },
      });
      return;
    }

    if (method === "account/chatgptAuthTokens/refresh") {
      client.respondError(
        ev.id,
        "chatgptAuthTokens refresh not implemented by this example",
        {
          code: -32000,
          data: { method },
        },
      );
      return;
    }

    client.respondError(ev.id, `Unhandled server request: ${method}`, {
      code: -32601,
      data: { method },
    });
  });

  await client.start();

  if (opts.listThreads !== null) {
    const result = await client.request("thread/list", {
      cursor: null,
      limit: opts.listThreads,
    });
    writeJson({ method: "thread/list", result });
    await client.close();
    return 0;
  }

  if (opts.listExperimentalFeatures !== null) {
    const result = await client.listExperimentalFeatures({
      cursor: null,
      limit: opts.listExperimentalFeatures,
    });
    writeJson({ method: "experimentalFeature/list", result });
    await client.close();
    return 0;
  }

  if (opts.resumeThread) {
    const result = await client.resumeThread({
      threadId: opts.resumeThread,
    });
    writeJson({ method: "thread/resume", threadId: opts.resumeThread, result });
    await client.close();
    return 0;
  }

  if (opts.steerTurn) {
    const result = await client.steerTurn({
      threadId: opts.steerTurn.threadId,
      expectedTurnId: opts.steerTurn.expectedTurnId,
      input: [
        {
          type: "text",
          text: opts.steerTurn.text,
          text_elements: [],
        },
      ],
    });
    writeJson({
      method: "turn/steer",
      threadId: opts.steerTurn.threadId,
      expectedTurnId: opts.steerTurn.expectedTurnId,
      result,
    });
    await client.close();
    return 0;
  }

  if (opts.readThread) {
    const result = await client.request("thread/read", {
      threadId: opts.readThread,
      includeTurns: Boolean(opts.includeTurns),
    });
    writeJson({ method: "thread/read", result });
    await client.close();
    return 0;
  }

  if (opts.compactThread) {
    const result = await client.request("thread/compact/start", {
      threadId: opts.compactThread,
    });
    writeJson({ method: "thread/compact/start", threadId: opts.compactThread, result });
    // Compaction progress streams as standard turn/item notifications.
    await client.close();
    return 0;
  }

  if (opts.prompt) {
    const threadId =
      opts.threadId ??
      (
        /** @type {any} */
        (await client.startThread({ cwd: opts.cwd }))
      )?.thread?.id;

    if (!threadId) {
      throw new Error("Failed to obtain threadId");
    }

    const collected = await client.startTurnAndCollect({
      threadId,
      input: [
        {
          type: "text",
          text: opts.prompt,
          text_elements: [],
        },
      ],
    });

    writeJson({
      method: "turn/start",
      threadId,
      turnId: collected.turnId,
      status: collected.turn?.status ?? null,
      agentMessageText: collected.agentMessageText,
      items: collected.items,
    });
    await client.close();
    return 0;
  }

  logErr(
    "Nothing to do (specify --list-threads, --list-experimental-features, --resume-thread, --steer-turn, --read-thread, or --prompt)",
  );
  logErr(usage());
  await client.close();
  return 2;
}

main()
  .then((code) => {
    process.exitCode = code;
  })
  .catch((err) => {
    logErr(`Fatal: ${err instanceof Error ? err.stack ?? err.message : String(err)}`);
    process.exitCode = 1;
  });
