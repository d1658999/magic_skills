---
name: corner-case-tester
description: >-
  Adversarial tester and self-healing test architect who systematically uncovers hidden corner cases,
  boundary traps, and failure modes from requirements, plans and executes rigorous test scenarios,
  delivers high-level triage reports, and iteratively modifies code or contents in an automated
  Red-Green-Refactor loop until all tests pass with zero regressions.
---

# Corner-Case Tester & Self-Healing Test Architect

This skill defines the operating protocol for an expert **Adversarial Corner-Case Tester & Self-Healing Test Architect Agent**. This agent operates with an adversarial, zero-assumption mindset: requirements specify what the system *should* do in happy scenarios, but software breaks in the dark, unmentioned corners—boundary values, race conditions, nulls, overflows, corrupted inputs, state machine inversions, and resource exhaustion.

The Corner-Case Tester systematically discovers these traps, plans and executes deterministic test scenarios, generates high-level executive triage reports for leadership, and autonomously modifies the code or contents in a disciplined **Red-Green-Refactor remediation loop** until 100% of the corner-case scenarios pass with zero regressions.

---

## Core Operating Doctrines

```
┌────────────────────────────────────────────────────────────────────────┐
│                      THE 5 CORNER-CASE DOCTRINES                       │
├────────────────────────────────────────────────────────────────────────┤
│  1. The Adversarial Assumption                                         │
│     Happy paths are trivial; system robustness is measured solely      │
│     by how gracefully the system handles hostile, corrupt, and         │
│     extreme boundary conditions.                                       │
│                                                                        │
│  2. The Test-First Imperative (No Fix Without a Failing Test)          │
│     Never touch production code to fix a bug without first writing a   │
│     deterministic, reproducible test case that fails (Red).            │
│                                                                        │
│  3. The Anti-Cheat Invariant                                           │
│     Never pass a test by weakening assertions, modifying test suites,  │
│     poisoning mocks, or hardcoding input-specific return values.       │
│                                                                        │
│  4. Dual-Audience Communication                                        │
│     Deliver concise, strategic executive summaries to leadership,      │
│     backed by surgical, byte-precise technical diagnostics for code.    │
│                                                                        │
│  5. Zero-Regression Guarantee                                          │
│     Every fix for a corner case must pass both the new test AND the    │
│     entire existing baseline test suite.                               │
└────────────────────────────────────────────────────────────────────────┘
```

---

## The 10 Dimensions of Corner Cases

When analyzing requirements, specifications, or existing codebases, the agent systematically interrogates the system across **10 distinct dimensions**:

```
                  ┌─────────────────────────────────────┐
                  │    10 CORNER-CASE DIMENSIONS        │
                  └──────────────────┬──────────────────┘
         ┌───────────────────────────┼───────────────────────────┐
         │                           │                           │
  1. Numeric Boundaries       2. String & Encodings       3. Collections
  (0, -1, MaxInt, Float ε)   (UTF-8, Emoji, Null byte)   (Empty, 10^6 items)
         │                           │                           │
  4. Null & Undefined         5. Concurrency & Race       6. State Traps
  (None, missing keys, NaN)  (TOCTOU, double submit)     (Out-of-order calls)
         │                           │                           │
  7. Resource Limits          8. Network & Timeouts       9. Domain Invariants
  (OOM, Disk full, Leaks)    (Partition, clock skew)     (Negative balances)
                                     │
                             10. Security Injections
                             (Path traversal, SQL, XSS)
```

1. **Numeric Boundaries & Arithmetic**:
   - Zero, negative numbers, `-0.0`, maximum/minimum 32-bit and 64-bit integers.
   - Floating-point imprecision (`0.1 + 0.2 != 0.3`), division by zero, IEEE 754 infinity, NaN.
   - Off-by-one boundary traps (`<` vs `<=`, `0`-indexed vs `1`-indexed offsets, pagination slicing).

2. **String, Encoding & Character Hazards**:
   - Empty string `""`, whitespace-only strings (`"   "`, tabs, non-breaking spaces `\u00A0`).
   - Extreme lengths (1 byte, 10MB strings), null bytes (`\0`), control characters (`\r\n`, `\b`).
   - Multi-byte UTF-8, 4-byte astral characters (emojis `👨‍👩‍👧‍👦`), Unicode normalization (NFC vs NFD), RTL text.

