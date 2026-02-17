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

const TIER_STRICTNESS = {
  surplus: 0,
  ahead: 1,
  on_track: 2,
  tight: 3,
  critical: 4,
};

function toEffectiveTier(tier) {
  return tier === "unknown" ? "on_track" : tier;
}

function tierStrictness(tier) {
  const effective = toEffectiveTier(tier);
  return Number.isInteger(TIER_STRICTNESS[effective]) ? TIER_STRICTNESS[effective] : TIER_STRICTNESS.on_track;
}

function evaluateWindow(window, kind, nowSec) {
  if (!isObject(window)) return null;

  const usedPercent = safeInt(window.usedPercent);
  const resetsAt = safeInt(window.resetsAt);
  const windowDurationMins = safeInt(window.windowDurationMins);

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
    kind,
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
    effectiveTier: toEffectiveTier(tierInfo.tier),
    strictness: tierStrictness(tierInfo.tier),
  };
}

function pickStricterWindow(primaryEval, secondaryEval, preferredKind) {
  if (!primaryEval && !secondaryEval) return null;
  if (!primaryEval) return secondaryEval;
  if (!secondaryEval) return primaryEval;

  if (primaryEval.strictness > secondaryEval.strictness) return primaryEval;
  if (secondaryEval.strictness > primaryEval.strictness) return secondaryEval;

  if (preferredKind === "primary") return primaryEval;
  if (preferredKind === "secondary") return secondaryEval;
  return primaryEval;
}

export function computeBudgetGovernor(rateLimitsResponse, opts = {}) {
  const nowSec = safeInt(opts.nowSec) ?? Math.floor(Date.now() / 1000);
  const { bucket, bucketKey, source } = pickBucket(rateLimitsResponse);
  const { kind } = pickWindow(bucket);

  const limitId = isObject(bucket) && typeof bucket.limitId === "string" ? bucket.limitId : null;
  const limitName = isObject(bucket) && typeof bucket.limitName === "string" ? bucket.limitName : null;
  const planType = isObject(bucket) && typeof bucket.planType === "string" ? bucket.planType : null;

  const primary = isObject(bucket) && isObject(bucket.primary) ? bucket.primary : null;
  const secondary = isObject(bucket) && isObject(bucket.secondary) ? bucket.secondary : null;
  const primaryEval = evaluateWindow(primary, "primary", nowSec);
  const secondaryEval = evaluateWindow(secondary, "secondary", nowSec);
  const selected = pickStricterWindow(primaryEval, secondaryEval, kind);

  return {
    ok: Boolean(bucket && selected),
    bucketSource: source,
    bucketKey,
    limitId,
    limitName,
    planType,
    windowKind: selected?.kind ?? null,
    nowSec,
    usedPercent: selected?.usedPercent ?? null,
    resetsAt: selected?.resetsAt ?? null,
    windowDurationMins: selected?.windowDurationMins ?? null,
    remainingMins: selected?.remainingMins ?? null,
    elapsedPercent: selected?.elapsedPercent ?? null,
    deltaPercent: selected?.deltaPercent ?? null,
    tier: selected?.tier ?? "unknown",
    tierReason: selected?.tierReason ?? "window_missing",
    pacingOk: selected?.pacingOk ?? false,
    pacingReason: selected?.pacingReason ?? "window_missing",
    effectiveTier: selected?.effectiveTier ?? "on_track",
    primary: primaryEval
      ? {
          usedPercent: primaryEval.usedPercent,
          resetsAt: primaryEval.resetsAt,
          windowDurationMins: primaryEval.windowDurationMins,
          remainingMins: primaryEval.remainingMins,
          elapsedPercent: primaryEval.elapsedPercent,
          deltaPercent: primaryEval.deltaPercent,
          tier: primaryEval.tier,
          tierReason: primaryEval.tierReason,
          pacingOk: primaryEval.pacingOk,
          pacingReason: primaryEval.pacingReason,
          effectiveTier: primaryEval.effectiveTier,
        }
      : null,
    secondary: secondaryEval
      ? {
          usedPercent: secondaryEval.usedPercent,
          resetsAt: secondaryEval.resetsAt,
          windowDurationMins: secondaryEval.windowDurationMins,
          remainingMins: secondaryEval.remainingMins,
          elapsedPercent: secondaryEval.elapsedPercent,
          deltaPercent: secondaryEval.deltaPercent,
          tier: secondaryEval.tier,
          tierReason: secondaryEval.tierReason,
          pacingOk: secondaryEval.pacingOk,
          pacingReason: secondaryEval.pacingReason,
          effectiveTier: secondaryEval.effectiveTier,
        }
      : null,
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
