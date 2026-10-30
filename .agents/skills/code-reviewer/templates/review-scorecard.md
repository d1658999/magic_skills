# Code Review Scorecard Rubric

Use this weighted scorecard to assess the overall readiness of a pull request or code change.

---

## 8-Dimension Quality Rubric

| Category | Weight | Score (1-5) | Weighted | Criteria for 5/5 |
| :--- | :---: | :---: | :---: | :--- |
| **Architecture & Modularity** | 15% | `[ ]` | `[ ]` | Clear separation of concerns, no domain leaks, backwards-compatible contracts, respects SOLID. |
| **Correctness & Edge Cases** | 20% | `[ ]` | `[ ]` | Flawless handling of nulls, empties, boundary numbers, error states, and logic invariants. |
| **Security & Threat Model** | 20% | `[ ]` | `[ ]` | Zero OWASP/CWE vulnerabilities, strict input validation, authorization checked at object level, no secret leaks. |
| **Concurrency & Async Safety** | 15% | `[ ]` | `[ ]` | Free of race conditions, deadlocks, unhandled promise rejections; safe transaction locks. |
| **Performance & Scalability** | 10% | `[ ]` | `[ ]` | No N+1 queries, optimal algorithmic complexity, bounded caches, no memory/descriptor leaks. |
| **Reliability & Resilience** | 10% | `[ ]` | `[ ]` | Explicit timeouts on I/O, circuit breakers/jittered retries, transactional atomicity, graceful recovery. |
| **Test Quality & Coverage** | 5% | `[ ]` | `[ ]` | Meaningful assertions (no over-mocking), regression tests for bugs, edge cases thoroughly tested. |
| **Maintainability & Hygiene** | 5% | `[ ]` | `[ ]` | Self-documenting naming, zero debug leftovers (`console.log`, `print`), zero unverified type suppressions. |

---

## Scoring Scale

- **5 - Exceptional / Flawless**: Meets staff-engineer standards; robust against all failure modes.
- **4 - Solid / Production Ready**: Minor non-blocking polish recommended; zero logic or security flaws.
- **3 - Needs Work**: Contains 1 major issue or several missing edge cases; requires another review iteration.
- **2 - Substandard**: Multiple major logic bugs, architectural coupling, or missing test suites.
- **1 - Unacceptable**: Critical security vulnerability, active data corruption risk, or complete lack of verification.

---

## Final Quality Thresholds

- **Score >= 85% & Zero Blockers/Majors**: -> **`APPROVE`**
- **Score 70% - 84% OR Has Major Issue(s)**: -> **`REQUEST_CHANGES`** (Requires targeted fixes)
- **Score < 70% OR Has Critical Blocker(s)**: -> **`REQUEST_CHANGES`** (Architectural overhaul / security fix)
