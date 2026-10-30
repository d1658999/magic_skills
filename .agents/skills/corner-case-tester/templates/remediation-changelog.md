# Remediation Changelog Template

Use this template during **Phase 4** and **Phase 5** to log all code modifications made during the Red-Green-Refactor loop.

---

# Remediation Changelog: [Component Name]

**Component**: `[e.g., src/billing/discount_engine.py]`  
**Initial Failing Scenarios**: `[Count, e.g., 6]`  
**Total Remediation Iterations**: `[Count, e.g., 2]`  
**Final Status**: `[ 100% GREEN - ALL TESTS PASSING ]`  
**Regression Status**: `[ ZERO REGRESSIONS (48/48 baseline tests passed) ]`  
**Anti-Cheat Status**: `[ VERIFIED - ZERO TEST FILES MODIFIED ]`  

---

## 1. Iteration History & Code Modifications

### Iteration 1: `[Defect 1 & 2 - Boundary Checks & Precision Fix]`
- **Target Files**:
  - `src/billing/discount.py`
- **Root Problem**: Missing validation for discount > subtotal; floating-point math causing rounding errors.
- **Code Modification Summary**:
  - Added boundary check: `if discount > subtotal: raise InvalidDiscountError("Discount cannot exceed subtotal")`.
  - Replaced `float` with `Decimal` and quantized with `ROUND_HALF_UP`.
- **Target Test Result**:
  - `TC-03`: `FAIL` ──▶ `PASS`
  - `TC-05`: `FAIL` ──▶ `PASS`
- **Regression Test Result**:
  - 48/48 baseline unit tests passed.

```diff
--- a/src/billing/discount.py
+++ b/src/billing/discount.py
@@ -12,4 +12,8 @@ def calculate_discount(subtotal: Decimal, discount: Decimal) -> Decimal:
+    if discount > subtotal:
+        raise InvalidDiscountError("Discount cannot exceed subtotal")
+    if discount < Decimal("0.00"):
+        raise InvalidDiscountError("Discount cannot be negative")
-    return subtotal - discount
+    return (subtotal - discount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
```

---

### Iteration 2: `[Defect 3 - Concurrency Double-Redemption Fix]`
- **Target Files**:
  - `src/billing/coupon_store.py`
- **Root Problem**: Non-atomic read-modify-write allowed concurrent workers to pass `if not coupon.used:` simultaneously.
- **Code Modification Summary**:
  - Wrapped coupon redemption in a threading lock / atomic compare-and-swap update.
- **Target Test Result**:
  - `TC-04`: `FAIL` ──▶ `PASS`
- **Regression Test Result**:
  - 48/48 baseline unit tests passed.

```diff
--- a/src/billing/coupon_store.py
+++ b/src/billing/coupon_store.py
@@ -20,6 +20,7 @@ class CouponStore:
+        with self._lock:
             if self._coupons[code].used:
                 raise CouponAlreadyUsedError("Coupon already redeemed")
             self._coupons[code].used = True
```

---

## 2. Final Verification & Anti-Cheat Audit

- [x] **Target Scenarios**: All 24 corner cases now pass (`24/24 PASS`).
- [x] **Baseline Suite**: All 48 existing unit/integration tests pass (`48/48 PASS`).
- [x] **Anti-Cheat Audit**: `git diff --name-only tests/` confirms **0 files modified** in test directories.
- [x] **Mutation Probes**: Deliberately inverted boundary operator; verified tests immediately failed (mutant killed).
- [x] **Code Quality**: No placeholder `TODO` or swallowed exceptions introduced.
