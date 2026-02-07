#!/usr/bin/env node

import { execFileSync, spawn } from "node:child_process";
import { existsSync } from "node:fs";
import { mkdir } from "node:fs/promises";
import { homedir } from "node:os";
import { basename, delimiter, join } from "node:path";
import process from "node:process";

const DEFAULT_PORT = 9222;
const DEFAULT_USER_DATA_DIR = join(homedir(), ".cache", "scraping");
const DEFAULT_MACOS_CHROME_PATH =
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const CONNECT_TIMEOUT_MS = 400;
const CONNECT_RETRY_INTERVAL_MS = 250;
const CONNECT_RETRY_ATTEMPTS = 60;

function printHelp(exitCode = 0) {
  const chromePathEnv =
    process.env["CODEX_CHROME_PATH"] ??
    process.env["CHROME_PATH"] ??
    process.env["PUPPETEER_EXECUTABLE_PATH"] ??
    "";
  const portEnv =
    process.env["CODEX_BROWSER_PORT"] ?? process.env["CODEX_CDP_PORT"] ?? "";
  const browserUrlEnv = process.env["CODEX_BROWSER_URL"] ?? "";
  const userDataDirEnv = process.env["CODEX_BROWSER_USER_DATA_DIR"] ?? "";

  console.log(
    "Usage: start.js [--profile] [--port N] [--user-data-dir DIR] [--chrome-path PATH] [--no-kill]",
  );
  console.log("\nOptions:");
  console.log("  --profile            Copy your default Chrome profile into user-data-dir");
  console.log(`  --port N             Remote debugging port (default: ${DEFAULT_PORT})`);
  console.log(
    `  --user-data-dir DIR  Chrome user data dir (default: ${DEFAULT_USER_DATA_DIR})`,
  );
  console.log("  --chrome-path PATH   Chrome/Chromium executable path");
  console.log("  --no-kill            Do not kill existing Chrome processes");
  console.log("  -h, --help           Show help");

  console.log("\nEnv (CLI overrides env):");
  console.log(`  CODEX_BROWSER_URL          CDP URL (connect tools; start.js only uses localhost)`);
  console.log(`  CODEX_BROWSER_PORT         CDP port (alias: CODEX_CDP_PORT)${portEnv ? ` (current: ${portEnv})` : ""}`);
  console.log(
    `  CODEX_BROWSER_USER_DATA_DIR  Chrome user data dir${userDataDirEnv ? ` (current: ${userDataDirEnv})` : ""}`,
  );
  console.log(
    `  CODEX_CHROME_PATH           Chrome path (aliases: CHROME_PATH, PUPPETEER_EXECUTABLE_PATH)${chromePathEnv ? ` (current: ${chromePathEnv})` : ""}`,
  );
  if (browserUrlEnv) {
    console.log(`  CODEX_BROWSER_URL          (current: ${browserUrlEnv})`);
  }

  console.log("\nExamples:");
  console.log("  start.js");
  console.log("  start.js --profile");
  console.log("  start.js --port 9223 --no-kill");
  console.log("  CODEX_CHROME_PATH=/usr/bin/google-chrome start.js --no-kill");

  process.exit(exitCode);
}

function parseArgValue(arg, name) {
  if (!arg) {
    console.error(`✗ Missing value for ${name}`);
    printHelp(1);
  }
  return arg;
}

function expandHome(pathname) {
  if (pathname === "~") return homedir();
  if (pathname.startsWith("~/")) return join(homedir(), pathname.slice(2));
  return pathname;
}

function tryParsePort(value) {
  const port = Number.parseInt(String(value), 10);
  if (!Number.isFinite(port) || port <= 0 || port > 65535) return null;
  return port;
}

function isLocalhostHostname(hostname) {
  return hostname === "localhost" || hostname === "127.0.0.1";
}

function resolvePortFromBrowserUrl(browserUrl) {
  if (!browserUrl) return null;
  try {
    const url = new URL(browserUrl);
    if (!isLocalhostHostname(url.hostname)) return null;
    return tryParsePort(url.port || DEFAULT_PORT);
  } catch {
    return null;
  }
}

