# Verify-Tester & Broad-Spectrum Test Architect

A systematic verification test architect skill that bridges the gap between written functional specifications and running software. It deconstructs requirements into atomic acceptance criteria, constructs bidirectional **Requirements Traceability Matrices (RTM)**, plans and executes broad-spectrum test suites covering **at least 90% of mainstream operational scenarios** across the Four Pillars (Happy Paths, Alternate Branches, Expected Errors, and E2E Workflows), and delivers authoritative compliance audit reports for production release.

---

## Key Capabilities

- **$\ge 90\%$ Scenario Coverage Guarantee**: Mathematically calculates and enforces minimum 90% coverage of all documented functional requirements, user stories, and acceptance criteria.
- **Bidirectional Requirements Traceability (RTM)**: Enforces forward traceability (no missing features) and backward traceability (no bloated/zombie test waste).
- **The Four-Pillar Scenario Balance**:
  - **Pillar 1: Golden Happy Paths (40%)**: Primary user journeys and nominal operational flows.
  - **Pillar 2: Alternate Valid Branches (30%)**: Optional parameter variations, pagination, filtering, and role permutations.
  - **Pillar 3: Expected Error Handling (20%)**: Standard validation failures, duplicate identity 409s, and authentication 401/403s.
  - **Pillar 4: End-to-End Workflows (10%)**: Multi-step state machine lifecycles and cross-service data chains.
- **Data Contract & Schema Verification**: Validates strict JSON Schema, Pydantic DTOs, and backward compatibility invariants.
- **Authoritative Verification Auditing**: Delivers executive dashboards and compliance scorecards certifying production readiness.

---

## Directory Structure

```
verify-tester/
├── SKILL.md                                  # Core operating doctrine, 5-phase lifecycle & RTM rules
├── README.md                                 # Skill overview & CLI quick-start guide
├── references/
│   ├── requirements-traceability-framework.md # Bidirectional RTM construction & 90% formula
│   ├── broad-spectrum-coverage-playbook.md   # Four Pillars allocation strategy and code exemplars
│   ├── verification-vs-validation.md          # Acceptance criteria (Given-When-Then) & compliance verdicts
│   ├── coverage-metrics-and-standards.md      # Scenario coverage vs code line/branch coverage standards
│   └── contract-and-schema-testing.md        # API schema, JSON Schema & DTO contract testing
├── templates/
│   ├── requirements-traceability-matrix.md   # Markdown RTM template linking REQ-IDs to tests
│   ├── general-test-scenario-plan.md         # Four-pillar scenario plan template
│   ├── verification-audit-report.md          # Executive verification sign-off audit report
│   ├── coverage-scorecard.md                 # Quantitative line, branch & scenario scorecard
│   └── acceptance-test-suite-template.md     # Scaffolding template for Python/pytest test suites
├── scripts/
│   ├── verify_coverage_calculator.ps1        # PowerShell: Computes Scenario Coverage % and audits 90% gate
│   ├── verify_coverage_calculator.py         # Python: Computes Scenario Coverage % and audits 90% gate
│   ├── test_suite_generator.ps1              # PowerShell: Scaffolds Four-Pillar test suite
│   └── test_suite_generator.py               # Python: Scaffolds Four-Pillar test suite
└── examples/
    ├── full-verification-walkthrough.md      # Complete end-to-end walkthrough achieving 94% coverage
    ├── sample-requirements-traceability-matrix.md # Filled concrete RTM sample
    ├── sample-general-test-plan.md           # Concrete test scenario plan sample
    └── sample-verification-report.md         # Formal production sign-off audit report
```

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

## Command-Line Tooling & Automation

### 1. Auditing Scenario Coverage against the 90% Gate

```powershell
# PowerShell
pwsh .agents/skills/verify-tester/scripts/verify_coverage_calculator.ps1 -RtmFile rtm.md -Threshold 90.0

# Python
python .agents/skills/verify-tester/scripts/verify_coverage_calculator.py --rtm-file rtm.md --threshold 90.0 --markdown-out scorecard.md
```

### 2. Scaffolding a Broad-Spectrum Test Suite across the Four Pillars

```powershell
# PowerShell
pwsh .agents/skills/verify-tester/scripts/test_suite_generator.ps1 -FeatureName "UserProfileService" -OutFile tests/test_user_profile.py

# Python
python .agents/skills/verify-tester/scripts/test_suite_generator.py --feature-name "UserProfileService" --req-prefix "REQ-PROF" --out-file tests/test_user_profile.py
```
