# Full Corner-Case Lifecycle Walkthrough

This document presents a comprehensive, end-to-end case study demonstrating the **Corner-Case Tester & Self-Healing Test Architect** in action. It follows an e-commerce company building a high-throughput **Promotional Discount & Voucher Redemption Engine**.

---

## 1. The Initial Requirement

The product owner submitted this user requirement:

```markdown
# Feature: E-Commerce Promotional Discount & Coupon Service
Users can apply promotional coupon codes to their cart during checkout.
Requirements:
1. Support percentage discounts (e.g., 20% off) and fixed cash discounts (e.g., $10 off).
2. Support single-use promotional vouchers (e.g., "WELCOME50" can only be redeemed once per customer).
3. Ensure cart total is calculated correctly including applicable 7% sales tax.
4. Calculate and return final checkout summary.
```

The initial developer drafted `src/discount_engine.py`:

```python
# Initial implementation: src/discount_engine.py
class DiscountEngine:
    def __init__(self, coupon_store):
        self.coupon_store = coupon_store

    def calculate_cart(self, items, discount_amount, coupon_code=None, user_id=None):
        subtotal = sum(item["price"] * item["quantity"] for item in items)
        
        # Apply coupon code if provided
        if coupon_code and user_id:
            if not self.coupon_store.is_used(coupon_code, user_id):
                subtotal -= discount_amount
                self.coupon_store.mark_used(coupon_code, user_id)

        # 7% sales tax
        tax = subtotal * 0.07
        total = subtotal + tax
        return {"subtotal": subtotal, "tax": tax, "total": total}
```

---

## Phase 1: 360° Requirement & Corner-Case Deconstruction

The agent interrogated the requirement across the **10 Dimensions** and extracted 12 adversarial corner cases:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        CORNER-CASE DISCOVERY REGISTER                  │
├────────────────────────────────────────────────────────────────────────┤
│ CC-001 [Numeric]: Discount ($50) exceeds Subtotal ($30) ──▶ Total < 0! │
│ CC-002 [Numeric]: Negative discount (-$10) ───────────────▶ Total grows│
│ CC-003 [Precision]: Floating point drift (0.1 + 0.2 != 0.3) on taxes   │
│ CC-004 [Collections]: Empty items list [] passed ─────────▶ Subtotal $0│
│ CC-005 [Collections]: Quantity is 0 or negative ──────────▶ Unchecked  │
│ CC-006 [Nulls]: Items is null/None ───────────────────────▶ Crash      │
│ CC-007 [Strings]: Coupon code is whitespace only "   " ───▶ Bypass     │
│ CC-008 [Strings]: Coupon code with emojis "🎁WELCOME🎁" ──▶ DB truncate│
│ CC-009 [Concurrency]: 10 simultaneous requests using single voucher    │
│ CC-010 [State]: Order marked CANCELLED while discount is being applied │
│ CC-011 [Security]: SQL metacharacters in coupon: "'; DROP TABLE..."    │
│ CC-012 [Idempotency]: Duplicate checkout call with same request ID     │
└────────────────────────────────────────────────────────────────────────┘
```

The agent generated the formal **[Corner-Case Matrix](./sample-corner-case-matrix.md)**.

---

## Phase 2: Adversarial Scenario Architecture & Test Synthesis

The agent authored an automated, executable test suite in `tests/adversarial/test_discount_engine.py`:

```python
import pytest
from decimal import Decimal
import concurrent.futures
from src.discount_engine import DiscountEngine

class MockCouponStore:
    def __init__(self):
        self.used_records = set()

    def is_used(self, coupon, user):
        return (coupon, user) in self.used_records

    def mark_used(self, coupon, user):
        self.used_records.add((coupon, user))

@pytest.fixture
def engine():
    return DiscountEngine(MockCouponStore())

# SCEN-001: Boundary Check - Discount exceeding subtotal
def test_discount_exceeding_subtotal_rejected(engine):
    items = [{"price": 30.00, "quantity": 1}]
    with pytest.raises(ValueError, match="Discount cannot exceed subtotal"):
        engine.calculate_cart(items, discount_amount=50.00, coupon_code="BIG50", user_id="u1")