function findExecutableInPath(candidates) {
  const pathValue = process.env.PATH;
  if (!pathValue) return null;

  const pathDirs = pathValue.split(delimiter);
  for (const dir of pathDirs) {
    for (const name of candidates) {
      const full = join(dir, name);
      if (existsSync(full)) return full;
    }
  }

  return null;
}

function resolveChromePath(cliValue) {
  const fromEnv =
    process.env["CODEX_CHROME_PATH"] ??
    process.env["CHROME_PATH"] ??
    process.env["PUPPETEER_EXECUTABLE_PATH"] ??
    null;

  const value = cliValue ?? fromEnv;
  if (value) return expandHome(value);

  if (process.platform === "darwin") return DEFAULT_MACOS_CHROME_PATH;

  if (process.platform === "linux") {
    return (
      findExecutableInPath([
        "google-chrome",
        "google-chrome-stable",
        "chromium-browser",
        "chromium",
      ]) ?? null
    );
  }

  return null;
}

function resolveProfileSourceDir() {
  const home = homedir();

  const candidates = [];
  if (process.platform === "darwin") {
    candidates.push(join(home, "Library", "Application Support", "Google", "Chrome"));
    candidates.push(join(home, "Library", "Application Support", "Chromium"));
  } else if (process.platform === "linux") {
    candidates.push(join(home, ".config", "google-chrome"));
    candidates.push(join(home, ".config", "google-chrome-beta"));
    candidates.push(join(home, ".config", "chromium"));
    candidates.push(join(home, ".config", "chromium-browser"));
  }

  return candidates.find((p) => existsSync(p)) ?? null;
}

async function canConnect(browserURL) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), CONNECT_TIMEOUT_MS);

  try {
    const probeUrl = new URL("/json/version", browserURL);
    const response = await fetch(probeUrl, {
      signal: controller.signal,
      cache: "no-store",
    });
    return response.ok;
  } catch {
    return false;
  } finally {
    clearTimeout(timeout);
  }
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

const args = process.argv.slice(2);

let useProfile = false;
let killExistingChrome = true;
let chromePath;
let userDataDir;
let port;

for (let i = 0; i < args.length; i++) {
  const arg = args[i];

  if (arg === "-h" || arg === "--help") {
    printHelp(0);
  } else if (arg === "--profile") {
    useProfile = true;
  } else if (arg === "--no-kill") {
    killExistingChrome = false;
  } else if (arg === "--kill") {
    killExistingChrome = true;
  } else if (arg === "--port") {
    port = tryParsePort(parseArgValue(args[++i], "--port"));
    if (!port) {
      console.error(`✗ Invalid port: ${args[i]}`);
      printHelp(1);
    }
  } else if (arg.startsWith("--port=")) {
    port = tryParsePort(arg.slice("--port=".length));
    if (!port) {
      console.error(`✗ Invalid port: ${arg.slice("--port=".length)}`);
      printHelp(1);
    }
  } else if (arg === "--user-data-dir") {
    userDataDir = expandHome(parseArgValue(args[++i], "--user-data-dir"));
  } else if (arg.startsWith("--user-data-dir=")) {
    userDataDir = expandHome(arg.slice("--user-data-dir=".length));
  } else if (arg === "--chrome-path") {
    chromePath = expandHome(parseArgValue(args[++i], "--chrome-path"));
  } else if (arg.startsWith("--chrome-path=")) {
    chromePath = expandHome(arg.slice("--chrome-path=".length));
  } else {
    console.error(`✗ Unknown option: ${arg}`);
    printHelp(1);
  }
}

const envPort = tryParsePort(
  process.env["CODEX_BROWSER_PORT"] ?? process.env["CODEX_CDP_PORT"] ?? "",
);
const portFromLocalUrl = resolvePortFromBrowserUrl(process.env["CODEX_BROWSER_URL"]);

