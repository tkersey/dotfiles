#!/usr/bin/env node

import puppeteer from "puppeteer-core";

const DEFAULT_PORT = 9222;
async function getActivePage(browser) {
  const targets = browser.targets();
  for (let i = targets.length - 1; i >= 0; i--) {
    if (targets[i].type() !== "page") continue;
    const page = await targets[i].page();
    if (page) return page;
  }
  return null;
}

function tryParsePort(value) {
  const port = Number.parseInt(String(value), 10);
  if (!Number.isFinite(port) || port <= 0 || port > 65535) return null;
  return port;
}

function printHelp(exitCode = 0) {
  console.log("Usage: pick.js [--port N] [--browser-url URL] [--] 'message'");
  console.log("\nOptions:");
  console.log(`  --port N           CDP port (default: ${DEFAULT_PORT})`);
  console.log("  --browser-url URL  CDP URL (overrides --port)");
  console.log("  -h, --help         Show help");
  console.log("\nEnv:");
  console.log("  CODEX_BROWSER_URL          CDP URL (used when no CLI port/url)");
  console.log("  CODEX_BROWSER_PORT         CDP port (alias: CODEX_CDP_PORT)");
  console.log("\nExample:");
  console.log('  pick.js "Click the submit button"');

  process.exit(exitCode);
}

const args = process.argv.slice(2);

let portFromCli;
let browserUrlFromCli;
let messageParts = [];

let parsingOptions = true;
for (let i = 0; i < args.length; i++) {
  const arg = args[i];

  if (parsingOptions && (arg === "-h" || arg === "--help")) {
    printHelp(0);
  } else if (parsingOptions && arg === "--") {
    parsingOptions = false;
  } else if (parsingOptions && arg === "--port") {
    portFromCli = tryParsePort(args[++i]);
    if (!portFromCli) {
      console.error(`✗ Invalid port: ${args[i]}`);
      printHelp(1);
    }
  } else if (parsingOptions && arg.startsWith("--port=")) {
    portFromCli = tryParsePort(arg.slice("--port=".length));
    if (!portFromCli) {
      console.error(`✗ Invalid port: ${arg.slice("--port=".length)}`);
      printHelp(1);
    }
  } else if (parsingOptions && arg === "--browser-url") {
    browserUrlFromCli = args[++i];
    if (!browserUrlFromCli) {
      console.error("✗ Missing value for --browser-url");
      printHelp(1);
    }
  } else if (parsingOptions && arg.startsWith("--browser-url=")) {
    browserUrlFromCli = arg.slice("--browser-url=".length);
  } else if (parsingOptions && arg.startsWith("--")) {
    console.error(`✗ Unknown option: ${arg}`);
    printHelp(1);
  } else {
    messageParts = args.slice(i);
    break;
  }
}

const message = messageParts.join(" ");
if (!message) {
  printHelp(1);
}

const envBrowserURL = process.env["CODEX_BROWSER_URL"] ?? null;
const envPort = tryParsePort(
  process.env["CODEX_BROWSER_PORT"] ?? process.env["CODEX_CDP_PORT"] ?? "",
);

const resolvedPort = portFromCli ?? envPort ?? DEFAULT_PORT;
const browserURL =
  browserUrlFromCli ??
  (portFromCli
    ? `http://localhost:${resolvedPort}`
    : envBrowserURL ?? `http://localhost:${resolvedPort}`);

let browser;
try {
  browser = await puppeteer.connect({
    browserURL,
    defaultViewport: null,
    targetFilter: (target) => {
      const type = target.type();
      return type === "browser" || type === "tab" || type === "page";
    },
  });
} catch (e) {
  console.error("✗ Failed to connect to Chrome via CDP");
  console.error(`  URL: ${browserURL}`);
  console.error("  Start Chrome via: ./tools/start.js");
  console.error(e);
  process.exit(1);
}

const page = await getActivePage(browser);

if (!page) {
  console.error("✗ No active tab found");
  console.error("  Open one via: ./tools/nav.js https://example.com --new");
  process.exit(1);
}