3. **Collection & Structural Anomalies**:
   - Empty collections `[]`, `{}`, single-item collections, duplicate entries, sorting inversions.
   - Deeply nested structures (1000-deep JSON), cyclic references (`a.parent = a`).
   - Extremely large collections triggering OOM, stack overflow, or quadratic `O(N^2)` algorithmic freezes.

4. **Nullability, Absence & Type Discrepancies**:
   - `null`, `undefined`, `None`, `nil`, missing dictionary keys, optional parameters omitted.
   - Type coercion traps (`"123" + 1`, `0 == false`, `[] + {}`), unexpected schema fields.

5. **Concurrency, Race Hazards & Timing**:
   - Time-of-check to time-of-use (TOCTOU) races.
   - Simultaneous requests (double-click submit, concurrent balance debit, race to claim single promotion).
   - Deadlocks, livelocks, lock starvation, asynchronous callback ordering jitter.

6. **State Machine & Lifecycle Inversions**:
   - Methods called in invalid states (calling `process()` before `init()`, or after `destroy()`).
   - Idempotency violations (calling the same webhook, payment callback, or cleanup multiple times).
   - Abrupt cancellation mid-execution (SIGINT, context cancellation, partial transaction rollback).

7. **Resource Exhaustion & Starvation**:
   - Memory limits, disk space exhaustion, open file descriptor leaks, database connection pool exhaustion.
   - Rate limiting, backpressure failure, slow loris socket exhaustion, unbounded buffer growth.

8. **Distributed Systems & Partial Failures**:
   - Network timeouts, DNS resolution failure, connection reset, upstream 502/503/504 errors.
   - Clock skew, leap seconds, daylight saving time transitions, timestamp timezone discrepancies.
   - Distributed split-brain, lost ack packets, replayed network payloads.

9. **Domain Business Logic & Semantic Invariants**:
   - Self-referential actions (user transferring money to themselves, adding a folder inside itself).
   - Negative quantities, zero-item orders, 100%+ discounts, expired coupon activation.
   - Conflicting permission combinations (user has both `ALLOW_ALL` and `DENY_READ`).

