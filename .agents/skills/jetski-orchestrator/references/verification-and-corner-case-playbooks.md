# Broad-Spectrum Verification & 10-Dimension Adversarial Corner-Case Playbooks

> **Reference Purpose**: Authoritative verification and adversarial testing manual fusing `verify-tester` (Gate 3) and `corner-case-tester` (Gate 4) into `jetski-orchestrator`. Governs **Subagent 1B** (Wave 1 planning), **`WP-Verify`** & **`WP-Corner`** (Wave 3 test synthesis), **Auditor 4A** (Wave 4 execution & anti-cheat audit), and **Wave 5** (autonomous Red-Green-Refactor self-healing).

---

## Part I: Broad-Spectrum Functional Verification (`verify-tester` — Gate 3)

While adversarial testing targets extreme 1% boundary anomalies, **Broad-Spectrum Verification** guarantees that the **90%+ mainstream operational surface area**—documented functional requirements, acceptance criteria, golden paths, alternate branches, standard validation errors, and multi-step workflows—operates with 100% contract fidelity.

### 1.1 The 5 Broad-Spectrum Verification Doctrines
1. **The $\ge 90.0\%$ Scenario Coverage Mandate**: At least **90.0%** of all documented functional requirements (`REQ-ID`s) and acceptance criteria (`AC-ID`s) must be mapped to passing, deterministic automated test cases (`TC-ID`s).
2. **The Bidirectional Traceability Invariant**: Every automated test case must trace backward to a specific `REQ-ID` / `AC-ID`, and every `REQ-ID` must trace forward to at least one executable `TC-ID`.
3. **The Four-Pillar Distribution Rule**: Test suites must be balanced across all four operational pillars (`40% Happy`, `30% Alternate`, `20% Standard Error`, `10% E2E`) rather than clustering solely on happy paths.
4. **Deterministic Contract & Schema Conformance**: Every test must assert exact data types, required/optional keys, status codes, error codes, and database state persistence—never loose `toBeTruthy()` or `is not None` checks.
5. **Quantitative Gate Sign-Off**: Gate 3 (`calc-coverage --threshold 90.0`) blocks promotion until mathematical scenario coverage reaches $\ge 90.0\%$ with a 100% test pass rate.

---

### 1.2 The Four Functional Coverage Pillars

```
┌──────────────────────────────────────────────────────────────────────────┐
│                 THE FOUR FUNCTIONAL COVERAGE PILLARS                     │
├──────────────────────────────────────────────────────────────────────────┤
│  Pillar 1 (40% Weight): GOLDEN HAPPY PATHS                               │
│  • Primary user journeys with nominal, realistic business payloads.      │
│  • Expected state mutations persisted & verified in storage/DB.          │
│  • Exact HTTP 200/201/204 status codes and full schema validation.       │
├──────────────────────────────────────────────────────────────────────────┤
│  Pillar 2 (30% Weight): ALTERNATE VALID BRANCHES                         │
│  • Optional parameters omitted vs. explicitly populated.                 │
│  • Pagination (first/middle/last page, custom page_size), sorting,       │
│    and multi-criteria filtering combinations.                            │
│  • Role/tier variations (Free vs. Enterprise, Guest vs. Authenticated)   │
│    and secondary business channels (e.g., Card vs. Wire vs. Credits).    │
├──────────────────────────────────────────────────────────────────────────┤
│  Pillar 3 (20% Weight): EXPECTED / STANDARD ERROR SCENARIOS              │
│  • Input validation rejections (HTTP 400 / typed ValidationError with    │
│    field-level details for malformed email, missing required fields).    │
│  • Authentication & authorization rejections (HTTP 401 / 403).           │
│  • Resource non-existence (HTTP 404) & duplicate conflict (HTTP 409).    │
├──────────────────────────────────────────────────────────────────────────┤
│  Pillar 4 (10% Weight): END-TO-END WORKFLOW INTEGRATIONS                 │
│  • Multi-step lifecycle journeys (e.g., Create -> Approve -> Execute     │
│    -> Audit Log -> Revoke) across module boundaries.                     │
│  • Cross-service event emission, cache invalidation, and telemetry.      │
└──────────────────────────────────────────────────────────────────────────┘
```

---

### 1.3 Bidirectional Requirements Traceability Matrix (RTM) & Coverage Formula

