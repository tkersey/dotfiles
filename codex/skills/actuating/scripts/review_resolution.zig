const std = @import("std");

const MaxInputBytes = 4 * 1024 * 1024;

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

const Witness = struct {
    statement: []const u8,
    verifier: []const []const u8,
};

const OwnerRefinement = struct {
    kind: []const u8,
    construction: []const u8,
};

const ProgressWitness = struct {
    kind: []const u8,
    statement: []const u8,
    verifier: []const []const u8,
};

const CorrectnessRefinement = struct {
    class_ref: []const u8,
    discrepancy: []const u8,
    law_delta: []const u8,
    owner_refinement: OwnerRefinement,
    preservation_witness: Witness,
    progress_witness: ProgressWitness,
};

const Finding = struct {
    finding_id: []const u8,
    disposition: []const u8,
    quotient_key: []const u8,
    owner_boundary: []const u8,
};

const EquivalenceClass = struct {
    quotient_key: []const u8,
    finding_ids: []const []const u8,
    owner_boundary: []const u8,
    law_family: []const u8,
};

const Compression = struct {
    equivalence_classes: []const EquivalenceClass,
};

const ReviewFold = struct {
    version: []const u8,
    findings: []const Finding,
    compression: Compression,
};

const Decision = struct {
    decision_id: []const u8,
    owner_boundary: []const u8,
    finding_ids: []const []const u8,
    liability_classes: []const []const u8,
    strategy: []const u8,
    correctness_refinement: ?CorrectnessRefinement = null,
    blockers: []const []const u8,
};

const SemanticBalance = struct {
    uncovered_liabilities: []const []const u8,
    required_retirements: []const []const u8,
    completed_retirements: []const []const u8,
    dominated_remaining: []const []const u8,
};

const Outcome = struct {
    status: []const u8,
    semantic_balance: SemanticBalance,
};

const Resolution = struct {
    version: []const u8,
    resolution_id: []const u8,
    run_id: []const u8,
    review_folds: []const ReviewFold,
    finding_ids: []const []const u8,
    decisions: []const Decision,
    outcome: Outcome,
};

const Envelope = struct {
    review_resolution: Resolution,
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
        try stderr_writer.interface.print("actuating review resolution: {s}\n", .{@errorName(err)});
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
        .ignore_unknown_fields = true,
    }) catch {
        try issues.add(allocator, "malformed-or-schema-invalid-json");
        try emitDecision(allocator, io, args.phase, &issues);
        return 2;
    };
    defer parsed.deinit();

    try validateResolution(allocator, parsed.value.review_resolution, args.phase, &issues);
    try emitDecision(allocator, io, args.phase, &issues);
    return if (issues.values.items.len == 0) 0 else 2;
}

