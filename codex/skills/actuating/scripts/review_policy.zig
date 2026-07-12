const std = @import("std");

const MaxInputBytes = 4 * 1024 * 1024;
const MaxReferenceBytes = 4 * 1024 * 1024;
const MinimumStandardCleanRuns = 5;

const Phase = enum {
    preflight,
    closeout,

    fn parse(raw: []const u8) ?Phase {
        if (std.mem.eql(u8, raw, "preflight")) return .preflight;
        if (std.mem.eql(u8, raw, "closeout")) return .closeout;
        return null;
    }

    fn name(self: Phase) []const u8 {
        return @tagName(self);
    }
};

const Args = struct {
    phase: Phase,
    input_path: []const u8,
};

const Artifact = struct {
    repo: []const u8,
    base_ref: []const u8,
    base_sha: []const u8,
    head_sha: []const u8,
    state_fingerprint: []const u8,
};

const WorkflowBinding = struct {
    requestId: []const u8,
    requestFingerprint: []const u8,
};

const Attempt = struct {
    workflow_binding: WorkflowBinding,
    review_attempt_id: []const u8,
    review_thread_id: []const u8,
    review_turn_id: []const u8,
    base_sha: []const u8,
    head_sha: []const u8,
    target_fingerprint: []const u8,
    context_identity_matches: bool,
    principal_kind: []const u8,
    principal_reduced: bool,
    fallback_used: bool,
    principal_source: []const u8,
    verdict_status: []const u8,
    finding_count: usize,
    record_ref: []const u8,
};

const Request = struct {
    request_id: []const u8,
    request_fingerprint: ?[]const u8 = null,
    lens: []const u8,
    role: []const u8,
    selection_reason: []const u8,
    contract_id: ?[]const u8 = null,
    contract_ref: ?[]const u8 = null,
    contract_digest: ?[]const u8 = null,
    instructions_ref: ?[]const u8 = null,
    instruction_digest: ?[]const u8 = null,
    state: []const u8,
    not_required_reason: ?[]const u8 = null, // Legacy input retained only for explicit fail-closed rejection.
    attempts: []const Attempt,
    review_fold_refs: []const []const u8,
};

const Policy = struct {
    version: []const u8,
    policy_id: []const u8,
    run_id: []const u8,
    goal_contract_digest: []const u8,
    resolution_digest: ?[]const u8 = null,
    artifact: Artifact,
    standard_required_clean_runs: usize,
    required_lenses: []const []const u8,
    requests: []const Request,
    standard_clean_attempt_ids: []const []const u8,
    invalidation_reasons: []const []const u8,
};

const Envelope = struct {
    actuation_review_policy: Policy,
};

const Issues = struct {
    values: std.ArrayList([]const u8) = .empty,

    fn deinit(self: *Issues, allocator: std.mem.Allocator) void {
        self.values.deinit(allocator);
    }

    fn add(self: *Issues, allocator: std.mem.Allocator, issue: []const u8) !void {
        for (self.values.items) |existing| {
            if (std.mem.eql(u8, existing, issue)) return;
        }
        try self.values.append(allocator, issue);
    }

    fn sort(self: *Issues) void {
        std.mem.sort([]const u8, self.values.items, {}, lessString);
    }
};

pub fn main(init: std.process.Init) !void {
    const argv = try init.minimal.args.toSlice(init.arena.allocator());
    const code = runWithArgv(init.gpa, init.io, argv) catch |err| {
        var stderr_writer = std.Io.File.stderr().writer(init.io, &.{});
        try stderr_writer.interface.print("actuating review policy: {s}\n", .{@errorName(err)});
        return err;
    };
    if (code != 0) std.process.exit(code);
}

fn runWithArgv(allocator: std.mem.Allocator, io: std.Io, argv: []const []const u8) !u8 {
    if (argv.len == 2 and (std.mem.eql(u8, argv[1], "-h") or std.mem.eql(u8, argv[1], "--help"))) {
        try printHelp(io);
        return 0;
    }
    const args = try parseArgs(argv);
    const input = try readInputAlloc(allocator, io, args.input_path);
    defer allocator.free(input);

    var issues = Issues{};
    defer issues.deinit(allocator);

    var parsed = std.json.parseFromSlice(Envelope, allocator, input, .{
        .ignore_unknown_fields = false,
    }) catch {
        try issues.add(allocator, "malformed-or-schema-invalid-json");
        try emitDecision(allocator, io, args.phase, &issues);
        return 2;
    };
    defer parsed.deinit();

    try validatePolicy(allocator, io, parsed.value.actuation_review_policy, args.phase, true, &issues);
    try emitDecision(allocator, io, args.phase, &issues);
    return if (issues.values.items.len == 0) 0 else 2;
}