Every requirement is decomposed into atomic `Given-When-Then` Acceptance Criteria (`AC-ID`) and mapped to concrete test functions (`TC-ID`):

| REQ-ID | Requirement Summary | AC-ID | Given-When-Then Acceptance Criterion | Pillar | Test Case ID (`TC-ID`) | Test File & Function | Status |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| `REQ-001` | Create API key with custom scopes | `AC-001A` | **Given** active tenant, **When** `POST /keys` with valid scopes, **Then** return `201` with `key_prefix` & persist SHA-256 hash | `P1: Happy` | `TC-001` | `tests/verification/keys.rtm.test.ts::test_create_key_happy` | `PASS` |
| `REQ-001` | Create API key with optional TTL | `AC-001B` | **Given** active tenant, **When** `expires_in_days` is omitted, **Then** default expiration to `90` days | `P2: Alternate` | `TC-002` | `tests/verification/keys.rtm.test.ts::test_create_key_default_ttl` | `PASS` |
| `REQ-002` | Reject invalid scope names | `AC-002A` | **Given** active tenant, **When** `scopes` contains unknown scope, **Then** return `400 INVALID_SCOPE` | `P3: Error` | `TC-003` | `tests/verification/keys.rtm.test.ts::test_create_key_invalid_scope` | `PASS` |
| `REQ-003` | Full key lifecycle rotation | `AC-003A` | **Given** created key, **When** rotated then used on protected route, **Then** old key returns `401` and new key returns `200` | `P4: E2E` | `TC-004` | `tests/verification/keys.rtm.test.ts::test_key_rotation_e2e` | `PASS` |

**Mathematical Coverage Formula (Enforced by `jetski_orchestrator.py calc-coverage`)**:
$$\text{Scenario Coverage \%} = \left( \frac{\text{Count of AC-IDs Mapped to Passing Automated TC-IDs}}{\text{Total Documented Functional AC-IDs}} \right) \times 100 \ge 90.0\%$$

### 1.4 Data Contract & Schema Conformance Verification
Tests in `WP-Verify` must verify four contract layers on every response:
1. **Envelope & Status Contract**: Exact HTTP status code, headers (`Content-Type`, `Cache-Control`, `X-Request-Id`), or return tuple type.
2. **Strict Field & Type Schema**: Validate returned payloads against the frozen Pydantic model, Zod schema, JSON Schema, or TypeScript interface (verifying no extra leaked internal fields like `password_hash`).
3. **Storage & Side-Effect State**: Query the repository/database/mock sink directly to prove state was mutated (or remained untouched on `4xx` errors).
4. **Deterministic Ordering & Idempotency**: Verify list sorting invariants and repeat-call idempotency.

---

## Part II: Adversarial 10-Dimension Corner-Case Hunting (`corner-case-tester` — Gate 4)

Requirements specify what should happen in nominal scenarios; software breaks in the unmentioned dark corners. **Subagent 1B** plans and **`WP-Corner`** synthesizes adversarial tests across all **10 Mandatory Corner-Case Dimensions**:

### Dimension 1: Numeric Boundaries & Arithmetic Traps
- **Concrete Input Vectors**: `0`, `-0`, `-0.0`, `-1`, `1`, `Number.MAX_SAFE_INTEGER` ($2^{53}-1$), `2147483647` ($2^{31}-1$), `-2147483648` ($-2^{31}$), `9223372036854775807` ($2^{63}-1$), `0.1 + 0.2`, `1e-18`, `1e308`, `NaN`, `Infinity`, `-Infinity`, boundary indices `N-1`, `N`, `N+1`.
- **Expected Invariants**:
  - Zero values (`0`) are never coerced to `false`/`null` by truthiness checks (`if (!amount)`).
  - Division denominators of `0` raise a typed domain error or return a defined fallback—never `NaN`/`ZeroDivisionError` crash.
  - Currency and financial calculations use exact integer minor units (cents) or `Decimal` with explicit rounding (`ROUND_HALF_UP`), satisfying `0.1 + 0.2 == 0.3`.
  - `NaN` and `±Infinity` are rejected at input validation boundaries before reaching arithmetic or storage layers.