fn printHelp(io: std.Io) !void {
    var stdout_writer = std.Io.File.stdout().writer(io, &.{});
    try stdout_writer.interface.writeAll(
        \\actuating review resolution
        \\
        \\usage: zig run codex/skills/actuating/scripts/review_resolution.zig -- --phase {preflight|closeout} --input FILE|-
        \\
        \\Purely check the structural correctness-refinement sub-contract in one review-resolution/v1 JSON snapshot. Verifiers are not executed; the decision grants no authority and mutates no storage.
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
    try out.writer.writeAll("{\"schema\":\"actuating-review-resolution-decision/v1\",\"phase\":");
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

fn validateResolution(allocator: std.mem.Allocator, resolution: Resolution, phase: Phase, issues: *Issues) !void {
    if (!std.mem.eql(u8, resolution.version, "review-resolution/v1")) try issues.add(allocator, "resolution-version");
    if (!isNonblank(resolution.resolution_id) or !isNonblank(resolution.run_id)) try issues.add(allocator, "resolution-identity");
    if (resolution.review_folds.len == 0) try issues.add(allocator, "review-fold-required");
    if (!stringIn(resolution.outcome.status, &.{ "pending", "clean", "resolved", "blocked" })) try issues.add(allocator, "resolution-outcome-status");

    for (resolution.finding_ids, 0..) |finding_id, index| {
        if (!isNonblank(finding_id)) try issues.add(allocator, "resolution-finding-id-empty");
        if (containsString(resolution.finding_ids[0..index], finding_id)) try issues.add(allocator, "resolution-finding-id-duplicate");
        if (!isResolutionInputFinding(resolution.review_folds, finding_id)) try issues.add(allocator, "resolution-finding-not-input");
        if (countDecisionsWithFinding(resolution.decisions, finding_id) != 1) try issues.add(allocator, "resolution-finding-decision-coverage");
    }

    for (resolution.review_folds) |fold| {
        if (!std.mem.eql(u8, fold.version, "RF-v2")) try issues.add(allocator, "review-fold-version");
        for (fold.compression.equivalence_classes) |class| {
            if (!isNonblank(class.quotient_key) or !isNonblank(class.owner_boundary) or !isNonblank(class.law_family)) {
                try issues.add(allocator, "equivalence-class-identity");
            }
            if (class.finding_ids.len == 0) try issues.add(allocator, "equivalence-class-empty");
            for (class.finding_ids, 0..) |finding_id, index| {
                if (!isNonblank(finding_id) or containsString(class.finding_ids[0..index], finding_id)) {
                    try issues.add(allocator, "equivalence-class-finding-identity");
                }
                if (!foldHasFinding(fold, finding_id, class.quotient_key, class.owner_boundary)) {
                    try issues.add(allocator, "equivalence-class-finding-mismatch");
                }
            }
        }
        for (fold.findings) |finding| {
            if (!isNonblank(finding.finding_id) or !isNonblank(finding.quotient_key) or !isNonblank(finding.owner_boundary)) {
                try issues.add(allocator, "finding-identity");
            }
            if (std.mem.eql(u8, finding.disposition, "resolution-input")) {
                if (!containsString(resolution.finding_ids, finding.finding_id)) try issues.add(allocator, "resolution-input-not-retained");
                if (!foldHasClass(fold, finding.quotient_key, finding.finding_id, finding.owner_boundary)) {
                    try issues.add(allocator, "resolution-input-class-mismatch");
                }
                if (countDecisionsWithClass(resolution.decisions, finding.quotient_key) != 1) {
                    try issues.add(allocator, "resolution-class-decision-coverage");
                }
            } else if (containsString(resolution.finding_ids, finding.finding_id)) {
                try issues.add(allocator, "non-resolution-finding-retained");
            }
        }
    }

    for (resolution.decisions, 0..) |decision, decision_index| {
        if (!isNonblank(decision.decision_id) or !isNonblank(decision.owner_boundary)) try issues.add(allocator, "decision-identity");
        if (decisionIdentitySeen(resolution.decisions[0..decision_index], decision)) try issues.add(allocator, "decision-identity-duplicate");
        if (!stringIn(decision.strategy, &.{ "local-repair", "replacement-kernel", "blocked" })) try issues.add(allocator, "decision-strategy");
        if (decision.finding_ids.len == 0) try issues.add(allocator, "decision-findings-required");
        for (decision.finding_ids, 0..) |finding_id, finding_index| {
            if (!isNonblank(finding_id) or containsString(decision.finding_ids[0..finding_index], finding_id)) {
                try issues.add(allocator, "decision-finding-identity");
            }
            if (!containsString(resolution.finding_ids, finding_id)) try issues.add(allocator, "decision-finding-not-retained");
            if (!isResolutionInputFinding(resolution.review_folds, finding_id)) try issues.add(allocator, "decision-finding-not-input");
        }
        if (decision.liability_classes.len != 1) try issues.add(allocator, "decision-class-cardinality");
        for (decision.liability_classes, 0..) |class_ref, class_index| {
            if (!isNonblank(class_ref) or containsString(decision.liability_classes[0..class_index], class_ref)) {
                try issues.add(allocator, "decision-class-identity");
            }
        }
        if (decision.liability_classes.len == 1 and !classMatchesDecision(resolution.review_folds, decision.liability_classes[0], decision)) {
            try issues.add(allocator, "decision-class-mismatch");
        }

        if (std.mem.eql(u8, decision.strategy, "blocked")) {
            if (decision.blockers.len == 0) try issues.add(allocator, "blocked-decision-without-blocker");
            if (decision.correctness_refinement != null) try issues.add(allocator, "blocked-decision-has-refinement");
            try issues.add(allocator, "mutation-blocked-by-resolution");
            continue;
        }

        if (decision.blockers.len != 0) try issues.add(allocator, "nonblocked-decision-has-blocker");
        const decision_refinement = decision.correctness_refinement orelse {
            try issues.add(allocator, "correctness-refinement-required");
            continue;
        };
        try validateRefinement(allocator, resolution, decision, decision_refinement, issues);
    }

    try validateSemanticBalance(allocator, resolution, issues);
    if (phase == .preflight and !std.mem.eql(u8, resolution.outcome.status, "pending")) {
        try issues.add(allocator, "preflight-outcome-not-pending");
    }
    if (phase == .closeout) try validateCloseout(allocator, resolution, issues);
}

fn validateRefinement(
    allocator: std.mem.Allocator,
    resolution: Resolution,
    decision: Decision,
    decision_refinement: CorrectnessRefinement,
    issues: *Issues,
) !void {
    if (!isNonblank(decision_refinement.class_ref) or !isNonblank(decision_refinement.law_delta) or !isNonblank(decision_refinement.owner_refinement.construction)) {
        try issues.add(allocator, "correctness-refinement-identity");
    }
    if (!stringIn(decision_refinement.discrepancy, &.{ "excess", "deficit", "incoherence", "partiality", "misbinding" })) {
        try issues.add(allocator, "correctness-refinement-discrepancy");
    }
    if (decision.liability_classes.len != 1 or !std.mem.eql(u8, decision.liability_classes[0], decision_refinement.class_ref)) {
        try issues.add(allocator, "correctness-refinement-class-binding");
    }
    if (countDecisionsWithClass(resolution.decisions, decision_refinement.class_ref) != 1) try issues.add(allocator, "correctness-refinement-class-duplicate");
    if (!classMatchesDecision(resolution.review_folds, decision_refinement.class_ref, decision)) try issues.add(allocator, "correctness-refinement-class-mismatch");

    if (std.mem.eql(u8, decision.strategy, "local-repair")) {
        if (!std.mem.eql(u8, decision_refinement.owner_refinement.kind, "restore-existing-law")) {
            try issues.add(allocator, "local-repair-refinement-kind");
        }
    } else if (std.mem.eql(u8, decision.strategy, "replacement-kernel")) {
        if (!stringIn(decision_refinement.owner_refinement.kind, &.{ "strengthen-representation", "replace-owner" })) {
            try issues.add(allocator, "replacement-kernel-refinement-kind");
        }
    }

    try validateWitness(allocator, decision_refinement.preservation_witness, "preservation-witness", issues);
    try validateProgressWitness(allocator, decision_refinement.discrepancy, decision_refinement.progress_witness, issues);
}

fn validateWitness(allocator: std.mem.Allocator, witness: Witness, issue: []const u8, issues: *Issues) !void {
    if (!isNonblank(witness.statement) or !validVerifier(witness.verifier)) try issues.add(allocator, issue);
}

fn validateProgressWitness(
    allocator: std.mem.Allocator,
    discrepancy: []const u8,
    witness: ProgressWitness,
    issues: *Issues,
) !void {
    if (!isNonblank(witness.statement) or !validVerifier(witness.verifier)) try issues.add(allocator, "progress-witness");
    const expected = if (std.mem.eql(u8, discrepancy, "excess"))
        "exclude"
    else if (std.mem.eql(u8, discrepancy, "deficit"))
        "restore"
    else if (std.mem.eql(u8, discrepancy, "incoherence"))
        "reconcile"
    else if (std.mem.eql(u8, discrepancy, "partiality"))
        "totalize"
    else if (std.mem.eql(u8, discrepancy, "misbinding"))
        "rebind"
    else
        "";
    if (!std.mem.eql(u8, witness.kind, expected)) try issues.add(allocator, "progress-witness-kind");
}

fn validateCloseout(allocator: std.mem.Allocator, resolution: Resolution, issues: *Issues) !void {
    if (!stringIn(resolution.outcome.status, &.{ "clean", "resolved" })) try issues.add(allocator, "closeout-outcome-open");
    if (std.mem.eql(u8, resolution.outcome.status, "clean") and (resolution.finding_ids.len != 0 or resolution.decisions.len != 0)) {
        try issues.add(allocator, "closeout-clean-has-resolution");
    }
    if (std.mem.eql(u8, resolution.outcome.status, "resolved") and resolution.finding_ids.len == 0) {
        try issues.add(allocator, "closeout-resolved-without-findings");
    }
    for (resolution.decisions) |decision| {
        if (std.mem.eql(u8, decision.strategy, "blocked")) try issues.add(allocator, "closeout-blocked-decision");
    }
    const balance = resolution.outcome.semantic_balance;
    if (balance.uncovered_liabilities.len != 0) try issues.add(allocator, "closeout-uncovered-liabilities");
    if (balance.dominated_remaining.len != 0) try issues.add(allocator, "closeout-dominated-remaining");
    for (balance.required_retirements) |required| {
        if (!containsString(balance.completed_retirements, required)) try issues.add(allocator, "closeout-retirement-debt");
    }
}

fn validateSemanticBalance(allocator: std.mem.Allocator, resolution: Resolution, issues: *Issues) !void {
    const balance = resolution.outcome.semantic_balance;
    try validateStringSet(allocator, balance.uncovered_liabilities, "semantic-balance-uncovered-identity", issues);
    try validateStringSet(allocator, balance.required_retirements, "semantic-balance-required-identity", issues);
    try validateStringSet(allocator, balance.completed_retirements, "semantic-balance-completed-identity", issues);
    try validateStringSet(allocator, balance.dominated_remaining, "semantic-balance-dominated-identity", issues);

    for (balance.completed_retirements) |completed| {
        if (!containsString(balance.required_retirements, completed)) try issues.add(allocator, "semantic-balance-completed-not-required");
    }
    if (std.mem.eql(u8, resolution.outcome.status, "pending")) {
        for (balance.required_retirements) |required| {
            const outstanding = !containsString(balance.completed_retirements, required);
            if (outstanding != containsString(balance.dominated_remaining, required)) {
                try issues.add(allocator, "pending-retirement-balance-mismatch");
            }
        }
        for (balance.dominated_remaining) |dominated| {
            if (!containsString(balance.required_retirements, dominated) or containsString(balance.completed_retirements, dominated)) {
                try issues.add(allocator, "pending-retirement-balance-mismatch");
            }
        }
    }
    if (std.mem.eql(u8, resolution.outcome.status, "blocked")) try issues.add(allocator, "mutation-blocked-by-outcome");
}

fn validateStringSet(
    allocator: std.mem.Allocator,
    values: []const []const u8,
    issue: []const u8,
    issues: *Issues,
) !void {
    for (values, 0..) |value, index| {
        if (!isNonblank(value) or containsString(values[0..index], value)) try issues.add(allocator, issue);
    }
}

fn validVerifier(verifier: []const []const u8) bool {
    if (verifier.len == 0) return false;
    for (verifier) |arg| if (!isNonblank(arg)) return false;
    return true;
}

fn isResolutionInputFinding(review_folds: []const ReviewFold, finding_id: []const u8) bool {
    for (review_folds) |fold| for (fold.findings) |finding| {
        if (std.mem.eql(u8, finding.finding_id, finding_id) and std.mem.eql(u8, finding.disposition, "resolution-input")) return true;
    };
    return false;
}

fn foldHasFinding(fold: ReviewFold, finding_id: []const u8, class_ref: []const u8, owner: []const u8) bool {
    for (fold.findings) |finding| {
        if (std.mem.eql(u8, finding.finding_id, finding_id) and
            std.mem.eql(u8, finding.quotient_key, class_ref) and
            std.mem.eql(u8, finding.owner_boundary, owner)) return true;
    }
    return false;
}

fn foldHasClass(fold: ReviewFold, class_ref: []const u8, finding_id: []const u8, owner: []const u8) bool {
    for (fold.compression.equivalence_classes) |class| {
        if (std.mem.eql(u8, class.quotient_key, class_ref) and
            std.mem.eql(u8, class.owner_boundary, owner) and
            containsString(class.finding_ids, finding_id)) return true;
    }
    return false;
}

fn classMatchesDecision(review_folds: []const ReviewFold, class_ref: []const u8, decision: Decision) bool {
    var found = false;
    for (review_folds) |fold| {
        for (fold.compression.equivalence_classes) |class| {
            if (!std.mem.eql(u8, class.quotient_key, class_ref)) continue;
            found = true;
            if (!std.mem.eql(u8, class.owner_boundary, decision.owner_boundary)) return false;
            for (class.finding_ids) |finding_id| {
                if (isResolutionInputFinding(review_folds, finding_id) and !containsString(decision.finding_ids, finding_id)) return false;
            }
        }
    }
    if (!found) return false;
    for (decision.finding_ids) |finding_id| {
        if (!findingMatchesClass(review_folds, finding_id, class_ref, decision.owner_boundary)) return false;
    }
    return true;
}

fn findingMatchesClass(review_folds: []const ReviewFold, finding_id: []const u8, class_ref: []const u8, owner: []const u8) bool {
    for (review_folds) |fold| for (fold.findings) |finding| {
        if (std.mem.eql(u8, finding.finding_id, finding_id) and
            std.mem.eql(u8, finding.disposition, "resolution-input") and
            std.mem.eql(u8, finding.quotient_key, class_ref) and
            std.mem.eql(u8, finding.owner_boundary, owner)) return true;
    };
    return false;
}

fn countDecisionsWithClass(resolution_decisions: []const Decision, class_ref: []const u8) usize {
    var count: usize = 0;
    for (resolution_decisions) |decision| {
        if (containsString(decision.liability_classes, class_ref)) count += 1;
    }
    return count;
}

fn countDecisionsWithFinding(resolution_decisions: []const Decision, finding_id: []const u8) usize {
    var count: usize = 0;
    for (resolution_decisions) |decision| if (containsString(decision.finding_ids, finding_id)) {
        count += 1;
    };
    return count;
}

fn decisionIdentitySeen(prior: []const Decision, decision: Decision) bool {
    for (prior) |candidate| if (std.mem.eql(u8, candidate.decision_id, decision.decision_id)) return true;
    return false;
}

fn isNonblank(value: []const u8) bool {
    return std.mem.trim(u8, value, " \t\r\n").len != 0;
}

fn stringIn(value: []const u8, expected: []const []const u8) bool {
    return containsString(expected, value);
}

fn containsString(values: []const []const u8, expected: []const u8) bool {
    for (values) |value| if (std.mem.eql(u8, value, expected)) return true;
    return false;
}

fn lessString(_: void, lhs: []const u8, rhs: []const u8) bool {
    return std.mem.order(u8, lhs, rhs) == .lt;
}

const command = [_][]const u8{ "zig", "build", "test" };
const finding_ids = [_][]const u8{"finding-1"};
const class_ids = [_][]const u8{"class-1"};
const findings = [_]Finding{.{
    .finding_id = "finding-1",
    .disposition = "resolution-input",
    .quotient_key = "class-1",
    .owner_boundary = "parser",
}};
const classes = [_]EquivalenceClass{.{
    .quotient_key = "class-1",
    .finding_ids = &finding_ids,
    .owner_boundary = "parser",
    .law_family = "parse-totality",
}};
const folds = [_]ReviewFold{.{
    .version = "RF-v2",
    .findings = &findings,
    .compression = .{ .equivalence_classes = &classes },
}};
const refinement = CorrectnessRefinement{
    .class_ref = "class-1",
    .discrepancy = "excess",
    .law_delta = "Malformed input cannot inhabit Parsed",
    .owner_refinement = .{ .kind = "restore-existing-law", .construction = "Reject malformed input in the parser constructor" },
    .preservation_witness = .{ .statement = "Previously valid input still parses", .verifier = &command },
    .progress_witness = .{ .kind = "exclude", .statement = "The malformed-input class is rejected", .verifier = &command },
};
const no_blockers = [_][]const u8{};
const decisions = [_]Decision{.{
    .decision_id = "decision-1",
    .owner_boundary = "parser",
    .finding_ids = &finding_ids,
    .liability_classes = &class_ids,
    .strategy = "local-repair",
    .correctness_refinement = refinement,
    .blockers = &no_blockers,
}};
const empty = [_][]const u8{};
const clean_findings = [_]Finding{};
const clean_classes = [_]EquivalenceClass{};
const clean_folds = [_]ReviewFold{.{
    .version = "RF-v2",
    .findings = &clean_findings,
    .compression = .{ .equivalence_classes = &clean_classes },
}};
const no_decisions = [_]Decision{};

fn validResolution(status: []const u8) Resolution {
    return .{
        .version = "review-resolution/v1",
        .resolution_id = "resolution-1",
        .run_id = "run-1",
        .review_folds = &folds,
        .finding_ids = &finding_ids,
        .decisions = &decisions,
        .outcome = .{
            .status = status,
            .semantic_balance = .{
                .uncovered_liabilities = &empty,
                .required_retirements = &empty,
                .completed_retirements = &empty,
                .dominated_remaining = &empty,
            },
        },
    };
}

fn validateForTest(resolution: Resolution, phase: Phase) !Issues {
    var issues = Issues{};
    errdefer issues.deinit(std.testing.allocator);
    try validateResolution(std.testing.allocator, resolution, phase, &issues);
    return issues;
}

fn hasIssue(issues: Issues, expected: []const u8) bool {
    return containsString(issues.values.items, expected);
}

test "preflight accepts one refinement per counterexample class" {
    var issues = try validateForTest(validResolution("pending"), .preflight);
    defer issues.deinit(std.testing.allocator);
    try std.testing.expectEqual(@as(usize, 0), issues.values.items.len);
}

test "closeout accepts a structurally resolved refinement" {
    var issues = try validateForTest(validResolution("resolved"), .closeout);
    defer issues.deinit(std.testing.allocator);
    try std.testing.expectEqual(@as(usize, 0), issues.values.items.len);
}

test "closeout accepts a clean fold without refinements" {
    var resolution = validResolution("clean");
    resolution.review_folds = &clean_folds;
    resolution.finding_ids = &empty;
    resolution.decisions = &no_decisions;
    var issues = try validateForTest(resolution, .closeout);
    defer issues.deinit(std.testing.allocator);
    try std.testing.expectEqual(@as(usize, 0), issues.values.items.len);
}

test "preflight accepts only a pending mutation resolution" {
    var issues = try validateForTest(validResolution("resolved"), .preflight);
    defer issues.deinit(std.testing.allocator);
    try std.testing.expect(hasIssue(issues, "preflight-outcome-not-pending"));
}

test "non-blocked decision requires correctness refinement" {
    var changed = decisions;
    changed[0].correctness_refinement = null;
    var resolution = validResolution("pending");
    resolution.decisions = &changed;
    var issues = try validateForTest(resolution, .preflight);
    defer issues.deinit(std.testing.allocator);
    try std.testing.expect(hasIssue(issues, "correctness-refinement-required"));
}

test "one class cannot manufacture duplicate refinements" {
    const duplicated = [_]Decision{ decisions[0], decisions[0] };
    var resolution = validResolution("pending");
    resolution.decisions = &duplicated;
    var issues = try validateForTest(resolution, .preflight);
    defer issues.deinit(std.testing.allocator);
    try std.testing.expect(hasIssue(issues, "resolution-class-decision-coverage"));
    try std.testing.expect(hasIssue(issues, "correctness-refinement-class-duplicate"));
}

test "refinement must bind the quotient owner and finding set" {
    var changed = decisions;
    changed[0].owner_boundary = "handler";
    var resolution = validResolution("pending");
    resolution.decisions = &changed;
    var issues = try validateForTest(resolution, .preflight);
    defer issues.deinit(std.testing.allocator);
    try std.testing.expect(hasIssue(issues, "correctness-refinement-class-mismatch"));
}

test "blocked decision retains class coverage but cannot authorize mutation" {
    const blockers = [_][]const u8{"authority is absent"};
    var changed = decisions;
    changed[0].strategy = "blocked";
    changed[0].correctness_refinement = null;
    changed[0].blockers = &blockers;
    var resolution = validResolution("blocked");
    resolution.decisions = &changed;
    var issues = try validateForTest(resolution, .preflight);
    defer issues.deinit(std.testing.allocator);
    try std.testing.expect(hasIssue(issues, "mutation-blocked-by-resolution"));
    try std.testing.expect(hasIssue(issues, "mutation-blocked-by-outcome"));
    try std.testing.expect(!hasIssue(issues, "resolution-class-decision-coverage"));
}

test "decision findings must be retained RF-v2 resolution inputs" {
    const ghost_findings = [_][]const u8{"ghost"};
    var changed = decisions;
    changed[0].finding_ids = &ghost_findings;
    var resolution = validResolution("pending");
    resolution.decisions = &changed;
    var issues = try validateForTest(resolution, .preflight);
    defer issues.deinit(std.testing.allocator);
    try std.testing.expect(hasIssue(issues, "decision-finding-not-retained"));
    try std.testing.expect(hasIssue(issues, "decision-finding-not-input"));
    try std.testing.expect(hasIssue(issues, "decision-class-mismatch"));
}

test "local repair may only restore an existing law" {
    var changed = decisions;
    var changed_refinement = refinement;
    changed_refinement.owner_refinement.kind = "replace-owner";
    changed[0].correctness_refinement = changed_refinement;
    var resolution = validResolution("pending");
    resolution.decisions = &changed;
    var issues = try validateForTest(resolution, .preflight);
    defer issues.deinit(std.testing.allocator);
    try std.testing.expect(hasIssue(issues, "local-repair-refinement-kind"));
}

test "discrepancy determines the progress witness kind" {
    var changed = decisions;
    var changed_refinement = refinement;
    changed_refinement.progress_witness.kind = "restore";
    changed[0].correctness_refinement = changed_refinement;
    var resolution = validResolution("pending");
    resolution.decisions = &changed;
    var issues = try validateForTest(resolution, .preflight);
    defer issues.deinit(std.testing.allocator);
    try std.testing.expect(hasIssue(issues, "progress-witness-kind"));
}

test "preservation and progress witnesses require nonempty verifier argv" {
    var changed = decisions;
    var changed_refinement = refinement;
    changed_refinement.preservation_witness.verifier = &empty;
    changed_refinement.progress_witness.verifier = &empty;
    changed[0].correctness_refinement = changed_refinement;
    var resolution = validResolution("pending");
    resolution.decisions = &changed;
    var issues = try validateForTest(resolution, .preflight);
    defer issues.deinit(std.testing.allocator);
    try std.testing.expect(hasIssue(issues, "preservation-witness"));
    try std.testing.expect(hasIssue(issues, "progress-witness"));
}

test "nonblocked decisions cannot retain blockers" {
    const blockers = [_][]const u8{"still blocked"};
    var changed = decisions;
    changed[0].blockers = &blockers;
    var resolution = validResolution("pending");
    resolution.decisions = &changed;
    var issues = try validateForTest(resolution, .preflight);
    defer issues.deinit(std.testing.allocator);
    try std.testing.expect(hasIssue(issues, "nonblocked-decision-has-blocker"));
}

test "pending retirement balance is exact" {
    const debt = [_][]const u8{"retire-x"};
    var resolution = validResolution("pending");
    resolution.outcome.semantic_balance.required_retirements = &debt;
    var issues = try validateForTest(resolution, .preflight);
    defer issues.deinit(std.testing.allocator);
    try std.testing.expect(hasIssue(issues, "pending-retirement-balance-mismatch"));
}

test "closeout rejects open outcomes and semantic debt" {
    const debt = [_][]const u8{"liability-1"};
    var resolution = validResolution("pending");
    resolution.outcome.semantic_balance.uncovered_liabilities = &debt;
    resolution.outcome.semantic_balance.dominated_remaining = &debt;
    resolution.outcome.semantic_balance.required_retirements = &debt;
    var issues = try validateForTest(resolution, .closeout);
    defer issues.deinit(std.testing.allocator);
    try std.testing.expect(hasIssue(issues, "closeout-outcome-open"));
    try std.testing.expect(hasIssue(issues, "closeout-uncovered-liabilities"));
    try std.testing.expect(hasIssue(issues, "closeout-dominated-remaining"));
    try std.testing.expect(hasIssue(issues, "closeout-retirement-debt"));
}

test "closeout distinguishes clean from resolved" {
    const clean_with_findings = validResolution("clean");
    var clean_issues = try validateForTest(clean_with_findings, .closeout);
    defer clean_issues.deinit(std.testing.allocator);
    try std.testing.expect(hasIssue(clean_issues, "closeout-clean-has-resolution"));

    var resolved_without_findings = validResolution("resolved");
    resolved_without_findings.review_folds = &clean_folds;
    resolved_without_findings.finding_ids = &empty;
    resolved_without_findings.decisions = &no_decisions;
    var resolved_issues = try validateForTest(resolved_without_findings, .closeout);
    defer resolved_issues.deinit(std.testing.allocator);
    try std.testing.expect(hasIssue(resolved_issues, "closeout-resolved-without-findings"));
}

test "skill doctrine exposes correctness refinement and keeps CAS opaque" {
    const allocator = std.testing.allocator;
    const actuating = try std.Io.Dir.cwd().readFileAlloc(std.testing.io, "codex/skills/actuating/SKILL.md", allocator, .limited(MaxInputBytes));
    defer allocator.free(actuating);
    const resolution_doc = try std.Io.Dir.cwd().readFileAlloc(std.testing.io, "codex/skills/actuating/references/review-resolution.md", allocator, .limited(MaxInputBytes));
    defer allocator.free(resolution_doc);
    const goal_actuating = try std.Io.Dir.cwd().readFileAlloc(std.testing.io, "codex/skills/goal-actuating/SKILL.md", allocator, .limited(MaxInputBytes));
    defer allocator.free(goal_actuating);
    const cas = try std.Io.Dir.cwd().readFileAlloc(std.testing.io, "codex/skills/cas/SKILL.md", allocator, .limited(MaxInputBytes));
    defer allocator.free(cas);

    for ([_][]const u8{ "correctness_refinement", "review_resolution.zig", "preservation_witness", "progress_witness", "$universalist" }) |token| {
        try std.testing.expect(std.mem.indexOf(u8, actuating, token) != null or std.mem.indexOf(u8, resolution_doc, token) != null or std.mem.indexOf(u8, goal_actuating, token) != null);
    }
    for ([_][]const u8{ "correctness_refinement", "preservation_witness", "progress_witness" }) |token| {
        try std.testing.expect(std.mem.indexOf(u8, cas, token) == null);
    }
}
