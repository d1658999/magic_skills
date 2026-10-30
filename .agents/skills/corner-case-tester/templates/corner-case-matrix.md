# Corner-Case Matrix Template

Use this template during **Phase 1** to document all discovered edge cases, boundary conditions, and failure modes extracted from requirements.

---

# Corner-Case Matrix: [Target Component / Feature Name]

**Component / Module**: `[e.g., src/billing/discount_engine.py]`  
**Analyzed Requirements**: `[e.g., docs/specs/billing_v2.md, JIRA-402]`  
**Date**: `[YYYY-MM-DD]`  
**Lead Test Architect**: `[Agent Role / Name]`  
**Overall Readiness Assessment**: `[READY | AT RISK | UNTESTED]`  

---

## 1. Summary of Corner-Case Discoveries

| Total Cases Identified | Critical (P0) | High (P1) | Medium (P2) | Low (P3) |
| :---: | :---: | :---: | :---: | :---: |
| `[Count]` | `[Count]` | `[Count]` | `[Count]` | `[Count]` |

---

## 2. Exhaustive Corner-Case Register

| Case ID | Dimension | Requirement Anchor | Input Trigger Vector / Scenario | Expected Behavior / Invariant | Sev | Likelihood | Risk Score | Test Status |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| `CC-001` | Numeric Boundary | Req 1.2: "Discount applied" | Subtotal = $100.00, Discount = $0.00 | Total = $100.00, zero discount | P2 | High (3) | 6 | `[PASS/FAIL]` |
| `CC-002` | Numeric Boundary | Req 1.2: "Discount applied" | Subtotal = $50.00, Discount = $50.00 | Total = $0.00 (100% free) | P1 | High (3) | 6 | `[PASS/FAIL]` |
| `CC-003` | Numeric Boundary | Req 1.2: "Discount applied" | Subtotal = $50.00, Discount = $50.01 | Raise `InvalidDiscountError` | P0 | Med (2) | 6 | `[PASS/FAIL]` |
| `CC-004` | Numeric Boundary | Req 1.2: "Discount applied" | Subtotal = $100.00, Discount = -$10.00 | Raise `InvalidDiscountError` | P0 | Med (2) | 6 | `[PASS/FAIL]` |
| `CC-005` | Floating Point | Req 1.4: "Tax calc" | 0.10 tax on $0.07 price | Exact penny rounding ($0.01) | P1 | High (3) | 6 | `[PASS/FAIL]` |
| `CC-006` | String / Encoding | Req 2.1: "Coupon code" | Coupon code = `"   "` (spaces) | Raise `InvalidCouponError` | P2 | High (3) | 6 | `[PASS/FAIL]` |
| `CC-007` | String / Encoding | Req 2.1: "Coupon code" | Coupon code containing emojis `🎁` | Handle cleanly or reject | P3 | Low (1) | 3 | `[PASS/FAIL]` |
| `CC-008` | Collections | Req 3.1: "Cart items" | Cart items = `[]` (empty) | Raise `EmptyCartError` | P1 | High (3) | 6 | `[PASS/FAIL]` |
| `CC-009` | Nullability | Req 1.1: "User payload" | User payload = `null` or `{}` | Raise `InvalidPayloadError` | P1 | Med (2) | 4 | `[PASS/FAIL]` |
| `CC-010` | Concurrency | Req 4.1: "Single-use code" | 2 parallel requests redeeming code | Exactly 1 succeeds, 1 rejected | P0 | High (3) | 9 | `[PASS/FAIL]` |
| `CC-011` | State Machine | Req 4.2: "Order state" | Redeem coupon on `CANCELLED` order | Raise `InvalidOrderStateError` | P1 | Med (2) | 4 | `[PASS/FAIL]` |
| `CC-012` | Security / Injection | Req 2.1: "Coupon code" | Coupon = `' OR 1=1 --` | Sanitize; treat as unknown code | P0 | Med (2) | 6 | `[PASS/FAIL]` |

---

## 3. High-Priority Risk Analysis & Mitigations

### Critical Risk 1: `[e.g., CC-010 Concurrency Double-Redemption]`
- **Root Risk**: Under high concurrency, single-use promotional codes could be redeemed dozens of times before the record updates.
- **Potential Impact**: Promotional budget exhaustion and financial loss.
- **Mandatory Verification**: Parallel thread stress test with shared state latch.

### Critical Risk 2: `[e.g., CC-003 Negative Total Exposure]`
- **Root Risk**: Discounts exceeding order subtotals generating negative checkout amounts.
- **Potential Impact**: Payment gateway processing errors or paying customers for goods.
- **Mandatory Verification**: Strict zero-floor boundary assertion.
