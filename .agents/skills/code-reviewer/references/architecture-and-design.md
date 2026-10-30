# Architecture & Clean Design Principles Reference

This reference provides architectural doctrines and design criteria for evaluating system structure, modularity, API evolution, and long-term maintainability during code reviews.

---

## 1. Modularity & The SOLID Principles

### 1.1 Single Responsibility Principle (SRP)
- **Review Question**: Does this class, module, or function have more than one reason to change?
- **Smell**: A controller or service class that parses HTTP requests, calculates business logic, constructs raw SQL queries, sends emails, and formats PDF invoices.
- **Guideline**: Delegate distinct concerns to dedicated domain services, repositories, and notification adapters.

### 1.2 Open/Closed Principle (OCP)
- **Review Question**: Can new behavior be introduced without rewriting core control flow?
- **Smell**: Mega `switch(type)` or `if-elif-elif-else` blocks that require editing existing lines every time a new payment provider, export format, or event type is added.
- **Guideline**: Use strategy patterns, handler registries, or polymorphism.

### 1.3 Liskov Substitution Principle (LSP)
- **Review Question**: Can subclasses or interface implementations be substituted without breaking caller invariants?
- **Smell**: Subclass overriding a method to throw `NotSupportedException` or silently doing nothing when the base contract promises a state update.

### 1.4 Interface Segregation Principle (ISP)
- **Review Question**: Are interfaces lean and focused on caller needs?
- **Smell**: Monolithic interfaces with 30 methods forcing lightweight mock consumers to implement 25 no-op stubs.
- **Guideline**: Prefer role interfaces (e.g., Go's single-method `io.Reader` and `io.Writer`).

### 1.5 Dependency Inversion Principle (DIP)
- **Review Question**: Do high-level domain modules depend on abstractions rather than low-level concrete implementations?
- **Smell**: Directly instantiating concrete third-party clients (e.g., `StripeClient()`, `AWS.S3()`) deep inside domain calculation functions.
- **Guideline**: Inject dependencies via constructors or factories to facilitate isolated unit testing and future engine upgrades.

---

## 2. API Design & Contract Evolution

### 2.1 Backward Compatibility
- **Rules of Compatibility**:
  - **Additive Changes are Safe**: Adding an optional field to a request or adding a new field to a response does not break well-behaved clients.
  - **Subtractive or Type-Changing Changes are Breaking**: Deleting a field, renaming a field, changing a type from string to array, or making an optional parameter mandatory breaks downstream consumers.
- **Review Rule**: If a breaking API change is necessary, verify:
  1. Has an explicit version bump (e.g., `/v1/` to `/v2/`) occurred?
  2. Is there a deprecation period and telemetry to measure active client usage?

### 2.2 Idempotency in Distributed APIs
- **Mechanism**: Operations that create side effects (e.g., payment processing, placing orders, external resource creation) MUST accept an `Idempotency-Key` header.
- **Review Check**:
  - Is the idempotency key checked atomically before executing the operation?
  - If a duplicate request arrives while processing, does the server return `409 Conflict` or await the primary lock?
  - Are previous response payloads cached and replayed identically?

### 2.3 Error Handling & Uniform Responses
- **Standard**: Follow RFC 7807 (Problem Details for HTTP APIs) or uniform company error envelopes.
  ```json
  {
    "type": "https://api.example.com/errors/insufficient-funds",
    "title": "Insufficient Account Balance",
    "status": 422,
    "detail": "Account balance of $25.00 cannot cover transfer amount of $100.00",
    "instance": "/transfers/txn_918231",
    "code": "INSUFFICIENT_FUNDS"
  }
  ```
- **Review Rule**: Never leak raw database error messages, stack traces, or internal server IPs in API response bodies.

---

## 3. Database Schema Evolution & Zero-Downtime Migrations

### 3.1 The Expand and Contract Pattern
When renaming or altering a database column in a live production system, the change MUST be split into phased deployments:

```
Phase 1: Expand
┌────────────────────────────────┐
│ Add new column (nullable)      │
│ App reads OLD, writes OLD+NEW  │
└────────────────────────────────┘
                │
                ▼
Phase 2: Backfill
┌────────────────────────────────┐
│ Run background job to copy     │
│ historical data from OLD to NEW│
└────────────────────────────────┘
                │
                ▼
Phase 3: Switch
┌────────────────────────────────┐
│ App reads NEW, writes NEW      │
└────────────────────────────────┘
                │
                ▼
Phase 4: Contract
┌────────────────────────────────┐
│ Drop OLD column safely         │
└────────────────────────────────┘
```

### 3.2 Locking & Table Contention
- **Postgres / MySQL Gotchas**:
  - Adding a column with a non-constant `DEFAULT` on older database versions can rewrite the entire table while holding an exclusive lock.
  - Adding an index on large tables without `CONCURRENTLY` (Postgres) or `ALGORITHM=INPLACE, LOCK=NONE` (MySQL) locks writes for hours.
- **Review Rule**: Verify migrations on high-traffic tables include concurrent index creation and statement timeouts.

---

## 4. State Management & Side-Effect Boundaries

### 4.1 The Dual-Write Problem
- **Smell**: Updating a database record, and immediately calling an external message queue or third-party API without transactional guarantee:
  ```python
  # BAD: If publish fails or server crashes, database has updated but event was never published!
  db.orders.insert(order)
  sns.publish("order.created", order)
  ```
- **Remediation**: Use the **Transactional Outbox Pattern**: write the domain event to an `outbox` table in the *same* database transaction as the order, and rely on a reliable CDC (Change Data Capture) or polling relay process.

### 4.2 Premature Abstraction vs. Pragmatic DRY
- **Staff Insight**: Duplication is far cheaper than the wrong abstraction.
- **Review Check**: Do not accept generic "do-it-all" utility functions that bundle unrelated logic under the guise of DRY (Don't Repeat Yourself). Maintain clear domain boundaries.