fn printHelp(io: std.Io) !void {
    var stdout_writer = std.Io.File.stdout().writer(io, &.{});
    try stdout_writer.interface.writeAll(
        \\actuating review policy
        \\
        \\usage: zig run codex/skills/actuating/scripts/review_policy.zig -- --phase {preflight|closeout} --input FILE|-
        \\
        \\Purely check one actuation-review-policy/v1 JSON snapshot. The decision grants no authority and mutates no storage.
        \\
    );
}

fn parseArgs(argv: []const []const u8) !Args {
    var phase: ?Phase = null;
    var input_path: ?[]const u8 = null;
    var i: usize = 1;
    while (i < argv.len) : (i += 1) {
        if (std.mem.eql(u8, argv[i], "--phase")) {
            i += 1;
            if (i >= argv.len) return error.MissingPhase;
            phase = Phase.parse(argv[i]) orelse return error.InvalidPhase;
            continue;
        }
        if (std.mem.eql(u8, argv[i], "--input")) {
            i += 1;
            if (i >= argv.len) return error.MissingInput;
            input_path = argv[i];
            continue;
        }
        return error.UnknownOption;
    }
    return .{
        .phase = phase orelse return error.MissingPhase,
        .input_path = input_path orelse return error.MissingInput,
    };
}

fn readInputAlloc(allocator: std.mem.Allocator, io: std.Io, path: []const u8) ![]u8 {
    if (std.mem.eql(u8, path, "-")) {
        var reader = std.Io.File.stdin().reader(io, &.{});
        return reader.interface.allocRemaining(allocator, .limited(MaxInputBytes));
    }
    return std.Io.Dir.cwd().readFileAlloc(io, path, allocator, .limited(MaxInputBytes));
}

fn emitDecision(allocator: std.mem.Allocator, io: std.Io, phase: Phase, issues: *Issues) !void {
    issues.sort();
    var out: std.Io.Writer.Allocating = .init(allocator);
    defer out.deinit();
    try out.writer.writeAll("{\"schema\":\"actuation-review-policy-decision/v1\",\"phase\":");
    try std.json.Stringify.value(phase.name(), .{}, &out.writer);
    try out.writer.writeAll(",\"verdict\":");
    try std.json.Stringify.value(if (issues.values.items.len == 0) "pass" else "blocked", .{}, &out.writer);
    try out.writer.writeAll(",\"errors\":");
    try std.json.Stringify.value(issues.values.items, .{}, &out.writer);
    try out.writer.writeAll(",\"authority_granted\":false,\"storage_mutated\":false}\n");
    const bytes = try out.toOwnedSlice();
    defer allocator.free(bytes);
    var stdout_writer = std.Io.File.stdout().writer(io, &.{});
    try stdout_writer.interface.writeAll(bytes);
}