### Dimension 2: String, Encoding & Character Hazards
- **Concrete Input Vectors**: `""` (empty), `"   "` (spaces), `"\t\r\n"` (control whitespace), `"\u00A0"` (non-breaking space), `"\u200B"` (zero-width space), 1-byte string, `10MB` string, `"abc\0def"` (null byte), `"👨‍👩‍👧‍👦"` (4-byte UTF-8 ZWJ emoji sequence), `"caf\u00e9"` (NFC) vs. `"cafe\u0301"` (NFD), RTL bidirectional override `"\u202E"`, Windows `C:\path\file` vs. POSIX `/path/file`.
- **Expected Invariants**:
  - Whitespace-only strings are trimmed prior to non-empty validation.
  - Strings are Unicode-normalized (`NFC`) before comparison, deduplication, or hashing.
  - Multi-byte UTF-8 and astral emojis are never truncated mid-codepoint or rejected by storage encodings.
  - Embedded null bytes (`\0`) and control characters are stripped or rejected with HTTP 400 / `ValidationError`.

### Dimension 3: Collection & Structural Anomalies
- **Concrete Input Vectors**: `[]`, `{}`, `set()`, single-element `[x]`, all-duplicate `[x, x, x]`, `100,000+` items, reverse-sorted input, `1,000`-level deeply nested JSON `{"a":{"a":...}}`, cyclic object graph (`a.self = a`).
- **Expected Invariants**:
  - Empty collections return clean empty results (`[]`, `0`) without `IndexError` / `TypeError` on `first()`, `min()`, `max()`, or `reduce()`.
  - Unbounded list endpoints enforce hard pagination caps (`max_limit <= 100`) to prevent OOM and $O(N^2)$ event-loop freezes.
  - Deeply nested payloads ($> 32$ levels) or cyclic references are rejected deterministically without `RecursionError` / stack overflow.

### Dimension 4: Nullability, Absence & Type Discrepancies
- **Concrete Input Vectors**: `null`, `undefined`, `None`, omitted JSON keys `{}` vs. explicit `{"field": null}`, type coercion traps (`"123" + 1`, `"false"`, `"0"`, `[]`, `{}`, `[1, "two", null]`), unexpected extra fields `{"isAdmin": true}`.
- **Expected Invariants**:
  - Patch/update operations distinguish between an omitted key (*"do not modify"*) and an explicit `null` (*"clear field or reject if non-nullable"*).
  - String `"false"` or `"0"` is never coerced to boolean `true`.
  - Unknown/untrusted schema fields are stripped or rejected (`additionalProperties: false` / `extra="forbid"`).

### Dimension 5: Concurrency, Race Hazards & Timing (TOCTOU)
- **Concrete Input Vectors**: 20 concurrent workers issuing identical balance withdrawal / coupon redemption requests in the same millisecond (TOCTOU), double-click form submit within `10ms`, out-of-order async event delivery (`v2` arrives before `v1`), opposite lock acquisition order across two threads.
- **Expected Invariants**:
  - State check-and-mutate operations execute atomically (via DB `SELECT ... FOR UPDATE`, atomic `UPDATE ... WHERE balance >= amount`, CAS, or mutex lock) so concurrent withdrawals never produce a negative balance or double-spend.
  - Duplicate requests with the same `Idempotency-Key` return the cached response without re-executing side effects.
  - Lock acquisition follows a strict global topological order with bounded timeout to prevent deadlocks.

### Dimension 6: State Machine & Lifecycle Inversions
- **Concrete Input Vectors**: Calling `execute()` before `initialize()`, calling `write()` after `close()`/`dispose()`, calling `close()` 5 times in a row, illegal state jump (`PENDING` $\rightarrow$ `REFUNDED` skipping `CAPTURED`), aborting `AbortController` / cancelling `asyncio.Task` mid-transaction.
- **Expected Invariants**:
  - Premature or post-close method calls raise a deterministic `InvalidLifecycleStateError` rather than dereferencing null pointers or corrupting state.
  - Teardown/cleanup methods (`close()`, `dispose()`, `shutdown()`) are 100% idempotent.
  - Mid-flight cancellation rolls back partial state mutations cleanly.

### Dimension 7: Resource Exhaustion & Starvation
- **Concrete Input Vectors**: Exception thrown mid-stream while file descriptor / DB connection / lock is open, burst of `1,000` requests against a pool of `10` connections, unbounded in-memory cache growth with unique keys.
- **Expected Invariants**:
  - Every file handle, socket, transaction, and lock is released inside a `finally` / `with` / `defer` / `using` block even when an exception occurs.
  - In-memory caches enforce strict `maxSize` LRU eviction and TTL bounds.

