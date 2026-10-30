# Test Execution Scorecard Template

Use this template during **Phase 3** and **Phase 4** to capture technical execution metrics, command invocations, assertion counts, and failure traces.

---

# Test Execution Scorecard: [Component Name]

**Execution Timestamp**: `[YYYY-MM-DDTHH:MM:SS]`  
**Test Suite File**: `[tests/adversarial/test_xyz.py]`  
**Execution Command**: `[pytest tests/adversarial/test_xyz.py -v]`  
**Exit Code**: `[ 0 (Success) | 1 (Failure) | 2 (Interrupted) ]`  
**Duration**: `[X.XX seconds]`  

---

## 1. Execution Telemetry Breakdown

| Metric | Count | Percentage |
| :--- | :---: | :---: |
| **Total Test Scenarios** | `[Total]` | 100.0% |
| **Passed Scenarios** | `[Passed]` | `[XX.X%]` |
| **Failed Scenarios** | `[Failed]` | `[XX.X%]` |
| **Skipped / Blocked** | `[Skipped]` | `[XX.X%]` |
| **Total Assertions Evaluated** | `[Asserts]` | — |

---

## 2. Detailed Scenario Results Table

| Test ID | Test Function / Target | Category | Duration | Result | Error Signature / Stack Trace Summary |
| :--- | :--- | :--- | :---: | :---: | :--- |
| `TC-01` | `test_zero_discount_boundary` | Boundary | 12ms | `PASS` | None |
| `TC-02` | `test_negative_discount_rejected`| Boundary | 15ms | `PASS` | None |
| `TC-03` | `test_discount_exceeding_subtotal`| Boundary | 18ms | `FAIL` | `AssertionError: Expected InvalidDiscountError, got None` |
| `TC-04` | `test_concurrent_coupon_redemption`| Concurrency | 142ms | `FAIL` | `AssertionError: Expected 1 success, got 4 successes` |
| `TC-05` | `test_floating_point_tax_rounding`| Numeric | 14ms | `FAIL` | `AssertionError: Decimal('0.07000000000000001') != Decimal('0.07')` |
| `TC-06` | `test_empty_cart_submission` | Collections | 9ms | `PASS` | None |
| `TC-07` | `test_whitespace_coupon_code` | Strings | 11ms | `PASS` | None |
| `TC-08` | `test_null_payload_handled` | Nullability | 10ms | `PASS` | None |

---

## 3. Failure Trace Deep Dive

### Failure Case 1: `TC-03 test_discount_exceeding_subtotal`
```text
File "tests/adversarial/test_discount.py", line 42, in test_discount_exceeding_subtotal
    result = calculate_discount(Decimal("50.00"), Decimal("60.00"))
E   AssertionError: InvalidDiscountError was not raised; function returned Total = -10.00
```
- **Failing Source File**: `src/billing/discount.py: line 24`
- **Root Problem**: Missing guard checking `if discount > subtotal: raise ...`

### Failure Case 2: `TC-04 test_concurrent_coupon_redemption`
```text
File "tests/adversarial/test_discount.py", line 88, in test_concurrent_coupon_redemption
    assert successful_redemptions == 1
E   AssertionError: assert 4 == 1
```
- **Failing Source File**: `src/billing/coupon_store.py: line 55`
- **Root Problem**: Non-atomic check-then-set on voucher usage flag.