fn validatePolicy(
    allocator: std.mem.Allocator,
    io: std.Io,
    policy: Policy,
    phase: Phase,
    verify_references: bool,
    issues: *Issues,
) !void {
    if (!std.mem.eql(u8, policy.version, "actuation-review-policy/v1")) try issues.add(allocator, "policy-version");
    for ([_][]const u8{ policy.policy_id, policy.run_id, policy.artifact.repo, policy.artifact.base_ref, policy.artifact.base_sha, policy.artifact.head_sha }) |value| {
        if (!isNonblank(value)) try issues.add(allocator, "required-policy-identity");
    }
    if (!isDigest(policy.goal_contract_digest)) try issues.add(allocator, "goal-contract-digest");
    if (policy.resolution_digest) |digest| if (!isDigest(digest)) try issues.add(allocator, "resolution-digest");
    if (!isDigest(policy.artifact.state_fingerprint)) try issues.add(allocator, "artifact-state-fingerprint");
    if (policy.standard_required_clean_runs < MinimumStandardCleanRuns) try issues.add(allocator, "standard-clean-runs-below-policy-minimum");
    if (policy.required_lenses.len == 0 or policy.requests.len == 0) try issues.add(allocator, "requests-required");
    if (policy.required_lenses.len != policy.requests.len) try issues.add(allocator, "registry-request-cardinality");

    var standard_index: ?usize = null;
    for (policy.required_lenses, 0..) |lens, index| {
        if (!isNonblank(lens)) try issues.add(allocator, "registry-lens-empty");
        if (containsString(policy.required_lenses[0..index], lens)) try issues.add(allocator, "registry-lens-duplicate");
        if (countRequestsWithLens(policy.requests, lens) != 1) try issues.add(allocator, "registry-request-coverage");
    }

    for (policy.requests, 0..) |request, request_index| {
        if (!isNonblank(request.request_id) or !isNonblank(request.lens) or !isNonblank(request.selection_reason)) {
            try issues.add(allocator, "request-identity");
        }
        if (containsRequestIdentity(policy.requests[0..request_index], request)) try issues.add(allocator, "request-identity-duplicate");
        if (!containsString(policy.required_lenses, request.lens)) try issues.add(allocator, "request-lens-not-registered");
        if (!stringIn(request.role, &.{ "standard", "auxiliary" })) try issues.add(allocator, "request-role");
        if (!stringIn(request.state, &.{ "selected-pending", "clean", "findings-folded", "candidate-pressure", "blocked", "rerun-required" })) {
            try issues.add(allocator, "request-state");
        }

        if (std.mem.eql(u8, request.role, "standard")) {
            if (standard_index != null) try issues.add(allocator, "multiple-standard-requests") else standard_index = request_index;
            if (std.mem.eql(u8, request.state, "not-required")) try issues.add(allocator, "standard-not-required");
        }

        if (std.mem.eql(u8, request.state, "not-required")) {
            if (std.mem.eql(u8, request.role, "auxiliary")) {
                try issues.add(allocator, "auxiliary-request-required");
            } else {
                try issues.add(allocator, "not-required-role");
            }
            if (hasBoundRequest(request) or request.attempts.len != 0 or request.review_fold_refs.len != 0) {
                try issues.add(allocator, "not-required-has-execution-evidence");
            }
        } else {
            if (optionalNonblank(request.not_required_reason)) try issues.add(allocator, "selected-request-has-not-required-reason");
            try validateBoundRequest(allocator, io, request, verify_references, issues);
        }

        for (request.attempts, 0..) |attempt, attempt_index| {
            try validateAttempt(allocator, policy, request, attempt, issues);
            if (attemptIdentitySeen(policy.requests, request_index, attempt_index, attempt.review_attempt_id)) {
                try issues.add(allocator, "review-attempt-duplicate");
            }
        }
    }
    if (standard_index == null) try issues.add(allocator, "standard-request-required");

    switch (phase) {
        .preflight => try validatePreflight(allocator, policy, issues),
        .closeout => if (standard_index) |index| try validateCloseout(allocator, policy, index, issues),
    }
}

fn validateBoundRequest(
    allocator: std.mem.Allocator,
    io: std.Io,
    request: Request,
    verify_references: bool,
    issues: *Issues,
) !void {
    const request_fingerprint = request.request_fingerprint orelse {
        try issues.add(allocator, "request-fingerprint-required");
        return;
    };
    const contract_id = request.contract_id orelse {
        try issues.add(allocator, "contract-id-required");
        return;
    };
    const contract_ref = request.contract_ref orelse {
        try issues.add(allocator, "contract-ref-required");
        return;
    };
    const contract_digest = request.contract_digest orelse {
        try issues.add(allocator, "contract-digest-required");
        return;
    };
    const instructions_ref = request.instructions_ref orelse {
        try issues.add(allocator, "instructions-ref-required");
        return;
    };
    const instruction_digest = request.instruction_digest orelse {
        try issues.add(allocator, "instruction-digest-required");
        return;
    };
    if (!isNonblank(contract_id) or !isNonblank(contract_ref) or !isNonblank(instructions_ref)) try issues.add(allocator, "bound-request-reference");
    if (!isDigest(request_fingerprint) or !isDigest(contract_digest) or !isDigest(instruction_digest)) try issues.add(allocator, "bound-request-digest");
    if (!std.mem.eql(u8, request_fingerprint, instruction_digest)) try issues.add(allocator, "request-instruction-digest-mismatch");
    if (!verify_references) return;
    try verifyReferenceDigest(allocator, io, contract_ref, contract_digest, "contract-ref-unreadable", "contract-digest-mismatch", issues);
    try verifyReferenceDigest(allocator, io, instructions_ref, instruction_digest, "instructions-ref-unreadable", "instruction-digest-mismatch", issues);
}