### Dimension 8: Distributed Systems & Partial Failures
- **Concrete Input Vectors**: Upstream HTTP/DB timeout after `3000ms`, upstream `502 Bad Gateway` / `503 Service Unavailable` / `504 Gateway Timeout`, truncated JSON response stream, clock skew of `±30s` between auth server and verifier, leap-second timestamp `23:59:60Z`, webhook replay delivered 3 times.
- **Expected Invariants**:
  - Every external I/O call enforces an explicit timeout and surfaces a typed upstream error without hanging worker threads.
  - Webhook and event consumers deduplicate replayed message IDs idempotently.

### Dimension 9: Domain Business Logic & Semantic Invariants
- **Concrete Input Vectors**: Self-transfer (`sender_id == recipient_id`), negative order quantity `-5`, discount coupon exceeding cart total (`$50` off `$30` order), removing the last remaining `ADMIN` from an organization, circular parent-child hierarchy (`Folder A` $\rightarrow$ `Folder B` $\rightarrow$ `Folder A`).
- **Expected Invariants**:
  - Self-referential transfers or cyclic hierarchies are rejected before mutating state.
  - Cart totals and account balances enforce floor invariants ($\ge 0$) and conservation of value.
  - Conflicting permissions (`ALLOW` + `DENY`) always resolve to **Explicit Deny Wins**.

### Dimension 10: Security Boundaries & Malformed Payloads
- **Concrete Input Vectors**: Path traversal `../../../../etc/passwd` and `..\..\Windows\win.ini`, SQL injection `' OR 1=1 --`, shell metacharacters `; rm -rf /` & `$(id)`, XSS `<script>alert(1)</script>`, prototype pollution `{"__proto__": {"isAdmin": true}, "constructor": {"prototype": {"isAdmin": true}}}`, catastrophic backtracking ReDoS input `"a" * 50000 + "!"`.
- **Expected Invariants**:
  - File paths are canonicalized (`path.resolve` / `Path.resolve`) and verified to remain strictly inside the allowed base directory (`startsWith(baseDir + sep)`).
  - Untrusted strings are parameterized or escaped; dangerous prototype keys (`__proto__`, `constructor`, `prototype`) are stripped or rejected; regex evaluation runs in linear $O(N)$ time or enforces input length caps.

### 2.11 Reference Adversarial Test Exemplar (Numeric, Unicode, & Concurrency TOCTOU)

```python
import asyncio
from decimal import Decimal
import pytest
from src.ledger.service import LedgerService, InsufficientFundsError, ValidationError

@pytest.mark.parametrize("hostile_amount", [
    Decimal("0"),
    Decimal("-0.00"),
    Decimal("-100.50"),
    Decimal("NaN"),
    Decimal("Infinity"),
])
async def test_cc_001_numeric_boundary_rejections(ledger: LedgerService, hostile_amount: Decimal):
    """CC-001 (Dim 1: Numeric Boundaries): Reject zero, negative, NaN, and Infinity transfers."""
    with pytest.raises(ValidationError, match="INVALID_TRANSFER_AMOUNT"):
        await ledger.transfer(sender_id="acc_1", recipient_id="acc_2", amount=hostile_amount, idempotency_key="k1")

@pytest.mark.parametrize("hostile_id", [
    "",
    "   \t\r\n  ",
    "acc_1\x00admin",
    "../../etc/passwd",
])
async def test_cc_002_string_and_injection_boundaries(ledger: LedgerService, hostile_id: str):
    """CC-002 (Dim 2 & 10: String/Null-Byte/Traversal): Reject blank, null-byte, and path-traversal IDs."""
    with pytest.raises(ValidationError, match="INVALID_ACCOUNT_ID"):
        await ledger.transfer(sender_id=hostile_id, recipient_id="acc_2", amount=Decimal("10.00"), idempotency_key="k2")

async def test_cc_005_toctou_concurrent_double_spend_prevention(ledger: LedgerService):
    """CC-005 (Dim 5: Concurrency/TOCTOU): 20 simultaneous $100 withdrawals from a $100 balance must succeed exactly once."""
    await ledger.seed_account(account_id="acc_race", balance=Decimal("100.00"))

    async def attempt_withdrawal(idx: int):
        return await ledger.withdraw(account_id="acc_race", amount=Decimal("100.00"), idempotency_key=f"race-{idx}")

    results = await asyncio.gather(*(attempt_withdrawal(i) for i in range(20)), return_exceptions=True)
    successes = [r for r in results if not isinstance(r, Exception)]
    failures = [r for r in results if isinstance(r, InsufficientFundsError)]

    assert len(successes) == 1, f"Expected exactly 1 withdrawal to succeed, got {len(successes)}"
    assert len(failures) == 19, f"Expected 19 InsufficientFundsError rejections, got {len(failures)}"
    assert await ledger.get_balance("acc_race") == Decimal("0.00")
```