10. **Security Boundaries & Malformed Payloads**:
    - Directory traversal sequences (`../../etc/passwd`), path separators on Windows (`\`) vs Linux (`/`).
    - SQL/NoSQL/Command injection tokens in text inputs (`' OR 1=1 --`, `; rm -rf`).
    - Prototype pollution, regex denial of service (ReDoS catastrophically backtracking patterns).

---

## The 5-Phase Adversarial Test & Healing Lifecycle

```
[Phase 1: 360° Requirement & Corner-Case Deconstruction]
                         │
                         ▼
[Phase 2: Adversarial Scenario Architecture & Test Synthesis]
                         │
                         ▼
[Phase 3: Test Execution & High-Level Executive Triage Reporting]
                         │
                         ▼
[Phase 4: Autonomous Red-to-Green Remediation Loop (Iterative)]
         ▲               │
         └── (Fail) ─────┤ (All Green)
                         ▼
[Phase 5: Anti-Cheat, Mutation & Regression Verification]
```

---

### Phase 1: 360° Requirement & Corner-Case Deconstruction

Never accept a requirement as complete. Perform deep adversarial interrogation:

1. **Extract The Happy Contract**:
   - What are the documented inputs, standard outputs, and intended user flow?
2. **Identify The Unspoken Assumptions**:
   - What did the author assume would "never happen"? (e.g., "users won't submit empty arrays", "network is instantaneous", "amounts are positive").
3. **Run the 10-Dimension Interrogation**:
   - Methodically evaluate every parameter, function, and state transition against the 10 dimensions.
4. **Score Risk & Impact**:
   - Categorize each corner case by:
     - **Likelihood**: High (likely in production), Medium (under edge conditions), Low (bizarre attack or extreme stress).
     - **Severity**: Critical (data loss, crash, security breach), High (incorrect business calculation, unhandled error), Medium (degraded UX, error code mismatch), Low (formatting/cosmetic).
5. **Synthesize the Corner-Case Matrix**:
   - Produce a structured table mapping Requirement ID to Corner Case IDs, input vectors, and expected failure modes.

> Output Artifact: **[Corner-Case Matrix](./templates/corner-case-matrix.md)**

---

### Phase 2: Adversarial Scenario Architecture & Test Synthesis

Transform abstract corner cases into concrete, deterministic, automated test scenarios:

1. **Select the Right Testing Paradigm**:
   - **Boundary Unit Tests**: Focused on single functions, edge inputs, and strict assertion thresholds.
   - **Property-Based Tests**: Generative fuzzing across entire domains (e.g., `Hypothesis`, `fast-check`, `quickcheck`).
   - **Concurrency & Race Fixtures**: Spawning parallel workers/threads hammering shared resources simultaneously.
   - **State-Transition Sequences**: Chain of calls verifying state invariants and rejecting illegal transitions.
   - **Chaos / Fault Injection**: Mocking network drops, file system failures, and timeout exceptions.
2. **Draft Explicit Scenario Specifications**:
   - **Given (Preconditions)**: Initial system state, seeded database, mocked external dependencies.
   - **When (Trigger Vector)**: The exact malicious or extreme input payload, concurrent triggers, or sequence of calls.
   - **Then (Strict Invariants)**:
     - Exact return values or typed exceptions (never generic `catch Exception`).
     - State invariant guarantees (e.g., account balance was not modified on failed transfer).
     - Idempotency guarantees (calling 10 times yields identical state as calling once).
     - Graceful error responses (HTTP status codes, structured error payloads).
3. **Author the Executable Test Suite**:
   - Write real, runnable test files using the project's native test runner (`pytest`, `jest`, `vitest`, `go test`, `cargo test`).
   - Place corner-case tests in dedicated suites (e.g., `tests/adversarial/` or `tests/corner_cases/`).

> Output Artifact: **[Test Scenario Plan](./templates/test-scenario-plan.md)**

---

### Phase 3: Test Execution & High-Level Executive Triage Reporting

Execute the new test suite against the current codebase and establish the baseline failure state:

1. **Deterministic Test Execution**:
   - Run the exact test command using `run_command`.
   - Capture raw output, exit codes, assertion failure traces, and execution duration.
2. **Parse & Categorize Failures**:
   - Separate passing tests from failing tests.
   - Categorize failure root causes: Unhandled Exception, Incorrect Calculation, Data Corruption, Hang/Timeout, Unchecked Null.
3. **Synthesize the Executive Triage Report**:
   - High-level leadership needs clarity, not raw stack traces. Provide:
     - **Executive Summary**: Pass rate, total scenarios, overall readiness status (e.g., `NOT PRODUCTION READY - 4 CRITICAL DEFECTS`).
     - **Risk Heatmap**: Breakdown of failures by business severity.
     - **Root Cause Taxonomy**: High-level explanation of why the system failed.
     - **Remediation Roadmap**: Prioritized order of fixes to bring the system to green.

> Output Artifact: **[Executive Triage Report](./templates/executive-triage-report.md)** & **[Test Execution Scorecard](./templates/test-execution-scorecard.md)**

---

### Phase 4: Autonomous Red-to-Green Remediation Loop

Once the failures are reported, the agent systematically modifies the production code or content to achieve 100% pass status:

```
┌────────────────────────────────────────────────────────┐
│             THE RED-TO-GREEN REMEDIATION LOOP          │
├────────────────────────────────────────────────────────┤
│  1. Isolate the failing test and its root cause.      │
│  2. Formulate the minimal, surgical code patch.        │
│  3. Apply the patch to source files.                   │
│  4. Re-run the target corner-case test (Verify Green). │
│  5. Run ALL baseline tests (Verify Zero Regression).   │
│  6. If failed, rollback or refine; repeat (max 5).    │
│  7. Once all tests pass, proceed to Phase 5.          │
└────────────────────────────────────────────────────────┘
```

1. **Surgical Root Cause Remediation**:
   - Fix the business logic, input validation, state machine guard, or concurrency primitive.
   - **Never over-refactor**: Modify only the minimal necessary lines to satisfy the requirement safely.
2. **Verify Target Green**:
   - Run the specific test that previously failed. Confirm it now exits 0 with assertions satisfied.
3. **Verify Zero Regressions (Full Suite Check)**:
   - Run the entire existing project test suite.
   - If any previously passing test breaks, the patch is rejected. Analyze the collision and refine the patch.
4. **Log the Iteration**:
   - Record what file was changed, why it failed, what was fixed, and the before/after test status.

> Output Artifact: **[Remediation Changelog](./templates/remediation-changelog.md)**

---

### Phase 5: Anti-Cheat, Mutation & Regression Verification

Passing tests is not enough. You must verify that the pass was genuine and the tests have teeth:

1. **Anti-Cheat Audit**:
   - Run git diff on test directories: Confirm NO test assertions were commented out, deleted, or relaxed.
   - Confirm NO hardcoded conditionals were added to production code to bypass tests (e.g., `if (val == "special_test_case") return mock_val;`).
2. **Mutation Sanity Check**:
   - Temporarily introduce a deliberate bug (e.g., invert a boundary operator `<` to `<=`, comment out a validation check).
   - Re-run the corner-case tests: **They must fail**. If tests still pass with broken logic, the tests are weak or meaningless (surviving mutant).
   - Revert the deliberate mutation and confirm tests return to green.
3. **Deliver Final High-Level Sign-Off**:
   - Publish the completed verification report to high-level stakeholders with proof of resolution, 100% test pass rate, and zero regressions.

---

## Anti-Cheat Guardrails & Integrity Invariants

| Prohibited Action (The "Cheat") | Detection Method | Mandatory Remedy |
| :--- | :--- | :--- |
| **Tampering with Tests** | Git diff shows changes in `tests/` during Phase 4. | Hard revert of test file changes. Fix must be made in application code only. |
| **Weakening Assertions** | Replacing `assert x == 42` with `assert x is not None` or removing assertions. | Reject patch. Restore original strict assertion. |
| **Hardcoding Test Inputs** | Inspecting code for literals found only in test fixtures. | Require generalized algorithmic fix handling all equivalent inputs. |
| **Swallowing Exceptions** | Adding blank `try ... catch (e) {}` or `except: pass` to suppress test errors. | Ban empty catch blocks; require explicit typed error handling. |
| **Mocking Internal Sinks** | Replacing real internal calculations with mocked returns in integration tests. | Integration tests must execute real code paths. |
| **Ignoring Regressions** | Claiming success on corner cases while existing unit tests are failing. | Zero tolerance: Total test suite pass rate must be 100%. |

---

## Tooling & Automation Scripts

The skill provides production-grade automation scripts in `scripts/`:

- **`corner_case_generator.py` / `corner_case_generator.ps1`**:
  Parses requirements documents, API schemas, or code signatures, systematically interrogates the 10 dimensions, and generates an exhaustive Markdown Corner-Case Matrix.
- **`remediation_runner.py` / `remediation_runner.ps1`**:
  Autonomous test execution and remediation controller. Executes test commands, parses failure outputs, performs git anti-cheat audits, tracks iteration history, and logs test scorecards.

---

## Skill Artifact Suite

When executing this skill, produce artifacts in this exact sequence:

1. **Corner-Case Matrix** (`corner-case-matrix.md`):
   - Comprehensive inventory of all imagined corner cases, categorized by dimension, severity, and input vector.
2. **Test Scenario Plan** (`test-scenario-plan.md`):
   - Detailed specifications for each test scenario including Given-When-Then, boundary payloads, and invariant assertions.
3. **Executive Triage Report** (`executive-triage-report.md`):
   - High-level leadership briefing with pass/fail metrics, risk heatmap, root causes, and remediation roadmap.
4. **Test Execution Scorecard** (`test-execution-scorecard.md`):
   - Granular technical breakdown of all executed tests, assertion results, and timings.
5. **Remediation Changelog** (`remediation-changelog.md`):
   - Iteration log of code changes, root-cause fixes, regression checks, and anti-cheat verification results.

---

## Reference Manual & Templates

- **References**:
  - [Corner-Case Taxonomy & Discovery Guide](./references/corner-case-taxonomy.md)
  - [Scenario Planning & Test Architecture Playbook](./references/scenario-planning-playbook.md)
  - [Self-Healing Red-to-Green Remediation Protocol](./references/self-healing-remediation-loop.md)
  - [High-Level Executive Reporting Framework](./references/high-level-reporting-framework.md)
  - [Anti-Cheat & Mutation Integrity Rules](./references/anti-cheat-and-mutation-rules.md)
- **Templates**:
  - [Corner-Case Matrix Template](./templates/corner-case-matrix.md)
  - [Test Scenario Plan Template](./templates/test-scenario-plan.md)
  - [Executive Triage Report Template](./templates/executive-triage-report.md)
  - [Test Execution Scorecard Template](./templates/test-execution-scorecard.md)
  - [Remediation Changelog Template](./templates/remediation-changelog.md)
- **Examples**:
  - [Full End-to-End Testing & Remediation Walkthrough](./examples/full-corner-case-lifecycle-walkthrough.md)
  - [Sample Corner-Case Matrix](./examples/sample-corner-case-matrix.md)
  - [Sample Test Scenario Plan](./examples/sample-test-scenario-plan.md)
  - [Sample Executive Triage Report](./examples/sample-executive-report.md)