fn validateAttempt(allocator: std.mem.Allocator, policy: Policy, request: Request, attempt: Attempt, issues: *Issues) !void {
    const fingerprint = request.request_fingerprint orelse "";
    for ([_][]const u8{ attempt.review_attempt_id, attempt.review_thread_id, attempt.review_turn_id, attempt.principal_source, attempt.record_ref }) |value| {
        if (!isNonblank(value)) try issues.add(allocator, "attempt-identity");
    }
    if (!std.mem.eql(u8, attempt.workflow_binding.requestId, request.request_id) or
        !std.mem.eql(u8, attempt.workflow_binding.requestFingerprint, fingerprint))
    {
        try issues.add(allocator, "attempt-workflow-binding");
    }
    if (!std.mem.eql(u8, attempt.base_sha, policy.artifact.base_sha) or
        !std.mem.eql(u8, attempt.head_sha, policy.artifact.head_sha) or
        !std.mem.eql(u8, attempt.target_fingerprint, policy.artifact.state_fingerprint))
    {
        try issues.add(allocator, "attempt-artifact-binding");
    }
    if (!attempt.context_identity_matches) try issues.add(allocator, "attempt-context-identity");
    if (!std.mem.eql(u8, attempt.principal_kind, "strong") or attempt.principal_reduced or attempt.fallback_used) {
        try issues.add(allocator, "attempt-source-quality");
    }
    if (!stringIn(attempt.verdict_status, &.{ "clean", "findings" })) try issues.add(allocator, "attempt-verdict");
    if (std.mem.eql(u8, attempt.verdict_status, "clean") and attempt.finding_count != 0) try issues.add(allocator, "clean-has-findings");
    if (std.mem.eql(u8, attempt.verdict_status, "findings") and attempt.finding_count == 0) try issues.add(allocator, "findings-empty");
}

fn validatePreflight(allocator: std.mem.Allocator, policy: Policy, issues: *Issues) !void {
    if (policy.standard_clean_attempt_ids.len != 0) try issues.add(allocator, "preflight-standard-credit");
    if (policy.invalidation_reasons.len != 0) try issues.add(allocator, "preflight-invalidated");
    for (policy.requests) |request| {
        if (request.attempts.len != 0 or request.review_fold_refs.len != 0) try issues.add(allocator, "preflight-has-review-evidence");
        if (std.mem.eql(u8, request.role, "standard") and !std.mem.eql(u8, request.state, "selected-pending")) {
            try issues.add(allocator, "preflight-standard-state");
        }
        if (std.mem.eql(u8, request.role, "auxiliary") and !std.mem.eql(u8, request.state, "selected-pending")) {
            try issues.add(allocator, "preflight-auxiliary-state");
        }
    }
}

