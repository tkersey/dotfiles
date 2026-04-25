# The Abstraction Ladder

> Each rung exists for a reason. Skip rungs and the abstraction collapses under the weight of what it's hiding.

## Contents

1. [The rungs](#the-rungs)
2. [The Rule of 3, restated](#the-rule-of-3-restated)
3. [Why over-abstraction costs more than duplication](#why-over-abstraction-costs-more-than-duplication)
4. [Autopsies](#autopsies)
5. [How to climb back down](#how-to-climb-back-down)

---

## The rungs

| Rung | Move | When |
|------|------|------|
| **0** | Copy-paste | 1–2 callsites; shape might still be wrong |
| **1** | Extract function | 3+ callsites, same shape, no variance |
| **2** | Parameterize function | 3+ callsites, ONE axis of variance, finite |
| **3** | Enum / strategy dispatch | 3+ callsites, 2+ axes of variance, bounded set |
| **4** | Trait / interface | Open set of implementors; users add new ones |
| **5** | Generic + trait bound | Type-parametric; cross-crate / cross-package |
| **6** | DSL / macro / codegen | You've done this exact refactor 3+ times across projects |

The progression is **monotonic in cost**. Each rung adds:
- **Indirection cost** — readers need to know the abstraction.
- **Compile-time cost** — generics inflate codegen; macros slow analysis.
- **Discovery cost** — new contributors don't grep the abstraction's keyword.
- **Coupling cost** — shared abstraction means a change ripples everywhere.

The progression is **non-monotonic in benefit**. Rungs 1–3 typically save you something. Rungs 4+ are bets — they pay off only if their open-ended generality is used. Most never are.

---

## The Rule of 3, restated

The classic formulation: **"three strikes, then you refactor."**

The unstated assumption: the third instance teaches you the *axis of variance*. With one instance you have a shape. With two, you have a coincidence. With three, you can see what changes between them — and that's the parameter you'd extract.

If you abstract at two, you'll guess wrong about the parameter, and the third case won't fit. Now you have a wrong abstraction *plus* a copy-paste, instead of two copy-pastes.

**Corollary:** the *fourth* instance is the diagnostic for whether the abstraction is right. If it slots in cleanly, you abstracted at the right rung. If it forces a new parameter or a special-case branch, you over-fit to the first three.

---

## Why over-abstraction costs more than duplication

Three forces work against the over-abstracter:

### 1. The "where do I look" tax

```typescript
// Reader sees:
const user = await fetcher.fetch(USER_KEY, { tx, ttl: 'short' });

// Reader needs to know:
//   - What is fetcher? (probably injected; trace 4 files)
//   - What does USER_KEY map to? (constants module)
//   - What does { tx, ttl: 'short' } mean? (Options interface)
//   - What's the return type? (generic over the key registry)
//
// Same code with the duplication left in:
const user = await db.users.findOne({ where: { id: userId }, transaction: tx });
// Reader sees the SQL shape immediately.
```

The "abstracted" version saves 5 lines and costs 5 minutes of reader time on every encounter.

### 2. The "every change touches everything" tax

A central abstraction is, by definition, a place where every variant lives. Adding a new variant requires:
- Adding a case to the dispatch
- Adding a parameter to the constructor
- Updating every caller that didn't pass it explicitly
- Updating tests for unrelated variants because the shared signature changed

Two duplicated functions cost a little time each time you write a new sibling. One over-abstracted function costs a little time every time you change *anything* in its neighborhood.

### 3. The "it accumulates parameters" decay

```python
# Started innocently
def render(component, props): ...

# Six months later
def render(component, props, *, theme=None, locale=None,
           fallback=None, suspense_boundary=None,
           tracing_span=None, error_boundary=None,
           portal_target=None, key=None):
    ...
```

Each parameter was added to support one caller's need. None of them are used by most callers. The function is now harder to read than ten variants would have been.

---

## Autopsies

### Autopsy 1: the `<Modal>` over-abstraction

A team had four similar modal components: `<ConfirmModal>`, `<AlertModal>`, `<FormModal>`, `<DrawerModal>`. They abstracted to `<Modal type="..." …>` with 17 props.

Three months later:
- `<ConfirmModal>` needs a "double-confirm for destructive actions" feature → adds `requireDoubleConfirm` prop, ignored by the other three.
- `<DrawerModal>` needs custom enter/exit animations → adds `animationVariant` prop, ignored by the other three.
- `<FormModal>` needs to handle async validation → adds `onValidate` and `validationState` props, ignored by the other three.

The component is now 600 LOC of conditionals, 14 props are mutually exclusive, and a new dev needs an hour to understand it. The original four components were 250 LOC total.

**Lesson:** they abstracted at rung 4 (open set of behaviors) when they were at rung 3 (closed set of variants). Composition would have served better:

```tsx
function Modal({ open, onClose, children }) { /* shell only */ }
function ConfirmModal(props) { return <Modal {...props}><ConfirmBody {...props}/></Modal>; }
// each variant remains separately readable
```

### Autopsy 2: the `BaseRepository<T>` over-abstraction

```typescript
abstract class BaseRepository<T, K> {
  abstract tableName(): string;
  abstract idColumn(): string;
  abstract serialize(t: T): Row;
  abstract deserialize(r: Row): T;

  async find(id: K): Promise<T | null> { /* shared SQL */ }
  async insert(t: T): Promise<T> { /* shared SQL */ }
  async update(t: T): Promise<T> { /* shared SQL */ }
  async delete(id: K): Promise<void> { /* shared SQL */ }
  async findMany(filter: Filter): Promise<T[]> { /* shared SQL */ }
}
class UserRepo extends BaseRepository<User, UserId> { ... }
class OrderRepo extends BaseRepository<Order, OrderId> { ... }
```

The abstraction looks clean. Six months later:

- `UserRepo` needs soft-delete → override `delete()` to set `deleted_at`.
- `OrderRepo` needs ON CONFLICT DO UPDATE → override `insert()`.
- `ProductRepo` joins to `inventory` → can't use `find()`, writes its own.
- Adding a new field requires touching `serialize()` and `deserialize()` — easy to drift.

The "shared" base now covers maybe 20% of actual queries, and the queries it does cover are the trivial ones that wouldn't have been duplicated anyway. The base class is dead weight.

**Lesson:** repositories rarely share business logic; they share *shape*, but the shape changes per table. A typed query builder (Kysely, sqlc) gives you the shape without the false abstraction.

### Autopsy 3: the `EventBus` over-abstraction

A team had two places that emitted "user signed up" events to do two side-effects each. They built an `EventBus` with publish/subscribe, async dispatch, retry, dead-letter queue, and observability. 800 LOC.

The two original places were 6 LOC each.

After 18 months: 12 events, 4 producers, 9 consumers. The EventBus is **the** central source of "why did this happen?" mysteries. Async dispatch means stack traces don't show the producer. Retry means side-effects fire 3× when transient errors occur. The dead-letter queue is full of events nobody understands.

**Lesson:** for fewer than ~10 producer-consumer pairs, direct calls are cheaper to read, debug, and operate. Pub/sub pays off when the *pairing* is dynamic — not when the count is small.

### Autopsy 4: the `useAsync()` over-abstraction

A team built a generic `useAsync()` hook that handles loading/error/data/cancellation. Used everywhere. 200 LOC.

Then they added pagination → `useAsync` grew an `append` mode.
Then optimistic updates → grew an `optimistic` slot.
Then SWR-style revalidation → grew `revalidateOnFocus`, `dedupingInterval`.
Then mutations → grew a `mutate` returning slot.

It's now a worse, untested SWR. They deleted it and adopted SWR/React Query.

**Lesson:** when the abstraction's surface starts to look like the surface of an existing well-known library, **stop and adopt the library**. You're not novel; you're behind.

---

## How to climb back down

If you inherit (or wrote) an over-abstraction, the safe descent is:

### Step 1 — Inline at one callsite, then verify

Pick the simplest caller. Inline the abstracted call. Confirm tests pass. The new code is more verbose; that's the point — it shows what was hidden.

### Step 2 — Repeat for each caller

Each caller now has its own, possibly slightly different, copy. That's intermediate state. Don't rush to re-abstract.

### Step 3 — Look at the spread

After every caller is inlined, actually compare them. Often you'll find:
- 60% are identical — leave them, or extract a smaller, less ambitious helper.
- 30% have small variations — keep them inlined; the variation was the bug the old abstraction was hiding.
- 10% are doing something completely different — they're now visible as the outliers they always were.

### Step 4 — Re-abstract minimally if needed

Sometimes the right answer after step 3 is: extract a *smaller* helper that handles only the truly common 60%, leaving the variants alone. That's rung 1, not rung 4.

### Step 5 — Ledger the descent

Document what was removed and why. Future agents will see the deleted abstraction in `git log` and ask "why?" Without an explanation, they may rebuild it.

---

## A short checklist before adding any abstraction

- [ ] Do I have **three** concrete instances? (not "I imagine we'll need…")
- [ ] Is the axis of variance **named** and **bounded**?
- [ ] Could I describe the abstraction's contract in one sentence without "and"?
- [ ] If I add a fourth caller next month, will it fit without a new parameter?
- [ ] If the variance changes (e.g. a new enum variant), is the change local to the abstraction?
- [ ] Is there an existing library that already does this? If yes — use it.

If you can't tick all six, leave the duplication. The cost of waiting is one more copy-paste; the cost of being wrong is six months of confused readers.