port ??= portFromLocalUrl ?? envPort ?? DEFAULT_PORT;
userDataDir ??= expandHome(
  process.env["CODEX_BROWSER_USER_DATA_DIR"] ?? DEFAULT_USER_DATA_DIR,
);
chromePath = resolveChromePath(chromePath);

if (!chromePath) {
  console.error("✗ Could not resolve a Chrome/Chromium executable path");
  console.error("  Provide --chrome-path or set CODEX_CHROME_PATH (or CHROME_PATH)");
  process.exit(1);
}

if (!existsSync(chromePath)) {
  console.error("✗ Chrome executable does not exist");
  console.error(`  Path: ${chromePath}`);
  console.error("  Provide --chrome-path or set CODEX_CHROME_PATH");
  process.exit(1);
}

const browserURL = `http://localhost:${port}`;

if (!killExistingChrome) {
  const alreadyRunning = await canConnect(browserURL);
  if (alreadyRunning) {
    if (useProfile) {
      console.error(
        "! Chrome already reachable; --profile ignored (choose a different --port if you need a fresh instance)",
      );
    }
    console.log(`✓ Chrome already reachable at ${browserURL}`);
    process.exit(0);
  }
}

if (killExistingChrome) {
  const killTargets = new Set(["Google Chrome", basename(chromePath)]);
  const killTargetList = Array.from(killTargets).join(", ");

  console.log(
    `• Killing existing Chrome processes (${killTargetList}; use --no-kill to skip)`,
  );

  for (const target of killTargets) {
    try {
      execFileSync("killall", [target], { stdio: "ignore" });
    } catch {
      // Best-effort. If killall isn't available or Chrome isn't running, continue.
    }
  }

  await sleep(1000);
}

await mkdir(userDataDir, { recursive: true });

if (useProfile) {
  const sourceDir = resolveProfileSourceDir();
  if (!sourceDir) {
    console.error("✗ Could not find a default Chrome/Chromium profile directory to copy");
    console.error("  Omit --profile or adapt start.js for your OS");
    process.exit(1);
  }

  console.log(`• Copying profile into user-data-dir via rsync`);
  console.log(`  Source: ${sourceDir}`);
  console.log(`  Dest:   ${userDataDir}`);

  try {
    execFileSync(
      "rsync",
      ["-a", "--delete", `${sourceDir}/`, `${userDataDir}/`],
      { stdio: "ignore" },
    );
  } catch (e) {
    console.error("✗ Failed to copy profile via rsync");
    console.error("  Ensure rsync is installed, or omit --profile");
    console.error(e);
    process.exit(1);
  }
}

console.log(`• Starting Chrome with CDP on ${browserURL}`);
console.log(`  Chrome: ${chromePath}`);
console.log(`  User data dir: ${userDataDir}`);

try {
  spawn(
    chromePath,
    [
      `--remote-debugging-port=${port}`,
      `--user-data-dir=${userDataDir}`,
      "--no-first-run",
      "--no-default-browser-check",
    ],
    { detached: true, stdio: "ignore" },
  ).unref();
} catch (e) {
  console.error("✗ Failed to spawn Chrome");
  console.error(`  Path: ${chromePath}`);
  console.error(e);
  process.exit(1);
}

let connected = false;
for (let i = 0; i < CONNECT_RETRY_ATTEMPTS; i++) {
  if (await canConnect(browserURL)) {
    connected = true;
    break;
  }
  await sleep(CONNECT_RETRY_INTERVAL_MS);
}

if (!connected) {
  console.error("✗ Failed to connect to Chrome via CDP");
  console.error(`  URL: ${browserURL}`);
  console.error("\nTroubleshooting:");
  console.error(`  - If the port is busy, pick a new one: start.js --port ${port + 1}`);
  console.error("  - If Chrome is already running, rerun with --no-kill or close it");
  console.error("  - If the Chrome path is wrong, set --chrome-path / CODEX_CHROME_PATH");
  console.error("  - Run start.js --help for all options");
  process.exit(1);
}

console.log(`✓ Chrome ready at ${browserURL}${useProfile ? " (profile copied)" : ""}`);