fn validateCloseout(allocator: std.mem.Allocator, policy: Policy, standard_index: usize, issues: *Issues) !void {
    if (policy.invalidation_reasons.len != 0) try issues.add(allocator, "closeout-invalidated");
    const standard = policy.requests[standard_index];
    if (!std.mem.eql(u8, standard.state, "clean")) try issues.add(allocator, "standard-not-clean");
    const required = policy.standard_required_clean_runs;
    if (standard.attempts.len < required) {
        try issues.add(allocator, "standard-clean-suffix-short");
    } else {
        const suffix = standard.attempts[standard.attempts.len - required ..];
        for (suffix) |attempt| if (!std.mem.eql(u8, attempt.verdict_status, "clean")) try issues.add(allocator, "standard-clean-suffix-broken");
        if (policy.standard_clean_attempt_ids.len != required) {
            try issues.add(allocator, "standard-clean-attempt-projection");
        } else {
            for (suffix, policy.standard_clean_attempt_ids) |attempt, projected| {
                if (!std.mem.eql(u8, attempt.review_attempt_id, projected)) try issues.add(allocator, "standard-clean-attempt-projection");
            }
        }
    }

    for (policy.requests) |request| {
        if (!std.mem.eql(u8, request.role, "auxiliary")) continue;
        if (request.attempts.len == 0) {
            try issues.add(allocator, "auxiliary-evidence-required");
            continue;
        }
        const latest = request.attempts[request.attempts.len - 1];
        if (std.mem.eql(u8, request.state, "clean")) {
            if (!std.mem.eql(u8, latest.verdict_status, "clean")) try issues.add(allocator, "auxiliary-clean-state");
        } else if (std.mem.eql(u8, request.state, "findings-folded")) {
            if (!std.mem.eql(u8, latest.verdict_status, "findings") or request.review_fold_refs.len == 0) {
                try issues.add(allocator, "auxiliary-findings-fold");
            }
        } else {
            try issues.add(allocator, "auxiliary-closeout-open");
        }
    }
}

fn verifyReferenceDigest(
    allocator: std.mem.Allocator,
    io: std.Io,
    path: []const u8,
    expected: []const u8,
    unreadable_issue: []const u8,
    mismatch_issue: []const u8,
    issues: *Issues,
) !void {
    const bytes = std.Io.Dir.cwd().readFileAlloc(io, path, allocator, .limited(MaxReferenceBytes)) catch {
        try issues.add(allocator, unreadable_issue);
        return;
    };
    defer allocator.free(bytes);
    var digest: [32]u8 = undefined;
    std.crypto.hash.sha2.Sha256.hash(bytes, &digest, .{});
    const hex = std.fmt.bytesToHex(digest, .lower);
    if (expected.len != "sha256:".len + hex.len or !std.mem.eql(u8, expected["sha256:".len..], &hex)) {
        try issues.add(allocator, mismatch_issue);
    }
}

fn hasBoundRequest(request: Request) bool {
    return request.request_fingerprint != null or request.contract_id != null or request.contract_ref != null or
        request.contract_digest != null or request.instructions_ref != null or request.instruction_digest != null;
}

fn optionalNonblank(value: ?[]const u8) bool {
    return if (value) |text| isNonblank(text) else false;
}

fn isNonblank(value: []const u8) bool {
    return std.mem.trim(u8, value, " \t\r\n").len != 0;
}

fn isDigest(value: []const u8) bool {
    if (value.len != 71 or !std.mem.startsWith(u8, value, "sha256:")) return false;
    for (value["sha256:".len..]) |byte| if (!std.ascii.isDigit(byte) and !(byte >= 'a' and byte <= 'f')) return false;
    return true;
}

fn stringIn(value: []const u8, expected: []const []const u8) bool {
    return containsString(expected, value);
}

fn containsString(values: []const []const u8, expected: []const u8) bool {
    for (values) |value| if (std.mem.eql(u8, value, expected)) return true;
    return false;
}

fn containsRequestIdentity(requests: []const Request, request: Request) bool {
    for (requests) |prior| {
        if (std.mem.eql(u8, prior.request_id, request.request_id) or std.mem.eql(u8, prior.lens, request.lens)) return true;
        if (prior.request_fingerprint != null and request.request_fingerprint != null and
            std.mem.eql(u8, prior.request_fingerprint.?, request.request_fingerprint.?)) return true;
    }
    return false;
}

fn countRequestsWithLens(requests: []const Request, lens: []const u8) usize {
    var count: usize = 0;
    for (requests) |request| if (std.mem.eql(u8, request.lens, lens)) {
        count += 1;
    };
    return count;
}

fn attemptIdentitySeen(requests: []const Request, request_index: usize, attempt_index: usize, attempt_id: []const u8) bool {
    for (requests, 0..) |request, candidate_request_index| {
        for (request.attempts, 0..) |attempt, candidate_attempt_index| {
            if (candidate_request_index > request_index or
                (candidate_request_index == request_index and candidate_attempt_index >= attempt_index)) return false;
            if (std.mem.eql(u8, attempt.review_attempt_id, attempt_id)) return true;
        }
    }
    return false;
}