# SCEN-002: Numeric Check - Floating point precision on sales tax
def test_tax_calculation_exact_cent_rounding(engine):
    items = [{"price": 0.07, "quantity": 1}] # 7% tax on $0.07 is 0.0049 -> should round to $0.00 or $0.01 exactly
    res = engine.calculate_cart(items, discount_amount=0.0)
    assert isinstance(res["tax"], (int, float, Decimal))
    # Must not contain float drift like 0.0049000000000000005
    assert str(res["tax"]).count(".") <= 1
    assert len(str(res["tax"]).split(".")[1]) <= 2

# SCEN-003: Concurrency Stress Check - Single-use coupon double-spend
def test_concurrent_voucher_redemption_race(engine):
    items = [{"price": 100.00, "quantity": 1}]
    successful_discounts = 0

    def attempt_checkout():
        res = engine.calculate_cart(items, discount_amount=50.00, coupon_code="SINGLE50", user_id="u1")
        return res["subtotal"] == 50.00

    # 10 workers hit simultaneously
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(attempt_checkout) for _ in range(10)]
        for f in concurrent.futures.as_completed(futures):
            if f.result() is True:
                successful_discounts += 1

    # Invariant: EXACTLY 1 request receives discount!
    assert successful_discounts == 1
```

---

## Phase 3: Initial Execution & High-Level Executive Triage Reporting

The agent ran the test suite using `pwsh remediation_runner.ps1`:

```text
[STEP 2] Executing Target Corner-Case Test Command...
pytest tests/adversarial/test_discount_engine.py
============================== FAILURES ==============================
FAILED test_discount_exceeding_subtotal_rejected - ValueError not raised; total was -21.40
FAILED test_tax_calculation_exact_cent_rounding - AssertionError: tax was 0.0049000000000000005
FAILED test_concurrent_voucher_redemption_race - AssertionError: assert 8 == 1
======================== 3 failed, 9 passed in 0.42s ========================
```

The agent delivered the **Executive Triage Report** to leadership:

> ### Executive Triage Report: E-Commerce Promotional Engine
> **PRODUCTION STATUS**: ❌ **BLOCKED - 3 CRITICAL DEFECTS**  
> **Pass Rate**: 75.0% (9 Passed, 3 Failed)  
>
> **Critical Discoveries**:
> 1. **Promotional Budget Bleed (Concurrency TOCTOU)**: 8 out of 10 simultaneous requests redeemed a single-use voucher due to non-atomic read/write.
> 2. **Negative Cart Exploitation**: Discounts greater than subtotal generated negative balances, allowing users to credit accounts.
> 3. **Tax Rounding Inaccuracy**: Floating-point drift produces fractional sub-pennies that violate GAAP accounting.
>
> **Remediation Plan**: Applying atomic locks, zero-floor input validation, and `Decimal` quantization.

---

## Phase 4: Autonomous Red-to-Green Remediation Loop

The agent executed the automated remediation loop:

### Iteration 1: Fixing Negative Balances & Decimal Rounding
The agent modified `src/discount_engine.py`:
- Replaced `float` math with `Decimal`.
- Added validation: `if discount_amount > subtotal: raise ValueError("Discount cannot exceed subtotal")`.
- Added quantization: `tax = (subtotal * Decimal("0.07")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`.

Target tests re-run:
- `test_discount_exceeding_subtotal_rejected`: ✅ **PASS**
- `test_tax_calculation_exact_cent_rounding`: ✅ **PASS**
- `test_concurrent_voucher_redemption_race`: ❌ **FAIL** (still failing)

### Iteration 2: Fixing Concurrency Double-Spend
The agent introduced an atomic mutex lock in `src/discount_engine.py`:
```python
import threading
self._lock = threading.Lock()

with self._lock:
    if not self.coupon_store.is_used(coupon_code, user_id):
        subtotal -= discount_amount
        self.coupon_store.mark_used(coupon_code, user_id)
```

Target tests re-run:
- `test_concurrent_voucher_redemption_race`: ✅ **PASS** (10 workers: exactly 1 succeeded, 9 rejected).

### Step 3: Baseline Regression Verification
The agent ran the existing unit test suite:
- `pytest tests/unit/`: **42 passed, 0 failed** (Zero regressions).

---

## Phase 5: Anti-Cheat & Mutation Verification

1. **Anti-Cheat Git Audit**:
   - `git diff --name-only tests/` ──▶ **0 files modified** (Passed).
2. **Mutation Testing**:
   - Inverted `<` to `<=` on boundary check: Test immediately failed (`Mutant Killed`).
   - Reverted mutant.
3. **High-Level Sign-Off**:
   - Final status: **100% GREEN, ZERO REGRESSIONS, PRODUCTION READY**.
