// Budget governor helpers for pacing orchestration against account rate limits.
//
// This is intentionally dependency-free and safe to import from headless runners.

function isObject(v) {
  return v !== null && typeof v === "object" && !Array.isArray(v);
}

function clamp(n, lo, hi) {
  if (!Number.isFinite(n)) return lo;
  if (n < lo) return lo;
  if (n > hi) return hi;
  return n;
}

function safeInt(v) {
  if (v === null || v === undefined) return null;
  const n = Number(v);
  return Number.isInteger(n) ? n : null;
}

function pickBucket(resp) {
  if (!isObject(resp)) return { bucket: null, bucketKey: null, source: "invalid" };

  const byId = isObject(resp.rateLimitsByLimitId) ? resp.rateLimitsByLimitId : null;
  if (byId) {
    if (isObject(byId.codex)) {
      return { bucket: byId.codex, bucketKey: "codex", source: "by_limit_id" };
    }

    const keys = Object.keys(byId).filter((k) => isObject(byId[k]));
    if (keys.length === 1) {
      const k = keys[0];
      return { bucket: byId[k], bucketKey: k, source: "by_limit_id" };
    }
    if (keys.length > 1) {
      const preferred = keys.find((k) => {
        const lower = String(k).toLowerCase();
        return lower === "codex" || lower.includes("codex");
      });
      const k = preferred ?? keys[0];
      return { bucket: byId[k], bucketKey: k, source: "by_limit_id" };
    }
  }

  if (isObject(resp.rateLimits)) {
    return { bucket: resp.rateLimits, bucketKey: null, source: "single_bucket" };
  }

  return { bucket: null, bucketKey: null, source: "missing" };
}

function pickWindow(bucket) {
  if (!isObject(bucket)) return { window: null, kind: null };

  const primary = isObject(bucket.primary) ? bucket.primary : null;
  const secondary = isObject(bucket.secondary) ? bucket.secondary : null;

  if (primary && secondary) {
    const a = safeInt(primary.windowDurationMins);
    const b = safeInt(secondary.windowDurationMins);
    if (a !== null && b !== null) {
      return a >= b ? { window: primary, kind: "primary" } : { window: secondary, kind: "secondary" };
    }
    if (a !== null) return { window: primary, kind: "primary" };
    if (b !== null) return { window: secondary, kind: "secondary" };
    return { window: primary, kind: "primary" };
  }
  if (primary) return { window: primary, kind: "primary" };
  if (secondary) return { window: secondary, kind: "secondary" };
  return { window: null, kind: null };
}

function computeLinearPacing({ usedPercent, resetsAt, windowDurationMins, nowSec }) {
  const used = safeInt(usedPercent);
  const reset = safeInt(resetsAt);
  const dur = safeInt(windowDurationMins);
  const now = safeInt(nowSec);

  if (used === null || now === null || reset === null || dur === null || dur <= 0) {
    return {
      ok: false,
      usedPercent: used,
      elapsedPercent: null,
      deltaPercent: null,
      remainingMins: null,
      reason: "missing_fields",
    };
  }

  const windowSec = dur * 60;
  const startAt = reset - windowSec;
  const elapsedSec = now - startAt;
  const elapsedPercent = clamp((elapsedSec / windowSec) * 100, 0, 100);
  const remainingMins = Math.max(0, Math.ceil((reset - now) / 60));
  const deltaPercent = used - elapsedPercent;

  return {
    ok: true,
    usedPercent: used,
    elapsedPercent,
    deltaPercent,
    remainingMins,
    reason: "ok",
  };
}