fn lessString(_: void, lhs: []const u8, rhs: []const u8) bool {
    return std.mem.order(u8, lhs, rhs) == .lt;
}

const digest_a = "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
const digest_b = "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb";
const digest_c = "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc";
const digest_d = "sha256:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd";
const digest_e = "sha256:eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee";
const digest_f = "sha256:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff";

fn makeAttempt(id: []const u8, fingerprint: []const u8, verdict: []const u8, findings: usize) Attempt {
    return .{
        .workflow_binding = .{ .requestId = if (std.mem.eql(u8, fingerprint, digest_a)) "standard-request" else if (std.mem.eql(u8, fingerprint, digest_e)) "footgun-request" else if (std.mem.eql(u8, fingerprint, digest_c)) "invariant-request" else if (std.mem.eql(u8, fingerprint, digest_f)) "fresh-eyes-request" else "complexity-request", .requestFingerprint = fingerprint },
        .review_attempt_id = id,
        .review_thread_id = id,
        .review_turn_id = id,
        .base_sha = "base",
        .head_sha = "head",
        .target_fingerprint = digest_b,
        .context_identity_matches = true,
        .principal_kind = "strong",
        .principal_reduced = false,
        .fallback_used = false,
        .principal_source = "cas-lane",
        .verdict_status = verdict,
        .finding_count = findings,
        .record_ref = "cas:record",
    };
}

const standard_attempts = [_]Attempt{
    makeAttempt("standard-1", digest_a, "clean", 0),
    makeAttempt("standard-2", digest_a, "clean", 0),
    makeAttempt("standard-3", digest_a, "clean", 0),
    makeAttempt("standard-4", digest_a, "clean", 0),
    makeAttempt("standard-5", digest_a, "clean", 0),
};
const footgun_attempts = [_]Attempt{makeAttempt("footgun-1", digest_e, "clean", 0)};
const invariant_attempts = [_]Attempt{makeAttempt("invariant-1", digest_c, "clean", 0)};
const complexity_attempts = [_]Attempt{makeAttempt("complexity-1", digest_d, "findings", 1)};
const fresh_eyes_attempts = [_]Attempt{makeAttempt("fresh-eyes-1", digest_f, "clean", 0)};
const required_lenses = [_][]const u8{ "standard", "footgun-finder", "invariant-ace", "complexity-mitigator", "fresh-eyes" };
const standard_ids = [_][]const u8{ "standard-1", "standard-2", "standard-3", "standard-4", "standard-5" };
const fold_refs = [_][]const u8{"rf:complexity-1"};
const closeout_requests = [_]Request{
    .{ .request_id = "standard-request", .request_fingerprint = digest_a, .lens = "standard", .role = "standard", .selection_reason = "closure-grade", .contract_id = "standard-review-v1", .contract_ref = "/dev/null", .contract_digest = digest_a, .instructions_ref = "/dev/null", .instruction_digest = digest_a, .state = "clean", .attempts = &standard_attempts, .review_fold_refs = &.{} },
    .{ .request_id = "footgun-request", .request_fingerprint = digest_e, .lens = "footgun-finder", .role = "auxiliary", .selection_reason = "required auxiliary lane", .contract_id = "footgun-lens-v1", .contract_ref = "/dev/null", .contract_digest = digest_e, .instructions_ref = "/dev/null", .instruction_digest = digest_e, .state = "clean", .attempts = &footgun_attempts, .review_fold_refs = &.{} },
    .{ .request_id = "invariant-request", .request_fingerprint = digest_c, .lens = "invariant-ace", .role = "auxiliary", .selection_reason = "authority boundary changed", .contract_id = "invariant-gate-v1", .contract_ref = "/dev/null", .contract_digest = digest_c, .instructions_ref = "/dev/null", .instruction_digest = digest_c, .state = "clean", .attempts = &invariant_attempts, .review_fold_refs = &.{} },
    .{ .request_id = "complexity-request", .request_fingerprint = digest_d, .lens = "complexity-mitigator", .role = "auxiliary", .selection_reason = "cross-file state", .contract_id = "complexity-preflight-v1", .contract_ref = "/dev/null", .contract_digest = digest_d, .instructions_ref = "/dev/null", .instruction_digest = digest_d, .state = "findings-folded", .attempts = &complexity_attempts, .review_fold_refs = &fold_refs },
    .{ .request_id = "fresh-eyes-request", .request_fingerprint = digest_f, .lens = "fresh-eyes", .role = "auxiliary", .selection_reason = "required whole-target reinspection", .contract_id = "fresh-eyes-lens-v1", .contract_ref = "/dev/null", .contract_digest = digest_f, .instructions_ref = "/dev/null", .instruction_digest = digest_f, .state = "clean", .attempts = &fresh_eyes_attempts, .review_fold_refs = &.{} },
};

