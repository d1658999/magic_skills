# Executive Triage Report Template

Use this template during **Phase 3** and **Phase 5** to deliver high-level, business-oriented testing and remediation reports to engineering leadership, directors, and stakeholders.

---

# Executive Triage Report: [System / Component Name]

**Component**: `[e.g., Billing & Discount Engine]`  
**Date**: `[YYYY-MM-DD]`  
**Assessment Phase**: `[INITIAL EVALUATION | REMEDIATION COMPLETE]`  
**Lead Test Architect**: `[Agent Role]`  

---

## 1. Executive Summary & Production Readiness Verdict

```
┌────────────────────────────────────────────────────────────────────────┐
│                        PRODUCTION READINESS VERDICT                    │
│                                                                        │
│   STATUS: [ READY FOR PROD | BLOCKED - DEFECTS FOUND | REMEDIATED ]   │
│   PASS RATE: [ XX.X % ] ( [Passed Count] / [Total Count] )             │
│   CRITICAL DEFECTS: [ Count ]                                          │
└────────────────────────────────────────────────────────────────────────┘
```

**Executive Statement**:  
`[2-3 sentence clear summary explaining the overall state of the software, key business risks discovered, and remediation progress.]`

---

## 2. Risk & Quality Scorecard

| Defect Severity | Total Tested | Passed | Failed | Business Impact / Exposure |
| :--- | :---: | :---: | :---: | :--- |
| **Critical (P0)** | `[Count]` | `[Count]` | `[Count]` | Direct financial loss, data loss, security exposure, or system crash. |
| **High (P1)** | `[Count]` | `[Count]` | `[Count]` | Core business calculation failure or persistent system freeze. |
| **Medium (P2)** | `[Count]` | `[Count]` | `[Count]` | Suboptimal error handling, missing validation, or degraded UX. |
| **Low (P3)** | `[Count]` | `[Count]` | `[Count]` | Cosmetic formatting, missing debug logs, or minor text mismatches. |
| **OVERALL TOTAL** | `[Total]` | `[Passed]` | `[Failed]` | **Health Grade: [ A | B | C | D | F ]** |

---

## 3. High-Level Failure Root Causes & Business Risks

### 1. `[Defect Title 1 - e.g., Concurrent Double-Spend on Promotion Redemption]`
- **Business Exposure**: `[e.g., Users can reuse single-use promotional vouchers simultaneously, causing uncapped promotional budget loss.]`
- **Root Cause**: `[e.g., Missing atomic database row lock on voucher state inspection.]`
- **Remediation Status**: `[REMEDIATED | IN PROGRESS | PENDING ARCHITECT APPROVAL]`

### 2. `[Defect Title 2 - e.g., Precision Drift in Tax Calculation]`
- **Business Exposure**: `[e.g., Fractional cent rounding discrepancies in invoices causing discrepancies during accounting audits.]`
- **Root Cause**: `[e.g., Use of IEEE 754 floating point arithmetic instead of Decimal quantization.]`
- **Remediation Status**: `[REMEDIATED | IN PROGRESS | PENDING ARCHITECT APPROVAL]`

---

## 4. Remediation Progress & Verification

```
[Phase 1: Corner-Case Discovery] ──▶ COMPLETED (Found [N] edge cases)
[Phase 2: Scenario Plan & Tests]  ──▶ COMPLETED (Synthesized [N] automated tests)
[Phase 3: Initial Execution]      ──▶ COMPLETED (Baseline pass rate: [X]%)
[Phase 4: Code Remediation Loop]  ──▶ [IN PROGRESS / COMPLETED]
[Phase 5: Anti-Cheat & Regress]   ──▶ [PENDING / VERIFIED (100% Green, 0 Regressions)]
```

---

## 5. Strategic Recommendations & Sign-Off

1. **Immediate Actions**:
   - `[Action 1, e.g., Deploy concurrency patch to staging]`
   - `[Action 2, e.g., Add property-based testing to CI pipeline]`
2. **Long-Term Architectural Hardening**:
   - `[Recommendation, e.g., Migrate database financial columns from FLOAT to NUMERIC(12, 4)]`

**Sign-off Status**: `[ APPROVED FOR DEPLOYMENT / BLOCKED REQUIRING REVIEW ]`
