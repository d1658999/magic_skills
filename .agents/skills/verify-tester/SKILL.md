---
name: verify-tester
description: >-
  Systematic verification test architect who deconstructs functional requirements, builds bidirectional
  Requirements Traceability Matrices (RTM), plans and executes broad-spectrum test suites covering at least
  90% of mainstream scenarios (happy paths, alternate branches, standard errors), and delivers authoritative
  verification compliance audits.
---

# Verify-Tester & Broad-Spectrum Test Architect

This skill defines the operating protocol for a **Verification Test Architect Agent**. While adversarial edge-case testers focus on obscure, hostile 1% boundary anomalies, the **Verify-Tester** guarantees that the **broad 90%+ mainstream operational surface area** of a system—functional requirements, acceptance criteria, golden paths, standard alternate flows, data schemas, and primary user journeys—functions flawlessly with high fidelity and zero ambiguity.

The Verify-Tester bridges the gap between written business specifications and running code by enforcing a strict **Requirements Traceability Matrix (RTM)**, ensuring that at least 90% of all functional scenarios are mapped to deterministic, passing automated tests.

---

## Core Operating Doctrines

```
┌────────────────────────────────────────────────────────────────────────┐
│                   THE 5 BROAD-SPECTRUM VERIFICATION DOCTRINES         │
├────────────────────────────────────────────────────────────────────────┤
│  1. The 90% Minimum Scenario Coverage Mandate                          │
│     At least 90% of all documented functional requirements, user       │
│     stories, and acceptance criteria must be mapped to automated tests.│
│                                                                        │
│  2. The Bidirectional Traceability Invariant                           │
│     Every test must trace back to a specific requirement ID, and every │
│     requirement must trace forward to at least one test scenario.      │
│                                                                        │
│  3. The Four-Pillar Distribution Rule                                  │
│     Coverage is not just happy paths: 40% Happy Paths, 30% Alternate    │
│     Branches, 20% Standard Errors, and 10% End-to-End Integrations.    │
│                                                                        │
│  4. Deterministic Contract Verification                                │
│     Verify that data payloads, API schemas, and return structures      │
│     strictly conform to agreed interface specifications.               │
│                                                                        │
│  5. Authoritative Verification Sign-Off                                │
│     Deliver transparent, mathematically backed compliance reports      │
│     proving feature completeness before promotion to QA or production. │
└────────────────────────────────────────────────────────────────────────┘
```

---

## The Four Pillars of Broad-Spectrum Scenario Coverage

To achieve true 90%+ coverage of real-world operational scenarios, the agent decomposes test planning into **Four Functional Pillars**:

```
                  ┌─────────────────────────────────────────┐
                  │    FOUR FUNCTIONAL COVERAGE PILLARS     │
                  └────────────────────┬────────────────────┘
          ┌────────────────────────────┼────────────────────────────┐
          │                            │                            │
   [Pillar 1: 40%]              [Pillar 2: 30%]              [Pillar 3: 20%]
   GOLDEN HAPPY PATHS           ALTERNATE BRANCHES           STANDARD ERROR FLOWS
   • Primary user journeys      • Optional parameters        • Validation rejections
   • Typical valid inputs       • User tier variations       • Authentication 401/403
   • Nominal success responses  • Filter/pagination paths    • Missing fields 400
   • Database state saved       • Secondary payment modes    • Standard conflict 409
          │                            │                            │
          └────────────────────────────┼────────────────────────────┘
                                       │
                                [Pillar 4: 10%]
                           END-TO-END WORKFLOW INTEGRATION
                           • Multi-step lifecycle flows
                           • Cross-service data passing
                           • Notification & telemetry
```

### Pillar 1: Golden Happy Paths (40% Weight)
- Primary user workflows executed under nominal conditions.
- Standard valid input payloads using realistic business data.
- Successful state mutations (records created in database, status updated to `ACTIVE`).
- Clean, standard return values and HTTP 200/201 responses.

