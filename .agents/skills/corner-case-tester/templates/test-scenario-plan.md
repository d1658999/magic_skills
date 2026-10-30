# Test Scenario Plan Template

Use this template during **Phase 2** to define detailed specifications for executable test suites covering corner cases.

---

# Adversarial Test Scenario Plan: [Feature / Component]

**Target File(s)**: `[e.g., src/billing/discount_engine.py]`  
**Test Suite Path**: `[e.g., tests/adversarial/test_discount_corners.py]`  
**Test Framework**: `[e.g., pytest 8.x / Jest 29.x / Vitest]`  
**Execution Command**: `[e.g., pytest tests/adversarial/test_discount_corners.py -v]`  

---

## 1. Scenario Architecture Overview

```
[Suite Initialization] ──▶ [Precondition Setup] ──▶ [Adversarial Injections] ──▶ [Strict Assertions]
```

- **Scope**: Rigorous testing of boundary conditions, concurrency, nulls, and illegal states.
- **Isolation Guarantee**: All external APIs/services mocked or containerized; zero cross-test state leakage.
- **Deterministic Requirement**: Tests must run without timing dependencies or flaky assertions.

---

## 2. Granular Test Scenario Specifications

### Scenario `SCEN-001`: `[Descriptive Scenario Name]`
- **Corner-Case Reference**: `CC-001` (Numeric Boundary)
- **Target Function**: `module.calculate_discount(subtotal, discount_amount)`
- **Category**: Boundary Value Analysis
- **Execution Severity**: Critical / High / Medium / Low

#### Given (Preconditions):
```python
subtotal = Decimal("100.00")
discount_amount = Decimal("0.00")
```

#### When (Trigger Action):
```python
result = calculate_discount(subtotal, discount_amount)
```

#### Then (Expected Invariants):
```python
assert result.total == Decimal("100.00")
assert result.discount_applied == Decimal("0.00")
assert result.tax == Decimal("0.00")
```

---

### Scenario `SCEN-002`: `[Descriptive Scenario Name - Concurrency]`
- **Corner-Case Reference**: `CC-010` (Concurrency Race Hazard)
- **Target Function**: `module.redeem_coupon(coupon_code, user_id)`
- **Category**: Concurrency & Atomic Mutex Testing
- **Execution Severity**: Critical (P0)

#### Given (Preconditions):
- A valid single-use coupon `"SAVE50"` seeded in database with `used = False`.
- Thread barrier initializing 10 concurrent worker threads.

#### When (Trigger Action):
- 10 threads call `redeem_coupon("SAVE50", user_id)` at the exact same millisecond.

#### Then (Expected Invariants):
- Exactly 1 thread receives `SuccessResponse(code=200)`.
- Exactly 9 threads receive `CouponAlreadyUsedError(code=409)`.
- Database query verifies `coupon.redemption_count == 1`.

---

## 3. Test Suite Generation Checklist

- [ ] All inputs and outputs have strictly pinned types.
- [ ] No hardcoded sleeps; concurrency tests use synchronization primitives (`threading.Barrier`, `CountDownLatch`).
- [ ] Error scenarios assert on exact exception types and error messages.
- [ ] Test file is saved in the repository under designated test directories.
