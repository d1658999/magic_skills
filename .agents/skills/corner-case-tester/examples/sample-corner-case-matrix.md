# Sample Corner-Case Matrix: Promotional Voucher Engine

**Component**: `src/billing/discount_engine.py`  
**Analyzed Requirements**: `docs/specs/promotional_engine_v1.md`  
**Date**: `2026-10-30`  
**Lead Test Architect**: `Corner-Case Tester Agent`  
**Status**: `COMPLETED & REMEDIATED`  

---

## Exhaustive Corner-Case Register

| Case ID | Dimension | Severity | Risk Score | Input Trigger Vector | Expected Invariant / Outcome | Initial Status | Final Status |
| :--- | :--- | :---: | :---: | :--- | :--- | :---: | :---: |
| `CC-001` | Numeric Boundary | P0 | 9 | Discount amount ($50.00) exceeds subtotal ($30.00) | Raise `ValueError("Discount cannot exceed subtotal")` | `FAIL` | `PASS` |
| `CC-002` | Numeric Boundary | P0 | 9 | Negative discount (-$10.00) passed | Raise `ValueError("Discount cannot be negative")` | `FAIL` | `PASS` |
| `CC-003` | Floating Point | P1 | 6 | Micro-penny tax calculation ($0.07 * 0.07) | Rounded to 2 decimal places with `ROUND_HALF_UP` | `FAIL` | `PASS` |
| `CC-004` | Concurrency | P0 | 9 | 10 concurrent requests redeeming single-use voucher | Exactly 1 succeeds, 9 fail with `CouponUsedError` | `FAIL` | `PASS` |
| `CC-005` | Collections | P1 | 6 | Empty cart items `items=[]` | Returns total $0.00 or raises `EmptyCartError` | `PASS` | `PASS` |
| `CC-006` | Collections | P1 | 6 | Item with quantity = 0 or negative quantity | Raise `InvalidQuantityError` | `PASS` | `PASS` |
| `CC-007` | Nullability | P0 | 9 | `items=None` passed to calculation | Raise `InvalidPayloadError` with clean message | `PASS` | `PASS` |
| `CC-008` | Strings | P2 | 3 | Coupon code is whitespace only `"   "` | Stripped and treated as no coupon provided | `PASS` | `PASS` |
| `CC-009` | Strings | P2 | 3 | Coupon code containing 4-byte astral emojis `"🎁SAVE🎁"`| Handled without database encoding crash | `PASS` | `PASS` |
| `CC-010` | State Machine | P1 | 4 | Applying discount to an order already `CANCELLED` | Raise `IllegalOrderStateError` | `PASS` | `PASS` |
| `CC-011` | Security | P0 | 6 | SQL metacharacters in voucher `"'; DROP TABLE vouchers;--"` | Parameterized lookup; treated as unknown code | `PASS` | `PASS` |
| `CC-012` | Idempotency | P1 | 4 | Duplicate API request with identical `Idempotency-Key` | Cached response returned; voucher not double-charged | `PASS` | `PASS` |
