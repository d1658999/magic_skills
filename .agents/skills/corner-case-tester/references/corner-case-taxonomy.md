# Corner-Case Taxonomy & Discovery Guide

This reference provides an exhaustive, field-tested taxonomy of corner cases, edge conditions, boundary traps, and failure modes across modern software applications. Use this guide during **Phase 1 (Corner-Case Deconstruction)** to systematically interrogate requirements, API contracts, database schemas, and algorithms.

---

## The 10 Core Corner-Case Dimensions

```
┌────────────────────────────────────────────────────────────────────────┐
│                      THE 10 CORNER-CASE DOMAINS                        │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Numeric & Boundary Values     │ 6. State Machine & Lifecycles       │
│ 2. Strings, Encodings & Nulls   │ 7. Resource Starvation & Overload   │
│ 3. Collections & Data Structures │ 8. Distributed & Network Failures   │
│ 4. Nullability & Missing Types   │ 9. Business Logic & Invariants      │
│ 5. Concurrency & Race Hazards    │ 10. Security & Input Sanitization   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Numeric & Boundary Values

Numeric bugs are among the most catastrophic (e.g., Ariane 5 explosion, integer wraps in financial systems).

| Sub-Category | Boundary Trigger Vectors | Typical Failure Modes |
| :--- | :--- | :--- |
| **Zero Traps** | `0`, `-0`, `0.0`, `"0"` | Zero division exceptions, falsey boolean coercion (`if (!val)` treats 0 as absent), infinite loops. |
| **Negative Boundaries** | `-1`, `-0.00001`, `-$100.00` | Unchecked negative amounts, array index out of bounds (`arr[-1]`), negative pagination offsets. |
| **Integer Extremes** | `2^31 - 1` (2,147,483,647), `2^31`, `-2^31`<br>`2^63 - 1`, `2^64 - 1` | 32-bit overflow wrapping to negative numbers, database column overflow (`INT` vs `BIGINT`). |
| **Floating-Point Quirks** | `0.1 + 0.2`, `1e-15`, `1e308`<br>`Infinity`, `-Infinity`, `NaN` | Inexact currency calculations, `NaN` propagating silently through aggregations, equality failure (`a == b`). |
| **Off-by-One Traps** | `N - 1`, `N`, `N + 1`<br>Index `0` vs `1`<br>`<` vs `<=` | Missing the final element in pagination, slice out-of-bounds, dropping the highest priority item. |
| **Precision & Rounding** | `0.005` with `ROUND_HALF_UP`<br>Banker's rounding vs ceiling | Accumulated micro-penny discrepancies in accounting or billing. |

### Interrogation Checklist for Numbers:
- [ ] What happens if the count, quantity, or balance is exactly zero?
- [ ] Can a price, discount, or timestamp ever be negative?
- [ ] Are intermediate arithmetic calculations susceptible to integer overflow before casting?
- [ ] Is floating point used for currency instead of fixed-point/integer cents/Decimals?
- [ ] Are array bounds checked with `< length` rather than `<= length`?

---

## 2. Strings, Encodings & Nulls

Strings are treated as simple character arrays by novices, but are complex byte sequences in reality.

| Sub-Category | Boundary Trigger Vectors | Typical Failure Modes |
| :--- | :--- | :--- |
| **Empty & Blank** | `""`, `" "`, `"\t"`, `"\r\n"`, `"\u00A0"` (NBSP) | Validation bypassed by whitespace, empty strings saved as database NULL, unhandled empty string indexing. |
| **Extreme Lengths** | 1 byte string, 65,536 char string, 10MB string | Database text column truncation (`VARCHAR(255)`), memory spikes, Regex catastrophic backtracking (ReDoS). |
| **Multi-byte & UTF-8** | `ñ`, `ç`, `日本語`, `العربية`, `עברית` | Byte length vs character length mismatch, corrupt string truncation splitting a UTF-8 character. |
| **Astral & Emojis** | `👨‍👩‍👧‍👦` (ZJW sequence), `😀`, `𠮷` | MySQL `utf8` (3-byte) crash instead of `utf8mb4`, string indexing pointing into middle of surrogate pair. |
| **Unicode Normalization** | `café` (`\u00e9` NFC) vs `cafe\u0301` (NFD) | String equality check fails (`"café" != "café"`), duplicate user registration or login failure. |
| **Control Characters** | `\0` (null byte), `\b`, `\x1B` (escape) | C-string termination truncation, terminal escape code injection, log file corruption. |
| **Right-to-Left (RTL)** | Hebrew/Arabic strings with LTR marks | UI layout breakage, bi-directional text injection (Bidi spoofing attacks). |

### Interrogation Checklist for Strings:
- [ ] Does input validation trim leading/trailing whitespace before checking string length?
- [ ] Can a user input surrogate pairs or emojis without crashing the database storage?
- [ ] Does length validation count Unicode grapheme clusters or raw bytes?
- [ ] Are strings normalized (e.g., NFC) before hashing, comparing, or deduplicating?

---

## 3. Collections & Data Structures

Collections can vary wildly in size, composition, and structure.

| Sub-Category | Boundary Trigger Vectors | Typical Failure Modes |
| :--- | :--- | :--- |
| **Empty Collection** | `[]`, `{}`, `set()` | `IndexError`, `NoSuchElementException`, `NullPointerException` on `head()`/`first()` or `min()`/`max()`. |
| **Single Item** | `[x]` | Iteration assumptions expecting 2+ items, delimiter joining bugs (extra trailing comma). |
| **Duplicate Entries** | `[x, x, x]` | Set collision, unexpected count inflation, infinite loop in deduplication logic. |
| **Massive Volume** | `10^5` to `10^7` items in list | Out-of-memory crash, unindexed query timeout, UI browser freeze, CPU throttling. |
| **Deeply Nested** | 1,000 nested JSON objects/arrays | Stack overflow during JSON serialization/deserialization or recursive AST traversal. |
| **Cyclic References** | `a.child = b; b.parent = a;` | Infinite loop during serialization, `JSON.stringify` TypeError, memory leak preventing GC. |
| **Sorted Inversions** | Already sorted, Reverse sorted, All identical | QuickSort worst-case `O(N^2)` degradation, binary search infinite loops. |

### Interrogation Checklist for Collections:
- [ ] What does `find()` or `select()` return when no items match?
- [ ] Does the reducer or aggregator provide an initial default value for empty lists?
- [ ] Can a list contain identical duplicates, and does the business logic handle them gracefully?
- [ ] Is pagination strictly bounded with a maximum `limit` to prevent users requesting `limit=10000000`?

---

## 4. Nullability & Missing Types

Languages handle missing values differently (`null`, `undefined`, `None`, `nil`, `NaN`).

| Sub-Category | Boundary Trigger Vectors | Typical Failure Modes |
| :--- | :--- | :--- |
| **Absent Fields** | `{}` passed where `{"name": "..."}` expected | `KeyError`, `undefined` property access causing runtime crash (`cannot read properties of undefined`). |
| **Explicit Null** | `{"status": null}` vs `{"status": "pending"}` | Null dereference, type casting failure when expecting non-nullable string. |
| **Undefined vs Null** | Optional properties omitted vs explicitly `null` | Merge/patch APIs treating omitted as "do not change" vs null as "clear field". |
| **Type Coercion Traps** | `"true"` vs `true`, `"0"` vs `0`, `[] == false` | Boolean inversion where `"false"` evaluates to truthy, numeric strings concatenated instead of added. |
| **Heterogeneous Arrays** | `[1, "two", null, {"three": 3}]` | Type assumption crash during mapping, filtering, or arithmetic operations. |

### Interrogation Checklist for Nullability:
- [ ] Are all external API and database fields marked with explicit nullability?
- [ ] Are default fallbacks provided at the edge boundary rather than deep within nested logic?
- [ ] Does the parser distinguish between an omitted field and an explicit `null` payload?

---

## 5. Concurrency & Race Hazards

Multi-threaded or asynchronous environments create unpredictable timing interactions.

| Sub-Category | Boundary Trigger Vectors | Typical Failure Modes |
| :--- | :--- | :--- |
| **TOCTOU Race** | Check balance > 0, then withdraw (concurrently) | Double-spend: both requests pass the check before either deducts, leading to negative balance. |
| **Double Click / Replay** | User clicks "Pay" twice within 50ms | Duplicate charges, duplicate database records, double email dispatch. |
| **Out-of-Order Delivery** | Message `Update_V2` arrives before `Update_V1` | Stale data overwrites fresh state in event-driven architectures. |
| **Deadlock Conditions** | Worker A locks (1, then 2); Worker B locks (2, then 1) | Thread or process freeze, database lock wait timeout, server outage. |
| **Lock Starvation** | High-frequency reader threads block writer thread | Cache or index updates never execute, serving stale data indefinitely. |

### Interrogation Checklist for Concurrency:
- [ ] Are balance deductions or inventory claims wrapped in atomic transactions with row locks or CAS?
- [ ] Are idempotent keys (`Idempotency-Key` HTTP header) enforced on all state-mutating endpoints?
- [ ] Is lock acquisition order deterministic across all codepaths to prevent cyclic deadlocks?

---

## 6. State Machine & Lifecycles

Systems transition through states; hostile or buggy callers trigger invalid sequences.

| Sub-Category | Boundary Trigger Vectors | Typical Failure Modes |
| :--- | :--- | :--- |
| **Premature Invocation** | Calling `send_message()` before `connect()` | Null socket reference, panic, unhandled promise rejection. |
| **Post-Termination Calls**| Calling `write()` after `close()` or `destroy()` | Writing to dead sockets, memory corruption, use-after-free, zombie threads. |
| **Illegal State Jumps** | Transitioning `DRAFT` directly to `REFUNDED` | Skipping approval, skipping payment capture, breaking audit trails. |
| **Double Initialization** | Calling `init()` or `start()` multiple times | Leaking worker pools, duplicate event listeners, corrupted configuration. |
| **Mid-Flight Abort** | HTTP client disconnects while server writes DB | Partial state updates left orphaned if transaction cleanup handler is omitted. |

### Interrogation Checklist for State:
- [ ] Does the state machine reject invalid transitions with explicit typed errors?
- [ ] Are cleanup methods (`dispose`, `close`, `cleanup`) strictly idempotent?
- [ ] Does every transaction guarantee rollback upon cancellation or timeout?

---

## 7. Resource Starvation & Overload

Real systems run on constrained CPU, memory, network, and disk.

| Sub-Category | Boundary Trigger Vectors | Typical Failure Modes |
| :--- | :--- | :--- |
| **Disk Space Full** | Zero bytes left on storage partition | Partial log writes, corrupt SQLite databases, silent save failures. |
| **File Descriptor Leaks** | Opening files/sockets without `finally` / `using` | `EMFILE: too many open files`, server ceases accepting new network connections. |
| **Memory Growth (Leaks)** | Caching without LRU eviction, unremoved listeners | Slow memory bloat culminating in Out Of Memory (OOM) killer terminating process. |
| **Connection Starvation** | DB pool of 10 connections receiving 500 req/sec | Request queue backlog, cascading HTTP 504 gateway timeouts. |
| **CPU Starvation** | ReDoS regex, complex nested loops on large inputs | Event loop starvation, health check ping timeouts, orchestration pod restarts. |

---

## 8. Distributed & Network Failures

In distributed systems, the network is fundamentally unreliable.

| Sub-Category | Boundary Trigger Vectors | Typical Failure Modes |
| :--- | :--- | :--- |
| **Network Timeout** | Upstream API hangs for 60s without responding | Thread pool exhaustion, domino-effect failure of dependent microservices. |
| **Partial Response** | Connection severed after receiving 50% of payload | JSON parser failure, partial state persisted as complete. |
| **Clock Skew / Leap Sec**| Machine clock 5 seconds behind authorization server | JWT token rejected as "used before issued" (`nbf` claim failure). |
| **Retry Storms** | 1000 failed clients all retry at exact same millisecond | Thundering herd problem, taking down recovery instances instantly. |

---

## 9. Business Logic & Semantic Invariants

Requirements express business rules; corner cases invert business assumptions.

| Sub-Category | Boundary Trigger Vectors | Typical Failure Modes |
| :--- | :--- | :--- |
| **Self-Referential Actions**| Transfer money from Account A to Account A | Transaction fee deducted twice, balance duplicated, or lock deadlock. |
| **Discount Exceeding Total**| $50 coupon applied to $30 shopping cart | Negative cart total, merchant pays customer to buy goods. |
| **Circular Dependencies** | Task A depends on Task B; Task B depends on Task A | Infinite loop in scheduler, deadlock in DAG topological sort. |
| **Role Inversions** | Removing the sole remaining Admin user from an org | Orphaned organization with no administrative access possible. |

---

## 10. Security & Input Sanitization

Adversarial inputs designed to breach system integrity.

| Sub-Category | Boundary Trigger Vectors | Typical Failure Modes |
| :--- | :--- | :--- |
| **Directory Traversal** | `../../../../etc/passwd`, `..\..\Windows\win.ini` | Arbitrary file read/write, unauthorized config exposure. |
| **Metacharacters** | `' OR '1'='1`, `$(whoami)`, `<script>alert(1)</script>` | SQL injection, remote command execution, stored cross-site scripting. |
| **Format String Injection**| `%s%s%s%s%s`, `{{constructor.constructor('...')()}}` | String formatting crash, template injection, prototype pollution. |

---

## The Corner-Case Scoring Heuristic (Risk Matrix)

When prioritizing corner cases, score each across **Likelihood** (1-3) and **Severity** (1-3):

```
Severity:
  3 = Critical (Data corruption, money loss, security vulnerability, crash)
  2 = High (Incorrect computation, permanent state lock, degraded SLA)
  1 = Medium / Low (Cosmetic defect, wrong error code, unformatted output)

Likelihood:
  3 = High (Common user typo, normal network jitter, daily occurrence)
  2 = Medium (Edge condition under stress or specific user sequence)
  1 = Low (Requires deliberate adversarial craft or bizarre system failure)

Risk Score = Severity × Likelihood (Range: 1 to 9)
  7 - 9: CRITICAL (Must be tested and fixed immediately)
  4 - 6: HIGH / MEDIUM (Must be tested and scheduled for remediation)
  1 - 3: LOW (Documented or guarded with defensive assertions)
```
