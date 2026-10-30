# Coverage Scorecard Template

Use this template during **Phase 4** to capture quantitative test execution metrics, line/branch coverage, and execution timings.

---

# Quantitative Coverage Scorecard: [Component Name]

**Execution Timestamp**: `[YYYY-MM-DDTHH:MM:SS]`  
**Execution Command**: `[pytest --cov=src --cov-report=term-missing tests/functional]`  
**Total Execution Time**: `[X.XX s]`  
**Overall Test Pass Rate**: `[ 100.0% ]`  

---

## 1. Multi-Level Coverage Summary

| Coverage Metric Level | Actual Value | Minimum Gate | Gate Status |
| :--- | :---: | :---: | :---: |
| **Scenario Coverage Ratio** | **`[XX.X%]`** | **90.0%** | `[ PASSED / FAILED ]` |
| **Line / Statement Coverage** | **`[XX.X%]`** | **85.0%** | `[ PASSED / FAILED ]` |
| **Branch / Decision Coverage** | **`[XX.X%]`** | **80.0%** | `[ PASSED / FAILED ]` |
| **Automated Test Pass Rate** | **100.0%** | **100.0%** | `PASSED` |

---

## 2. File-by-File Code Coverage Breakdown

| Source File | Total Lines | Executed Lines | Missing Lines | Line Coverage % | Branch Coverage % |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `src/auth/service.py` | 120 | 115 | 45-49 | 95.8% | 92.0% |
| `src/auth/validators.py`| 80 | 76 | 32-35 | 95.0% | 88.0% |
| `src/auth/dto.py` | 45 | 45 | None | 100.0% | 100.0% |
| **TOTAL** | **245** | **236** | — | **96.3%** | **93.3%** |

---

## 3. Uncovered Lines & Branch Analysis

- **Missing Lines 45-49 in `src/auth/service.py`**:
  - *Code*: Unused internal debug logging method.
  - *Risk Assessment*: Low risk; does not affect user-facing business logic.