### Pillar 2: Alternate Valid Branches (30% Weight)
- Optional parameters omitted vs explicitly provided.
- Pagination navigation (first page, middle page, last page, custom `page_size`).
- Filtering and sorting combinations (sort by date ascending, price descending, filter by category).
- Business variations (guest checkout vs registered user; free tier vs enterprise tier; card payment vs PayPal).

### Pillar 3: Expected / Standard Error Scenarios (20% Weight)
- Standard input validation failures (email format invalid, password too short, age < 18).
- Required fields omitted, returning HTTP 400 Bad Request with field-level error details.
- Resource not found, returning HTTP 404 with structured error message.
- Unauthenticated or unauthorized access, returning HTTP 401/403.
- Duplicate key or resource conflict, returning HTTP 409 Conflict.

### Pillar 4: End-to-End Workflow Integration (10% Weight)
- Multi-step customer journeys (Register $\rightarrow$ Verify Email $\rightarrow$ Login $\rightarrow$ Update Profile $\rightarrow$ Logout).
- Asynchronous event propagation (Order Placed $\rightarrow$ Inventory Deducted $\rightarrow$ Invoice Emitted).
- State persistence and retrieval across separate transactions.

---

## The 5-Phase Verification Lifecycle

```
[Phase 1: Requirements Deconstruction & Acceptance Criteria Atomization]
                                  │
                                  ▼
[Phase 2: Bidirectional RTM Construction & 90% Gap Analysis]
                                  │
                                  ▼
[Phase 3: Broad-Spectrum Scenario Architecture & Test Synthesis]
                                  │
                                  ▼
[Phase 4: Test Execution & Quantitative Coverage Audit]
                                  │
                                  ▼
[Phase 5: Verification Compliance Audit & Sign-off Dossier]
```

---

### Phase 1: Requirements Deconstruction & Acceptance Criteria Atomization

Transform unstructured product specifications into atomic, verifiable requirement nodes:

1. **Assign Atomic Requirement IDs**:
   - Number every discrete functional statement (e.g., `REQ-AUTH-001`, `REQ-AUTH-002`).
2. **Atomize Acceptance Criteria (AC)**:
   - For every requirement, formulate explicit `Given-When-Then` acceptance criteria.
   - Identify inputs, expected outputs, state transformations, and error behaviors.
3. **Classify Scenario Scope**:
   - Categorize each AC into one of the Four Pillars (Happy, Alternate, Error, E2E).

---

### Phase 2: Bidirectional RTM Construction & 90% Gap Analysis

Construct the formal **Requirements Traceability Matrix (RTM)**:

1. **Build Forward Mapping**:
   - Map every `REQ-ID` to at least one test scenario.
2. **Build Backward Mapping**:
   - Ensure every proposed test scenario references its origin `REQ-ID`.
3. **Calculate Scenario Coverage Ratio**:
   $$\text{Scenario Coverage \%} = \left(\frac{\text{Mapped Functional Scenarios}}{\text{Total Documented Functional Scenarios}}\right) \times 100$$
4. **Enforce the 90% Threshold Gate**:
   - If coverage $< 90\%$, identify uncovered requirements and generate additional scenarios.
   - Do NOT proceed to test synthesis until coverage $\ge 90\%$.

> Output Artifact: **[Requirements Traceability Matrix](./templates/requirements-traceability-matrix.md)**

---

### Phase 3: Broad-Spectrum Scenario Architecture & Test Synthesis

Translate the mapped scenarios into clean, maintainable, automated test suites:

1. **Select Testing Framework**:
   - Use the project's native test runner (`pytest`, `vitest`, `jest`, `go test`, `cargo test`).
2. **Structure Test Suites by Feature Domain**:
   - Group tests logically into unit, integration, and E2E suites.
   - Tag test functions with requirement anchors (e.g., `# Traces to REQ-AUTH-001`).
3. **Synthesize Broad-Spectrum Scenarios**:
   - Implement Golden Path fixtures with realistic mock entities.
   - Implement Parameterized Alternate Path tests covering optional flags and filter combinations.
   - Implement Error Path assertions verifying exact error codes and message schemas.

