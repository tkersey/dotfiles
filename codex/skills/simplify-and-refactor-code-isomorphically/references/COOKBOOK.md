# Cookbook — complete worked examples

> Side-by-side "before / collapse decision / after / proof" for real-looking
> scenarios. Each recipe maps to a clone type and one lever. Copy, adapt, execute.

## Contents

1. [Recipe 1 — Type-II parametric clone (TypeScript)](#recipe-1--type-ii-parametric-clone-typescript)
2. [Recipe 2 — Type-IV semantic clone → dispatch (Rust)](#recipe-2--type-iv-semantic-clone--dispatch-rust)
3. [Recipe 3 — Type-III gapped clone (Python)](#recipe-3--type-iii-gapped-clone-python)
4. [Recipe 4 — Type-V ACCIDENTAL RHYME → leave alone (Go)](#recipe-4--type-v-accidental-rhyme--leave-alone-go)
5. [Recipe 5 — Dead-code removal with full gauntlet](#recipe-5--dead-code-removal-with-full-gauntlet)
6. [Recipe 6 — `_v2` orphan merge (C++)](#recipe-6--_v2-orphan-merge-c)
7. [Recipe 7 — Collapse DTO explosion](#recipe-7--collapse-dto-explosion)
8. [Recipe 8 — Type-shrink: `any` → sum type](#recipe-8--type-shrink-any--sum-type)
9. [Recipe 9 — Error-handling unification](#recipe-9--error-handling-unification)

---

## Recipe 1 — Type-II parametric clone (TypeScript)

**Before.** Two near-identical mappers that differ only in how they read the key.

```ts
// src/ingest/users.ts
export function mapUsers(rows: Row[]): User[] {
  return rows.map(r => ({
    id: String(r['user_id']),
    label: r['display_name']?.trim() ?? 'anon',
    createdAt: new Date(r['created_at']),
  }));
}

// src/ingest/accounts.ts
export function mapAccounts(rows: Row[]): Account[] {
  return rows.map(r => ({
    id: String(r['account_id']),
    label: r['name']?.trim() ?? 'unnamed',
    createdAt: new Date(r['opened_at']),
  }));
}
```

**Clone classification.** Type II (parametric). Only the key names and the
default label differ. Same shape, same side effects, same observable contract.

**Lever.** L-PARAMETERIZE.

**After.**

```ts
// src/ingest/shared.ts
export interface EntitySpec<T> {
  idKey: string;
  labelKey: string;
  createdKey: string;
  defaultLabel: string;
  assemble: (id: string, label: string, createdAt: Date) => T;
}

export function mapRows<T>(rows: Row[], spec: EntitySpec<T>): T[] {
  return rows.map(r => spec.assemble(
    String(r[spec.idKey]),
    r[spec.labelKey]?.trim() ?? spec.defaultLabel,
    new Date(r[spec.createdKey])
  ));
}
```

Call sites become three lines each. LOC before: 22. LOC after: 10 (plus the
helper which replaces both). Net saving: 14.

**Proof.** Run the existing unit tests for both mappers. Goldens capture
`JSON.stringify` of `mapUsers(fixture)` and `mapAccounts(fixture)` at HEAD~1
and HEAD — bytes identical.

**Commit.** `refactor(ingest): extract mapRows helper`

---

## Recipe 2 — Type-IV semantic clone → dispatch (Rust)

**Before.**

```rust
pub fn render_email(evt: &Event) -> String {
    match evt.kind {
        EventKind::Signup  => format!("Welcome, {}!", evt.user),
        EventKind::Reset   => format!("Reset link: {}", evt.link.as_ref().unwrap()),
        EventKind::Invoice => format!("${} due on {}", evt.amount.unwrap(), evt.due.unwrap()),
    }
}

pub fn render_sms(evt: &Event) -> String {
    match evt.kind {
        EventKind::Signup  => format!("Welcome {}", evt.user),
        EventKind::Reset   => format!("Reset: {}", evt.link.as_ref().unwrap()),
        EventKind::Invoice => format!("${} due {}", evt.amount.unwrap(), evt.due.unwrap()),
    }
}
```

**Clone classification.** Type IV (semantic). The control-flow is identical;
only the message templates differ.

**Lever.** L-DISPATCH.

**After.**

```rust
pub struct Templates { signup: &'static str, reset: &'static str, invoice: &'static str }

const EMAIL: Templates = Templates {
    signup:  "Welcome, {user}!",
    reset:   "Reset link: {link}",
    invoice: "${amount} due on {due}",
};
const SMS: Templates = Templates {
    signup:  "Welcome {user}",
    reset:   "Reset: {link}",
    invoice: "${amount} due {due}",
};

pub fn render(evt: &Event, tpl: &Templates) -> String {
    let raw = match evt.kind {
        EventKind::Signup  => tpl.signup,
        EventKind::Reset   => tpl.reset,
        EventKind::Invoice => tpl.invoice,
    };
    // templating library call; same error surface as before
    apply_template(raw, evt)
}
```

**Pitfall.** The two original functions used `unwrap()`. Do **not** "fix"
that panic-on-missing-field behavior as part of this commit. That is a
different lever. If the panics are a separate bug, file a follow-up bead.
The isomorphism card explicitly lists "panics on missing field for Reset /
Invoice" as observable behavior to preserve.

**Commit.** `refactor(render): dispatch via Templates table`

---

## Recipe 3 — Type-III gapped clone (Python)

**Before.**

```python
def process_order(order):
    if order.country == 'US':
        tax = order.subtotal * 0.07
    else:
        tax = 0
    total = order.subtotal + tax
    log.info("order %s total %.2f", order.id, total)
    send_receipt(order.user, total)
    return total

def process_refund(refund):
    if refund.country == 'US':
        tax = refund.subtotal * 0.07
    else:
        tax = 0
    total = refund.subtotal + tax
    log.info("refund %s total -%.2f", refund.id, total)
    # no send_receipt — intentional
    return total
```

**Clone classification.** Type III (gapped). The difference ("no send_receipt
for refunds") is intentional.

**Decision.** Collapse is TEMPTING but the lever must preserve the receipt gap.

**Lever.** L-EXTRACT + L-PARAMETERIZE — extract the tax+total+log, leave the
side effect OUTSIDE.

**After.**

```python
def _compute_total(item, sign="+"):
    tax = item.subtotal * 0.07 if item.country == 'US' else 0
    total = item.subtotal + tax
    log.info("%s %s total %s%.2f", type(item).__name__, item.id, sign, total)
    return total

def process_order(order):
    total = _compute_total(order)
    send_receipt(order.user, total)
    return total

def process_refund(refund):
    return _compute_total(refund, sign="-")
```

**Proof.** Golden-capture the exact log lines for a representative order and
refund before and after. Byte-identical.

**Pitfall.** If you had merged the two into one function with a `should_send`
flag, you'd have erased the semantic signal that "refunds never trigger
receipts." Reviewers would start adding it back over time. Keep the boundary.

**Commit.** `refactor(billing): extract _compute_total helper`

---

## Recipe 4 — Type-V ACCIDENTAL RHYME → leave alone (Go)

**Before.**

```go
func ParseTCPHeader(b []byte) (*Header, error) {
    if len(b) < 4 { return nil, ErrShort }
    return &Header{kind: b[0], length: binary.BigEndian.Uint16(b[1:3])}, nil
}

func ParseUDPHeader(b []byte) (*Header, error) {
    if len(b) < 4 { return nil, ErrShort }
    return &Header{kind: b[0], length: binary.BigEndian.Uint16(b[1:3])}, nil
}
```

**Clone classification.** Looks like Type I — but:
- TCP headers evolved in RFC 9293; length field changed semantics.
- UDP headers are frozen in RFC 768 — byte layout will never change.
- Collapsing links the two fates. Any future TCP change has to avoid
  affecting UDP.

**Decision.** LEAVE SEPARATE. Log in rejection_log.md with citation.

**Entry for rejection_log.md.**

```
ISO-022 — TCP/UDP header parsers appear identical
- Sites: src/net/tcp.go:14, src/net/udp.go:9
- Clone-type: V (accidental rhyme)
- Rejection reason: specs evolve independently; collapsing couples their change-frequency.
- Notes: If TCP parser acquires a field, do not re-propose this collapse.
```

---

## Recipe 5 — Dead-code removal with full gauntlet

See [DEAD-CODE-SAFETY.md](DEAD-CODE-SAFETY.md) for the 12-step gauntlet. The
short version for this cookbook:

1. Grep for the symbol across the repo, including `.sql`, `.graphql`, config, and YAML.
2. Grep in dependent repos if this is a library.
3. Check for reflection / dynamic dispatch (`reflect.`, `getattr`, `Object.fromEntries`, `eval`).
4. Check string-based call sites (`require("…")`, `import(…)`, string-based routers).
5. Check CI / infra scripts for invocations.
6. Check test fixtures for references.
7. Check DB for any rows referring to the symbol.
8. Check logs / telemetry for a year-long window.
9. Stage the removal into a `_to_delete/` folder rather than deleting.
10. Deploy to staging for ≥ 7 days; watch logs.
11. If clean, delete. If not, revert.
12. Document in the ledger with the probe evidence.

**Never** delete in a refactor PR. Separate lever.

---

## Recipe 6 — `_v2` orphan merge (C++)

**Before.**

```
src/auth.cpp        (canonical)
src/auth_v2.cpp     (newer — used by 2 of 7 callers)
src/auth_new.cpp    (abandoned draft)
```

**Detection.** [ai_slop_detector.sh](../scripts/ai_slop_detector.sh) flags this
as pathology P3.

**Decision.** Merge the useful bits of `auth_v2.cpp` into `auth.cpp`, then
stage `auth_v2.cpp` and `auth_new.cpp` to `_to_delete/` after updating all
callers.

**Lever.** L-MERGE-FILES. The whole operation is *still* one lever — one
conceptual unification.

**Before committing:** every caller of `auth_v2` must be updated in the same
PR. Do not leave the system with two call sites surviving.

---

## Recipe 7 — Collapse DTO explosion

**Symptom.** `UserDTO`, `UserDTOv2`, `UserResponseDTO`, `UserApiDTO`,
`UserInternalDTO` — five nearly-identical records.

**Investigation.**
1. Callsite census: who constructs each type, who consumes each type.
2. Observable contract: do any of them have fields the others don't, at
   boundaries the caller can observe?
3. Are any used only by dead code? (gauntlet them first.)

**Typical finding.** Two of the five are actually needed for different
serialization boundaries. The other three are drive-by AI duplicates.

**Lever.** L-ELIMINATE + L-EXTRACT — remove three, extract a shared core for
the remaining two.

See also [TYPE-SHRINKS.md](TYPE-SHRINKS.md).

---

## Recipe 8 — Type-shrink: `any` → sum type

**Before.**

```ts
function handleEvent(e: any) {
  if (e.type === 'click') { /* ... */ }
  else if (e.type === 'hover') { /* ... */ }
  else if (e.type === 'submit') { /* ... */ }
}
```

**Lever.** L-TYPE-SHRINK.

**After.**

```ts
type UiEvent =
  | { type: 'click';  target: string; at: number }
  | { type: 'hover';  target: string; at: number }
  | { type: 'submit'; formId: string; at: number };

function handleEvent(e: UiEvent) {
  switch (e.type) {
    case 'click':  /* ... */ break;
    case 'hover':  /* ... */ break;
    case 'submit': /* ... */ break;
  }
}
```

**Proof.** Before the shrink, capture every call site's `e` shape via runtime
logging in one representative session. Verify the new sum type admits each
captured shape. THEN commit the type change.

---

## Recipe 9 — Error-handling unification

**Symptom.** Six files each define their own `ApiError` class with slightly
different fields.

**Investigation.**
1. Use [TRIANGULATED-KERNEL.md](TRIANGULATED-KERNEL.md) rule R-021 — error
   types at a boundary should converge, not diverge.
2. Check whether any caller uses `instanceof` — if so, you must preserve the
   class identity.
3. Check whether the wire format differs — if yes, that's a real divergence,
   not a duplication.

**Typical lever.** L-EXTRACT into a shared `ApiError` with a discriminator
tag; re-export from each module under the old name so call sites stay stable
for one release; then flip imports in a second pass.

**Pitfall.** Do NOT delete the old classes in the same commit — you'd
break `instanceof` checks silently. Stage the old classes to
`_to_delete_after_v2.3/` and commit their removal only after a release.