---

## Part III: Autonomous Red-Green-Refactor Self-Healing & Anti-Cheat Invariants

### 3.1 The 5-Step Red-to-Green Self-Healing Loop (Wave 5)

```
┌──────────────────────────────────────────────────────────────────────────┐
│               THE AUTONOMOUS RED-TO-GREEN REMEDIATION LOOP               │
├──────────────────────────────────────────────────────────────────────────┤
│  Step 1 [ISOLATE & WRITE FAILING TEST (RED)]:                            │
│    Reproduce the uncovered corner case, functional defect, or security   │
│    exploit with a deterministic automated test that FAILS right now.     │
│                                                                          │
│  Step 2 [MINIMAL SURGICAL PRODUCTION PATCH (GREEN)]:                     │
│    Modify ONLY the minimal necessary lines in production source files    │
│    to fix the root cause (validation guard, atomic lock, boundary check).│
│                                                                          │
│  Step 3 [VERIFY TARGET GREEN & ANTI-CHEAT AUDIT]:                        │
│    Re-run the failing test (must exit 0) AND audit `git diff` on test    │
│    files to verify zero existing assertions were deleted or weakened.    │
│                                                                          │
│  Step 4 [MUTATION SANITY CHECK (PROVE TEST HAS TEETH)]:                  │
│    Temporarily invert the new production guard (e.g., `<` to `<=`) and   │
│    confirm the new test FAILS (Mutant Killed), then restore the fix.     │
│                                                                          │
│  Step 5 [VERIFY FULL BASELINE SUITE (ZERO REGRESSIONS)]:                 │
│    Execute 100% of existing unit, 4-Pillar RTM, and 10D corner-case      │
│    tests. Every single test must pass (100% pass rate).                  │
└──────────────────────────────────────────────────────────────────────────┘
```

---

### 3.2 Anti-Cheat Guardrails & Integrity Invariants Table

When a subagent is tasked with turning a failing test suite green during Wave 5, `jetski_orchestrator.py run-remediation --enforce-anti-cheat` enforces strict guardrails against defect masking:

| # | Prohibited Cheat Pattern | Automated Detection Mechanism | Mandatory Orchestrator Remedy |
| :-: | :--- | :--- | :--- |
| **1** | **Tampering with Existing Tests** | `git diff --name-only` shows unauthorized modifications, deletions, or `.skip` / `@pytest.mark.skip` in `tests/` during a code-fix turn. | **Hard Reject**: Run `git checkout -- tests/` to restore the original test file; require the fix in production source code only. |
| **2** | **Weakening Assertions** | Diff replaces strict equality (`assert total == Decimal("19.99")`) with loose checks (`assert total is not None` or `expect(res).toBeDefined()`). | **Hard Reject**: Restore the exact value/schema/error-code assertion. |
| **3** | **Hardcoding Test Input Literals (Overfitting)** | Production source diff contains specific magic strings, UUIDs, or numbers copied from test fixtures (`if (userId === "test-user-99") return true`). | **Hard Reject**: Require a generalized algorithmic implementation that handles arbitrary inputs across the domain. |
| **4** | **Silent Exception Swallowing** | Diff adds empty or generic `try { ... } catch (e) {}` / `except Exception: pass` blocks to suppress crashes without fixing state. | **Hard Reject (`audit-diff`)**: Ban blank catch blocks; enforce typed exception propagation per the Error Taxonomy Matrix. |
| **5** | **Mocking Internal Production Sinks** | Test or production code mocks out the actual validator, SQL query, or calculation under test so the test passes trivially. | **Hard Reject**: Require real execution of the unit's logic and real schema/state verification. |
| **6** | **Ignoring Baseline Regressions** | Target corner-case test turns green, but 1 or more pre-existing unit or RTM tests break. | **Zero Tolerance**: Reject the patch immediately; 100% of both new and baseline test suites must pass simultaneously. |