function tierFromDelta({ usedPercent, elapsedPercent, deltaPercent }) {
  const used = safeInt(usedPercent);
  const elapsed = Number.isFinite(elapsedPercent) ? elapsedPercent : null;
  const delta = Number.isFinite(deltaPercent) ? deltaPercent : null;

  if (used === null) return { tier: "unknown", tierReason: "used_unknown" };
  if (used >= 95) return { tier: "critical", tierReason: "used_ge_95" };
  if (elapsed === null || delta === null) return { tier: "unknown", tierReason: "pacing_unknown" };

  if (delta <= -25) return { tier: "surplus", tierReason: "delta_le_-25" };
  if (delta <= -10) return { tier: "ahead", tierReason: "delta_le_-10" };
  if (delta < 10) return { tier: "on_track", tierReason: "delta_lt_10" };
  if (delta < 25) return { tier: "tight", tierReason: "delta_lt_25" };
  return { tier: "critical", tierReason: "delta_ge_25" };
}

export function computeBudgetGovernor(rateLimitsResponse, opts = {}) {
  const nowSec = safeInt(opts.nowSec) ?? Math.floor(Date.now() / 1000);
  const { bucket, bucketKey, source } = pickBucket(rateLimitsResponse);
  const { window, kind } = pickWindow(bucket);

  const limitId = isObject(bucket) && typeof bucket.limitId === "string" ? bucket.limitId : null;
  const limitName = isObject(bucket) && typeof bucket.limitName === "string" ? bucket.limitName : null;
  const planType = isObject(bucket) && typeof bucket.planType === "string" ? bucket.planType : null;

  const usedPercent = isObject(window) ? safeInt(window.usedPercent) : null;
  const resetsAt = isObject(window) ? safeInt(window.resetsAt) : null;
  const windowDurationMins = isObject(window) ? safeInt(window.windowDurationMins) : null;

  const pacing = computeLinearPacing({
    usedPercent,
    resetsAt,
    windowDurationMins,
    nowSec,
  });

  const tierInfo = tierFromDelta({
    usedPercent: pacing.usedPercent,
    elapsedPercent: pacing.elapsedPercent,
    deltaPercent: pacing.deltaPercent,
  });

  return {
    ok: Boolean(bucket && window),
    bucketSource: source,
    bucketKey,
    limitId,
    limitName,
    planType,
    windowKind: kind,
    nowSec,
    usedPercent: pacing.usedPercent,
    resetsAt,
    windowDurationMins,
    remainingMins: pacing.remainingMins,
    elapsedPercent: pacing.elapsedPercent,
    deltaPercent: pacing.deltaPercent,
    tier: tierInfo.tier,
    tierReason: tierInfo.tierReason,
    pacingOk: pacing.ok,
    pacingReason: pacing.reason,
  };
}

export function meshArgsForBudget({ mode, tier }) {
  const m = typeof mode === "string" ? mode : "aware";
  const t = typeof tier === "string" ? tier : "unknown";

  if (m === "all_out") {
    return { parallelTasks: "auto", maxTasks: "auto", chosenTier: t, decision: "all_out" };
  }

  const effectiveTier = t === "unknown" ? "on_track" : t;
  const decision = t === "unknown" ? "unknown->on_track" : "budget_aware";
  if (effectiveTier === "surplus" || effectiveTier === "ahead") {
    return {
      parallelTasks: "auto",
      maxTasks: "auto",
      chosenTier: effectiveTier,
      decision,
    };
  }

  if (effectiveTier === "on_track") {
    return { parallelTasks: 1, maxTasks: "auto", chosenTier: effectiveTier, decision };
  }

  // tight/critical
  return { parallelTasks: 1, maxTasks: 1, chosenTier: effectiveTier, decision };
}

export function effectiveWorkersForBudget({ mode, tier, maxWorkers }) {
  const m = typeof mode === "string" ? mode : "aware";
  const t = typeof tier === "string" ? tier : "unknown";
  const max = Number.isInteger(maxWorkers) && maxWorkers >= 0 ? maxWorkers : 0;

  if (m === "all_out") return max;

  const effectiveTier = t === "unknown" ? "on_track" : t;
  if (effectiveTier === "surplus" || effectiveTier === "ahead") return max;
  if (effectiveTier === "on_track") return Math.min(max, 1);
  return 0;
}
