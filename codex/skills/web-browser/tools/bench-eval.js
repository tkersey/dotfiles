#!/usr/bin/env node

import { spawnSync } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

function percentile(sorted, p) {
  if (sorted.length === 0) return NaN;
  if (sorted.length === 1) return sorted[0];
  const k = (sorted.length - 1) * (p / 100);
  const f = Math.floor(k);
  const c = Math.ceil(k);
  if (f === c) return sorted[f];
  return sorted[f] + (sorted[c] - sorted[f]) * (k - f);
}

function parseIntArg(value, name, fallback) {
  if (value == null) return fallback;
  const n = Number.parseInt(value, 10);
  if (!Number.isFinite(n) || n <= 0) {
    console.error(`✗ Invalid value for ${name}: ${value}`);
    process.exit(1);
  }
  return n;
}

function parseFloatArg(value, name, fallback) {
  if (value == null) return fallback;
  const n = Number.parseFloat(value);
  if (!Number.isFinite(n) || n <= 0) {
    console.error(`✗ Invalid value for ${name}: ${value}`);
    process.exit(1);
  }
  return n;
}

const args = process.argv.slice(2);

let warmup = 5;
let samples = 40;
let expression = "1+1";
let budgetP95Ms = null;

for (let i = 0; i < args.length; i++) {
  const arg = args[i];
  if (arg === "--warmup") {
    warmup = parseIntArg(args[++i], "--warmup", warmup);
  } else if (arg.startsWith("--warmup=")) {
    warmup = parseIntArg(arg.slice("--warmup=".length), "--warmup", warmup);
  } else if (arg === "--samples") {
    samples = parseIntArg(args[++i], "--samples", samples);
  } else if (arg.startsWith("--samples=")) {
    samples = parseIntArg(arg.slice("--samples=".length), "--samples", samples);
  } else if (arg === "--expr") {
    expression = args[++i] ?? expression;
  } else if (arg.startsWith("--expr=")) {
    expression = arg.slice("--expr=".length);
  } else if (arg === "--budget-p95-ms") {
    budgetP95Ms = parseFloatArg(args[++i], "--budget-p95-ms", budgetP95Ms);
  } else if (arg.startsWith("--budget-p95-ms=")) {
    budgetP95Ms = parseFloatArg(
      arg.slice("--budget-p95-ms=".length),
      "--budget-p95-ms",
      budgetP95Ms,
    );
  } else if (arg === "-h" || arg === "--help") {
    console.log(
      "Usage: bench-eval.js [--warmup N] [--samples N] [--expr JS] [--budget-p95-ms N]",
    );
    process.exit(0);
  } else {
    console.error(`✗ Unknown option: ${arg}`);
    process.exit(1);
  }
}

const evalScript = join(dirname(fileURLToPath(import.meta.url)), "eval.js");

const durationsMs = [];
for (let i = 0; i < warmup + samples; i++) {
  const t0 = process.hrtime.bigint();
  const res = spawnSync(evalScript, [expression], { encoding: "utf8" });
  const durationMs = Number(process.hrtime.bigint() - t0) / 1e6;
  if (res.status !== 0) {
    process.stderr.write(res.stderr ?? "");
    process.stdout.write(res.stdout ?? "");
    process.exit(res.status ?? 1);
  }
  if (i >= warmup) durationsMs.push(durationMs);
}

durationsMs.sort((a, b) => a - b);
const min = durationsMs[0];
const p50 = percentile(durationsMs, 50);
const p95 = percentile(durationsMs, 95);
const p99 = percentile(durationsMs, 99);
const max = durationsMs[durationsMs.length - 1];

console.log(`samples: ${durationsMs.length} (warmup ${warmup})`);
console.log(`min/p50/p95/p99/max ms: ${min.toFixed(3)} / ${p50.toFixed(3)} / ${p95.toFixed(3)} / ${p99.toFixed(3)} / ${max.toFixed(3)}`);

if (budgetP95Ms != null) {
  if (p95 > budgetP95Ms) {
    console.error(`✗ p95 ${p95.toFixed(3)} ms exceeds budget ${budgetP95Ms.toFixed(3)} ms`);
    process.exit(1);
  }
  console.log(`✓ p95 budget met: ${p95.toFixed(3)} <= ${budgetP95Ms.toFixed(3)} ms`);
}