---

### 3.3 Mutation Sanity Check Protocol (Proving Tests Have Teeth)

A passing test that never fails when the underlying logic is broken is a **false-positive mirage**. Before signing off Gate 4 on critical business or security logic, execute a **3-Probe Mutation Sanity Check**:
1. **Boundary Operator Inversion Probe**: Temporarily flip `<` to `<=` (or `>` to `>=`, `==` to `!=`) in the production guard and run the corner-case test. The test **must fail** (*Mutant Killed*).
2. **Guard Deletion Probe**: Temporarily comment out the new validation/sanitization/lock statement and run the test. The test **must fail** (*Mutant Killed*).
3. **Restore & Re-Verify Clean Green**: Revert the temporary mutation probe and re-run the test suite to confirm 100% green status and clean `git diff`.

---

### 3.4 Cryptographic Test Checksum Locking (`lock-tests`) & Anti-Hardcoding Detection

Lower-tier or literal subagents under pressure to make a test suite pass will frequently resort to three subtle cheats: (1) editing the test file to match their buggy output, (2) hardcoding `if/else` branches for the exact literal inputs used in the unit tests, or (3) writing tautological assertions. `jetski-orchestrator` neutralizes all three mechanically:

#### 1. Cryptographic Test Checksum & Assertion Count Locking (`lock-tests`)
Before dispatching implementation workers (`WP-1..WP-K`) or running Wave 5 remediation on production code, lock all test files:

```bash
# Step A (Before Worker Runs): Snapshot SHA-256 hashes, file sizes, and assertion counts of all test files
python .agents/skills/jetski-orchestrator/scripts/jetski_orchestrator.py lock-tests \
  --test-dir ./tests --manifest ./.test-locks.json

# Step B (After Worker Finishes): Verify zero unauthorized test modifications or assertion drops
python .agents/skills/jetski-orchestrator/scripts/jetski_orchestrator.py lock-tests \
  --test-dir ./tests --manifest ./.test-locks.json --verify
```

- **How `lock-tests` Works**:
  - Computes the exact **SHA-256 digest** and **strict assertion count** (`assert `, `expect(`, `assertEquals`, `pytest.raises`, `toThrow`) of every test file in `--test-dir` and writes `.test-locks.json`.
  - When `--verify` is executed in Gate 4 / Wave 5, any byte mismatch, deleted test file, added `.skip` / `@pytest.mark.skip` decorator, or reduced assertion count immediately fails the gate with a non-zero exit code and triggers an automatic `git checkout -- <test_file>` rollback.

#### 2. Automated Detection of Test-Literal Hardcoding (Anti-Overfitting)
Weak subagents often inspect the failing test output (`AssertionError: expected calculate_tax("TX-9941", 100) to equal 8.25`) and insert a literal bypass in production code:

```python
# FORBIDDEN CHEAT: Hardcoding test fixture literals in production code
def calculate_tax(region_code: str, subtotal: float) -> float:
    if region_code == "TX-9941" and subtotal == 100:
        return 8.25  # <-- Overfitted to the exact unit test vector!
    return subtotal * 0.05
```

- **Detection & Defense Protocol**:
  1. **Cross-File Literal Scan (`audit-diff` & `run-remediation --enforce-anti-cheat`)**: Extracts string/numeric constants from `tests/` fixtures and flags any newly added production conditional (`if ... == "<test_literal>"`) that matches a test-only fixture literal.
  2. **Parameterized & Randomized Property Probes**: Pair fixed boundary vectors with randomized inputs (e.g., random UUIDs, dynamic timestamps, or `Hypothesis` / `fast-check` generators) so hardcoded literal checks always fail on the dynamic test pass.

#### 3. Ban on Tautological & Toothless Assertions
When `WP-Verify` or `WP-Corner` subagents synthesize test files, Gate 3/4 (`audit-diff`) scans for and rejects tautological or vacuous assertions:
- ❌ **Forbidden Tautologies**: `assert True`, `assert 1 == 1`, `expect(true).toBe(true)`, `expect(result).toBeDefined()`, `assert res is not None` (when an exact value or schema is known).
- ✅ **Mandatory Strict Assertions**: Every test function must assert the **exact return value/payload**, **exact state transition**, or **exact error class + error code substring** (`pytest.raises(ValidationError, match="ERR_CODE")` / `expect(...).rejects.toThrow("ERR_CODE")`).
