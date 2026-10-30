# Testing & Observability Engineering Reference

This reference establishes rigorous standards for evaluating test suites, telemetry, structured logging, metrics, and production debuggability during code reviews.

---

## 1. Test Suite Quality & Coverage Standards

### 1.1 The Testing Pyramid Balance
- **Unit Tests (Fast, In-Memory)**: Test pure business logic, boundary transformations, validation algorithms, and error state transitions.
- **Integration Tests (With Real Dependencies)**: Test repository interactions against real containerized databases (e.g. Testcontainers), HTTP route serialization, and cache layers.
- **End-to-End Tests (Critical Paths)**: Test key business workflows end-to-end (e.g. signup -> checkout -> receipt generation).

### 1.2 The Bug Fix Rule (Mandatory Regression Tests)
- **Ironclad Policy**: Every bug fix PR **MUST** include an automated regression test that:
  1. Reproduces the defect (fails without the fix).
  2. Passes with the fix.
  3. Verifies that adjacent behavior remains intact.

### 1.3 Anti-Patterns in Testing ("Test Smells")

#### Smell A: "Testing the Mock" (Over-Mocking)
- **Defect**: The test mocks 90% of internal method calls, asserting only that mock methods were called with specific arguments. If the underlying library or class changes behavior, the test still passes green.
- **Rule**: Mock only at genuine I/O boundaries (third-party payment gateways, external SMTP servers, SMS providers). Never mock internal domain helpers or pure functions.

#### Smell B: Flaky Time-Dependent Assertions
- **Defect**: Tests relying on `sleep(100)` to await an asynchronous event, or asserting `datetime.now() == record.created_at`.
- **Remediation**: Use virtual time clocks (e.g. `freezegun`, `sinon.useFakeTimers()`, or explicit clock injection) and polling assertion helpers (`eventually()`).

#### Smell C: Shared Mutable Test State & Order Dependence
- **Defect**: Tests that depend on records inserted by prior test cases or fail when run in randomized order.
- **Remediation**: Ensure every test isolates its database transactions (rollback per test) or uses dedicated unique tenant/user IDs (`uuidv4()`).

---

## 2. Test Coverage Completeness Checklist

When reviewing tests, verify coverage across all 5 quadrants:

- [ ] **Happy Path**: Expected inputs yield expected outputs.
- [ ] **Edge Cases**: Empty arrays, 0, -1, max values, Unicode characters, extremely long strings.
- [ ] **Negative / Failure Paths**: Invalid credentials, non-existent entity IDs, network timeouts, downstream 500 errors.
- [ ] **Permission / Auth Boundaries**: Unauthorized callers, expired tokens, tenant cross-access attempts.
- [ ] **Idempotency & Concurrency**: Duplicate request submissions, rapid concurrent updates.

---

## 3. Observability & Operability Standards

### 3.1 Structured Logging (JSON Logs)
- **Standard**: Application logs must be machine-parsable JSON with structured contextual fields:
  ```json
  {
    "timestamp": "2026-10-29T15:30:00Z",
    "level": "INFO",
    "message": "Order processed successfully",
    "service": "billing-service",
    "trace_id": "8f3a1b02-...",
    "user_id": "usr_99182",
    "order_id": "ord_5521",
    "duration_ms": 142
  }
  ```
- **Log Level Discipline**:
  - `ERROR`: System is in an abnormal state requiring human intervention or on-call paging (e.g., database connection pool exhausted, unhandled exception).
  - `WARN`: Recoverable error or unusual condition handled gracefully (e.g., fallback cache used, deprecated API invoked).
  - `INFO`: Significant lifecycle events (e.g., service started, periodic sync batch finished, major transaction completed).
  - `DEBUG`: Verbose diagnostics for local development or targeted troubleshooting.

### 3.2 Correlation & Distributed Tracing
- **Rule**: Trace IDs (`traceparent`, `X-Correlation-ID`) must be:
  1. Extracted from incoming HTTP/RPC headers.
  2. Injected into every log statement within that execution context.
  3. Propagated to downstream outgoing HTTP/RPC calls.

### 3.3 Golden Signals & Metrics
When new endpoints or background jobs are added, verify telemetry is emitted:
- **Rate**: Invocations per second (counter).
- **Errors**: Number of failed invocations (counter).
- **Duration**: Request latency histogram (p50, p95, p99).
- **Saturation**: Queue depths, active worker count, connection pool utilization.

### 3.4 Production Hygiene Checks
- [ ] No raw credentials, tokens, or PII logged in messages or attributes.
- [ ] Health check endpoints (`/healthz`, `/ready`) accurately reflect dependency availability without leaking internal status.
- [ ] Graceful shutdown handlers catch `SIGTERM` / `SIGINT` to finish in-flight requests and close DB pools cleanly.
