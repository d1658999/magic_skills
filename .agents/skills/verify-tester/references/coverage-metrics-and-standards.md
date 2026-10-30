# Coverage Metrics & Quality Standards

This reference defines the quantitative metrics, coverage thresholds, and gap analysis procedures used by the **Verify-Tester** to ensure comprehensive test suite rigor.

---

## 1. Dual-Coverage Model: Scenario Coverage vs. Code Coverage

A high-quality software system requires two distinct types of coverage measurement:

```
┌───────────────────────────────────────┐      ┌───────────────────────────────────────┐
│          SCENARIO COVERAGE            │      │             CODE COVERAGE             │
│        (Black-Box / Behavioral)       │      │         (White-Box / Structural)      │
├───────────────────────────────────────┤      ├───────────────────────────────────────┤
│ • Did we test all business rules?     │      │ • Did the tests execute every line?   │
│ • Are all acceptance criteria covered?│      │ • Were all if/else branches taken?    │
│ • Metric: Mapped Scenarios / Total    │      │ • Metric: Line %, Branch %, Stmt %    │
│ • Minimum Standard: >= 90.0%          │      │ • Minimum Standard: >= 80.0% - 85.0%  │
└───────────────────────────────────────┘      └───────────────────────────────────────┘
```

### The Pitfall of Code Coverage Alone:
100% line coverage can easily be achieved with zero meaningful assertions (e.g., executing code without verifying return values). Conversely, 100% scenario coverage might leave error-handling branches in third-party libraries unexecuted. **Both metrics must be evaluated together.**

---

## 2. Formal Quality Thresholds

| Metric | Target Standard | Minimum Release Gate | Action if Below Gate |
| :--- | :---: | :---: | :--- |
| **Scenario Coverage Ratio** | **$\ge 95\%$** | **$90.0\%$** | **BLOCK RELEASE**: Synthesize additional tests for unmapped requirements. |
| **Test Suite Pass Rate** | **$100\%$** | **$100.0\%$** | **BLOCK RELEASE**: All executed tests must pass; zero tolerated failures. |
| **Branch / Decision Coverage** | **$\ge 90\%$** | **$80.0\%$** | Audit unreached branches; add parameterized alternate path scenarios. |
| **Line / Statement Coverage** | **$\ge 90\%$** | **$85.0\%$** | Identify dead code or unexercised error handling blocks. |

---

## 3. Coverage Gap Analysis & Closing Protocol

When coverage falls below the 90% threshold, follow this 3-step closure protocol:

```
[Step 1: Identify Uncovered Nodes]
├── Run RTM audit to find REQ-IDs with 0 mapped tests
└── Run coverage tool (pytest-cov / istanbul) with missing line reports (e.g., --cov-report=term-missing)
         │
         ▼
[Step 2: Classify the Missing Logic]
├── Is it an unmapped Acceptance Criterion? ──▶ Draft new test in Pillar 1 or 2
├── Is it an unhandled Error Condition?    ──▶ Draft new test in Pillar 3
└── Is it dead / unreachable code?         ──▶ Remove dead code from codebase
         │
         ▼
[Step 3: Re-Execute & Recalculate]
└── Confirm new tests bring Scenario Coverage >= 90% and Branch Coverage >= 80%
```