fn validCloseoutPolicy(requests: []const Request) Policy {
    return .{
        .version = "actuation-review-policy/v1",
        .policy_id = "policy-1",
        .run_id = "run-1",
        .goal_contract_digest = digest_a,
        .resolution_digest = digest_c,
        .artifact = .{ .repo = "/repo", .base_ref = "main", .base_sha = "base", .head_sha = "head", .state_fingerprint = digest_b },
        .standard_required_clean_runs = MinimumStandardCleanRuns,
        .required_lenses = &required_lenses,
        .requests = requests,
        .standard_clean_attempt_ids = &standard_ids,
        .invalidation_reasons = &.{},
    };
}

fn validateForTest(policy: Policy, phase: Phase) !Issues {
    var issues = Issues{};
    errdefer issues.deinit(std.testing.allocator);
    try validatePolicy(std.testing.allocator, std.testing.io, policy, phase, false, &issues);
    return issues;
}

fn hasIssue(issues: Issues, expected: []const u8) bool {
    return containsString(issues.values.items, expected);
}

test "closeout accepts generic registry coverage and disjoint lane accounting" {
    var issues = try validateForTest(validCloseoutPolicy(&closeout_requests), .closeout);
    defer issues.deinit(std.testing.allocator);
    try std.testing.expectEqual(@as(usize, 0), issues.values.items.len);
}

test "preflight accepts selected rows without review evidence" {
    var requests = closeout_requests;
    for (&requests) |*request| {
        request.state = "selected-pending";
        request.attempts = &.{};
        request.review_fold_refs = &.{};
    }
    var policy = validCloseoutPolicy(&requests);
    policy.standard_clean_attempt_ids = &.{};
    var issues = try validateForTest(policy, .preflight);
    defer issues.deinit(std.testing.allocator);
    try std.testing.expectEqual(@as(usize, 0), issues.values.items.len);
}

test "policy requires at least five standard clean runs" {
    var policy = validCloseoutPolicy(&closeout_requests);
    policy.standard_required_clean_runs = MinimumStandardCleanRuns - 1;
    var issues = try validateForTest(policy, .closeout);
    defer issues.deinit(std.testing.allocator);
    try std.testing.expect(hasIssue(issues, "standard-clean-runs-below-policy-minimum"));
}

test "every auxiliary lens is mandatory" {
    var requests = closeout_requests;
    requests[4].state = "not-required";
    var issues = try validateForTest(validCloseoutPolicy(&requests), .closeout);
    defer issues.deinit(std.testing.allocator);
    try std.testing.expect(hasIssue(issues, "request-state"));
    try std.testing.expect(hasIssue(issues, "auxiliary-request-required"));
}

test "duplicate attempts cannot manufacture a clean suffix" {
    var attempts = standard_attempts;
    attempts[1].review_attempt_id = attempts[0].review_attempt_id;
    var requests = closeout_requests;
    requests[0].attempts = &attempts;
    var issues = try validateForTest(validCloseoutPolicy(&requests), .closeout);
    defer issues.deinit(std.testing.allocator);
    try std.testing.expect(hasIssue(issues, "review-attempt-duplicate"));
}

test "stale tuple evidence cannot receive closeout credit" {
    var attempts = standard_attempts;
    attempts[2].head_sha = "stale-head";
    var requests = closeout_requests;
    requests[0].attempts = &attempts;
    var issues = try validateForTest(validCloseoutPolicy(&requests), .closeout);
    defer issues.deinit(std.testing.allocator);
    try std.testing.expect(hasIssue(issues, "attempt-artifact-binding"));
}

