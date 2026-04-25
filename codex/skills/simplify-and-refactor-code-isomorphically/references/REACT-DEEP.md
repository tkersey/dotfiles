# React-Specific Refactoring — deep dive

> React has more behavior-preservation axes than almost any other framework. This file is the detailed guide for refactoring React components without breaking reconciliation, hook order, memo keys, or Suspense boundaries.

## Contents

1. [The React isomorphism axes (full list)](#the-react-isomorphism-axes-full-list)
2. [Component unification recipes](#component-unification-recipes)
3. [Hook extraction recipes](#hook-extraction-recipes)
4. [State migration: lifted / context / store](#state-migration-lifted--context--store)
5. [Rerender-behavior-preserving patterns](#rerender-behavior-preserving-patterns)
6. [Suspense and streaming](#suspense-and-streaming)
7. [Server Components + Next.js App Router](#server-components--nextjs-app-router)
8. [Testing matrix per change](#testing-matrix-per-change)
9. [Specific vibe-code patterns in React](#specific-vibe-code-patterns-in-react)

---

## The React isomorphism axes (full list)

When merging or splitting components, every one of these must be preserved unless you mean otherwise:

| Axis | What changes if you break it |
|------|------------------------------|
| **Hook count & order** | React throws "rendered more/fewer hooks than previous render" |
| **Hook identity across renders** | effects re-run unnecessarily, or skip when they should run |
| **Component identity across parent re-renders** | state resets on conditional remount |
| **Key prop on lists** | state associated with an item migrates to wrong row |
| **Ref identity** | `useImperativeHandle` consumers break; measurement refs point at wrong element |
| **`useEffect` dep arrays** | stale closures or infinite loops |
| **`useMemo` / `useCallback` dep arrays** | referential equality assumptions break downstream memo |
| **Context provider position** | descendants read stale/default values |
| **Suspense boundary position** | pending fallbacks render for the wrong subtree; hydration mismatches |
| **Error boundary position** | uncaught errors unmount unintended subtrees |
| **Event bubbling / capture** | synthetic event propagation changes with DOM restructure |
| **Portal target** | z-index / focus-trap / aria-live gets re-anchored |
| **`aria-*` / role** | screen-reader output changes |
| **Form state (uncontrolled inputs)** | values are lost on DOM replacement |
| **CSS specificity order** | styles change because class-string concatenation order flipped |
| **Animation keyframes / transition states** | mount/unmount triggers animation on previously-persisted element |
| **Server-rendered HTML** | hydration mismatch; entire subtree re-renders on client |
| **Streaming response chunks** | pages render in different order |
| **Cache tags (Next.js Cache Components)** | ISR invalidation graph shifts; wrong pages revalidate |

---

## Component unification recipes

### Recipe 1 — the `<Xxx>`-family → `<Xxx variant>` collapse

Pattern: `<PrimaryButton>`, `<SecondaryButton>`, `<DangerButton>`. See [TECHNIQUES.md §2.1](TECHNIQUES.md#21-component-variants-ui) for the basic shape. Here are the REACT-SPECIFIC pitfalls.

**Pitfall: component identity changes.**
```tsx
// before — component identity differs per branch
{isDanger ? <DangerButton/> : <PrimaryButton/>}
// after — same component, different variant
{<Button variant={isDanger ? 'danger' : 'primary'}/>}
```

**Effect:** previously, toggling `isDanger` unmounted one and mounted the other — local state and effects reset. Now it's the same component; state persists across the toggle.

**Resolution:** if state *should* reset, add a `key` prop that changes on toggle:
```tsx
<Button key={isDanger ? 'danger' : 'primary'} variant={isDanger ? 'danger' : 'primary'}/>
```

**Pitfall: conditional refs.**
```tsx
// before
const dangerRef = useRef();
return isDanger ? <DangerButton ref={dangerRef}/> : <PrimaryButton/>;
// after
return <Button ref={isDanger ? dangerRef : null} variant={...}/>;
// the ref is always the same DOM node across toggles — the dangerRef fires on toggle
```

### Recipe 2 — Compound component → discriminated union of prop shapes

Pattern: `<Menu>`, `<MenuItem>`, `<MenuSeparator>`, `<MenuHeader>` each have slightly different required/optional props.

```tsx
// before — four components with drift in prop names
<Menu>
  <MenuHeader title="Options"/>
  <MenuItem icon={<Edit/>} onClick={edit} label="Edit"/>
  <MenuSeparator/>
  <MenuItem icon={<Trash/>} onClick={delete} destructive label="Delete"/>
</Menu>

// after — single component, discriminated items
type MenuItemProps =
  | { type: 'header'; title: string }
  | { type: 'item'; icon: ReactNode; label: string; onClick: () => void; destructive?: boolean }
  | { type: 'separator' };
<Menu items={[
  { type: 'header', title: 'Options' },
  { type: 'item', icon: <Edit/>, label: 'Edit', onClick: edit },
  { type: 'separator' },
  { type: 'item', icon: <Trash/>, label: 'Delete', onClick: delete, destructive: true },
]}/>
```

**Pitfall:** the old compound version let parents freely reorder children. The array version forces the parent to spell the order out. Less composable, but more predictable.

### Recipe 3 — HOC chain → hook

```tsx
// before — withAuth(withTheme(withAnalytics(MyPage)))
const EnhancedPage = withAuth(withTheme(withAnalytics(MyPage)));
// after
function MyPage() {
  const auth = useAuth();
  const theme = useTheme();
  const analytics = useAnalytics();
  // ...
}
```

**Pitfall:** HOCs inject props; hooks return values. If the HOC-wrapped component had a named prop (`this.props.auth`), downstream destructure code changes. Only do this refactor if every callsite is within the consumer.

---

## Hook extraction recipes

### Recipe 4 — fetch-on-mount → `useResource`

See [TECHNIQUES.md §2.2](TECHNIQUES.md#22-custom-hook-react). The REACT-SPECIFIC audit points:

- **Strict-mode double-effect (React 18+):** both the old and new versions handle it via `let cancelled = false`. But verify — some AI-generated hooks forget this and cause stale-state races in strict mode.
- **Effect dep array** — the URL must be in deps. Extracting a hook that closes over multiple props means the hook's effect now depends on all of them.

### Recipe 5 — `useState` cluster → `useReducer`

```tsx
// before — 5 setStates touching the same object
const [name, setName]   = useState('');
const [email, setEmail] = useState('');
const [bio, setBio]     = useState('');
const [loading, setLoading] = useState(false);
const [error, setError]     = useState<Error|null>(null);

function submit() {
  setLoading(true); setError(null);
  fetch('/api', { body: JSON.stringify({ name, email, bio }) })
    .catch(e => setError(e))
    .finally(() => setLoading(false));
}

// after
type FormState = { name: string; email: string; bio: string; loading: boolean; error: Error|null };
type Action =
  | { type: 'set'; field: 'name'|'email'|'bio'; value: string }
  | { type: 'submit/start' }
  | { type: 'submit/error'; error: Error }
  | { type: 'submit/done' };
const reducer = (s: FormState, a: Action): FormState => { /* switch */ };
const [state, dispatch] = useReducer(reducer, initial);
```

**Pitfall:** `useReducer` returns the same dispatch reference across renders, but `useState` setters also do. No memo impact. But the state object identity changes on every dispatch — downstream `useMemo` deps on `state.name` should still work, but on `state` itself (rare) won't.

### Recipe 6 — effect+setState pair → `useSyncExternalStore`

For external-subscription state (store, websocket, matchMedia), hooks were traditionally `useEffect` + `useState`. `useSyncExternalStore` (React 18+) is safer and faster.

```tsx
// before
const [matches, setMatches] = useState(() => mql.matches);
useEffect(() => {
  const handler = (e) => setMatches(e.matches);
  mql.addEventListener('change', handler);
  return () => mql.removeEventListener('change', handler);
}, []);
// after
const matches = useSyncExternalStore(
  (cb) => { mql.addEventListener('change', cb); return () => mql.removeEventListener('change', cb); },
  () => mql.matches,
  () => false   // server snapshot
);
```

Δ: −2 to −4 LOC; fewer tearing bugs.

---

## State migration: lifted / context / store

| State scope | Tool | When |
|-------------|------|------|
| Single component | `useState` | default |
| Sibling components | lift to common parent | 2 consumers |
| Cross-cutting (auth, theme, locale) | `useContext` | many read-only consumers |
| Shared editable state | Zustand / Redux / Jotai | many writers |
| Server state | TanStack Query / SWR | fetched data, cache, revalidation |

**Anti-pattern in vibe code:** throwing everything into Redux / Zustand. Most state is local. Refactoring down the tool ladder is often the right move:

- store → context — if it's a singleton never-mutated after login
- context → prop — if there's only one consumer, drill the prop
- context → lift-to-parent — if consumers are siblings

---

## Rerender-behavior-preserving patterns

### The memo-key audit

When refactoring, count `useMemo` / `useCallback` dep arrays **before** and **after**.

```bash
rg 'useMemo\(.*\[' -t tsx --multiline -U
rg 'useCallback\(.*\[' -t tsx --multiline -U
```

If the count decreased, you may have removed memoization that downstream components relied on for referential equality. Audit downstream React.memo consumers.

### React.memo compatibility

`React.memo(Component)` compares props with `===`. If a refactor now passes a new object literal where before a memoized one was passed, the memo is defeated.

```tsx
// before
const options = useMemo(() => ({ mode: 'strict' }), []);
<Consumer options={options}/>
// after (regression) — object literal created per render
<Consumer options={{ mode: 'strict' }}/>    // memo of Consumer broken
```

### Stable callbacks

```tsx
// before — new function per render
<Consumer onClick={() => setX(x+1)}/>
// after — stable ref
const handle = useCallback(() => setX(x => x+1), []);
<Consumer onClick={handle}/>
```

But: don't add `useCallback` unless downstream is memo'd. It's a minor allocation either way.

---

## Suspense and streaming

### Moving code across Suspense boundaries

If your refactor moves data-fetching from below to above a Suspense boundary:

- **Before:** the fallback shows while the fetch is in flight (good UX).
- **After:** the parent suspends; a higher-up fallback shows, which may be a bigger loading overlay (worse UX).

Preserve boundary placement, or reposition the `<Suspense>` with care.

### Error boundaries

Similar argument. A try/catch inside a component becomes "above" an error boundary once the component is restructured; errors that were handled silently now unmount subtrees.

---

## Server Components + Next.js App Router

### Client / Server boundary

`'use client'` at the top of a file crosses the server/client network boundary. Refactoring that moves a client hook into a server component breaks the build.

**Audit:**
```bash
rg "^'use client'" -t tsx -l      # files that are client components
rg "^'use server'" -t ts -l       # server actions
```

### Server actions

Refactoring a server action changes the RPC contract. The `action` function's body runs on the server; its serialized args + return shape are the wire format.

```tsx
'use server';
export async function createUser(data: UserInput) { ... }
```

If you unify two server actions into one, the URL changes. Bookmarks and browser history can point at the old one. Ship as a behavior change, not a refactor.

### Cache components (Next.js 16)

`cacheLife`, `cacheTag`, `use cache` directives determine the cache invalidation graph. Refactoring two cached functions into one with shared tags changes what `updateTag` invalidates.

---

## Testing matrix per change

For each change in this skill's verify phase, run:

| Test | What it catches |
|------|-----------------|
| `vitest` / `jest` unit | logic regression |
| `@testing-library/react` behavior | event/state regression |
| `playwright` smoke | visual regression (goldens) |
| `playwright` full + `toHaveScreenshot` | pixel-diff on every page |
| Type-check | prop shape regression |
| `react-devtools` profiler (manual) | re-render count changed |
| `@axe-core/react` in CI | accessibility regression |
| `@welldone-software/why-did-you-render` (dev only) | unnecessary re-renders surfaced |

Bundle the above into `./scripts/verify_isomorphism.sh` when the project is React.

---

## Specific vibe-code patterns in React

See [VIBE-CODED-PATHOLOGIES.md](VIBE-CODED-PATHOLOGIES.md) for P1/P2 (over-defensive), P17 (prop drilling), P18 (everything hook). React-specific additions:

### V-R1 — the "forgetting strict-mode"-pattern

```tsx
// AI-generated; fails in strict mode
useEffect(() => {
  fetch('/api').then(setData);   // fires twice in strict mode; sets state twice
}, []);
```
Fix: cancellation flag.
```tsx
useEffect(() => {
  let cancelled = false;
  fetch('/api').then(r => { if (!cancelled) setData(r); });
  return () => { cancelled = true; };
}, []);
```

### V-R2 — `useState(props.initial)` forever-stale

```tsx
// AI-generated, sets state once — never updates if props.initial changes
const [val, setVal] = useState(props.initial);
```
Fix: it depends. If intent is "initial value only," document it. If intent is "sync with prop," use a reset-on-change pattern or controlled input.

### V-R3 — useEffect for derived state

```tsx
// anti-pattern
const [sum, setSum] = useState(0);
useEffect(() => { setSum(a + b); }, [a, b]);
```
Fix: compute it directly.
```tsx
const sum = a + b;    // or useMemo if expensive
```
Very common in vibe code.

### V-R4 — `key={index}` for reorderable lists

```tsx
items.map((item, i) => <Row key={i} item={item}/>)
```
Fix: use a stable id.
```tsx
items.map(item => <Row key={item.id} item={item}/>)
```
State migrates incorrectly with `key={index}` when lists reorder.

### V-R5 — `onClick={() => setOpen(!open)}` toggle

Fine pattern but couples to current-state closure. For multi-step operations, use reducer.

### V-R6 — conditional hooks from early return

```tsx
function Comp({mode}) {
  if (mode === 'off') return null;
  const [x, setX] = useState(0);   // conditional hook — React throws
}
```
Fix: hook at top; early-return uses hook's state.
```tsx
function Comp({mode}) {
  const [x, setX] = useState(0);
  if (mode === 'off') return null;
  // ...
}
```

### V-R7 — context value as object literal

```tsx
<Ctx.Provider value={{ a, b, setA, setB }}>  // new ref per render → consumers re-render every time
```
Fix: `useMemo`.
```tsx
const value = useMemo(() => ({ a, b, setA, setB }), [a, b]);
<Ctx.Provider value={value}>
```

### V-R8 — portal without cleanup

```tsx
const el = document.getElementById('portal-root');
createPortal(<Modal/>, el);    // fine, but if el is missing, createPortal throws
```
Fix: check `el` or use Suspense/ErrorBoundary.
