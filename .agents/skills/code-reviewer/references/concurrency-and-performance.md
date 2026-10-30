# Concurrency & Performance Engineering Reference

This reference outlines high-impact concurrency hazards, race conditions, async flow bugs, and scalability bottlenecks that staff-level reviewers must catch during code reviews.

---

## 1. Concurrency Hazards & Race Conditions

### 1.1 Time-of-Check to Time-of-Use (TOCTOU)
- **Defect Mechanism**: Checking a condition (e.g., checking if a file exists, or if a user has sufficient account balance) and acting upon it in separate, non-atomic steps.
- **Failure Scenario**: Between the check and the use, a concurrent thread or process modifies the state, leading to overdrafts, duplicate records, or crashes.
- **Red Flag Snippet**:
  ```python
  # BAD: Non-atomic balance check and update
  user = db.get_user(user_id)
  if user.balance >= amount:
      # Concurrency gap! Another request can execute here before deduction
      user.balance -= amount
      db.save_user(user)
  ```
- **Remediation**:
  - **Pessimistic Locking**: `SELECT ... FOR UPDATE` inside a database transaction.
  - **Optimistic Locking**: Update with version check: `UPDATE accounts SET balance = balance - 100, version = version + 1 WHERE id = 1 AND version = 5;`
  - **Atomic DB Operation**: `UPDATE accounts SET balance = balance - 100 WHERE id = 1 AND balance >= 100;`

### 1.2 Shared Mutable State Without Synchronization
- **Defect Mechanism**: Multiple goroutines/threads writing to a shared dictionary, map, or slice without synchronization primitives (Mutex, RWMutex, Atomic operations).
- **Red Flag Snippet (Go)**:
  ```go
  // BAD: Concurrent map write causes fatal runtime crash in Go
  var cache = make(map[string]string)
  func Set(k, v string) {
      cache[k] = v // CRASH: concurrent map writes
  }
  ```
- **Remediation**: Use `sync.RWMutex`, `sync.Map`, or channel-based actor patterns.

### 1.3 Lock Ordering & Deadlocks
- **Defect Mechanism**: Acquiring multiple locks in different orders across concurrent code paths.
  - Thread 1: Locks `MutexA` -> then waits for `MutexB`.
  - Thread 2: Locks `MutexB` -> then waits for `MutexA`.
- **Review Rule**: All locks must be acquired in a globally uniform hierarchy. Always prefer scoped/timed locks (`try_lock_for`) with timeouts rather than unbounded lock waits.

---

## 2. Asynchronous Flow Hazards

### 2.1 Unhandled Promise / Async Task Rejections
- **Defect Mechanism**: Firing async promises without `await` or `.catch()`, or launching background tasks that fail silently or terminate the node process (`UnhandledPromiseRejection`).
- **Red Flag Snippet**:
  ```typescript
  // BAD: Fire-and-forget without error boundary or awaiting
  async function handleWebhook(payload) {
    sendNotification(payload); // If this rejects, it's an unhandled rejection!
    return { status: 'received' };
  }
  ```
- **Remediation**:
  ```typescript
  // GOOD: Awaited with proper handling or explicitly caught background task
  async function handleWebhook(payload) {
    sendNotification(payload).catch(err => {
      logger.error('Failed to send notification', { err, payloadId: payload.id });
    });
    return { status: 'received' };
  }
  ```

### 2.2 Blocking the Event Loop
- **Defect Mechanism**: Running synchronous CPU-intensive work (crypto hashing, massive JSON parsing, synchronous filesystem reads `fs.readFileSync`) on the main Node.js / Python asyncio event loop.
- **Failure Scenario**: Entire server freezes, rejecting all concurrent incoming HTTP requests while processing a single payload.
- **Remediation**: Offload CPU-bound work to worker threads (`worker_threads`, Python `ProcessPoolExecutor`, Go goroutines).

### 2.3 Goroutine / Task Leaks
- **Defect Mechanism**: Starting a goroutine or background task that blocks on an unbuffered channel write or un-cancelled context, remaining in memory indefinitely.
- **Review Rule**: Every spawned asynchronous task must have:
  1. A cancellation context (`context.Context` in Go, `AbortController` in JS, `asyncio.Task.cancel`).
  2. A bounded lifecycle with guaranteed exit conditions.

---

## 3. Database Scaling & Query Regressions

### 3.1 The N+1 Query Problem
- **Defect Mechanism**: Iterating over a collection of records and executing an individual database query for each item to load relational data.
- **Red Flag Snippet**:
  ```python
  # BAD: 1 query to fetch orders, then N queries to fetch user for each order
  orders = db.query(Order).limit(100).all()
  for order in orders:
      user_email = order.user.email # Triggers individual SQL SELECT
  ```
- **Remediation**: Eager-load relations (`joinedload`, `selectinload` in SQLAlchemy; `select_related`, `prefetch_related` in Django; `include` in Prisma).

### 3.2 Unindexed Filter & Sort Operations
- **Defect Mechanism**: Introducing queries with `WHERE`, `JOIN`, or `ORDER BY` clauses on columns lacking indexes.
- **Failure Scenario**: Sequential table scan causes query latency to spike from 2ms to 15,000ms as table grows beyond 10,000 rows.
- **Review Rule**: Verify every new query filter condition is backed by an index in the migration file.

### 3.3 Unbounded Result Sets (Missing Pagination)
- **Defect Mechanism**: `SELECT * FROM audit_logs` without `LIMIT` or keyset pagination.
- **Remediation**: Enforce cursor-based or offset-limit pagination with strict maximum page size caps.

---

## 4. Memory Leaks & Resource Management

### 4.1 Unbounded Caches
- **Defect Mechanism**: Using a plain dictionary/map as an in-memory cache without TTL (time-to-live) or max capacity eviction (LRU).
- **Failure Scenario**: Out-Of-Memory (OOM) killer terminates the process after several days in production.
- **Remediation**: Use bounded LRU caches (e.g., `lru_cache` in Python, `lru-cache` in JS, `groupcache` in Go).

### 4.2 Unclosed Streams and Sockets
- **Defect Mechanism**: Opening file descriptors, HTTP responses, or database connections without releasing them in error pathways.
- **Remediation**: Always use language-level scoped resource cleanup:
  - Python: `with open(...) as f:`
  - TypeScript/JS: `try ... finally { resource.close() }` or `using` (ECMAScript Explicit Resource Management)
  - Go: `defer resp.Body.Close()`
  - Java: `try-with-resources`
  - C#: `using var resource = ...`

---

## 5. Network & I/O Resilience

### 5.1 Missing HTTP / RPC Timeouts
- **Defect Mechanism**: Using default HTTP clients that wait indefinitely for responses (e.g. `requests.get()` without `timeout`, default `http.Client{}` in Go).
- **Failure Scenario**: Remote service hangs; client exhausts connection pools and thread pools, causing cascading service failure.
- **Review Rule**: Zero unbounded network calls. Every outgoing request MUST specify explicit connect and read timeouts (e.g., `timeout=(3.0, 10.0)`).

### 5.2 Retry Storms & Missing Jitter
- **Defect Mechanism**: Retrying failed requests immediately or in lockstep without exponential backoff and randomized jitter.
- **Failure Scenario**: Thundering herd knocks over an already struggling downstream dependency.
- **Remediation**: Implement exponential backoff with full jitter:
  $$\text{Sleep} = \text{random}(0, \min(M, B \times 2^{\text{attempt}}))$$