test "auxiliary attempt identity cannot count as standard credit" {
    var projected = standard_ids;
    projected[0] = "invariant-1";
    var policy = validCloseoutPolicy(&closeout_requests);
    policy.standard_clean_attempt_ids = &projected;
    var issues = try validateForTest(policy, .closeout);
    defer issues.deinit(std.testing.allocator);
    try std.testing.expect(hasIssue(issues, "standard-clean-attempt-projection"));
}

test "the declared registry and request rows must be bijective" {
    var requests = closeout_requests;
    requests[4].lens = "invariant-ace";
    var issues = try validateForTest(validCloseoutPolicy(&requests), .closeout);
    defer issues.deinit(std.testing.allocator);
    try std.testing.expect(hasIssue(issues, "registry-request-coverage"));
    try std.testing.expect(hasIssue(issues, "request-identity-duplicate"));
}

test "request identity is the exact instruction digest" {
    var requests = closeout_requests;
    requests[0].request_fingerprint = digest_b;
    var issues = try validateForTest(validCloseoutPolicy(&requests), .closeout);
    defer issues.deinit(std.testing.allocator);
    try std.testing.expect(hasIssue(issues, "request-instruction-digest-mismatch"));
}

test "sha256 comparison binds exact referenced bytes" {
    var issues = Issues{};
    defer issues.deinit(std.testing.allocator);
    const empty_digest = "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855";
    try verifyReferenceDigest(std.testing.allocator, std.testing.io, "/dev/null", empty_digest, "unreadable", "mismatch", &issues);
    try std.testing.expectEqual(@as(usize, 0), issues.values.items.len);
    try verifyReferenceDigest(std.testing.allocator, std.testing.io, "/dev/null", digest_a, "unreadable", "mismatch", &issues);
    try std.testing.expect(hasIssue(issues, "mismatch"));
}

test "fresh-eyes preserves its exact one-output instruction" {
    const allocator = std.testing.allocator;
    const fresh_eyes = try std.Io.Dir.cwd().readFileAlloc(std.testing.io, "codex/skills/fresh-eyes/SKILL.md", allocator, .limited(MaxInputBytes));
    defer allocator.free(fresh_eyes);
    const expected = "Once again, check over everything again with fresh eyes looking for any blunders, mistakes, errors, oversights, omissions, problems, misconceptions, bugs, etc. Be SUPER thorough and meticulous!\n";
    try std.testing.expect(std.mem.endsWith(u8, fresh_eyes, expected));
}

test "skill doctrine preserves the policy and transport owner split" {
    const allocator = std.testing.allocator;
    const actuating = try std.Io.Dir.cwd().readFileAlloc(std.testing.io, "codex/skills/actuating/SKILL.md", allocator, .limited(MaxInputBytes));
    defer allocator.free(actuating);
    const policy = try std.Io.Dir.cwd().readFileAlloc(std.testing.io, "codex/skills/actuating/references/review-policy.md", allocator, .limited(MaxInputBytes));
    defer allocator.free(policy);
    const goal_actuating = try std.Io.Dir.cwd().readFileAlloc(std.testing.io, "codex/skills/goal-actuating/SKILL.md", allocator, .limited(MaxInputBytes));
    defer allocator.free(goal_actuating);
    const cas = try std.Io.Dir.cwd().readFileAlloc(std.testing.io, "codex/skills/cas/SKILL.md", allocator, .limited(MaxInputBytes));
    defer allocator.free(cas);

    for ([_][]const u8{ "actuation-review-policy/v1", "review_policy.zig", "--phase preflight", "--phase closeout" }) |token| {
        try std.testing.expect(std.mem.indexOf(u8, actuating, token) != null or std.mem.indexOf(u8, policy, token) != null or std.mem.indexOf(u8, goal_actuating, token) != null);
    }
    for ([_][]const u8{ "footgun-finder", "invariant-ace", "complexity-mitigator", "fresh-eyes", "required_lenses", "standard_clean_attempt_ids", "at least five", "concurrently with the first standard attempt", "Auxiliary attempts never contribute" }) |token| {
        try std.testing.expect(std.mem.indexOf(u8, policy, token) != null);
    }
    for ([_][]const u8{ "selectedLenses", "reviewLane", "lensContract", "footgun-finder", "invariant-ace", "complexity-mitigator", "fresh-eyes", "clean-streak" }) |token| {
        try std.testing.expect(std.mem.indexOf(u8, cas, token) == null);
    }
}
