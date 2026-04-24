# Language-Specific Profiling and Trouble Spots

## Rust

### First Commands

```bash
cargo test --release
cargo bench
cargo flamegraph --release -- <args>
perf record -g -- ./target/release/app && perf report
heaptrack ./target/release/app
```

### Red Flags

- `.clone()` or `.to_string()` in hot loops
- `format!` in hot paths
- default hasher on hot maps where DoS resistance is not needed
- iterator chains that materialize intermediate `Vec`s
- `Box<dyn Trait>` or dynamic dispatch in hot paths
- lock contention around `Mutex` or `RwLock`
- excessive async overhead for CPU-bound paths

### Common Levers

- accept `&str` / slices; return `Cow` when conditional ownership helps
- `Vec::with_capacity`, `HashMap::with_capacity`
- `SmallVec` for mostly-small collections
- `memchr` / `aho-corasick` for string search
- `rayon` for data parallel CPU work
- PGO/LTO only after workload is stable

## Go

### First Commands

```bash
go test ./...
go test -bench . -benchmem ./...
go test -bench BenchmarkX -cpuprofile cpu.pprof -memprofile mem.pprof
go tool pprof -http :0 cpu.pprof
go test -run TestX -trace trace.out && go tool trace trace.out
go build -gcflags='-m -m' ./... 2>&1 | grep 'escapes to heap'
```

### Red Flags

- `interface{}` / `any` causing boxing or reflection
- `defer` in hot loops
- `fmt.Sprintf` for simple conversions
- tiny goroutine per item
- channel used where direct return or atomic would suffice
- slices/maps repeatedly grown without capacity
- high GC percentage or allocation churn

### Common Levers

- concrete types or generics
- `strings.Builder`, `strconv`, pre-sized slices/maps
- `sync.Pool` for expensive reusable objects with reset semantics
- `sync.RWMutex` or sharding for read-heavy state
- worker pools and bounded channels

## TypeScript / Node.js

### First Commands

```bash
node --prof app.js && node --prof-process isolate-*.log > profile.txt
node --inspect app.js
clinic doctor -- node app.js
clinic flame -- node app.js
clinic bubbleprof -- node app.js
```

### Red Flags

- `JSON.parse` / `JSON.stringify` in hot request path
- synchronous filesystem calls on event loop
- `await` inside loops that can run concurrently
- `.map().filter().reduce()` chains over large arrays
- object spread in hot loops
- `Array.includes` for repeated membership tests
- `console.log` or formatting in production hot paths

### Common Levers

- `Set`/`Map` for membership and dynamic keys
- `Promise.all` or bounded concurrency
- streaming parsers for large JSON
- precompiled regexes
- worker threads for CPU-bound work
- monitor event-loop delay for tail issues

## Python

### First Commands

```bash
python -m cProfile -s cumtime script.py > profile.txt
py-spy record -o profile.svg -- python script.py
py-spy top --pid <pid>
scalene script.py
python -m memory_profiler script.py
```

### Red Flags

- string `+=` in loops
- `in list` for repeated membership checks
- `pandas.iterrows()`
- repeated regex compilation
- object creation in tight loops
- global or attribute lookup inside hot loops
- pure-Python numeric loops that should be vectorized

### Common Levers

- `''.join`, comprehensions, generators
- `set`/`dict` indexes
- `functools.lru_cache`
- local-variable caching in hot loops
- `re.compile`
- NumPy/Pandas vectorization
- `__slots__` for many small instances
- `tracemalloc`/`objgraph` for leak investigation

## JVM

### First Commands

```bash
java -XX:StartFlightRecording=filename=recording.jfr,dumponexit=true -jar app.jar
jcmd <pid> JFR.start name=profile settings=profile filename=recording.jfr
./profiler.sh -e cpu -d 30 -f cpu.svg <pid>
./profiler.sh -e alloc -d 30 -f alloc.svg <pid>
./profiler.sh -e lock -d 30 -f lock.svg <pid>
```

### Red Flags

- boxing/unboxing in hot collections
- reflection or dynamic proxies on hot paths
- high allocation rate and young-gen churn
- synchronized hot methods or global locks
- logging format work in hot paths
- warmup ignored in benchmarks

## Zig / C / C++

### First Commands

```bash
perf record -g -- command && perf report
perf stat -d -- command
heaptrack command
valgrind --tool=massif command
strace -c command
```

### Red Flags

- heap allocation in hot loops
- unnecessary copies/memmove/string formatting
- unpredictable branches in tight loops
- poor cache locality and pointer chasing
- false sharing across worker threads
- syscalls in inner loops

## Universal Grep Signals

```bash
rg 'for|while' src
rg 'JSON\.(parse|stringify)|json\.' src
rg 'clone|copy|deepcopy|to_string|Sprintf|format!' src
rg 'Mutex|Lock|synchronized|channel|queue' src
rg 'read|write|fetch|http|query' src
```