// Inject pick() helper into current page
await page.evaluate(() => {
  if (!window.pick) {
    window.pick = async (message) => {
      if (!message) {
        throw new Error("pick() requires a message parameter");
      }
      return new Promise((resolve) => {
        const selections = [];
        const selectedElements = new Set();

        const overlay = document.createElement("div");
        overlay.style.cssText =
          "position:fixed;top:0;left:0;width:100%;height:100%;z-index:2147483647;pointer-events:none";

        const highlight = document.createElement("div");
        highlight.style.cssText =
          "position:absolute;border:2px solid #3b82f6;background:rgba(59,130,246,0.1);transition:all 0.1s";
        overlay.appendChild(highlight);

        const banner = document.createElement("div");
        banner.style.cssText =
          "position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:#1f2937;color:white;padding:12px 24px;border-radius:8px;font:14px sans-serif;box-shadow:0 4px 12px rgba(0,0,0,0.3);pointer-events:auto;z-index:2147483647";

        const updateBanner = () => {
          banner.textContent = `${message} (${selections.length} selected, Cmd/Ctrl+click to add, Enter to finish, ESC to cancel)`;
        };
        updateBanner();

        document.body.append(banner, overlay);

        const cleanup = () => {
          document.removeEventListener("mousemove", onMove, true);
          document.removeEventListener("click", onClick, true);
          document.removeEventListener("keydown", onKey, true);
          overlay.remove();
          banner.remove();
          selectedElements.forEach((el) => {
            el.style.outline = "";
          });
        };

        const onMove = (e) => {
          const el = document.elementFromPoint(e.clientX, e.clientY);
          if (!el || overlay.contains(el) || banner.contains(el)) return;
          const r = el.getBoundingClientRect();
          highlight.style.cssText = `position:absolute;border:2px solid #3b82f6;background:rgba(59,130,246,0.1);top:${r.top}px;left:${r.left}px;width:${r.width}px;height:${r.height}px`;
        };

        const buildElementInfo = (el) => {
          const parents = [];
          let current = el.parentElement;
          while (current && current !== document.body) {
            const parentInfo = current.tagName.toLowerCase();
            const id = current.id ? `#${current.id}` : "";
            const cls = current.className
              ? `.${current.className.trim().split(/\s+/).join(".")}`
              : "";
            parents.push(parentInfo + id + cls);
            current = current.parentElement;
          }

          return {
            tag: el.tagName.toLowerCase(),
            id: el.id || null,
            class: el.className || null,
            text: el.textContent?.trim().slice(0, 200) || null,
            html: el.outerHTML.slice(0, 500),
            parents: parents.join(" > "),
          };
        };

        const onClick = (e) => {
          if (banner.contains(e.target)) return;
          e.preventDefault();
          e.stopPropagation();
          const el = document.elementFromPoint(e.clientX, e.clientY);
          if (!el || overlay.contains(el) || banner.contains(el)) return;

          if (e.metaKey || e.ctrlKey) {
            if (!selectedElements.has(el)) {
              selectedElements.add(el);
              el.style.outline = "3px solid #10b981";
              selections.push(buildElementInfo(el));
              updateBanner();
            }
          } else {
            cleanup();
            const info = buildElementInfo(el);
            resolve(selections.length > 0 ? selections : info);
          }
        };

        const onKey = (e) => {
          if (e.key === "Escape") {
            e.preventDefault();
            cleanup();
            resolve(null);
          } else if (e.key === "Enter" && selections.length > 0) {
            e.preventDefault();
            cleanup();
            resolve(selections);
          }
        };

        document.addEventListener("mousemove", onMove, true);
        document.addEventListener("click", onClick, true);
        document.addEventListener("keydown", onKey, true);
      });
    };
  }
});

const result = await page.evaluate((msg) => window.pick(msg), message);

if (Array.isArray(result)) {
  for (let i = 0; i < result.length; i++) {
    if (i > 0) console.log("");
    for (const [key, value] of Object.entries(result[i])) {
      console.log(`${key}: ${value}`);
    }
  }
} else if (typeof result === "object" && result !== null) {
  for (const [key, value] of Object.entries(result)) {
    console.log(`${key}: ${value}`);
  }
} else {
  console.log(result);
}

await browser.disconnect();
