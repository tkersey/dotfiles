# C++ Refactor Deep Dive

> C++ has the deepest abstraction toolbox (templates, concepts, constexpr, CRTP, variant, ranges). That makes refactoring both more powerful and more dangerous than any other language. This file is the C++-specific playbook.

## Contents

1. [The C++ isomorphism axes](#the-c-isomorphism-axes)
2. [RAII-preserving refactors](#raii-preserving-refactors)
3. [Rule of 0 / 3 / 5](#rule-of-0--3--5)
4. [std::variant vs class hierarchy](#stdvariant-vs-class-hierarchy)
5. [std::unique_ptr / std::shared_ptr migration](#stdunique_ptr--stdshared_ptr-migration)
6. [Templates: reducing compile time + LOC](#templates-reducing-compile-time--loc)
7. [Concepts (C++20) replacing SFINAE](#concepts-c20-replacing-sfinae)
8. [Ranges (C++20/23)](#ranges-c2023)
9. [constexpr promotion](#constexpr-promotion)
10. [Move semantics refactors](#move-semantics-refactors)
11. [CMake refactors](#cmake-refactors)
12. [Sanitizers as refactor oracles](#sanitizers-as-refactor-oracles)

---

## The C++ isomorphism axes

In addition to general axes, C++-specific:

| Axis | What changes if you break it |
|------|------------------------------|
| **Constructor / destructor order** | exceptions in constructors leave partially-constructed state |
| **Exception safety guarantees** | basic / strong / nothrow — changing between is observable |
| **Copy / move semantics** | deep vs shallow copy differs; perf characteristics change |
| **Template instantiation set** | compile times explode or symbols vanish |
| **ODR (One Definition Rule)** | inline vs non-inline, `constexpr` vs not, changes link behavior |
| **Name mangling** | ABI break; header-only changes ripple |
| **ABI compatibility** | struct layout, vtable order, inline namespace changes |
| **Implicit conversions** | changing `explicit` vs implicit changes calls that compile |
| **SFINAE / concept match** | subtle overload resolution changes |
| **Lambda capture semantics** | value vs reference captures lifetime differences |
| **Preprocessor expansion** | `#define` vs `constexpr` behave differently in subtle ways |

---

## RAII-preserving refactors

RAII is the single most load-bearing C++ idiom. Refactors that break it break resource management.

### Pattern: raw new/delete → unique_ptr

```cpp
// before
Widget* w = new Widget(args);
// ... may throw; may return early; may forget delete
delete w;

// after
auto w = std::make_unique<Widget>(args);
// destroyed on scope exit automatically
```

**Isomorphism axes:**
- Destruction: the original delete executed at end-of-scope (if no return/throw). The unique_ptr destroys at end-of-scope of the unique_ptr. Same location usually.
- Ownership: the raw pointer may have been passed to functions that took ownership. unique_ptr requires explicit `std::move`. Confirm each callsite.
- Null checks: raw `if (w != nullptr)` → `if (w)` works either way.

### Pattern: explicit exception-safety guarantee

Add to the isomorphism card for any C++ refactor:

```
### Exception safety
- Guarantee level (was): basic / strong / nothrow
- Guarantee level (is):  basic / strong / nothrow
- If downgraded: why is it acceptable?
```

**Downgrade is a behavior change.** If a function used to provide the strong guarantee (either succeeds or leaves state unchanged) and the refactor provides only basic (no leaks, but state may be partial), callers that relied on strong break.

### The RAII bug classic (before the refactor)

```cpp
class Logger {
public:
    Logger() { file = fopen("log.txt", "w"); }
    ~Logger() { if (file) fclose(file); }
private:
    FILE* file;
};
// missing copy/move semantics → Rule of 3/5 violation
```

Two `Logger` instances from the same source cause double-`fclose`. Any refactor here needs Rule of 0/3/5.

---

## Rule of 0 / 3 / 5

- **Rule of 0**: If your class doesn't need a user-defined destructor, copy/move constructor, or copy/move assignment operator, don't declare any. Use members that already handle it (unique_ptr, vector, etc.).
- **Rule of 3**: If you declare a destructor, copy constructor, or copy assignment operator, declare all three.
- **Rule of 5**: In modern C++, if you declare any of the Rule-of-3, also declare move constructor and move assignment (or delete them).

### The 80% refactor: move a class from Rule-of-3 to Rule-of-0

```cpp
// before (Rule of 3)
class Buffer {
public:
    Buffer(size_t n) : data(new char[n]), size(n) {}
    ~Buffer() { delete[] data; }
    Buffer(const Buffer& o) : data(new char[o.size]), size(o.size) { memcpy(data, o.data, size); }
    Buffer& operator=(const Buffer& o) { /* copy-and-swap */ }
    // move ctor/op missing → Rule of 5 violation

private:
    char* data;
    size_t size;
};

// after (Rule of 0)
class Buffer {
public:
    Buffer(size_t n) : data(n) {}
    // destructor, copy, and move all auto-generated and correct
private:
    std::vector<char> data;
};
```

**Isomorphism caveat:** vector's internal allocator may differ; capacity semantics differ from raw new/delete. For most uses, identical. For memory-constrained embedded / game dev, audit.

---

## std::variant vs class hierarchy

The canonical refactor: closed-set class hierarchy → `std::variant` + `std::visit`.

### Pattern

```cpp
// before — virtual dispatch, heap alloc per shape
class Shape { public: virtual double area() const = 0; virtual ~Shape() = default; };
class Circle : public Shape { /* area() */ };
class Square : public Shape { /* area() */ };
std::vector<std::unique_ptr<Shape>> shapes;

// after — value semantics, no heap (for small types), no vtable
using Shape = std::variant<Circle, Square, Rectangle>;
double area(const Shape& s) {
    return std::visit([](const auto& x) { return x.area(); }, s);
}
std::vector<Shape> shapes;
```

**Isomorphism axes:**
- Polymorphism set: variant is closed. External users can't add new variants. Good for app code; bad for library APIs.
- Storage: variant is sized = max(variants) + tag. Can be larger than a single-pointer hierarchy if one variant is big.
- Virtual dispatch → direct dispatch via `std::visit`. Typically faster.
- RTTI: `dynamic_cast<T*>` → `std::get_if<T>` or `std::holds_alternative<T>`. Different spelling, same semantics.

### When NOT to use variant

- Open set (library users extend).
- One variant is much larger than others (wastes storage).
- You need double dispatch or more complex OO patterns.

---

## std::unique_ptr / std::shared_ptr migration

Common C++ refactor from older codebases:

```cpp
// before — raw ownership; easy to leak
class Cache {
    std::map<Key, Value*> data;
public:
    ~Cache() { for (auto& [k, v] : data) delete v; }
    void insert(Key k, Value* v) { data[k] = v; }   // takes ownership
    Value* get(Key k) { /* returns ... what? owning? observer? */ }
};

// after — clarified ownership
class Cache {
    std::map<Key, std::unique_ptr<Value>> data;
public:
    void insert(Key k, std::unique_ptr<Value> v) { data[k] = std::move(v); }
    Value* get(Key k) { auto it = data.find(k); return it != data.end() ? it->second.get() : nullptr; }
    // `get` returns non-owning observer; caller must not delete
};
```

**Ownership-clarification isomorphism:**
- Callers that used to `delete cache.get(k)` now crash (double-free). Audit every callsite.
- Callers that took `Value*` and stored it keep working (non-owning observer is a raw pointer).
- The error semantics are better but the ABI is different.

**Migration strategy:** one method at a time, per-module, per-commit. Never bulk-convert all pointers at once.

---

## Templates: reducing compile time + LOC

### Over-templated code

```cpp
// AI-generated: every function is a template even when not needed
template<typename T> T max_of(T a, T b) { return a > b ? a : b; }
template<typename T> void print(T x) { std::cout << x; }
```

If `max_of<int>` and `max_of<double>` are the only instantiations, explicit functions are clearer. If it's used for 50 types, the template is right.

### Extern templates to control instantiation

```cpp
// header
template<typename T> class Registry { ... };
extern template class Registry<User>;
extern template class Registry<Order>;
// extern template class Registry<AnyLargeType>;   // compile-once in one .cpp

// one .cpp
template class Registry<User>;
template class Registry<Order>;
```

Reduces compile time significantly for heavy templates. Pure compile-time refactor; no runtime impact.

### Pattern: template → concept (C++20)

```cpp
// before (SFINAE)
template<typename T>
std::enable_if_t<std::is_integral_v<T>, T> double_it(T x) { return x * 2; }

// after (concept)
template<std::integral T>
T double_it(T x) { return x * 2; }
```

See [MICROPATTERNS.md §M-C5](MICROPATTERNS.md#m-c5--sfinae--concepts-c20). Massive LOC win on SFINAE-heavy code.

---

## Concepts (C++20) replacing SFINAE

Concepts are the single biggest LOC reducer for generic code written before C++20.

### Common patterns

```cpp
// before
template<typename Container>
typename std::enable_if_t<
    std::is_same_v<typename Container::value_type, typename Container::iterator::value_type>,
    typename Container::value_type
> front(Container& c) { return *c.begin(); }

// after
template<std::ranges::forward_range R>
std::ranges::range_value_t<R> front(R&& r) { return *std::ranges::begin(r); }
```

### Defining project-specific concepts

```cpp
template<typename T>
concept Hashable = requires(T t) {
    { std::hash<T>{}(t) } -> std::convertible_to<size_t>;
};

template<Hashable K, typename V>
class MyMap { /* ... */ };
```

**Isomorphism:** concept constraints narrow the set of valid Ts. Callers that previously (wrongly) instantiated with non-hashable types now get a concept-error (better) instead of a cryptic deep template error.

---

## Ranges (C++20/23)

The ranges library collapses nested iterator loops.

```cpp
// before
std::vector<int> squared_even;
for (int x : numbers) {
    if (x % 2 == 0) {
        squared_even.push_back(x * x);
    }
}

// after (C++20)
auto squared_even = numbers
    | std::views::filter([](int x) { return x % 2 == 0; })
    | std::views::transform([](int x) { return x * x; })
    | std::ranges::to<std::vector>();   // C++23 to<> or manual collect in 20
```

**Isomorphism axes:**
- Allocation: the eager version allocs a `vector`; views are lazy — only materialized by `to<>`. Same result for this case.
- Iteration order: preserved (views preserve order).
- Exception: if any view element throws, behavior identical to the loop.

**Caution:** range views are non-owning; don't capture them past the lifetime of the underlying range.

---

## constexpr promotion

Modern C++ allows more code at compile time.

```cpp
// before
int factorial(int n) { return n <= 1 ? 1 : n * factorial(n - 1); }
static const int FACT_10 = factorial(10);   // runtime

// after
constexpr int factorial(int n) { return n <= 1 ? 1 : n * factorial(n - 1); }
static_assert(factorial(10) == 3628800);   // compile-time
```

**Isomorphism:** identical runtime results; compile-time evaluation where used.

**Caveat:** `constexpr` functions have restrictions (no allocation in C++17; more allowed in C++20+). Promoting a function may require refactoring its body.

Related: `consteval` (always-compile-time) and `constinit` (compile-time initialized) in C++20.

---

## Move semantics refactors

### Pattern: pass by value + move

```cpp
// before — copy on every call
void set_name(const std::string& name) { this->name = name; }

// after — caller can move to avoid copy
void set_name(std::string name) { this->name = std::move(name); }
```

**Isomorphism:** callers that pass temporaries / movable strings now avoid copies. Callers that still have lvalues pay the same cost. Pure improvement.

### Pattern: explicit move vs NRVO

```cpp
// OK — compiler does NRVO, no move needed
std::vector<int> make_data() {
    std::vector<int> result;
    // ...
    return result;
}

// ANTI-PATTERN — std::move disables NRVO
std::vector<int> make_data() {
    std::vector<int> result;
    // ...
    return std::move(result);   // slower than letting compiler NRVO
}
```

A refactor that adds `std::move` to returns is usually wrong. Let the compiler do RVO/NRVO.

---

## CMake refactors

CMake files accumulate cruft as fast as any codebase.

### Common cleanups

- Collapse duplicate `target_include_directories` / `target_link_libraries` calls.
- Switch from file globs to explicit file lists (globs miss CMake regeneration triggers).
- Remove unused `find_package` calls.
- Migrate from `add_definitions` to `target_compile_definitions`.
- Adopt `CMakePresets.json` for IDE integration; reduces command-line flags.

### Anti-pattern: modern-CMake pretending

```cmake
# bad — relies on variables propagating from parent scope
set(CMAKE_CXX_STANDARD 20)
add_library(mylib ${SOURCES})
```

vs

```cmake
# good — target-scoped
add_library(mylib ${SOURCES})
target_compile_features(mylib PUBLIC cxx_std_20)
```

The target-scoped form is "modern CMake" — propagates cleanly via transitive deps.

---

## Sanitizers as refactor oracles

For any non-trivial C++ refactor, run under sanitizers:

```bash
# AddressSanitizer
cmake -DCMAKE_CXX_FLAGS="-fsanitize=address -fno-omit-frame-pointer" ..
make && ./tests

# UndefinedBehaviorSanitizer
cmake -DCMAKE_CXX_FLAGS="-fsanitize=undefined" ..

# ThreadSanitizer (for concurrent code)
cmake -DCMAKE_CXX_FLAGS="-fsanitize=thread" ..

# MemorySanitizer (Clang only)
cmake -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_CXX_FLAGS="-fsanitize=memory" ..
```

Each catches a different class of UB / bug. Refactors that involve:
- Raw pointer → smart pointer: ASAN catches double-free, use-after-free.
- std::thread / async: TSAN catches races.
- New template usage: UBSAN catches shift-overflow, null deref, etc.

Run before committing. Expensive (~5× slowdown for ASAN) but catches what static analysis misses.

---

## Common C++ refactor smells

- **Public headers including `<iostream>`** — pulls in huge amounts of code for every translation unit. Prefer `<ostream>` / `<istream>` or forward-declare.
- **`using namespace std;` in headers** — ODR violation potential; pollutes every includer.
- **Manual vtable emulation with function pointers** — usually refactorable to `std::variant` + `std::visit`.
- **`new` inside ctors without RAII members** — leak on exception. Move ownership into members.
- **Template metaprogramming that could be `if constexpr`** — C++17+ gives you compile-time branching without TMP.
- **Function-template specializations** — hard to reason about; usually refactor to overloads or class-template specialization.
- **C-style casts** — `(Foo*)ptr` should be `static_cast<Foo*>(ptr)` or `reinterpret_cast<>` explicitly.

For each: score, card, one lever, Edit only.