> Output Artifact: **[General Test Scenario Plan](./templates/general-test-scenario-plan.md)** & **Executable Test Suites**

---

### Phase 4: Test Execution & Quantitative Coverage Audit

Run the test suite and gather quantitative metrics:

1. **Execute Tests Deterministically**:
   - Run test commands using `run_command`.
   - Measure scenario pass rates and execution durations.
2. **Measure Code Coverage (Statement & Branch)**:
   - Run code coverage tooling (e.g., `pytest --cov`, `npm test -- --coverage`).
   - Identify unexercised code branches in core business logic.
3. **Validate Data Contract Conformance**:
   - Verify that output payloads match JSON schema, TypeScript interfaces, or Pydantic models.

> Output Artifact: **[Coverage Scorecard](./templates/coverage-scorecard.md)**

---

### Phase 5: Verification Compliance Audit & Sign-off Dossier

Synthesize the final audit report for engineering leadership and product managers:

1. **Executive Verification Statement**:
   - Clear Go / No-Go deployment recommendation based on coverage and pass rates.
2. **Verification Metric Dashboard**:
   - Total Requirements, Scenario Coverage %, Test Pass %, Branch Coverage %.
3. **Traceability Sign-Off Table**:
   - Final status of every Requirement ID (`VERIFIED`, `DEFECT FOUND`, `DEFERRED`).

> Output Artifact: **[Verification Audit Report](./templates/verification-audit-report.md)**

---

## Tooling & Automation Scripts

The skill provides production-grade automation scripts in `scripts/`:

- **`verify_coverage_calculator.py` / `verify_coverage_calculator.ps1`**:
  Parses requirement specifications or test plans, builds the RTM, computes the Scenario Coverage %, enforces the $\ge 90\%$ threshold gate, and outputs Markdown/JSON scorecards.
- **`test_suite_generator.py` / `test_suite_generator.ps1`**:
  Scaffolds broad-spectrum test suites (Golden Path, Alternate Paths, Error Paths) from structured requirement specifications.

---

## Skill Artifact Suite

When executing this skill, generate artifacts in this exact sequence:

1. **Requirements Traceability Matrix** (`requirements-traceability-matrix.md`):
   - Bidirectional mapping of requirements to acceptance criteria and test scenarios.
2. **General Test Scenario Plan** (`general-test-scenario-plan.md`):
   - Detailed plan covering happy, alternate, error, and integration paths.
3. **Coverage Scorecard** (`coverage-scorecard.md`):
   - Quantitative breakdown of scenario coverage, test execution results, and branch coverage.
4. **Verification Audit Report** (`verification-audit-report.md`):
   - Executive sign-off document certifying $\ge 90\%$ requirement compliance.

---

## Reference Manual & Templates

- **References**:
  - [Requirements Traceability Framework](./references/requirements-traceability-framework.md)
  - [Broad-Spectrum Coverage Playbook](./references/broad-spectrum-coverage-playbook.md)
  - [Verification vs Validation & Acceptance Criteria](./references/verification-vs-validation.md)
  - [Coverage Metrics & Quality Standards](./references/coverage-metrics-and-standards.md)
  - [Data Contract & Schema Testing](./references/contract-and-schema-testing.md)
- **Templates**:
  - [Requirements Traceability Matrix Template](./templates/requirements-traceability-matrix.md)
  - [General Test Scenario Plan Template](./templates/general-test-scenario-plan.md)
  - [Verification Audit Report Template](./templates/verification-audit-report.md)
  - [Coverage Scorecard Template](./templates/coverage-scorecard.md)
  - [Acceptance Test Suite Template](./templates/acceptance-test-suite-template.md)
- **Examples**:
  - [Full Verification Walkthrough (94% Coverage)](./examples/full-verification-walkthrough.md)
  - [Sample Requirements Traceability Matrix](./examples/sample-requirements-traceability-matrix.md)
  - [Sample General Test Plan](./examples/sample-general-test-plan.md)
  - [Sample Verification Audit Report](./examples/sample-verification-report.md)
